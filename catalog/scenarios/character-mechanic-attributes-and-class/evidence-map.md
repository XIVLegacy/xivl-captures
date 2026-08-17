# Attributes and Class Switching - Evidence Map

Reference scenario. Raw captures live in this repo's `sources/pcap-1.23b/objects/`; this map distils their opcode evidence by joining this repo's own `derived/observations.json` (numeric truth) against `derived/opcode_names.json` (names, promoted from xivl-opcodes:opcodes.json).

## Captures (4)

- `add_str.pcapng` - 20,056 B, 11 distinct opcodes (map 12).
- `attributes.pcapng` - 22,624 B, 5 distinct opcodes (map 6).
- `change_to_botanist.pcapng` - 41,500 B, 21 distinct opcodes (map 22).
- `switch_to_weaver.pcapng` - 33,364 B, 23 distinct opcodes (map 24).

## Observed opcodes (28 distinct)

Union across the member captures. `name` is the derived/opcode_names.json entry name; `retail class` is the retail_class_name attribution when known.

| opcode | service | direction | name | retail class | payload lengths |
|---|---|---|---|---|---|
| `0x0001` | map | clientbound | PongPacket | - | 64 |
| `0x0001` | map | serverbound | PingPacket | - | 56 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00cf` | map | clientbound | MoveActorToPositionPacket | - | 80 |
| `0x00d0` | map | clientbound | SetActorSpeedPacket | - | 168 |
| `0x00d6` | map | clientbound | SetActorAppearancePacket | - | 296 |
| `0x00e3` | map | clientbound | SetActorQuestGraphicPacket | - | 40 |
| `0x012d` | map | serverbound | EventStartPacket | - | 216 |
| `0x012e` | map | serverbound | EventUpdatePacket | - | 120 |
| `0x012f` | map | serverbound | WorkStateUpdatePacket | - | 72 |
| `0x0130` | map | clientbound | RunEventFunctionPacket | Application::Lua::Script::Client::Command::Network::StartServerOrderEventFunctionReceiver | 176 |
| `0x0131` | map | clientbound | EndEventPacket | Application::Lua::Script::Client::Command::Network::EndClientOrderEventReceiver | 80 |
| `0x0137` | map | clientbound | SetActorPropetyPacket | Application::Lua::Script::Client::Command::Network::SyncMemoryReceiver | 168 |
| `0x0139` | map | clientbound | CommandResultX01Packet | - | 88 |
| `0x0144` | map | clientbound | SetActorSubStatePacket | Application::Lua::Script::Client::Command::System::ChangeActorSubStatModeBorderReceiver | 40 |
| `0x0146` | map | clientbound | InventorySetBeginPacket | - | 40 |
| `0x0147` | map | clientbound | InventorySetEndPacket | - | 40 |
| `0x0148` | map | clientbound | InventoryListX01Packet | - | 144 |
| `0x0149` | map | clientbound | InventoryListX08Packet | - | 936 |
| `0x014d` | map | clientbound | LinkedItemListX01Packet | - | 40 |
| `0x0152` | map | clientbound | InventoryRemoveX01Packet | - | 40 |
| `0x0159` | map | clientbound | _0x0159 | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 64 |
| `0x015a` | map | clientbound | _0x015A | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 80 |
| `0x015b` | map | clientbound | _0x015B | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 112 |
| `0x016d` | map | clientbound | InventoryBeginChangePacket | - | 40 |
| `0x016e` | map | clientbound | InventoryEndChangePacket | - | 40 |
| `0x018d` | map | clientbound | PartyMapMarkerUpdatePacket | - | 696 |
| `0x01a4` | map | clientbound | SetCurrentJobPacket | Application::Lua::Script::Client::Command::Network::JobChangeReceiver | 40 |

## Verification

- Every opcode above is sourced from this repo's own `derived/observations.json` (numeric truth) joined against `derived/opcode_names.json` (names) for the member pcaps - no hand-asserted opcodes.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
