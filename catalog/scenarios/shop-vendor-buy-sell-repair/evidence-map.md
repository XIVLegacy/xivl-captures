# Vendor - Buy, Sell, Repair - Evidence Map

Reference scenario. Raw captures live in this repo's `sources/pcap-1.23b/objects/`; this map distils their opcode evidence by joining this repo's own `derived/observations.json` (numeric truth) against `derived/opcode_names.json` (names, promoted from xivl-opcodes:opcodes.json).

## Captures (3)

- `buy_square_maple_shield.pcapng` - 54,088 B, 18 distinct opcodes (map 19).
- `sell_item.pcapng` - 57,580 B, 23 distinct opcodes (map 24).
- `repair_items.pcapng` - 63,400 B, 24 distinct opcodes (map 25).

## Observed opcodes (30 distinct)

Union across the member captures. `name` is the derived/opcode_names.json entry name; `retail class` is the retail_class_name attribution when known.

| opcode | service | direction | name | retail class | payload lengths |
|---|---|---|---|---|---|
| `0x0001` | map | clientbound | PongPacket | - | 64 |
| `0x0001` | map | serverbound | PingPacket | - | 56 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00cc` | map | serverbound | LockTargetPacket | - | 40 |
| `0x00cd` | map | serverbound | SetTargetPacket | - | 40 |
| `0x00cf` | map | clientbound | MoveActorToPositionPacket | - | 80 |
| `0x00d0` | map | clientbound | SetActorSpeedPacket | - | 168 |
| `0x00d2` | map | clientbound | _0x00D2 | - | 40 |
| `0x00d3` | map | clientbound | SetActorTargetAnimatedPacket | Application::Lua::Script::Client::Command::Network::SetTargetTimeReceiver | 40 |
| `0x00d9` | map | clientbound | PlayBGAnimation | - | 40 |
| `0x012d` | map | serverbound | EventStartPacket | - | 216 |
| `0x012e` | map | serverbound | EventUpdatePacket | - | 120 |
| `0x0130` | map | clientbound | RunEventFunctionPacket | Application::Lua::Script::Client::Command::Network::StartServerOrderEventFunctionReceiver | 176 |
| `0x0131` | map | clientbound | EndEventPacket | Application::Lua::Script::Client::Command::Network::EndClientOrderEventReceiver | 80 |
| `0x013c` | map | clientbound | CommandResultX00Packet | - | 72 |
| `0x0144` | map | clientbound | SetActorSubStatePacket | Application::Lua::Script::Client::Command::System::ChangeActorSubStatModeBorderReceiver | 40 |
| `0x0146` | map | clientbound | InventorySetBeginPacket | - | 40 |
| `0x0147` | map | clientbound | InventorySetEndPacket | - | 40 |
| `0x0148` | map | clientbound | InventoryListX01Packet | - | 144 |
| `0x0149` | map | clientbound | InventoryListX08Packet | - | 936 |
| `0x014b` | map | clientbound | InventoryListX32Packet | - | 3616 |
| `0x014e` | map | clientbound | LinkedItemListX08Packet | - | 88 |
| `0x0153` | map | clientbound | InventoryRemoveX08Packet | - | 56 |
| `0x0169` | map | clientbound | _0x0169 | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 72 |
| `0x016d` | map | clientbound | InventoryBeginChangePacket | - | 40 |
| `0x016e` | map | clientbound | InventoryEndChangePacket | - | 40 |
| `0x018d` | map | clientbound | PartyMapMarkerUpdatePacket | - | 696 |
| `0x018f` | map | clientbound | _0x018F | - | 40 |
| `0x0190` | map | clientbound | _0x0190 | - | 136 |
| `0x0191` | map | clientbound | _0x0191 | - | 40 |

## Verification

- Every opcode above is sourced from this repo's own `derived/observations.json` (numeric truth) joined against `derived/opcode_names.json` (names) for the member pcaps - no hand-asserted opcodes.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
