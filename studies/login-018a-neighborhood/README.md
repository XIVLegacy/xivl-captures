# Login 0x018A Main-Lane Neighborhood

## Study contents

This bounded packet study records the immediate connection-local context around
the sole admitted server-to-client `0x018A` event in `login.pcapng`. It keeps
the main and chat connections separate, reconstructs retransmitted TCP bytes by
sequence offset, and uses capture-packet arrival only to bracket the nearest
client-to-server frames on the same connection.

The study does not assign `0x018A` a packet noun. `_0x018A` is the retained
catalog placeholder.

## Start here

- `derived/timeline.csv` - six main-lane s2c events before and after the anchor,
  plus the nearest bracketing c2s frames on that connection.
- `derived/accounting.json` - capture identity, admission accounting, anchor
  payload hashes, retransmission accounting, timing bracket, and limitations.

Regenerate or verify the canonical products:

```text
python tools/extractors/extract_login_018a_timeline.py
python tools/extractors/extract_login_018a_timeline.py --check
```

## Source material

The runtime source is `login.pcapng`, SHA-256
`28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62`,
listed in `sources/pcap-1.23b/manifest.yaml:136-138`. The canonical admission
boundary accepts the two clear TCP 54992 game connections and rejects two TLS
connections and two TCP 54994 lobby connections.

Opcode labels come from the promoted local snapshot in
`derived/opcode_names.json`. Its source at
`XIVLegacy/xivl-opcodes@7f66a82d40455ad96fca0c26d9f58f0e61265b99:opcodes.json`
attributes the retained event to the map main lane while deliberately keeping
the `_0x018A` placeholder. The tracked dispatcher record at
`XIVLegacy/xivl-decomp@2bbad7ff4fc06492982eb0a5eeaf0d7d50d8f61a:config/ffxivgame.protocol_evidence.json`
establishes routing to `FUN_00576380` but explicitly does not establish the
imported semantic suffix.

## Verdict

The single admitted `0x018A` occurs on lane 0 (`main`), direction s2c, in outer
frame 21 and capture packet 977. That one packet contains the complete frame,
not only its first byte. The anchor is sub-event 6 at inflated-body offset 656.
Its exact 136-byte sub-event SHA-256 is
`5525cde8cf9851c96f50b1c4200e7b6c8cf04f2d99664b24515ad19677d36854`;
the 120 bytes after the sub-event header hash to
`adb89225cfbd6b906a7178a6f7954aa460fdb1fdd8e054639917cd34dbe7cf18`.

The immediate main-lane s2c predecessor is `0x0137`
(`SetActorPropetyPacket` in the promoted catalog), and the immediate follower
is `0x0189` (`CreateNamedGroupMultiple`). All three are in the same outer frame,
so neither capture time nor the outer 8-byte value orders them more finely;
their sub-event offsets do.

| Relative event | Opcode | Catalog label | Sub-event offset |
|---:|---|---|---:|
| -6 | `0x0144` | `SetActorSubStatePacket` | 0 |
| -5 | `0x0179` | `SetActorStatusAllPacket` | 40 |
| -4 | `0x0145` | `SetActorIconPacket` | 112 |
| -3 | `0x017B` | `SetActorIsZoningPacket` | 152 |
| -2 | `0x00CC` | `ActorInstantiatePacket` | 192 |
| -1 | `0x0137` | `SetActorPropetyPacket` | 488 |
| 0 | `0x018A` | `_0x018A` | 656 |
| 1 | `0x0189` | `CreateNamedGroupMultiple` | 792 |
| 2-6 | `0x0136` | `SetEventStatusPacket` | 1344-1632 |

On the same main connection, the nearest earlier c2s frame contains three
`0x0007` events. Its raw outer value is 214 units lower and its complete frame
arrives 107,421 microseconds before the anchor frame. The nearest later
c2s frame contains `0x01CE`, `0x0007`, and `0x0001`; its raw outer value is 151
units higher and its complete frame arrives 257,778 microseconds after
the anchor. Capture arrival and the raw outer values agree on earlier/later
ordering, but their numeric deltas differ and are not treated as the same clock.

## Promoted conclusions

The promoted conclusion is limited to the main-lane order, the c2s frame
bracket, capture-relative timing, frame/sub-event positions, and byte hashes in
the two derived artifacts. The neighborhood supports connection and phase
context, not a semantic packet noun for `0x018A`.

## Topics

- Login and pre-zone game-lane chronology
- TCP retransmission-safe reconstruction
- Main/chat connection separation
- Reproducible packet payload identity

## Evidence boundary

The s2c window is ordered only inside one reconstructed direction on one
connection. The c2s bracket uses the earliest capture point at which every byte
of each frame has arrived; first-byte witnesses are retained separately, and a
retransmission cannot replace an earlier complete witness. The main s2c
stream has 160 captured payload segments but only 82 unique reconstructed start
offsets, so concatenating capture-order payloads would be invalid.

The outer header's 8-byte field is retained verbatim as
`a41e8bee3b010000` for the anchor. Its little-endian differences are useful as
numeric order checks, but this study does not promote the field as wall-clock
time. Capture timestamps independently establish the c2s bracket.

## Evidence gaps

One event cannot establish the meaning of `0x018A`, whether its adjacency to
`0x0189` is invariant, or a causal relation between them. Same-frame ordering
does not expose processing time between sub-events.

## Further research

Another retained or newly preserved retail login with `0x018A` would be needed
to test whether the same `0x0137 -> 0x018A -> 0x0189` neighborhood repeats.

## Verification

The unified checks reproduce the study from the admitted capture corpus. The
focused unit tests reject a chat-lane anchor, prevent a neighborhood from
crossing connection or direction boundaries, select the earliest packet
witness when retransmitted segments overlap a frame start, and distinguish a
fragmented frame's first-byte packet from its completion packet.
