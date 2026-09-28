# Inventory and Gear Changes - Evidence Map

This map joins two repository-owned products:

- `derived/observations.json` supplies numeric observations.
- `derived/opcode_names.json` supplies names promoted from xivl-opcodes:opcodes.json.
- Raw captures live in `sources/pcap-1.23b/objects/`.

## Captures (6)

- `inventory.pcapng` - 27,908 B, 5 distinct opcodes (map 6).
- `open_gear_menu.pcapng` - 25,940 B, 5 distinct opcodes (map 6).
- `change_bodyarmor.pcapng` - 54,536 B, 17 distinct opcodes (map 18).
- `change_helm.pcapng` - 39,660 B, 18 distinct opcodes (map 19).
- `gear_changesoul.pcapng` - 23,784 B, 12 distinct opcodes (map 13).
- `gear_changeweapon.pcapng` - 21,352 B, 18 distinct opcodes (map 19).

## Observed opcodes (23 distinct)

Union across the member captures. `name` is the derived/opcode_names.json entry name; `retail class` is the retail_class_name attribution when known.

| opcode | service | direction | name | retail class | payload lengths |
|---|---|---|---|---|---|
| `0x0001` | map | clientbound | PongPacket | - | 64 |
| `0x0001` | map | serverbound | PingPacket | - | 56 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00cf` | map | clientbound | MoveActorToPositionPacket | - | 80 |
| `0x00d0` | map | clientbound | SetActorSpeedPacket | - | 168 |
| `0x00d6` | map | clientbound | SetActorAppearancePacket | - | 296 |
| `0x00da` | map | clientbound | PlayAnimationOnActorPacket | - | 40 |
| `0x012d` | map | serverbound | EventStartPacket | - | 216 |
| `0x012f` | map | serverbound | WorkStateUpdatePacket | - | 72 |
| `0x0137` | map | clientbound | SetActorPropetyPacket | Application::Lua::Script::Client::Command::Network::SyncMemoryReceiver | 168 |
| `0x0139` | map | clientbound | CommandResultX01Packet | - | 88 |
| `0x0144` | map | clientbound | SetActorSubStatePacket | Application::Lua::Script::Client::Command::System::ChangeActorSubStatModeBorderReceiver | 40 |
| `0x0146` | map | clientbound | InventorySetBeginPacket | - | 40 |
| `0x0147` | map | clientbound | InventorySetEndPacket | - | 40 |
| `0x0148` | map | clientbound | InventoryListX01Packet | - | 144 |
| `0x0149` | map | clientbound | InventoryListX08Packet | - | 936 |
| `0x014d` | map | clientbound | LinkedItemListX01Packet | - | 40 |
| `0x0152` | map | clientbound | InventoryRemoveX01Packet | - | 40 |
| `0x015a` | map | clientbound | _0x015A | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 80 |
| `0x015b` | map | clientbound | _0x015B | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 112 |
| `0x016d` | map | clientbound | InventoryBeginChangePacket | - | 40 |
| `0x016e` | map | clientbound | InventoryEndChangePacket | - | 40 |
| `0x01a4` | map | clientbound | SetCurrentJobPacket | Application::Lua::Script::Client::Command::Network::JobChangeReceiver | 40 |

## Verification

- Every opcode above comes from `derived/observations.json` joined with `derived/opcode_names.json` for the member pcaps. No opcode is added manually.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
