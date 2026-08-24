# Comparative verdicts

## Complete census

The 54-capture canonical clear-game corpus contains 31 `0x00DA` occurrences
across seven captures and three `0x00E1` occurrences across three captures.
All 34 occur server-to-client on the main lane. No target opcode occurs
client-to-server or on a chat or unknown lane.

The same complete admitted corpus contains zero `0x00E0` occurrences in either
direction. `occurrences.csv` therefore has no synthetic `0x00E0` row;
`accounting.json` records the zero census explicitly.

No admitted target occurrence is truncated or lacks the 8-byte inner header or
8-byte game-message preamble. Across the raw reconstructed admitted
connections, the canonical reducer discards 228 trailing bytes: six s2c bytes
in each of 38 captures. The retained complete-frame streams have zero unparsed
bytes. The complete decoder pass also records zero truncated sub-events, zero
wrapped sub-events with a short inner header, and zero compressed-frame
inflation failures.

## Payload distinction

Every `0x00DA` occurrence is a 40-byte sub-event with a 16-byte payload after
the inner header and an 8-byte application body after the shared 8-byte
preamble. Its second application u32 is zero in all 31 occurrences. The first
application u32 has ten distinct values; `0x040C9000` occurs 11 times,
`0x04000FFA` and `0x04000FFB` occur six times each, and the remaining seven
values occur one or two times.

Every `0x00E1` occurrence is a 48-byte sub-event with a 24-byte payload after
the inner header and a 16-byte application body after the shared preamble. All
three exact application byte strings differ. Their fourth application u32 is
zero, while the first three u32 positions vary across the three rows.

The two observed opcode sets share no exact application byte string. Their
different fixed application sizes already distinguish the retained wire
shapes without assigning a noun to either one.

## Actor-identifier relationships

All 34 sub-event transport targets are `0x029B2941`. For `0x00DA`, transport
source equals transport target in 16 of 31 rows; the other 15 rows use 14
distinct source identifiers. For `0x00E1`, source equals target in two of three
rows, while the remaining row uses `0x029B27D3` as source. That source also
appears twice among `0x00DA`, so the two opcode sets share transport actor
identifiers even though their application bodies do not match.

The preamble's first u32 equals neither transport source nor transport target
in any target row. This is a negative numeric equality result, not a semantic
field identification.

## Bounded chronology

No immediate predecessor or follower is invariant for `0x00DA`. Its most
frequent immediate predecessor is `0x0169` in 10 of 31 rows, and its most
frequent immediate follower is `0x0130` in seven of 31. Two `0x00DA` rows are
directly adjacent to each other, contributing one predecessor and one follower
relationship.

Two of the three `0x00E1` rows have `0x0001` immediately before and after. The
remaining row has `0x00CF` immediately before and `0x00CE` immediately after.
This repeated bounded neighborhood does not prove a causal relation or packet
meaning.

`neighborhoods.csv` retains three events on each available side within one
reconstructed connection direction. Same-frame neighbors have zero capture
and outer-value delta and remain ordered only by sub-event offset.

## Claim boundary

Capture and scenario filenames served only to locate rows and are not semantic
evidence. The study promotes numeric opcode identities, byte shapes,
distributions, actor-ID equality, and bounded chronology only. It does not
promote emote, animation, effect, action, or causal packet nouns.
