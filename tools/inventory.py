#!/usr/bin/env python3
"""Write data/looks.tsv from a census: every retail mount and battle pet look the client lacks
and the converter takes.

    python3 inventory.py --census <census out dir>

The census is wow-mod-retail-creatures' tools/census.py run with --models against your
client: its displays.tsv lists every look, its models.json what the converter made of each model.
A look's 3.3.5 display id is 200000 + its retail display id, so it never moves, whatever is
added or dropped later, and anything that knows a retail display knows ours.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOOKS = os.path.join(HERE, "..", "data", "looks.tsv")
OFFSET = 200000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", required=True)
    args = ap.parse_args()
    models = json.load(open(os.path.join(args.census, "models.json")))
    looks, skipped = {}, {}
    for line in open(os.path.join(args.census, "displays.tsv"), encoding="utf-8").read().splitlines()[1:]:
        kind, _id, name, display, fdid, path, status, tex, _geosets = line.split("\t")
        if status != "new model":
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
        look = looks.setdefault(int(display), {"form": kind, "model": os.path.basename(path)[:-3], "names": []})
        if kind == "mount":
            look["form"] = "mount"  # a look both a mount and a pet wear is kept with the mounts
        if name not in look["names"]:
            look["names"].append(name)
    rows = sorted(looks.items(), key=lambda kv: (kv[1]["form"], kv[1]["model"], kv[0]))
    with open(LOOKS, "w", encoding="utf-8", newline="\n") as f:
        f.write("display\tretail_display\tform\ttier\tmodel\tname\n")
        for display, l in rows:
            f.write("%d\t%d\t%s\t0\t%s\t%s\n" % (OFFSET + display, display, l["form"], l["model"], " / ".join(l["names"])))
    print("%d looks (%d mount, %d pet) on %d models" % (
        len(rows), sum(1 for _d, l in rows if l["form"] == "mount"), sum(1 for _d, l in rows if l["form"] == "pet"),
        len({l["model"] for _d, l in rows})))
    for result, names in sorted(skipped.items()):
        print("left out, %s: %s" % (result, ", ".join(sorted(names))))


if __name__ == "__main__":
    main()
