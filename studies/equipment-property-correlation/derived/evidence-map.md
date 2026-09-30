# Equipment transition census evidence map

## Corpus accounting

The deterministic census covers all 54 canonical captures. It matched 158 balanced 0x0146/0x0147 scopes into 142 outer framed inventory events, inside 81 observed 0x016D/0x016E change scopes. It decoded 186 item packets (2982 nonempty rows) and 31 linked-item packets (146 rows).

TCP reconstruction suppressed 1759 exact repeated payload segments. The census separately marks 10 repeated aggregate equipment events. The 5625 observed 0x018F-0x0191 packets are counted as excluded nearby traffic and are never treated as equipment-transition carriers.

## Result classes

`matrix.csv` preserves sanitized per-capture actor equality plus lane, frame, subevent, transaction, item-row, equipment-row, slot, catalog-id, and temporal-distance locators. `property-joins.csv` preserves before-only, after-only, unchanged, and changed hashes from the nearest actor-scoped projections around each carrier event. Same-lane order is correlation evidence, not a causal assertion.

| Class | Rows | Meaning |
|---|---:|---|
| EXACT-TRANSITION | 1 | Single-slot 0x014D item/link join with comparable changed before/after properties. |
| BOUNDED-CANDIDATE | 5 | Single-slot 0x014D carrier whose property or item side is incomplete. |
| AGGREGATE-SNAPSHOT | 140 | 0x014E multi-slot state; not promoted as a transition. |
| MISSING-CARRIER | 124 | Framed inventory activity without an equipment link, plus the named soul property-only gap. |

## Exact transitions

| Event | Capture | Equipment slot | Catalog item | Changed hashes | Property frame bracket |
|---|---|---:|---|---:|---|
| equipment-event-004 | `change_helm.pcapng` | 8 | `0x007A3F58` | 1 | 16 -> 30 |

## Bounded candidates

| Event | Capture | Equipment slot | Catalog item | Join | Property bracket |
|---|---|---:|---|---|---|
| equipment-event-002 | `change_bodyarmor.pcapng` | 10 | `0x007A88D7` | exact-same-event-item-link | 13 -> 20 |
| equipment-event-005 | `change_to_botanist.pcapng` | 0 | `0x006B1DE2` | exact-same-event-item-link | 12 -> 23 |
| equipment-event-006 | `change_to_botanist.pcapng` | 1 | `0x006B1E4C` | exact-same-event-item-link | 23 -> 36 |
| equipment-event-027 | `gear_changeweapon.pcapng` | 0 | `0x003D7E3D` | exact-same-event-item-link | 13 -> 16 |
| equipment-event-111 | `switch_to_weaver.pcapng` | 0 | `0x005C77E6` | exact-same-event-item-link | 10 -> 26 |

## Bounded earlier-property-write replay

`property-replay.csv` covers exactly the five bounded candidates listed below. For each candidate it partitions records by capture, lane, header actor pair, property hash, and target-marker context, then retains the last wire-ordered write before carrier start and every subsequent write in the inclusive nearest actor-scoped property frame after carrier end. Writes inside the carrier frame/subevent bounds are counted and excluded from the before/after comparison. Target-marker contexts are emitted only as capture-local `context-NN` tokens; numeric actor IDs, endpoints, and raw target-marker strings are not published.

A `CHANGED` row is replay-supported correlation evidence and remains separate from `EXACT-TRANSITION`. `UNKNOWN-INITIAL` means a post-carrier write had no compatible earlier writer in the partition. `NO-SUBSEQUENT-WRITE-IN-POST-FRAME` means the earlier writer was retained but no compatible write arrived in the selected nearest post-carrier frame. `NO-POST-FRAME` records that no actor-scoped post-carrier property frame exists.

| Event | Capture | Carrier bounds | Post frame | Rows | Changed | Unchanged | Unknown initial | No subsequent | In-carrier writes |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| equipment-event-002 | `change_bodyarmor.pcapng` | f19/s1 -> f19/s6 | 20 | 7 | 0 | 0 | 5 | 2 | 0 |
| equipment-event-005 | `change_to_botanist.pcapng` | f21/s1 -> f21/s6 | 23 | 35 | 0 | 0 | 33 | 2 | 0 |
| equipment-event-006 | `change_to_botanist.pcapng` | f34/s1 -> f34/s6 | 36 | 36 | 0 | 0 | 1 | 35 | 0 |
| equipment-event-027 | `gear_changeweapon.pcapng` | f14/s1 -> f14/s6 | 16 | 83 | 0 | 0 | 81 | 2 | 0 |
| equipment-event-111 | `switch_to_weaver.pcapng` | f22/s1 -> f22/s6 | 26 | 70 | 0 | 0 | 68 | 2 | 0 |

The five retained candidates produced no `CHANGED` or `UNCHANGED` replay row. Their nearest-frame classifications and the established helm `EXACT-TRANSITION` remain unchanged; the replay closes this bounded check as a negative while retaining exact last-writer and subsequent-writer locators in the CSV.

## Claim boundary

Actor labels are capture-local tokens assigned by first observed appearance. They preserve equality without publishing actor or session identifiers. Property hashes and integer values are wire facts only; no gameplay meaning is assigned to `generalParameter[18]` or another indexed property. Aggregate snapshots, chronology, and 0x018F-0x0191 traffic are not forced into transition claims.

## Original gap disposition

The complete-corpus result below is generated from carrier and property evidence; it does not treat a similarly timed record as proof of causality.

- Helm transition: closed in `change_helm.pcapng`; equipment slot 8 changes to catalog item `0x007A3F58` while property hash `0x8cae90db` changes 141 -> 161.
- Helm old link: closed as prior state by 6 exact aggregate snapshots that bind equipment slot 8 to catalog item `0x007A3D64`; no snapshot is promoted as the transition itself.
- Body: still open; `change_bodyarmor.pcapng` exactly joins equipment slot 10 to `0x007A88D7` and has after-only `0x8cae90db=147`, but no comparable before value.
- Weapon: still open; `gear_changeweapon.pcapng` exactly joins equipment slot 0 to `0x003D7E3D` and has after-only `0x8cae90db=169`, but no comparable before value.
- Soul: still open; `gear_changesoul.pcapng` has property traffic but no inventory frame, item row, or equipment-link carrier.
- Additional bounded candidates: `change_to_botanist.pcapng` has exact slot 0 and slot 1 item/link joins, and `switch_to_weaver.pcapng` has an exact slot 0 join; none has comparable changed before/after property evidence.
