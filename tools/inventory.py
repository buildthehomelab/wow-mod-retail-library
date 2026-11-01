#!/usr/bin/env python3
"""Write data/looks.tsv from a census: every retail mount and battle pet look the client lacks
and the converter takes.

    python3 inventory.py --census <census out dir> [--also wanted-looks.tsv]

The census is wow-mod-retail-creatures' tools/census.py run with --models against your
client: its displays.tsv lists every look, its models.json what the converter made of each model.
--also (repeatable) names tsv files with a retail_display column, such as
wow-mod-retail-collection's data/wanted-looks.tsv: those looks are converted too although the
client has their model (a mount the client lacks, on a model it has) or it is no creature
model. Pass the same files to the census's --also, so their models are probed.
A look there that no retail mount or pet wears (a creature's, listed by the census as kind
"creature") comes in with form creature.
--add-only mount (or pet) adds new looks of that kind only; the looks already in the list stay,
and so do creature looks, which only --also brings in.
A look's 3.3.5 display id is 200000 + its retail display id, so it never moves, whatever is
added or dropped later, and anything that knows a retail display knows ours.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOOKS = os.path.join(HERE, "..", "data", "looks.tsv")
OFFSET = 200000
# A model's path in the client is <root>\<Model>\<Model>[_geosets].mdx, and the server's
# creaturemodeldata_dbc.ModelName holds 100 characters: longer model names are cut to fit.
ROOT = json.load(open(os.path.join(HERE, "..", "pack.json")))["root"]
PATH_MAX = 100


def model_name(stem, path, taken):
    """The look's model name: retail's file name, cut to fit the path, and unique (two retail
    models with one file name in different folders get two names)."""
    def client_path(name):
        folder = "".join(p[:1].upper() + p[1:] for p in name.split("_"))
        return "%s\\%s\\%s_000000.mdx" % (ROOT, folder, folder)
    name = stem
    while len(client_path(name)) > PATH_MAX:
        name = name[:-1].rstrip("_")
    base, n = name, 2
    while taken.get(name, path) != path:
        name = "%s%d" % (base[:len(base) - len(str(n))], n)
        n += 1
    taken[name] = path
    return name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", required=True)
    ap.add_argument("--also", action="append", default=[], help="tsv with a retail_display column (repeatable)")
    ap.add_argument("--add-only", choices=("mount", "pet"), help="add new looks of this kind only")
    args = ap.parse_args()
    models = json.load(open(os.path.join(args.census, "models.json")))
    also = set()
    for path in args.also:
        lines = open(path, encoding="utf-8").read().splitlines()
        col = lines[0].split("\t").index("retail_display")
        also.update(l.split("\t")[col] for l in lines[1:])
    # hide (retail texture file ids a look leaves out, with their batches) is set by hand: keep it.
    # A look already in the list keeps its model name, so its files in the client stay where they are.
    hide, had = {}, {}
    if os.path.exists(LOOKS):
        lines = open(LOOKS, encoding="utf-8").read().splitlines()
        head = lines[0].split("\t")
        for line in lines[1:]:
            row = dict(zip(head, line.split("\t")))
            had[int(row["retail_display"])] = row["model"]
            if row.get("hide"):
                hide[int(row["retail_display"])] = row["hide"]
    looks, skipped = {}, {}
    for line in open(os.path.join(args.census, "displays.tsv"), encoding="utf-8").read().splitlines()[1:]:
        kind, _id, name, display, fdid, path, status, tex, _geosets = line.split("\t")
        # A look already in the list stays (while the converter takes it), --also or not.
        if status != "new model" and display not in also and int(display) not in had:
            continue
        model = models.get(fdid, {})
        result = model.get("result", "not probed")
        if result != "ok":
            skipped.setdefault(result, set()).add(os.path.basename(path))
            continue
        # A look whose own texture the build lacks (a colour not released yet) would be white.
        if any(isinstance(model["tex"].get(t), str) for t in tex.split(",")[:3]):
            skipped.setdefault("a texture is not in this build", set()).add("%s (%s)" % (name, display))
            continue
        look = looks.setdefault(int(display), {"form": kind, "model": os.path.basename(path)[:-3], "path": path,
                                               "names": []})
        if kind == "mount":
            look["form"] = "mount"  # a look both a mount and a pet wear is kept with the mounts
        if name not in look["names"]:
            look["names"].append(name)
    for display in [d for d, l in looks.items()
                    if args.add_only and d not in had and l["form"] not in (args.add_only, "creature")]:
        skipped.setdefault("new, not a %s (--add-only)" % args.add_only, set()).add(
            "%s (%d)" % (" / ".join(looks[display]["names"]), display))
        del looks[display]
    # A look the list has never goes: its model would take the next one's id, and every model
    # after it would move. A census without --also or --effects can leave one out.
    gone = sorted(set(had) - set(looks))
    if gone:
        sys.exit("%d looks of %s would go (%s): run the census with --effects and the --also files "
                 "they came from" % (len(gone), LOOKS, ", ".join(map(str, gone[:20]))))
    taken = {}
    for display, look in looks.items():
        if display in had:
            look["model"] = had[display]
            taken.setdefault(look["model"], look["path"])
    for display, look in looks.items():
        if display not in had:
            look["model"] = model_name(look["model"], look["path"], taken)
    # Looks already in the list keep their place and new ones go after them: the build numbers
    # models in this order, so the models of a list's earlier looks keep their ids.
    order = {d: i for i, d in enumerate(had)}
    rows = sorted(looks.items(), key=lambda kv: (kv[0] not in order, order.get(kv[0], 0),
                                                 kv[1]["form"], kv[1]["model"], kv[0]))
    with open(LOOKS, "w", encoding="utf-8", newline="\n") as f:
        f.write("display\tretail_display\tform\ttier\tmodel\tname\thide\n")
        for display, l in rows:
            f.write("%d\t%d\t%s\t0\t%s\t%s\t%s\n" % (OFFSET + display, display, l["form"], l["model"],
                                                     " / ".join(l["names"]), hide.get(display, "")))
    print("%d looks (%d mount, %d pet, %d creature) on %d models" % (
        len(rows), sum(1 for _d, l in rows if l["form"] == "mount"), sum(1 for _d, l in rows if l["form"] == "pet"),
        sum(1 for _d, l in rows if l["form"] == "creature"), len({l["model"] for _d, l in rows})))
    for result, names in sorted(skipped.items()):
        print("left out, %s: %s" % (result, ", ".join(sorted(names))))


if __name__ == "__main__":
    main()
