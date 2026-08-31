# Evidence map - SE forum White Mage enhancing magic

This study records Stoneskin, Protect, and Regen claims from post 1 of the
official FFXIV forum thread "White Mage: A Guide." The author is Sol_Aureus.
The post was published on 2012-04-05 and last edited on 2012-06-26 with the edit
reason `1.22c`.

Evidence class: web tables, wiki tier. Every row is CALIBRATION grade. The page
is a community guide hosted on the official forum, not an official Square Enix
mechanics statement or a retail capture.

## Source and locators

- Stable id: `se-forum-white-mage-41900`
- Source key: `se-forum-41900`
- Source manifest: `sources/se-forum-white-mage-41900/manifest.yaml`
- Selected excerpt: `sources/se-forum-white-mage-41900/objects/pages/thread-41900-post-1.md`
- Derived ledger: `studies/se-forum-white-mage-41900/derived/enhancing-magic.csv`
- Source locators: post 1, "Enhancing Magic Potency Returns" and "Specific
  Mechanics," under Stoneskin, Protect, and Regen

## Source observations

### Stoneskin

The author states that the available sample is too small to establish a trusted
formula. Only values at 396 through 449 Enhancing Magic Potency were personally
confirmed; values outside that range were projected. The stated trend is an
increase of one or two mitigation points per potency, usually two, with a
possible one-point increase every 25 potency levels. The author does not trust
that interval as a constant rule.

At 398 potency the guide prints a BRD and WHM comparison followed by `534 vs
780`. The display does not unambiguously bind each value to a job. This study
therefore preserves the printed order without assigning the values.

### Protect

The guide states that Enhancing Magic Potency affects Protect. It refines a
four-to-five point summary into a repeating defense input sequence of
`5-4-5-4-5-4-5-4-5`, with slight fluctuation. Because the sequence has odd
length, adjacent cycles create a `5-5` boundary. It also gives a repeating
`7-6-7` input sequence for one point of all elemental resistances.

### Regen

The guide names Enhancing Magic Potency as the only modifying input. Its base
step sequence is `1-2-2-1-2` repeated three times, followed by `1-2-1-2-2`
repeated three times. The source says AF Boots add up to 41 HP per tic, scale
with potency, and change the sequence to
`1-1-2-1-1-1-2-1-1-2-1-1-1-2-1-1-1-2`.

The stated level 50 cap is 203 HP per tic at 438 potency with AF Boots. A later
equipment list names Healer's Boots in the feet slot. That adjacency does not
independently prove that the source's AF Boots label means this item, so the
identity remains unresolved.

## Derived arithmetic

This section interprets the published step sequences. It is not a source
formula and does not upgrade the evidence grade.

- The Regen base cycle contains 30 HP increments over 48 potency steps. Its
  cycle average is `30 / 48 = 0.625` HP per tic per potency.
- The AF Boots cycle contains 18 HP increments over 23 potency steps. Its cycle
  average is exactly `18 / 23`.
- The ratio of those averages is exactly `144 / 115`, rounded to `1.25217`.
  This can explain recognizable `0.625` and `1.25` constants, but not an
  intercept, offset, rounding rule, or continuous equation.
- The Stoneskin display yields unassigned printed ratios of exactly `267 / 199`
  and `390 / 199`. The author explicitly declines to claim a trusted formula,
  so these are sample ratios only.
- Protect's defense sequence totals 41 input potency points for nine defense
  increases, an exact average of `41 / 9` input points per defense, rounded to
  `4.55556`.
- Protect's resistance sequence totals 20 input potency points for three
  resistance increases, an exact average of `20 / 3` input points per
  resistance, rounded to `6.66667`. Both Protect averages describe input
  required per output point, not output multiplied by potency.

## Limits and conflicts

- The source does not establish continuous formulas, intercepts, offsets, or
  exact rounding rules for any action.
- Stoneskin's two displayed values cannot be assigned to BRD and WHM with
  confidence, and the source rejects a trusted formula.
- The equipment claim is AF Boots. The source does not name another equipment
  slot in that enhancement claim or bind the label to an item identifier.
- The source discusses Protect. It does not identify a separate Protect II
  action or define variant-specific modifiers.
- The Protect averages run from input potency to one output point. Treating
  `4.56` or `6.67` as output multipliers reverses the stated relationship.
- The original charts were not transcribed, and no raw trial data accompanies
  the prose sequences.

## Verdict

The ledger is a faithful, narrow record of what the cited forum post claims.
It can support source comments and identify formula conflicts. It does not
justify exact server formulas or policy. Every claim remains wiki-tier
CALIBRATION evidence pending patch-scoped retail observations or decoded
formulas.

## Evidence gaps

- No raw trials, packet captures, or decoded formulas reproduce the values.
- Exact rounding, intercepts, and status storage semantics are unknown.
- AF Boots lacks an independent item-identity binding in this study.
- Protect II identity and behavior are not addressed.
- Stoneskin job-to-value assignment remains ambiguous.
