# Stage 2 Distribution Analysis

## Boundary and method

This analysis treats `numeric_value` as a generic packet observation. A value
enters a damage, block, parry, miss, or HP-recovery distribution only after its
`world_master_text_id` assigns that exact message class. The source table has
622 rows; `distribution-summary.csv` retains every contributing `row_index` and
physical CSV line for each aggregate (`battle-result-rows.csv:2-623`,
`distribution-accounting.json:input`).

The command, scenario, source-actor, and target-actor tables use no inferred
actor identity. Their keys are the numeric packet values as captured. Complete
value counts and source-row inventories are in `distribution-summary.csv`.

## Outcome distributions

| Message class | Rows | Range | Distinct values | Duplicate excess | Source |
|---|---:|---:|---:|---:|---|
| Normal damage | 227 | 18-903 | 94 | 133 | `distribution-summary.csv:7` |
| Critical damage | 20 | 22-1535 | 18 | 2 | `distribution-summary.csv:3` |
| Block damage | 14 | 0-60 | 8 | 6 | `distribution-summary.csv:2` |
| Parry damage | 7 | 23-76 | 6 | 1 | `distribution-summary.csv:8` |
| Miss | 29 | 0 | 1 | 28 | `distribution-summary.csv:5` |
| HP recovery | 14 | 136-241 | 14 | 0 | `distribution-summary.csv:4` |

`duplicate_excess_count` is the number of observations beyond the first for
each repeated value. It is not a probability or a roll-frequency estimate.
All 29 miss rows carry value zero, while all 14 HP-recovery values are distinct;
the exact row identities are in the cited distribution rows.

The six selected outcome classes occur in three scenarios. The action-mechanic
scenario carries 13 normal, one critical, and two parry rows
(`distribution-summary.csv:10-14`). The battlecraft-leve scenario carries 170
normal, 12 critical, 14 block, two parry, 22 miss, and 13 HP-recovery rows
(`distribution-summary.csv:16-23`). The job-quest scenario carries 44 normal,
seven critical, three parry, seven miss, and one HP-recovery row
(`distribution-summary.csv:29-35`).

## Matched comparison sets

A matched set holds `scenario_id`, `command_id`, `source_actor_id`, and
`target_actor_id` constant. It then separates normal rows from one outcome
class. Effect fields remain uninterpreted and do not enter the key. A
one-to-one capacity is `min(normal_count, outcome_count)`. The Cartesian count
is every normal/outcome combination in the set and is not a temporal pairing.

| Comparison | Available outcome rows | Matched sets | Matched outcome rows | Unmatched outcome rows | One-to-one capacity | Cartesian candidates | Inventory |
|---|---:|---:|---:|---:|---:|---:|---|
| Critical vs normal | 20 | 9 | 14 | 6 | 12 | 51 | `matched-comparison-sets.csv:2-10` |
| Block vs normal | 14 | 8 | 14 | 0 | 12 | 34 | `matched-comparison-sets.csv:11-18` |
| Parry vs normal | 7 | 3 | 3 | 4 | 3 | 5 | `matched-comparison-sets.csv:19-21` |
| Miss vs normal | 29 | 19 | 21 | 8 | 21 | 72 | `matched-comparison-sets.csv:22-40` |

Every inventory row records the exact normal and outcome `row_index` lists and
their physical lines in `battle-result-rows.csv`. The match counts therefore
measure comparison capacity, not controlled trials. Unknown gear, buffs,
levels, positions, and encounter state remain uncontrolled.

## HP-recovery clusters

Recovery clusters hold scenario, command, source, target, and message identity
constant. Cure command 27346 contributes values 151 and 152 in one two-row
cluster and value 166 in a different-source singleton. This yields one
within-cluster row pair, but zero stat-controlled pairs
(`hp-recovery-clusters.csv:8-9`; `battle-result-rows.csv:176,178,398`).

Aegis Boon contributes four singleton clusters with values 136, 161, 148, and
144. It has zero repeated-context pairs. The four source rows and their distinct
source actors are preserved in `hp-recovery-clusters.csv:2-5` and
`battle-result-rows.csv:109,211,314,418`.

The remaining seven HP-recovery rows use command 27100 and form three clusters
(`hp-recovery-clusters.csv:6-7,10`). No recovery row carries MND, VIT, healing
potency, level, gear, or buff controls.

## Stage 3 entry conditions

- Critical potency and rate receive nine matched strata but no critical-rate,
  potency, level, or gear control.
- Block receives eight matched strata; four block rows have value zero and
  cannot support a positive magnitude ratio (`distribution-summary.csv:2`).
- Parry receives three matched strata and four unmatched parry rows.
- Cure has one repeated-context pair but zero stat-controlled pairs. Aegis has
  zero repeated-context pairs.
- DEF/VIT has zero matched stat-control pairs because none of the 622 source
  rows contains an actor-stat join (`battle-result-rows.csv:1-623`).

These are the complete Stage 2 comparison ceilings. Stage 3 may describe ratios
inside the matched strata, but it cannot promote a coefficient or convert the
Cartesian candidates into independent trials.
