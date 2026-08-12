# Aetheryte Teleport Flows - Evidence Map

Reference scenario. Raw captures live in this repo's `sources/pcap-1.23b/objects/`; this map distils their opcode evidence by joining this repo's own `derived/observations.json` (numeric truth) against `derived/opcode_names.json` (names, promoted from xivl-opcodes:opcodes.json).

## Captures (4)

- `teleport_to_camp_nine_ivies.pcapng` - 80,004 B, 61 distinct opcodes (map 65, world 6).
- `teleport_to_camp_tranquil.pcapng` - 67,920 B, 61 distinct opcodes (map 65, world 6).
- `teleport_to_gridania.pcapng` - 67,620 B, 65 distinct opcodes (map 69, world 6).
- `return_to_inn.pcapng` - 44,012 B, 61 distinct opcodes (map 65, world 6).

## Observed opcodes (79 distinct)

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
| `0x0005` | map | clientbound | SetMapPacket | - | 48 |
| `0x0006` | map | clientbound | _0x0006 | - | 40 |
| `0x0007` | map | clientbound | DeleteAllActorsPacket | - | 40 |
| `0x0007` | map | serverbound | ZoneInCompletePacket | - | 40 |
| `0x0008` | map | clientbound | _0x0008 | - | 80 |
| `0x0009` | map | clientbound | _0x0009 | - | 112 |
| `0x000c` | map | clientbound | SetMusicPacket | - | 40 |
| `0x000d` | map | clientbound | SetWeatherPacket | - | 40 |
| `0x000f` | map | clientbound | _0xFPacket | - | 56 |
| `0x0010` | map | clientbound | SetDalamudPacket | - | 40 |
| `0x00ca` | map | clientbound | AddActorPacket | - | 40 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00cc` | map | clientbound | ActorInstantiatePacket | - | 296 |
| `0x00ce` | map | clientbound | SetActorPositionPacket | - | 72 |
| `0x00cf` | map | clientbound | MoveActorToPositionPacket | - | 80 |
| `0x00d0` | map | clientbound | SetActorSpeedPacket | - | 168 |
| `0x00d6` | map | clientbound | SetActorAppearancePacket | - | 296 |
| `0x00da` | map | clientbound | PlayAnimationOnActorPacket | - | 40 |
| `0x00e2` | map | clientbound | _0xE2Packet | - | 40 |
| `0x012d` | map | serverbound | EventStartPacket | - | 216 |
| `0x012e` | map | clientbound | SetTalkEventCondition | Application::Lua::Script::Client::Command::Network::SetTalkEventConditionReceiver | 72 |
| `0x012e` | map | serverbound | EventUpdatePacket | - | 120 |
| `0x0130` | map | clientbound | RunEventFunctionPacket | Application::Lua::Script::Client::Command::Network::StartServerOrderEventFunctionReceiver | 176 |
| `0x0131` | map | clientbound | EndEventPacket | Application::Lua::Script::Client::Command::Network::EndClientOrderEventReceiver | 80 |
| `0x0132` | map | clientbound | _0x132Packet | - | 72 |
| `0x0133` | map | serverbound | GroupWorkUpdatePacket | - | 72 |
| `0x0134` | map | clientbound | SetActorStatePacket | - | 40 |
| `0x0136` | map | clientbound | SetEventStatusPacket | Application::Lua::Script::Client::Command::Network::SetEventStatusReceiver | 72 |
| `0x0137` | map | clientbound | SetActorPropetyPacket | Application::Lua::Script::Client::Command::Network::SyncMemoryReceiver | 168 |
| `0x0139` | map | clientbound | CommandResultX01Packet | - | 88 |
| `0x013d` | map | clientbound | SetActorNamePacket | Application::Lua::Script::Client::Command::Network::SetDisplayNameReceiver | 72 |
| `0x0144` | map | clientbound | SetActorSubStatePacket | Application::Lua::Script::Client::Command::System::ChangeActorSubStatModeBorderReceiver | 40 |
| `0x0145` | map | clientbound | SetActorIconPacket | Application::Lua::Script::Client::Command::Network::ChangeActorExtraStatReceiver | 40 |
| `0x0146` | map | clientbound | InventorySetBeginPacket | - | 40 |
| `0x0147` | map | clientbound | InventorySetEndPacket | - | 40 |
| `0x0148` | map | clientbound | InventoryListX01Packet | - | 144 |
| `0x0149` | map | clientbound | InventoryListX08Packet | - | 936 |
| `0x014a` | map | clientbound | InventoryListX16Packet | - | 1824 |
| `0x014b` | map | clientbound | InventoryListX32Packet | - | 3616 |
| `0x014e` | map | clientbound | LinkedItemListX08Packet | - | 88 |
| `0x0152` | map | clientbound | InventoryRemoveX01Packet | - | 40 |
| `0x0153` | map | clientbound | InventoryRemoveX08Packet | - | 56 |
| `0x0166` | map | clientbound | _0x0166 | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 40 |
| `0x0168` | map | clientbound | _0x0168 | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 56 |
| `0x0169` | map | clientbound | _0x0169 | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 72 |
| `0x016b` | map | clientbound | SetNoticeEventCondition | Application::Lua::Script::Client::Command::Network::SetNoticeEventConditionReceiver | 72 |
| `0x016d` | map | clientbound | InventoryBeginChangePacket | - | 40 |
| `0x016e` | map | clientbound | InventoryEndChangePacket | - | 40 |
| `0x016f` | map | clientbound | SetPushEventConditionWithCircle | Application::Lua::Script::Client::Command::Network::SetPushEventConditionWithCircleReceiver | 88 |
| `0x0177` | map | clientbound | SetActorStatusPacket | - | 40 |
| `0x0179` | map | clientbound | SetActorStatusAllPacket | Application::Lua::Script::Client::Command::System::ChangeActorSubStatStatusReceiver | 72 |
| `0x017a` | map | clientbound | SynchGroupWorkValuesPacket | - | 176 |
| `0x017b` | map | clientbound | SetActorIsZoningPacket | Application::Lua::Script::Client::Command::Network::ChangeShadowActorFlagReceiver | 40 |
| `0x017c` | map | clientbound | GroupHeaderPacket | - | 152 |
| `0x017d` | map | clientbound | GroupMembersBeginPacket | - | 64 |
| `0x017e` | map | clientbound | GroupMembersEndPacket | - | 56 |
| `0x017f` | map | clientbound | GroupMembersX08Packet | - | 440 |
| `0x0183` | map | clientbound | ContentMembersX08Packet | - | 152 |
| `0x0187` | map | clientbound | _0x0187 | - | 96 |
| `0x018d` | map | clientbound | _0x018D | - | 696 |
| `0x0193` | map | clientbound | _0x0193 | - | 40 |
| `0x0194` | map | clientbound | SetGrandCompanyPacket | Application::Lua::Script::Client::Command::Network::GrandCompanyReceiver | 40 |
| `0x0196` | map | clientbound | SetSpecialEventWorkPacket | - | 56 |
| `0x0198` | map | clientbound | SetChocoboNamePacket | Application::Lua::Script::Client::Command::System::ChocoboReceiver | 64 |
| `0x0199` | map | clientbound | SetHasChocoboPacket | - | 40 |
| `0x019a` | map | clientbound | SetCompletedAchievementsPacket | - | 160 |
| `0x019b` | map | clientbound | SetLatestAchievementsPacket | - | 64 |
| `0x019c` | map | clientbound | SetAchievementPointsPacket | Application::Lua::Script::Client::Command::Network::AchievementPointReceiver | 40 |
| `0x019d` | map | clientbound | SetPlayerTitlePacket | Application::Lua::Script::Client::Command::Network::AchievementTitleReceiver | 40 |
| `0x01a3` | map | clientbound | SetCutsceneBookPacket | - | 336 |
| `0x01a4` | map | clientbound | SetCurrentJobPacket | Application::Lua::Script::Client::Command::Network::JobChangeReceiver | 40 |

## Verification

- Every opcode above is sourced from this repo's own `derived/observations.json` (numeric truth) joined against `derived/opcode_names.json` (names) for the member pcaps - no hand-asserted opcodes.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
