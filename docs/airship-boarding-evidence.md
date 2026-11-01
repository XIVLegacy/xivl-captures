# Airship purchase, boarding and waiting evidence

The retained retail captures contain four `PopulaceFlyingShip` NPC creations,
but no selected purchase or flight invocation. The client scripts establish
booking and voluntary-exit presentation. They do not establish the subsequent
server movement, boarding placement or waiting policy.

## Answers

These answers apply separately to Gridania, Limsa Lominsa and Ul'dah.

| Question | Supported answer | Evidence locator | Confidence | Exact unknowns |
| --- | --- | --- | --- | --- |
| After buying a ticket, did retail move the player or leave them at the attendant, and which packets followed? | The confirmed client menu branch says text-bank `7620` row `21`, finishes the talk turn and returns the saved destination choice. It contains no local warp. The retained NPC witnesses below have no joined purchase invocation. | [Attendant menu and callback operands][menu]; [retail witnesses](#retail-npc-witnesses) | High for the static menu return and captured creations; unresolved for purchase movement. | Warp versus same-zone movement versus remaining at the attendant; `SetMap`, `SetActorPosition` spawn type, including `10`, zone-in, and their order relative to attendant `EndEvent`. |
| If retail moved the player, where was each city's boarding or waiting point? | No authenticated passenger boarding placement is established for any city. Static landing names and capital zone pairs do not assign a boarding instance. | [Static names and placement limits](#static-names-and-placement-limits); [scene asset boundary][scene-assets] | Unresolved for world placement. | Each city's zone ID, private-area name and level, XYZ position and rotation. |
| What appeared between purchase and departure, and what happened on walking away or logout? | The menu method has no departure timer or boarding invitation. A separate voluntary-exit callback presents the text and results described below. A finite English text-bank search selected a denial template, with no invitation or countdown match. No retail waiting-state trigger is joined to these captures. | [Exit callback and selector 30010][exit]; [waiting text search](#waiting-text-search); [waits and connection failures][waits] | High for static text and returns; unresolved for runtime waiting and recovery. | Waiting-area presentation, timer text, invitation event and text ID, walk-away movement or ticket effects, and logout/reconnect behavior before departure. |

`PopulaceFlyingShip.eventOut(attendant, player, 30010)` says rows `23` and
`24`: defer travel and leave the landing area, with purchased tickets described
as nonrefundable and usable later. Other selector values say row `32`. Both
branches ask row `25` with two answers. Yes says row `28` and returns true;
other answers return nil. `30010` is a callback selector, not an authenticated
boarding event ID. The text does not prove ticket persistence, missed-departure
policy or logout recovery. The [canonical exit contract][exit] owns the exact
call operands and the `populaceFlyingShip.csv` source identity.

## Waiting text search

Searching English logical column `1` of all 2,321 numeric `worldMaster.csv`
rows with `airship|flying\s+ship|boarding|depart(?:ure|ing|s|ed)?` selected only
row `51146`. It describes an actor attempting to board a regular airship and
denies access to an `xtx/raidDungeon` lookup. This is a denial template, with
no authenticated producer or boarding-state meaning. No invitation or countdown
matched these selectors in this English bank; other banks, locales and computed
substitutions remain unsearched by this query.

The [canonical row finding][airship-text] is
`xivl-client-data:docs/message-operand-rows.md`, row `51146`.
The [table manifest][text-manifest] identifies `worldMaster.csv` by its
1,851,138-byte size and SHA-256
`2e2e2dd5cd9651388f6fa575b4229081ad0452165e78b725df0a5b5b7cf7c643`.

## Retail NPC witnesses

Evidence class: `packet-capture`, from the retail 1.23b corpus
[`pcap-1.23b`](../sources/pcap-1.23b/manifest.yaml). These four S2C `0x00CC`
records have fixed class `PopulaceFlyingShip` and initializer class path
`/Chara/Npc/Populace/PopulaceFlyingShip`.

Connection, frame and sub-event indices are zero-based decoder indices.
The packet column is the one-based capture packet completing the frame.
Actor keys are capture-local transport-source identities and are not reused
as identities across captures.

| Capture | Connection / direction | Frame / sub-event | Packet | Actor key | Actor-class ID | Internal instance name |
| --- | --- | --- | ---: | --- | ---: | --- |
| `move_out_of_room.pcapng` | main `0` / S2C | `46` / `14` | 104 | `0x44D80004` | 1500055 | `pplFlyingSh_fst0Twn01_03@09B00` |
| `move_out_of_room.pcapng` | main `0` / S2C | `47` / `7` | 105 | `0x44D80007` | 1500056 | `pplFlyingSh_fst0Twn01_06@09B00` |
| `moving_around_gridania.pcapng` | main `0` / S2C | `1264` / `7` | 3582 | `0x44D80007` | 1500056 | `pplFlyingSh_fst0Twn01_06@09B00` |
| `moving_around_gridania.pcapng` | main `0` / S2C | `1265` / `29` | 3585 | `0x44D80004` | 1500055 | `pplFlyingSh_fst0Twn01_03@09B00` |

The [source manifest](../sources/pcap-1.23b/manifest.yaml) pins the two witnesses:

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `move_out_of_room.pcapng` | 83,412 | `a7a03a1d688f3feb264f8da9fae3519c55b7e267aa3802472f0221f4d729b37b` |
| `moving_around_gridania.pcapng` | 855,000 | `bf6abf7ccc7a16e071846036477c1fadbc3b46385ef6e747b543d836f3f51017` |

Within the two witness captures, neither application u32 at `+0x00` or
`+0x04` in S2C `0x0130` or C2S `0x012D` matches a selected actor key on
the same connection. These are numeric, route-qualified comparisons.
NPC presence supplies no selected
booking, departure, landing-exit or passenger-placement witness. No NPC or
passenger coordinates are authenticated here.

## Finite capture coverage

All 54 manifest members matched their sizes and SHA-256 values and underwent
framing validation. The decoder admitted 84 connections. Their complete-frame
streams had zero unparsed admitted bytes, truncated sub-events, compressed-frame
inflation failures or compression-flag mismatches. Canonical stream selection
excluded 228 trailing reconstructed S2C bytes; those bytes were not searched.
The [decode and wire-order contract](pcap-decoding.md) owns connection admission
and the distinction between direction-local order and capture-wide chronology.

| Inspected field | Complete field count | Result |
| --- | ---: | --- |
| S2C `0x00CC` fixed class | 831 | Four `PopulaceFlyingShip` creations, listed above. |
| S2C `0x0130` event/function fields and 64-byte parameter spans | 200 each | 137 typed strings; no selected airship event, function or argument-string identifier. |
| C2S `0x012D` application `+0x04` | 126 | No same-connection selected-attendant actor-key match. |
| C2S `0x00CE` scene name | 2 | No selected city-airship scene identifier. |

Exact string selectors were `PopulaceFlyingShip`,
`/Chara/Npc/Populace/PopulaceFlyingShip`, `DftSrt`, `eventDeparture`,
`zep0g000`, `zep0g010`, `zep0l000`, `zep0l010`, `zep0u000` and `zep0u010`.
The fixed class supplied the four matches; no event/function/parameter-string
or scene field matched these airship identifiers. No numeric `7620` candidate
appeared in the decoded event arguments.
A numeric candidate alone would not authenticate a text-bank operand.

The general initializer inspection was incomplete: 13 unselected `0x00CC`
spans encountered tag `0x0C`, which the query did not admit. Thus only 818
general initializer spans were decoded, and no complete initializer or
actor-class-ID vocabulary is claimed. All four selected NPC initializer spans
decoded without an error. This limit does not reduce the complete fixed-class,
event-field or scene-field counts above.

These are finite field-query results, not proof that retail had no airship
booking or waiting policy. Computed names, other callers, unsearched bytes and
uncaptured historical behavior remain outside the observation.

## Reproduction

Use the manifest-pinned restricted members with the existing tools at
`xivl-captures` revision `9c22b89bfd89bfe8da5d151ea60e62b634e07c4f`:

- [`validate_framing.py`][framing-tool] for each explicit manifest member.
- [`extract_00da_00e1_comparison.py:_decode_capture`][decoder] for retained
  connections, direction-local frames, sub-events and transport actor fields.
- [Actor initialization layout and stream grammar][actor-layout] for selected
  `0x00CC` fields, controls and typed values.

For wrapped records, `sub_body` begins at the game-message header. Application
offsets below begin after its full 16 bytes, separately from the 16-byte
sub-event wrapper. Do not use a game-header preamble word as an actor key.

| Direction / opcode | Application-relative field |
| --- | --- |
| S2C `0x00CC` | Instance name `+0x04`, fixed class `+0x24`, each 32 bytes; tagged initializer `+0x44`, 192 bytes. |
| S2C `0x0130` | Owner u32 `+0x04`; event `+0x09` and function `+0x29`, each 32 bytes; typed arguments `+0x49`, 64 bytes. |
| C2S `0x012D` | Route-qualified u32 `+0x04`; compare selected actor keys only within the same capture and connection. |
| C2S `0x00CE` | Scene name `+0x04`, 32 bytes; preserve the separate selector at `+0x00`. |

For the selected-actor correlation in the two witness captures, compare both
application u32 values `+0x00` and `+0x04` of `0x0130` and `0x012D` against
the capture-local actor keys in the table.

The [incoming event contract][incoming-event], [outgoing event envelope][outgoing-event]
and [scene notice contract][scene-notice] own these respective field meanings.
The C2S `+0x04` comparison is numeric; its direct command fallback source is
a control binding reference, so it is not a universal NPC-owner field.
Preserve fixed-string termination, typed-value extents and connection identity.
Count exact matches before extracting any ordered neighborhood; never combine
independent connection blocks into one trip sequence.

## Static names and placement limits

The [client-data name crosswalk][names] has English `Airship Landing` keys
`1062`, `1078`, `2530` and `3519`, plus `Limsa Lominsa Landing`, `Gridania
Landing` and `Ul'dah Landing` at `1094`, `2531` and `3520`. None of these
seven keys joins a `placeNameId` in its 111 zone records. The [capital zone
pairs][zones] share city place-name keys; they do not assign public/private
status, a waiting zone or a layout variant.

No inspected promoted S2C `0x00CE` field model authenticates XYZ/rotation names
for the selected records. The [generated opcode header][position-header]
retains opaque byte fields, and its [consumer contract][header-contract]
limits semantic interpretation. Neither cinematic transforms nor UI map-marker
coordinates authenticate a world spawn. All three cities' passenger boarding
zone, private-area identity, level, XYZ and rotation remain unresolved.

[menu]: https://github.com/XIVLegacy/xivl-decomp/blob/c3a751809ecf052b770bc7d46da42ac27c10e9e5/docs/event/airship-scene-sequence.md#attendant-menu-and-callback-operands
[exit]: https://github.com/XIVLegacy/xivl-decomp/blob/c3a751809ecf052b770bc7d46da42ac27c10e9e5/docs/event/airship-scene-sequence.md#exit-callback-and-selector-30010
[waits]: https://github.com/XIVLegacy/xivl-decomp/blob/c3a751809ecf052b770bc7d46da42ac27c10e9e5/docs/event/airship-scene-sequence.md#waits-removal-and-connection-failures
[scene-assets]: https://github.com/XIVLegacy/xivl-decomp/blob/c3a751809ecf052b770bc7d46da42ac27c10e9e5/docs/event/airship-scene-sequence.md#scene-assets
[framing-tool]: https://github.com/XIVLegacy/xivl-captures/blob/9c22b89bfd89bfe8da5d151ea60e62b634e07c4f/tools/validate_framing.py
[decoder]: https://github.com/XIVLegacy/xivl-captures/blob/9c22b89bfd89bfe8da5d151ea60e62b634e07c4f/tools/extractors/extract_00da_00e1_comparison.py#L276-L350
[actor-layout]: https://github.com/XIVLegacy/xivl-decomp/blob/c3a751809ecf052b770bc7d46da42ac27c10e9e5/docs/actor/actor-instantiation-and-self-player.md#record-layout
[incoming-event]: https://github.com/XIVLegacy/xivl-decomp/blob/c3a751809ecf052b770bc7d46da42ac27c10e9e5/docs/event/start-event-fn-receiver.md
[outgoing-event]: https://github.com/XIVLegacy/xivl-client-structs/blob/b356634bd04a421769fe5fd73b336649963feff0/docs/player-command-wire-contract.md#dispatch-and-construction
[scene-notice]: https://github.com/XIVLegacy/xivl-decomp/blob/c3a751809ecf052b770bc7d46da42ac27c10e9e5/docs/net/ferry-scene-notice-producer.md#complete-copied-span-and-field-boundary
[names]: https://github.com/XIVLegacy/xivl-client-data/blob/a8e7075594d0209033aea51520e91cc1ccfc2d00/derived/autotranslate_name_crosswalk.json
[zones]: https://github.com/XIVLegacy/xivl-client-data/blob/a8e7075594d0209033aea51520e91cc1ccfc2d00/docs/zone-group-place-rows.md
[position-header]: https://github.com/XIVLegacy/xivl-opcodes/blob/8eef487105c53b7602597cd204db008693cc0b24/structs/map/clientbound.h#L384-L400
[header-contract]: https://github.com/XIVLegacy/xivl-opcodes/blob/8eef487105c53b7602597cd204db008693cc0b24/structs/README.md#consumer-contract
[text-manifest]: https://github.com/XIVLegacy/xivl-client-data/blob/a8e7075594d0209033aea51520e91cc1ccfc2d00/manifests/tables.json#L5891-L5897
[airship-text]: https://github.com/XIVLegacy/xivl-client-data/blob/7b4337b4efe873c0e3c865a8ea7646a80f75d9cd/docs/message-operand-rows.md
