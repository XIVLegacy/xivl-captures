# Evidence map - eLeMeN FF14 1.x History - Removed-System Milestones - Web Tables

Client-first scoping and cross-check for the eLeMeN - FF14
(`elemen.sakura.ne.jp`) `etc/history/` section - the Lodestone "History"
milestone feed. Scope: the narrow historical slice (the
removed-system records), the rest dropped.

## Client-first tiering

The History section is a deprecated Lodestone milestone-notification feed (~951
rows across 42 tables: kill counts, NM, leves, gil rewards, quests, seasonal/
other events, physical level, class-and-level). It is **superseded by the
achievement system**, which the client ships as primary evidence -
`xtx_achievement.csv` (748 rows, named + ranked + EN: "勝利の栄光：ランク1 /
To Crush Your Enemies I / Defeat 100 enemies"), `achievement.csv`, `xtx_title.csv`.

The History strings themselves are not in the client (the exact templates return
zero hits), but the progression milestones (kill/level/gil/leve/quest ladders)
are substance-redundant with the client achievement system, which carries EN and
structure the History feed lacks. Those achievement-overlapping ladders were
**dropped**.

Kept: the **`現在は取得不可能` (currently unobtainable) rows only** - 190 records
of removed systems and past content the achievement system does not preserve:

| category | rows | what it preserves |
|---|---|---|
| Quest (クエスト) | 117 | discontinued quest milestones |
| Seasonal Event (シーズナルイベント) | 42 | past seasonal-event item grants |
| Other Event (その他イベント) | 11 | past one-off event milestones |
| Physical Level (フィジカル) | 10 | the removed 1.0 physical-level ladder (Lv5-50) |
| Class and Level (クラスとレベル) | 10 | the **removed Shield class** (盾, Lv5-50) |

Evidence tier: **wiki** (packet captures > video breakdown > wiki) -
CALIBRATION-grade; this is a historical/provenance record.

## Client cross-check

The one column with a client join is the event-item name: the seasonal/other-event
display texts name the item obtained (`イベント「X」で「ITEM」を入手`). Items join
`xtx_itemName.csv` (JP col5 -> EN col6, id col0), NFKC.

- **27/43** event items resolve to a client item id (e.g. エッグキャップ ->
  Pristine Egg Cap 8012801).
- **16/43** do **not** resolve - and that is the payload, not a join failure:
  they are removed event-exclusive items absent from the 1.23b client (the
  summer 水着 swimsuits, 浴衣/股引 yukata sets, 下駄, ムーンマウス /
  チョコボエッグリング event rewards, モーグリキャップ, etc. - confirmed absent).
  A blank `client_item_id` on a non-blank `event_item_jp` means "existed at the
  time, gone from the final client."

The removed **Shield class** and **physical-level** ladders have no client join
(the systems no longer exist) - that absence is the evidence.

## What was dropped and why

- The achievement-overlapping progression ladders (kill counts, class levels for
  live classes, gil rewards, leve/NM/quest counts) - substance-redundant with the
  client achievement system, reach them via `xtx_achievement.csv`.
- Conditional-availability notes (GC-affiliation, start-city, "取得不可能 only if
  started in X") are not `現在は取得不可能` and are out of scope for this set.
- The `ingame.html` variant (the in-game-log form of the same History) - same
  content, not separately harvested.

## Edition

The removed records predate the 1.23b world-down (physical level was removed in
the 1.0 -> 1.x transition; the Shield class and the listed events are 1.x-era).
The 27 resolvable event items confirm the 1.x client join.
