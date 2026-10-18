# Map music wire evidence

## Result and boundary

This bounded check selected five existing members of `pcap-1.23b`, verified
their manifest sizes and SHA-256 values, and scanned both directions of every
admitted game connection. It found six `0x000C` messages, all main-lane
server-to-client. Within each of the two combat-named members, song/mode
`13/1` preceded `57/4`. The mount-named member carried `83/4`, then `57/4`.
The stance and action-bar members contained no admitted `0x000C` message.

This is packet-capture evidence, not an inference from a reference server.
Filenames describe the retained scenarios; they do not identify the exact
combat start/end predicate, the actor's zone, or the state of the client's
audio driver. The selected set is not a full-corpus music census. Its absence
of modes 2/3 does not prove that retail never used those modes for combat.
No capture-wide chronology was constructed across connections or directions.

## Source identities

Source id `pcap-1.23b`, evidence class `packet-capture`, and the original
retail provenance are owned by
[`sources/pcap-1.23b/manifest.yaml`](../../../sources/pcap-1.23b/manifest.yaml).
The following members, including the negative samples, define this study's
complete search boundary:

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `combat_autoattack.pcapng` | 82908 | `2f677ab61047b25c4168a3dd9496f372d48de3bba018d582dd5a968b9272f7b2` |
| `combat_skills.pcapng` | 63028 | `7fe66d92f6f62584e57562e51355d310546935690e0b96c2c689b83bbe8a07a7` |
| `battle_mode_passive_mode.pcapng` | 12776 | `5a8290df1d11781f4f5fa1f6990651c679e57ee3b8c5549021f06767bb172d4b` |
| `action_and_traits.pcapng` | 37584 | `c3d30fe46d69996dc74e4864245c42675cde2388525c03063dac180df528352f` |
| `mount_unmount_chocobo.pcapng` | 21240 | `e77c06799f07029feb054792eac30baa431da15a61937b1a39bcd025e4db4072` |

## Captured layout and locators

All six witnesses are 40-byte type-`0x0003` sub-events. Removing their
16-byte wrappers leaves 24-byte game packets. Game `+0x00` contains
`14 00`, `+0x02` contains `0C 00`, `+0x04..+0x07` and
`+0x0C..+0x0F` are zero, and `+0x08..+0x0B` varies. Wrapper source and
destination fields both contain `41 29 9B 02` in this sample. Neither that
equality nor the variable game-header dword receives additional semantics.
The observed initial value `20` is not rewritten to the game extent `24`.

Every row below is connection 0, lane `main`, direction `s2c`. Connection
and frame ordinals are zero-based. Frame stream offsets count bytes in the
reconstructed direction; sub-event offsets count bytes in the decoded frame
body. They are not pcap-file offsets, and cannot be added to a compressed
frame's stream offset to locate a capture-file byte.

| Member | Frame | Stream offset | Decoded sub-event offset | Game bytes `+0x10..+0x17` | Song | Mode |
| --- | ---: | --- | ---: | --- | ---: | ---: |
| `combat_autoattack.pcapng` | 18 | `0x7FA` | 0 | `0D 00 01 00 00 00 00 00` | 13 | 1 |
| `combat_autoattack.pcapng` | 128 | `0x4282` | 0 | `39 00 04 00 00 00 00 00` | 57 | 4 |
| `combat_skills.pcapng` | 25 | `0xB81` | 168 | `0D 00 01 00 00 00 00 00` | 13 | 1 |
| `combat_skills.pcapng` | 85 | `0x253F` | 0 | `39 00 04 00 00 00 00 00` | 57 | 4 |
| `mount_unmount_chocobo.pcapng` | 2 | `0x74` | 0 | `53 00 04 00 00 00 00 00` | 83 | 4 |
| `mount_unmount_chocobo.pcapng` | 13 | `0x3D2` | 0 | `39 00 04 00 00 00 00 00` | 57 | 4 |

The song interpretation is an unsigned little-endian word at game `+0x10`;
mode is an unsigned byte at `+0x12`. Original `ffxivgame.exe`, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`,
size `15996808`, image base `0x00400000`, supplies the independent native
anchor: VA `0x004DCC12..0x004DCC22` reads those fields for opcode `0x000C`
and calls `0x004BBB30`. Capstone `5.0.7` with pefile `2024.8.26` checked
the original PE instructions. Zero at `+0x13` is observed packet data; it
does not widen the consumed mode to 16 bits.

## Reproduction and verdict

The decoder was read at `xivl-captures` revision
`7ae5956bbd1fcfc46b11c5751b73ffb467188cfb`. Validate each selected member
with `tools/validate_framing.py`; all reported zero compression-flag
mismatches and no trailing bytes in the admitted reconstructed streams.
Use `tools/extractors/extract_streams.py` APIs `reconstruct_lanes`,
`parse_outer_frames` and `maybe_inflate`. For each direction, walk complete
sub-events using their unsigned little-endian size/type words; select type 3
with at least an 8-byte inner header and opcode `0x000C` at sub-event
`+0x12`. Slice at the listed decoded offset and remove the 16-byte wrapper.
All decoded sub-event boundaries in this selected scan were complete.
Frame-clean reconstruction can exclude incomplete TCP tails; these checks do
not certify every captured TCP byte as a complete game frame.

For connection-local order and an individual witness:

```text
python tools/validate_framing.py sources/pcap-1.23b/objects/combat_autoattack.pcapng
python tools/extractors/extract_wire_order.py sources/pcap-1.23b/objects/combat_autoattack.pcapng --direction s2c --around 0x000c --before 2 --after 2
```

Confirmed: the listed values, order within each connection, layout and six
locators. Unresolved: precise combat eligibility and exit timing, aggro-only
versus drawn-weapon rules, party/boss/KO policy, cross-zone restoration and
audible results. Modes 1/4 are supported sample inputs for an explicitly
reconstructed combat policy. These samples do not justify declaring modes
2/3 the universal retail combat pair or copying another server's timing.
