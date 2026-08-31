# Evidence map - bluegartr FFXIV 1.x community stat testing

Filter this before using the CSVs. This set distills two bluegartr threads -
"Stats and how they work." (604 posts, 2011-10-11 to 2013-06-10) and "Trait point
cap?" (8 posts, 2011-09-02/03) - into eight topic tables. Everything here is
**CALIBRATION** grade.

## Evidence tier and version - read first

- Wiki tier (packet captures > video breakdown > wiki). Nothing in this set
  supports a retail-confirmed value. Community players parsing their own combat
  log, no source access, no methodology review.
- **Every row carries a `patch`.** A row without one is not usable, because the
  thread spans 1.18b to 1.23b and the mechanics moved underneath it: 1.20
  reworked essentially every skill and formula, 1.22 completely redid block
  damage reduction, and a 2012-05-23 hotfix inside the 1.22a window rewrote the
  critical hit rating / critical attack power / magic critical rating
  algorithms. A crit number from 1.21a and a crit number from 1.23a are
  measurements of different games.
- `patch_basis` says how the patch was assigned. `stated` means the tester named
  the patch they tested under; `post-date` means it was derived from the post
  date against `patch-dating.csv`, which is built from the bluegartr patch-note
  thread start dates. `post-date` is the weaker attribution: a post can report a
  test run days or weeks earlier. Kaeko's block writeup (post 439) is the clearest
  case - posted 2012-05-26, inside 1.22a, but explicitly tested under 1.22.
- Sample sizes are a few hundred to a few thousand swings. The largest single
  dataset in the whole thread is 6,027 attacks; several conclusions rely on
  100-200 trials, and some on a stated eyeball impression.
- The repo targets **1.23b** (2012-09-12). Only a handful of posts postdate it
  and none of them are tests. The closest usable rows are the 1.23a crit-rate
  parses (posts 570 and 582).

## Best tables

- `critical-hit-rate.csv` - 20 rows. The strongest single dataset in the set is
  Kaeko + Seiken's 6,027-attack R45 control and its 3,015-attack +crit-rate arm
  (post 330). The 1.23a rows from post 582 are the closest thing to a 1.23b
  measurement anywhere in the set.
- `physical-damage-taken.csv` - 20 rows. Kaeko's DEF/VIT formula and the 2:3
  DEF:VIT ratio (post 217) are the most reused conclusions from the thread, and
  the block rate / block reduction rules from post 439 are the only per-point
  numbers for either mechanic.
- `enmity.csv` - 32 rows. Mostly Stanislaw's translations of a JP tester's
  per-ability measurements across 1.20 to 1.21a - the only per-action enmity
  numbers that survive at all, since Kaeko's own R50 enmity table is a dead
  image.
- `cure-potency.csv` - 22 rows. Kaeko's three-build Cure III dataset (n=608,
  post 39) is fully transcribed including criticals.
- `magic-evasion.csv`, `critical-damage-bonus.csv`, `trait-point-cap.csv`,
  `power-surge.csv`, `patch-dating.csv`.

## Unique value

- Per-action **enmity** numbers, enmity bar thresholds, and the multi-target
  enmity split. Nothing in the client data or the pcap corpus carries these.
- The **DEF/VIT damage formula shape** and the existence of a dLVL-dependent
  damage floor.
- **Trait point cap by rank** - the equipped-trait budget, from the only thread
  that ever tabulated it.
- Patch-by-patch **drift**: the same mechanic measured before and after 1.20,
  1.21, 1.22 and the 1.22a crit hotfix. This is the set's real contribution -
  it shows which 1.x numbers are safe to carry to 1.23b and which are not.
- A bounded **Power Surge displayed-stat ladder** under patch 1.22a. It is a
  calibration observation, not a formula or target-version value.

## Power Surge claims and limits

Post 429 labels its test as patch 1.22a. One character using mostly artifact
armor and a Mogfork displayed 574 attack before Power Surge, then 689, 805, and
920 at tiers one through three. The observed deltas were 115, 116, and 115. The
author described the increase as roughly 115 per tier and reported an
approximate 158 defense loss at tier one. Defense then remained at 386 in the
listed setup. Two tested base attack values led the author to reject simple
percentage scaling.

The same post estimates roughly five minutes to reach tier three while stating
that the tier-two to tier-three transition was not watched. Adjacent post 431
mentions trying Jump and weapon skills and says more than three weapon skills
were needed. Neither post supplies the exact qualifying-action count, timestamps,
raw log, hidden precision, rounding rule, or controlled equipment comparison.

Related records own only separate parts of the action contract:

- `elemen-battle-actions:derived/battle-actions.csv` identifies Power Surge as
  command 27261, records three stages, names weapon skills or Jump as the
  extension trigger, says reuse ends the effect, and makes Life Surge mutually
  exclusive. These are web-table CALIBRATION claims, not packet observations.
- The same Elemen table says Enhanced Power Surge, trait 27281, increases the
  effect by 1.5 times. This remains a web-table CALIBRATION claim. No retained
  packet or video observation confirms the multiplier.
- `status-wire-projection-census:derived/status-projections.csv` contains no
  Power Surge status observation. Existing packet products therefore do not
  establish the status sequence, exact magnitudes, tier thresholds, refresh,
  reuse termination, or mutual-exclusion behavior.

The Power Surge ledger preserves the forum claims at their source tier. It does
not authorize attack values for 1.23b, a multiplier, a duration, a tier counter,
or server policy.

## Contradictions - recorded, not resolved

1. **Crit potency vs the cap and floor.** Post 261 states, in the same
   paragraph, that +Crit Potency is applied *after* the bonus floor and cap
   (bullet 3) and that it is applied *prior to* them (the sentence immediately
   below). The worked example that follows only makes sense on the "prior to"
   reading. Both are preserved in `critical-damage-bonus.csv`.
2. **+62 vs +72 crit rate, same trial.** In post 330 Seiken's quoted summary
   says "+72 Crit Rate increased the % to 13.5% (3000 trials)"; Kaeko's tabulated
   version of what reads as the same trial says "Addition (+62): 406/3015
   [13.47%]". The trial count matches, the gear value does not. This propagates:
   Kaeko's "+30 crit per +1%" is derived from the +62 figure.
3. **Crit rate cap.** 20% (posts 265, 330, 1.20a-1.21a) versus 26.43% measured
   at +102 crit rate on an R40 doblyn (post 582, 1.23a). Not a contradiction so
   much as the 2012-05-23 hotfix, but the 20% figure was quoted as a hard cap for
   months afterward.
4. **Crit rate return per point.** ~0.036%/point, +30 per 1% (1.21a, post 330)
   versus ~0.16%/point, +6-7 per 1% (1.22a, post 432) - a 4-5x jump across the
   hotfix. Both stand.
5. **Enmity gear.** 1 stat = 0.1% enmity (post 332, 1.21a) versus +1 enmity =
   +0.01% (post 478, 1.23) - a factor of 10. Post 478 states it as known without
   citing a test, and builds a spreadsheet on it.
6. **Aggro enmity.** Kaeko measures a tiny aggro bonus worth 1 damage (post 201);
   the JP tester concludes aggroing causes no enmity at all (post 207). Both are
   1.20.
7. **Chameleon.** -760 (1.20) -> "around 1200" (1.21, eyeball) -> -840 (1.21a,
   measured). The 1200 figure has no data behind it.
8. **Block reduction across 1.22.** Post 312 (1.21a) measures -63.6% to -72.7%
   on an R52 target; post 439 (1.22) says the pre-1.22 formula "gave -20%
   reduction against most anything over R50". The 1.21a numbers were taken with
   the damage floor already reached, which may be the whole explanation - it is
   not resolved in-thread.
9. **Healer's Robe cure bonus.** Rocl's printed averages give about +9% (616 ->
   672, 1264 -> 1359, 1072 -> 1168); his own stated conclusion is 7-8%; Niiro
   reading the first partial dataset says 10%; a ~100-cast follow-up says 7%. The
   printed sample values are in the CSV, and the Cura no-AF average printed as
   1264 does not match the five printed values, which average 1252.4.
   Additionally the AF and no-AF sets differ by 7 MND and 2 healing potency, so
   the comparison never isolated the robe.
10. **Cure III formula.** The post-39 formula (196 + Healing*1.5 + MND*0.25,
    1.19) and the post-182 ratios (+1.25 HP per potency on CNJ Cure, +0.25 per
    MND, 1.20a) are different mechanics from different patches, not competing
    fits. Do not average them.

## The "every multiple of 5" claim - display rounding, not a mechanic

Post 6 (2011-10-12) asserts that "on every mutiple of 5 (210, 215, 220, 225,
ext), a stat will go up, like magic attack, elemental resists, magic acc, magic
enhancing" and that the same holds for attack stats. It was repeated all thread
as fact - "5 MND = 1 magic accuracy" (posts 15, 174), "5 INT = 1 magic potency"
(post 137), "every ~4 INT adds 1 MATK" (post 548) - and later hardened into
claims of real damage thresholds (post 247: a jump at 340 in both stats).

**Treat it as a display-rounding artifact.** The character sheet shows derived
stats as integers. A primary attribute that contributes a fraction of a point to
a derived stat will only visibly tick the displayed number every few points; that
is what every one of these observations actually measured - the menu updating,
not the damage changing. Kaeko's position, from testing rather than menu-reading,
is the opposite: "all stat increases give linear returns that are independent of
each other beyond caps" (post 240), and he tested VIT to 345 with no change in
return per point (post 248), publicly challenged the threshold claim, and got no
response. The DEF/VIT formula (post 217) is linear with no step terms.

None of the "tiers up at every multiple of 5" claims are in the CSVs. Only the
measured per-point returns are.

## Gaps and lost evidence

- **Every numeric image in both threads is dead.** No graph, chart, table
  screenshot or parser output was recovered from imageshack, imgbox, abload or
  photobucket. The worst losses, in order:
  - Kaeko's **R50 enmity table** (post 201) - the per-action enmity values. Only
    the recurring cluster values 4, 19, 114, 55, 363 survive in prose.
  - The **critical damage bonus table by dLVL** (post 261), covering dLVL -30 to
    +10 with baseline bonus, bonus-to-potency ratio, and wasted potency per row.
    The 175% cap and 115% floor survive; the per-dLVL curve does not.
  - The **damage floor by dLVL** plot and the **damage reduction per +1 DEF by
    dLVL** plot (post 217). The formula shape survives, the coefficients do not.
  - The **MEVA resist-rate plot** for Seismic Scream, its per-mob MEVA table, and
    the mirrored magic-accuracy version (post 215).
  - The **block baseline by dLVL** raw data sheets (post 439). The per-point
    rules survive, the dLVL baselines they add to do not.
- The four kanican LiveJournal posts cross-posted here (cure formula, MEVA,
  physical damage taken, critical damage bonus) are the same author's fuller
  writeups. **The `kanican-tables` set in this repo holds those posts and 40
  recovered Excel screenshots from them** - go there first for the underlying
  numbers, and use this set for the patch attribution, the discussion, and the
  1.21-1.23a material kanican never covered.
- Kaeko never posted a formula for Cure III (1.19) or for magic attack, and
  repeatedly declined to, on the grounds that the game changed faster than the
  testing.
- No test in either thread was run on a 1.23b client.
- Crit damage bonus was never re-measured after the 2012-05-23 hotfix. Post 575
  says as much: "That's one of the reasons I never got around to looking at the
  crit atk changes." So the 175%/115% cap and floor are **unverified for 1.22a
  onward**, including 1.23b.

## Out of scope

The threads carry substantial material this set deliberately does not
transcribe, per the intake rule against mirroring whole articles: INT vs magic
attack and the Thundara combo's +700 MATK, weapon base damage vs weapon DPS and
the primary/secondary stat caps, the per-piece AF "Enhances" effect inventory,
Regen and Stoneskin scaling off Enhancing Magic, Sentinel/Vengeance/Sanguine Rite
damage reduction, Store TP, crafting and gathering stats, and accuracy vs DEX.
Read the source threads for those.

## Further research

- The four overlapping topics have fuller treatment in `kanican-tables`, which
  contains the recovered images and is by the same author.
- The 1.23a crit-rate rows (posts 570, 582) are the calibration anchor for 1.23b
  crit, not the 20% cap.
- Recovered Wayback snapshots of the dead image hosts would be most valuable for
  the enmity table and the crit-bonus-by-dLVL table.
