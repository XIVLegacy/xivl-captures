# Quest - Accept, Journal, Update - Evidence Map

Reference scenario. Raw captures live in this repo's `sources/pcap-1.23b/objects/`; this map distils their opcode evidence by joining this repo's own `derived/observations.json` (numeric truth) against `derived/opcode_names.json` (names, promoted from xivl-opcodes:opcodes.json).

## Captures (3)

- `accept_quest.pcapng` - 53,180 B, 15 distinct opcodes (map 16).
- `quest_journal.pcapng` - 32,264 B, 5 distinct opcodes (map 6).
- `quest_update.pcapng` - 66,756 B, 14 distinct opcodes (map 15).

## Observed opcodes (17 distinct)

Union across the member captures. `name` is the derived/opcode_names.json entry name; `retail class` is the retail_class_name attribution when known.

| opcode | service | direction | name | retail class | payload lengths |
|---|---|---|---|---|---|
| `0x0001` | map | clientbound | PongPacket | - | 64 |
| `0x0001` | map | serverbound | PingPacket | - | 56 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00cc` | map | serverbound | LockTargetPacket | - | 40 |
| `0x00cd` | map | serverbound | SetTargetPacket | - | 40 |
| `0x00cf` | map | clientbound | MoveActorToPositionPacket | - | 80 |
| `0x00d2` | map | clientbound | _0x00D2 | - | 40 |
| `0x00d3` | map | clientbound | SetActorTargetAnimatedPacket | Application::Lua::Script::Client::Command::Network::SetTargetTimeReceiver | 40 |
| `0x00e3` | map | clientbound | SetActorQuestGraphicPacket | - | 40 |
| `0x012d` | map | serverbound | EventStartPacket | - | 216 |
| `0x012e` | map | serverbound | EventUpdatePacket | - | 120 |
| `0x0130` | map | clientbound | RunEventFunctionPacket | Application::Lua::Script::Client::Command::Network::StartServerOrderEventFunctionReceiver | 176 |
| `0x0131` | map | clientbound | EndEventPacket | Application::Lua::Script::Client::Command::Network::EndClientOrderEventReceiver | 80 |
| `0x0133` | map | clientbound | GenericDataPacket | Application::Lua::Script::Client::Command::Network::UserDataReceiver | 224 |
| `0x0137` | map | clientbound | SetActorPropetyPacket | Application::Lua::Script::Client::Command::Network::SyncMemoryReceiver | 168 |
| `0x0167` | map | clientbound | _0x0167 | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 56 |
| `0x018d` | map | clientbound | _0x018D | - | 696 |

## Verification

- Every opcode above is sourced from this repo's own `derived/observations.json` (numeric truth) joined against `derived/opcode_names.json` (names) for the member pcaps - no hand-asserted opcodes.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
- content_kind side-quest is the generic quest-state reading; the captures do not identify the specific quest, so it could be a class/job/story quest. Refine if the quest is identified.
