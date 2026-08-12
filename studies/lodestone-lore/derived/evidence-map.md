# Evidence map - FFXIV 1.x Lodestone Lore - GC Newsletters, The Last Word, Events

The 1.x Lodestone lore/flavor pages, 63 transcribed into `sources/lodestone-lore/objects/pages/`.
Page-to-kind map: `index.md`; per-page provenance: `file-inventory.csv`.

## Tier

**Lowest tier in the Lodestone harvest: period lore and flavor, not mechanics.**

- First-party SE in-world/flavor writing (newsletters, a news serial, event
  announcements). It documents story and color, not game behavior.
- Nothing here is runtime evidence. Do not promote a figure or claim from these
  pages as a 1.23b behavior fact; packet/video/client-data and even the manual
  and dev-patch sets all outrank it.
- Value is limited to downstream lore, GC, and seasonal content.

## Highest-value pages (for lore)

- The Last Word serial (`last-word-*`) - the closest thing to a 1.x metaplot
  record: the Garlean advance, the Mor Dhona base (`harbor-herald-07` corroborates
  it), Dalamud's approach, Atomos, and the run-up to the Calamity, ending with
  `last-word-2012-11-01` "Goodbye, and Good Luck" at the 1.0 sunset.
- GC newsletters (`mythril-eye-*`, `raven-*`, `harbor-herald-*`) - each Grand
  Company's in-world voice and the alliance politics against the Empire.
- Seasonal-event posts - the 1.x in-world framing of each recurring festival.

## Coverage

- 30 GC newsletters (Mythril Eye 01-11, Raven 01-09, Harbor Herald 01-10),
  12 The Last Word, 21 seasonal events. Counts and dates in `file-inventory.csv`.
- GC newsletters use an older Lodestone template (`div.gc-news-detail-inner`);
  the converter handles both templates.

## Gaps and caveats

- **Flavor only** - see the tier note; not to be cited for behavior.
- Battle event posts (Ifrit / Garuda / Good King Moggle Mog / Skirmish)
  are in `lodestone-dev-patch`, not here.
- Prose ASCII-normalized (decorative circle bullets -> "-", a stray ideographic
  comma -> ","); three loanword accents kept verbatim (facade, naive). The
  byte-exact original is the cold-stored HTML in the master rar.
- This set completes the 1.x-relevant harvest; the remaining ~34 master-rar
  pages are ARR-transition / billing / misc announcements, out of 1.23b scope.
