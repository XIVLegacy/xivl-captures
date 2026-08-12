# FFXIV 1.x Lodestone Dev Posts and Patch Notes

## Study contents

Clean Markdown transcription of the **official 1.x Lodestone dev communications
and patch notes** - 63 pages, ~55,000 words, 166 images - harvested from the same
January 2015 master archive as the manual set. This is the **patch-history /
design-intent layer**: what SquareEnix changed and why across 1.x, plus the
developer Q&A and producer letters. One `.md` per page, dated 2010-09-21 to
2012-07-10 (1.0 launch prep through late 1.x).

Grouped by kind in `derived/dev-patch-index.md`:

- **patch-notes** (4) - Patch 1.15a, 1.15b, 1.16, 1.18 Miscellaneous Adjustments
- **version-updates** (3) - Comprehensive Version Update Details / upcoming-content
- **battle-mechanics** (5) - Battle Reform Auto-Attack, Battle Reform Enmity,
  Battle Regimens and Incapacitation, Changes to the Battle System, Balancing
- **systems-and-features** (12) - materia, guildleve reform, repair, synthesis,
  UI, item search, settlements, airships, instanced raids, quest adjustments
- **content-and-monsters** (14) - NMs, Ifrit/Garuda/Good King Moggle Mog, relic,
  gear, beastman strongholds, skirmish
- **dev-qa** (17) - Ask the Devs!
- **producer-letters** (6) - Letters from the Producer I-V + Message from the Director
- **pre-launch** (2) - Prelive FAQ, Choosing a Path Companion

Provides first-party patch-history and design-intent reference for downstream
behavior and reference content. The verbatim SE text stays here in the
evidence layer.

**Evidence tier.** First-party SE dev communication of design **intent** -
stronger than community wiki, but it records what was *announced/intended*.
Observed packet/video evidence still outranks it for actual runtime values, and
an announced change is intent until confirmed shipped in 1.23b.

## Start here

- `derived/dev-patch-index.md` - the 63 pages grouped by kind and ordered by date.
- `derived/evidence-map.md` - highest-value posts, the patches covered, tier note.
- `derived/file-inventory.csv` - every page: slug, title, date, subclass, topic
  URL, word/image counts. The single home for per-page provenance.

## Source material

- `sources/lodestone-dev-patch/objects/pages/<slug>.md` - the 63 posts, transcribed verbatim from the
  saved HTML. Typographic punctuation is normalized to ASCII. Two genuinely non-ASCII
  glyphs kept verbatim (a yen sign, an accented letter in "a la mode").
- `sources/lodestone-dev-patch/objects/images/<slug>/*` - 166 screenshots/diagrams from the posts that
  carry them (31 of 63 pages), referenced inline.
- Master archive: the full `Old Lodestone.rar` (all 208 pages) is the **same**
  file cold-stored under the manual set at
  `archives/lodestone-manual/Old Lodestone.rar` (gitignored);
  not duplicated here. sha256 in `manifest.yaml`.

## Promoted conclusions

The dated patch and design-intent record is used by downstream consumers and
supplies patch chronology for versioning community measurements. Announced
behavior remains intent until retail-confirmed.

## Topics

- Battle reform: auto-attack introduction (1.18), enmity calculation overhaul
  and the enmity UI icon, battle regimens/incapacitation
- Patch-note history: 1.15a/1.15b/1.16/1.18 adjustments; comprehensive version
  updates for the 1.19/1.20 wave
- System changes: fatigue/surplus removal, Raise and Return revisions, materia
  introduction, guildleve reform, repair changes, synthesis balance, item search
- Content: notorious monsters, Ifrit / Garuda / Good King Moggle Mog primals,
  settlements, airships, instanced raids, relic weapons
- Dev direction: 17 Ask the Devs Q&A, 6 producer letters

## Evidence gaps

- **Dev/patch only.** The master rar's ~120 lore/event/ARR-transition pages (GC
  newsletters, The Last Word, seasonal events, ARR-transition/billing) and the
  12 Beginner's Guide columns are NOT harvested. Four 2013 ARR-beta pages were
  excluded as out of 1.23b scope.
- **Intent, not shipped state.** These announce and explain changes. Whether a given
  change landed exactly as described in 1.23b needs confirmation against the
  client/packets. Dates give the patch ordering.
- Prose punctuation is normalized to ASCII. The byte exact original is the
  cold-stored HTML in the master rar.

## Further research

- Announced changes still need confirmation against 1.23b client or packet
  evidence before they can be treated as shipped behavior.
