# eLeMeN FF14 1.x Site Archive - HTML Mirror of Digested Sections

A consolidated verbatim HTML mirror of the eLeMeN - FF14
(`elemen.sakura.ne.jp/ff14_dated_archives/`) sections represented in this archive,
preserved at their true site paths. eLeMeN is the fragile fan site that preserves
the final 1.x (patch 1.23b) data at the 2012-11-11 world-down and is the primary
source behind every `elemen-*` set. This archive is its preservation and provenance
copy so the source cannot vanish.

## Study contents

- `sources/elemen-site-archive/objects/ff14_dated_archives/<site-path>` - 271 files mirroring the site's
  own directory structure (e.g. `monster/bestiary/Amalj'aa.html`,
  `quest/ClassQuest/Alchemist1.html`, `etc/food/index.html`, plus the shop data
  file `js/db_shop.js`). Bytes are identical to the source pages.
- `derived/url-map.csv` - every archived file -> its exact source URL.
- `derived/file-inventory.csv` - file count per site section.
- `sources/elemen-site-archive/manifest.yaml` - member-level SHA-256 integrity
  anchor over the mirror.

Scope is **the sections represented here**, not the whole site. Each file was
fetched to support an `elemen-*` set or evaluate a candidate section; the
`origin_set` context lives in each page's own breadcrumb and in the sibling sets.

## Start here

- `derived/url-map.csv` - what is here and where it came from.
- Open any `sources/elemen-site-archive/objects/ff14_dated_archives/**/*.html` directly in a browser.

## Source material

The mirror itself is the raw material - the single home for eLeMeN source HTML.
Each `elemen-<topic>` set keeps only its distilled `derived/` output plus its
`sources/elemen-site-archive/objects/pages/*.md` transcriptions and points here via a
`source_refs` entry for `elemen-site-archive`. This set is the browsable,
path-faithful consolidation.

## Promoted conclusions

The path-faithful HTML mirror is the shared source record for the distilled
`elemen-*` studies, and `derived/url-map.csv` supplies their source-URL mapping.
Its promoted role is provenance, not game-content interpretation.

## Topics

Sections mirrored (see `file-inventory.csv` for exact counts):

- `monster/bestiary` (65 monsters + index), `monster/nm` (NM lists)
- `class/action` (7 battle + 11 craft/gather classes), `class/battle`, `class/level`
- `quest/ClassQuest`, `quest/JobQuest`, `quest/MainQuest` detail pages + indexes
- `guildleve/regional` (3 battlecraft-leve pages)
- `etc/area` (28 zones + index), `etc/shopitem` (+ `js/db_shop.js`),
  `etc/playguide` (18), `etc/history`, `etc/food`, `etc/medicine`
- `gamecontents/InstancedRaids`, `PrimalBattle`, `StrongholdandDungeon`,
  `Materia`, `TheGrandCompanies`, `etc`

## Evidence gaps

- **Only pages represented here.** Index-based sections are effectively complete
  (bestiary, area, playguide, actions, food/medicine, history). Detail-page
  sections are partial: `quest` holds the 112 detail pages and 5 indexes the
  reward/walkthrough set used (not every SubQuest); `guildleve` holds the 3
  battlecraft-leve pages (no fieldcraft/tradecraft/local, no regional index).
- **Not mirrored:** the `gear/` section (evaluated and skipped as client-redundant,
  never fetched), and any section outside the digested set.
- **No images.** The site's images live under a separate `ff14_archives/img/`
  subtree and are mostly icons/maps already decoded in the sibling repo's
  [derived icons directory](https://github.com/XIVLegacy/xivl-client-data/tree/main/derived/icons-1.23b); only
  HTML (+ the shop JS) is mirrored here. Internal image `src` and links to
  un-mirrored pages will 404 offline.
- **WAF gaps.** A few resources 403 outright (e.g. `etc/playguide/server.html`,
  `gamecontents/index.html`) and were never fetched.

## Further research

- The mirror remains limited to the fetched sections. The WAF-blocked and
  unfetched pages above are not mirrored.
