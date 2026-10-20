# Armoire Event Caller Census

The retained evidence binds retail `ObjectItemStorage` class-bearing
records, including class paths, instance names, and same-source observed
`0x013d` wire initializers. It does not bind an Armoire store or retrieve
caller, request, result, or state transition. The evidence ceiling is explicit
below so the class-bearing records are not mistaken for item-storage
transactions.

## Scope and method

The query started with the existing full-corpus products for the exact names
`ObjectItemStorage`, `storageMenu`, `selectCategory`, `selectStoreItem`,
and `selectReceiveItem`, plus the numeric and named 0x01a5 item-storage
opcode records. Only `return_to_inn.pcapng` had a concrete
`ObjectItemStorage` spawn row, and it was the first capture opened for typed
actor, display, and interaction context. The later 54-member pass was limited
to the metadata census described below; `login.pcapng` was then selected for
the second bounded direct-record context check.

The return-to-inn capture was decoded with the existing clear-game decoder
after framing validation. It has one admitted `main` lane, 50 c2s frames, and 63 s2c
frames. The decoder excluded its known six-byte s2c reconstructed-tail
remainder. Direction-local wire order was used throughout; no c2s/s2c
cross-direction order or causality is inferred. The framing check had zero
stream trailing bytes and zero flag mismatches.
All frame, subevent, and direction-local event indices in this study are
zero-based.

## Bound actor record

The existing spawn product has one matching row in
`return_to_inn.pcapng`. This is a bounded product query, not a complete
actor census:

| Field | Value |
| --- | --- |
| Spawn-product actor field | `0x50e0ede1` |
| s2c 0x00cc locator | frame 51, subevent 7, direction-local event index 270; wire wrapped index 268 |
| Transport | source `0x47a0000f`, target `0x029b2941`; subpacket size 296 |
| Instance name | `objItemStor_prv0Inn01_0e@0F400` |
| Base class | `ObjectItemStorage` |
| Class path | `/Chara/Npc/Object/ObjectItemStorage` |
| Associated literal | `TEST` in the 0x00cc string area; retained as a literal slot, not interpreted as a semantic name |

The spawn product names the preamble field above `actorId`, but it is read
from `sub_body[8:12]` and is shared by distinct s2c `0x012e` records:
frame 49/subevent 28 from source `0x47a00007`, frame 50/subevent 2 from
`0x47a0000c`, frame 50/subevent 17 from `0x47a00006`, and frame
50/subevent 32 from `0x47a0000f`. It is retained here only as the existing
product field, not as a unique actor key.

The direct same-source records supporting the return-to-inn actor presence are
s2c `0x00ca` add at frame 50/subevent 31, direction-local event index 257,
and s2c `0x00ce` position at frame 50/subevent 35, direction-local event
index 261. The direct class-bearing s2c `0x00cc` record at frame
51/subevent 7, direction-local event index 270, and the observed s2c
`0x013d` wire initializer at frame 51/subevent 1, direction-local event
index 264, share transport source `0x47a0000f`. The `0x013d` record is
reported as an observed wire initializer only; it is not proof that a
semantic name was applied. The original-record locators and direct transport
source are the binding evidence. The per-actor rebuild section of
`xivl-client-structs:docs/client-architecture.md` explains why this
`0x013d` record is not used as an applied-name join.
The direct `0x00ca` add and `0x00ce` position records provide the presence
support used here; the derived spawn booleans are not used as proof.
Using the proposed 0x013d layout in
`xivl-client-structs:manifests/inbound_proposed_field_layouts.json`, the
record has application length 40, display-name ID `0x003d3023`, an empty
custom-name field, raw consumed byte at application offset +36 equal to
`0`, and a three-byte zero tail. The meaning of that consumed byte remains
unresolved.
This is an observed wire initializer; it does not resolve the ID to text or
prove application of the name. The 0x00cc actor record remains the
class-bearing initialization record, consistent with the named sections
`The per-actor rebuild transaction: s2c 0x00CA opens, only 0x00CC closes it`
and `Zone actor binding and Lua class readiness` in
`xivl-client-structs:docs/client-architecture.md`.

## Existing product query

The exact-name query produced these bounded results:

| Product | Coverage and result |
| --- | --- |
| `derived/spawn_observations.json` | 54-capture walk, 497 positioned rows across 18 captures; exactly one matching `ObjectItemStorage` row in this product, with the shared preamble caveat above |
| `derived/observations.json` | 54 retained capture members; aggregate count of 200 s2c `0x0130` packets only, with no function names; no s2c numeric key `0x01a5` |
| `studies/director-wire-identity` | 54 captures and 126 c2s `0x012d` EventStart role/event-name rows; the five exact storage names were absent from these retained role rows |
| `studies/c2s-012d-event-start` | 126 c2s `0x012d` messages in 39 captures; none of the five exact storage names occur in the product |
| Opcode metadata | `0x01a5` is named `SetPlayerItemStoragePacket` with class `EntrustItemReceiver`, but its existing capture metadata has `observedIn: []` and `payloadLengths: []` |

The `ObjectItemStorage actor boundary` section of
`xivl-client-scripts:docs/item-storage-widget-contracts.md` confirms the
actor boundary and the UI methods `storageMenu`, `selectCategory`,
`selectStoreItem`, and `selectReceiveItem`. It describes the Ask/widget
results and the `_getCatalogID`, `_countStoredItem`, and
`_getStoredItem` UI enumeration paths. The `Native callback result and
EventUpdate` section of
`xivl-client-scripts:docs/passivegl-dialogue-producer.md` links conditional
callback completion to generic c2s `0x012e` result serialization. That is
not a storage-specific caller or result, and neither document identifies one.

## Focused 54-member name census

A focused pass ran the canonical decoder over all 54 source
manifest members. It authenticated every member's manifest SHA-256 and size,
and the existing framing validator reported zero compression flag mismatches
for every admitted direction. The pass counted 200 s2c `0x0130` packets,
matching the existing aggregate count. For each `0x0130`, it read the fixed
function-name slot `application[0x29:0x49]` as null-terminated ASCII before
parameter decoding, with `application = sub_body[16:]`. It also scanned the
full admitted decoded `sub_body` for exact UTF-8/ASCII byte strings. No requested storage method name
matched: `storageMenu`, `selectCategory`, `selectStoreItem`, and
`selectReceiveItem` each had zero matches. `ObjectItemStorage` had four
byte matches, all in two s2c `0x00cc` records; each record had two class
occurrences and one class-path occurrence:

| Capture | Locator | Direct transport |
| --- | --- | --- |
| `login.pcapng` | frame 20, subevent 10, direction-local event index 194, lane `main`/0 | source `0x47a0000f`, target `0x029b2941` |
| `return_to_inn.pcapng` | frame 51, subevent 7, direction-local event index 270, lane `main`/0 | source `0x47a0000f`, target `0x029b2941` |

The `login.pcapng` row was selected for the second bounded direct-record
context check. Its direct same-source records are:

| Opcode | Locator | Direct fields |
| --- | --- | --- |
| s2c `0x00ca` | frame 19, subevent 38, direction-local event index 181 | add record; preamble word `0x50e0e838` |
| s2c `0x00ce` | frame 20, subevent 1, direction-local event index 185 | position record; preamble word `0x50e0e838` |
| s2c `0x013d` | frame 20, subevent 4, direction-local event index 188 | display ID `0x003d3023`, custom name empty, raw consumed byte +36 = `0`, zero tail |
| s2c `0x00cc` | frame 20, subevent 10, direction-local event index 194 | instance `objItemStor_prv0Inn01_0e@0F400`, class `ObjectItemStorage`, path `/Chara/Npc/Object/ObjectItemStorage`, literal `TEST`; preamble word `0x50e0e838` |

The login `0x013d` row is an observed wire initializer only, not proof that
a semantic name was applied. Login has no `0x012d` or `0x0130` records.
Its four `0x012e` records are s2c 40-byte records, including one from
direct source `0x47a0000f` at frame 19/subevent 39, direction-local event
index 182. The c2s EventUpdate layout does not apply to those s2c records,
so they provide no store/retrieve request or typed callback result. The
return-to-inn row is the direct record already described above. The scan made
no cross-direction causality claim and performed no additional
parameter-field decoding.

### Per-member counts

The authored table below keeps one row for every source-manifest member. The
four callback columns count exact byte-string matches in any admitted decoded
event payload; the ObjectItemStorage column counts matching s2c 0x00cc records.

| Capture | s2c 0x0130 | ObjectItemStorage s2c 0x00cc records | storageMenu | selectCategory | selectStoreItem | selectReceiveItem |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `accept_leve.pcapng` | 10 | 0 | 0 | 0 | 0 | 0 |
| `accept_local_leve.pcapng` | 9 | 0 | 0 | 0 | 0 | 0 |
| `accept_quest.pcapng` | 2 | 0 | 0 | 0 | 0 | 0 |
| `action_and_traits.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `add_str.pcapng` | 1 | 0 | 0 | 0 | 0 | 0 |
| `attributes.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `battle_mode_passive_mode.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `buy_square_maple_shield.pcapng` | 8 | 0 | 0 | 0 | 0 | 0 |
| `change_bodyarmor.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `change_helm.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `change_to_botanist.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `chat_say.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `chat_shout.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `check_room_map.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `checkbed.pcapng` | 1 | 0 | 0 | 0 | 0 | 0 |
| `coerthas_map.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `combat_autoattack.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `combat_skills.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `cutscene_book.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `emote_dance.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `emote_kneel.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `friendlist_search.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `from_gridania_to_blackshroud.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `gather_wood.pcapng` | 43 | 0 | 0 | 0 | 0 | 0 |
| `gear_changesoul.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `gear_changeweapon.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `gridania_map.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `gridania_to_coerthas.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `harvest.pcapng` | 4 | 0 | 0 | 0 | 0 | 0 |
| `idle_in_party.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `idling.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `inventory.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `invite_join_party.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `local_leve_complete.pcapng` | 71 | 0 | 0 | 0 | 0 | 0 |
| `login.pcapng` | 0 | 1 | 0 | 0 | 0 | 0 |
| `mount_unmount_chocobo.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `move_around_gridania.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `move_out_of_room.pcapng` | 1 | 0 | 0 | 0 | 0 | 0 |
| `moving_around_gridania.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `open_gear_menu.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `party_battle_leve.pcapng` | 7 | 0 | 0 | 0 | 0 | 0 |
| `quest_journal.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `quest_update.pcapng` | 2 | 0 | 0 | 0 | 0 | 0 |
| `repair_items.pcapng` | 13 | 0 | 0 | 0 | 0 | 0 |
| `return_to_inn.pcapng` | 1 | 1 | 0 | 0 | 0 | 0 |
| `sell_item.pcapng` | 10 | 0 | 0 | 0 | 0 | 0 |
| `small_talk_louisoix.pcapng` | 2 | 0 | 0 | 0 | 0 | 0 |
| `switch_to_weaver.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `teleport_to_camp_nine_ivies.pcapng` | 5 | 0 | 0 | 0 | 0 | 0 |
| `teleport_to_camp_tranquil.pcapng` | 3 | 0 | 0 | 0 | 0 | 0 |
| `teleport_to_gridania.pcapng` | 3 | 0 | 0 | 0 | 0 | 0 |
| `war_quest_update1.pcapng` | 1 | 0 | 0 | 0 | 0 | 0 |
| `war_quest_update2.pcapng` | 0 | 0 | 0 | 0 | 0 | 0 |
| `war_quest_update3.pcapng` | 3 | 0 | 0 | 0 | 0 | 0 |

The source manifest pin for this pass is
`sources/pcap-1.23b/manifest.yaml`, SHA-256
`baaa15f99f7f5d865bf2ec0dbcc1e454d034382b0559edccb0085c57c4061cf5`.
The reproducibility pins for this pass are decoder
`tools/extractors/extract_00da_00e1_comparison.py`, SHA-256
`c48f1224ca62d7c0ca6ca876751caaeff243e9b7f7af1507dfabbeab1f89fdc4`,
source revision `526954241b592aefec1d57f3697796114466753c`; stream decoder
`tools/extractors/extract_streams.py`, SHA-256
`bc7450d0ba80a7410ce6a407f0efcd429facf2e4384b4f40a294d4e9b209d0e5`; and
framing validator `tools/validate_framing.py`, SHA-256
`f5172a1d25ebb179362d9c8849c774c2087169273f41eb7603aab6f919725302`.
The per-member table above is the authored public count artifact. Raw payloads
and function-body dumps are excluded from public products.

## Return-to-inn event context

The selected capture contains one c2s `0x012d` and one s2c `0x0130`, and
neither contains direct source `0x47a0000f`:

| Direction and opcode | Locator and typed context |
| --- | --- |
| c2s `0x012d` | frame 8, subevent 1, direction-local event index 20; trigger actor `0x029b2941`, owner `0xa0f05e9c`, server codes `0x33800000`, selector `0`, event name `commandContent` |
| s2c `0x0130` | frame 6, subevent 1, direction-local event index 13; source/target `0x029b2941`, owner `0xa0f05e9c`, function `delegateCommand`, delegate prefix `eventConfirm`; generic parameter decoding stops at unsupported tag 3 at offset 19 |

The already-decoded capture also has one c2s `0x012e` EventUpdate at frame
19, subevent 1, direction-local event index 47. Its source and target are
both player actor `0x029b2941`, and its application length is 88. The
application fields are event actor `0x029b2941`, unresolved context dword
`0x33800000`, signed byte `0`, CRC32 `0x1005bd49`, event type byte
`0`, and a 64-byte parameter block followed by the documented seven-byte
unwritten tail. Direct source `0x47a0000f` is absent from this request.
The field boundary and tail treatment come from the `C2S EventUpdate fields
and talk-request boundary` document in
`xivl-client-structs:structs/network/event-update.md` and the
`Native callback result and EventUpdate` section in
`xivl-client-scripts:docs/passivegl-dialogue-producer.md`.

The c2s `0x012e` record is consistent with the generic EventUpdate layout,
but it does not identify its producing callback or bind the route to the
Armoire actor or an item-storage method. The 0x0130, 0x012d, and 0x012e
observations are reported with direction-local locators; they are not joined
across directions as a causal sequence.

## Evidence ceiling

The searched `studies/director-wire-identity` and
`studies/c2s-012d-event-start` products do not supply a typed
CreateActor/0x00cc inventory joined to the full 0x0130 or 0x012d payloads.
The existing `derived/observations.json` numeric product had no s2c
0x01a5 key. The current evidence therefore does not establish any of the
following for the direct source `0x47a0000f` class-bearing records:

- a caller for `selectStoreItem` or `selectReceiveItem`;
- a c2s request carrying a store or retrieve choice;
- an s2c inventory, acknowledgement, or failure result;
- a state transition caused by storing or retrieving an item.

The bounded non-observation excludes only the admitted clear-game lanes and
the retained products named above. An unretained session, another packet
opcode, or a server-side path not represented in these captures remains
possible. A concrete binding would require a capture with the actor-targeted
request and its matching typed result, plus a retained caller/result product
that preserves those joins.

## Source and product pins

- Corpus manifest `sources/pcap-1.23b/manifest.yaml`: content SHA-256
  `3e39bfbffdf5a7efa0f42fc221f42dc2d1d28af8f19378d28921a3b903c0c7ee`.
- `sources/pcap-1.23b/objects/return_to_inn.pcapng`: SHA-256
  `9a81e483d3dd2673081afef06ed521c190c4d42be16e95e24097f25ff81f58c1`.
- `derived/observations.json`: SHA-256
  `d545668f3f4b7abbab220dc2e73345ea5080571957dca8f7c2f2f28f805b8f30`;
  `derived/observations.meta.yaml`: SHA-256
  `2534bc940f04ecdaa5af8555f8433f5db95786e5bdbe0fc8bcea3053e40715a0`.
- `derived/spawn_observations.json`: SHA-256
  `69f7a21ef4b7bd0c48cafc1c7db68884b9273bfa3fd03043303633106e940581`;
  `derived/spawn_observations.csv`: SHA-256
  `d4f68b277795a828d9373a03a81421af9940c8524517775593fa2581058eab93`.
- `derived/opcode_names.json`: SHA-256
  `529ee24970932ca62cc4504432252d671b2c6a63f29b1e52ecd2bf0f900e0ff6`.
- `studies/director-wire-identity/derived/accounting.json`: SHA-256
  `a358e8ff87cb0df479ae6e84987725c51b6d40445639c4de22ab6f5706118f77`;
  `event-role-candidates.csv`: SHA-256
  `3cc5f6aecf452418e24cc9e024e2f949b94501085e2f6f79c0377a42c23e0b7f`.
- `studies/c2s-012d-event-start/derived/accounting.json`: SHA-256
  `124a6bb7dd9b5e9c764401802eca3f40de50a4e11c28f6905646f8bc271263f6`;
  `derived/verdicts.md`: SHA-256
  `d8fcfcee7b7c39d97064dc4181bcd6ff1b7f5f4e85608716d69e5a0af95d32a9`.

The capture decoder and wire-order boundaries are documented in
`xivl-captures:docs/pcap-decoding.md`. This study does not publish raw
packet payloads, private strings, or a generated full-corpus refresh.
