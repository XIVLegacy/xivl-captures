# Login 0x0002 Same-Source Appearance Order

The sole admitted s2c inner `0x0002` in `login.pcapng` has wrapped source
`0x029B2941`. On the same main connection and direction, that source has
`0x0002 -> 0x00CA -> 0x00D6 -> 0x00CC` in reconstructed stream order.
There is one `0x00D6`, one `0x00CC`, and no `0x00D7` for that source.
No admitted s2c `0x00D7` occurs anywhere in this capture. These are numeric
wire observations; native case-2 and actor-role interpretation belongs to the
consumer.

## Evidence

[events.csv](derived/events.csv) contains only the selected source's
`0x0002`, `0x00CA`, `0x00CC`, `0x00D6`, and `0x00D7` events.
[accounting.json](derived/accounting.json) records source identity,
connection admission, per-direction framing, counts, and the anchor.

| Inner opcode | Frame | Stream offset | Sub-event | Decoded body offset | Complete-frame capture packet |
|---|---:|---:|---:|---:|---:|
| `0x0002` | 3 | 167 | 0 | 0 | 951 |
| `0x00CA` | 9 | 962 | 0 | 0 | 961 |
| `0x00D6` | 9 | 962 | 11 | 856 | 961 |
| `0x00CC` | 17 | 5457 | 19 | 2232 | 970 |

Every row is connection 0, lane `main`, direction s2c, wrapped source and
destination `0x029B2941`. Connection, frame, sub-event and direction-event
indexes are zero-based. Capture packet indexes are one-based. Stream offsets
count wire bytes from the direction's reconstructed start; sub-event offsets
count bytes in the decoded frame body. The compressed body offset cannot be
added to the stream offset to locate a raw capture byte.

The `0x00CA` and `0x00D6` share an outer frame; their decoded body offsets
establish their order. Capture packet 951 supplies the complete 53-byte anchor
frame, including its first byte. The `0x00CC` frame starts in packet 969 and
completes in packet 970. The study orders events by
stream and body position, not by these packet witnesses or timestamps.

## Source and reproduction

The input is source `pcap-1.23b`, member `login.pcapng`, 856236 bytes,
SHA-256 `28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62`,
listed at `sources/pcap-1.23b/manifest.yaml:135-137`. The source manifest owns
retail provenance and restricted storage.

The canonical reconstructor admits the two clear TCP 54992 game connections
and excludes two TLS connections and two TCP 54994 lobby connections. The main
s2c direction has 89 compressed outer frames, 15240 reconstructed bytes,
82 captured payload segments and 82 distinct segment start offsets. The chat
connection remains separate. All four admitted directions have no sequence
gaps, trailing captured bytes or compression-flag mismatches in this input.

```text
python tools/validate_framing.py sources/pcap-1.23b/objects/login.pcapng
python tools/extractors/extract_login_0002_appearance_order.py
python tools/extractors/extract_login_0002_appearance_order.py --check
```

The generator also accepts `--repo` and `--out-dir` for explicit repository and
output paths. It verifies the input size and hash before extraction, uses the
canonical connection reconstruction and sub-event parser, and rejects
incomplete tails, sequence gaps, compression mismatches and truncated
sub-events. Packet spans use the IP-declared length minus the IP and TCP header
lengths, excluding link-layer padding from payload counts and frame witnesses.
Synthetic tests guard padded ACKs and padding after actual TCP data, as well as
connection and direction separation,
wrapped-source attribution, and frame/body ordering even when packet witnesses
would suggest a different order.

## Interpretation boundary

Wrapped source equality joins the selected events numerically. It does not
establish packet handler execution, native appearance admission, script-bind
completion, rendering, movement or contact. The study establishes order only
inside this one reconstructed s2c direction. It establishes no cross-direction
or capture-wide arrival order and no universal ordering rule for other logins.

The existing [login-018a-neighborhood](../login-018a-neighborhood/README.md)
window begins later and records a different `0x00CC`; it does not contain
the selected `0x0002` anchor or
`0x00D6`. The aggregate observation and sequence products do not retain the
required same-source frame/body locators. This narrow study provides those
locators without extending the corpus or introducing another decoder.
