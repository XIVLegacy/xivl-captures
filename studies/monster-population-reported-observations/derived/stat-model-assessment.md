# Reported empirical stat model

## Evidence boundary

This is a separately assessed empirical model, not a retail measurement or
recovered retail formula. The supplied report describes extensive server
testing and a retail-directed approximation. No underlying retail stat
measurement series, video locators, fitting residuals, or independent
validation dataset accompanies that assertion. Server testing establishes
neither the retail formula nor its accuracy. The capture evidence policy
therefore admits no retail-formula citation from this material.

The restricted source preserves the model artifact, original authorship and
license, and exact byte identity. Its SHA-256 is
`12eec5c6b716f4fd228841383fa826a581783e42456e695037a874c34c066678`.
Locators 326-392, 628-658, and 674-786 cover the inspected model decisions.
No program body or calculated test vector is reproduced as observation data.

## Model as reported

Let L be the integer level clamped to at least one. The hard profile applies
to notorious monsters or private-area content other than Guildleve and Behest;
other cases select normal. This selection is part of the supplied model,
not a finding about retail content.

For each multiplier, the curve stays at its initial value through level 5,
uses `a + (1-a) * ((L-5)/7)^1.35` between levels 5 and 12, and reaches one
at level 12. Initial values are 0.65 for stats and 0.35 for HP. Disabling
the curve gives one. With S and H as those multipliers:

| Quantity | Normal | Hard |
|---|---|---|
| Primary stats | `(12 + 3.2*L)*S` | `(12 + 3.6*L)*S` |
| Attack | `(24 + 4.4*L)*S` | `(26 + 5.0*L)*S` |
| Accuracy and magic accuracy | `(18 + 4.2*L)*S` | `(18 + 4.8*L)*S` |
| Defense | `(16 + 4.0*L)*S` | `(18 + 4.6*L)*S` |
| Evasion and magic evasion | `(14 + 4.0*L)*S` | `(14 + 4.4*L)*S` |
| HP | `(50 + 45*L + 4.4*max(0,L-15)^1.35)*H` | `(50 + 45*L + 18.0*max(0,L-15)^1.35)*H` |
| MP | `max(1000, fallback_HP*0.75)` | `max(1000, fallback_HP*0.75)` |

Fallback replaces values at or below one, preserving greater values unless
forced. The early-return test checks HP, strength, vitality, dexterity,
intelligence, mind, piety, attack, accuracy, and MP. Defense, evasion, and
magic accuracy/evasion alone do not bypass that early return. Positive profile
HP/MP values are applied before fallback;
the supplied resource precedence prefers a nonzero profile resource to the
static placement's legacy 100 placeholder. These are model semantics only.
Downstream vitality/piety contributions and scaling must not be confused with
these base values or with measured MaxHP/MaxMP.

## Explicit values

[Profiles](profiles.csv) is separate from the placement observation CSV. Among
the 599 referenced profiles, 31 have positive HP overrides and 26 have positive
MP overrides; all 599 carry attack 40. Since 40 exceeds the placeholder
threshold, the ordinary non-forced fallback does not replace it. These counts
are source facts, not evidence of retail attack or resource values.

The restricted `NM guessed HP per level.md` explicitly distinguishes estimates
from historical claims and warns against representing guesses as recovered
values. Its own confidence labels are not adopted as evidence grades here.
Published profile values retain an unverified supplied-value verdict until
their individual underlying sources can be inspected.

The missing admissible input is an identified retail measurement series with
subject identity, level, observed resource/stat values, conditions, patch or
capture identity, and locators sufficient to reproduce a comparison. Until
then a consumer may cite this record only for the model's reported status and
source-value audit, never as proof of the retail formula.
