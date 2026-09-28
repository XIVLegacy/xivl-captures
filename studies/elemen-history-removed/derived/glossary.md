# elemen-history-removed - glossary

Columns for `derived/history-removed.csv`. Japanese is verbatim from the source;
the item EN is a client cross-check (see `evidence-map.md`).

## history-removed.csv

The 190 Lodestone History milestones marked `現在は取得不可能` (currently
unobtainable) - the removed-system / past-content records.

| column | meaning |
|---|---|
| `category_jp` | source category (クエスト / シーズナルイベント / その他イベント / フィジカル / クラスとレベル) |
| `category_en` | Quest / Seasonal Event / Other Event / Physical Level / Class and Level |
| `title_jp` | the History milestone title, verbatim |
| `display_text_jp` | the full log line, verbatim (`[Your Name]` placeholder kept) |
| `event_item_jp` | for event rows, the item named as obtained (`「ITEM」を入手`); blank otherwise |
| `event_item_en_client` | client EN from `xtx_itemName.csv`; blank if the item is absent from the 1.23b client |
| `client_item_id` | `xtx_itemName` row id; **blank on a non-blank `event_item_jp` = a removed event-exclusive item** (the historical payload) |

## Notes

- Only `現在は取得不可能` rows are included; the live achievement-overlapping
  ladders are client-primary (`xtx_achievement.csv`) and out of scope.
- The removed **Shield class** (盾, Class and Level rows) and the **physical-level**
  ladder have no client join - their absence from the 1.23b client is the point.
- Wiki tier -> CALIBRATION; this is a historical record.
