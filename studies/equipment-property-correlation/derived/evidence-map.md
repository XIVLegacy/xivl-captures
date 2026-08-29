# Equipment property correlation evidence map

## Deterministic matrix

`matrix.csv` is exhaustive for the four named gear captures. Packet locators
for item records and links are s2c and use reconstructed lane, outer frame,
and subevent indices. Property locators use the canonical record indices from
the 0x0137 property-stream study.

| Capture | Verdict | Item record | 0x014D link | Property evidence |
|---|---|---|---|---|
| `change_bodyarmor.pcapng` | AFTER-ONLY | 0x0149 lane 0 frame 19 subevent 2; 0x007A88D7 item slot 140 | lane 0 frame 19 subevent 4; equipment slot 10 -> item slot 140 | generalParameter[18] after 147 at record 36; before value missing; projection records 33-37 |
| `change_helm.pcapng` | CORRELATED | 0x0148 lane 0 frame 28 subevent 2; 0x007A3F58 item slot 113 | lane 0 frame 28 subevent 4; equipment slot 8 -> item slot 113 | generalParameter[18] 141 -> 161; records 43 and 44 |
| `gear_changesoul.pcapng` | NO-GO | absent | absent | unjoined; no item/link carrier |
| `gear_changeweapon.pcapng` | AFTER-ONLY | 0x0149 lane 0 frame 14 subevent 2; 0x003D7E3D item slot 79 | lane 0 frame 14 subevent 4; equipment slot 0 -> item slot 79 | generalParameter[18] after 169 at record 593; before value missing; projection records 575-649 |

## Promoted facts

The helm capture changes `generalParameter[18]` from 141 to 161. The new catalog item `0x007A3F58` is linked from equipment slot 8 to item slot 113.
The old catalog item is present at item slot 131, but no earlier explicit
equipment-slot-8 link exists in the capture.

Body and weapon each have an item/link join followed by a property projection,
but neither capture supplies comparable before values. Soul has 0x0137 property
traffic but no 0x0148/0x0149 item record and no 0x014D link, so it is NO-GO.

## Claim boundary

`generalParameter[18]` is an exact indexed field label only. This study does
not assign gameplay meaning to that index or to any other generalParameter
index. It does not turn after-only body or weapon projections into changes.
The actual four captures contain no 0x018F, 0x0190, or 0x0191 stream.

## Unresolved fields

The body and weapon before-side property values remain missing. The helm old
item's explicit equipment-slot-8 link remains missing. Soul cannot be joined
to an item or equipment link within the retained capture.
