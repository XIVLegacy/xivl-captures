# M9 Verdicts

## Autotranslate selections: ABSENCE-RECORDED

All 54 manifest members were searched in both directions. The search covered
raw TCP segment payloads, TCP-sequence-reconstructed streams, complete outer
frame bodies after zlib inflation, parsed actor-event payloads, and the tracked
payload sample set. It tested 9,048 distinct byte patterns built from all 758
rows in `xivl-client-data:csv/xtx__fixedPhrase.csv`.

No `02 1d` selector pattern ending in `03` matched. The no-terminator control
found 43 structural matches, all in the `u16be_nterm` family. Eighteen decoded
body/event copies of `02 1d 04 6e` appeared in repeated `0x0137` property
payloads. Seven additional copies appeared only in raw streams. These are
binary collisions: they lack the tested terminator and are not chat packets.

This is a bounded absence for the tested encodings, not proof of a retail wire
grammar. No permitted source establishes the `02 1d` marker or the tested ID,
category, and index layouts. A different encoding would not be detected by this
study.

## Chat relay specimens: SPECIMENS-FOUND

The lane-aware scan found exactly 39 target packets. The complete packet list
is `derived/chat-relay-specimens.csv`.

### Map main client-to-server `0x0003`

Two packets occur, one each in `chat_say.pcapng` and `chat_shout.pcapng`. Their
wrapped sub-event size is 576 bytes: an 8-byte inner header and 552 application
bytes. The application payload contains a 32-byte binary prefix, a little-endian
u32 selector at `+32` (`1` Say, `2` Shout), a 512-byte NUL-padded text field at
`+36..+547`, and a 4-byte unknown tail at `+548..+551`.

The fixed 552-byte body is independently cataloged at
`xivl-opcodes:structs/map/serverbound.h:28` and the emitter evidence is recorded
at `xivl-opcodes:opcodes.json` in the Map serverbound `0x0003` entry. Prefix and
tail semantics remain unproven.

### World chat client-to-server `0x00c9`

Eleven packets occur: nine in `party_battle_leve.pcapng` and two in
`war_quest_update2.pcapng`. Their wrapped sub-event size is 552 bytes: an
8-byte inner header and 528 application bytes. The application payload contains
a 12-byte prefix, a 512-byte NUL-padded text field at `+12..+523`, and a 4-byte
unknown tail at `+524..+527`. The observed prefix begins with chat-group value
`0x0000000a`; the next observed session value is `0x00003fd7`.

The body is independently cataloged at
`xivl-opcodes:structs/world/serverbound.h:14` and in the World serverbound
`0x00c9` entry of `xivl-opcodes:opcodes.json`.

### World chat server-to-client `0x00c9`

Twenty-six relay packets occur: 25 in `party_battle_leve.pcapng` and one in
`war_quest_update2.pcapng`. Their wrapped sub-event size is 584 bytes: an
8-byte inner header and 560 application bytes. The application payload contains
a 12-byte shared prefix, a 32-byte sender name at `+12..+43`, a 512-byte message
at `+44..+555`, and a 4-byte zero tail at `+556..+559`. Observed session values
in the prefix are `0x00003fd7` and `0x00003f3e`.

The relay interpretation and fixed body are independently cataloged at
`xivl-opcodes:opcodes.json` in the World clientbound `0x00c9` entry and at
`xivl-opcodes:structs/world/clientbound.h:14`.

## Collision ruling

The sub-event type `0x0003` is wrapper metadata, not the inner opcode. Numeric
`0x0003` also names unrelated Lobby serverbound and World clientbound catalog
entries. The lane-aware corpus scan found target `0x0003` only on the Map main
client-to-server lane. All 37 `0x00c9` packets occur on the World chat lane.
