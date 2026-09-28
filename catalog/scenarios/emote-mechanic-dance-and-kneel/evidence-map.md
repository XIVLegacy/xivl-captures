# Emotes - Dance, Kneel - Evidence Map

This map joins two repository-owned products:

- `derived/observations.json` supplies numeric observations.
- `derived/opcode_names.json` supplies names promoted from xivl-opcodes:opcodes.json.
- Raw captures live in `sources/pcap-1.23b/objects/`.

## Captures (2)

- `emote_dance.pcapng` - 30,352 B, 5 distinct opcodes (map 6).
- `emote_kneel.pcapng` - 23,920 B, 5 distinct opcodes (map 6).

## Observed opcodes (6 distinct)

Union across the member captures. `name` is the derived/opcode_names.json entry name; `retail class` is the retail_class_name attribution when known.

| opcode | service | direction | name | retail class | payload lengths |
|---|---|---|---|---|---|
| `0x0001` | map | clientbound | PongPacket | - | 64 |
| `0x0001` | map | serverbound | PingPacket | - | 56 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00cf` | map | clientbound | MoveActorToPositionPacket | - | 80 |
| `0x00e1` | map | clientbound | ActorDoEmotePacket | - | 48 |
| `0x012d` | map | serverbound | EventStartPacket | - | 216 |

## Verification

- Every opcode above comes from `derived/observations.json` joined with `derived/opcode_names.json` for the member pcaps. No opcode is added manually.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
