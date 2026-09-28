# Cross-Zone Travel (Gridania / Black Shroud / Coerthas) - Evidence Map

This map joins two repository-owned products:

- `derived/observations.json` supplies numeric observations.
- `derived/opcode_names.json` supplies names promoted from xivl-opcodes:opcodes.json.
- Raw captures live in `sources/pcap-1.23b/objects/`.

## Captures (2)

- `gridania_to_coerthas.pcapng` - 939,832 B, 65 distinct opcodes (map 68, world 6).
- `from_gridania_to_blackshroud.pcapng` - 196,308 B, 55 distinct opcodes (map 57, world 6).

## Observed opcodes (74 distinct)

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
| `0x000c` | map | clientbound | SetMusicPacket | - | 40 |
| `0x000d` | map | clientbound | SetWeatherPacket | - | 40 |
| `0x000f` | map | clientbound | _0xFPacket | - | 56 |
| `0x0010` | map | clientbound | SetDalamudPacket | - | 40 |
| `0x00ca` | map | clientbound | AddActorPacket | - | 40 |
| `0x00ca` | map | serverbound | UpdatePlayerPositionPacket | - | 64 |
| `0x00cb` | map | clientbound | RemoveActorPacket | - | 40 |
| `0x00cc` | map | clientbound | ActorInstantiatePacket | - | 296 |
| `0x00ce` | map | clientbound | SetActorPositionPacket | - | 72 |
| `0x00cf` | map | clientbound | MoveActorToPositionPacket | - | 80 |
| `0x00d0` | map | clientbound | SetActorSpeedPacket | - | 168 |
| `0x00d6` | map | clientbound | SetActorAppearancePacket | - | 296 |
| `0x00d8` | map | clientbound | SetActorBGPropertiesPacket | - | 40 |
| `0x00d9` | map | clientbound | PlayBGAnimation | - | 40 |
| `0x00e2` | map | clientbound | _0xE2Packet | - | 40 |
| `0x012d` | map | serverbound | EventStartPacket | - | 216 |
| `0x012e` | map | clientbound | SetTalkEventCondition | Application::Lua::Script::Client::Command::Network::SetTalkEventConditionReceiver | 72 |
| `0x0131` | map | clientbound | EndEventPacket | Application::Lua::Script::Client::Command::Network::EndClientOrderEventReceiver | 80 |
| `0x0132` | map | clientbound | _0x132Packet | - | 72 |
| `0x0133` | map | serverbound | GroupWorkUpdatePacket | - | 72 |
| `0x0134` | map | clientbound | SetActorStatePacket | - | 40 |
| `0x0136` | map | clientbound | SetEventStatusPacket | Application::Lua::Script::Client::Command::Network::SetEventStatusReceiver | 72 |
| `0x0137` | map | clientbound | SetActorPropetyPacket | Application::Lua::Script::Client::Command::Network::SyncMemoryReceiver | 168 |
| `0x0139` | map | clientbound | CommandResultX01Packet | - | 88 |
| `0x013c` | map | clientbound | CommandResultX00Packet | - | 72 |
| `0x013d` | map | clientbound | SetActorNamePacket | Application::Lua::Script::Client::Command::Network::SetDisplayNameReceiver | 72 |
| `0x0144` | map | clientbound | SetActorSubStatePacket | Application::Lua::Script::Client::Command::System::ChangeActorSubStatModeBorderReceiver | 40 |
| `0x0145` | map | clientbound | SetActorIconPacket | Application::Lua::Script::Client::Command::Network::ChangeActorExtraStatReceiver | 40 |
| `0x0146` | map | clientbound | InventorySetBeginPacket | - | 40 |
| `0x0147` | map | clientbound | InventorySetEndPacket | - | 40 |
| `0x0149` | map | clientbound | InventoryListX08Packet | - | 936 |
| `0x014a` | map | clientbound | InventoryListX16Packet | - | 1824 |
| `0x014b` | map | clientbound | InventoryListX32Packet | - | 3616 |
| `0x014e` | map | clientbound | LinkedItemListX08Packet | - | 88 |
| `0x0157` | map | clientbound | _0x0157 | Application::Lua::Script::Client::Command::Network::SendLogReceiver | 48 |
| `0x016b` | map | clientbound | SetNoticeEventCondition | Application::Lua::Script::Client::Command::Network::SetNoticeEventConditionReceiver | 72 |
| `0x016d` | map | clientbound | InventoryBeginChangePacket | - | 40 |
| `0x016e` | map | clientbound | InventoryEndChangePacket | - | 40 |
| `0x016f` | map | clientbound | SetPushEventConditionWithCircle | Application::Lua::Script::Client::Command::Network::SetPushEventConditionWithCircleReceiver | 88 |
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
| `0x0193` | map | clientbound | _0x0193 | - | 40 |
| `0x0194` | map | clientbound | SetGrandCompanyPacket | Application::Lua::Script::Client::Command::Network::GrandCompanyReceiver | 40 |
| `0x0196` | map | clientbound | SetSpecialEventWorkPacket | - | 56 |
| `0x0197` | map | clientbound | SetCurrentMountChocoboPacket | Application::Lua::Script::Client::Command::System::ChocoboGradeReceiver | 40 |
| `0x0198` | map | clientbound | SetChocoboNamePacket | Application::Lua::Script::Client::Command::System::ChocoboReceiver | 64 |
| `0x0199` | map | clientbound | SetHasChocoboPacket | - | 40 |
| `0x019a` | map | clientbound | SetCompletedAchievementsPacket | - | 160 |
| `0x019b` | map | clientbound | SetLatestAchievementsPacket | - | 64 |
| `0x019c` | map | clientbound | SetAchievementPointsPacket | Application::Lua::Script::Client::Command::Network::AchievementPointReceiver | 40 |
| `0x019d` | map | clientbound | SetPlayerTitlePacket | Application::Lua::Script::Client::Command::Network::AchievementTitleReceiver | 40 |
| `0x01a4` | map | clientbound | SetCurrentJobPacket | Application::Lua::Script::Client::Command::Network::JobChangeReceiver | 40 |

## Verification

- Every opcode above comes from `derived/observations.json` joined with `derived/opcode_names.json` for the member pcaps. No opcode is added manually.
- Member sizes and sha256 were taken from this repo's `sources/pcap-1.23b/objects/`; the canonical hashes live in `sources/pcap-1.23b/manifest.yaml`.

## Gaps / caveats

- Opcode identity and framing only; decoded payload field semantics live in this repo's `derived/` (payload_layouts.json and friends).
