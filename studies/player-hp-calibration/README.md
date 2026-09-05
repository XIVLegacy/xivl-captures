# Player HP Calibration Anchors

## Study contents

This study retains the 12 repeated same-frame correlations for four exact
property hashes when both wrapped `0x0137` header actor fields equal the known
sample player actor ID `43723073`. Two additional complete correlations occur
only once and remain outside this repeated-lead table. The retained observations
collapse to two leads with six occurrences each; they are not 12 independent
curve points.

## Start here

- `derived/evidence-map.md` - promoted correlation and claim boundaries.
- `derived/anchors.csv` - one row per complete same-frame occurrence with
  packet, subevent, and source-record locators.

Regenerate or verify the table:

```text
python tools/extractors/extract_player_hp_calibration.py
python tools/extractors/extract_player_hp_calibration.py --check
```

## Source material

The input is the deterministic record-level `0x0137` decode in
`studies/property-stream-hash-catalog/derived/property-records.csv`, derived
from the canonical retail 1.23b packet corpus.

## Promoted conclusions

The exact wire correlation has two six-occurrence clusters:

- `state_mainSkill[0]` 4, `state_mainSkillLevel` 26,
  `generalParameter[5]` 102, `hpMax[0]` 758.
- `state_mainSkill[0]` 3, `state_mainSkillLevel` 31,
  `generalParameter[5]` 110, `hpMax[0]` 1016.

## Topics

- Player HP calibration anchors
- Same-frame actor property correlation
- Repeated retail packet observations

## Evidence gaps

The packet evidence does not identify `generalParameter[5]` as Vitality, map
the main-skill values to classes, or prove that either wrapped header actor ID
is the property subject.

## Further research

Independent retail actors or externally established class and attribute
identities are required before treating these repeated leads as curve points
or attaching gameplay meanings beyond the exact field labels.
