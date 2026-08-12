# elemen-playguide - glossary

Columns for the derived CSVs. Japanese is verbatim from the source; EN
columns are client cross-checks (see `evidence-map.md`) except where noted as
romanized UI labels. The 17 verbatim page transcriptions under
`sources/elemen-playguide/objects/pages/` are the full mirror of the FAQ/lore prose.

## weather-legend.csv

Decodes the `[weatherN]` tokens in `elemen-zone-guide/derived/weather.csv`.

| column | meaning |
|---|---|
| `weather_icon` | the `weatherN` icon token (matches the zone-guide `weather_behavior`) |
| `name_jp` | the source's weather-type name; blank for `weather10-19` (名称不明) |
| `name_en_client` | client EN from `xtx__fixedPhrase.csv` |
| `client_fixedphrase_id` | `xtx__fixedPhrase` row id |
| `match_note` | blank = joined; `unknown-on-source` = the source gives no name |

## aethernet.csv

Intra-city aethernet shard network, one row per shard.

| column | meaning |
|---|---|
| `city` | home city (リムサ・ロミンサ / グリダニア / ウルダハ) |
| `destination_jp` | shard destination name, verbatim (`（※n）` gate markers kept) |
| `destination_en_client` / `client_place_id` | `xtx_placeName` join |
| `location_area` | sub-area within the city (or field region for gate rows) |
| `x`, `y` | player-map coordinates |
| `guard_npc_jp` | the aethernet gate-guard NPC (blank for field-region gates) |
| `guard_npc_en_client` / `client_npc_id` | `xtx_displayName` join |
| `match_note` | `gate-no-npc` = a field-region gate with no guard; `no-client-place` = destination not in `placeName` |

## market-tax.csv

The market indirect-tax reduction rule, one row per market street.

| column | meaning |
|---|---|
| `street_jp` | market-street name (naming differs per city: ～街 / ～通り / ～横町; the site lists the category label) |
| `street_en` | romanized street label |
| `level_band` | equipment level band for the fashion streets (レベル1～20 / 21～40 / 41以上); blank otherwise |
| `reduced_categories_jp` | the item categories whose indirect tax this street reduces, verbatim |

## units.csv

In-game measurement units.

| column | meaning |
|---|---|
| `system` | `length` or `weight` |
| `unit_jp` | unit name (イルム/フルム/ヤルム/マルム; オンズ/ポンズ/トンズ) |
| `abbr` | source abbreviation (Im/Fm/Ym/Mm; Oz/Pz/Tz) |
| `definition` | the in-game definition (e.g. `12イルム`) |
| `metric` | real-world equivalent (e.g. `30.48センチ`) |

## moon-phases.csv

The 8 lunar-cycle phase names (`moon_icon`, `phase_jp`). JP only - no client
name table carries them.
