# Evidence map - FFXIV 1.x Lodestone Dev Posts and Patch Notes

The 1.x Lodestone dev communications and patch notes, 63 pages transcribed into
`sources/lodestone-dev-patch/objects/pages/`. This file flags the highest-value posts, the patches
covered, the evidence tier, and gaps. Page-to-kind map: `dev-patch-index.md`;
per-page provenance: `file-inventory.csv`.

## Tier

First-party SE dev communication documenting **intended** 1.x changes. Ranking:

- Stronger than community wiki (this is SE announcing/explaining its own changes).
- Records design **intent and announcements**, not observed runtime. An announced
  change is intent until confirmed shipped in 1.23b; where it disagrees with a
  1.23b packet capture (`xivl-opcodes`) or the decoded client data
  (`xivl-client-data`), those win.
- Dates establish patch ordering; a value here is documented-intent, not
  runtime-confirmed.

## Highest-value posts

Most likely to inform downstream behavior/patch work:

- `battle-reform-auto-attack-2011-06-30.md` - the 1.18 auto-attack introduction
  (before 1.18, DoW/DoM had no passive auto-attack); explains the change.
- `battle-reform-enmity-2011-07-06.md` - the 1.18 enmity overhaul: from the old
  opaque calculation to an accumulated-actions model, plus the enmity UI icon
  (no icon / green-orange-red / blinking red = highest enmity, being targeted);
  direct vs indirect enmity; reset on KO/inaction.
- `patch-1-18-misc-2011-07-14.md` - fatigue/surplus system
  removal, Raise spell revisions, removal of anima cost for Return, and more.
- `patch-1-15a-notes...`, `patch-1-15b-notes...`, `patch-1-16-notes...` - the
  itemized change records (sidequests, levequest reworks, battle/size tuning,
  synthesis and UI changes).
- `version-update-details-*.md` and
  `upcoming-version-updates-*.md` - the
  broad 1.19/1.20-wave change briefings.
- `battle-system-changes-2011-02-01.md`,
  `battle-regimens-2010-10-06.md`,
  `balancing-2010-11-19.md` - combat-system direction.
- Feature posts: `guildleve-reforms-*`, `repairing-repairs-*`,
  `materia-intro-*`, `synthesis-balance-*`,
  `item-searching-*` / `item-search-*`.
- Content/encounter posts: the four `notorious-monsters-*`, `ifrit-*`,
  `garuda-*`, `good-king-moggle-mog-*` (primal encounter
  framing), `instanced-raids-*`, `beastman-strongholds-*`.
- `ask-the-devs-*` (17) and `producer-letter-*` (6) - scattered mechanic
  answers and design direction; read all claims in context and cross-check
  specific mechanics and figures.

## Patches / window covered

- Dated 2010-09-21 (Prelive FAQ) to 2012-07-10 (Skirmish).
- Explicit patch notes: 1.15a, 1.15b, 1.16, 1.18. Version-update briefings cover
  the 1.19/1.20 wave. Battle-reform posts target 1.18-1.19.

## Gaps and caveats

- **Dev/patch only.** The master rar holds 208 pages; the ~120
  lore/event/ARR-transition pages, the 12 Beginner's Guide columns, and 4 2013
  ARR-beta pages are not here (the ARR pages are out of 1.23b scope).
- **Announced vs shipped.** Posts describe intended changes; confirm against the
  1.23b client/packets before treating a specific number as runtime truth.
- **Ask the Devs / letters** are conversational; treat specific figures in them
  as the softest evidence in this set.
- Prose is ASCII-normalized (two verbatim glyphs kept: a yen sign, an accent in
  "a la mode"); the byte-exact original is the cold-stored HTML in the master rar.
