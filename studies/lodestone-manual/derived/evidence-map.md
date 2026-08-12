# Evidence map - FFXIV 1.0 Lodestone Official Game Manual

The official FFXIV 1.0 Lodestone game manual, 36 pages, transcribed verbatim
into `sources/lodestone-manual/objects/pages/`. This file flags the highest-value pages per system,
the evidence tier, and known gaps. For the page-to-wiki-section map see
`wiki-target-index.md`; for per-page provenance see `file-inventory.csv`.

## Tier

First-party SE documentation of **intended** 1.x behavior. Ranking for this repo:

- Stronger than community wiki (this is the source, not a fan interpretation).
- Records design **intent**, not observed runtime. Where it disagrees with a
  1.23b packet capture (`xivl-opcodes`) or the decoded client data
  (`xivl-client-data`), those win - the manual describes what the game was
  meant to do, which can diverge from what 1.23b shipped, and it predates the
  1.23b sunset by up to two years of patches.
- A value taken only from here is **documented-intent**, not runtime-confirmed.

## Highest-value pages

Mechanic ground truth most likely to inform downstream behavior work:

- `battle-and-being-ko.md` - flow of battle; auto-attack eligibility (DoW/DoM
  only, main-hand weapon, must face target, interval by weapon); enmity is
  direct (damage/enfeeble) vs indirect (heal/buff), reset on KO or inaction;
  Being KO'd -> Return (Weakness 3 min, durability loss) vs Raise (Weakness +
  Brink of Death 3 min); EXP chain and linked-enemy bonuses; loot/spoils list
  rules; attribute points (DoW/DoM from Lv10, 5 pts then +1/level, per-attribute
  level cap, Keeper's Hymn to undo).
- `effect-inducing-tactics.md` - incapacitation/status tactics and combos.
- `actions-and-traits.md` - action categories (weaponskill/magic/combat
  ability), traits are class-exclusive passives, cross-class action caps, the
  Actions & Traits interface.
- `classes-and-jobs.md` - the class/discipline system.
- `materia.md` - spiritbond, conversion, grades, melding, grade-compatibility
  tables (the filled-circle marker means "compatible").
- `guildleves.md` - the levequest system.
- `aetheryte.md` + `getting-around.md` - aetheryte teleport / Return / home-point
  mechanics.
- `synthesis.md`, `repair.md` - crafting and durability.
- `hamlet-defense.md` - the instanced Battle-for defense content.

## Coverage

- 36 pages transcribed; text coverage vs the source HTML content is ~1.00 on
  every page (no page silently dropped content). Word/image counts per page are
  in `file-inventory.csv`.
- Every referenced image (330) was copied into `sources/lodestone-manual/objects/images/<slug>/`.

## Gaps and caveats

- **Manual only.** The archive holds 208 pages; the ~170 news/lore/patch/event
  pages (Ask the Devs, Letters from the Producer, patch notes, Battle Reform
  Auto-Attack / Enmity, Comprehensive Version Update Details, GC newsletters,
  seasonal events, ARR-transition notices) are NOT transcribed in this set. The
  dev/patch and lore subsets are covered by `lodestone-dev-patch` and
  `lodestone-lore`; the remaining pages stay in the cold-stored master rar.
- **Patch drift.** These pages are a Jan-2015 snapshot of a manual written across
  1.0-1.23; individual numbers may reflect an earlier patch than 1.23b. Treat
  specific values as intent; patch-note comparison is needed when version matters.
- **Prose normalized to ASCII.** The byte-exact original is the cold-stored HTML
  in the master rar; the recorded `checksums.sha256` covers the transcribed `.md`
  and image files, not the HTML.
- **Data CSVs** live in `tables/` (19 files, 481 rows), rebuilt from the
  rowspan-aware HTML because the Markdown flatten dropped some anchor rows (e.g.
  the repair 1-10 tier, the Sword incapacitation weaponskills, the GC Enlistee
  rank, the Carbonized Matter catalyst). Image-only grids (macro icons, micro-menu
  legend) and the 4-column interaction-menu were left inline in the page `.md`.
