# eLeMeN FF14 1.x Play Guide - Weather Legend, Aethernet, Market Tax - Web Tables

A full mirror of the eLeMeN - FF14 (`elemen.sakura.ne.jp`) `etc/playguide/`
section - the game's play-guide (FAQ, lore, tutorial, plus a few structured data
tables). All pages are transcribed verbatim. Six sets carry structured,
cross-checkable evidence and are normalized into derived CSVs. The centerpiece is
the **weather-icon legend**, which decodes the `[weatherN]` tokens left opaque in
`elemen-zone-guide`.

## Study contents

Six derived CSVs (client cross-checked where a name table exists):

- `derived/weather-legend.csv` - `weather1-9` -> name -> client EN (via
  `xtx__fixedPhrase`); `10-19` unknown on source. **Decodes the zone-guide
  `[weatherN]` tokens.** There is no weather table in the client, so this is the
  only readable legend.
- `derived/aethernet.csv` - the 3 cities' intra-city aethernet shard networks
  (24 shards): destination, sub-area + coords, gate-guard NPC. Guards 19/19 to
  `xtx_displayName`.
- `derived/market-tax.csv` - the 19 market streets -> the item categories each
  reduces indirect tax on (a server economy rule). Repair is on the source
  table with no categories.
- `derived/units.csv` - in-game length/weight units (ilm/fulm/yalm/malm,
  onze/ponze/tonze) with metric equivalents.
- `derived/moon-phases.csv` - the 8 lunar-cycle phase names.
- `derived/race-base-stats.csv` - the 15 selectable tribe/gender combinations
  with their six base attributes, six elemental resistances, and client tribe
  id. Attributes sum to 90 per tribe. Gender is a row because 1.x locked
  several tribes to one gender (Highlander male, both Miqo'te female, both
  Roegadyn male); the attribute values themselves do not vary by gender.
  A presentation of these stats as a flat 17 baseline plus a per-clan
  modifier, summing to 120, is this same table with 5 added to every
  attribute - a rescale, not a second source, so it cannot corroborate this
  one. Such a restatement also drops the resistances and the gender locks,
  which exist only here.

## Source material

- `sources/elemen-playguide/objects/pages/*.md` - verbatim transcriptions of all 17 captured content
  pages: the FAQ/lore/tutorial prose (character creation, world lore, races,
  guardian deities, class/job concepts, mounts, collections, inns, bookshelf,
  market, aethernet, and the aetheryte/class/quest/guildleve/micromenu Q&A).
  These are the full mirror. The lore is captured but not normalized (nothing
  tabular. Lore is not behavior evidence).
- Source HTML - preserved verbatim in the `elemen-site-archive` set; see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping. This set
  carries no HTML of its own, per the eLeMeN intake rule.

### Client-first tiering

The playguide is dominantly FAQ/lore/tutorial prose - client-string-derivable or
non-behavioral. It is mirrored verbatim but only the six structured sets are
normalized and cross-checked. See `derived/evidence-map.md` for the per-study
reasoning and join stats.

Evidence tier: **wiki** (packet captures > video breakdown > wiki) -
CALIBRATION-grade until corroborated by packet/client evidence.

## Promoted conclusions

`derived/weather-legend.csv` decodes the source weather tokens used by
`elemen-zone-guide`. The aethernet network is also a wiki input. Market tax and
race-base-stat rows remain uncorroborated.

## Start here

- `derived/evidence-map.md` - scope, per-study client-first reasoning, joins.
- `derived/weather-legend.csv` (+ `elemen-zone-guide/derived/weather.csv`),
  `derived/aethernet.csv`, `derived/market-tax.csv`.
- `derived/glossary.md` - columns and the client joins.

## Topics

- weather-icon legend: `weather1-9` names and their client EN, the decoder for
  the `[weatherN]` tokens in `elemen-zone-guide`
- aethernet: the 3 cities' 24 intra-city shards, sub-areas, coords, gate guards
- market streets: the 19 streets and the item categories each reduces indirect
  tax on
- in-game units: ilm / fulm / yalm / malm, onze / ponze / tonze, with metric
  equivalents
- lunar cycle: the 8 moon-phase names
- race and tribe base stats: Midlander, Highlander, Wildwood, Duskwight,
  Plainsfolk, Dunesfolk, Seeker, Keeper, Sea Wolf, Hellsguard

## Related studies

- **`elemen-zone-guide`** - `weather-legend.csv` here decodes that study's
  `[weatherN]` weather-behavior tokens; the aethernet guards extend its shop/
  service-NPC placement layer.
- **`elemen-shop-inventory`** - the market-tax rule pairs with the shop economy.

## Source note (edition)

Play guide content tracks the final 1.x state. The weather names, aethernet
guards, and place joins resolve against the 1.23b client tables.

## Evidence gaps

- **server.html** (world/server list, the lowest-value page) is **intentionally
  not captured** - the host WAF blocks that specific resource (HTTP blackhole,
  HTTPS 403) and it is a low-value server list. Skipped by decision. The other 17
  pages are captured.
- `weather10-19` names are unknown on the source (the special-event types).
- 6 aethernet destinations (central plaza + minor landmarks) have no `placeName`
  row.
- Lore/FAQ pages are verbatim-only, not normalized (by design).

## Further research

- The market-tax rule and specific aethernet placements need packet/client
  corroboration before retail confirmation.
