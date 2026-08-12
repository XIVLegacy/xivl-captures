# eLeMeN FF14 1.x Zone Guide - Weather, Aetheryte, Adjacency - Web Tables

The web-unique slices of the eLeMeN - FF14 (`elemen.sakura.ne.jp`) `etc/area/`
section: per-zone **weather runtime behavior**, **aetheryte teleport economy**,
**adjacency + transport graph**, **service-NPC and shop-NPC rosters** with
coords, and **sub-map patch-implementation dates**. A client-first comparison found
the map geometry, shop item inventories, and gathering tables redundant with
`xivl-client-data`; these are the parts the client does not carry in usable
form. Full mirror of the web-unique content across all 28 area pages.

## Study contents

Seven derived CSVs (all cross-checked to client ids; see `evidence-map.md`):

- `derived/weather.csv` - 28 zones. The headline payload: which region drives a
  zone's weather, Eorzea-time change timing, sub-area weather independence/
  absence, and special-event weather. There is **no weather table in the client
  at all**.
- `derived/aetheryte.csv` - 25 aetherytes: gil teleport cost (500/1000/2000/4000)
  and served sub-landmarks. `aetheryte.csv` in the client is opaque numeric
  params.
- `derived/adjacency.csv` - 52 zone-to-zone edges with transport mode
  (walk / ferry / airship).
- `derived/service-npcs.csv` - 70 rows: repair / leve-publisher / linkshell /
  retainer-hire / retainer-bell NPCs (or bell placement points) with player-map
  coords.
- `derived/shops.csv` - 154 shop-NPC roster rows (category / venue / NPC /
  coords / patch). Item inventories are client-redundant and dropped.
- `derived/submaps.csv` - 45 displayable sub-maps with implementation patch
  dates.
- `derived/zones.csv` - the 28-zone master list (kind + client place id).

### Client-first tiering (why these slices)

Check `xivl-client-data` FIRST. Dropped as client-primary: map geometry
(`2Dmap_*`), shop item inventories (`shopItem` / `populace*Shop*` /
`xtx_itemName`, plus the site's own `etc/shopitem/`), aetheryte placement
(`aetheryte*`), gathering tables, zone roster (`_zoneParam` /
`zoneGroupParam`), facilities (`xtx_facility`),
NPC dialogue (`populace*` greeting tables). Kept: the runtime/economy/placement
data the client stores only as opaque params or not at all. Full reasoning and
the join stats are in `derived/evidence-map.md`.

Evidence tier: **wiki** (packet captures > video breakdown > wiki) -
CALIBRATION-grade until corroborated by packet/client evidence.

## Start here

- `derived/evidence-map.md` - client-first scoping, the client cross-check, join
  stats, audited overrides, and the genuine gaps.
- `derived/weather.csv`, `derived/aetheryte.csv`, `derived/adjacency.csv`.
- `derived/glossary.md` - columns, notation, the client join.
- `manifest.yaml` `sources` list - the section URL and retrieval date.

## Source material

- `sources/elemen-zone-guide/objects/pages/area-guide.md` - per-zone name / adjacency / weather /
  aetheryte / service NPCs, verbatim (weather icons as `[weatherN]`).
- `sources/elemen-zone-guide/objects/pages/submaps.md`, `sources/elemen-zone-guide/objects/pages/shops.md` - verbatim
  sub-map and shop-roster transcriptions (item inventories dropped).
- Source HTML - preserved verbatim in the `elemen-site-archive` set; see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping.

## Promoted conclusions

Downstream reference work consumes the zone, travel, weather, shop, and
service-NPC tables. Downstream planning names the shop, repair, and aetheryte
tables as inputs for server placement, economy, and teleport work.

## Source note (edition)

`etc/area/` on eLeMeN = the final 1.x state at the 2012-11-11 world-down (patch
1.23b), not ARR - confirmed by the place/NPC joins to the 1.x client tables and
the in-page patch dates (1.18-1.22).

## Weather icons

The source encodes weather types as `weatherN.png` icons with no legend, and the
client has no weather table to resolve them against. The icons are preserved
verbatim as `[weatherN]` tokens - the behavioral text is the payload. The icon
sequence is left as opaque refs, not guessed.

## Topics

- Per-zone weather runtime behavior (region linkage, Eorzea-time timing, sub-area
  rules, special-event weather) - absent from the client.
- Aetheryte teleport economy (gil cost + served landmarks) - client stores as
  opaque params.
- Zone adjacency + transport-mode graph; service/shop NPC placement; sub-map
  patch history.
- Every place joins `xtx_placeName.csv`; every NPC joins `xtx_displayName.csv`.

## Evidence gaps

- No weather-icon legend (source provides none; client has no weather table) -
  icons kept as `[weatherN]` refs.
- Genuine client absences (flagged, not guessed): 船/Ship + its 2 sub-decks and
  the モードゥナ/交信電波塔 landmark (no `xtx_placeName` row); 酒保商人フォルガード
  (no `xtx_displayName` row).
- Placement coords are the site's player-map X/Y (observation), wiki tier ->
  CALIBRATION. Server world coordinates come from packet and spawn observations.
- Client-primary blocks (map geometry, shop inventories, gathering, zone params)
  are deliberately NOT here - reach them via the client ids.

## Further research

- Specific weather rules and teleport costs need packet/client corroboration
  before retail confirmation.
