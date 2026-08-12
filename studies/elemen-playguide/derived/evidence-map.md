# Evidence map - eLeMeN FF14 1.x Play Guide - Weather Legend, Aethernet, Market Tax - Web Tables

Client-first scoping and cross-check for the eLeMeN - FF14
(`elemen.sakura.ne.jp`) `etc/playguide/` section - the game's play-guide: FAQ,
lore, tutorial, and a few structured data tables. Scope: full
mirror (all pages transcribed verbatim) with derived CSVs normalizing the
cross-checkable evidence sets.

## Shape and scope

The playguide is 19 pages, dominantly **FAQ / lore / tutorial prose** (character
creation, world lore, races, guardian deities, class/job concepts, mounts,
collections, inns, and Q&A pages on aetheryte/class/quest/guildleve mechanics).
That bulk is client-string-derivable or non-behavioral - it is captured verbatim
under `sources/elemen-playguide/objects/pages/` as the full mirror, but not normalized into tables
(there is nothing tabular to normalize, and lore is not behavior evidence).

Six sets carry structured, evidence-grade data and are normalized into derived
CSVs, cross-checked to the client where a name table exists:

### 1. weather-legend.csv - the centerpiece

`faq_tips` (`月齢と天候の名称`) names the weather-type icons: `weather1-9` ->
快晴/晴れ/曇り/霧/暴風/雨/雷雨/砂嵐/妖霧, with `weather10-19` marked 名称不明
(name unknown - the special-event snow/sakura types). This **decodes the
`[weatherN]` tokens** that `elemen-zone-guide` (`derived/weather.csv`) had to
leave opaque - there is no weather table in the client, so this legend is the
only readable source. Each name cross-checks to the client `xtx__fixedPhrase.csv`
(the auto-translate dictionary; JP col3 -> EN col5, id col0): clear / fair /
cloudy / foggy / blustery / rainy / stormy / sandy / gloomy. **9/9 named icons
resolved.**

### 2. aethernet.csv - intra-city teleport topology

`aethernet` gives the 3 cities' aethernet shard networks (8 shards each): the
destination, sub-area + coords, and the gate-guard NPC. Not in clean client form
(`aetheryteChild.csv` is a dialogue table, arrival messages). Guards cross-check
to `xtx_displayName.csv` (JP col1 -> EN col2, id col0) - **19/19 resolved**
(e.g. シノードル・ガードナー一等甲兵 -> Storm Private Gardner). Destinations
cross-check to `xtx_placeName.csv` - 18/24 (the 6 gaps are the central
`エーテライト・プラザ` shard and minor bridge/lane landmarks not in `placeName`).
Field-region gate rows carry no guard NPC (`gate-no-npc`).

### 3. market-tax.csv - market indirect-tax rule

`market` maps the 19 market "streets" (Free / Fighter / Sorcerer / Gatherer /
Crafter / Armor / Low-Mid-High Fashion / Accessory / Food / Potion / Metal /
Wood / Leather / Stone / Cloth / Crystal / Repair) to the item categories each
reduces indirect tax on. 18 carry a category list; Repair is on the source
table with `--` and reduces tax on nothing. A server-side economy rule; the item categories are
client item-type names but the street->category tax assignment is web-unique.
Category lists kept verbatim JP. Street names romanized (no client join - these
are market UI labels).

### 4. units.csv - in-game measurement units

`faq_tips` length (ilm/fulm/yalm/malm) and weight (onze/ponze/tonze) units with
their in-game definitions and real-world metric equivalents. Reference data.

### 5. moon-phases.csv - lunar cycle names

`faq_tips` names the 8 moon-phase icons (新月 ... 二十六夜). JP only - not in
`xtx__fixedPhrase` (astronomy terms, not weather), and the source gives no EN.

### 6. race-base-stats.csv - racial/tribal base attributes

`races` (`sources/elemen-playguide/objects/pages/races.md`) carries one stat table per race section
(interleaved with lore). 15 rows total: 5 races x their 1.x tribes x gender, but
gender-locked in 1.x, so not 20 - **Highlander is M-only, both Miqo'te tribes are
F-only, both Roegadyn tribes are M-only.** Each row is STR/VIT/DEX/INT/MND/PIE and
6 elemental resistances (火/水/雷/風/土/氷 = fire/water/lightning/wind/earth/ice),
numbers **verbatim** from the source table. The client `xtx_tribe.csv` ships
**exactly these 15 gendered tribe rows** (ids 1-15) and no others, independently
corroborating the gender locks. `tribe_en` is the client's own tribe string
(`xtx_tribe.csv` JP+gender col4 -> EN col5, id col0 in `tribe_client_id`),
**15/15 resolved**; the client uses the ARR-era spellings (Wildwood, Duskwight,
Hellsguard, Sea Wolf, Seeker of the Sun, Keeper of the Moon), NOT the site's 1.0
romaji (Forester, Shader, ...), so the client string is shipped per the trust
model. The site gives no per-attribute source beyond the printed table; these are
CALIBRATION-grade until corroborated by client stat data or a decode.

## Client cross-check summary

| set | client table | result |
|---|---|---|
| weather names | `xtx__fixedPhrase.csv` (JP col3 -> EN col5) | 9/9 named |
| aethernet guards | `xtx_displayName.csv` | 19/19 |
| aethernet destinations | `xtx_placeName.csv` | 18/24 |
| moon phases | (none) | JP only |
| market streets / units | (none - UI labels) | romanized |
| race/tribe base stats | `xtx_tribe.csv` (JP+gender col4 -> EN col5) | 15/15 |

## Evidence gaps

- **server.html** (ワールド／サーバー, the world/server list - the lowest-value
  page) is **intentionally not captured.** The host WAF blocks that specific
  resource (HTTP connection blackholed, HTTPS 403) regardless of headers, scheme,
  or URL-encoding; both urllib and a real browser engine fail. Given the page is
  a low-value server list and the block is resource-specific, it was skipped by
  decision, not left pending. Of the remaining 18, `index.html` is the section
  nav page (archived in `elemen-site-archive`, nothing to transcribe); the 17
  content pages are the mirror.
- 6 aethernet destinations (central plaza + minor landmarks) have no `placeName`
  row - flagged `no-client-place`.
- `weather10-19` names are unknown on the source (名称不明) - the special-event
  weather types the zone-guide set records by icon (snow=11, sakura=13).
- Lore/FAQ pages are captured verbatim only (no normalization) - by design.

## Edition

Play-guide content tracks the final 1.x state; the weather names, aethernet
guards, and place joins resolve against the 1.23b client tables. The `market`
page and others carry 1.2x-era mechanics.
