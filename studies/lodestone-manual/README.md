# FFXIV 1.0 Lodestone Official Game Manual

## Study contents

Clean Markdown transcription of the **official FINAL FANTASY XIV 1.0 Lodestone
game manual** - 36 pages, ~45,000 words, 330 content images - harvested from a
local January 2015 snapshot of the (now defunct) 1.x Lodestone. This is SE's own
first-party documentation of how 1.x works: combat flow, actions/traits,
classes, gathering, crafting, materia, guildleves, travel, grand companies, the
UI, and text commands. One `.md` per page.

Built as reference text for downstream reference work and implementation
consumers.
Verbatim SE text stays here in the evidence layer, and
`derived/wiki-target-index.md` maps each page to its content area.

**Evidence tier.** This is SE's own manual, so it documents *intended* 1.x
behavior authoritatively - stronger than community wiki. But it records design
**intent**: observed packet/video evidence still outranks it for actual runtime
values, since intent can diverge from what 1.23b shipped. Treat a value taken
only from here as documented-intent, not runtime-confirmed.

Full page prose is preserved because the source site is dead and the manual's
mechanic descriptions are the evidence.

## Start here

- `derived/wiki-target-index.md` - the 36 pages grouped by downstream reference
  area (Battle, Classes, Gathering, Crafting, Travel, ...), each with its source
  URL. Start here to find the pages behind a given wiki page.
- `derived/evidence-map.md` - the highest-value pages per system, the tier note,
  and known gaps.
- `derived/file-inventory.csv` - every page: slug, title, section, source URL,
  word count, image count. The single home for per-page provenance.
- `derived/tables/` - 19 normalized CSVs (481 rows) pulled from the manual's
  inline data tables (text commands, emotes, macro placeholders, keyboard
  controls, config options, classes, jobs, grand-company ranks, aetherial
  transport, incapacitation matrices, materia grades/catalysts, repair costs,
  achievement NPCs, main menu, display-name colors). See `derived/tables/index.md`.

## Source material

- `sources/lodestone-manual/objects/pages/<slug>.md` - the 36 manual pages, transcribed verbatim from
  the saved HTML. Prose, headings, and tables are preserved. Typographic punctuation
  is normalized to ASCII. Genuinely non-ASCII data cells are kept verbatim (the Materia
  grade-compatibility tables use a filled-circle yes-marker).
- `sources/lodestone-manual/objects/images/<slug>/*` - 330 page screenshots and UI diagrams, referenced
  inline from each `.md`.
- Master archive: the full `Old Lodestone.rar` contains all 208 saved pages,
  including the ~170 news / lore / patch-note / event pages **not** transcribed
  here. It is not duplicated here; its sha256 is recorded in `manifest.yaml`.

## Promoted conclusions

`derived/wiki-target-index.md` maps the manual into downstream reference
content, and the normalized tables supply reusable class, job, materia, travel,
repair, command, and UI reference data. Manual-only values remain documented
intent.

## Topics

- Battle: flow of battle, auto-attack eligibility, enmity (direct/indirect),
  Being KO'd, Weakness / Brink of Death, EXP chain, loot/spoils, attribute points
- Classes and Jobs; actions/traits/abilities and the action bar
- Gathering (mining, logging, fishing), crafting (synthesis, repair, materia)
- Travel (getting around, aetheryte/Return), guildleves, quests, hamlet defense,
  inns, achievements
- Grand Companies (Maelstrom, Twin Adder, Immortal Flames) and Garlean Empire lore
- UI (game screen, menus, configuration) and text commands / macros

## Evidence gaps

- **Manual only.** The archive's ~170 news/lore/patch/event pages (Ask the Devs,
  Letters from the Producer, patch notes, Battle Reform posts, GC newsletters,
  seasonal events, ARR-transition notices) are NOT transcribed in this study. The
  dev/patch and lore subsets are covered by `lodestone-dev-patch` and
  `lodestone-lore`; the remaining pages stay in the cold-stored master rar.
- The inline data tables are normalized in `derived/tables/` (19 CSVs). Prose-
  heavy tables and image-only grids (the macro-icon reference, micro-menu icon
  legend, meldable-slot lists, the 4-column interaction-menu) were left inline in
  the page `.md`, not turned into CSVs.
- Prose punctuation is normalized to ASCII. The byte exact original is the
  cold-stored HTML in the master rar.

## Further research

- Runtime confirmation remains open for manual values that have no packet or video
  corroboration.
