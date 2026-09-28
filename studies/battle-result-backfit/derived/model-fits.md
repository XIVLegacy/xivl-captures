# Stage 3 Competing Model Fits

## Fit boundary

These fits use only the strict Stage 2 key: scenario, command, source actor,
and target actor. For each set, the reported ratio divides the arithmetic mean
of message-identified outcome values by the arithmetic mean of
message-identified normal values. It is a descriptive packet ratio, not a
temporal pair or fitted coefficient. Gear, buffs, level and dLVL, and scenario
mixing remain uncontrolled (`model-fit-accounting.json:81-86`).

`numeric_value` and both effect fields remain uninterpreted packet
observations. Exact `worldMaster` identity is the only reason a row enters a
normal, critical, block, parry, miss, or HP-recovery fit.

## Critical ratio and potency ordering

The corpus has 20 critical rows. Nine strict sets carry 14 critical rows and
27 normals; six critical rows have no strict normal comparison. The aggregate
ratio of the two contributing means is 1.485976, while the nine set-level
ratios span 1.047619-1.730475 (`model-fit-accounting.json:22-31`;
`matched-set-ratios.csv:2-10`).

The calibration record proposes a 115%-175% critical-bonus floor/cap and
contains mutually contradictory statements about whether Crit Potency is
applied before or after that boundary (`../../bluegartr-stat-tests/derived/critical-damage-bonus.csv:5-9`).
It also reports that 50 Crit Potency points changed critical damage by about 7%
at dLVL 0 and 6% at dLVL -5 (`../../bluegartr-stat-tests/derived/critical-damage-bonus.csv:12-13`).

Neither ordering can be evaluated here. None of the 41 matched observations
contains Crit Potency, level, dLVL, gear, or buff state, and the broad ratio
range extends below the claimed floor and approaches the claimed cap. The
result carries ratio shape only; it cannot identify the order of operations or
a critical-rate anchor. Unknown gear, buffs, and scenario mixing remain
uncontrolled for this fit.

## Block and parry reduction

All 14 block rows enter eight strict sets. Four block observations are zero and
are excluded from positive magnitude ratios. The remaining ten block rows and
16 normals produce an aggregate mean ratio of 0.658730 across seven usable
sets; set ratios span 0.515267-1.071429 (`model-fit-accounting.json:12-21`;
`matched-set-ratios.csv:11-18`).

The calibration record contains five block-reduction samples ranging from
15.2% to 72.7%, including a tester-flagged sampling reversal, followed by a
different 1.22 formula with a 20%-75% stated reduction range
(`../../bluegartr-stat-tests/derived/physical-damage-taken.csv:13-17,21`). The
packet sets contain no Block, VIT, level, dLVL, gear, or buff controls. Their
0.658730 descriptive ratio therefore does not fit or refute that formula;
scenario mixing is also uncontrolled.

Three of seven parry rows have strict normals. Those three parry rows and five
normals yield an aggregate mean ratio of 0.704100, with set ratios spanning
0.720000-1.178571 (`model-fit-accounting.json:70-79`;
`matched-set-ratios.csv:19-21`). Four parry rows are unmatched. No calibration
row supplies a competing parry formula, and the packet rows supply no parry
stat or level controls, so only the observed shape is retained. Unknown gear,
buffs, and scenario mixing remain uncontrolled for this fit.

For context, 21 of 29 miss rows share strict keys with 65 normal rows. Their
descriptive fraction inside those matched sets is 0.244186; it is not a
controlled accuracy denominator (`model-fit-accounting.json:64-69`;
`matched-comparison-sets.csv:22-40`).

## Cure and Aegis Boon

The SHA-recorded client-data row maps command 27346 to Cure and supplies base
magnitude 1000 (`model-fit-accounting.json:48-57`;
`xivl-client-data:derived/command_battle_params.csv:1101`). Client-data limits
that field to static magnitude identity; native scaling and final HP recovery
remain unresolved (`xivl-client-data:docs/command-battle-params.md:167-176,192-208`).
Three Cure rows
join the HP-recovery message: values 151, 166, and 152, or descriptive
observed/base ratios 0.151000, 0.166000, and 0.152000
(`recovery-model-observations.csv:3-4,7`). Values 151 and 152 share source,
target, command, scenario, and message identity; 166 has a different source
actor (`hp-recovery-clusters.csv:8-9`). None has MND, VIT, healing potency,
level, gear, or buff controls; scenario mixing also remains uncontrolled.

The competing calibration shapes are a speculative Cure III affine formula
from 1.19, per-stat Cure increments from 1.20a, and confounded no-AF versus AF
Cure samples from 1.21 (`../../bluegartr-stat-tests/derived/cure-potency.csv:2-5,7-15,16-17,22-23`).
The 151/152 repeated-context cluster establishes a one-point packet spread, not
a stat response. With zero stat-controlled pairs, none of those models can
produce a testable prediction from this corpus (`model-fit-accounting.json:32-40`).

Aegis Boon remains a separate localized identity. Its four singleton rows have
values 136, 161, 148, and 144 and four different source actors
(`recovery-model-observations.csv:2,5-6,8`). No Aegis base magnitude or stat
join is imported, and zero stat-controlled pairs exist
(`model-fit-accounting.json:2-10`). These rows cannot extend or contradict the
Cure shape.

## DEF/VIT curve

The calibration record proposes a DEF/VIT curve from measurements including
69 VIT, 99 DEF, and 214 DEF changes, plus the candidate expression using
`DEF + 0.67 * VIT` (`../../bluegartr-stat-tests/derived/physical-damage-taken.csv:2-8`).
The backfit has 622 rows, zero actor-stat joins, and zero stat-controlled pairs
(`model-fit-accounting.json:42-46`). Unknown gear, buffs, and scenario mixing
prevent even an indirect endpoint comparison. The DEF/VIT curve is therefore
not fit; this is an explicit evidence ceiling rather than a negative result.

## Stage 3 result

No fitted coefficient is promotable. The corpus carries descriptive critical,
block, parry, and miss shapes; three Cure recovery observations against one
static command magnitude; four separate Aegis observations; and zero DEF/VIT
or healing-stat controls. Stage 4 closed the contradiction verdicts from these
exact ceilings without selecting a number (`promotion-decision.md`).
