# Packet Decode and Wire Order

Use this guide to interpret the 1.23b packet-capture products, understand what
the aggregate products preserve, and select the tool for a sequence question
within a connection. Source and study manifests own provenance, and numeric
fields remain observation-only until evidence supports a semantic name.

## Product map

- `sources/pcap-1.23b/objects/` holds the original capture objects when the
  retention policy permits them. The objects are immutable.
- `derived/observations.json` is the merged per-capture inventory of outer
  frame types, sub-event types, inner opcodes, lengths, and capture witnesses.
- `derived/lane_observations.json` keeps the main, chat, and unknown connection
  lanes separate for inner-opcode attribution.
- `tools/extractors/extract_wire_order.py` prints sub-events in stream order
  within each reconstructed connection block for one direction of one capture.
- `derived/sequences.json` is an aggregate motif view. It is not an authority
  for chronology because it merges offsets from separate directions and
  collapses consecutive runs.

## Decode contract

### TCP streams and connections

The decoder reconstructs each TCP direction by placing segments at their
sequence offsets. It does not concatenate packets in capture order. Doing so
would duplicate retransmits and break framing.

A capture can contain the main world connection and a second chat connection.
Frame-clean connections are retained, classified as `main`, `chat`, or
`unknown`, and used by the lane-aware product. The merged observation product
keeps the existing corpus view, while the lane product preserves connection
attribution.

`login.pcapng` is TLS traffic to `secure.square-enix.com`, not game protocol
evidence, and is excluded from the game-protocol extraction.

### Outer frames

Each reconstructed stream is a sequence of back-to-back outer frames. The
frame header is 16 bytes, and the little-endian `size` field includes that
header. The next frame starts at the current offset plus `size`.

Marker byte 1 is the compression flag. `0x01` means the body is an inflatable
zlib stream. `0x00` means the body is raw sub-event bytes. This is a wire
invariant, not a direction shortcut: main-lane server output is compressed,
while client output and the chat lane's server output are raw.

Validated against `chat_say.pcapng` and `chat_shout.pcapng`, the observed
4-byte marker values are `01 00 00 00` on c2s and `01 01 00 00` on s2c. The
header layout is:

    offset  size  field
    0       4     marker  (01 00 00 00 on c2s, 01 01 00 00 on s2c)
    4       2     size    (total frame bytes including this 16-byte header)
    6       2     type    (outer type / channel)
    8       8     timestamp_or_seq
    16      N     body    (N = size - 16). On s2c, body is a zlib stream
                          (78 9c magic). On c2s, body is raw sub-events.

Frames are back-to-back: a correctly reconstructed stream has no gaps between
frames, since the `size` field accounts for the full frame length.

### Sub-events and inner fields

The body, after inflation when required, is a sequence of variable-length
sub-events. Each sub-event has a 16-byte header, and its size includes that
header. The body begins immediately after the header and the next sub-event
starts at the previous offset plus its size.

The observed `0x0003` wrapped-actor class can carry an 8-byte inner header at
sub-event body offset 16. The inner opcode is at offset 2 within that inner
header. Session sub-events such as `0x0002`, `0x0007`, and `0x0008` are direct
session records and do not imply an inner game opcode.

Outer types, sub-event types, and inner opcodes are numeric wire observations.
They are not names, service assignments, or proof of a complete field map.

## Order and validation limits

`extract_wire_order.py` walks frames in reconstructed stream order and
sub-events at increasing body offsets without sorting or collapsing them. It
reports one direction at a time and concatenates multiple connection blocks in
deterministic connection order. It does not recover capture-wide arrival order.

`python tools/validate_framing.py` checks the compression-flag invariant over
the default priority captures or over explicit capture paths. The repository
gate checks the committed aggregate products and their provenance. Neither
check proves live client or server behavior beyond the captured inputs.
