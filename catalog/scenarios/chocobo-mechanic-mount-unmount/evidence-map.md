# Chocobo Mount / Unmount - Evidence Map

Reference scenario. Raw captures live in this repo's `sources/pcap-1.23b/objects/`; this map distils their opcode evidence by joining this repo's own `derived/observations.json` (numeric truth) against `derived/opcode_names.json` (names, promoted from xivl-opcodes:opcodes.json).

## Captures (1)

- `mount_unmount_chocobo.pcapng` - 21,240 B, 13 distinct opcodes (map 14).

## Observed opcodes (14 distinct)

Union across the member captures. `name` is the derived/opcode_names.json entry name; `retail class` is the retail_class_name attribution when known.

| opcode | service | direction | name | retail class | payload lengths |
|---|---|---|---|---|---|
| `0x0001` | map | clientbound | PongPacket | - | 64 |
| `0x0001` | map | serverbound | PingPacket | - | 56 |
| `0x000c` | map | clientbound | SetMusicPacket | - | 40 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00d0` | map | clientbound | SetActorSpeedPacket | - | 168 |
| `0x012d` | map | serverbound | EventStartPacket | - | 216 |
| `0x0131` | map | clientbound | EndEventPacket | Application::Lua::Script::Client::Command::Network::EndClientOrderEventReceiver | 80 |
| `0x0134` | map | clientbound | SetActorStatePacket | - | 40 |
| `0x0139` | map | clientbound | CommandResultX01Packet | - | 88 |
| `0x013c` | map | clientbound | CommandResultX00Packet | - | 72 |
| `0x0157` | map | clientbound | _0x0157 | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 48 |
| `0x018b` | map | clientbound | SetGroupLayoutIDPacket | - | 88 |
| `0x018d` | map | clientbound | PartyMapMarkerUpdatePacket | - | 696 |
| `0x0197` | map | clientbound | SetCurrentMountChocoboPacket | Application::Lua::Script::Client::Command::System::ChocoboGradeReceiver | 40 |

## Verification

- Every opcode above is sourced from this repo's own `derived/observations.json` (numeric truth) joined against `derived/opcode_names.json` (names) for the member pcaps - no hand-asserted opcodes.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
