# Map 0x018F/0x0190/0x0191 transaction verdicts

## Complete corpus accounting

The complete canonical 54-capture corpus contains 28
`0x018F`, 5569 `0x0190`, and
28 `0x0191` events across all
84 admitted lanes. They form 28
complete same-lane `0x018F -> 0x0190* -> 0x0191` spans containing
5569 records. Orphan records, orphan ends,
nested begins, and unterminated spans are respectively 0,
0, 0, and
0. Shape exclusions total
0.

Record counts per span are 197 in 3 spans, 198 in 2, 199 in 18, and 200 in 5.
The eight target-bearing capture contexts are `combat_autoattack.pcapng` (2), `combat_skills.pcapng` (1), `gather_wood.pcapng` (1), `harvest.pcapng` (2), `local_leve_complete.pcapng` (3), `party_battle_leve.pcapng` (17), `repair_items.pcapng` (1), `war_quest_update2.pcapng` (1). Filenames are
corpus locators, not causal labels.

All admitted `0x018F` and `0x0191` application areas are zero. Their imported
MassSetItemModifier labels remain unproven and are not promoted here.

## Key, vector, and tail verdicts

The two leading `0x0190` dwords are retained as unnamed keys. Key dword 0 has
206 distinct values and no zero event;
204 values repeat. Key dword 1 has one
distinct value and is zero in all 5569 records.
The pair distribution therefore matches key dword 0, and the two key dwords
are never equal. Values are not exposed because their roles are unproven.

Across all records there are 150 distinct 16-dword
vectors and 0 all-zero vectors. Exact vector
repetitions beyond the first total
5419. Repeated same-capture,
same-lane key pairs provide 3976
ordered comparisons: 3927 are equal and
49 change. The accounting document records
every changed word position, sparsity histogram, per-position nonzero count,
and bounded unsigned value distribution.
Only positions 0, 1, 3, 4, and 8 are nonzero anywhere. Ordered changes occur
only at positions 0 and 8. Among bounded values from 0 through 255, only 0 and
1 occur; larger values remain grouped into unsigned numeric bands.

The 32-byte unread tail has 1 distinct byte strings;
5569 of 5569 tails are all zero. Its varying
and nonzero byte positions are recorded without publishing tail bytes.

TCP reconstruction removed transport duplicates before these event counts.
The source corpus separately contains 1759 exact
repeated admitted TCP segments. After reconstruction,
0 complete span record sequences
repeat beyond their first occurrence, while
5281 `0x0190` applications
repeat beyond their first occurrence, including
0 consecutive exact
repetitions inside spans. Those are recurring decoded events, not retransmits.

## Context and claim boundary

The span ledger records the nearest prior and following wrapped opcode on the
same reconstructed lane and all non-target opcodes intervening inside each
span. Numeric inventory-frame, equipment-carrier, and change-frame opcodes
occur inside 0,
0, and
0 spans respectively. These are
bounded order correlations, not causal or semantic assignments.

No non-target opcode intervenes inside any complete span. `0x0137` is the
immediate prior opcode for 3 spans and the immediate following opcode for 9;
`0x016E` is immediately prior to 2 spans, and `0x0130` is immediately prior to
1. These numeric same-lane adjacencies are retained for consumer investigation;
imported names do not assign those contexts to the target transaction.

Packet filenames, neighboring opcodes, repeated vectors, and key equality do
not prove inventory mutation, equipment transition, server ordering policy,
event ownership, or a gameplay noun. Such interpretations require an
independent consumer route or directly linked state transition.
