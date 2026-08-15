# Login Handshake and In-World Idle - Evidence Map

Reference scenario. Raw captures live in this repo's `sources/pcap-1.23b/objects/`; this map distils their opcode evidence by joining this repo's own `derived/observations.json` (numeric truth) against `derived/opcode_names.json` (names, promoted from xivl-opcodes:opcodes.json).

## Captures (2)

- `login.pcapng` - 856,236 B, 0 distinct opcodes ().
- `idling.pcapng` - 42,608 B, 4 distinct opcodes (map 5).

## Observed opcodes (5 distinct)

Union across the member captures. `name` is the derived/opcode_names.json entry name; `retail class` is the retail_class_name attribution when known.

| opcode | service | direction | name | retail class | payload lengths |
|---|---|---|---|---|---|
| `0x0001` | map | clientbound | PongPacket | - | 64 |
| `0x0001` | map | serverbound | PingPacket | - | 56 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00cf` | map | clientbound | MoveActorToPositionPacket | - | 80 |
| `0x018d` | map | clientbound | _0x018D | - | 696 |

## Verification

- Every opcode above is sourced from this repo's own `derived/observations.json` (numeric truth) joined against `derived/opcode_names.json` (names) for the member pcaps - no hand-asserted opcodes.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
- login.pcapng contains TLS account-service connections and later raw lobby connections on TCP 54994. The lobby bodies remain undecoded after a tested decrypt recipe was refuted, so the capture is excluded from the canonical game decode and contributes zero observed opcodes here.
