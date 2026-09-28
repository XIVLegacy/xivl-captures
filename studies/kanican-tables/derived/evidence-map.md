# Evidence map - kanican FFXIV 1.x combat theorycrafting

This map summarizes the FFXIV 1.x
theorycrafting of `kanican` (Kaeko Leta) on LiveJournal - the primary community
source that later 1.x/2.0 testers (e.g. Valk's "B.L.I.T.Z.B.A.L.L.") built their
methodology on.

## Evidence tier and version - read first

- Wiki tier (packet captures > video breakdown > wiki). A value here supports a
  CALIBRATION-tagged server value, not a retail-confirmed one.
- Data spans **patches 1.18 - 1.20/1.21** (Aug 2011 - Mar 2012). The repo targets
  **1.23b** (Nov 2012). Patch 1.20 "fundamentally changed essentially every skill
  and formula"; the author judged the 1.20 core formulas stable going into 1.21.
  So the four 1.20 stat-testing posts are the best proxy for 1.23b combat maths;
  the pre-1.20 posts (Combat SP, v1.18 enmity) describe replaced mechanics.
- Every formula is the author's explicit "working"/best-fit predictor, not the
  true in-game formula. He flags his own numbers as approximations throughout.

## Best tables (highest-value, recovered verbatim)

- `healing-cure-cura.csv` - 26-row Cure/Cura dataset (class, potency, VIT, MND,
  normal + critical MIN/MAX/PREDICT/mean, crit rate, crit bonus). Image
  `stat-testing-1-cure-formula/01.png` is authoritative.
- `critical-damage-bonus.csv` - 38-row crit dataset across enemies/dLVL/crit
  potency, with the 175% cap / 115% floor and per-dLVL baseline. Image
  `stat-testing-4-critical-damage-bonus/01.png` is authoritative.
- `physical-damage-taken.csv` - 21 Defense-vs-damage sample points at ranks 52
  and 59, plus the R40-R49 Defense trendlines in `formulas.md`.
- `magic-evasion-caps.csv` + `magic-evasion-resist-tests.csv` - enemy MEVA-to-cap
  estimates and resist-strength distributions; the -25/-50/-75% resist-tier
  model.
- `formulas.md` - every derived formula, ratio, and stated conclusion, verbatim.

## Confirmed / usable

- Cure/Cura stat scaling (MND is CNJ-only; potency is a % multiplier; VIT minor),
  the crit-bonus cap/floor (175% / 115%) and dLVL dependence, the three magic
  resist tiers (-25/-50/-75%), and the linear Defense->damage relationship with a
  damage floor - all backed by the recovered data tables above and internally
  consistent across ~100-trial samples.

## Unverifiable here / needs primary corroboration

- All numeric ratios and formulas are author best-fits, not decompiled constants.
  Any downstream value based only on these formulas remains CALIBRATION-tagged until
  corroborated by client-data, a decomp, or a packet set.
- The 1.20-specific constants (0.1729%/potency crit ratio, cure 1.25/2.50
  potency ratios, Defense slopes) may have shifted by 1.23b.

## Unique value

- These are damage/heal *magnitudes and mechanics* that neither the client data
  sheets nor the thin 1.23b packet corpus carry: crit multiplier behavior,
  resist tiering, defense mitigation slope, and cure scaling. This is the
  upstream primary source for the later community formula writeups.

## Gaps / lost evidence

- **All pre-1.20 numeric images are dead** LiveJournal placeholders and were not
  recoverable from LiveJournal's proxy or the Wayback Machine. The worst loss is
  the **v1.18 Enmity Table** (`enmity-table-v118`): its single table image is
  gone from every source (no Wayback snapshot exists), so the per-action enmity
  values are lost - only the surrounding text survives. The `enmity-testing`,
  both `combat-sp` posts, and the Dodore/Return-AI/Five-Months posts likewise
  keep their text but lost their graphs (48 dead images total; see
  `file-inventory.csv`).
- Within the 1.20 stat-testing posts, many supporting scatter-plot graphs were
  preserved as images but not re-keyed cell-by-cell (their datum - a trendline
  equation or a resist curve - is captured in `formulas.md`); the poison-resist
  panel in `sources/kanican-tables/objects/images/stat-testing-2-meva/09.png` is
  summarized, not fully transcribed.
- CSV values were transcribed from Excel screenshots by eye; the preserved images
  under `sources/kanican-tables/objects/images/` are the authoritative source for any disputed cell.

## Cross-source contradictions

- None internal to this set. Note only that the author explicitly contrasts his
  FFXIV 1.20 findings against FFXI and against the earlier 1.19 state; those are
  version differences, not contradictions. Downstream, Valk's ARR 2.0-beta
  "B.L.I.T.Z.B.A.L.L." reused this methodology but with 2.0 values - do not
  conflate the two (that site is out of scope for a 1.23b repo).
