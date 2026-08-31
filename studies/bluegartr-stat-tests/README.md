# bluegartr FFXIV 1.x Community Stat Testing - Web Tables

## Study contents

Eight topic tables distilled from two bluegartr forum threads: **"Stats and how
they work."** (604 posts, 2011-10-11 to 2013-06-10) and **"Trait point cap?"**
(8 posts, 2011-09-02/03). Critical hit rate, critical damage bonus, enmity,
physical damage taken vs DEF/VIT and block, magic evasion, cure potency, and the
trait point cap ladder, plus a bounded Power Surge stat observation.

Web-source evidence, **wiki tier** (packet captures > video breakdown > wiki).
Everything here is **CALIBRATION** grade. Most tables come from players parsing
their own combat logs in samples of a few hundred to a few thousand swings.
The Power Surge rows instead preserve one displayed-stat observation and one
uncontrolled progression report. None has source access or methodology review.

**Every row carries the patch it was tested under.** The threads span 1.18b to
1.23b and the mechanics moved underneath them - 1.20 reworked essentially every
formula, 1.22 redid block damage reduction, and a 2012-05-23 hotfix inside 1.22a
rewrote the crit rating algorithms. A row without a patch would not be usable, so
`patch` and `patch_basis` are mandatory columns on every table.

The same author (Kaeko / kanican) cross-posted four of these topics to
LiveJournal in fuller form. **The `kanican-tables` set in this repo holds those
posts plus 40 recovered Excel screenshots** - go there for the underlying
numbers, and here for patch attribution, the discussion around them, and the
1.21-1.23a material kanican never covered.

## Start here

- `derived/evidence-map.md` - tier and patch caveats, the ten recorded
  contradictions, the "every multiple of 5 a stat tiers up" claim and why it is a
  display-rounding artifact, and the full list of lost images. Read before the
  CSVs.
- `derived/patch-dating.csv` - the release-date table behind every
  `patch_basis: post-date` assignment.

## Source material

- `sources/bluegartr-stat-tests/objects/pages/bg-107403-stats-and-how-they-work.md` - verbatim excerpts
  of the 25 data-bearing posts, tables and minimal caveats only. The rest of the
  604-post thread stays at the source.
- `sources/bluegartr-stat-tests/objects/pages/bg-106754-trait-point-cap.md` - the whole 8-post thread.
- `sources/bluegartr-stat-tests/objects/pages/bg-107403-power-surge-posts.md` -
  post metadata, one short source fragment, and non-verbatim locators for the
  Power Surge observations.

**Every numeric image in both threads is dead.** No graph, chart, table
screenshot or parser output survived on imageshack, imgbox, abload or
photobucket. What that cost is itemized in the evidence map. The largest losses
are Kaeko's per-action enmity table, the critical-damage-bonus-by-dLVL table
(dLVL -30 to +10), and the damage-floor-by-dLVL plot.

## Promoted conclusions

`derived/patch-dating.csv` is the version anchor used by downstream planning to
separate pre-1.20, post-1.20, and post-hotfix calibration material. The topic
tables remain CALIBRATION inputs. No individual formula is retail-confirmed.

## Topics

- critical hit rate: per-point return, the 20% cap claim and its collapse after
  the 2012-05-23 hotfix, dLVL dependence
- critical damage bonus: 175% cap, 115% floor, crit potency, Rampage HP return,
  the Thundaga combo's +175 magic crit potency
- enmity: per-action values, cure-to-enmity ratio, Chameleon / Freeze /
  Invincible / Antagonize / Flat Blade, enmity bar thresholds, the multi-target
  split
- physical damage taken: the DEF/VIT formula, the 2:3 DEF:VIT ratio, the
  dLVL-dependent damage floor, block rate and block damage reduction
- magic evasion: the -25 / -50 / -75% resist tiers, the 75% enfeeble land-rate
  cap, Magic Evasion Down
- cure potency: Cure III scaling, healing magic potency vs MND, CNJ-only MND,
  crit cure bonus, the Healer's Robe AF enhancement
- trait point cap: trait points by rank, 1 through 50
- Power Surge: displayed attack progression, the tier-one defense penalty, and
  the limits of the observed progression timing

## Evidence gaps

- No test in either thread ran on a 1.23b client. The closest anchors are the
  1.23a crit-rate parses.
- The Power Surge observations are patch 1.22a. The displayed-stat observation
  uses one uncontrolled character setup, while the progression report provides
  no setup details. Neither establishes exact tier thresholds or an
  enhanced-trait multiplier.
- Critical damage bonus was never re-measured after the 2012-05-23 hotfix, so
  the 175% / 115% cap and floor are unverified for 1.22a onward.
- Ten contradictions are recorded and left unresolved, including a self-
  contradiction inside a single post about whether crit potency applies before or
  after the cap and floor.
- Enfeeble land-rate tests were run at the cap, so they say nothing about how
  magic accuracy or MND move the rate.
- Out of scope on purpose: INT vs magic attack, weapon DPS and stat caps, the AF
  "Enhances" inventory, Regen and Stoneskin, Sentinel and Vengeance, Store TP,
  crafting stats, accuracy vs DEX.

## Further research

- The four overlapping topics have fuller treatment in `kanican-tables`; any
  promoted value should account for that source.
- The 1.23a crit-rate rows are the 1.23b crit calibration anchor, not the
  earlier 20% cap.
- Recovered copies of the dead image hosts would be most valuable for the
  enmity table and the crit-bonus-by-dLVL table.
