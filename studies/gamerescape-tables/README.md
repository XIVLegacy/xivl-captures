# Gamer Escape FFXIV 1.x Item and Mob Tables - Web Tables

## Study contents

The Gamer Escape FFXIV wiki's 1.0-era item, mob, and NPC data was mined from raw
wikitext into normalized CSVs: **5,665 items**, **824 mobs**, **1,501 mob
sightings** across 51 zones, the **52 mob families** those mobs inherit their
defaults from, and **1,333 NPCs** with their race, clan, occupation, and
coordinates. This is web-source evidence at the **wiki tier** (packet captures >
video breakdown > wiki), so the values are CALIBRATION-grade.

For item and mob names, ids, and much of the numeric stat block, check
`xivl-client-data` first: those values are shipped by the client and are primary
evidence there. This study adds two fields that no live FFXIV wiki documents:

- **`patch_introduced`** on 1,087 items, including the sub-patches **1.19a,
  1.20b, 1.22b and 1.22c** that no longer appear anywhere else.
- **`removed_before_arr`** on 2,593 of 5,665 items (46%), read from the source
  page's `Obsolete` / `PhasedOut` template - the 1.x-only item population that
  has no ARR-era equivalent to look up.

## Start here

- `derived/evidence-map.md` - tier and version caveats, the unique-value fields, and every
  dirty-data pattern (unnormalized booleans, mixed `hq_effect`
  vocabularies, undocumented `behavior_flags`). Read this before using the CSVs.
- `derived/items.csv`, `derived/mobs.csv`, `derived/mob-locations.csv`,
  `derived/mob-families.csv`.
- `derived/client-column-map-notes.md` - if you are here to read the client's own
  item tables. It names the bare-integer columns of `xivl-client-data`'s
  `weapon` / `armor` / `itemData` / `equipment` / `_item` sheets by joining this
  set's items to them on English name.
- `derived/materia-notes.md` - if you are here for materia. The client's
  `materia.csv` is decoded outright into `derived/materia-decoded.csv`: which stat
  each line grants, its magnitude per grade and rank, and what it melds into.
- `derived/mob-client-crosscheck-notes.md` - if you are here for mobs. Records
  that the client ships no mob stats, so these tables are the only source for
  1.x mob levels and HP.
- `derived/zone-client-crosscheck-notes.md` - if you are here for spawn zones.
  Classifies every sighting-zone string against the client's zone roster.
- `derived/npc-client-crosscheck-notes.md` - if you are here for NPCs. `npcs.csv` is the
  best-dated GE material in the study (263 of its 1,335 pages last edited in 2010) and the
  only source here for an NPC's race, clan, occupation and coordinates.

## Source material

**`raw/original/` is empty and stays empty.** The GE wikitext is not in this
repo: Gamer Escape is a permitted factual baseline, but verbatim GE prose and
bulk imports of GE pages as-is are excluded. An 11,227-page wikitext mirror is
exactly such a bulk import. The source corpus remains outside repository
history; only the normalized products below are public.

The CSVs under `derived/` are the canonical, self-contained product.
`derived/checksums.sha256` anchors them rather than any raw original. They are
promoted evidence: mined from the GE wiki table corpus by walking
brace-balanced `{{Infobox Item}}` / `{{Infobox Mob}}` / `{{Mob Row}}` /
`{{Infobox Mob Family}}` calls and splitting depth-zero params, and verified
against `derived/checksums.sha256`.

`derived/file-inventory.csv` records generation provenance. The verification
guarantees referenced throughout this README and the derived notes describe the
checks used to pin each value. Current bytes are anchored by
`derived/checksums.sha256`.

## Promoted conclusions

The canonical derived CSVs supply downstream reference work with item
availability, mob, NPC, and zone evidence. The client joins also promoted named
item-table columns,
decoded materia fields, and client-keyed mob and zone cross-checks for reuse.

## Client column map

`items.csv` was joined by English item name to the 1.23b client item tables to
name their columns, which ship as bare indices with a type row and no field
names. The join is verified over 11 hand-checked values across three items
(Alesone's Songbow for the ordinary numeric columns, plus Storm Sergeant's
Hoplon and Bronze Buckler for the two dedicated slot pairs below), and holds
two structural invariants: no HQ or set-bonus row carries a GE field, and no
two-valued column reaches high confidence without recording the GE baseline it
beat. The verified result is `derived/client-column-map.csv` plus the two
mismatch lists.

The map is 299 rows. The breakdown by what named each column was 16 from GE, 30
from client structure, 120 bonus-slot ids named from the client's own
`xtx_text_paramName.csv`, 37 high-quality bonus rows, 25 set-bonus rows, 25
more through a +1,000,000 offset that marks consumable on-use effects, 28
slot-machinery columns and 18 dead in 1.23b. **Nothing is left
unidentified.** Method and per-column verdicts:
`derived/client-column-map-notes.md`.

The six tables are slices of **one shared column space**: every populated column
index is owned by exactly one table, so a column number alone identifies a field
(`116` is armor's defense, `141` is weapon's). Row membership nests by item kind
instead of partitioning - all 278 accessories also have rows in `weapon.csv` and
`armor.csv`, where they carry filler - so read `equipment.69` to learn what an
item is, never which table it appears in.

Three of the client's own dialogue tables were audited against the map and settle
things GE cannot: `populaceShopSalesman.csv` defines the class-affinity ladder
(`itemData.48` is `1001` for all classes, other `1xxx` for **Favors** - equippable
by anyone but full stats only for the listed classes - and `2xxx` for **Requires**,
a hard gate), and fixes Condition as a cliff rather than a slope: **Gear Damage**
at 10% costs nothing, **Heavy Gear Damage** at 0% removes all benefits.
`populaceItemRepairer.csv` names the repair gating, and the two materia files carry
the melding rules. Details in `derived/client-column-map-notes.md`.

The following client findings are not documented elsewhere.
`equipment`'s ten bonus-slot pairs are **not** ten interchangeable slots: the
first four are dedicated and only 79/80 onward is the worn-stat run.

- `equipment.77/78` is the **high-quality bonus** - the attribute and the amount
  HQ adds over normal quality. GE names the attribute on ~500 items and gives the
  amount on none.
- `equipment.71/72` is the **condition** of a conditional bonus (grand-company
  set count, `Sanction`) and `73/74` is the **stat that condition grants**. GE
  confirms none of those 93 values as a worn stat.
- `armor` ships a **four-slot bonus run of its own and never uses it** - all four
  ids are -1 on every one of its 3,599 rows, because equipment serves armor
  bonuses instead. `weapon`'s damage-type run has the same shape: slot 1 only.

## Materia

The client uses `itemData.140` as a key into its own `materia.csv`, which holds
the whole of 1.0 materia. It is decoded as its own artifact,
`derived/materia-decoded.csv`:

66 lines, each with four grade item ids, a primary parameter and 16 magnitudes as
4 grades x 4 ranks, an optional second parameter with 16 more, one icon per grade, and
38 booleans for the equipment it melds into. GE's `meld_slots` names 27 of
those booleans; the 11 secondary-tool columns are byte-identical and cannot be
told apart by any test, so they carry a positional label only.

The catalyst is not in `materia.csv` - it is on the item, in `itemData.65`, which
holds an `-ized Matter` id on materia rows and a Dark Matter repair grade on gear.
The rules themselves are in two text files, neither of which has columns to map:
`materiaBook.csv`, the in-game materia tome (52 rows of localized prose - the only
source for spiritbond, catalyst gathering and the multi-meld penalty), and
`populaceShopMateriaRemover.csv`, Mutamix's shop dialogue (25 rows), which adds
that the **first meld never fails** and which never mentions the gil purge fee the
tome asserts. All of it is written up in `derived/materia-notes.md`.

## Mob crosscheck

The mob side has no column map, because the client ships mob names and models and
**no mob stats at all**. It resolves 812 of 824 GE mobs to a client actor-class id, lists the 12 that miss
(8 are GE misspellings the client contradicts), the 468 client monster names with no
GE mob page, and both family rosters. GE covers **63% of the 1,277 distinct client
monster names**, and each of the 468 carries a `likely_cause` - only **270 are
ordinary GE gaps**; the rest are faction rank-and-file, the 1900 NPCs, the chocobo
roster, 34 actors named only after their species, and **10 named boss-tier actors
whose siblings GE does document** - `Arges` and `Brontes` beside the documented
`Steropes`, `Chirada` and `Suparna` beside `Garuda`. Those 10 are the part of the gap
worth acting on. GE's mob levels, HP, element and
aggression have no client counterpart and stay this study's own evidence - see
`derived/mob-client-crosscheck-notes.md`.

**The actor id encodes the monster race.** `2100112` is race `1001` (Puk) variant
12, so `race_id = 1000 + digits 3-5`, and 699 of the 812 joined mobs resolve to one
of 78 named races at **0.9943** purity against GE's `family`. That replaces the
string-similarity guess the family rosters used to rely on: **68 of GE's 72
families pair to a client race, against 48 by name matching**, including pairs that
share no letters (`Rodent`/`Rat`, `Landtrap`/`Flytrap`, `Cactuar`/`Sabotender`,
`Fomor`/`Zombie`) and six the client only names in Japanese. The full many-to-many
pairing is `derived/mob-race-crosscheck.csv`.

Two client races are both `Crab` in English and are different animals - 1011 is
GE's `Diremite`, 1076 is GE's `Crab` - so **key the taxonomies on the race id, not
the name**. `--verify` fails if anything reverts to a name join.

Nine race-field values are not in `xtx_monsterRace` at all, covering 567 of the
2,662 monster actors, and they group by **faction** rather than species -
Garlean legion, brigands, ordinary pirates, and the Sahagin-sworn Serpent Reavers
whose claw / fin / eye are ranks rather than body parts. **A block is an allocation,
not a closed set**: the Amalj'aa span race 1065 and block 1620, and the lunatic cult
spans blocks 1801 and 1803, so same-block does not mean same-group. Two more are not
factions: **1620** is a
second Amalj'aa roster named by office and stronghold rather than by job, and
**1890** is the scripted-opponent block - job-quest champions, coliseum challengers and duel
squads, 93% of its GE mobs notorious against a 12% baseline. The 1620
interpretation rests only on naming, since every member is one species. The 1890
interpretation is measured and gated.
GE proves the distinction: it files 95 of its 113 such mobs as one family,
`Enemy Humanoid`, while its `subfamily` gives a playable race that varies inside
every block. `derived/mob-race-blocks.csv` records all nine with `client_names` and
`humanoid_actors` shape columns;
no client table names them. Two are not blocks: **1110 is the race Atomos**, missing
from this dump's table - 24 actors under one display name, the shape of the primal and
single-creature races, sitting immediately past the table's last row - and
**1910** is five humanoids named at runtime - all five point at the client's
`kahen` variable-name sentinel, not at a missing translation. One block is not monsters at
all: **1900 is 98 friendly NPCs that fight** -
hamlet militia, Grand Company scouts, story allies and escort targets - so the
actor-id range is not a sufficient mob filter, and 52 entries in
`client-mobs-without-ge-page.csv` were never GE's to document. `populaceWaveAttack.csv`
ties 1900 and 1800 together as the ally and enemy sides of the hamlet-invasion
content, which corroborates the interpretation of 1800 as imperial.

**1800 itself is one rank ladder deployed five times.** Seven Roman line ranks - secutor,
hoplomachus, laquearius, eques, sagittarius, medicus, signifer - in three tiers over 117
actors, and it is the tier plus the rank family that picks the deployment, not the id
band: `imperial` line at level 50-55 and `elite` line at 56 hold Castrum Novum,
`VIIth Legion` adds Mor Dhona, the `imperial` skirmish ranks hold East Shroud and the
Dzemael Darkhold, and the `elite` skirmish ranks roam four field zones as the
hamlet-invasion attackers. The level is near-constant inside each group. **GE is missing
`sagittarius` in all three tiers** - the client has 7 of 7 in each, GE has 6 of 7 in each, and
the omission is the same rank every time across 12 client actors, which is a hole in
GE's roster rather than an oversight. `--verify` gates the ladder, the absentee and the
actor count it was measured over. Race **1070** is the same faction's other namespace,
holding the officer ranks - centurion, pilus prior, primus ordinarius - over 13 actors,
the way the Amalj'aa split across race 1065 and block 1620.

Two client constraints from the 1800 sub-run bound these findings. **A display-name id is
not the actor id with its 2 turned into a 3** - that parallel holds
for 1,587 of 2,662 monster-range actors and fails for 1,075, and the name table has rows no
parallel actor claims, so an id must never be transformed instead of followed. And
**nothing in the dump links an actor to a zone, a spawn or a level**: all 803 client files
were searched for monster-range actor ids and only `actorclass.csv` and
`actorclass_graphic.csv` carry them. Every zone and level statement in this study comes from
GE, which is why they are hints.

The quest corpus adds **a fourth GE evidence tier not represented in the tables**.
`imperial centurion` has no mob page because GE wrote it up inside a quest - `Futures
Perfect`, whose objectives are to chase one through an instance, and whose walkthrough also
names the Hoplomachus and Sagittarius escorting it, corroborating the sagittarius hole from
GE's own prose. `derived/mob-quest-attribution.csv` generalises it: **71 of the 468
undocumented client names are mentioned in one of GE's 273 quest pages**, 35 of them
`ge-gap`, and the page names the content rather than interpolating from other mobs. All 273
pages were last edited in 2011 or 2012, so unlike the ARR-era behavior-code templates they
are contemporaneous 1.x observation. Only the attribution is stored, never the walkthrough
prose. The corpus is local only, so this one output is skipped rather than emptied when it
is absent.

The quest infobox provides **the strongest level statement in the set**. `Minimum Level`
is filled on 263 of the 273 pages and behaves as a floor: the mob's
own `level_low` sits at or above it on **150 of 167 documented pairs (0.898)**, within 10
levels above on 0.754, median +5. That beats the flanking bracket's 0.530 inside a 10-level
band, and unlike it the figure comes from the content the mob appears in rather than from
interpolating between other mobs. It supplies 50 `quest_level_floor` rows, 28 of them
`ge-gap`; six names no bracket could reach now have a level - including `nael van darnus` and
`good king moggle mog xii`. Eligibility turns on the client's own
capitalisation rather than word count: a one-word name the client capitalises holds the
floor 0.867 of the time, one it writes in lower case only 0.595, so `Audhumbla` and
`Coincounter` qualify and `bloodhound` and `shrieker` do not. Story NPCs and species words
are excluded whatever the casing, because the floor is a claim about a mob's level.

The 270 names left after that triage are ordinary mobs in races GE covers, and
`derived/mob-gap-brackets.csv` gives each one a level bracket and a zone shortlist
interpolated from its documented actor-id neighbours, plus how the name sits against
documented siblings of its own race (146 share a head noun with one). **The hint is
weak and is labelled as such**: leave-one-out over the documented mobs it is right 53%
of the time on level and 55% on zone, which beats picking any two same-race mobs by
about 12 points, so it is a prioritised list of retail-observation targets and not
evidence. `--verify` gates the lift over that null rather than the raw accuracy, and
counts leave-one-out tests contaminated by the mob under test - the leak that made this
look 84% accurate. Two alternative interpretations of the names were tested and
rejected: place prefixes like `Bloodshore` are real but cannot be told from ordinary
adjectives by any vocabulary in reach, and the actor-id sequence is **not** a level
ladder (an id pair is in level order 59% of the time).

The 48 names with no bracket are the far end of a measurable gradient rather than a
class of their own: **GE's coverage thins along each race's id run**, so its undocumented
actors sit at median position 0.644 of that run against 0.467 for the documented ones,
39% of them in the last quarter against 22%, and 17 own the highest actor id their race
was ever given. `bracket_basis` and `race_run_position` carry this per row, and
`--verify` holds the two medians at least 0.10 apart. A one-sided single-neighbour hint
was measured for them and rejected - a lift of 0.036 on level, under the same 0.05 floor
- so those cells are blank by decision rather than omission. This analysis also sets a
scope caveat for the whole 468: the corpus holds no page at all for `nael van darnus`,
`good king moggle mog xii` or `sabotender alegre`, so "no GE page" means "not in a
harvest scoped to 1.0 mob and item content", not that the wiki never documented them.

Among the 17 names that own the highest id in their race, **Ten of the 17 are in the `23`
allocation band**, which is by construction the numerically highest band a race can use.
This confounds the gradient: "late in the run" and "in the 23 band" overlap. Measured
within a single band, the medians are 0.556 against 0.472, half the 0.178 seen across
bands. The 23 band is **a level floor rather than a correlation** - every one
of the 45 documented
mobs holding a 23-band actor tops out at level 35 or above, and the 38 in a named race
also start there. `band_level_floor` carries it for the 18 gap names with such an actor,
15 of which had no hint at all, and `--verify` fails on any documented counterexample.
The lone mob starting lower, `Imperial Speculator` at 22 to 52, is in the Garlean block
rather than a named race. The 23 band also selects for **instanced content**, which explains
the floor: 43 of the 47 documented band-23 mobs
carrying a zone are sighted in nothing but the Dzemael Darkhold, the Thousand Maws of
Toto-Rak, Cutter's Cry and the Aurum Vale, and all four exceptions are the Garlean legion
at Castrum Novum, itself an instanced battle rather than a zone. 20 of the 25 races with a
band-23 sighting pin to exactly one dungeon, so `band_zone_hint` predicts a mob's dungeon
from its race at **0.828 from a median of 2 candidates** - against 0.545 from 2 for the
general flanking hint. The roster is derived from the sightings rather than written down;
`--verify` holds the band 90% inside its own top four zones.

The other two bands show that **the band digit is a spawn container**, and a mob actor id
is `2 | band | race | variant`. 277 of the 280 documented
mobs whose actors are all band 22 are sighted only inside a guildleve or quest, against
12 of 376 in band 21 and 0 of 41 in band 23, and **223 of GE's 248 distinct sighting tags
are an exact cell in the client's own `xtx_guildleve` or `xtx_quest` names**, so the
correlate is client content rather than a wiki grouping. It is a container and not an
overflow page: all 82 races holding both a band-21 and a band-22 actor restart their
variant numbering in each band, and the fullest band-21 race stops at 73 of 99. `--verify`
gates the tag share in both directions, puts a synthetic continuing race through the
renumbering test, and requires the client's own quest tables to reference band 22 and
nothing else - which they do, on 7 references over 2 actors. That is too thin to carry the
finding but points in the right direction. `spawn_container` is published on both the
crosscheck and the gap table. **169 of the 270 gap names hold a band-22 actor** - the
largest single reason GE never wrote them up. The 23-band level floor and dungeon shortlist
are now readable as properties of dungeon content rather than of a number.

For the three sighted band-22 mobs to which GE attached no leve, `Frenzied Aurelia` is
settled by GE's own `Notes` - it "Spawns as part of the Limsa Lominsa Main
Scenario Quest Shapeless Melody", an exact client quest name - and the other two by
**the level span, which owes nothing to the tag column**: a
band-22 mob spans 10 levels or more 0.480 of the time against 0.018 for a persistent one, and
97 of those 120 wide spans are a multiple of 4, the shape of an evenly stepped
difficulty ladder. `Gorged Djigga` at 24 and `Hairless Hare` at 28 sit in that
distribution. Both also sit inside a run of tagged leve mobs of their own race, which
generalises into `leve_candidates`: flanking a band-22 name with its nearest tagged
band-22 race-mates names a leve at **0.516 from 2 candidates against a 0.319 random-pair
null**, the second-strongest hint in the study, published for 117 of the 169 band-22 gap
names. The one case with a known answer is one it gets wrong, and that miss is pinned as a
fixture rather than smoothed over.

For the 52 names that the level hint cannot reach, **the one-sided flank clears the gate
the level side failed**: over the 185 documented points that genuinely have
a single neighbour it names a true leve 0.238 of the time against 0.177 for any tagged
race-mate, a lift of 0.061 where the level bracket's one-sided form managed 0.036. So 45 of
the 52 carry `leve_one_sided`, in its own column so 0.238 and 0.516 are never mixed, and
`leve_basis` records why a row has one and not the other - 31 above their band's documented
high, 14 below its low, 7 in a race where GE tagged no band-22 mob at all. The all-point
measurement reads 0.358, which still
clears the floor and still sits under the flanked hint, so `--verify` puts a four-point
control through the function rather than trusting the real data to notice.

The remaining 7 names are in races GE tagged nowhere. **The client's own leve briefings
name mobs**: `xtx_guildleve`
column 11 is the English leve name and column 15 the English objective; 610 rows carry both,
with 167 of those briefings naming a client mob. `client_leve` on both mob tables attributes
**110 mobs to a named leve from the client**, agreeing with GE's tag on 33 of the 37 where
both exist, and reaching 66 documented mobs - 29 of which GE never tagged - plus 19 gap
names, 4 of them with no other leve statement at all. A mention is a strong band signal and
not a proof, so it is gated inside `[0.80, 1.0)`: 96 of the 110 hold a band-22 actor, and
the 14 without one are examined below.

None of the 7 names appears in a briefing. Two are attributed a tier up -
`mob-quest-attribution.csv` puts `goblin
robber` in `Losing One's Thread` and `hellhound` in `Arms Race` - so **5 names are left with
no GE tag, no quest page, no tagged band-22 race-mate and no client briefing**. They are the
first in this study to be exhausted rather than weakly hinted.

Client attribution for the **29 documented mobs the client attributes and GE never tagged**
exposes a defect in that column: most are species words, not individuals - `Balloon`,
`Basilisk`, `Cactuar`, `Aurelia`, `Roseling` - and a briefing saying "a pack of ravenous
marmots" is using the noun rather than naming the actor. Split on the client's own
capitalisation and one agreement figure becomes two: **11 of 11 where the briefing names an
individual, 22 of 26 where it uses a species word**. `client_proper_name` on the crosscheck
says which kind a row is, with a floor on each and a margin between them.

This attribution also provides the strongest check on the container interpretation, which
previously rested entirely on GE's tag column. **Folding the client's own attribution in as a second
tag source does not overturn it**: band 21 moves 0.032 to 0.061, still well inside its 0.10
ceiling, band 22 stays at 0.989 and band 23 at 0.000.

The 12 persistent-only mobs behind that rise explain the discrepancy. **All 12 are species
words** - `Balloon`, `Basilisk`, `Cactuar`, `Sundrake` - reached because
a leve briefing describes its target by what it is: `Wanted: Coiled Adder` mentions
sundrakes, and the scan lands on the persistent base-species actor. So the rise was an
artefact of the scan, not leves sending players after persistent mobs. **Fold in only the
attributions where the client names an individual and band 21 returns to exactly its GE-only
0.032** - a stronger agreement between the two sources than the mixed figure showed. All 29
of those individual attributions hold a band-22 actor, no exceptions, and every one of the
14 with no band-22 actor is a species word. `--verify` gates both, plus the GE-only shares;
it fails if the mixed merge adds no band-21 mob GE had missed, since a swap that changes
nothing tests nothing.

The 15 mismatches reveal one real bug and six kinds of prose. **`cassiopeia` was a place,
not a mob** - all 13 of its attributions were
briefings naming `Cassiopeia Hollow` - so the client's own 907 place names now join the scan as
decoys that win positions without being attributed. That also caught `kobold`, attributed
through a "kobold garrison". Attributions go 111 to 110 with agreement unchanged. Of the
rest, **7 are the briefing naming a species while the leve spawns its own band-22 variant** -
every one of those races holds band-22 actors, `frightened cactuar` and `bloated
burble` among them, so they support the container interpretation rather than contradicting it. The
remainder is prose no scan can read: a carnival sideshow list, a hunt's backstory,
"zombie-like creatures", and "Ixali Battle Balloons" where `battle balloon` is not a client
mob name.

The **quest** side requires a different field. `xtx_quest` column 7 is the English
description and is the wrong field - it attributes 12 species words whose single
GE-checkable case disagrees outright. The objectives live one indirection away, behind
`[@SHEET(xtx/journalxtxWil,383,1)]` macros into four regional journal sheets whose column 1 is
English: **273 quests with objective text over 1,585 entries**, attributing **115 mobs and
agreeing with GE's quest pages on 24 of 25**. `client_quest` carries it on both mob tables.

The two sources differ on an important point. Among individual-name attributions - the half
worth trusting - **all 29 leve attributions hold a band-22 actor and only 38 of
55 quest attributions do**. 17 named individuals are quest targets with no leve deployment at
all (`Audhumbla`, `Cactuar Jack`, `Daddy Longlegs`, `Gluttonous Gertrude`). **Quests reuse
the persistent field population and leves spawn their own roster**. `--verify` gates the margin
between the sources, since the distinction is the difference rather than either figure.

The remaining `dragon` attributions are explained by their briefing text. Its two briefings are
`Heat of the Moment`, where an airship
"attacked by a pair of dragons" outruns them and the leve is recovering the cargo it
jettisoned. `Nutritious Fishes` opens with "the effort spent slaying
deadly dragons and saving distressed damsels" as a figure of speech. Race 1068 is
`Dragon` and holds four
band-21 actors all named `dragon`, no variants - the bare race word a briefing reaches when it
means the noun. **So all 14 non-band-22 attributions are accounted for and none is a target**,
with `--verify` pinning the count so a fifteenth would violate the retained count.

The same comparison corroborates the triage causes in `client-mobs-without-ge-page.csv`,
which were assigned from names before the band digit was read. **The two meaning
"spawned by content" are entirely band 22** - all 52 `not-a-monster`
names and all 18 `mount-or-companion` ones - while the two meaning "roster artefact",
`placeholder` and `second-roster-filler`, are entirely band 21. All four are gated.

The three `race-name-only` names with no band-22 actor - `crab`, `dragon`, `zombie` - are
also accounted for. None is an unused shell: all three carry full
`actorclass_graphic` rows indistinguishable from their race-mates. **`dragon` belongs to a
class of four**: 12 of the 95 named mob races
hold exactly one distinct name, and only 4 never reach band 22 - race 1068 `dragon`, race 1110
`atomos`, and races 1101 and 1102 whose only name is `???`. Three of those four were already
recorded here as special, so `dragon` sits with set pieces and placeholders rather than field
rosters. `crab` and `zombie` are ordinary mobs in well-populated races that GE never wrote
up; both sit in an **actor-to-name transposition** - `crab` holds `beryl crab`'s expected name
id and vice versa, likewise `zombie` and `dapper cadaver` - one of 26 such mutual pairs. That
is the sharpest form of why a name must be read through the pointer: the arithmetic does not
fail loudly, it returns the wrong mob's name.

All 26 are published as `derived/mob-name-id-transpositions.csv` - both actor ids, both name
ids, both names, the variant distance. The shape is tight: **the distance is only ever 1, 2 or
4**, always within one race and one band, and **6 of the 26 are race 1002 alone**, the raptors,
whose first four actors trade name rows wholesale with its next four. One pair displays
`kobold` either way and so has no observable effect. The other 25 return a different mob's
name. The table carries no taxonomy column; neither candidate taxonomy produced a valid
bucket. **The only relation the client asserts is race, and every pair has it** - all 26 are
within one race and one band, now gated. Whether the two *names* look related is an
English-language question, and a string test answers it for only 8 of 26; the other 18
are 1.0 renaming inside a family
(`dapper cadaver` against `zombie`, `bomb baron` against `grenade`) or a notorious monster
against its species. There is no "unrelated" class.

The client has no behavior data, so the derived tables resolve each mob's
behavior flags across the three GE tiers that do carry them - the family category
page, the mob's own infobox, and each sighting row - into
`derived/mob-behavior-resolved.csv`, **780 of 824 mobs** against the 505 that
`aggressive` covers. The flags are a six-code vocabulary (`A` aggressive, `P`
passive, `S` sight, `H` sound, `TH` unshakeable sound, `L` links), not the
one-letter mystery they were recorded as, and a blank on a mob means "inherit the
family" rather than "unknown". `--verify` gates that precedence: of the 24 mobs
that override their family, 17 of the 17 cases the sightings can decide side with
the mob page, and reordering the tiers either way fails the check.

The codes are defined by GE's own `Template:Mob Notes-<code>` pages, none of which
are in the local corpus. All eight were harvested from the live wiki and are pinned by
revision id in `derived/mob-behavior-codes.csv`. `S` is sight and
`H` is hearing, `TS` / `TH` are their unshakeable forms, and `M` (magic) and `TS`
exist wiki-wide but on no 1.0 page. **The definitions are ARR-era revisions**
(2017-2022) against 2012 mob pages, so the letter meanings carry but the
`Aggressive` article's level threshold and ability names do not - see the notes.

## NPC crosscheck

`Infobox NPC` was the largest unmined family in the corpus. `npcs.csv` carries race,
clan, gender, occupation, affiliation, zone and coordinates for 1,333 NPCs - none of
which any client sheet ships - and 1,182 of them have map coordinates, the only
positional record here for 1.0's town population.

**1,272 of 1,333 (95.4%) join a named client actor** outside the monster ranges, and the
actor-id prefix is a real division: **prefix `16` is the merchant space**,
0.967 merchants against 0.030 for the general `10` population, with `15` mixed shop and
service staff at 0.227. `--verify` holds the purity and the contrast, since a floor alone
would pass if the whole roster became merchants.

The `xtx_displayName` table is **five-language** with a singular and a plural per language -
1 Japanese, 2/3 English, 7/9 German, 14/15 French, 20 Chinese. English alone made
21 GE NPCs look absent. **1.0's locales did not name Grand Company
NPCs the same way**: English shows a rank where French and German show the person, so
`Allond` is `storm sergeant allond` in English and `Brielle Allond` in French. 15 join once
the other locales are indexed, every one Grand Company personnel. Family names that stand
alone in no column (`Brooks` inside `Alain Brooks`) need the last word of each rendering
indexed as well.

The 61 unmatched NPCs split three ways, and the first is corroboration rather than a
gap: **34 `mob-range-actor`** whose actor sits in a monster range - 14 rental chocobos and
**the 12 hamlet militia supporting the 1900-block interpretation**, now attested from GE's NPC
roster and not just from the client's naming - **7 `no-client-actor`** that GE places in a
zone this dump has no actor for, and **20 `lore-figure`** with neither zone nor actor, the
Ishgardian saints and `Frandelont Raimdelle` among them. That last class is measured, not
assumed: 0.958 of joined NPCs carry a zone.

A surname guard precedes generic fallback matching: it maps `Storm Captain Roemannsyn` to
the client spelling `storm captain roehmannsyn`, and joins 7 names including GE's typo
`Bizzare Blacksmith`. Matching requires a unique winner above a 0.88 ratio. No current
real name is ambiguous.

On the mob side this settles two triage causes. `client-mobs-without-ge-page.csv` now says
when GE documents a name as a *person*: **53 of the 468 do**, and 47 are
`not-a-monster` or `mount-or-companion` - so the 1900 block really is friendly NPCs and
race 1105 really is the rental chocobos, GE giving every bird `race = Chocobo` and a zone.

## Zone crosscheck

`mob-locations.csv`'s 51 `zone` strings mix real zones, sub-areas and guildleve
names, so they are classified against the client's zone tables.

43 strings are real client zones covering 1,429 of 1,501 sightings; 5 are
sub-areas the client knows but that are not zones; 3 are not places at all. It
also resolves the `Coerthas` ambiguity - `Coerthas` is its own client zone
(146), not a grouping label - and records a cross-reference to
the historical external zone roster.
See `derived/zone-client-crosscheck-notes.md`.

## Topics

- item stats: defense, damage, `delay_seconds`, `wear_durability_points`,
  `resale_price_gil`, repair class/level, HQ grades
- materia: `materia_effect`, `meld_slots`, `meldable`, `convertible`,
  `materia_catalyst`
- crafting: `recipe_templates_raw` preserves the full `{{Recipe}}` wikitext for
  3,672 items
- mobs: superfamily / family / subfamily / subspecies, level and HP ranges,
  elemental weakness, aggression and detection codes, 106 notorious monsters
- spawns: zone, map coords, level range, drops, and the 1.x-only zones
  (`Locke's Lie`, `Rivenroad`, `Castrum Novum`, `Mistbeard Cove`,
  `Cassiopeia Hollow`, `Shposhae`, `Paglth'an`, `Natalan`, `Murmur Rills`)

## Evidence gaps

- Corpus is local-only, outside every repository history.
- Only four template families were mined - quests, guildleves, NPCs, shops and
  standalone recipe pages are in the corpus and are not extracted here.
- The behavior-code definitions come from current GE revisions, not 1.0-era ones.
  Their letter meanings are corroborated back to 2010, but any mechanic detail on
  those pages is ARR-era and is not 1.x evidence.
- `removed_before_arr` is item-side only: zero mob rows carry it, so an unflagged
  mob is not evidence the mob survived into ARR.
- Empty cells mean unknown, never zero. `magic_defense` has 20 rows,
  `gender_restriction` 100, `required_rank` 133; `hp_low` covers 458 of 824 mobs.
- Zone strings are not the canonical 1.0 roster, and 5 of the 51 name sub-areas
  rather than zones; `derived/zone-client-crosscheck.csv` classifies each one and
  preserves client ids and external roster ids imported at research time.

## Further research

- Two client-side interpretations remain unresolved and require a decomp of
  `ffxivgame.exe`: `equipment.137`'s 1001-1023 effect table is absent from the
  client dump, and `weapon.141`'s runtime use (a displayed bow-plus-arrow total or a
  no-ammunition fallback) is not decidable from the sheets. The pcap corpus
  is ruled out for both, and for every static sheet column, because inventory
  packets carry only item id and quantity while the client resolves stats from
  these sheets locally.
