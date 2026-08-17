# War Quest Updates - Evidence Map

This map joins two repository-owned products:

- `derived/observations.json` supplies numeric observations.
- `derived/opcode_names.json` supplies names promoted from xivl-opcodes:opcodes.json.
- Raw captures live in `sources/pcap-1.23b/objects/`.

## Captures (3)

- `war_quest_update1.pcapng` - 42,812 B, 19 distinct opcodes (map 20).
- `war_quest_update2.pcapng` - 206,216 B, 67 distinct opcodes (map 71, world 8).
- `war_quest_update3.pcapng` - 103,520 B, 40 distinct opcodes (map 43, world 5).

## Observed opcodes (82 distinct)

Union across the member captures. `name` is the derived/opcode_names.json entry name; `retail class` is the retail_class_name attribution when known.

| opcode | service | direction | name | retail class | payload lengths |
|---|---|---|---|---|---|
| `0x00c9` | world | clientbound | PartyChatMessagePacket | - | 584 |
| `0x00c9` | world | serverbound | PartyChatMessagePacket | - | 552 |
| `0x0133` | world | serverbound | GroupWorkUpdatePacket | - | 72 |
| `0x017a` | world | clientbound | SynchGroupWorkValuesPacket | - | 176 |
| `0x017c` | world | clientbound | GroupHeaderPacket | - | 152 |
| `0x017d` | world | clientbound | GroupMembersBeginPacket | - | 64 |
| `0x017e` | world | clientbound | GroupMembersEndPacket | - | 56 |
| `0x017f` | world | clientbound | GroupMembersX08Packet | - | 440 |
| `0x0001` | map | clientbound | PongPacket | - | 64 |
| `0x0001` | map | serverbound | PingPacket | - | 56 |
| `0x0006` | map | clientbound | _0x0006 | - | 40 |
| `0x0007` | map | clientbound | DeleteAllActorsPacket | - | 40 |
| `0x0007` | map | serverbound | ZoneInCompletePacket | - | 40 |
| `0x0008` | map | clientbound | _0x0008 | - | 80 |
| `0x000c` | map | clientbound | SetMusicPacket | - | 40 |
| `0x000d` | map | clientbound | SetWeatherPacket | - | 40 |
| `0x000f` | map | clientbound | _0xFPacket | - | 56 |
| `0x0010` | map | clientbound | SetDalamudPacket | - | 40 |
| `0x00ca` | map | clientbound | AddActorPacket | - | 40 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00cb` | map | clientbound | RemoveActorPacket | - | 40 |
| `0x00cc` | map | clientbound | ActorInstantiatePacket | - | 296 |
| `0x00cc` | map | serverbound | LockTargetPacket | - | 40 |
| `0x00cd` | map | serverbound | SetTargetPacket | - | 40 |
| `0x00ce` | map | clientbound | SetActorPositionPacket | - | 72 |
| `0x00cf` | map | clientbound | MoveActorToPositionPacket | - | 80 |
| `0x00d0` | map | clientbound | SetActorSpeedPacket | - | 168 |
| `0x00d2` | map | clientbound | _0x00D2 | - | 40 |
| `0x00d3` | map | clientbound | SetActorTargetAnimatedPacket | Application::Lua::Script::Client::Command::Network::SetTargetTimeReceiver | 40 |
| `0x00d6` | map | clientbound | SetActorAppearancePacket | - | 296 |
| `0x00db` | map | clientbound | SetActorTargetPacket | - | 40 |
| `0x00de` | map | clientbound | _0x00DE | - | 40 |
| `0x00e1` | map | clientbound | ActorDoEmotePacket | - | 48 |
| `0x00e2` | map | clientbound | _0xE2Packet | - | 40 |
| `0x00e3` | map | clientbound | SetActorQuestGraphicPacket | - | 40 |
| `0x012d` | map | serverbound | EventStartPacket | - | 216 |
| `0x012e` | map | serverbound | EventUpdatePacket | - | 120 |
| `0x012f` | map | clientbound | KickEventPacket | Application::Lua::Script::Client::Command::Network::KickClientOrderEventReceiver | 144 |
| `0x0130` | map | clientbound | RunEventFunctionPacket | Application::Lua::Script::Client::Command::Network::StartServerOrderEventFunctionReceiver | 176 |
| `0x0131` | map | clientbound | EndEventPacket | Application::Lua::Script::Client::Command::Network::EndClientOrderEventReceiver | 80 |
| `0x0133` | map | clientbound | GenericDataPacket | Application::Lua::Script::Client::Command::Network::UserDataReceiver | 224 |
| `0x0133` | map | serverbound | GroupWorkUpdatePacket | - | 72 |
| `0x0134` | map | clientbound | SetActorStatePacket | - | 40 |
| `0x0136` | map | clientbound | SetEventStatusPacket | Application::Lua::Script::Client::Command::Network::SetEventStatusReceiver | 72 |
| `0x0137` | map | clientbound | SetActorPropetyPacket | Application::Lua::Script::Client::Command::Network::SyncMemoryReceiver | 168 |
| `0x0139` | map | clientbound | CommandResultX01Packet | - | 88 |
| `0x013a` | map | clientbound | CommandResultX10Packet | - | 216 |
| `0x013d` | map | clientbound | SetActorNamePacket | Application::Lua::Script::Client::Command::Network::SetDisplayNameReceiver | 72 |
| `0x0143` | map | clientbound | DeleteGroupPacket | - | 64 |
| `0x0144` | map | clientbound | SetActorSubStatePacket | Application::Lua::Script::Client::Command::System::ChangeActorSubStatModeBorderReceiver | 40 |
| `0x0145` | map | clientbound | SetActorIconPacket | Application::Lua::Script::Client::Command::Network::ChangeActorExtraStatReceiver | 40 |
| `0x0146` | map | clientbound | InventorySetBeginPacket | - | 40 |
| `0x0147` | map | clientbound | InventorySetEndPacket | - | 40 |
| `0x0148` | map | clientbound | InventoryListX01Packet | - | 144 |
| `0x0157` | map | clientbound | _0x0157 | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 48 |
| `0x015a` | map | clientbound | _0x015A | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 80 |
| `0x0167` | map | clientbound | _0x0167 | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 56 |
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
| `0x0187` | map | clientbound | SetOccupancyGroupPacket | - | 96 |
| `0x018b` | map | clientbound | SetGroupLayoutIDPacket | - | 88 |
| `0x018d` | map | clientbound | PartyMapMarkerUpdatePacket | - | 696 |
| `0x018f` | map | clientbound | _0x018F | - | 40 |
| `0x0190` | map | clientbound | _0x0190 | - | 136 |
| `0x0191` | map | clientbound | _0x0191 | - | 40 |
| `0x0193` | map | clientbound | _0x0193 | - | 40 |
| `0x0194` | map | clientbound | SetGrandCompanyPacket | Application::Lua::Script::Client::Command::Network::GrandCompanyReceiver | 40 |
| `0x0195` | map | clientbound | SetEnmityIndicator | Application::Lua::Script::Client::Command::Network::HateStatusReceiver | 40 |
| `0x019d` | map | clientbound | SetPlayerTitlePacket | Application::Lua::Script::Client::Command::Network::AchievementTitleReceiver | 40 |
| `0x01a4` | map | clientbound | SetCurrentJobPacket | Application::Lua::Script::Client::Command::Network::JobChangeReceiver | 40 |

## Verification

- Every opcode above comes from `derived/observations.json` joined with `derived/opcode_names.json` for the member pcaps. No opcode is added manually.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
- The `war_quest` filename is read here as a Warrior job questline, hence content_kind job-quest / progression_track job-quest. This is a filename inference only - not confirmed against the quest data - and could instead be a story or other quest. Refine when the quest is identified.
