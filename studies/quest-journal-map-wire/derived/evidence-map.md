# Quest 110658 journal and map exchange

`quest_journal.pcapng` contains two command-24211 requests and two
`requestedData` replies on the same main game connection. The map request
contains integers `110658, 2` followed by seven nils. The map reply contains
`requestedData, qtmap, 110658, 11065801` in that order. Transport and time
correlation support pairing them, without identifying the server's application
matching or marker-selection code.

## Source and records

The source is `pcap-1.23b`, evidence class `packet-capture`, member
`quest_journal.pcapng`, 32,264 bytes, SHA-256
`e1f983e9009a9ebe8b8231647229bee1672a1ac85d95a830113280f534531edc`.
The [source manifest](../../../sources/pcap-1.23b/manifest.yaml) owns provenance.
No other original capture was used for this finding.

All four records belong to connection 0, lane `main`, client port 36166 and
server port 54992. Wrapped source and target actor IDs both equal
`0x029B2941`. Indexes are zero-based except one-based capture packet numbers.
Stream offsets belong to the stated direction; subevent offsets belong to
the inflated frame body.

| Packet | Direction/opcode | Frame | Stream offset | Subevent/body offset | Ordered typed values |
| ---: | --- | ---: | ---: | --- | --- |
| 57 | c2s `0x012D` | 21 | 3416 | 2 / 120 | command24211: integer 110658, eight nils |
| 75 | s2c `0x0133` | 13 | 1159 | 0 / 0 | requestedData, qtdata, integers 110658, 0, 0, 0, 0, 0, 8 |
| 94 | c2s `0x012D` | 30 | 5152 | 1 / 64 | command24211: integers 110658, 2, seven nils |
| 96 | s2c `0x0133` | 18 | 1557 | 0 / 0 | requestedData, qtmap, integers 110658, 11065801 |

The requests have owner `0xA0F05E93`; its static-owner prefix and low word
identify command 24211. The inline method is `commandRequest`. Each
184-byte application is inside a 200-byte game message and 216-byte subpacket.
The 128-byte parameter block starts at application offset 49, has a matching
CRC32 and contains nine explicit values. END is at parameter offset 13 or 17,
respectively, followed by 114 or 110 zero bytes. Nonzero bytes after the
method string's first NUL are unconsumed remainder, without assigned meaning.

Each reply has a 192-byte application, 208-byte game message and 224-byte
subpacket. Its typed stream starts at application offset 0. For `qtmap`,
tags begin at 0 (`requestedData`), 15 (`qtmap`), 22 (110658) and
27 (11065801). END is at 32, followed by 159 zero bytes. The `qtdata` stream
ends at 58, followed by 133 zero bytes. Neither contains type-9 metadata.
These extents do not require every generic-data message to have this size.

## Correlation

The original frame-completion packet order is 57, 75, 94, 96. Packet 75
follows packet 57 by 561798 microseconds and repeats key 110658. Its ACK
3946315618 covers the first request frame's end sequence 3946315474 plus
144 later client-stream bytes.

Packet 96 follows packet 94 by 274967 microseconds and repeats key 110658.
Its ACK 3946317154 exactly covers the request frame's TCP span
`[3946316794,3946317154)`. This proves transport receipt and captured order.
It supports pairing these records; ACKs and temporal adjacency do not prove
that one application request caused a particular response. No aggregate
`derived/sequences.json` ordering was used.

## Client argument and static-row join

The authenticated
`xivl-client-scripts:docs/content-director-ui-contracts.md`, Requested-data
fixed arguments, separates the values when the PlayerBaseClass override is
selected:

| Desktop argument | Value |
| --- | --- |
| Fixed subtype | qtmap |
| Fixed supplied ID | 110658 |
| Ordered marker varargs | 11065801 |

The desktop `qtmap` arm ignores its supplied-ID formal. Only `11065801`
enters the marker list and its two string-property routes. The native
UserData receiver preserves accepted values in order, as recorded in
`xivl-decomp:docs/event/user-data-receiver.md`, ordinary call boundary.
The short capture does not identify the actor's historical leaf Lua class,
actual looked-up callback function or successful UI execution.

The exact static crosscheck belongs to
`xivl-client-data:docs/quest-marker-rows.md`, Row 11065801. It records two
coordinates, `m00018`, `MapMarkerQuestArea` and `@5208/i11065801`.
Same-key `xtx_quest` English text names 110658 The Penultimate Prank. A
matching row does not establish the native resource binding of
`ssd_marker_data` or visible marker rendering.

## Quest-phase boundary

The `qtdata` tail is the six numbers `0,0,0,0,0,8`. The existing
`xivl-client-scripts:docs/quest-event-client-contracts.md`, Quest journal and
reward presentation widgets, leaves their meanings unassigned. The final 8 is the sixth
numeric input, without an established phase meaning. Marker suffix 01
likewise does not establish phase 1.

This establishes one received list associated by key and transport timing
with one map request. It does not recover the server's list-selection rule,
prove a quest-phase transition, authenticate other quests' lists or provide
the missing historical class/function lookup.

## Reproduction and framing

Use the exact member with `tools/validate_framing.py`. Inspect c2s `0x012D`
and s2c `0x0133` with `tools/extractors/extract_wire_order.py`, preserving
separate direction streams. The producing Python 3.12 analysis used
`tools/extractors/extract_streams.py` reconstruction and
`tools/extractors/extract_observations.py:parse_sub_events` admission at
revision `b647aaa018f8af9bc6ef6b60c41fb114134396ae`.
Typed-list inspection uses tag 0 plus signed big-endian four-byte integer,
tag 2 plus NUL-terminated string, tag 5 nil and tag 15 END at tag positions.
The offsets and extents above select the complete records without a corpus
sweep.

Framing consumed 9616 c2s bytes in 56 raw frames and 2721 s2c bytes in
32 compressed frames, with zero frame trailing bytes or compression
mismatches. There are 134 c2s and 72 s2c subevents, without truncation.
Independent reconstruction bounded TCP payload by the IPv4 declared length
and matched both canonical direction streams byte-for-byte, with zero TCP
gaps or overlaps.

Scapy exposes six bytes of Ethernet padding on each of 52 ACK-only packets.
Those 312 bytes are outside the IP-declared TCP payload. The canonical raw
Scapy-span counter separately reports six discarded final s2c bytes from
this padding; it is not discarded TCP application data or frame truncation.
That counter remains separate from the clean framing result.
