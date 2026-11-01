# Guildleve 12487 observed lifecycle

The retained `party_battle_leve.pcapng` observation binds Guildleve 12487 to
`PrivateGLBattleOrbNormal` and records activation, a content group, a Director
finish update, reward presentation and retirement. It does not identify the
actors or gameplay actions that produced objective progress.

| Question | Observation | Evidence locator | Confidence | Unknowns |
| --- | --- | --- | --- | --- |
| What initializes Guildleve 12487, and what establishes its objectives and outcome? | Actor `0x45100D44` carries the OrbNormal script path and numeric vector `20005,12487,6,0,0,0`. The selected lifecycle reaches a finish update, reward presentation and retirement. | [Director binding](../studies/regional-guildleve-publisher-contract/README.md#retail-client-director-binding-for-12487); [timeline](../studies/regional-guildleve-publisher-contract/derived/timeline.csv), `party_battle_leve.pcapng`, sequences 10-23 | Direct retained packet observations, with separately qualified static client consumers | Owned objective actors, authenticated collection or combat interactions, objective increments, wave transitions, failure rules and reward settlement |

## Source and order

The packet source is `pcap-1.23b`, evidence class `packet-capture`. Its
[source manifest](../sources/pcap-1.23b/manifest.yaml) pins
`party_battle_leve.pcapng` at 1,429,864 bytes, SHA-256
`6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f`.
The [study accounting](../studies/regional-guildleve-publisher-contract/derived/accounting.json),
`party_activation_comparison`, owns the retained activation/completion scope.

Every locator below belongs to the canonical 54992 main connection 0. Frame
and subevent indexes are zero-based within the indicated reconstructed TCP
direction. Completing capture packet numbers are one-based and identify the
earliest captured packet that completes an outer frame. Stream offsets belong
to that direction and cannot order the opposite direction. Capture completion
order associates records with capture packets; it does not establish server
causality. See the [decode and order contract](pcap-decoding.md).

The study retained 1,827 c2s and 3,516 s2c complete frames, zero admitted
unparsed stream bytes and six discarded trailing reconstructed s2c bytes.
These are retained decoding results.

## Selected lifecycle

The [timeline](../studies/regional-guildleve-publisher-contract/derived/timeline.csv)
contains 23 rows for this capture. Sequences 10-23 provide the selected
lifecycle below. The class-bearing packet 118 is separately retained in the
[Director-binding record](../studies/regional-guildleve-publisher-contract/README.md#retail-client-director-binding-for-12487);
it is not a row in that timeline.

| Completing packet | Direction / opcode | Frame / subevent | Stream offset | Observation |
| ---: | --- | --- | ---: | --- |
| 94 | s2c `0x0130` | 40 / 2 | 4319 | `eventGLStart`, owner `0x4510000C`, presents Guildleve 12487. |
| 110 | c2s `0x012E` | 42 / 2 | 7664 | One returned integer, 1. This does not prove that the response caused creation. |
| 118 | s2c `0x00CC` | 50 / 17 | 5608 | Actor `0x45100D44`, class `PrivateGLBattleOrbNormal`, path `/Director/Guildleve/PrivateGLBattleOrbNormal`, then five false controls and numeric vector `20005,12487,6,0,0,0`. |
| 156 | s2c `0x017C` | 78 / 0 | 9469 | Content group type 30001. |
| 156 | s2c `0x0183` | 78 / 2 | 9469 | Four member IDs: `0x45100D44`, `0x029B2941`, `0x029B27D3`, `0x45100D45`. |
| 5244 | s2c `0x0137` | 3374 / 0 | 418150 | Director finish properties from the same `0x45100D44` actor. |
| 5380 | c2s `0x012D` | 1763 / 1 | 296584 | `talkDefault` interaction, trigger `0x029B2941`, owner `0x45100D5B`. |
| 5384 | s2c `0x0130` | 3420 / 0 | 422974 | `eventGuildleveReward` presents Guildleve 12487. Presentation does not prove payout. |
| 5444 | s2c `0x0143` | 3448 / 2, 3 | 426046 | Group `0x2880000000000822` receives retirement controls 7 and 4. |
| 5444 | s2c `0x0131` | 3451 / 0 | 426300 | Event retirement with selector 5, distinct from group retirement. |

The class-bearing record starts at decoded-body offset 1304. Its application
SHA-256 is
`6d8094109a3c70cbf8252ef6dba9c457ccb67b112e189b6c6681c7055e933491`.
The binding record owns the complete tagged argument interpretation.

The timeline also retains the reward response, warp presentation and response,
then a final unanswered `talkDefault` interaction. None establishes publisher
hand-in, a granted reward or journal removal. Content-group membership does
not identify an owned objective-actor roster or assign combat roles to its
members. Event owners name the selected interaction endpoints, without
authenticating page collection or a kill callback.

## Client initializer and objective boundaries

The static chain is `PrivateGLBattleOrbNormal -> GuildleveBaseClass ->
DirectorBaseClass`. Conditional on the separately documented native vector
transfer and invocation, `DirectorBaseClass._onInit` stores 20005 as the client
Director ID and forwards the tail. `GuildleveBaseClass.init` stores Guildleve
12487, location 6 and extra-marker coordinates 0/0/0. OrbNormal's empty,
non-vararg `initAsGuildleve(self)` consumes no further values and returns zero
results. The script path and five controls precede the Lua numeric arguments.
The [initializer contract](https://github.com/XIVLegacy/xivl-client-scripts/blob/7d09b0f1dfffac8f488c1a24e2f031fbb4fb7757/docs/guildleve-initializer-arguments.md)
owns the operand proof and its vector-lifetime, branch/endian and completed
invocation limits. Neither 20005 nor location 6 acquires an additional server
or place meaning here.

The [OrbNormal objective contract](https://github.com/XIVLegacy/xivl-client-scripts/blob/7d09b0f1dfffac8f488c1a24e2f031fbb4fb7757/docs/local-regional-leve-contracts.md#objective-consumption-and-finish)
owns article slots 3 and 4 selecting `get` and `smash`, inherited four-slot
`aimNumNow`/`uiState` UI updates, and the signed `signal=-1` finish consumer.
The stored aim tuple `3,3,0,0` is recorded in the
[selected client rows](https://github.com/XIVLegacy/xivl-client-data/blob/68a74fe25eed9069615ab03a52dbac88f0bdd7d5/docs/guildleve-selected-row-values.md#guildleve-rows).
These are static consumers and fields. They do not authenticate actor
interactions, progress production, page or enemy selection, waves or failure
policy. A resolving observation would join the same Director, Guildleve and
objective slot to actor/class lifetimes and an attributable progress, failure
or wave transaction.

## Start observation and recipient limits

The selected start observation is main connection 0, s2c frames 40-90.
A separate source/member query follows only Director `0x45100D44` work,
group `0x2880000000000822`, and member `0x45100D45` through frame 122,
which contains the first positive start-time write. These bounds do not
identify the first objective actor or supply a complete encounter transcript.

| Question | Observed answer | Evidence | Confidence | Unknowns |
| --- | --- | --- | --- | --- |
| What followed the camp menu answer, and did a zone change occur? | The answer precedes Director setup, objective work, content-group synchronization, marker updates and positive startTime in capture-completion order. No SetMap, c2s ZoneInComplete or direct session record occurs in the separately specified interval through the retained finish. | [Start order](#bounded-server-order), [work and group fields](#start-work-and-group-fields), [map boundary](#map-and-session-boundary). | High for the selected packet fields and bounded negative. | First objective actor; exact music/content-command producer; universal private-area or zone policy. |
| Which battle NPCs belonged to the leve, who received them, and how were they cleaned up? | The selected content roster associates eleven keys with GuildleveSearchPoint and one with GuildleveBonusTreasureBox. Their creation, initial work and removal records reach `0x029B2941`; none is an authenticated enemy. | [Associated object roster](#associated-object-roster), [recipient boundary](#candidate-and-recipient-boundary). | High for class/group association and wire lifetimes; insufficient for objective production or recipient policy. | Battle-enemy roster and ID band, owner/party/outsider delivery, and causes of removal after end, abandon, failure, timeout or owner logout. |
| Did gathering or crafting leve targets use the same rules? | This battle-leve observation establishes no gathering-leve node or crafting-delivery NPC lifecycle. | [Local comparison](#gathering-and-local-crafting-boundary). | Insufficient for a shared policy. | Target spawn, visibility, Director binding and cleanup for those distinct content types. |
| What did outsiders, mid-leve joiners or reconnecting players receive? | The recording shows content-member snapshots delivered to one identified recipient. Membership additions alone do not identify when those actors joined the player party or which clients received resends. | [Group fields](#start-work-and-group-fields), [recipient boundary](#candidate-and-recipient-boundary). | High for the snapshots; insufficient for recipient and reconnect policy. | Outsider observations, mid-leve admission, zone-in/reconnect resends and paired observer delivery. |

### Bounded server order

The table preserves every one of the 178 s2c records in frames 40-90.
Opcode values are hexadecimal; each row lists them in subevent order starting
at index zero, without collapsing repetitions. This includes background
traffic and does not make every listed record a Guildleve operation.
The c2s answer is separately located at frame 42/subevent 2, completing
packet 110. Its frame index cannot be sorted against s2c frame indexes.

| s2c frame | Completing packet | Opcodes in subevent order |
| ---: | ---: | --- |
| 40 | 94 | 0x0144 0x0139 0x0130 |
| 41 | 94 | 0x0137 |
| 42 | 96 | 0x018D |
| 43 | 99 | 0x0001 |
| 44 | 101 | 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF |
| 45 | 103 | 0x00CF |
| 46 | 105 | 0x0001 |
| 47 | 109 | 0x0001 |
| 48 | 115 | 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF |
| 49 | 118 | 0x00DA 0x0168 0x0168 |
| 50 | 118 | 0x00CA 0x016B 0x016B 0x016B 0x00D0 0x00CE 0x00CF 0x013D 0x017C 0x017D 0x0183 0x017E 0x0134 0x0144 0x0179 0x0145 0x017B 0x00CC 0x0137 |
| 51 | 118 | 0x0137 0x0137 0x0137 |
| 52 | 118 | 0x0131 0x0137 |
| 53 | 121 | 0x0001 |
| 54 | 121 | 0x017A |
| 55 | 123 | 0x0144 0x00D0 0x00D0 0x00D0 0x00D0 0x00D0 0x00D0 0x013A |
| 56 | 123 | 0x00D2 0x00D3 |
| 57 | 123 | 0x0137 0x0137 0x0137 0x0137 |
| 58 | 125 | 0x017A |
| 59 | 127 | 0x0001 |
| 60 | 127 | 0x00CF |
| 61 | 127 | 0x00CF |
| 62 | 130 | 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF |
| 63 | 134 | 0x0001 |
| 64 | 134 | 0x018D |
| 65 | 134 | 0x0187 |
| 66 | 137 | 0x0177 |
| 67 | 137 | 0x0137 |
| 68 | 137 | 0x00D0 0x00D0 0x00D0 0x0139 |
| 69 | 140 | 0x0137 |
| 70 | 142 | 0x0001 |
| 71 | 142 | 0x00CB |
| 72 | 145 | 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF |
| 73 | 147 | 0x00D3 |
| 74 | 147 | 0x00CA 0x016B 0x00D0 0x00CE 0x00CF 0x00D6 0x013D 0x017C 0x017D 0x0183 0x017E 0x0134 0x0144 0x0179 0x0145 0x017B 0x00CC 0x0137 |
| 75 | 150 | 0x0001 |
| 76 | 152 | 0x017A |
| 77 | 154 | 0x00CB |
| 78 | 156 | 0x017C 0x017D 0x0183 0x017E |
| 79 | 156 | 0x0001 0x017C 0x017D 0x0183 0x017E |
| 80 | 171 | 0x017C 0x017D 0x0183 0x017E |
| 81 | 171 | 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF 0x00CF |
| 82 | 173 | 0x0137 0x0137 |
| 83 | 173 | 0x0001 |
| 84 | 173 | 0x017C 0x017D 0x0183 0x017E |
| 85 | 173 | 0x017C 0x017D 0x0183 0x017E |
| 86 | 175 | 0x017C 0x017D 0x0183 0x017E |
| 87 | 177 | 0x0137 |
| 88 | 179 | 0x0001 |
| 89 | 179 | 0x017C 0x017D 0x0183 0x017E 0x018D 0x017C 0x017D 0x0183 0x017E |
| 90 | 179 | 0x00CF |

The Director's frame 50 starts with AddActor at subevent 0; its previously
retained class binding is subevent 17, followed by `0x0137` at subevent 18.
The candidate Nuteater source's frame 74 starts with AddActor at subevent 0,
has `0x00CE` at subevent 3, its class binding at subevent 16 and `0x0137`
at subevent 17. A same-source RemoveActor follows at frame 77/subevent 0.
The bracket contains no `0x000C` SetMusic or additional `0x0130` call beyond
the retained eventGLStart presentation. This does not establish which music
was already playing or whether a content command used another producer.

### Start work and group fields

Property names below are exact hash resolutions in
[the pinned GAM catalog](https://github.com/XIVLegacy/xivl-client-structs/blob/b356634bd04a421769fe5fd73b336649963feff0/manifests/gam_hash_names.json).
Widths and values are observed leaves, not default values inferred for absent
slots. `0x0137` applications are 136 bytes, with the length byte at application
offset zero. The owning parser is
`tools/extractors/extract_property_stream_catalog.py:parse_records`.

| Source and frame/subevent | Observed fields |
| --- | --- |
| `0x45100D44`, 50/18; repeated at 57/3 | One-byte `aimNum[0]=3`, `aimNum[1]=3`, `aimNum[3]=2`; one-byte `uiState[0]=1`, `uiState[1]=1`, `uiState[3]=1`. |
| `0x029B2941`, 51/2 | Four-byte `charaWork.currentContentGroup=30001`; separate one-byte `work.guildleveChecked[0]=1`. |
| `0x45100D44`, 82/1 | Four-byte marker slot 0 components, interpreted as float32: X `0.271607727`, Y `5.00880146`, Z `-413.047607`. |
| `0x45100D44`, 87/0 | Marker slot 1: X `141.184448`, Y `16.7274189`, Z `-434.126892`; slot 2: X `60.3757324`, Y `16.375`, Z `-525.834412`. |
| `0x45100D44`, 122/0, packet 206, stream offset 16049 | Four-byte `startTime`, hash `0xD2C67973`, receives `1356929891`; application SHA-256 `59d17f4b1c6fcc3ecba6e45ddb9fb6c0f90a703c8c124ac5d71eb471a4836b94`. |

The startTime leaf has width tag at application `+1`, hash at `+2`, and
little-endian value at `+6`. Its declared stream length is 29 bytes.
The existing [UI consumer](https://github.com/XIVLegacy/xivl-client-scripts/blob/20ec80505035a492409b2677dff51aa439363487/docs/content-director-ui-contracts.md#guildleve-and-request-directors)
uses positive startTime for its local start presentation. This is not a
server timeout or success rule. The selected initial work does not write
aimNum slot 2 or aimNumNow; it does not establish those fields' prior values.
The runtime write to aimNum slot 3 is distinct from the selected static row's
stored aim tuple. Neither gives an authenticated enemy count.

At frame 50/subevent 8, `0x017C` carries group type 30001 and reference
`0x2880000000000822` at application `+0x18` and `+0x28`. Its following
`0x0183` lists the Director and players `0x029B2941` and `0x029B27D3`.
Frame 78 adds member `0x45100D45`; subsequent selected snapshots add
`0x45100D46` through `0x45100D50`. Frame 121 carries 15 members across
two `0x0183` records: the Director, those two players, and `0x45100D45`
through `0x45100D50`. The same-frame `0x017D`, `0x0183` and `0x017E`
records share their preceding header's 16-byte transaction prefix. That
prefix is separate from the group reference; no member-prefix word is
substituted for the group ID.

At frame 54/subevent 0, `0x017A` addresses that group and carries one
eight-byte property, unresolved hash `0x33D2BD7B`, numeric value
`0x45100D4400000000`, followed by target marker
`contentGroupWork/director`. Frame 58/subevent 0 repeats the property with
target `/_init`. The high 32 bits equal the observed Director source ID;
the property name and full member-reference encoding are not assigned here.
Group `0x2880000000000681` has a separate `/_init` record at 76/0 and is
not substituted for the Guildleve group. Group-work extents and typed
records follow the existing [group-work contract](../studies/group-combat-wire-contracts/README.md#group-work-0x017a).

The focused continuation inspects only the selected Director's property
records, the identified group's work/member transactions and exact member
`0x45100D45` lifecycle/initial work. It stops after the completed outer
frame 122 containing the positive startTime. No AddActor, class record,
RemoveActor or initial `0x0137` sourced by `0x45100D45` occurs between
frames 91 and 122. The separate exact-member query below follows the
concrete roster beyond that start-time endpoint. It does not expand the
Director work query or perform a generic class or wave census.

### Map and session boundary

The separate query selects only s2c SetMap `0x0005`, c2s ZoneInComplete
`0x0007`, and direct session subevents outside wrapped type `0x0003`.
There are zero matches on main connection 0 from s2c frame 40/subevent 0
through the finish at 3374/0, and from c2s frame 42/subevent 2 through
the last c2s frame completing no later than packet 5244. These are separate
directional intervals; packet completion associates their endpoints without
establishing causality. No intervening actor, objective or class census was
performed by this longer query.

This observation contains no selected SetMap or zone-in/session transition.
It does not establish universal private-area entry, server instance ownership
or zone policy. The PrivateGL class name and content-group kind do not supply
those missing meanings.

### Associated object roster

The 15-member snapshot at frame 121 supplies twelve nonplayer keys after
excluding the Director and two party players. Following only those exact
keys on main0 s2c frames 0-3448 joins eleven keys to
`/Chara/Npc/Object/GuildleveSearchPoint` and one to
`/Chara/Npc/Object/GuildleveBonusTreasureBox`. This is an observed
content-group object association. It does not identify battle enemies,
authenticate an objective increment, or prove that the Director created
each object.

The following table retains every selected AddActor, class binding and
RemoveActor locator, including repeated records. Each cell lists
frame/subevent pairs in that source's wire order. The class is unchanged
across the selected class records for each key.

| Member key | Client class | AddActor `0x00CA` | Class binding `0x00CC` | RemoveActor `0x00CB` |
| --- | --- | --- | --- | --- |
| `0x45100D45` | GuildleveBonusTreasureBox | 1018/0, 1449/0, 1763/0, 1957/15 | 1018/13, 1449/13, 1763/13, 1957/28 | 1134/0, 1650/0, 1799/0, 2141/0, 2141/1 |
| `0x45100D46` | GuildleveSearchPoint | 180/0 | 180/16 | 339/0, 339/1 |
| `0x45100D47` | GuildleveSearchPoint | 190/0, 997/0, 2033/26 | 190/16, 997/16, 2034/9 | 355/0, 1059/0, 2871/0 |
| `0x45100D48` | GuildleveSearchPoint | 953/0 | 953/16 | 1129/0, 1129/1 |
| `0x45100D49` | GuildleveSearchPoint | 206/0 | 206/16 | 377/0, 377/1 |
| `0x45100D4A` | GuildleveSearchPoint | 220/0, 1036/0, 2012/0 | 220/16, 1036/16, 2012/16 | 259/0, 1046/0, 2331/0, 2331/1 |
| `0x45100D4B` | GuildleveSearchPoint | 233/0 | 233/16 | 787/0, 787/1 |
| `0x45100D4C` | GuildleveSearchPoint | 1110/0 | 1110/16 | 1851/0, 1851/1 |
| `0x45100D4D` | GuildleveSearchPoint | 220/18 | 220/34 | 417/0, 417/1 |
| `0x45100D4E` | GuildleveSearchPoint | 2019/0 | 2019/16 | 2826/0, 2826/1 |
| `0x45100D4F` | GuildleveSearchPoint | 960/18, 1025/0 | 960/34, 1025/16 | 979/0, 1411/2, 1411/3 |
| `0x45100D50` | GuildleveSearchPoint | 220/36, 1004/18, 1998/0 | 221/10, 1004/34, 1998/16 | 259/1, 1092/0, 2284/0, 2284/1 |

The first delivered creation for these keys is `0x45100D46` AddActor at
180/0, packet 279, stream offset 24018. Its class binding is 180/16,
decoded-body offset 1352; the 264-byte application SHA-256 is
`a06f4d9c6a863a9f01c40f15bcc2162805ef8bf4d771ec8312b56e5079359955`.
The group already names these keys before their first selected AddActor;
group registration is therefore distinct from a delivered actor creation.
The last selected removal is `0x45100D47` at 2871/0, packet 4523,
stream offset 354239. All selected removals precede the retained Director
finish at 3374/0 and group retirement at 3448/2-3. Their timing alone
does not establish why the client stopped receiving an object or which
server cleanup rule applied.

The exact-key query retains 22 AddActor records, 22 class records and
33 RemoveActor records. Repeated removals are retained wire records, not
proof of repeated effective destruction. The first `0x0137` following each
of the 22 class records has one-byte `charaWork.property[0]=1` and
`charaWork.property[1]=1`. SearchPoint records additionally carry two-byte
`npcWork.pushCommand=10004` and one-byte `npcWork.pushCommandPriority=12`.
These fields do not provide an objective-progress or Director-reference
join. The bonus-box records have only the two selected property leaves.

A source/target membership predicate over the same main0 s2c interval's
338 complete `0x0139`-`0x013C` packets finds zero battle-result matches
for these twelve keys. The [battle-result parser](../tools/extractors/extract_battle_results.py)
and [pinned field model](https://github.com/XIVLegacy/xivl-client-structs/blob/b356634bd04a421769fe5fd73b336649963feff0/manifests/battle_result_field_semantics.json)
supply that predicate's record geometry. This bounded zero does not
identify the leve's actual enemies or rule out object interaction through
another event family. The enemy roster and kill-to-objective join remain
unresolved.

### Candidate and recipient boundary

At frame 74/subevent 16, packet 147, transport source `0x451006BF`
carries class `NuteaterStandard` and path
`/Chara/Npc/Monster/Lemming/NuteaterStandard`. Its application SHA-256 is
`8f5dcbf286b11b64e6afcc8cd73bf2a3109a8fddb8389a049144ba3bc9646a81`.
The fixed class begins at application `+0x24`; path tag `0x02` is at
`+0x44`, with NUL at `+0x70`. Its neighboring source-associated records
do not join this NPC to the Director or an objective increment. Its
creation/removal therefore supplies neither a leve-enemy roster nor a
leve-cleanup rule. No first objective endpoint is authenticated by this
selection.

All 178 selected start records, the focused start continuation and the
exact object-roster lifecycle/initial-work records have transport recipient
`0x029B2941`. Wrapper source and recipient
are retained separately; the game-header timestamp is not used as an actor
join. `0x00CE` records contribute source-associated numeric candidates only;
this page assigns no NPC XYZ, rotation or spawn-type meaning to them.
One recipient's recording cannot show that other clients were excluded or
that the same records reached every nearby client. The retained source
accounting identifies one main and one chat connection, not paired observer
recordings. Content membership does not establish which actors a nonmember
or returning participant could see.

The [party continuity contract](https://github.com/XIVLegacy/xivl-client-scripts/blob/20ec80505035a492409b2677dff51aa439363487/docs/guildleve-party-continuity.md#director-continuation-and-retirement)
records that generic client initialization can reconstruct a running leve's
presentation from current work. It does not prove that a reconnecting client
received those records. Director/group retirement remains distinct from
objective-actor cleanup, and no observed abandon, failure, timeout or logout
transaction is identified here.

### Gathering and local crafting boundary

The [local Guildleve dialogue study](../studies/local-guildleve-dialogue/README.md)
owns the separate processPgEvent and quest-120202 craft observations.
The [land-gathering sequence](land-gathering-observed-sequence.md) owns
Logging/Harvesting command and state observations. Neither binds this battle
leve's group members to gathering nodes or establishes delivery-NPC spawn,
visibility, Director linkage or cleanup. Those questions require an identified
target and recipient transaction for the relevant content type.

### Reproduction of the bounded fields

Verify the manifest member size and SHA-256 above, then validate framing with
`tools/validate_framing.py`. Decode with
`tools/extractors/extract_00da_00e1_comparison.py:_decode_capture` at revision
`0d59991d51ef3436f0c7a934f49090d7743ee86f`. Select main connection 0 and
the directional bounds stated above. Application offset zero follows the
16-byte subevent header, 8-byte inner header and 8-byte game preamble.
Use `parse_records` for the selected 136-byte `0x0137` applications and
`tools/extractors/extract_group_combat_contracts.py:parse_work` for the
144-byte `0x017A` applications; preserve declared extents and unresolved
hashes. The start-work continuation stops after outer frame 122. The separate
roster predicate uses only the twelve keys in frame 121's two member records
and excludes Director/player keys. Select their `0x00CA`, `0x00CB` and
`0x00CC` plus initial `0x0137` through frame 3448; parse their class streams
with the published model in
`xivl-decomp:tools/verify_actor_instantiation.py:parse_application` at
revision `c3a751809ecf052b770bc7d46da42ac27c10e9e5`. Admit battle-result
rows only when their application source or target equals one of those keys.
The longer map/session predicate does not authorize other field decoding.

The selected member reproduced zero admitted unparsed bytes, truncated
subevents, short wrapped inner headers, inflation failures and framing-flag
mismatches. Six reconstructed trailing s2c bytes remain outside complete
frames. Exact source/recipient, application-offset, truncated-extent and
typed-leaf length controls rejected substitutions. No live-client validation
or paired-observer delivery is claimed.
