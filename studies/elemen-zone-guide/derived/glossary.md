# elemen-zone-guide - glossary

Columns, notation, and the client join for the seven derived CSVs. Japanese is
verbatim from the source; every EN column is a client cross-check (see
`evidence-map.md`), not a hand-authored gloss. `(?)` marks a value nothing in the
client resolved.

## Common conventions

- `zone_slug` - the source page stem (apostrophes in filenames written as `_`:
  `Ul_dah`, `U_GhamaroMines`, `Cutter_sCry`).
- `zone_jp` - the zone's Japanese name, verbatim.
- `*_en_client` - the client English for that JP token (`xtx_placeName.csv` for
  places, `xtx_displayName.csv` for NPCs). Blank = no client row.
- `client_place_id` / `client_npc_id` - the client row id for join-back.
- `name_match_note` - blank = direct NFKC join; `prefix-variant:client=...` =
  matched on personal-name base (site abbreviated the role prefix);
  `no-client-place` / `no-client-npc` = genuine gap; `furigana-stripped` = joined
  after removing a `（reading）`.
- Multi-line source prose is flattened to one cell with ` / ` separators.
- `[weatherN]` - a source weather-type icon (`weatherN.png`); no legend provided.

## zones.csv

Master zone list. `zone_en_site` is the source's own EN (shown beside the JP on
the page); `zone_en_client` is the `xtx_placeName` EN. `kind` is one of
`city-state`, `field-region`, `instance`, `transport`.

## adjacency.csv

One row per adjacent-zone edge. `transport_jp` is the source's transit label
(定期船 / 飛空艇 / blank); `transport_en` normalizes it (`ferry` / `airship` /
`walk`). `-` (no adjacency) rows are omitted.

## weather.csv

Per-zone weather runtime behavior - the set's headline web-unique payload.
`linked_region_jp` / `linked_region_en_client` = the region whose weather drives
this zone (`...と連動`). `weather_icons` = the icon sequence on the header line.
`weather_behavior` = the full behavioral text verbatim (linkage, Eorzea-time
change timing, sub-area independence/absence, special-event weather + dates),
icons as `[weatherN]`.

## aetheryte.csv

Aetheryte teleport economy. `gil_cost` = the favorite-registration teleport cost
(500/1000/2000/4000; blank for the home-city aetheryte, which lists `-`).
`served_landmarks_jp` / `_en_client` = the sub-areas that aetheryte teleports to
(` / `-separated, resolved 63/63).

## service-npcs.csv

Zone service NPCs. `service_jp` = the source row label; `service_type`
normalizes it: 修理屋/修理請負 -> `item-repairer`, リーヴ発行 ->
`guildleve-publisher`, リンクシェル発行 -> `linkshell-manager`, リテイナー雇用
-> `retainer-manager`, リテイナー呼び鈴 -> `retainer-bell`. `npc_jp` +
`npc_en_client` + `client_npc_id` are the NPC (retainer-bell rows have no NPC -
they are placement points, `npc_jp` blank). `location_area` / `x` / `y` are the
player-map location (area named when no grid coords are given).

## submaps.csv

Displayable sub-maps per zone with implementation history. `submap_jp` = the
source's map-switch label (verbatim, may be `zone/sub-area` or carry a `（mapN）`
floor suffix). `submap_part_en_client` = the client EN of the sub-area part.
`implement` / `ingame_implement` = the source's patch-date annotations
(`YYYY年M月D日実装（パッチ X.YY）` and the separate in-game-enable date where the
source gives one).

## shops.csv

Shop-NPC roster (placement, not inventory - item lists are client-redundant and
dropped, see `evidence-map.md`). `category` = the source shop grouping
(ギルドショップ / ショップ / マーケット / street or camp name); `venue_jp` = the
shop building/venue (with its `[type]` bracket verbatim); `npc_jp` +
`npc_en_client` + `client_npc_id` = the shop NPC; `location_area` / `x` / `y` =
placement; `implement_patch` = the source's patch-date annotation.
