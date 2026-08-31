# Evidence map - SE forum Second Wind

This study records Second Wind calculation claims from post 4 of the official
FFXIV forum thread "2nd wind modifier." The author is Almalexia. The post was
published and last edited on 2012-08-08. It has no patch marker.

The forum page is a community calculation hosted on the official forum, not an
official Square Enix mechanics statement or a retail capture. Every source row
is wiki-tier CALIBRATION evidence with a `source-claim-only` verdict.

## Source and locators

- Stable id: `se-forum-second-wind-51208`
- Source key: `se-forum-51208`
- Source manifest: `sources/se-forum-second-wind-51208/manifest.yaml`
- Selected excerpt:
  `sources/se-forum-second-wind-51208/objects/pages/thread-51208-post-4.md`
- Derived ledger:
  `studies/se-forum-second-wind-51208/derived/second-wind-claims.csv`
- Source locator: post 4, Second Wind calculation

## Source claims

The post names class level as the primary modifier. Its worked example assigns
a base recovery of 580 HP to a level 50 Warrior. It states that Pugilist alone
receives one HP per two INT, describes a Pugilist Second Wind trait as a 25
percent increase, and adds an unspecified random integer. A separate level 50
Monk example reaches approximately 918 HP after the stated INT and trait steps.

These are player-authored calculation claims. The post does not publish raw
trials, a level series, the random range, the distribution, rounding order, or
an exact continuous equation.

## Related evidence by tier

### Tier 1 - retail packet observations

`battle-result-backfit:derived/battle-result-rows.csv` has seven self-targeted
command 27100 HP-recovery rows with exact values of 199, 201, 204, 206, 210,
215, and 241. The record identifies exact packet observations, not the action's
calculation inputs.

`battle-result-backfit:derived/distribution-analysis.md` states that these rows
do not carry level, INT, MND, VIT, healing potency, gear, or buff controls.
They therefore cannot confirm or refute the forum calculation terms.

### Tier 2 - retail video observation

`primal-battle-ifrit-bowl-of-embers:derived/evidence-map.md` records Second Wind
recoveries ranging from 145 to 265 in one uncontrolled run. This range overlaps
the packet observations, but the video does not establish the actor's inputs or
the random distribution.

### Tier 3 - web claims

`elemen-battle-actions:derived/battle-actions.csv` identifies command 27100 as
Second Wind, a level 6 Pugilist self-recovery action with a 45-second recast. It
also identifies Enhanced Second Wind as command 27120, a level 20 trait with a
claimed 25 percent recovery increase. Those rows are web-table CALIBRATION
evidence.

`bluegartr-stat-tests:derived/cure-potency.csv` records a patch 1.21 comparison
where Healer's Robe did not appear to affect Second Wind. The comparison is
confounded and does not determine the action's formula.

## Formula limits and conflicts

- A level 50 base value of 580 is one claimed anchor. It cannot establish a
  quadratic or any other level curve.
- The source describes an additional random integer. It does not support a
  multiplicative decimal roll. Its range, distribution, and operation order
  remain unknown.
- No cited evidence establishes a 9999 clamp or any other clamp.
- The forum post does not establish a numeric class id or trait id. The Elemen
  record independently owns the action and trait identities.
- The sources do not establish operation order or rounding behavior.
- Packet and video ranges cannot validate a formula without controlled actor
  state.

## Verdict

The ledger faithfully preserves the forum post's claims and the evidence map
places them beside stronger retail observations without merging their tiers.
Exact packet values are retail observations, but the calculation inputs are
absent. No level curve, INT rule, trait application order, random distribution,
clamp, or server policy is promoted as retail-confirmed behavior.

## Evidence gaps

- No patch-scoped controlled trial binds command 27100 recovery to known level,
  INT, trait, gear, and buff state.
- No multi-level series tests the level curve.
- No repeated controlled sample establishes the random term.
- Exact rounding and application order remain unknown.
