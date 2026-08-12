# Evidence map - Gamer Escape FFXIV 1.x item and mob tables

Filter this before using the CSVs. This set is a normalized mine of the Gamer
Escape FFXIV wiki's 1.0-era `Infobox Item`, `Infobox Mob` and `Mob Row`
templates, taken from an 11,227-page raw-wikitext corpus.

## Evidence tier and version - read first

- Wiki tier (packet captures > video breakdown > wiki). A value here supports a
  CALIBRATION-tagged server value, not a retail-confirmed one.
- **Check `xivl-client-data` first.** Item and mob names, ids, and much of the
  numeric stat block are shipped by the client and are primary evidence there.
  Use this set for what the client sheets do not carry (patch attribution,
  removal status, spawn zones, drop lists, crafting-recipe composition) or to
  corroborate a decode.
- Version is not one patch. Pages were last edited across the whole 1.x run and
  beyond; `ge_revision_timestamp` is the only per-row version signal, and it
  dates the *edit*, not the observation. Treat the tables as a 1.x aggregate that
  drifts toward late 1.x, not a 1.23b snapshot.
- Editorial provenance: community wiki, uncredited, no stated methodology, no
  sample sizes. Numeric fields are whatever an editor typed.

## Best tables (highest-value)

- `items.csv` - 5,665 rows x 68 columns, one row per `Infobox Item` call. 157
  item categories; the dense fields are `item_category` (5,663),
  `resale_price_gil` (3,929), `recipe_templates_raw` (3,672), `repair_class`
  (2,891), `wear_durability_points` (2,917), `meldable` / `convertible` (~2,750
  each), `description` (2,499), `defense` (2,108).
- `mobs.csv` - 824 rows x 27 columns, one row per `Infobox Mob` call. 72
  families; 769 rows carry `level_low`, 458 carry `hp_low`, 106 are flagged
  `notorious_monster`.
- `mob-locations.csv` - 1,501 rows x 8 columns, one row per `Mob Row` sighting
  across 51 zones and 822 distinct mobs. Carries `zone`, `map_coords`,
  `event_or_quest`, `level_range`, `drops`, `behavior_flags`.
- `npcs.csv` - 1,333 rows x 16 columns, one row per `Infobox NPC` call, 1,311
  distinct NPCs. The only source here for an NPC's `race` (1,282), `clan` (935),
  `gender` (1,242), `occupation` (577), `affiliation` (1,077), `zones` (1,261) and
  `map_coords` (1,182) - the client ships an NPC's name and model and nothing else.
  **Best-dated GE material in the set**: 263 of its source pages were last edited in
  2010 and none after 2012, so it is the one table here that is unambiguously 1.0
  rather than a 1.x aggregate.
- `mob-families.csv` - 52 rows x 16 columns, one row per `Infobox Mob Family`
  call. The family tier of the taxonomy, and the only source here for
  `superfamily`. Its `element` / `elemental_weakness` / `behavior_flags` are the
  defaults that individual mob rows override, so it is denser than `mobs.csv` on
  all three.

## Unique value - what no live FFXIV wiki documents

Two fields justify this set on their own. The modern Gamer Escape and Final
Fantasy XIV wikis document A Realm Reborn onward; 1.x content that was removed
before ARR was dropped, and per-item 1.x patch attribution was never carried
forward at all.

- **`patch_introduced`** - 1,087 of 5,665 items. Distribution: 1.17 (53), 1.18
  (115), 1.19 (130), **1.19a (2)**, 1.20 (114), **1.20b (6)**, 1.21 (278), 1.22
  (197), 1.22a (66), **1.22b (31)**, **1.22c (31)**, 1.23 (38), 1.23a (25),
  1.23b (1). The bolded sub-patches are the point: 1.19a, 1.20b, 1.22b and 1.22c
  are not enumerated in any surviving wiki, and this is the only per-item
  attribution to them found so far.
- **`removed_before_arr`** - 2,593 of 5,665 items (46%), set from the source
  page's `{{Obsolete}}` / `{{PhasedOut}}` template. This is the 1.x-only item
  population: content that existed on the 1.23b server and has no ARR-era
  equivalent to look up.

Secondary unique value: `recipe_templates_raw` preserves the full `{{Recipe}}`
wikitext (crystals, ingredients, HQ outputs) for 3,672 items, and
`mob-locations.csv` carries the 1.x zone roster including instanced and removed
zones (`Locke's Lie`, `Rivenroad`, `Castrum Novum`, `Mistbeard Cove`,
`Cassiopeia Hollow`, `Shposhae`, `Paglth'an`, `Natalan`, `Murmur Rills`).

## Confirmed / usable

- Column semantics are stable: every column is one GE infobox param, renamed to
  `lower_snake_case` with the unit carried in the name
  (`delay_seconds`, `recast_seconds`, `duration_seconds`, `resale_price_gil`,
  `wear_durability_points`, `blunt_attack_pct` and its three siblings). No value
  was interpolated, coerced, or unit-converted - cells are as printed on the
  page.
- Per-row provenance is exact and re-checkable: `ge_page_title`,
  `ge_revision_id`, `ge_revision_timestamp`.
- The `source` column keys each row to the manifest `sources:` list
  (`ge-item-pages`, `ge-mob-pages`, `ge-mob-family-pages`).

## Contradictions and dirty data - recorded, not resolved

- **Boolean fields are not normalized upstream.** `unique` alone appears as
  `Yes` (537), `yes` (172), `Y` (98), `y` (77), `x` (14) and `Yea` (1);
  `meldable`, `convertible`, `untradeable`, `has_attributes`, `aggressive`,
  `notorious_monster`, `drops_no_shards` and `drops_no_crystals` are the same
  shape. Presence means true; the spelling is meaningless. Left verbatim on
  purpose - normalizing would be interpolation.
- **HTML entities and template pages were defects, now fixed upstream.** The
  miner did not decode `&#39;` (127 item names, 14 mob names) and mined the
  `Infobox Mob` template-definition pages as three placeholder mobs. Both are
  fixed in the now-retired `tools/mine_gamerescape.py` and the CSVs regenerated;
  mob counts moved 827 -> 824 rows and 1,507 -> 1,501 sightings as a result.
- **Three value-corrupting defects were also fixed upstream**, all in the same
  miner and none of them changing a row count: `<br>` was stripped as a tag and
  fused list entries (29 materia rows read `+6Vitality`), element icon templates
  reached cells as the literal `{{Earth}}` on 44 of 72 populated
  `elemental_weakness` values, and `{{Verification}}` was mined as data in 4
  cells. Details in `mob-client-crosscheck-notes.md`.
- **`hq_effect` mixes two vocabularies**: bare grades (`+1`, `1`, `+3`, `3`,
  `+2`), the string `No` (85 rows), and full stat phrases
  (`Magic Accuracy+10`). Do not parse it as a number.
- **`removed_before_arr` is item-side only in practice.** Zero of the 824 mob
  rows carry it: the Obsolete/PhasedOut templates were applied to item pages and
  essentially never to mob pages. A mob absent from ARR is not flagged here -
  absence of the flag is not evidence the mob survived.
- **`item_category` carries at least one typo**: one row reads
  `Thamaturge's Arm` for `Thaumaturge's Arm`. The client files it with the
  correctly spelled rows, so the misspelling is GE's. Do not treat
  `item_category` as a closed vocabulary.
- **Five duplicate `item_name` values** across 5,665 rows (one page emitting two
  `Infobox Item` calls, or two pages sharing a name). Rows are not deduplicated;
  key on `ge_page_title` + row order, not on name.
- **Zone naming is not the canonical 1.0 roster.** `mob-locations.csv` carries
  both `Coerthas` and the split `Coerthas Central/Eastern/Western
  Highlands/Lowlands` forms, and both `Mun-Tuy Cellars` and `The Mun-Tuy
  Cellars`. Both of those turn out to be harmless - `Coerthas` is a real
  distinct client zone and the Mun-Tuy pair folds to one zone - but 5 strings
  name sub-areas rather than zones, and one GE zone name can map to several
  client zone ids because 1.0 duplicated field zones. Use
  `zone-client-crosscheck.csv` rather than the raw strings as keys.
- **`behavior_flags` is a six-code vocabulary spread over three tiers** - `A`, `P`,
  `S`, `H`, `TH`, `L` - and the tier that carries most of it is the family page,
  not the sighting. A blank on a mob row means "inherit the family", not
  "unknown", which inverts the empty-means-unknown rule below for this one field.
  Use `mob-behavior-resolved.csv`, which applies GE's own precedence and covers
  780 of 824 mobs, rather than either raw column. The sighting tier only ever
  carries `A` or `P`. The codes are defined in `mob-behavior-codes.csv`, harvested
  from GE's own `Template:Mob Notes-*` pages and pinned by revision id; those
  revisions are ARR-era, so the letter meanings carry to 1.x but the mechanic
  detail on them does not.
- **`aggressive` in `mobs.csv` is a dirty boolean and is not a negative claim.**
  Truthy spellings are `x` (212), `Y` (205), `Yes` (76), `y` (5), `A` (5), `^` (2);
  the 319 empty cells include 90 mobs whose family is aggressive, so empty does
  not mean passive.

## Evidence gaps

- The corpus itself is not in this repo (see the manifest `retention.note`), so
  the CSVs cannot be regenerated on a checkout without the local staging
  directory. They are committed as the canonical product for that reason.
- Only four template families were mined. Quests, guildleves, recipes as their
  own pages, NPCs, achievements and shop inventories are all present in the
  corpus and are **not** extracted here.
- The behavior-code definitions in `mob-behavior-codes.csv` are current-GE
  revisions (2017-2022), not 1.0-era ones. The letter meanings are corroborated
  back to a 2010 revision of `Template:Monster Notes`; the mechanic specifics on
  those pages are ARR-era and are not 1.x evidence.
- Sparse columns are sparse because editors left them blank, not because the
  value is zero: `magic_defense` has 20 rows, `gender_restriction` 100,
  `fits_races` 101, `required_rank` 133, `output_bonus` 140. An empty cell is
  unknown, never zero.
- `hp_low` / `hp_high` are present for 458 of 824 mobs; `mp_low` / `mp_high` are
  sparser still. Community-measured, no sample sizes given.
- No per-page Wayback snapshots exist. If Gamer Escape goes down, the local
  corpus and these CSVs are the only copy on hand.

## Derived from the client join

`items.csv` was joined by English item name to the client item tables in
`<client-data-csv>` to name their bare-integer columns. That produced
`client-column-map.csv` plus the two mismatch lists; read
`client-column-map-notes.md` for the method, the confidence bands and the
per-column verdicts. Headline results over 299 rows: 16 named from GE, 120
bonus-stat slot ids named from the client's own `xtx_text_paramName.csv`, 37
high-quality bonus rows, 25 set-bonus rows, 25 more through a +1,000,000 offset
that marks consumable on-use effects, 30 from client structure alone (equip kind,
race/gender restriction, crafter and gatherer tool base stats), 28
slot-machinery columns and 18 dead in 1.23b, with none left unidentified. The run prints
that breakdown on its `by origin` line, which is the copy to trust.
`itemData.140` proved to be a key into the client's `materia.csv`, so that table is
decoded as its own pair of artifacts (`materia-column-map.csv`,
`materia-decoded.csv`) with method and gaps in `materia-notes.md`. GE's
`materia_effect` and `meld_slots` are reachable only through it, and its
`materia_catalyst` through `itemData.65`.

6 of GE's 68 fields have no client column, and all six are now closed with a
reason rather than a blank: `base_item` and `base_material` are the row's own
recipe ingredient restated (0.9936 and 0.9243 of rows with a recipe contain the
value verbatim in `recipe_templates_raw`), `dye_colors` is a family of sibling
item ids rather than one item's property (the client ships every listed colour as
its own item on 0.9404 of rows), `hq_effect` is the HQ grade suffix the client
renders from a macro, and `convertible` and `magic_defense` were searched
exhaustively. See `client-column-map-notes.md`.

`equipment.77/78` is the exception inside the slot run: it is the high-quality
bonus, the attribute and amount HQ adds over normal quality. A downstream
reference consumer reads it directly for the High Quality row on its
item pages.

`mobs.csv` got the same treatment and the result is a negative one worth knowing
before planning work: the client ships mob names and models and **no mob stats**,
so there is no mob column map. 812 of 824 mobs resolve to a client actor-class
id, and the 89-name `xtx_monsterRace` taxonomy **is** linked to individual mobs -
not through any column, but through the actor id itself, whose digits 3-5 are the
race id offset by 1000. That pairs 68 of GE's 72 families to a client race at
0.9943 purity, against 48 by name matching, and it is the mapping to use;
`mob-race-crosscheck.csv` carries it. Note that races 1011 and 1076 are both
`Crab` in English and are different families, so join on the id. Nine further
race-field values form a second namespace no client table names
(`mob-race-blocks.csv`): five are faction or organization rosters - the Garlean
legion, a second Amalj'aa garrison, brigands, pirates, the Serpent Reavers - and
four are not. 1110 is the race Atomos missing from this dump's `xtx_monsterRace`;
1890 is scripted-fight opponents; 1900 is 98 friendly combat NPCs rather than
monsters (hamlet militia and story allies, the other side of the imperial block
1800); 1910 is five runtime-named actors.

The *stats* are still unreachable:
`level_low`/`level_high`/`hp_low`/`hp_high`/`element`/`aggressive` have no client
counterpart and cannot be corroborated from client-data. The per-mob family is no
longer in that position - it now has one. Behavior flags are in the same position, so they were resolved
across GE's own three tiers instead: `mob-behavior-resolved.csv` covers 780 of
824 mobs. Method and rosters: `mob-client-crosscheck-notes.md`.

For the 270 client mob names GE simply never wrote up, `mob-gap-brackets.csv`
interpolates a level bracket and a zone shortlist from each name's documented
actor-id neighbours. It is **a target list, not evidence**: right 53% of the time
on level and 55% on zone leave-one-out, about 12 points better than picking any two
mobs of the same race. Do not read a bracket back as a mob's level. The same file
records where each actor sits in its race id run: GE coverage thins along the run,
so undocumented actors sit at median position 0.644 of it against 0.467 for the
documented, which is why the last 48 cannot be bracketed at all. And note the scope
of "no GE page" throughout: the corpus is a 1.0 mob-and-item harvest, so a story
boss filed as a character article - Nael van Darnus, Good King Moggle Mog XII - is
absent from it without the wiki having missed it.

One mob hint here is strong rather than indicative: an actor id in the `23` allocation
band means level 35 or above, holding on all 45 documented mobs that have one, and 18
undocumented names inherit it through `band_level_floor`. It is a floor, not a bracket.
The reason is that the band is instanced content - 43 of 47 of its documented mobs are
sighted only in the Dzemael Darkhold, Toto-Rak, Cutter's Cry or the Aurum Vale - so
`band_zone_hint` places those 18 names at 0.828 accuracy from 2 candidates, the strongest
zone statement in this set.

The band itself is now read: **the digit is a spawn container** - 21 persistent, 22
guildleve-or-quest, 23 instanced dungeon - published as `spawn_container` on
`mob-client-crosscheck.csv` and `mob-gap-brackets.csv`. 277 of 280 documented band-22
mobs are sighted only inside a leve or quest against 12 of 376 in band 21, and 223 of
GE's 248 sighting tags are an exact cell in the client's own `xtx_guildleve` /
`xtx_quest` names. Read it as what kind of content spawned the mob, not as a level or a
zone: **169 of the 270 gap names are leve content**, which is why they were never written
up, and it says nothing about their level or spawn point.

`leve_candidates` on the same file names the *leve* a band-22 gap mob likely belongs to,
flanked from its nearest tagged band-22 race-mates: **0.516 from 2 candidates against a
0.319 random-pair null**, on 117 of the 169. Second-strongest hint in the set after the
band-23 dungeon pairing, and still a target list rather than evidence - the one case with
a known answer, `Frenzied Aurelia`, it gets wrong. A tag-independent corroboration of the
band sits beside it: band-22 mobs span 10+ levels 0.480 of the time against 0.018 for
persistent ones, and 97 of those 120 spans are a multiple of 4.

`leve_one_sided` is the weaker sibling for the 45 names flanked on one side only: 0.238
against a 0.177 null, published in a separate column precisely so it is not read as the
0.516 one, with `leve_basis` giving the reason per row. 7 band-22 gap names get neither -
their race has no tagged band-22 mob to interpolate from at all.

`client_leve`, on both mob tables, is the one leve statement here that is not an
interpolation: the client's own `xtx_guildleve` briefing text names the mob, attributing
**110 mobs to a named leve** and agreeing with GE's tag on 33 of the 37 where both exist.
Prefer it over `leve_candidates` and `leve_one_sided` wherever it is filled. It is still not
a container claim - 14 of the 110 are persistent-only mobs, every one of them a species word,
and every one read in the notes as prose rather than a target. Independently, the triage causes
in `client-mobs-without-ge-page.csv` line up with the band digit they predate: `not-a-monster`
and `mount-or-companion` are 100% band-22, `placeholder` and `second-roster-filler` 0%.

**Never derive a mob name from its actor id by arithmetic.** 1,587 of 2,662 mob actors have a
display-name id that parallels the actor id, but 26 pairs *transpose* theirs - `crab` carries
`beryl crab`'s expected row and vice versa - so the shortcut returns the wrong mob's name
rather than no name. Follow the pointer in `actorclass.csv` column 6.
`mob-name-id-transpositions.csv` lists all 26 pairs; the variant distance is only ever 1, 2 or
4, 6 of them are race 1002 reordering a block, and one displays `kobold` either way. Every
pair is within one race and one band; only 8 of the 26 have names a string test can relate, so
read the ids, not the names.

`client_quest` is its quest-side twin, read out of the client's regional journal sheets rather
than the leve table: 115 mobs attributed, 24 of 25 agreeing with GE's quest pages. **The two
are not interchangeable** - all 29 leve attributions that name an individual hold a band-22
actor, but only 38 of 55 quest ones do, because quests reuse the persistent field population
while leves spawn their own.

**Read `client_proper_name` beside it.** A briefing that names an individual is an exact
attribution (11 of 11 against GE); one that uses a species word - `balloon`, `basilisk`,
`aurelia` - is 22 of 26, because the noun is generic. And the container reading survives the
source swap: folding in only the attributions that name an individual leaves band 21 at
exactly its GE-only 0.032, with bands 22 and 23 unchanged, so the split is not an artefact of
what GE wrote down. Folding in the species-word half as well moves band 21 to 0.061, and
those 12 additions are the scan reaching a base-species actor through a briefing that
describes its target by what it is - not evidence a leve spawned them.

One caveat that block 1800 makes concrete: **GE files by mob name, and one name can own
actors in several id bands and several deployments**, so its `zone` list is the union over
all of them and cannot be split back per actor. Do not read a multi-zone GE mob as one
that roams; it may be three separate deployments sharing a rank name.

And the hard boundary behind every mob hint here: **the client dump contains no
actor-to-zone, actor-to-spawn or actor-to-level table.** All 803 files were searched for
monster-range actor class ids and only `actorclass.csv` and `actorclass_graphic.csv` carry
them. Note also that a display-name id is not a transform of an actor id - the 2-to-3
parallel fails for 1,075 of 2,662 mob actors - so follow the pointer, never compute it.

**A fourth GE tier is now mined: quest pages.** `mob-quest-attribution.csv` names the
quest that 71 undocumented client mob names appear in, 35 of them ordinary gaps. All 273
quest pages in the corpus were last edited in 2011 or 2012, which makes them the only GE
material in this set that is unambiguously contemporaneous with 1.x - better provenance
than the ARR-era behavior-code templates. Caveats: only the attribution is stored, never
the walkthrough prose, and `race-name-only` rows are unreliable because a species word
appears in quest prose for reasons unrelated to any one mob.

The same file's `quest_level_floor` is the quest's `Minimum Level`, and it is the strongest
level statement in this set: the mob's own level_low is at or above it on 0.898 of documented
pairs, within 10 above on 0.754. Treat it as a floor, never as the level, and ignore it where the
file leaves it blank - it is withheld from lower-case one-word names, story NPCs and species
words on measured grounds, and `client_proper_name` records the signal it turns on.

`mob-locations.csv`'s zone strings were classified the same way: 43 of 51 are
real client zones covering 1,429 of 1,501 sightings, 5 name sub-areas that are
not zones, and 3 are guildleve or instance labels. `Coerthas` is settled as its
own client zone (146) rather than a grouping label. See
`zone-client-crosscheck-notes.md`, which also records two defects it surfaced in
the historical external zone roster consulted at research time.

## Further research

- A 1.x item-availability timeline remains uncompiled. `patch_introduced`
  provides its seed, and the sub-patch rows (1.19a, 1.20b, 1.22b, 1.22c)
  require comparison with the `lodestone-dev-patch` study before they are treated
  as settled.
