# kanican FFXIV 1.x Combat Theorycrafting - Web Tables

## Study contents

Transcribed FFXIV 1.x combat theorycrafting from `kanican` (Kaeko Leta) on
LiveJournal - 11 posts spanning patches **1.18 to 1.20/1.21** (Aug 2011 - Mar
2012). This is the primary community source that later 1.x and ARR-beta testers
built their methodology on. Web-source evidence, **wiki tier** (packet captures >
video breakdown > wiki), so the values here are CALIBRATION-grade, not
retail-confirmed. The four 1.20 "Stat Testing" posts carry the recoverable data:
Cure/Cura scaling, magic evasion / resist tiers, physical damage taken /
defense, and critical damage bonus.

Not to be confused with Valk's "B.L.I.T.Z.B.A.L.L." (`valk.dancing-mad.com`),
which reused kanican's methodology but tested **ARR 2.0 beta** values - a
different game version, out of scope for this 1.23b repo.

## Start here

- `derived/evidence-map.md` - version/tier caveats, the best tables, and what was
  lost. Read before the raw posts.
- `derived/formulas.md` - every derived formula, ratio, and stated conclusion,
  verbatim, per post.

## Source material

- `sources/kanican-tables/objects/*.md` - the 11 posts, transcribed verbatim from the page HTML.
  The four `stat-testing-*` files are the data-bearing ones.
- `sources/kanican-tables/objects/images/<slug>/*.png` - 40 recovered Excel/graph screenshots (the
  authoritative source for any disputed CSV cell). All from the 1.20 stat-testing
  posts. The 48 pre-1.20 images are dead LiveJournal placeholders (unrecoverable).
- `derived/*.csv` - normalized tables: `healing-cure-cura.csv` (26 rows),
  `critical-damage-bonus.csv` (38 rows), `physical-damage-taken.csv` (21 rows),
  `magic-evasion-caps.csv`, `magic-evasion-resist-tests.csv`.

## Promoted conclusions

The recovered combat tables are the underlying calibration source used by
`bluegartr-stat-tests` for overlapping cure, resistance, defense, and critical
damage findings. They remain version-qualified community evidence.

## Topics

- cure / cura formula, healing magic potency, MND scaling
- magic evasion (MEVA), the -25/-50/-75% resist tiers
- physical damage taken, defense mitigation slope, damage floor
- critical damage bonus, 175% cap / 115% floor, critical potency, dLVL
- enmity (v1.18), combat SP mechanics (pre-1.20)

## Evidence gaps

- All pre-1.20 numeric images are dead placeholders not on the Wayback Machine.
  The **v1.18 enmity table values are lost** (text survives, table gone).
- CSVs were transcribed from Excel screenshots by eye. The preserved images are
  authoritative for disputed cells.
- Formulas are the author's best-fit predictors, not decompiled constants, and
  from the 1.20 era. They may have shifted by 1.23b.

## Further research

- The v1.18 enmity table image remains missing. Only its surrounding text
  survives.
