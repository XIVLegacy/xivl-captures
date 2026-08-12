# Evidence map - eLeMeN FF14 1.x Zone Guide - Weather, Aetheryte, Adjacency - Web Tables

Client-first scoping and cross-check for the eLeMeN - FF14
(`elemen.sakura.ne.jp`) `etc/area/` section (28 per-zone pages: 4 city-states,
5 field regions, 18 dungeons/instances, 1 ship). Tier
decision: full mirror of the web-unique slices, client-redundant blocks dropped.

## Client-first tiering (what dropped, what stayed)

Check `xivl-client-data/csv/` FIRST. The area pages carry three blocks - an
area guide, a map, and a shop list. Most of it is client primary evidence:

Dropped as client-redundant:

- **Map geometry / markers** (the map block) -> `2Dmap_data.csv`,
  `2Dmap_marker.csv`, `2Dmap_piece.csv`, `mapNavi_data.csv`,
  `2Dmap_actor_data.csv`. The source states its map block only shows the in-game
  map-open overlay.
- **Shop item inventories** (the JS-rendered `ショップ一覧` item lists) ->
  `shopItem.csv`, `shopBase.csv`, `populaceGuildShop.csv`,
  `populaceCompanyShop.csv`, `populaceShopSalesman.csv`, `gcSealShopItem.csv`,
  `blackMarket.csv`; item names -> `xtx_itemName.csv`. The page itself links to
  the site's separate `etc/shopitem/` reverse-lookup for this.
- **Aetheryte existence/placement** -> `aetheryte*.csv`. **Gathering-item
  tables** (field pages) -> client gathering sheets. **Zone roster/names** ->
  `_zoneParam.csv` / `zoneGroupParam.csv` / `_region.csv`. **Facilities** ->
  `xtx_facility.csv`. **NPC
  dialogue** -> the `populace*.csv` tables (these are greeting-line tables, not
  rosters - confirmed).

Kept as web-unique (client stores these as opaque params, or has no table):

- **Weather runtime behavior** - there is **no weather table anywhere in the
  client** (zero `weather`/`tenki` files; the noun hits are dialogue strings).
  The source carries the readable rules: which region drives a zone's weather,
  change timing (Eorzea 0/8/16h), sub-area weather independence/absence, and
  special-event weather (snow/sakura) with implementation dates.
- **Aetheryte teleport economy** - the gil cost tiers (500/1000/2000/4000) and
  the sub-landmarks each aetheryte teleports to. `aetheryte.csv` is opaque
  numeric params with no readable cost or served-landmark list.
- **Adjacency + transport mode** - which zones connect and by what means
  (walk / 定期船 ferry / 飛空艇 airship). `mapObjPortDoor` / `populaceFlyingShip`
  are only the transit dialogue, not an adjacency graph.
- **Service-NPC roster** (repair / leve-publisher / linkshell / retainer-hire /
  retainer-bell) with personal names + player-map coords - not in readable
  client form.
- **Shop-NPC roster** (category / venue / NPC / coords / patch) - the placement,
  not the inventory. Also not in readable client form.
- **Sub-map roster + patch-implementation dates** - history/provenance the client
  never carried.

Evidence tier: **wiki** (packet captures > video breakdown > wiki) -
CALIBRATION-grade until corroborated by packet/client evidence.

## Client cross-check

Every name column is cross-checked against `xivl-client-data`,
whitespace-insensitive NFKC:

| column | client table | join |
|---|---|---|
| zone / region / sub-area / landmark / aetheryte-camp names | `xtx_placeName.csv` | JP col1 -> EN col2, id col0 |
| service-NPC / shop-NPC personal names | `xtx_displayName.csv` | JP col1 -> EN col2, id col0 |
| weather type | (none) | no client weather table exists |

Join results:

- **zones**: 27/28 to a client place id (船/Ship is a generic transport zone,
  not a client place).
- **adjacency**: 52/52 adjacent zones resolved.
- **aetheryte**: 25/25 camps resolved; **63/63** served landmarks resolved.
- **service NPCs**: 55/55 named entries resolved (retainer-bell rows are
  locations, not NPCs).
- **shop NPCs**: 153/154 named resolved.
- **sub-maps**: 42/45 resolved (the sub-area part after `/`, `（...）` suffixes
  stripped).

### Audited overrides

The shop list abbreviates role prefixes (the page warns it omits words for
space), so four shop NPCs carry a site role-prefix that differs from the client
while the personal name is identical - matched on the personal-name base and
noted in `name_match_note` (`prefix-variant:client=...`):

- 板金商フェーズギム = client 甲冑商フェーズギム (Faezghim, 1600070)
- 画屋ゴールディヴ = client 面屋ゴールディヴ (Goldyve, 1100079)
- 板金商オディブランド = client 甲冑商オディブランド (Odibrand, 2200193)
- 板金商イゾルド = client 甲冑商イゾルド (Isaulde, 1300119)

### Genuine client gaps (flagged, not guessed)

- **船 / Ship** - generic transport zone, no `xtx_placeName` row; 2 ship
  sub-decks (船内 / 甲板) likewise absent.
- **モードゥナ/交信電波塔** - landmark not in `xtx_placeName`.
- **酒保商人フォルガード** (Coerthas / Camp Glory) - not in `xtx_displayName`
  (removed or renamed camp NPC); the client has many other 酒保商人.

## Weather icons

The source encodes weather types as `weatherN.png` icons (17 distinct across the
section) and provides no legend on the area pages. The icons are preserved
verbatim as `[weatherN]` tokens - the behavioral text (linkage, timing, sub-area
rules) is the payload; the icon sequence is the per-zone weather roster.

**Legend (decoding these tokens): `elemen-playguide/derived/weather-legend.csv`.**
The playguide's `faq_tips` names weather1-9 (快晴/晴れ/曇り/霧/暴風/雨/雷雨/砂嵐/
妖霧, cross-checked to the client `xtx__fixedPhrase.csv`: clear/fair/cloudy/foggy/
blustery/rainy/stormy/sandy/gloomy); weather10-19 are unnamed on the source (the
special-event types - snow=11, sakura=13 per the behavior text here).

## Edition

`etc/area/` on eLeMeN = the final 1.x state at the 2012-11-11 world-down (patch
1.23b), confirmed by the place/NPC joins to the 1.x client tables and the
in-page patch dates (1.18-1.22). The 1.x aetheryte teleport economy and per-zone
weather behavior are the durable payloads.
