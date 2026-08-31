# World Party-Chat 0x00C9 Verdicts

## Corpus accounting

The complete 54-member retained corpus contains 37 World chat-lane `0x00C9`
events: 11 c2s and 26 s2c. The c2s rows are nine in
`party_battle_leve.pcapng` and two in `war_quest_update2.pcapng`; the s2c rows
are 25 and one respectively. Every target occupies one raw chat-lane outer
frame and one actor-wrapped subevent. No target occurs on the main lane.

## Direction-specific contract

Both directions use outer type 1 with raw, not zlib-compressed, frame bodies.
The c2s outer/subevent sizes are 568/552 bytes and the s2c sizes are 600/584
bytes. The common 24-byte prefix is the 16-byte actor wrapper followed by tag
`0x0014`, opcode `0x00c9`, and a zero u32. Application bytes begin at subevent
offset 24.

The c2s application is selector u32 10, zero u32, an unnamed u32, a 512-byte
message field, and an unnamed four-byte tail. The s2c application inserts a
32-byte sender-name field before the 512-byte message and ends with four zero
bytes. Every observed name and message has a NUL terminator, zero padding to
field width, and exact UTF-8 roundtrip. This proves the observed encoding; it
does not exclude other byte sequences in unobserved retail messages.

## Identity and sequence boundary

The wrapper exposes distinct u32 source-actor and destination-actor fields, but
their values do not substitute for the s2c sender-name field. The unnamed
application u32 at `+8` has one c2s value and two s2c values across the retained
capture contexts; the same sender-name bytes occur in both files. It is therefore
not promoted as a stable sender identifier. The wrapper counter is one
invariant nonzero value c2s and zero in all s2c rows. The c2s tail has two
nonzero equality classes and is non-monotonic.
Neither field supplies an observed message sequence.

## Bahamut adoption boundary

A retail-shaped recipient packet is World clientbound `0x00C9` on the chat
lane, not Map clientbound `0x0003` on the main lane. A consumer may adopt the
fixed s2c offsets, widths, selector, sender-name buffer, message buffer, and
zero fields in `field-matrix.csv`. It must source or preserve the wrapper actor
values and unnamed context u32 explicitly; this study does not define how a
server synthesizes them. It must not translate the relay into a Map message
type or infer recipients, moderation, persistence, delivery policy, or
causality from these captures.

## Evidence reconciliation

`xivl-client-structs:manifests/symbols.json#BCS-Y-0309` and
`xivl-opcodes:data/client_opcode_semantics.json#c2s-00c9` independently place
the c2s emitter on the Chat forwarder, establish opcode `0x00c9`, the fixed
record extent, a u32 selector, and a 512-byte text field. The capture corpus
establishes the direction-specific wire prefixes and the additional s2c
sender-name field. No client receiver evidence used here assigns a noun to the
remaining context or tail bytes.
