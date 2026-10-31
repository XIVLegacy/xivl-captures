# Selected class action behavior evidence

The client descriptions below establish authored effects in extraction
`2012.09.19.0001`. Numeric effect windows come from the retained final-1.x
eLeMeN tables, evidence class `web-tables`. They remain community values.
The packet observations establish the selected wire publications and result
messages. Confidence is high for those identified artifacts; applied
durations, universal consumption rules and resource formulas require their
own observed transaction.

`C` locators are physical lines in
`xivl-client-data:derived/command_battle_params.csv`; `W` locators are physical
lines in [battle-actions.csv](../studies/elemen-battle-actions/derived/battle-actions.csv).
Each row also supplies the command ID. Raw costs and cast values are client
getter inputs, before effective-cost or actor adjustments.

## Authored behavior and remaining limits

| Action | Client-authored behavior | Community window | Evidence | Unresolved behavior |
| --- | --- | --- | --- | --- |
| Rampart 27142 | Raises physical defense and generates high enmity. Enhanced Rampart 27163 adds nearby party coverage. | 60 s | C940, W9 | Mitigation/enmity amount, replacement and expiry cause. One wire interval is recorded below. |
| Aegis Boon 27141 | With a shield, blocks the next physical attack and recovers HP proportionally. The Japanese client text supplies the physical-attack qualification. Swift Aegis Boon 27164 reduces recast by 15 s. | 30 s | C939, W11 | Healing coefficient and damage basis, failed-trigger policy and universal consumption. Four selected brackets are recorded below. |
| Foresight 27181 | Raises parry rate and ends when an attack is parried. Swift Foresight 27201 reduces recast by 15 s. | 30 s | C970, W73 | Rate magnitude and a same-target parry/removal transaction. |
| Decoy 27222 | Consumes MP to evade one ranged or magic attack. Enhanced Decoy 27244 adds melee attacks. Raw MP input is 100. | 60 s | C1002, W139 | Effective debit, simultaneous/ineligible attacks and precise removal. |
| Featherfoot 27103 | Raises evasion, restores MP on evasion and ends on evasion or timeout. Enhanced Featherfoot 27123 increases restoration by 25%. | 30 s | C910, W41 | Base MP amount, rounding and an evasion/removal/resource transaction. |
| Howling Fist 27116 | Demolish 27115 is the combo prerequisite; increased damage is the bonus. Flank accuracy is a separate clause. Raw TP input is 3000, cast input 0. | No persistent action effect specified | C923, W53 | Combo window, success conditions, effective TP cost and damage bonus. |
| Dragon Kick 27118 | A twofold attack. Sucker Punch 27117 is the combo prerequisite; a chance to prevent weaponskills is the bonus. The prerequisite's flank MP recovery belongs to Sucker Punch. Raw TP input is 2000, cast input 0. | Lock duration unspecified | C925, W37 | Combo window/cost, lock chance, qualifying hit and lock expiry. |
| Protect 27351 | Protects party members around the target. Japanese base text specifies physical defense; Enhanced Protect 27365 adds magic defense. Raw cast/MP inputs are 3/80. | 300 s; the table also reports later Protect/Shell overwriting earlier effects | C1106, W173 | Applied duration, replacement/stacking, defense magnitude and effective MP debit. |
| Shroud of Saints 27341 | Temporarily halves enmity and restores MP gradually while active. | 20 s | C1096, W181 | Tick size/cadence/total, removal and the enmity operation when it ends. |
| Blissful Mind 27343 | Reduces HP immediately and accumulates MP over time. Reuse ends the effect and grants stored MP. Enhanced Blissful Mind 27362 increases accumulation speed. | Unspecified | C1098, W175 | HP basis/amount, storage rate/cap, enhanced multiplier, reuse payout and other removal outcomes. |
| Aerora 27354 | Wind damage to the target and nearby enemies, dispelling one effect per target. Aero is the combo action; its bonus raises accuracy and makes the attack single-target. Raw cast/MP inputs are 4/150; the community table labels cast time as 4 s. | No persistent damage effect specified | C1109, W182 | Measured cast time, effective MP debit, combo timing, damage and dispel selection/resistance. |
| Excruciate 27302 | Gradually raises spell critical rate and ends on landing a critical hit. Enhanced Excruciate 27321 raises its bonus. The wording does not say every completed spell consumes it. | 30 s | C1066, W213 | Qualifying critical type, multi-target consumption, rate ramp, enhanced amount and applied timeout. |
| Sanguine Rite 27307 | Restores MP proportionally to damage taken and prevents cast interruption while active. Enhanced Sanguine Rite 27324 adds damage reduction. Raw MP input is 120. | 20 s | C1071, W211 | Conversion coefficient, pre/post-mitigation basis, rounding/caps, damage categories and exact removal. |
| Dark Seal 27300 | Raises magic accuracy for the next cast. | 30 s | C1064, W207 | Accuracy amount and consumption on canceled, interrupted, resisted or non-damaging spells. |

The selected ability descriptions supply no combo prerequisite for Rampart,
Aegis Boon, Foresight, Decoy, Featherfoot, Protect, Shroud, Blissful Mind,
Excruciate, Sanguine Rite or Dark Seal. No combo rule is assigned to them here.
Howling Fist and Dragon Kick author no MP restoration. Neither a raw zero
cost nor the base `getCommandHPCost` result establishes an actual HP/MP
transaction. Blissful Mind explicitly authors HP reduction despite its
exported `hp_cost=0`.

Current and legacy identities remain distinct. Player Dragon Kick 27118 is
separate from monster command 23486. Legacy Sanguine Rite 28462/status
223117 describes HP sacrifice for magic potency; current 27307 describes
MP restoration and interruption protection. Same-name status rows, including
Protect 223129/223239, Decoy 223108/223238 and Sanguine Rite 223234/223240,
do not by themselves identify which command or trait applies each row.
`status_col_47` has no assigned duration units in the status export.

## Selected packet observations

The [battle-result study](../studies/battle-result-backfit/README.md#source-material)
retained 622 target rows from 53 generation inputs. Its 54-member source
manifest is a different scope. Exact command filtering finds two Rampart
rows, four Aegis activation rows and six Protect rows; the other selected
commands have zero matches in that product. These counts are target rows,
not numbers of uses or a complete coverage claim.

All selected matches belong to `party_battle_leve.pcapng`, main connection 0.
Locators below use zero-based frame/subevent/row indices in its reconstructed
s2c stream. `row_index` refers to
[battle-result-rows.csv](../studies/battle-result-backfit/derived/battle-result-rows.csv).

| Action | Retained rows and observation | Remaining limit |
| --- | --- | --- |
| Rampart | Rows 333/334, frame 2455/subevent 6, contain status-application text 30328. Same numeric actor slot byte 4 receives wire word 23064 at frame 2452/subevent 1 and zero at 2803/0. | The publication interval is about 59.07 s on the capture clock. It does not establish rendered duration, intended timer or expiry cause. |
| Aegis Boon | Activation rows 105/203/309/413 contain text 30328. Four separate incoming-attack results pair blocked-damage text 30306 with value 0 and Aegis HP-recovery text 33008 with values 136, 161, 148 and 144. | Reported recovery values are observed; HP before/after, prevented-damage basis and a healing coefficient are absent. |
| Protect | Rows 89/260 contain cast-start text 30128. Rows 90/91 and 262/263 contain status-application text 30328. | These rows do not prove an applied duration, replacement, defense formula or effective MP debit. |

### Aegis status and recovery brackets

For the four brackets below, the same numeric actor receives `0x0177` wire
word 23058, then zero in the same slot. The current native translation maps
23058 to status key 223058, whose client label is Aegis Boon. Zero is the
slot-clear sentinel. The translation and clear consumer belong to
`xivl-decomp:docs/actor/status-wire-translation.md`, sections `Translation`
and `Producers`. The status-name identity belongs to
`xivl-client-data:derived/status_names.csv`, row 223058.

| Slot byte | Set frame/subevent | Aegis command-result frame/subevent | Clear frame/subevent | Incoming result frame/subevent | Result rows | Reported HP recovery |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | 455/0 | 456/0 | 458/0 | 459/0 | 106/107 | 136 |
| 2 | 1519/0 | 1521/0 | 1549/1 | 1550/0 | 208/209 | 161 |
| 2 | 2357/0 | 2358/0 | 2373/0 | 2374/0 | 311/312 | 148 |
| 2 | 2928/0 | 2930/0 | 2939/1 | 2941/0 | 415/416 | 144 |

Each incoming result is `0x013A`: row 0 has text 30306 and row 1 has text
33008. The first two use attack command 23003, the last two 23005.
Set/clear completing packets are 652/658, 2693/2741, 3829/3846 and
4585/4599 respectively. Completing packets are one-based; they do not replace
the direction-local frame order. In all four brackets the zero publication
precedes the paired result messages. This is wire order, without a claim
about native queue execution, universal one-shot consumption or rendered
health/status updates.

The [recovery clusters](../studies/battle-result-backfit/derived/distribution-analysis.md#hp-recovery-clusters)
and [model observations](../studies/battle-result-backfit/derived/recovery-model-observations.csv)
own the four recovery values and their lack of stat controls. Those values
cannot supply a general damage-to-HP formula.

## Source identities and confidence

The packet source is evidence class `packet-capture`, member
`party_battle_leve.pcapng`, 1,429,864 bytes, SHA-256
`6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f`,
pinned by the [source manifest](../sources/pcap-1.23b/manifest.yaml).
Selected source decoding checked member identity, complete-frame parsing,
typed scalar widths and same-connection numeric actor/slot equality. The
slot brackets do not authenticate a rendered status lifetime or server
evaluation order.

The following product hashes fix the row locators used above:

| Product | SHA-256 |
| --- | --- |
| `xivl-client-data:derived/command_battle_params.csv` | `bc043bbd5558916a971de4d3a3a8dac5ec9d8ca36571bb534d0e964cd0b55d6a` |
| `xivl-client-data:derived/status_names.csv` | `bc15e20841a7d0ac13adb0760166795c13924b72fb821025b79d0e218ea86208` |
| `studies/elemen-battle-actions/derived/battle-actions.csv` | `e543ff7e2c1315d4764ac2110b06edb8e36ec876d7002d12f02b2697048bb26a` |
| `studies/battle-result-backfit/derived/battle-result-rows.csv` | `d67cb49d9489df127b3f374ee85792c43a6feffecbd4e2314072c0622b22e494` |

Client source identities and getter limits are in
`xivl-client-data:manifests/tables.json` and
`xivl-client-data:docs/command-battle-params.md`. Status export limits are in
`xivl-client-data:docs/status-names.md#columns-and-limits`.
Community provenance, source-page URLs and edition are owned by the
[eLeMeN study](../studies/elemen-battle-actions/README.md#source-note-edition)
and its [source manifest](../sources/elemen-battle-actions/manifest.yaml).
Community durations, descriptions and trait statements retain their original
evidence tier when compared with client text or packet observations.
