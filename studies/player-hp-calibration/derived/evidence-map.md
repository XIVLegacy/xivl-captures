# Player HP calibration evidence map

## Evidence selection

The reducer reads the canonical record-level `0x0137` table at
`studies/property-stream-hash-catalog/derived/property-records.csv`. It keeps
records whose wrapped source and destination header fields both equal
`43723073`, then requires one occurrence of each target hash in the same
capture, reconstructed lane, and outer frame.

The four exact wire labels are:

| Field label | Property hash | Wire width |
|---|---:|---:|
| `state_mainSkill[0]` | `0x7532ce24` | 1 byte |
| `state_mainSkillLevel` | `0x96063588` | 2 bytes |
| `generalParameter[5]` | `0x416571ac` | 2 bytes |
| `hpMax[0]` | `0x7bcdfb69` | 2 bytes |

`derived/anchors.csv` preserves the capture, lane, frame, packet, subevent,
and canonical source-record locators for every admitted group.

## Promoted correlation

| Repeated lead | Occurrences | `state_mainSkill[0]` | `state_mainSkillLevel` | `generalParameter[5]` | `hpMax[0]` |
|---|---:|---:|---:|---:|---:|
| lead-1 | 6 | 4 | 26 | 102 | 758 |
| lead-2 | 6 | 3 | 31 | 110 | 1016 |

These are two repeated leads, not 12 curve points. Repetition establishes that
the two exact tuples recur in the retained corpus; it does not add independent
attribute or level variation.

## Claim boundary

The wrapped source and destination actor IDs are packet-header selection
fields. Even though both equal the known sample player actor ID in all 12
groups, this study does not rename either field as the property subject.

`generalParameter[5]` is not identified as Vitality. Values 4 and 3 are not
mapped to classes. The table does not promote an HP formula, coefficient,
interpolation, or extrapolation.

## Evidence gaps

Separate evidence is required to identify the property subject, attach
gameplay semantics to `generalParameter[5]`, map main-skill values to classes,
or establish enough independent points for an HP curve.
