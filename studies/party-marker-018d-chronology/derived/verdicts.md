# Party marker 0x018D chronology verdicts

## Exhaustive accounting

The complete 54-capture corpus contains 592 decoded s2c `0x018D`
events and 769 decoded marker records after canonical TCP
reconstruction. The count is 1 in 415 events and 2 in
177 events. The chronology contains
38 first-observed nonempty snapshots,
371 changed same-count snapshots,
1 increased-count snapshots,
0 decreased-count snapshots, and
182 repeated nonempty snapshots.

## Packet and snapshot shape

Every admitted event uses the 664-byte application layout: three leading u32
fields, sixteen reserved 0x28-byte record slots, a u8 count at `+0x290`, and a
seven-byte reserved tail. The client-read positions are u32 values at `+0x00`,
`+0x08`, and `+0x0C`, plus f32 values at `+0x14`, `+0x18`, and `+0x1C`.
Identifier-shaped dwords are capture-local pseudonyms. The f32 view at `+0x20`
is retained only as a bounded structural hypothesis over the unprojected
`+0x20..+0x27` span.

All snapshot labels describe only packet chronology. A decreased-count or
`empty-after-nonempty` row is removal-shaped, but does not prove server intent
or client-side removal behavior. Neither shape occurs in this corpus.

## Bounded chronology

No tested category is a consistent predecessor across the 38 lanes with a
marker event. Any prior actor-lifecycle or broader group-update event appears
in 5 and
5 lanes respectively;
prior `0x018B`, `0x0193`, and zone-transition events appear in
3,
1, and
1 lanes. The detailed
five-event preceding and following neighborhoods remain in
`neighborhoods.csv`. These are chronology correlations, not evidence that a
neighbor creates the nullable selector `0x0D` pointee or causes marker
handling.

## Rejected interpretations

The chronology does not establish party policy, permission, membership,
server causality, or nouns for coordinate and unknown numeric values. No
neighboring opcode is claimed to create selector `0x0D`. The gate at
`RaptureElementContainer+0x4D8` is a nullable pointer; marker records live in
the pointee's `+0x98` subobject and are not stored in the gate field.

## Remaining boundary

The preserved corpus can prove only the observed same-lane order and repeated
packet snapshots. Direct runtime evidence linking a specific packet or state
transition to selector `0x0D` creation would be required for a creation
boundary. An empty or decreasing-count witness would be required for a
removal-shaped packet chronology; direct runtime observation would still be
required to establish removal behavior.
