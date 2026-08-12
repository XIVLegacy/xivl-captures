# eLeMeN FF14 1.x History - Removed-System Milestones - Web Tables

The narrow historical slice of the eLeMeN - FF14 (`elemen.sakura.ne.jp`)
`etc/history/` section: the **`現在は取得不可能` (currently unobtainable)**
Lodestone History milestones - the records of removed systems and past content
the client's achievement system does not preserve. A client-first recon found the
History feed's live progression ladders substance-redundant with the client
achievement system. These records for removed systems are the part that clears the bar.

## Study contents

- `derived/history-removed.csv` - 190 removed/unobtainable History milestones:
  the removed **Shield class** (盾, Lv5-50) and **physical-level** (Lv5-50)
  ladders, past **seasonal/other events** (42 + 11), and discontinued **quest**
  milestones (117). Event rows carry the obtained item, cross-checked to
  `xtx_itemName`.
- `derived/glossary.md`, `derived/evidence-map.md`.

## Source material

- `sources/elemen-history-removed/objects/pages/history-removed.md` - the `現在は取得不可能` rows
  transcribed verbatim.
- Source HTML - preserved verbatim in the `elemen-site-archive` set; see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping. This set
  carries no HTML of its own, per the eLeMeN intake rule.

### Client-first tiering (why only the unobtainable rows)

The History section is a deprecated Lodestone milestone feed, superseded by the
achievement system the client ships (`xtx_achievement.csv`, with EN + structure).
The live progression ladders (kill/level/gil/leve/quest counts) are
substance-redundant with it and were dropped. Kept: the 190 `現在は取得不可能`
rows - removed systems (Shield class, physical level) and past events the
achievement system never carried. See `derived/evidence-map.md`.

Evidence tier: **wiki** (packet captures > video breakdown > wiki) -
CALIBRATION-grade. It is a historical provenance record.

## Promoted conclusions

`derived/history-removed.csv` is the historical record for removed Shield,
physical-level, event, and quest milestones. The rows remain CALIBRATION-grade
pending corroboration against retail evidence.

## The removed-content signal

16 of 43 event items do **not** resolve to a 1.23b client item id - not a join
failure but the payload: removed event-exclusive items (summer 水着 swimsuits,
浴衣 yukata sets, 下駄, Moonfire/Chocobo-egg rewards) absent from the final
client. A blank `client_item_id` on a non-blank `event_item_jp` means "existed
then, gone now." The removed Shield class and physical-level ladders likewise
have no client join - their absence is the evidence.

## Start here

- `derived/evidence-map.md` - scoping, the client cross-check, the removed-content
  reasoning.
- `derived/history-removed.csv`, `derived/glossary.md`.

## Topics

- removed **Shield class** (盾) rank ladder, Lv5-50
- removed **physical level** ladder, Lv5-50 - dropped in the 1.0 -> 1.x transition
- past seasonal events and their exclusive items: Moonfire Faire 水着 swimsuits,
  浴衣 yukata sets, 下駄, Chocobo-egg rewards
- discontinued quest milestones (117 rows)
- `現在は取得不可能` (currently unobtainable) as the selection criterion

## Related evidence

- The **live** History ladders are client-primary: `xtx_achievement.csv` /
  `achievement.csv` / `xtx_title.csv` (the achievement system that superseded the
  History feed).
- Event items reach the client via `client_item_id` -> `xtx_itemName.csv`.

## Source note (edition)

Physical level was removed in the 1.0 -> 1.x transition. The Shield class and the
listed events are 1.x-era. The 27 resolvable event items confirm the 1.x client
join. The `ingame.html` in-game-log variant carries the same History content and
was not separately harvested.

## Evidence gaps

- Only `現在は取得不可能` rows are here; the live achievement-overlapping ladders
  are not included because `xtx_achievement.csv` is client-primary.
- 16 removed event items have no client id (that is the historical record).
- Wiki tier -> CALIBRATION.

## Further research

- This ladder is the retail-observed milestone record for the removed Shield class
  and physical-level system. Packet or client evidence from the 1.0 era would provide
  corroboration.
