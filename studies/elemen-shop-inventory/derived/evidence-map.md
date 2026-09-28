# Evidence map - eLeMeN FF14 1.x Shop Item-to-NPC Sales Edges - Web Tables

Client-first scoping and cross-check for the eLeMeN - FF14
(`elemen.sakura.ne.jp`) `etc/shopitem/` section - the item -> selling-NPC reverse
index, backed by `js/db_shop.js`. Patch 1.22. Scope: the one
web-unique slice (the item<->NPC sales edges), redundant halves dropped.

## Client-first tiering (what dropped, what stayed)

The section is a 518-item x 154-NPC sales matrix. Against `xivl-client-data`:

Dropped as client-primary:

- **Item names** -> `xtx_itemName.csv` (JP col5 -> EN col6, id col0). Redundant.
- **Flat gil prices** (503 of 518 items) -> `shopItem.csv` (each shop slot carries
  item id + gil). Redundant.
- **Seller NPC names + locations** (154) -> already captured in the sibling set
  `elemen-zone-guide` (`derived/shops.csv` roster). Not re-shipped as a roster.

Kept as web-unique:

- **The item<->NPC "who sells what" edges** (2,087). The client ships
  `shopBase.csv` -> `shopItem.csv` (a shop's inventory grouping + price) and
  `xtx_itemName`, but the binding from a **named NPC** to a `shopBase` inventory
  is not in any decoded `xivl-client-data` sheet (`actorclass` columns are
  empty; the `populace*Shop*` tables are pure greeting dialogue) - it lives in
  the actor-behavior binary. These edges are exactly what `elemen-zone-guide`
  left open when it dropped the per-NPC item inventories. Recovering them lets a
  named shop NPC be matched to its client `shopBase` by item-set intersection.
- **15 rank-scaled hamlet prices** - the `ハムレット関連` items price as
  `A/B/C（備蓄ランク0/1/2）` (stockpile-rank-scaled), not a flat `shopItem.csv`
  gil value. The verbatim `source_price` column preserves these; the 503 flat
  prices in that column duplicate `shopItem.csv` and are kept only as the source's
  own annotation, not as a client-price re-derivation.

Evidence tier: **wiki** (packet captures > video breakdown > wiki) -
CALIBRATION-grade until corroborated by packet/client evidence.

## Client cross-check

| column | client table | join |
|---|---|---|
| item name | `xtx_itemName.csv` | JP col5 -> EN col6, id col0 |
| seller NPC name | `xtx_displayName.csv` | JP col1 -> EN col2, id col0 |

Whitespace-insensitive NFKC. Results:

- **items**: 518/518 resolved to a client item id.
- **edges**: 2,076/2,087 resolved to a client NPC id.
- **sellers**: 154 distinct, all named; the single unresolved seller
  (酒保商人フォルガード) accounts for the 11 unresolved edges.

### Audited overrides (item name variants)

The source writes item-name separators as `_`; the client uses one of several
forms. `item_match_note` records the transform that joined (`variant:<form>`):

- `_` -> `・` (word separator): ウェザード_クロスペインハンマー =
  ウェザード・クロスペインハンマー; グロースフォーミュラ_アルファ =
  グロースフォーミュラ・アルファ.
- `_` -> `＆`: カープ_マグワート = カープ＆マグワート.
- `_X` -> `（X）` (dye variant): 別珍_レイヴン = 別珍（レイヴン）.
- `_X` -> `[X]` (dye code): ウェザードサイブーツ_GR = ウェザードサイブーツ[GR].
- bare base (`variant-base:...`) where no separator form resolved (e.g.
  クァールの粗皮_1 -> クァールの粗皮).

### Genuine client gap (flagged, not guessed)

- **酒保商人フォルガード** (Coerthas / Camp Glory) - not in `xtx_displayName`
  (removed or renamed camp NPC); same gap as `elemen-zone-guide`. 11 edges carry
  the JP name with a blank client id.

### Skipped source tokens

The `db_shop.js` item defs reference `s1`/`s3`/`s4` - these are HTML tooltip
wrappers (`s1 = "...価格:"`, `s3`/`s4` = span tags), not sellers, and are dropped.

## Edition

`etc/shopitem` is annotated ※パッチ1.22対応 - one patch before the 1.23b
world-down. Shop rosters changed little between 1.22 and 1.23b, but treat this
as 1.22 evidence: corroborate against the 1.23b client shop tables before
relying on a specific edge or price.
