# Garuda command observations

Great Whirlwind hit magnitude and mitigation, Slipstream applied stun timing,
and Thermal Tumult applied effect and duration remain unresolved. The static
client catalog establishes command identities and stored fields. It does not
supply the missing runtime observations.

The [Battle Result Backfit study](../studies/battle-result-backfit/README.md)
owns the retained packet evidence. Its
[result table](../studies/battle-result-backfit/derived/battle-result-rows.csv)
contains 622 target rows from 531 family packets and has SHA-256
`d67cb49d9489df127b3f374ee85792c43a6feffecbd4e2314072c0622b22e494`.
The [generation accounting](../studies/battle-result-backfit/derived/accounting.json)
names 53 capture inputs. Their hashes match the
[54-member source manifest](../sources/pcap-1.23b/manifest.yaml), with
`login.pcapng` excluded from that accounting. The observations below apply to
this retained product. They do not describe a fresh extraction of all source
members or establish historical absence.

## Command summary

Static row locators below refer to
[`xivl-client-data:derived/command_battle_params.csv`](https://github.com/XIVLegacy/xivl-client-data/blob/main/derived/command_battle_params.csv),
extraction `2012.09.19.0001`. Packet selectors refer to the retained result
table linked above.

| Subject | Observation | Exact locator | Confidence | Remaining limits |
| --- | --- | --- | --- | --- |
| Great Whirlwind | Static identity is command 23556, with `dmg_attr=13`, `dmg_elem=7` and `magnitude=0`. The retained result table has zero matching rows. | Static catalog `id=23556`; result table `command_id=23556`. | Verified static fields and finite table result; hit magnitude and mitigation unresolved. | An exact command-bound hit must be joined to the struck target's level, defense, gear and active mitigation. Static magnitude zero is neither an observed hit nor a damage coefficient. |
| Slipstream | Static identity is command 23539, with `cast_time=3`. The retained result table has zero matching rows. | Static catalog `id=23539`, `cast_time`; result table `command_id=23539`. | Verified static fields and finite table result; applied stun onset and duration unresolved. | Require the same hit's same-target status/control onset and removal, with timestamp resolution and log delay accounted for. Cast time and an interval between log messages do not establish applied stun duration. |
| Thermal Tumult | Static identity is command 23552, with `dmg_attr=-1`, `dmg_elem=-1`, `magnitude=0` and effect-block column 120 equal to zero. The retained result table has zero matching rows. | Static catalog `id=23552`, `effect_block_raw` entry `120=0`; result table `command_id=23552`. | Verified static fields and finite table result; applied effect and duration unresolved. | Require an independent command-to-status identity and same-target application/removal bracket. Neither Sleep nor an applied duration is established by these fields. Column 120 is not a status-duration field. |

## Field and timing limits

[`xivl-client-data:docs/command-battle-params.md`](https://github.com/XIVLegacy/xivl-client-data/blob/main/docs/command-battle-params.md)
owns the field meanings: section 2 maps cast time, section 5 describes the
effect block, and sections 5.1 and 6 separate stored command parameters from
status linkage and the magnitude-to-hit-point scale. The catalog's stored
values do not establish status application or observed damage.

A source-qualified hit needs its exact result-row or video/time locator and
target context. Applied duration needs onset and removal for the same target
and command instance. A guide claim also needs an attributable source and
revision at its actual evidence tier. Those observations remain unavailable
in the retained evidence cited here.
