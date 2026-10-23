# Retail Library

The models of the mounts and battle pets of later expansions, converted for the 3.3.5a client of
an [AzerothCore](https://www.azerothcore.org/) (WotLK 3.3.5a) server: 3,147 looks on 1,169 models,
every retail mount and pet look (retail 12.1.0) that the converter can take and that a 3.3.5a
client with an HD creature pack doesn't already have. The list was made against such a client;
the census below makes one against yours.

This is a library, not a feature. It puts the models in the client and tells the server their
display ids, and that is all: nothing here is learnable, sold or dropped. A mount or a pet a
player can own is a spell, an item and a source on top of one of these displays, and that belongs
in a module of its own (the way
[wow-mod-retail-pets](https://github.com/buildthehomelab/wow-mod-retail-pets) does its red
pandas).

- **A look's display id is 200000 + its retail display id.** The Chaos-Forged Gryphon is retail
  display 123098, so it is display 323098 here. An id never moves, and anything that names a
  retail display (Wowhead, wago.tools, Blizzard's API) names ours.
- [`data/looks.tsv`](data/looks.tsv) lists every look: its display id, retail display id, whether
  retail uses it for a mount or a pet, the model, and the retail names that wear it.
- To see one in game: `.morph 323098` on yourself, or `.npc set model 323098` on a creature.

## What it is not

- **Not checked in a client yet.** Every model passes the converter's own checks (the ones that
  catch what crashes or hangs a 3.3.5a client), and each look was drawn from its converted model
  and put next to Blizzard's picture of it. How they move, where a rider sits and how they sound
  has not been looked at.
- **Not every effect.** The models keep their particles, ribbons, lights and most glows and
  shines (`"effects": true` in [`pack.json`](pack.json), an option of the converter). Left out:
  - emitters that spawn other models, draw a creature skin slot, or are of a kind 3.3.5a lacks;
  - a multi-texture emitter's second and third textures (it draws its first);
  - glows and shines that retail limits to the first texture's alpha (among them a common
    environment-map shine), which 3.3.5a can't draw as a pass of their own.
- **No fourth skin texture.** 124 looks use one, and 3.3.5a's display rows have only three.
- **No sounds and no footprints.** The rows carry none, so that hundreds of unlike models don't
  all growl like the one stock creature they were cloned from. A module that turns a look into a
  mount gives it its sound.
- **Not every mount and pet.** Left out:
  - what the client already has (retail's own looks from before Cataclysm, and what the HD
    pack added);
  - nine models the converter refuses (the Tauralus mounts, two Gladiator's Drakes and a few
    more);
  - four models and two looks that are in retail's tables but not in its live build yet;
  - the dragonriding drakes and other looks that are not creature models;
  - looks that need only new textures on a model the client has.

## Installing

Server: clone this repo into the server's `modules` folder under the name `mod-retail-library`
(AzerothCore names the module's loader after its folder), then rebuild:

```bash
cd modules
git clone https://github.com/buildthehomelab/wow-mod-retail-library.git mod-retail-library
```

The module has no code of its own; its SQL
([`data/sql/db-world`](data/sql/db-world/mod_retail_library.sql)) gives the server the display
and model rows, which it checks every creature display against.

Client: two patches, built by the tools below and not stored here. The names are examples; any
two names work if the small one loads after every other patch that ships any of the same tables.

| Patch | Holds | Size |
|---|---|---|
| `patch-z72-retail-library.MPQ` | the models and textures, under `Creature\RetailLibrary` | 2.5 GB |
| `patch-z75-retail-looks.MPQ` | `CreatureDisplayInfo.dbc` and `CreatureModelData.dbc` with the looks' rows, and `ParticleColor.dbc` with their particle colours | under 1 MB |

The split is on purpose. A patch replaces whole files, so the small one has to be rebuilt on the
client's current tables whenever another patch adds rows to them, and it has to load after every
other patch that ships them. The big one never changes for that.

## Requirements

- An AzerothCore (WotLK 3.3.5a) server.
- The two client patches in every player's `Data` folder. A player without them sees nothing where
  one of these looks is.
- To build the patches: Python 3.10+, [StormLib](https://github.com/ladislav-zezula/StormLib), and
  [wow-mod-retail-creatures](https://github.com/buildthehomelab/wow-mod-retail-creatures).

## Building

With [wow-mod-retail-creatures](https://github.com/buildthehomelab/wow-mod-retail-creatures)
cloned next to this repo:

```bash
# what the client has, and what retail has that it lacks
python3 ../mod-retail-creatures/tools/client_files.py --client <WoW folder> --out <client dir> [your own patches, in load order]
RETAIL_SOURCE=cdn python3 ../mod-retail-creatures/tools/census.py --cache ~/retail-cache --client <client dir> --out <census dir> --models
# the look list, then the patches and the SQL
python3 tools/inventory.py --census <census dir>
RETAIL_SOURCE=cdn python3 ../mod-retail-creatures/tools/build_patch.py --pack . --dbc <client dir> --cache ~/retail-cache --work <work dir> --out patch-z75-retail-looks.MPQ --data-dir <out dir> --sql data/sql/db-world/mod_retail_library.sql
```

`client_files.py` doesn't copy `ParticleColor.dbc`: put it into `<client dir>` yourself, from the
last patch that ships one or else the client's own (`Data\enUS\patch-enUS-2.MPQ` in the stock
client). Without it the build only warns, and the looks whose particles take their colours from
the display come out the wrong colour, or white.

The build downloads about 5 GB from Blizzard's CDN the first time and takes a quarter of an hour.

## Removing

Run [`data/sql/uninstall/mod_retail_library_uninstall.sql`](data/sql/uninstall/mod_retail_library_uninstall.sql)
on the world database, remove the module folder and rebuild.

## Patch Notes: Retail Model Library

Category: Collections

- The game client now carries the models of more than three thousand mounts and companions from
  later expansions. None of them can be collected yet: they are there so that new mounts and
  companions can be added without another large download.
- They come with their **effects**: flames, sparkles, smoke and trails, and glowing eyes and
  runes.

## Credits

- Models and textures: Blizzard Entertainment, downloaded at build time; nothing of theirs is
  stored in this repo.
- Converter and patch builder:
  [wow-mod-retail-creatures](https://github.com/buildthehomelab/wow-mod-retail-creatures).

## License

MIT. See [LICENSE](LICENSE).
