# Chat Channels - Say, Shout, NPC Talk - Evidence Map

Reference scenario. Raw captures live in this repo's `sources/pcap-1.23b/objects/`; this map distils their opcode evidence by joining this repo's own `derived/observations.json` (numeric truth) against `derived/opcode_names.json` (names, promoted from xivl-opcodes:opcodes.json).

## Captures (3)

- `chat_say.pcapng` - 8,864 B, 5 distinct opcodes (map 6).
- `chat_shout.pcapng` - 7,872 B, 5 distinct opcodes (map 6).
- `small_talk_louisoix.pcapng` - 18,444 B, 25 distinct opcodes (map 29).

## Observed opcodes (30 distinct)

Union across the member captures. `name` is the derived/opcode_names.json entry name; `retail class` is the retail_class_name attribution when known.

| opcode | service | direction | name | retail class | payload lengths |
|---|---|---|---|---|---|
| `0x0001` | map | clientbound | PongPacket | - | 64 |
| `0x0001` | map | serverbound | PingPacket | - | 56 |
| `0x0003` | map | serverbound | ChatMessagePacket | - | 576 |
| `0x00ca` | map | clientbound | AddActorPacket | - | 40 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00cc` | map | clientbound | ActorInstantiatePacket | - | 296 |
| `0x00cc` | map | serverbound | LockTargetPacket | - | 40 |
| `0x00cd` | map | serverbound | SetTargetPacket | - | 40 |
| `0x00ce` | map | clientbound | SetActorPositionPacket | - | 72 |
| `0x00cf` | map | clientbound | MoveActorToPositionPacket | - | 80 |
| `0x00d0` | map | clientbound | SetActorSpeedPacket | - | 168 |
| `0x00d2` | map | clientbound | _0x00D2 | - | 40 |
| `0x00d3` | map | clientbound | SetActorTargetAnimatedPacket | Application::Lua::Script::Client::Command::Network::SetTargetTimeReceiver | 40 |
| `0x00d6` | map | clientbound | SetActorAppearancePacket | - | 296 |
| `0x012d` | map | serverbound | EventStartPacket | - | 216 |
| `0x012e` | map | clientbound | SetTalkEventCondition | Application::Lua::Script::Client::Command::Network::SetTalkEventConditionReceiver | 72 |
| `0x012e` | map | serverbound | EventUpdatePacket | - | 120 |
| `0x0130` | map | clientbound | RunEventFunctionPacket | Application::Lua::Script::Client::Command::Network::StartServerOrderEventFunctionReceiver | 176 |
| `0x0131` | map | clientbound | EndEventPacket | Application::Lua::Script::Client::Command::Network::EndClientOrderEventReceiver | 80 |
| `0x0134` | map | clientbound | SetActorStatePacket | - | 40 |
| `0x0136` | map | clientbound | SetEventStatusPacket | Application::Lua::Script::Client::Command::Network::SetEventStatusReceiver | 72 |
| `0x0137` | map | clientbound | SetActorPropetyPacket | Application::Lua::Script::Client::Command::Network::SyncMemoryReceiver | 168 |
| `0x013d` | map | clientbound | SetActorNamePacket | Application::Lua::Script::Client::Command::Network::SetDisplayNameReceiver | 72 |
| `0x0144` | map | clientbound | SetActorSubStatePacket | Application::Lua::Script::Client::Command::System::ChangeActorSubStatModeBorderReceiver | 40 |
| `0x0145` | map | clientbound | SetActorIconPacket | Application::Lua::Script::Client::Command::Network::ChangeActorExtraStatReceiver | 40 |
| `0x016b` | map | clientbound | SetNoticeEventCondition | Application::Lua::Script::Client::Command::Network::SetNoticeEventConditionReceiver | 72 |
| `0x0179` | map | clientbound | SetActorStatusAllPacket | Application::Lua::Script::Client::Command::System::ChangeActorSubStatStatusReceiver | 72 |
| `0x017b` | map | clientbound | SetActorIsZoningPacket | Application::Lua::Script::Client::Command::Network::ChangeShadowActorFlagReceiver | 40 |
| `0x018b` | map | clientbound | SetGroupLayoutIDPacket | - | 88 |
| `0x018d` | map | clientbound | PartyMapMarkerUpdatePacket | - | 696 |

## Verification

- Every opcode above is sourced from this repo's own `derived/observations.json` (numeric truth) joined against `derived/opcode_names.json` (names) for the member pcaps - no hand-asserted opcodes.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
