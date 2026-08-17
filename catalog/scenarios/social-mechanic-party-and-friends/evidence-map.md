# Party and Friend List - Evidence Map

Reference scenario. Raw captures live in this repo's `sources/pcap-1.23b/objects/`; this map distils their opcode evidence by joining this repo's own `derived/observations.json` (numeric truth) against `derived/opcode_names.json` (names, promoted from xivl-opcodes:opcodes.json).

## Captures (3)

- `invite_join_party.pcapng` - 88,372 B, 16 distinct opcodes (map 18, world 6).
- `idle_in_party.pcapng` - 20,168 B, 4 distinct opcodes (map 5).
- `friendlist_search.pcapng` - 37,744 B, 9 distinct opcodes (map 11).

## Observed opcodes (29 distinct)

Union across the member captures. `name` is the derived/opcode_names.json entry name; `retail class` is the retail_class_name attribution when known.

| opcode | service | direction | name | retail class | payload lengths |
|---|---|---|---|---|---|
| `0x0133` | world | serverbound | GroupWorkUpdatePacket | - | 72 |
| `0x017a` | world | clientbound | SynchGroupWorkValuesPacket | - | 176 |
| `0x017c` | world | clientbound | GroupHeaderPacket | - | 152 |
| `0x017d` | world | clientbound | GroupMembersBeginPacket | - | 64 |
| `0x017e` | world | clientbound | GroupMembersEndPacket | - | 56 |
| `0x017f` | world | clientbound | GroupMembersX08Packet | - | 440 |
| `0x0001` | map | clientbound | PongPacket | - | 64 |
| `0x0001` | map | serverbound | PingPacket | - | 56 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00cf` | map | clientbound | MoveActorToPositionPacket | - | 80 |
| `0x012d` | map | serverbound | EventStartPacket | - | 216 |
| `0x012f` | map | serverbound | WorkStateUpdatePacket | - | 72 |
| `0x0133` | map | serverbound | GroupWorkUpdatePacket | - | 72 |
| `0x0137` | map | clientbound | SetActorPropetyPacket | Application::Lua::Script::Client::Command::Network::SyncMemoryReceiver | 168 |
| `0x0143` | map | clientbound | DeleteGroupPacket | - | 64 |
| `0x0145` | map | clientbound | SetActorIconPacket | Application::Lua::Script::Client::Command::Network::ChangeActorExtraStatReceiver | 40 |
| `0x0169` | map | clientbound | _0x0169 | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 72 |
| `0x017a` | map | clientbound | SynchGroupWorkValuesPacket | - | 176 |
| `0x017c` | map | clientbound | GroupHeaderPacket | - | 152 |
| `0x017d` | map | clientbound | GroupMembersBeginPacket | - | 64 |
| `0x017e` | map | clientbound | GroupMembersEndPacket | - | 56 |
| `0x017f` | map | clientbound | GroupMembersX08Packet | - | 440 |
| `0x0187` | map | clientbound | SetOccupancyGroupPacket | - | 96 |
| `0x018d` | map | clientbound | PartyMapMarkerUpdatePacket | - | 696 |
| `0x01cf` | map | clientbound | _0x01CF | - | 1640 |
| `0x01cf` | map | serverbound | _0x01CFHandler | - | 40 |
| `0x01dd` | map | serverbound | _0x01DD | - | 296 |
| `0x01df` | map | clientbound | _0x01DF | - | 968 |
| `0x01e0` | map | clientbound | PlayerSearchCommentResultPacket | - | 648 |

## Verification

- Every opcode above is sourced from this repo's own `derived/observations.json` (numeric truth) joined against `derived/opcode_names.json` (names) for the member pcaps - no hand-asserted opcodes.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
