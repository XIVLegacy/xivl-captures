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
