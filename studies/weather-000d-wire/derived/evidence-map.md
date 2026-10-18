# Map weather wire evidence

## Result and scope

All 54 members of source `pcap-1.23b` were checked against their manifest
sizes and SHA-256 values. The canonical decoder admitted 11 game-lane
server-to-client `0x000D` messages across eight captures. All were on the
`main` lane, with weather bytes `5E 1F` (`8030`, little-endian) and the
following byte `05`. No admitted game `0x000D` message carried `8007`.
This does not validate a retail Limsa rain transmission or its duration.

The source manifest records these as retail 1.23b live-server captures.
The input set is frozen; this study uses existing files only. Login's TCP
54994 `0x000D` is outside the clear TCP 54992 game-lane contract and is
not a weather witness. The field interpretation below combines captured
numeric bytes with separately identified native receiver evidence.

## Captured layout

Every selected sub-event was 40 bytes, type `0x0003`, with a 24-byte game
packet beginning after its 16-byte sub-event header. Source and destination
wrapper IDs were equal in every witness. This equality does not establish
the native actor role or a constant ID for another session.

Offsets in this table start at the 24-byte game packet, not the TCP frame
or sub-event. Values describe the retained witnesses; zero fields and the
variable dword do not receive additional semantics here.

| Game offset | Width | Observed bytes/value |
| --- | --- | --- |
| `+0x00` | 2 | `14 00`, the inner-header field value `20` |
| `+0x02` | 2 | `0D 00`, opcode `0x000D` |
| `+0x04` | 4 | Zero |
| `+0x08` | 4 | Variable dword |
| `+0x0C` | 4 | Zero |
| `+0x10` | 2 | `5E 1F`, weather value `8030` |
| `+0x12` | 1 | `05`, interpreted as 5 seconds by the native receiver |
| `+0x13` | 5 | Zero |

The initial `14 00` is retained as observed. It is not rewritten to the
24-byte game-packet extent. The [decode contract](../../../docs/pcap-decoding.md)
owns wrapping, compression and field boundaries.

## Source identities and locators

Member identities come from
[`sources/pcap-1.23b/manifest.yaml`](../../../sources/pcap-1.23b/manifest.yaml),
source id `pcap-1.23b`, evidence class `packet-capture`. That manifest owns
retail provenance and restricted storage. The complete 54-member inventory
defines the negative-search boundary; these are the positive witnesses:

| Member | SHA-256 |
| --- | --- |
| `from_gridania_to_blackshroud.pcapng` | `eff300de679230653953ea3399939a15ce9d6aeafd202c7ebcf5f55e6d24930f` |
| `gridania_to_coerthas.pcapng` | `63152a1ed6e446df5cc4750fe50a0839f9e45ad270c79abfc72b5c09cc47e547` |
| `move_out_of_room.pcapng` | `a7a03a1d688f3feb264f8da9fae3519c55b7e267aa3802472f0221f4d729b37b` |
| `moving_around_gridania.pcapng` | `bf6abf7ccc7a16e071846036477c1fadbc3b46385ef6e747b543d836f3f51017` |
| `teleport_to_camp_nine_ivies.pcapng` | `fac2b485608247d299a406a7065e19918789118e7e544ca85cec4d772da0e3ab` |
| `teleport_to_camp_tranquil.pcapng` | `488318351cdedb2e2b650dc68c55014b160fbbc26753c200922402c1ba6c4dd7` |
| `teleport_to_gridania.pcapng` | `779141dc79a4bcf4bfc2e265f8b9510607d5a6b6e78d32f8940e5a847e598fa0` |
| `war_quest_update2.pcapng` | `bf43b5ee32c58e5dc6f8149b071bd9c5cd5cc0aaa55ea3528872308fd7be2429` |

Every locator below is connection 0, lane `main`, direction `s2c`.
Connection and frame ordinals are zero-based. Stream offsets count bytes
from that connection direction's reconstructed start. Sub-event offsets
count bytes in the decompressed frame body and cannot be added to a
compressed frame's stream offset to locate a capture-file byte.

| Member | Frame | Frame stream offset | Sub-event offset in decoded frame |
| --- | ---: | --- | ---: |
| `from_gridania_to_blackshroud.pcapng` | 233 | `0x620D` | 120 |
| `gridania_to_coerthas.pcapng` | 173 | `0x3DD9` | 40 |
| `gridania_to_coerthas.pcapng` | 843 | `0x1C883` | 80 |
| `gridania_to_coerthas.pcapng` | 1317 | `0x3458B` | 80 |
| `move_out_of_room.pcapng` | 29 | `0x8FB` | 40 |
| `moving_around_gridania.pcapng` | 200 | `0x77BC` | 80 |
| `moving_around_gridania.pcapng` | 1248 | `0x2E9CA` | 80 |
| `teleport_to_camp_nine_ivies.pcapng` | 69 | `0x161E` | 120 |
| `teleport_to_camp_tranquil.pcapng` | 43 | `0xB87` | 80 |
| `teleport_to_gridania.pcapng` | 55 | `0x18BC` | 120 |
| `war_quest_update2.pcapng` | 637 | `0xEA33` | 120 |

Filenames and adjacent packets are not used to infer a Limsa region state.
No capture-wide chronology is constructed across connection blocks.

## Native interpretation and sender consequence

`xivl-decomp:docs/net/weather-transition-runtime.md#packet-fields-and-publication`
at revision `ab76ac02939023447bf8fe49d030a929085466cc` owns the native
semantics. Its pinned `ffxivgame.exe` SHA-256 is
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
The opcode dispatch at VA `0x004DCBF7` reaches the weather case at
`0x0059CF79..0x0059CFB8`, which reads an unsigned 16-bit weather ID at
game-packet `+0x10` and an unsigned duration byte at `+0x12`. The subsequent
native publication interprets that byte as whole seconds. These offsets
agree with the captured values above.

For a server targeting the documented Limsa rain case, the supported
construction is map/clientbound opcode `0x000D`, weather ID `8007`
encoded `47 1F`, and a deliberately selected unsigned one-byte duration.
The capture set supports the message shape and the observed 5-second value;
it does not establish 5 seconds as the required duration for `8007`.

For example, the eight bytes at game-packet `+0x10..+0x17` for a chosen
5-second `8007` update would be:

```text
47 1F 05 00 00 00 00 00
```

This is a synthetic construction from the native ID/field contract and
the observed zero tail, not an observed retail `8007` payload. Use the
normal session's transport, wrapper addressing and header fields; do not
copy another session's IDs or the variable header dword. The native Limsa
selection also requires the documented region/actor conditions. Successful
binding of rain resources and visible rain remain separate claims.
The client owns the region-dependent `8007 -> 0x29D90013` resource lookup;
the weather field carries the ID `8007`.

## Reproduction and limits

The extraction used the repository's `tools/extractors/extract_streams.py`
APIs `reconstruct_lanes`, `parse_outer_frames` and `maybe_inflate`, with
`struct.unpack_from` on complete type-3 sub-events. It visited every member
listed in the source manifest, verified each hash/size, and filtered only
the inner opcode `0x000D` on admitted game connections. Both directions
were inspected; all matches were s2c. There were no compression-flag
mismatches, and every selected weather sub-event was complete.
Frame-clean reconstruction excludes trailing partial frames; this result
does not claim that every captured TCP byte was a complete game frame.
The reconstruction tools were read at repository revision
`991b9e8de76333cf5e18ac424076624c89fd94f3`.

To locate an individual witness with the existing tools:

```text
python tools/validate_framing.py sources/pcap-1.23b/objects/gridania_to_coerthas.pcapng
python tools/extractors/extract_wire_order.py sources/pcap-1.23b/objects/gridania_to_coerthas.pcapng --direction s2c --around 0x000d --before 2 --after 2
```

For byte replay, select the connection/frame in the locator table using
`reconstruct_lanes` and `parse_outer_frames`, inflate its body with
`maybe_inflate`, and slice 40 bytes at the listed sub-event offset.
Discard its 16-byte wrapper to obtain the 24-byte game packet. Compare the
fields in the captured-layout table. Repeating that scan across the source
manifest reproduces the bounded absence of `8007`.
