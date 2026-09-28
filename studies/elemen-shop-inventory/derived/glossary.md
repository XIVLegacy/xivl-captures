# elemen-shop-inventory - glossary

Columns and the client join for `derived/shop-sales.csv`. Japanese is verbatim
from `js/db_shop.js`; the EN columns are client cross-checks (see
`evidence-map.md`), not hand-authored glosses.

## shop-sales.csv

One row per item<->seller edge (2,087 rows: 518 items x their sellers). An item's
per-item fields (name, id, price) repeat across its seller rows.

| column | meaning |
|---|---|
| `item_jp` | item name, verbatim (source `_` separators kept as written) |
| `item_en_client` | client EN from `xtx_itemName.csv` |
| `client_item_id` | `xtx_itemName` row id (join-back to `shopItem.csv` / `_item.csv`) |
| `item_match_note` | blank = direct join; `variant:<form>` = joined after a `_`->separator transform; `variant-base:<x>` = joined on the bare base |
| `seller_npc_jp` | selling NPC name, verbatim |
| `seller_npc_en_client` | client EN from `xtx_displayName.csv` |
| `client_npc_id` | `xtx_displayName` row id |
| `npc_match_note` | blank = direct; `prefix-variant:client=...` = matched on personal-name base (site abbreviated the role prefix); `no-client-npc` = gap |
| `seller_city_region` | the city (リムサ・ロミンサ/グリダニア/ウルダハ) or field region the seller stands in |
| `seller_area` | sub-area / camp within the city or region (blank when the source gives only coords) |
| `x`, `y` | player-map coordinates of the seller |
| `source_price` | the source's verbatim price string. Flat gil for most items (duplicates `shopItem.csv`); `A/B/C（備蓄ランク0/1/2）` for the 15 hamlet items - stockpile-rank-scaled pricing that is NOT a flat client value |

## Notes

- The set is the item<->NPC **edge** only. Item names + flat prices are
  client-primary (reach them via `client_item_id`); the seller roster
  (name/coords) is also in `elemen-zone-guide/derived/shops.csv`.
- `source_price` is kept verbatim because 15 rows carry web-unique rank-scaled
  hamlet pricing; the flat-price rows are the source's own annotation, not a
  re-derivation of `shopItem.csv`.
- Patch 1.22 (the section's stated edition), one patch before the 1.23b
  world-down.
