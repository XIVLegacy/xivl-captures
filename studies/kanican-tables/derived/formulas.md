# kanican FFXIV 1.x combat formulas and conclusions

Derived formulas, ratios, and stated conclusions transcribed verbatim from
kanican's (Kaeko Leta's) FFXIV 1.x theorycrafting posts. Formula text and worked
examples are the author's own words, unaltered. The supporting per-trial data is
in the sibling CSVs and the preserved images under `sources/kanican-tables/objects/images/`.

## Version and evidence tier - read first

- These are **community testing results, wiki tier** (packet captures > video
  breakdown > wiki). A value here justifies a CALIBRATION-tagged server value,
  not a retail-confirmed one.
- The data spans **FFXIV patches 1.18 through 1.20/1.21** (Aug 2011 - Mar 2012).
  The repo targets **1.23b** (the final 1.x patch, Nov 2012). The author states
  that patch **1.20 "fundamentally changed essentially every skill and formula"**
  and that he believed "the core mechanics ... have been implemented already with
  v1.20 [and future changes] will likely be small tweaks rather than complete
  overhauls." Treat the 1.20 stat-testing formulas as the closest available
  proxy for 1.23b, and the pre-1.20 material (Combat SP, the v1.18 enmity work)
  as describing mechanics that 1.20 replaced.
- All formulas are the author's own "working"/best-fit predictors, explicitly not
  the true in-game formulas. He repeatedly flags his own numbers as
  approximations. Cross-check against primary evidence before shipping.

---

## Cure / Cura (patch 1.20) - `stat-testing-1-cure-formula`

Data: `healing-cure-cura.csv`, image `images/stat-testing-1-cure-formula/01.png`.
Column meaning (author's): `n` = trials; `PREDICT` = (MIN+MAX)/2; `DEV` = % gap
between MAX and PREDICT; `Mean` = trial average (not used in analysis); `Crit %`
= crit rate; `BONUS` = crit PREDICT as a % of normal PREDICT.

Author's conclusions (verbatim):

- "(1) Mind itself does not affect the HP gain from Cure when used on classes
  other than CNJ." (MND only adds cure HP on Conjurer; on other classes MND helps
  only via the +1 Healing Magic Potency per +4 MND.)
- "(2) Adding +1 Healing Magic Potency adds roughly 1.25 HP on Cure and 2.50 HP
  on Cura when on CNJ. It adds roughly 1.10 HP per potency when on non-CNJ
  classes." (Author stresses this is an oversimplification; "potency is a
  percentage increase to HP cured.")
- "(3) Vitality is a minor modifier to the Cure formula." ("roughly 1 point to
  Cure for every 8-10 points" of VIT; measured +9.5 cure for +84 VIT.)
- "(4) For CNJ only, +1 Mind adds roughly +0.25 to HP to Cure and 0.50 to Cura."
  Accounting for the +1 potency per +4 MND, the combined ratios are "0.5625 for
  Cure and 1.125 for Cura."
- Summary stat-gain ratios (author's):
  - Cure on CNJ: 1 potency = 1.25, 1 MND = 0.5625
  - Cura on CNJ: 1 potency = 2.50, 1 MND = 1.125
  - Cure on non-CNJ: 1 potency = 1.10, 1 MND = 0
- "(5) When the caster and target are both R50 with no critical bonuses, the %
  bonus on critical cures is roughly an increase of 22-23%. The rate is roughly
  7.8%." THM's "+10 critical" trait raises the pooled crit rate (THM 10.80% vs
  other 7.71%; Chi-squared 4.3968, p=0.036). "+58 critical potency" raises the
  crit bonus from ~22-23% to ~34-35% (i.e. BONUS column 123.70% -> 133.85%).

Damage variation model (used across all four posts): a hit's value is a uniform
random draw over a fixed set; "Minimum = Average x 0.95, Maximum = Average x
1.05" in ARR, but for 1.20 the observed DEV around large trials is ~3.00% (see
Trial Size Discrepancy section of the raw post), i.e. roughly +/- 3% about the
PREDICT midpoint. The mean equals the midpoint of true min/max.

---

## Magic Evasion / resist mechanics (patch 1.20) - `stat-testing-2-meva`

Data: `magic-evasion-caps.csv`, `magic-evasion-resist-tests.csv`, images
`images/stat-testing-2-meva/`.

Author's conclusions (verbatim):

- "(1) All magic spells and elemental based normal/TP attacks are subject to a
  MEVA check."
- "(2) There are 3 'tiers' of resists ... 'Single' (-25%), 'Double' (-50%), and
  Triple (-75%)." No -100% tier except Decoy and direct non-damage enfeebles.
- "(3) Elemental Resistances only affect direct damage taken and not MEVA or
  resist rate."
- "(5) There is no pre-mature resist rate floor or cap. You can potentially
  resist 100% or 0%."
- "(6) ... There is a 1:1 ratio where 1 'status resist' gives 1 MEVA for that
  status ailment."
- "(7) Enfeebling spells (maybe all magic spells) have their own unique land
  rates for a given MEVA."
- "(8) Enfeebling spells (e.g. Poison) likely only need to have any resist to
  fully resist. There is currently no such thing as a 'partial resist' for
  enfeebles."
- "(9) The 'Magic Evasion Down' effect on R50 CNJ's Stone gave -29 MEVA on R40
  Lemurs." (Unchanged by +80 PIE / +20 enfeebling skill.)

Resist rate vs MEVA is presented only as plotted curves (per-enemy), not a closed
formula; the plots and the enemy MEVA-to-cap estimates are in the images/CSV.

---

## Physical damage taken / Defense (patch 1.20) - `stat-testing-3-physical-damage-taken`

Data: `physical-damage-taken.csv`, images
`images/stat-testing-3-physical-damage-taken/`.

- The relationship between Defense and damage taken is "directly linear and this
  relationship does not appear altered by VIT (range 178 to 269)." Best-fit slope
  for the initial R52 test set was "a very consistent slope around -0.295 for all
  3 curves."
- There is "a cap on the amount of defense one can stack before no gains are
  seen ... defense works up to the point where the damage range becomes 35-42
  (38.5 predicted average)." Higher VIT does not change the floor but lowers the
  Defense needed to reach it.
- "The slope appears to increase as the level of the mob increases." Best-fit
  lines from the Blotched Mongrel rank series (image `04.png`; x = Defense,
  y = predicted damage taken):
  - @R40: y = -0.1580x + 114.71
  - @R43: y = -0.1786x + 135.54
  - @R46: y = -0.2127x + 166.15
  - @R49: y = -0.2280x + 195.22

---

## Critical damage bonus (patch 1.20, posted just before 1.21) - `stat-testing-4-critical-damage-bonus`

Data: `critical-damage-bonus.csv`, images
`images/stat-testing-4-critical-damage-bonus/`.

Author's conclusions (verbatim):

- "(1) The critical bonus is a straight percentage increase in damage / HP cured.
  This percentage increase is only affected by 'Crit Potency' enhancements, 'Crit
  Resilience' enhancements, and dLVL." (Same rule for physical, magic, and cure
  crits.)
- "(2) There is a cap on the critical bonus percentage increase at 175%. There is
  a floor at 115%." The formula may compute outside this band; the game clamps to
  it, but "+ critical potency effects are applied prior to application of the cap
  and floor."
- "(3) + Crit Potency enhancement increases the critical bonus by a fixed
  increase in %. This fixed bonus decreases as dLVL increases. The enhancement is
  applied before the bonus floor and cap."
- "(4) The baseline critical bonus (the critical bonus at +0 potency) is affected
  only by dLVL."
- "(5)" Worked example at dLVL=0: baseline critical damage bonus = 121.43%; with
  +10 crit potency the added bonus = 10 x 0.1729% = 1.729%, giving 121.43% +
  1.729% = 123.159%. ("Bonus to Potency Ratio" = crit bonus % per potency point;
  the full baseline-and-ratio-per-dLVL table for dLVL -30..+10 is in image
  `16.png`.)
- "(6) For cure criticals, dLVL is calculated by [Target Rank] - [Caster Rank].
  ... dLVL=0 is really the only relevant endgame situation."
- "(8) The Rampage status gives 50% of the critical damage dealt back to HP. This
  HP return is capped at 20% of your maximum HP."
- "(9) The Thundaga combo bonus grants a rough +175 magic critical potency and
  allows the critical to break and exceed the 175% critical damage bonus cap."

---

## Pre-1.20 material (superseded by the 1.20 rework)

These posts describe mechanics from before the 1.20 formula overhaul; the raw
text is preserved but the numeric graphs are mostly dead LiveJournal placeholder
images (see `file-inventory.csv`).

- `combat-sp-part-1` / `combat-sp-part-2` (~1.16): how combat Skill Points were
  awarded per action. Pre-1.20 SP mechanics.
- `enmity-testing-v118-part-1` and `enmity-table-v118` (patch 1.18): enmity
  generation testing and a per-action enmity table. The enmity table image is a
  dead placeholder and was not recoverable from any source, so the table values
  are lost; only the surrounding text survives.
- `abusing-the-return-ai` (~1.17): notes on exploiting mob "Return" AI behavior.
- `thaumaturge-dodore-solo` (~1.17): a THM solo writeup (video-backed).
- `five-months-in` (~1.16): opinion/retrospective, no formula content.
