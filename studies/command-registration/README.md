# Command Registration 0x0132 Wire Census

The retained retail corpus contains 96 s2c `0x0132` records in nine captures.
Each record has a 72-byte sub-event and a 40-byte application at sub-event
offset 32. Application bytes 0 and 1 are recorded separately. A NUL-terminated
name occupies the 32-byte field at application offset 2. Remaining name-field
padding and the six bytes at application offset 34 are zero in every record.

| Function name | Byte 0 | Byte 1 | Occurrences |
|---|---:|---:|---:|
| commandForced | 11 | 0 | 12 |
| commandDefault | 10 | 0 | 12 |
| commandWeak | 6 | 0 | 12 |
| commandContent | 4 | 0 | 12 |
| commandJudgeMode | 6 | 0 | 12 |
| commandRequest | 0 | 1 | 12 |
| widgetCreate | 0 | 1 | 12 |
| macroRequest | 0 | 1 | 12 |

The table follows observed stream order. The two leading bytes can also be
read mechanically as little-endian u16 values, but that grouping does not
establish a shared semantic field.

## Exact evidence and order

[occurrences.csv](derived/occurrences.csv) gives every record's capture,
connection, direction, frame, sub-event, wrapped source and destination actors,
two leading bytes, name, zero-padding shape, and payload fingerprints.
[accounting.json](derived/accounting.json) pins all 54 input members and
records complete-corpus framing, the 12 batches, and client actor references.

Every batch contains the eight table entries consecutively in one outer
frame, on connection 0, lane `main`, direction s2c. The table below locates
each batch. Within each listed frame, the eight records are sub-events 1
through 8, at decoded body offsets 40, 112, 184, 256, 328, 400, 472, and 544.

| Capture | Frame indexes | Completing capture packets | Records |
|---|---|---|---:|
| from_gridania_to_blackshroud.pcapng | 237 | 757 | 8 |
| gridania_to_coerthas.pcapng | 176, 846, 1320 | 594, 2857, 4011 | 24 |
| login.pcapng | 9 | 961 | 8 |
| move_out_of_room.pcapng | 32 | 87 | 8 |
| moving_around_gridania.pcapng | 203, 1251 | 464, 3567 | 16 |
| return_to_inn.pcapng | 38 | 139 | 8 |
| teleport_to_camp_nine_ivies.pcapng | 73 | 307 | 8 |
| teleport_to_camp_tranquil.pcapng | 47 | 211 | 8 |
| teleport_to_gridania.pcapng | 59 | 181 | 8 |

Connection, frame, and sub-event indexes are zero-based. Capture packet indexes
are one-based and identify the first packet completing all bytes of the outer
frame, accounting for TCP segmentation and retransmissions. Frame stream
offsets count wire bytes from that connection direction's reconstructed start.
Sub-event offsets count bytes in the inflated frame body and cannot be added
to compressed stream offsets to obtain a raw capture byte location.

All 96 wrapped source and destination actor fields equal `0x029B2941`. On each
contributing connection, that value also appears in c2s session `0x0008` body
offset 0 and as the wrapped source of c2s inner `0x00CA`. The accounting retains
counts and the first exact locator for each reference. This agreement supports
association with the client's player reference. It does not by itself prove
the native target object, handler execution, accepted registration, persistence,
or command availability. The [player HP calibration study](../player-hp-calibration/)
independently uses the same numeric sample player actor ID.

## Source and reproduction

Source `pcap-1.23b` owns the retail provenance, frozen membership, and exact
member sizes and SHA-256 pins in `sources/pcap-1.23b/manifest.yaml`. The
accounting copies those member identities and pins the manifest bytes.
The restricted archive's identity and storage belong to that source manifest.
The study includes no raw application payloads, private endpoints, or names
other than the eight fixed command identifiers.

`xivl-client-structs:manifests/bundled_small_client_receivers.json` pins the
capture snapshot `41f5899e0f51c213cbcda95ebc364cdf2b8cb0d4`, whose
`derived/observations.json` records 88 occurrences across eight captures.
At that revision, `tools/extractors/extract_observations.py:EXCLUDE_CAPTURES`
excluded `login.pcapng` entirely. Current canonical admission retains its clear
TCP 54992 game connections and rejects TLS and lobby connections. The eight
`login.pcapng` records account exactly for the difference between the pinned
88-record scope and this 96-record census.

```text
python tools/extractors/extract_command_registration.py
python tools/extractors/extract_command_registration.py --check
python tools/extractors/extract_command_registration.py --check --public-shape
```

The generator validates all 54 member identities, uses canonical game-lane
admission and stream/sub-event parsing, and derives TCP packet spans from
IP-declared lengths so link padding cannot witness frame completion. All
admitted connection directions pass sequence coverage, complete-frame,
compression, and sub-event checks. `--check` reproduces both products exactly.
`--public-shape` checks retained row accounting, byte/name mappings, fingerprints,
batch order, actor agreement, and input membership without reopening captures.

## Evidence limits

Order is established only within one reconstructed connection direction.
The study does not merge separate connection blocks, directions, or captures
into an arrival chronology. Capture timestamps and filenames do not establish
live retail chronology or the cause of a batch. Repeated batches establish
repeated wire observations, not object lifetime or acceptance by the client.
Native meanings of the two leading bytes and the named commands belong to
separate client evidence at
`xivl-client-structs:manifests/command_descriptor_registration.json`, including
the priority and selector interpretation.
