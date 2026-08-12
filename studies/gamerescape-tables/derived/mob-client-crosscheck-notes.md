# Mob tables vs client mob data - what the join can and cannot settle

The item side of this set produced a column map, because the 1.23b client ships
item stats in bare-integer columns that GE can name. **The mob side has no
equivalent, and that is the main result.** The client ships mob *names* and
*models*; it ships no mob levels, HP, MP, element, or aggression. There are no
unnamed mob stat columns because there are no mob stat columns.

Generation provenance is recorded in `file-inventory.csv`. The verification
guarantees described throughout this file are the checks used to pin each
reading. The client-data input was `<client-data-csv>`.

## Where the client keeps mobs

| Table | Holds |
|---|---|
| `xtx_displayName.csv` | 5,813 actor display names in five languages; English singular at list index 2, English plural at 3 |
| `actorclass.csv` | 7,984 actor class ids, each pointing at one display-name id |
| `actorclass_graphic.csv` | model, scale and appearance ids per actor class |
| `xtx_monsterRace.csv` | 89 internal monster-race names |

`actorclass.csv` carries the row key and exactly one populated column, the
display-name id, so it is a name link and nothing else. `actorclass_graphic`'s
41 populated columns are all model and appearance data - columns 32-37 are
bitfields whose values are sums of powers of two (`1024`, `1056`, `2048`), which
is what an equipment or visibility mask looks like and is not what a race id
looks like.

### Column 2 is the right column for a mob, and column 3 was going unused

Everything here joins mobs on `xtx_displayName` column 2, which was an untested assumption
until the NPC side turned up four more populated columns on the same rows. Checked: the
table is **five languages with a singular and a plural each** - 1 Japanese, 2/3 English,
7/9 German, 14/15 French, 20 Chinese - so column 2 is the English singular and **is** the
correct field for a mob name. The assumption holds.

What it was missing is **column 3, the English plural**, which nothing in this set was
reading. `mob-client-crosscheck.csv` now carries it as `client_plural`, populated on 811 of
812 joined mobs, and 0.858 of those differ from the singular case-insensitively. The
remainder are mobs the client treats as uncountable - `ahriman` pluralises to `ahriman` -
or where the plural only restores proper-noun casing, `akoman`. The irregular forms are the
interesting ones: `Ala Mhigan axeman` pluralises to `Ala Mhigan axemen`, so this is hand-
written inflection and not a suffix rule. `--verify` pins one regular, one irregular and
one uncountable plural, and fails if the column stops differing from the singular.

Two locale details worth knowing before reading those cells: untranslated values are
`[de]` / `[fr]` rather than empty, and German adjective endings are left as an `[a]`
placeholder for the client to inflect - `jung[a] Puk` for `puk hatchling`.

**Columns 15-21 are a humanoid marker.** 84% of the actors in the humanoid faction
blocks populate at least three of them, and **no actor of any named monster race
populates a single one - 0 of 2,095**. Monsters carry a median of 6 populated
columns overall; the humanoid blocks carry 20. So this run says whether an actor is
a person, independently of the race field, and `mob-race-blocks.csv` carries the
count per block. It confirms two readings arrived at by other means: the Atomos and
Amalj'aa blocks are 0% humanoid, while every faction block is 75% or more.

Mob actor classes live in the id ranges **21/22/23** (2,652 with an English
name). Some mobs additionally appear in the 10 range, which holds quest-actor
duplicates.

**Casing is not a mob/NPC discriminator.** The client stores generic mob names
lowercase (`puk hatchling`) because it composes them into sentences, but
Notorious Monsters have capitalised proper names exactly like NPCs. Filtering on
case drops all 106 NMs.

The id range is a better filter but **not a sufficient one**: 98 actors in the
22 range are friendly combat NPCs, and the race field identifies them - see the 1900
block below. Filter on the race field, not the range.

## Why there are no mob stats to name - and how that was checked

Two searches, both negative:

- No table is keyed by mob actor ids other than `actorclass` and
  `actorclass_graphic`, and neither carries a numeric column that behaves like a
  level or an HP pool.
- No *column* anywhere holds a monster-race id. Every column of every mob-keyed
  table was tested by taking its value as a race id and scoring the resulting
  family against GE's `family`; nothing reached even 30 comparable rows at any
  agreement level. An earlier range-overlap heuristic suggested
  `actorclass_graphic` column 33 held race ids; scoring it agreed on 12 of 1,285
  rows, i.e. chance, so that reading is withdrawn.

That second search was looking in the wrong place, and its conclusion - that the
race taxonomy is not linked to individual mobs - **is withdrawn**. The link is not
in a column. It is in the actor id itself. See below.

Consequence worth keeping: **GE's `level_low` / `level_high` / `hp_low` /
`hp_high` / `element` / `aggressive` have no client counterpart at all.** They
cannot be corroborated or downgraded by client-data, and they stay this set's
own evidence at wiki tier. The per-mob family is in the same position.

## Roster reconciliation

`mob-client-crosscheck.csv` - 812 of 824 GE mobs resolved to a client actor:
809 exact (case-insensitive), 2 after folding hyphenation (`Mun-Tuy Sapling` vs
`muntuy sapling`), 1 after dropping a GE disambiguator (`J'moldva (Mob)`). All
812 landed on a 21/22/23 actor id, and all 106 Notorious Monsters matched.

`ge-mobs-without-client-actor.csv` - the 12 that did not, with a computed
`likely_cause` and the nearest client spelling:

- **8 `ge-misspelling`**, where the client contradicts GE: `Elite Sagitarius`,
  `Imperial Sagitarius` and `VIIth Legion Sagitarius` (client: *Sagittarius*),
  `Errant Spirt` (*errant spirit*), `Magitek Vanguard F-1` / `H-1` (client uses
  Roman *F-I* / *H-I*), `Roadside Stabber` (*roadside backstabber*), and
  `B'Khenna Phoenixfire`, which duplicates this set's own
  `B'khenna the Pheonixfire` row.
- **4 `no-client-name-match`**: `Drifting Mine`, `Pyro`, `Rift Angler`, `Zikko`.

`client-mobs-without-ge-page.csv` - 468 monster-range display names with no GE **mob**
page, out of 1,277 distinct names, so **GE documents 63%**. Each row carries a
`likely_cause`, and most of them are not gaps:

| Cause | Names | What it is |
|---|---|---|
| `ge-gap` | 270 | ordinary epithet mobs in a race GE covers - the residue that is genuinely GE's to fill |
| `faction-filler` | 76 | rank-and-file of the 18xx faction blocks |
| `not-a-monster` | 52 | the 1900 block, friendly NPCs |
| `race-name-only` | 34 | the actor is called after its own species, with no epithet |
| `mount-or-companion` | 18 | the chocobo roster |
| `named-boss-gap` | 10 | one-word proper names whose siblings GE does document |
| `second-roster-filler` | 6 | block 1620 |
| `placeholder` | 2 | `???` and `****` |

Three things recorded here earlier were wrong:

- **"GE never documented" is too strong.** 47 of the 468 do have a GE page - 45 an
  `{{Infobox NPC}}`, 2 another template. GE filed them as people, not as monsters,
  which for the 1900 block and the chocobos is the correct call.
- **The largest single zero-coverage race is the chocobos.** Race 1105 has 18 client
  names and no GE mob page for any of them, and the names say why: `choco`, `coco`,
  `bonny`, `salty`, `slugger`, `steamer`, `stitch`, `lucky`. Rental and companion
  birds, not monsters.
- **`11th order patriarch gu bu` is a kobold, not a primal.** Both `Nth order` names
  belong to race 1066, Kobold, whose hierarchy is numbered that way. There is no
  "ordered-primal" category, and these are 2 rows rather than a class.

The other zero-coverage races are single leftovers - `Titan`, `Dragon`, `Wyvern` and
`Hellhound` at one client name apiece, plus the stagehand and provisional-warrior
system races. Where GE does cover a race it is consistently around two thirds
complete: Ixal 24 of 40, Kobold 24 of 37, Rat 27 of 36, Flytrap 24 of 33,
Amalj'aa 14 of 30. So GE's mob coverage is thin evenly, not absent in patches.

### The gap has a shape, and 10 of it is boss content

The residue was first left as one undifferentiated 314. Two tests split it, and both
use the client's own casing, which marks proper names.

**34 are `race-name-only`**: the actor's display name is just its species, with no
epithet - `bat`, `boar`, `antling`, `coblyn`, `crab`, `flan`, `kobold`, `rat`, `sheep`,
`sylph`, `wolf` and so on. GE catalogues mobs by their in-world name, so an actor
called only `bat` has nothing for GE to write a page about. The label states the test
and not an inference: it does **not** claim the actor is unused, and `Titan`, `dragon`
and `wyvern` sit in this class too.

**10 are `named-boss-gap`**, one-word proper names in races GE otherwise covers, and
this is the part of the gap worth acting on. They come in **sets whose other members
GE documents**, which is what makes the class checkable rather than a guess:

| Race | Documented by GE | Missing from GE |
|---|---|---|
| 1107, the cyclopes | `Steropes`, an NM | `Arges`, `Brontes`, `Coincounter` |
| 1095, Garuda | `Garuda`, family Primal | `Chirada`, `Suparna` |
| 1008 Buffalo, 1035 Gargoyle, 1016 Bomb, 1032 Coeurl, 1025 Ogre | the ordinary mobs of each | `Audhumbla`, `Baraquel`, `Bombard`, `Fang`, `Porus` |

Arges, Brontes and Steropes are the three cyclopes, and GE caught one of the three.
Chirada and Suparna accompany Garuda. So these are named, boss-tier actors the wiki
missed, and the siblings both identify them and confirm they are real content rather
than leftovers. `--verify` asserts Arges and Brontes stay in the class and stay in the
same race as the documented Steropes.

**The remaining 270** are ordinary epithet mobs - `Bloodshore eft`, `Coerthas
spriggan`, `Amalj'aa archer`, `11th Order Patriarch Gu Bu` - and nothing
distinguishes them from the documented population. They have the same median actor
count (1) and the same rate of quest-range duplicates (4% against 5%), so they are not
instanced or event-only content that GE skipped on purpose. They are simply pages the
wiki never wrote. Closing them needs GE or retail observation - but the client can say
roughly *what to go and look at*, which is the next section.

### The 270 have no signal of their own, but they have neighbours

`mob-gap-brackets.csv` - one row per `ge-gap` name, carrying how the name relates to
the documented names of its own race and, where the actor id allows it, a level
bracket and a shortlist of zones. Two readings of the *name* were tried first and both
fail as classifiers; what works is the actor id.

**Rejected: the place-prefixed name.** `Bloodshore eft`, `Coerthas spriggan`,
`Sagolii serpent` and `U'Ghamaro potman` each prefix a real place, so it looks like a
class - but no vocabulary in reach separates it from ordinary adjectives. GE's 51
sighting-zone strings are zone-level and miss sub-area prefixes entirely (`Bloodshore`
sits inside Eastern La Noscea and GE never files it as a zone), so they catch 4 names.
Widening to the client's `xtx_placeName` - 826 distinct words over 923 place names -
catches 53, but most of those are false positives: 1.0 named places *after* the beast
tribes, which makes `Amalj'aa`, `Ixali` and `Kobold` place words, and `cave`, `desert`,
`dusk`, `river` and `tower` are simultaneously places and plain adjectives. Place
prefixes are real and are not automatable.

**Rejected: the actor id as a level ladder.** Ids run in sequence within a race, so it
is worth asking whether that sequence is the level order. It is not. Across the
documented mobs an id pair is in level order 59% of the time, barely better than a
coin. Grouped by race and id band, 14 of 104 groups are perfectly monotone and 3 run
backwards, so a handful of races happened to be allocated in level order and the
encoding does not carry it.

**Weakly informative: flanking.** Ids are dense inside a race, so a gap name sits
between two documented mobs, and their levels and zones are the only thing in reach to
guess from. Measured leave-one-out over the documented mobs - hide one, predict it from
its two id-neighbours - against two nulls, because the interesting question is not
whether the guess is any good but whether *adjacency* is doing the work:

| Hint | The two id-neighbours | Any two same-race mobs | The whole race |
|---|---|---|---|
| Level | 53.0% correct, within 10 levels | 41.2% | 86.5%, within 39 levels |
| Zone | 54.5% correct, from 2 candidates | 42.0% | 81.7%, from 11 candidates |

**So the hint is real and small.** Being adjacent in the id space is worth about 12
points over picking any two mobs of the same race, and the result is still wrong
roughly half the time. Widening to two neighbours a side gets 64.2% at 20 levels and
three a side 72.0% at 25, converging on the race-wide figure - so there is no setting
at which this becomes reliable; a narrow hint is a coin flip and a reliable one is the
whole race. Treat `mob-gap-brackets.csv` as a prioritised list of retail-observation
targets, not as a bracket anything can be built on.

`--verify` gates the **lift** rather than the accuracy, since a floor on accuracy alone
would pass a hint that had stopped depending on adjacency at all: the nearest pair must
beat the random same-race pair by at least 0.05 on both facts. It also caps the hint
size (20 levels, 4 zones), walks four brackets that were checked by hand against the
race's ids, and holds the invariants that a bracket is never one-sided and that a race
with no documented mob is never flanked. 222 of the 270 get a level bracket; the
`bracket_basis` column says why each of the other 48 does not, and the next section is
what that turned out to mean.

**The first measurement of this was wrong, and the way it was wrong is now gated.** It
read 83.8% on level and 84.4% on zone, which would have made the hint look four times
better than it is. The cause was leakage: a mob owns several actor ids, so hiding one
id left the mob's *other* ids in the pool, and the flank kept handing back the mob's
own answer. Withholding every point of the mob under test - which is the situation a
gap name is actually in, since it has no documented points at all - drops the figure to
53%. `--verify` now counts any test whose flank touches the mob under test and requires
that count to be zero.

How each name relates to the documented names of its own race:

| Relation | Names | What it means |
|---|---|---|
| `sibling-base` | 146 | GE documented another mob of this race with the same head noun, so this is a variant of a species GE covers - `cave crab` beside `Lake Crab` |
| `race-documented` | 69 | GE covers the race but no name component is shared - `cinderwing` in the Vulture race |
| `sibling-prefix` | 51 | the shared word is the modifier, which is the beast-tribe job-title namespace (`Ixali ...`, `Amalj'aa ...`) but also fires on a bare element word, so it is the weaker reading |
| `race-undocumented` | 4 | GE documented nothing in this race at all |

The 4 `race-undocumented` names are worth naming, because they are the only gaps with
no anchor of any kind, and they share a cause: **each sits in a race the client itself
never translated.** `cloud dragon` and `sephiroth dragon` are race 1081, whose name is
still the Japanese *erimakitokage*, frilled lizard, with the U+4EEE *kari* provisional
marker; `hellhound` is race 1098, *kaashii* (Cu Sith), also provisional; `tunnel worm`
is race 1106, *kuroko*, the stagehand - the utility race that also holds the `****`
placeholder. So the client left these races unfinished and GE, working from retail,
had nothing to see. These four need a decomp or retail observation; nothing here
brackets them.

### The 48 unbracketed names are the end of a gradient, not a class

Why each one has no bracket, from the `bracket_basis` column:

| Basis | Names | |
|---|---|---|
| `flanked` | 222 | documented mobs on both sides, so a bracket |
| `above-race-high` | 27 | past the highest documented level-bearing mob of its race |
| `below-race-low` | 13 | below the lowest |
| `no-level-bearing-race-mate` | 8 | no mob of its race carries a level at all |

The 2-to-1 split between `above-race-high` and `below-race-low` is the visible end of
something measurable across the whole roster: **GE's coverage thins along a race's id
run.** Over the races that hold both a documented and an undocumented actor, the
undocumented ones sit at median position **0.644** of their race's client id run against
**0.467** for the documented - 39% of them in the last quarter of the run against 22%,
and 20% in the first quarter against 30%. `race_run_position` carries the figure per
row, measured over every monster-range actor of the race rather than over GE's subset,
so it describes the client's allocation and not the wiki's coverage of it. `--verify`
requires the two medians to stay at least 0.10 apart; they are 0.178 apart now.

**17 of the 270 own the highest actor id their race was ever given.** That is the
extreme of the same effect: the wiki documented what it met, met less of each race as
the ids ran on, and stopped before the end.

### Half of that gradient is the 21/22/23 band, and the 23 band is a real level floor

Reading those 17 top-of-run names is what exposed a confound in the paragraph above.
**Ten of the 17 sit in the `23` band**, and a 23-band id is numerically the highest an
actor of a race can have, so "late in the race's run" and "in the 23 band" are largely
the same statement. Measuring each band as its own run separates them: the two medians
are **0.556 against 0.472 within a band**, against 0.644 against 0.467 across all of
them. So roughly half the gradient is allocation order inside a band and half is GE
covering the 23 band hardly at all - 26 gap actors there against 48 documented. Both
figures are now gated, at 0.05 within a band and 0.10 across them.

**The 23 band is worth more than the whole flanking apparatus.** It was already recorded
here that the band correlates with level; measured properly against the documented mobs,
it is a floor and not a correlation:

| Claim | Support |
|---|---|
| a mob with a 23-band actor tops out at level 35 or above | 45 of 45 documented, no exceptions |
| ... and *starts* at 35 or above, in a named race | 38 of 38 |
| ... and starts at 35 or above, blocks included | 44 of 45 |

The single mob that starts lower is **`Imperial Speculator`, 22 to 52**, and it is in the
Garlean block 1800 rather than a named race - which is why the floor is stated on the top
of the range where a block is involved and on the bottom of it for a race.

`band_level_floor` carries this for the **18 gap names holding a 23-band actor**, 15 of
which had nothing at all before. At 45 of 45 it is the only hint in this file that is
better than a coin flip, and it is a floor rather than a bracket - it says "35 or above",
not "roughly 35". `--verify` fails on any documented counterexample, on the support
dropping under 0.95 on the named-race form, and on a row carrying the floor without a
23-band actor to justify it.

### The 23 band is instanced content, and that is what the floor was measuring

Asking where the 15 newly floored names live answered what the band *is*. Of the 47
documented band-23 mobs that carry a sighting zone, **43 are sighted in nothing but four
dungeons**:

| Zone | Documented band-23 mobs |
|---|---|
| The Dzemael Darkhold | 15 |
| The Thousand Maws of Toto-Rak | 14 |
| Cutter's Cry | 8 |
| The Aurum Vale | 7 |

**All four exceptions are the same block.** `Imperial Hoplomachus`, `Imperial Medicus`,
`Imperial Signifer` and `Imperial Speculator` are race 1800, the Garlean legion, sighted
at Castrum Novum - which `zone-client-crosscheck.csv` already classifies as
`client-place-not-a-zone`, a sub-area rather than a zone, because it is an instanced
battle. So the residue does not weaken the reading, it completes it: **the 23 band is
instanced content**, the four dungeons plus the Castrum assault. It also explains the one
level-floor exception, since `Imperial Speculator`'s 22-to-52 is a wave-battle range
rather than a mob's level.

That makes a zone hint out of the band, and it is by a wide margin the best one in this
file. **20 of the 25 races with a band-23 sighting are pinned to exactly one dungeon** -
Basilisk and Antling to Cutter's Cry, Wight and Ahriman and Drake and Gargoyle to
Dzemael Darkhold, Slug and Funguar and Jellyfish to the Aurum Vale, Puk and Flan and
Chigoe to Toto-Rak. Leave-one-out over the documented mobs, predicting a mob's dungeon
from the *other* band-23 mobs of its race scores **0.828 from a median of 2 candidates**,
against 0.545 from 2 for the general flanking hint and 0.817 from 11 for a race-wide
guess. `band_zone_hint` carries it for all 18 band-23 gap names: the race's own dungeons
where it has any, the four-dungeon roster where it does not.

The roster is derived from the sightings on every run rather than written down, so a
re-mine that moves it moves the hint. `--verify` requires the band to stay 90% inside its
own top four zones, the same-race hint to stay above 0.70, and the median race to offer
fewer than all four - the last of those being what makes the per-race pairing worth more
than the roster.

**What the band still is not.** Not notorious-monster status, and not a level tier as
such: bands 21 and 22 both run from level 1 upward and cover the whole 23 range, whose
own documented mobs run 22 to 59 with a median of 52. The level floor is a *consequence*
of the content being instanced dungeons at the top of the 1.x level curve, not an
independent property of the band. What it *is* is one value of a three-value axis, which
the last section in this arc reads off the other two.

Where this leaves the 15: each has a level floor of 35 and a dungeon shortlist, and the
names corroborate the shortlist without being part of how it was computed - `vale eft`
and `vale banemite` point at the Aurum Vale and the hint says Aurum Vale, `quicksand
basilisk` at Cutter's Cry and the hint says Cutter's Cry, `myrmidon marshal` and
`myrmidon scavenger` are Antlings and the hint says Cutter's Cry. That agreement is
encouraging rather than evidential. Confirming any of them still needs retail
observation.

**The one-sided hint was measured and rejected.** A single nearest neighbour is not
nothing, but it is not enough: leave-one-out over the documented mobs it lands within 5
levels 30.9% of the time against 27.3% for any race-mate, and names a true zone 32.0%
against 28.1% - lifts of 0.036 and 0.039, under the 0.05 floor the two-sided bracket
clears at 0.117 and 0.124. So these 48 cells stay blank because the gate says so, not
because the work was skipped.

**4 of the 8 with no level-bearing race-mate do have documented race-mates** -
`deepvoid butcher`, `lesser gargoyle`, `monolith` and `satin plume` are in races GE
covers, but every GE page in those races leaves the level blank. The other 4 are the
`race-undocumented` names above.

**A scope caveat this section forced out, and it applies to the whole 468.** Several of
the 48 are conspicuous 1.x content - `nael van darnus` and `nael deus darnus` of the
Meteor storyline, `good king moggle mog xii`, `sabotender alegre`, `sabotender
desertor`, `torama`. The 11,227-page corpus holds **no page at all** for any of them,
not even under another title, so this is not GE filing them as something else the way it
filed the 1900 block as NPCs. "No GE page" here means "no page in a harvest scoped to
1.0 mob and item content" - a story boss belongs to a character article, which such a
harvest would not collect. Read `client-mobs-without-ge-page.csv` as a list of names
this corpus cannot corroborate, not as proof the wiki never documented them.

**Item names do not corroborate a gap mob.** GE has `Hellhound Fang` and
`Hellhound Hide` but no hellhound, and `Sabotender` and `Sabotender Del Sol` but not
`Sabotender Alegre`, which looks like the drops vouching for the mob. Measured, it does
not: 62 of the 270 gap names share their head noun with a GE item name, 23%, against 22%
for the documented mobs - and `Dragon Kabuto` / `Dragon Pepper` matching `cloud dragon`
shows what the test is really picking up, which is crafting vocabulary.

**What this section is not.** Every bracket and zone shortlist is an interpolation
between two other mobs, not a measurement of the undocumented one, and it is wrong
about half the time. The file is a target list for retail observation - go look at this
actor, expect roughly this level, in one of these zones - and it must not be read back
as evidence about the mob.

### The band digit is a spawn container, and band 22 is guildleve content

The 23 band was read three times in this file - as a correlation, then a level floor,
then instanced content - without ever asking what its two much larger neighbours are.
They hold 1,392 and 1,190 of the 2,662 mob actors against 80, so the question was the
larger one. **The band digit is a spawn container**, and the three values are three
independent deployments of the same race:

| Band | Container | Documented mobs sighted inside a guildleve or quest |
|---|---|---|
| 21 | persistent | 12 of 376 |
| 22 | leve-or-quest | **277 of 280** |
| 23 | instanced-dungeon | 0 of 41 |

Measured over the mobs whose actor ids are all in one band and that GE sighted at all,
since a name in two containers has no single answer and an unsighted one has no evidence
either way. Both ends are gated: a floor of 0.97 on band 22 and a ceiling of 0.10 on band
21, because a tag rule that fired on everything would clear the floor by itself. Both
filters determine that floor - letting band 22's 10 unsighted mobs in drops it
to 0.955 and its 26 dual-band names to 0.845.

**The tags are the client's own content names, not GE's grouping.** That distinction
decides whether this is a finding or a wiki habit, so it is measured too: **223 of the
248 distinct sighting tags are an exact cell in `xtx_guildleve` or `xtx_quest`** - 172
guildleve names, 51 quest-only. The 25 that are not are behests, seasonal events, leve
*categories* rather than leve names (`Skirmish`, `Caravan Security`, `Hunter's Moon`) and
eight quests GE titles differently. Exact cell match rather than a substring search,
which for a tag as short as `Behest` would hit almost any description; `A Fine Host` and
`Skirmish` pin the check from both sides.

**It is a container and not an overflow page.** The obvious alternative reading is that a
race fills band 21, runs out of variant numbers and continues into 22. It does not:
**all 82 races that hold both a band-21 and a band-22 actor reuse variant numbers across
them**, the numbering restarting at 01 in each band, and the fullest band-21 race stops
at 73 of the 99 a two-digit variant field holds - so there was no capacity to overflow.
The same fact from the name side is that **91 mob names own actors in more than one
band** (88 in two, 3 in all three): one creature, deployed twice. Nothing in the dump can
show that this test compares anything, since every race renumbers, so `--verify` puts a
synthetic continuing race through it and requires no overlap.

**The client corroborates, thinly.** Two client tables reference a mob actor at all -
`quest_marker.csv` and `passiveGL_craft.csv`, the second being guildleve crafting - and
**all 7 of their references are band 22**: `scalepuk` on `2200101` and `stonescale
pteroc` on `2200114`. 7 references over 2 distinct actors is far too little to carry
anything, and GE's tags carry the finding instead; what this adds is that the client's
own quest and leve plumbing points where the reading says it should. `--verify` requires
both tables present, at least one reference, and no reference outside band 22.

**What this settles about the gap list.** `spawn_container` is now published on both
`mob-client-crosscheck.csv` and `mob-gap-brackets.csv`, and it reshapes the 270:

| Container | Gap names |
|---|---|
| leve-or-quest | 143 |
| persistent | 83 |
| persistent + leve-or-quest | 26 |
| instanced-dungeon | 17 |
| persistent + instanced-dungeon | 1 |

**169 of the 270 hold a band-22 actor**, which is the largest single explanation of why
GE never wrote them up: a leve mob is not standing in a zone to be found and written up
the way a persistent one is, and GE's coverage of leve rosters is by leve rather than by
mob. For those 169 the container is worth more than the level bracket beside it - it says
what kind of thing the name is, which the bracket never does.

It also puts the earlier 23-band work in its place. The level floor and the dungeon
shortlist stand exactly as measured, but they are properties of *dungeon content*, and
the band was only ever the way to spot it. The medians line up with that reading and add
nothing to it: band 21 documented mobs run to a median level of 42, band 22 to 35 - leve
rank rather than zone level - and band 23 to 52.

**What this does not settle.** The container says where a mob was spawned, not what it did
there: no level, no HP, no spawn point, no respawn timer. The three sighted band-22 mobs
GE attached nothing to are read in the next section.

### The 3 band-22 exceptions, and a second reading of the band that owes nothing to tags

Three mobs were the whole residue of the container reading: sighted by GE, all their
actors in band 22, and no leve or quest attached. `--verify` now pins them as the *entire*
residue, so "the three" is a claim something holds rather than a count in prose.

**`Frenzied Aurelia` is settled outright, by GE's own prose.** Its `Notes` field says it
"Spawns as part of the Limsa Lominsa Main Scenario Quest **Shapeless Melody**" - and that
title is an exact cell in the client's own quest names. GE recorded the quest in the
infobox note and left `Event/Quest` blank in the sighting row, which is a data-entry gap
and not a statement about the mob. Its sighting zone, `Y'shtola's Ship (Instance)`, agrees.

**The other two are placed by two independent readings, neither of which is a measurement
of them.** GE's pages for `Gorged Djigga` and `Hairless Hare` have `Event/Quest` blank and
nothing in `Notes`, and no other page in the 11,227-page corpus mentions either name.

The first reading is **the level span, which is a second correlate of band 22 and owes
nothing to the tag column at all**. A leve mob's level is a *range* because the leve has
difficulty steps:

| Container | Mobs spanning 10+ levels | Median span |
|---|---|---|
| leve-or-quest | **0.480** | 1 |
| persistent | 0.018 | 4 |
| instanced-dungeon | 0.000 | 0 |

The band-22 median is *lower* than the persistent one because its spans are bimodal - a
leve mob is either a single-level spawn or a whole ladder, where a persistent mob's range
is the ordinary few levels of a spawn area. The share is the figure that separates them,
not the median, and it is gated in both directions: a 0.40 floor on band 22 and a 0.05
ceiling on band 21.

`Gorged Djigga` spans 24 levels and `Hairless Hare` 28, which puts them in the band-22
distribution and nowhere near the band-21 one - only 7 persistent mobs in the whole set
span 10 levels or more. And the spans are *evenly* stepped: **97 of the 120 wide band-22
spans are a multiple of 4**, against the 0.25 a multiple-of-4 test scores by chance,
which is what a fixed ladder of difficulty steps looks like. How many steps is an
inference the client's `guildleve.csv` does not confirm and this file does not claim; that
the ladder is evenly spaced is measured. Since 0.808 of the real spans pass the test,
nothing in the dump could show it discriminates, so `--verify` puts an unstepped control
through it.

The second reading is **adjacency**. Both sit inside a run of leve mobs of their own race
and band:

- `Hairless Hare` owns `2204205`, `2204207` and `2204208`, *interleaved* with `Salt Hare`
  on `2204204`, `2204206` and `2204213` - and Salt Hare is tagged `Best Cellars` and
  `Wanted: Ser Aucheforne of the High Tide`. Interleaved ids in one band and race are one
  allocation. (This also explains the odd `Hare` in the Slug family: `sea hare` and `salt
  hare` are Slug-family sea hares, so GE's family is right and the name is 1.0's.)
- `Gorged Djigga` on `2205606` sits between `ankle biter` and `Plague Djigga`, tagged
  `Treasures of the Main` and `Preventing the Plague`. Every documented band-22 actor in
  race 1056 carries a leve.

**That adjacency is worth publishing as a hint, and it is the second-best one in this
file.** Flanking a band-22 name with its nearest tagged band-22 race-mates predicts a
*named leve*: leave-one-out over the documented mobs it scores **0.516 from a median of 2
candidates against 0.319 for a random same-race band-22 pair**, a lift of 0.197 against
the 0.117 the level bracket manages, with zero leave-one-out leakage. `leve_candidates`
carries it for **117 of the 169 band-22 gap names**; the other 52 are flanked on one side
only, and are the subject of the next section.

**The one case where the hint can be scored against a known answer, it is wrong.** For
`Frenzied Aurelia`, flanked by `Drifting Aurelia` and `Drifting Anemone`, the hint offers
`Sharing the Load | Soft Targets`. The real content is `Shapeless Melody`. A 0.516 hint is
wrong about half the time and this is one of those halves - so it is pinned as a fixture,
and if a future change turns it into a hit that is a change to explain rather than a
quiet improvement.

**A mechanism that was tried and rejected.** If GE's `Notes` resolved one exception, the
obvious move is to scan every mob's notes for a client content name and treat a hit as a
tag. Measured, it does not work: 7 persistent mobs and 3 dungeon mobs also name one, and
their notes read "Involved in the quest X" - a persistent mob a quest sends you to kill,
which is the opposite of what the container says. `Frenzied Aurelia`'s note says "spawns
as part of", a different claim. That distinction is real but not measurable here -
"involved in" appears in 6 notes, all persistent, too few to gate - so the exception is
recorded as a reading of one page and no notes-scanning mechanism was added.

**What is still open on these two.** Which leve, exactly. `Hairless Hare` gets `Best
Cellars | Wanted: Ser Aucheforne of the High Tide` and `Gorged Djigga` gets `Preventing
the Plague | Treasures of the Main`, each a shortlist that is right about half the time,
and the one case with ground truth says it can be wrong. Confirming either needs retail
observation.

### The 52 one-sided names, where the weak flank is worth publishing after all

The 52 band-22 gap names the flanked hint cannot reach split the way the level side's
48 did, and `leve_basis` now carries the reason per row rather than leaving the cell
unexplained:

| `leve_basis` | Rows | What it is |
|---|---|---|
| `above-band-high` | 31 | above every band-22 actor GE tagged in that race |
| `below-band-low` | 14 | below every one of them |
| `no-tagged-band-mate` | 7 | GE tagged no band-22 mob of that race at all |

**And here the one-sided flank clears the gate the level one failed.** Over the 185
documented points that genuinely have a single neighbour, that neighbour names a true leve
**0.238 of the time against 0.177 for any tagged race-mate - a lift of 0.061**, where the
level bracket's one-sided form managed 0.036 and was rejected. So 45 of the 52 get a
`leve_one_sided` cell, and the 0.05 floor is applied consistently rather than the weaker
hint being dropped because it feels weak.

**It gets its own column on purpose.** 0.238 and 0.516 are different claims, and a
consumer filtering one column must not silently get a mixture. `leve_candidates` stays the
flanked hint alone, `leve_one_sided` is the single-neighbour one, `--verify` fails if a row
carries both or if the basis disagrees with which is filled, and it also fails if the two
accuracies converge to within 0.10 - at which point publishing them apart would be telling
the reader something no longer true.

**Scoping the measurement was the whole difficulty.** Run the same test over *every*
documented point and it reads 0.358, which still clears the lift floor and still sits under
the flanked hint, so no gate on real data can tell the two measurements apart. That figure
is about a different question - it includes the points that have two neighbours, which the
52 by definition do not. The correct population is the one-sided points alone. `--verify`
puts a four-point control through the function whose two flanked members would score and
whose two one-sided members must not, so scoring the wrong population cannot pass.

**The 7 with nothing are a real dead end, not a thin one.** `cloud dragon`, `sephiroth
dragon`, `goblin robber`, `hellhound`, `lynx`, `torama` and `ochu` are in races where GE
tagged no band-22 mob at all - six of them have no documented band-22 race-mate of any
kind, and `ochu`'s race has one, `Morbol`, which GE left untagged. There is no roster to
fall back on the way the band-23 zone hint falls back to its four dungeons, because the
band's tag vocabulary is 248 leves wide and naming all of them is not a hint. Three of the
seven are names other sections already flagged as thinly covered by this corpus - `torama`,
which has no GE page at all, and `hellhound` and `cloud dragon`, whose only apparent
corroboration was item names that turned out to be crafting vocabulary.

### The 7 are exhausted, and looking for them found the client's own leve attribution

Chasing the 7 meant asking whether anything outside GE names a leve for a mob, and the
answer turned out to be yes: **`xtx_guildleve` carries the leve's own objective text, and
that text names mobs.** Column 11 is the English leve name and column 15 the English
briefing; 610 of the 623 rows carry both, and 167 of those briefings name a client mob.
The layout is pinned by fixture for the same reason `xtx_displayName`'s was - columns
12/13 and 16/17 are the German and French renderings.

Scanning it attributes **110 mobs to a named leve, from the client rather than from any
interpolation in this file**, and where GE tagged the mob too the two agree on **33 of 37**.
Matching is maximal, longest name first, because `djigga` sits inside `plague djigga` and a
shortest-first scan silently credits the wrong mob - the same defect that once collected 13
quest pages for `amalj'aa`. `--verify` pins the two apart.

`client_leve` carries it on both tables. What it adds:

| Where | Rows |
|---|---|
| documented mobs, 29 of them never tagged by GE | 66 |
| `ge-gap` names | 19 |
| ... of those, the only leve statement the row has | 4 |

`delinquent sylph`, `princess pudding`, `pteroc` and `nannygoat` had no flanked hint, and
now carry a leve named by the client - which outranks a 0.238 interpolation outright.

**A mention is not proof of the container, and is gated as such.** 12 of the 66 documented
matches are persistent-only mobs: a briefing can send you after something that was always
standing there. So 96 of the 110 hold a band-22 actor, 0.873, and `--verify` holds that
inside `[0.80, 1.0)` - the upper end on purpose, because at 1.0 the test would be claiming
the mention *is* the band, which those 12 deny. It is the same distinction GE's prose drew
between a mob that "spawns as part of" a quest and one merely "involved in" it, and this
time there is enough of it to measure.

**For the 7 themselves, no briefing names any of them.** Not `cloud dragon`, `sephiroth
dragon`, `goblin robber`, `hellhound`, `lynx`, `torama` or `ochu`, in any of the 610 rows.
That absence is pinned as a fixture, so a later change that starts matching one is noticed
rather than quietly improving a count.

**But 2 of the 7 were already attributed, one tier up, and this section nearly missed it.**
`mob-quest-attribution.csv` puts `goblin robber` in the sidequest `Losing One's Thread`
with a level floor of 25, and `hellhound` in the Grand Company quest `Arms Race`. Both are
band-22 mobs whose content is a quest rather than a leve, which is exactly what the
container name allows for and what a search restricted to `xtx_guildleve` cannot see. So
the residue is **5, not 7**: `cloud dragon`, `sephiroth dragon`, `lynx`, `torama` and
`ochu`.

For those 5, every tier is now empty: no GE tag, no quest page, no tagged band-22
race-mate, no client briefing. **They are the first names in this set to be exhausted
rather than weakly hinted**, and recording that is worth more than a shortlist nothing
supports.

### `client_leve` is two claims, not one, and the 29 GE never tagged are what showed it

29 documented mobs carry a leve the client names and GE never tagged. Reading the list is
what caught a defect in the previous section: they are mostly not individuals. `Balloon`,
`Basilisk`, `Cactuar`, `Aurelia`, `Roseling`, `Devilet`, `Ahriman`, `Ladybug`, `Lemur`,
`Orobon`, `Flytrap`, `Anemone`, `Angler` - **species words**. A briefing that says "a pack
of ravenous marmots" is not naming the actor `marmot`; it is using the noun. The scan cannot
tell the difference, and the previous section published a single 33-of-37 agreement figure
over both kinds.

Split on the client's own capitalisation - the signal this file already learned to trust
over word count - and the one figure becomes two:

| The briefing names | Attributed | GE also tagged | Agree |
|---|---|---|---|
| an individual, capitalised | 13 | 11 | **11 of 11** |
| a species, lower case | 53 | 26 | 22 of 26 |

**Where the client names an individual the attribution is exact**, every case GE can check:
`Deadeyes`, `Palemoon Parazuzu`, `Rorogun the Tailtamer`, `Godwin Goodgoat`, `Alvara
Sourkiss`, `Ser Aucheforne of the High Tide`, `B'khenna the Phoenixfire`. Where it uses a
species word it is 0.846, which is good but is a different claim, and the four disagreements
are all in that half. `client_proper_name` on the crosscheck says which kind a row is;
`--verify` holds a floor on each and a margin between them, because if a species word became
as reliable as a named individual the column would be marking a distinction that no longer
exists.

**The one check worth more than any of this: the container survives a source swap.** GE's
tag column is what the whole spawn-container reading rests on, and GE is a wiki. Folding the
client's own attribution in as an additional tag source moves the numbers as follows:

| Band | GE tags only | GE tags plus the client |
|---|---|---|
| 21 persistent | 0.032 | 0.061 |
| 22 leve-or-quest | 0.989 | 0.989 |
| 23 instanced-dungeon | 0.000 | 0.000 |

Band 21 rises and stays well inside its 0.10 ceiling, band 22 does not move at all, and
band 23 stays empty. So **the split is not an artefact of what GE chose to write down** -
it holds when a second, independent source is consulted. `--verify` gates the merged shares
as well as the GE-only ones, and fails if the client adds no band-21 mob GE had missed,
since a swap that changes nothing tests nothing.

The rise in band 21 comes from 12 persistent-only mobs the client attributes and GE did
not. **The next section reads those 12, and they are not what this paragraph first claimed
they were.**

**What the 29 do not do** is become tagged mobs. They are not added to GE's tag column and
the container measurement still reports the GE-only share as its primary figure, with the
merged one beside it as the robustness check. A species-word attribution at 0.846 is not
evidence a particular actor spawned in a particular leve.

### The 12 persistent ones were an artefact, and saying so makes the container reading exact

The section above wrote the band-21 rise up as "12 persistent mobs a leve sends you after
rather than spawns" - a statement about how 1.0 built its leves. Reading the 12 shows it was
a statement about the scan. **All 12 are species words. Not one is a named individual:**

`Balloon`, `Basilisk`, `Burble`, `Cactuar`, `Cassiopeia`, `Cellar Puk`, `Errant Soul`,
`Flytrap`, `Forest Funguar`, `Phurble`, `Sundrake`, `Will-o'-the-wisp`.

The mechanism is visible in the leve names themselves. `Wanted: Coiled Adder` is a hunt for
a named NM and its briefing describes the target as a sundrake; the scan reaches the
persistent base-species actor `Sundrake`. `Wanted: Soft Evidence` mentions phurbles the same
way. The briefing is not naming that actor, it is naming what the target *is*.

**Restrict the merge to the half of the attribution worth trusting and the container reading
comes back exact.** Folding in only the attributions where the client named an individual:

| Band | GE tags only | plus all attributions | plus proper-named only |
|---|---|---|---|
| 21 persistent | 0.032 | 0.061 | **0.032** |
| 22 leve-or-quest | 0.989 | 0.989 | 0.989 |
| 23 instanced-dungeon | 0.000 | 0.000 | 0.000 |

Band 21 returns to exactly where GE left it. The reliable half of the client's own leve
attribution adds nothing to the persistent band at all - which is a stronger agreement
between the two sources than the previous section claimed, not a weaker one.

**And the invariant behind it: all 29 attributions that name an individual hold a band-22
actor. No exceptions**, and every one of the 14 attributions with no band-22 actor is a
species word. So the `[0.80, 1.0)` band on the mixed figure stays, but its justification
changes: the 15 exceptions are the artefact of scanning prose for a common noun, not leves
reaching persistent mobs. `--verify` holds both - zero strays among the proper-named
attributions, and the proper-only merge leaving the band-21 tagged count unchanged.

Both of those pass on data that cannot fail them, which is the recurring shape in this file:
since every proper-named attribution already holds a band-22 actor, "no strays" is also what
a check accepting *any* band would report, and "the proper-only merge adds nothing to band
21" is also what consulting no attributions at all would report. Two controls close it -
`Deadeyes` for a named individual and `balloon` for a species word, both given only a
band-21 actor, with the band check required to call exactly one a stray and the merge to
count exactly one as tagged.

One hole stays open and cannot be closed here. Hand the proper-only merge no attributions at
all and it reports the same band-21 share, because *adding nothing* is precisely what the
finding says the reliable half does. The control shows the function discriminates; nothing in
this dump can show it was actually consulted, since no band-22 mob is untagged by GE and
attributed by a proper-named client briefing. It is the same limitation this file hits
whenever a measurement's true answer is empty, and it is recorded rather than papered over.

### Reading all 15 mismatches: one was a bug, the rest are six kinds of prose

Every one of the 15 was read in its own briefing sentence rather than counted. They are not
one failure mode, and one of them was a defect in the scan:

| What the briefing was doing | Names |
|---|---|
| naming the species while the leve spawns its own band-22 variant | 7 |
| naming a **place** that begins with the mob's name | 1 |
| flavour prose, not a target at all | 3 |
| a hedged simile | 1 |
| a longer creature name the vocabulary does not hold | 1 |
| a second mention beside the correct maximal hit | 1 |
| a generic word whose race has no band-22 actor | 1 |

**The place-name collision was a bug, and fixing it needed no new rule.** `cassiopeia` is a
mob name and also the head of the zone `Cassiopeia Hollow`, and all 13 of its attributions
were briefings mentioning the place. Maximal match already prefers the longer name - it
simply did not know the longer name existed. The client's own 907 place names now join the
scan as **decoys**: they win positions but are never attributed. That drops `cassiopeia`
outright and also caught one nobody had looked for - `kobold` was attributed to `Operation:
Crosseye`, whose briefing is about a "kobold garrison". Both are pinned as fixtures.
Attributions go 111 to 110, agreement with GE stays at 33 of 37, so nothing real was lost.

**The largest group is not a false positive in the ordinary sense.** For 7 of them the
briefing genuinely states the leve's target - "attacks by deadly seedkin called flytraps",
"the walking seedkin known as the cactuar", "parasitic voidsent known as burbles" - and the
scan lands on the persistent base-species actor because that is the actor the client names
with the bare word. **Every one of those 7 races does hold band-22 actors**: `frightened
cactuar`, `bloated burble`, `wandering wisp`, `fumbling funguar`, `deepground puk`,
`landtrap`, `dune bogy`. So the reading is that the briefing names the species in prose while
the leve spawns its own variant - which is the container reading, not a counterexample to it.

`will-o'-the-wisp` shows it exactly. The client ships **two spellings one band apart**:
`will-o'-the-wisp` on a band-21 actor and `will-o-'the-wisp`, apostrophe misplaced, on a
band-22 one. The briefing uses the correct spelling, so the scan reaches the persistent
actor while the leve's own actor sits in band 22 under the typo.

The rest are prose the scan cannot be taught to read. `Wanted: Soft Evidence` lists "the
two-headed nannygoat, the hairless phurble" as carnival sideshow attractions; `Wanted: Coiled
Adder` mentions a `sundrake` hatchling in the backstory of a hunt for something else;
`Corpse Cupid` says "zombie-like creatures", which is a simile and not a `zombie`; `Operation:
Frame Work` says "Ixali Battle Balloons", and `battle balloon` is not a client mob name so
`balloon` is the longest thing the vocabulary knows. `basilisk` is attributed to a leve that
correctly attributes `butcher basilisk` too, from a second mention.

**`dragon` is read in the next section**, and it turns out to be prose as well.

**None of the 14 supports leves targeting persistent mobs**, which is the question the
previous section left open. Every one is either the species-in-prose pattern with a band-22
variant available, or prose that names no target. The question stays open on the evidence,
not answered by it.

### `dragon` is prose too, and the triage causes turn out to corroborate the band

Reading the two briefings settles it, and neither is a target:

- **`Heat of the Moment`** - "an airship carrying supplies to Gridania was attacked by a pair
  of dragons. Knowing that they did not have the firepower to dispatch the creatures, the
  pilot chose instead to outrun them" - and jettisoned cargo to do it. **The leve is the
  recovery of that cargo.** The dragons are explicitly not fought.
- **`Nutritious Fishes`** - "With all the effort spent slaying deadly dragons and saving
  distressed damsels, today's active adventurer does not always have the time for a healthy
  meal." A figure of speech in a leve about salt carp.

The actor shape agrees. Race 1068 is `Dragon`, its name in `xtx_monsterRace` still carrying
the provisional marker, and it holds **four actors, all band 21, all named `dragon`**, with no
variant and no band-22 counterpart. `client-mobs-without-ge-page.csv` already files it as
`race-name-only` - a bare race word with no epithet - which is what a briefing reaches when it
uses "dragons" as a noun. The dragons of 1.x that players actually fight are elsewhere: race
1022 holds `ashdrake`, `battle drake`, `branded drake` and `biast` with band-22 actors, race
1038 `wyvern`, race 1081 `Cloud dragon` and `Sephiroth dragon`.

So **all 14 non-band-22 attributions are accounted for and none is a target**. `--verify`
pins the count at 14, so a fifteenth would be an attribution nobody has read.

**And asking why `dragon` sits alone in band 21 turned up a corroboration nobody arranged.**
The triage causes in `client-mobs-without-ge-page.csv` were assigned from the names, long
before the band digit was read. Lined up against it:

| Likely cause | Names | Hold a band-22 actor |
|---|---|---|
| `not-a-monster` | 52 | **52** |
| `mount-or-companion` | 18 | **18** |
| `race-name-only` | 34 | 30 |
| `faction-filler` | 76 | 60 |
| `ge-gap` | 270 | 169 |
| `placeholder` | 2 | 0 |
| `second-roster-filler` | 6 | 0 |

The two causes meaning "spawned by content rather than standing in the world" - the hamlet
militia and Grand Company staff, and the rental chocobos - are **entirely** band 22, 70 of 70.
The two meaning "an artefact of the roster" are entirely band 21. That is the container axis
arrived at from the opposite direction, and `--verify` now holds all four, which also makes
`dragon` legible: it is one of only 3 `race-name-only` names with no band-22 actor at all.

### The 3 race-name-only holdouts: one is a set piece, two are ordinary

`crab`, `dragon` and `zombie`. The first thing to rule out was that they are unused shells,
and they are not: all three have full `actorclass_graphic` rows, column for column
indistinguishable from their race-mates. Whatever they are, the client can deploy them.

**`dragon` is the interesting one, and it belongs to a class.** 12 of the 95 named mob races
hold exactly one distinct name, and **only 4 of those never reach band 22**:

| Race | Its one name | Already recorded here as |
|---|---|---|
| 1110 | `atomos` | the single-creature primal missing from `xtx_monsterRace` |
| 1101 | `???` | the runtime-named placeholder space |
| 1102 | `???` | the same |
| 1068 | `dragon` | - |

Three of the four were already known to this set as special cases. So `dragon` sits with set
pieces and placeholders rather than with field rosters, which is exactly what a race holding
one name across four actors - all four pointing at the same name row - looks like. The other 8
single-name races do reach band 22 and are ordinary in that light: `wyvern`, `titan`,
`ascian`, `hellhound`, three elementals and `imperial juggernaut`. `--verify` pins the
membership of the band-21-only four, because the membership is the finding.

**`crab` and `zombie` are ordinary undocumented mobs, and there is nothing more to find.**
Their races are well populated - 25 distinct names over 38 actors for Crab, 18 over 33 for
Zombie, both with band-22 rosters of their own - and the bare word sits mid-run rather than
appended at the end. GE simply never wrote up a mob whose name is the race word.

**They do share one quirk worth recording, because it is the mechanism behind a rule this
file already states.** Both are in a *transposition*: actor `2107615` carries the name id
`3107613` while `2107613` carries `3107615`, so `crab` and `beryl crab` have each other's
expected name row - and `zombie` does the same with `dapper cadaver` at `2101817`/`2101815`.
26 such mutual pairs exist across the dump. This is the sharpest form of why a name must be
read through the pointer: turning the actor id's leading 2 into a 3 does not fail loudly here,
it returns **the wrong mob's name**. `--verify` pins the pair count and both examples, and the
next section reads all 26 out.

### All 26 transpositions, published as a table

`mob-name-id-transpositions.csv` - 26 rows, both actor ids, both name ids, both names and the
variant distance. It exists because the actor id is what a consumer joins on and this is the
one place where the arithmetic shortcut fails *quietly*.

The shape is tight. **The variant distance is only ever 1, 2 or 4**, never more, and the pairs
are always within one race and one band. **6 of the 26 are a single race**: 1002, the raptors,
whose first four actors trade name rows wholesale with its next four - `anole` against `grass
raptor`, `lindwurm` against `velociraptor` - at distance 4, plus two more at distance 1. That
is one race's allocation out of phase rather than 6 independent swaps.

**One pair has no observable effect**: actors `2206603` and `2206604` transpose their rows and
both display `kobold`, so nothing downstream can tell. The remaining 25 return a name that
belongs to a different mob.

Among those 25 there is a visible tendency but not a rule, and it is worth stating as the
weaker thing it is. In most pairs the lower actor holds the more specific name and the higher
the plainer one - `beryl crab` against `crab`, `musk roseling` against `roseling`, `stuffed
dodo` against `dodo`, `gnawing gnat` against `gnat`, `wandering wight` against `wight`, `Old
Six-arms` against `snipper`, `Gluttonous Gertrude` against `cockatrice`, `Prince of
Pestilence` against `ked`, `Barometz` against `landtrap`. The table carries no taxonomy
column - only the facts.

**The taxonomy this was first classified with mis-fired, in a way this file has hit before.**
Sorting the pairs by "proper name against common noun" using the client's capitalisation put
`Kokoroon Quickfingers` / `Qiqirn mercenary` and `Natali Xlotl the Howler` / `Ixali
bombardier` in the *unrelated* bucket, because `Qiqirn` and `Ixali` are capitalised tribe
adjectives, not individual names. Capitalisation is the best proper-name signal here and still
not a reliable one - the same limit the quest-page level floor ran into - so the classification
was dropped rather than patched with a list of tribe words.

`--verify` holds the row count, the distance set, race 1002's six, the single no-effect pair,
and that every row genuinely transposes - each name id being the other actor's parallel.

### The quest journals: quests target the field population, leves spawn their own

The leve briefings worked, so the same question for quests was overdue. It took two attempts.

**`xtx_quest` column 7 is the English description, and it is the wrong field.** Scanning it
attributes 12 mobs, all species or tribe words, and its single case checkable against GE -
`amalj'aa` - **disagrees outright**: the client's descriptions name it in 3 quests, GE's pages
in 13, and the two lists do not intersect. Descriptions narrate; they do not state objectives.

**The objectives live one indirection away.** Cells across a quest row carry
`[@SHEET(xtx/journalxtxWil,383,1)]` macros into four regional journal sheets - `Wil`, `Fst`,
`Sea`, `Roc` - whose column 1 is English, the same locale position the quest name uses.
Resolving them gives **273 quests with English objective text over 1,585 entries**, drawn from
1,943 journal rows. That count matching GE's 273 `Infobox Quest` pages is a coincidence, but a
useful one to notice.

Scanning that text with the same machinery as the leve briefings - one shared `scan_prose`, so
the two are measured identically, with the client's place names as decoys - attributes **115
mobs to a named quest, agreeing with GE's quest pages on 24 of 25**. A better rate than the
leve side's 33 of 37. `client_quest` carries it on both mob tables, 62 documented rows and 16
gap rows.

**And the two sources disagree about something that matters.** On the half worth trusting -
where the client names an individual rather than a species:

| Source | Attributions naming an individual | Holding a band-22 actor |
|---|---|---|
| leve briefings | 29 | **29** |
| quest journals | 55 | 38 |

**Every leve attribution is a band-22 mob. Only 0.691 of quest attributions are.** 17 named
individuals are sent after by a quest and have no leve deployment at all - `Audhumbla`,
`Cactuar Jack`, `Daddy Longlegs`, `Downy Dunstan`, `Gluttonous Gertrude`, `Haughtpox
Bloatbelly`, `Flamefist Ahlygg Roh`. Some of the 55 are the capitalised tribe adjectives this
file has been caught by twice, but those seven are unambiguously individual names.

So **quests reuse the persistent field population and leves spawn their own roster**. That is
the question the container sections left open and then explicitly withdrew a wrong answer to -
"a leve sends you after a persistent mob" was an artefact there, and the real distinction turns
out to run between quests and leves rather than inside either. `--verify` gates the margin
between the two sources rather than either figure alone, because the reading is the difference.

Two mechanical notes. The scan is bucketed by first character - same result, but the journal
text is far too long to try the whole 1,242-name vocabulary at every position. And a leve name
appearing on several rows now accumulates its briefings instead of overwriting them, which the
first version of the shared scan silently did.

### There is no "unrelated" class - that was the classifier, twice

The section above listed 6 pairs as having names with no relation at all. Chasing them
retires the category rather than explaining it, and it is the second time a classification of
these pairs has produced a fake bucket.

**The only relation the client asserts is race, and every pair has it.** All 26 pairs are
within one monster race *and* one band - 26 of 26 on both counts, now gated. There is no such
thing as a transposition between unrelated mobs; the question was only ever whether the two
*names* look related, and that is a question about English.

**On that question the honest count is 8 of 26.** A string test - shared head noun, or one
name inside the other as a whole word - links `gnawing gnat`/`gnat`, `wandering wight`/`wight`,
`stuffed dodo`/`dodo`, `musk roseling`/`roseling`, `beryl crab`/`crab`, `lunar golem`/`stone
golem`, `kobold`/`kobold` and `bomb ember`/`bomb`. The other 18 are 1.0 naming that no string
test can reach:

- **renaming inside a family** - `dapper cadaver` against `zombie`, `bomb baron` against
  `grenade`, `jackanapes` against `lemur`, `popoto-opoto` against `galago`. Cadaver and zombie
  are the same thing; so are bomb and grenade in the Final Fantasy bomb line; and race 1005 is
  `Opo-opo`, filing galagos, lemurs and jackanapes together as primates.
- **a notorious monster against its species** - `Prince of Pestilence`/`ked`, `Gluttonous
  Gertrude`/`cockatrice`, `Barometz`/`landtrap`, `Old Six-arms`/`snipper`, `Kokoroon
  Quickfingers`/`Qiqirn mercenary`, `Longnose Gnognoroon`/`Qiqirn goon`, `Natali Xlotl the
  Howler`/`Ixali bombardier`.
- **race 1002's block reorder**, whose race is `Raptor` and whose members include `anole` and
  `lindwurm` - a grab-bag race, so its pairs look unrelated for the same reason.

So the 8 is recorded as a count, and `--verify` pins it, but only as a measure of how far a
string test gets - not as a fact about the mobs. The lesson repeats what the tribe-adjective
misfire already showed: on 1.0 names, lexical tests under-report relatedness, and the honest
move is to publish the ids and the names and stop.

**What this does not settle.** Whether 1.0 leves ever did send players after persistent
mobs. The evidence that looked like it says nothing either way: GE's own prose draws the
distinction on 6 mobs with "Involved in the quest X", which is too few to measure, and the
client's briefings only name individuals - all of which are band 22. The question is open,
and the previous reading of it is withdrawn rather than reversed.

## The behavior codes are a six-code vocabulary, not a one-letter flag

`behavior_flags` was recorded here as an undocumented one-letter code with `H`
unexplained. It is neither undocumented nor one letter. GE's mob infoboxes resolve
each letter through a `Template:Mob Notes-<code>` page, none of which are in the
local corpus; all of them were harvested from the live wiki through
the MediaWiki API, together with the terminology pages they link to.
`mob-behavior-codes.csv` carries the result with a revision id per definition:

| Code | GE's definition | Used by 1.0 pages |
|---|---|---|
| `A` | aggressive - attacks on sight unless the player is far enough above it in level, or out of its line of sight | yes |
| `P` | passive - does not attack unless engaged | yes |
| `S` | detects players by sight | yes |
| `H` | detects players by hearing - triggers when a player passes nearby at a non-walking rate of movement | yes |
| `TH` | detects players by true hearing | yes |
| `L` | links - helps other mobs of its own kind | yes, one family (Raptor) |
| `TS` | detects players by true sight | no |
| `M` | detects players by magic use - triggers when a player casts nearby | no |

Eight codes exist wiki-wide; the 1.0 pages use six. The vocabulary is also
self-explaining once `TS` and `TH` are both in it: `T` is a modifier, so `S` is
Sight and `H` is Hearing.

**Read the definitions as ARR-era, not 1.23b.** The defining revisions date from
2017 to 2022 while the 1.0 mob and family pages were written in 2012. The letter
semantics are stable across that span - `Template:Monster Notes`, revised 2010,
already glosses `A` as aggressive and `L` as linking - but the specifics are not:
the `Aggressive` article's "11 or more levels above" threshold and the Stealth and
Hide abilities it names are ARR mechanics and must not be promoted as 1.x values.
Only the letter meanings are being claimed here.

The detection codes qualify `A` rather than standing beside it: both the sound and
the magic page say an *aggressive* monster attacks when the trigger fires. That
resolves what was recorded here as an open question - the 13 Crab mobs carrying
`P, H`, passive and sound-detecting at once, are a GE editor inconsistency and not
evidence that detection governs something other than the unprovoked attack.

## Where the codes live, and why a blank does not mean unknown

Three tiers carry behaviors, and GE's own template plumbing orders them:

| Tier | Rows | Vocabulary |
|---|---|---|
| `Mob Row`, one per sighting -> `mob-locations.csv` | 1,292 of 1,501 populated | `A` / `P` only, plus one stray `A, H` |
| `Infobox Mob`, one per mob -> `mobs.csv` | 24 of 824 | the full six codes |
| `Infobox Mob Family`, one per family -> `mob-families.csv` | 41 of 52 | the full six codes |

The one stray `A, H` on a sighting row is `Mossy Goobbue`, whose editor copied the
family value into a tier that otherwise only takes `A` or `P`.

The per-mob infobox is the override and the family page is the default: when a
mob's `Behaviors` is blank, GE's template pulls the family's value in through a
DPL include of the category page. So for that one field, **blank means "inherit
the family", not "unknown"** - which is the opposite of this set's general rule
that empty cells mean unknown. `Mob Row` has no such fallback, so a blank
sighting really is blank.

The ordering is not only read off the template - the sighting tier tests it. Of
the 24 mobs that set their own `Behaviors`, **18 disagree with their family**, and
in **17 of the 17 cases the sightings can decide** the sightings agree with the
mob page rather than the family. (The eighteenth, `Floating Eye`, has sightings
that contradict each other.) So the per-mob override wins on independent evidence
and not just on plumbing, which is what `--verify` gated in the retired tool:

```bash
python tools/map_client_mobs.py --client-dir <client-data-csv> --corpus <ge-pages-dir> --verify
```

It checks one fixture per tier and asserts that invariant, and it fails if the
precedence is reordered in either direction - both reorderings were tried.

`mob-behavior-resolved.csv` applies that precedence and resolves **780 of 824
mobs**, against the 505 that `aggressive` covers - 90 of them are mobs whose
`aggressive` cell is empty and whose family is aggressive, so reading empty
`aggressive` as "not aggressive" is wrong for at least those 90.

Two mobs, `Scout Wolf` and `Zombie Mage`, have sightings that disagree with each
other (`A` in one zone, `P` in another) and are marked `sighting-conflict` rather
than resolved. Thirteen more are truthy in `aggressive` while their family page
says passive; the family page loses to nothing in that comparison, because
`aggressive` is a per-mob field and is kept as the higher-precedence claim in the
`ge_aggressive` column for anyone who wants to re-adjudicate.

## The family pages were never mined, and they carry more than behaviors

GE's 52 mob-family pages live in the `Category:` namespace, which the miner skips
wholesale - correctly, since that skip is what stops the `Template:` sample calls
from mining as real rows. The cost was that `{{Infobox Mob Family}}`, which
appears **only** in that namespace, was never read at all. Category pages carry
no item, mob or mob-row infobox, so mining the family template out of the
category namespace cannot contaminate the other three passes.

`mob-families.csv` is the result: 52 families, every one of which is a family
named by at least one mob in `mobs.csv`, together covering 679 of 824 mobs. The
20 GE families with no page are mostly one-off or grouping labels (`Primal`,
`Unknown`, `Hyur`, `Magitek Armor`, `Juggernaut`, `Ascian`).

Beyond behaviors it brings `superfamily` - a taxonomy tier this set did not have
at all, grouping families into `Cloudkin`, `Spoken`, `Beast` and the rest - plus
family-level `element` and `weakness`. Those fill real gaps: `elemental_weakness`
is populated on only **72 of 824** mob rows, and family pages supply a weakness
for **175** more of the blanks. `element` fills 33. Twelve mobs state an element
that differs from their family's, which is the override working as designed, not
a defect.

The four prose params - `Description`, `Notes`, `Etymology`, `Raimdelle Codex` -
are deliberately not mined. They are the bulk verbatim prose these hub pages
exist to host (`Description` alone runs to a median of 439 characters), and
The downstream reference register admits GE as a factual baseline while
excluding verbatim GE prose.

## Three more upstream defects fixed while doing this

All three were in `tools/mine_gamerescape.py`, all three silently corrupted
values rather than dropping them, and all three are now fixed with the CSVs
regenerated:

- **`<br>` was stripped as a tag, jamming list entries together.** 29 materia
  rows read `Strength: +4, +5, +6Vitality: +4, +5, +6` - the two stats fused at
  `+6Vitality`. `<br>` inside a param is a list separator, so it now becomes a
  comma, or a plain space where the text already punctuates there (13 item
  descriptions and 1 mob note break mid-sentence).
- **Element icon templates reached the cells verbatim.** 44 of the 72 populated
  `elemental_weakness` cells held `{{Earth}}` rather than `Earth`, so any
  consumer grouping on the value saw `{{Earth}}` and `Earth` as two different
  weaknesses - and `{{Water}}<br>{{Wind}}` collapsed to `WaterWind`. Element
  templates now unwrap to the capitalized element name, and a run of them becomes
  a comma-separated list. `recipe_templates_raw` is exempt, since it exists to
  preserve wikitext verbatim.
- **`{{Verification}}` was mined as data.** It is an editorial maintenance tag
  and appeared in 2 `job` cells and 2 `notes` cells; it is now dropped like a
  comment.

Neither fix changed a row count (items 5,665, mobs 824, sightings 1,501) and
`map_client_columns.py --verify` still passed, so the item column map was
unaffected.

## The actor id encodes the monster race

A mob actor-class id is seven digits, and the middle of it is the
`xtx_monsterRace` id:

```
2 1 001 12     ->  race 1001 (Puk), variant 12
^ ^ ^   ^
| | |   two-digit variant within the race
| | race id, leading 1 implied by the block
| allocation band (the 21 / 22 / 23 prefix)
leading 2
```

So `race_id = 1000 + digits 3-5`. That resolves **699 of the 812 joined mobs** to
one of **78 named races**, and scoring the race against GE's `family` gives
**0.9943 purity** - 5 rows off-dominant out of 812. This was found by testing the
id's *structure*, the same technique that showed the item id encodes equip kind;
the earlier search only ever tested column *values*.

The 21 / 22 / 23 band is not part of the race. It is not notorious-monster status
(10%, 18% and 17% of each band are NMs), and the two large bands span the whole
level range - in GE's own level fields, which carry out-of-range typos, 21 runs 1
to 90 and 22 runs 1 to 60, so both cover essentially the full ladder rather than
sitting at a tier. The small band is the exception worth recording: **every one
of the 38 mobs in the 23 band with a known level sits at 35 or above** (35 to 59),
so it is not an arbitrary split. What it actually selects for - instanced dungeon
content - is established above ("The 23 band is instanced content"); the race link
does not depend on it.

### It resolves the vocabulary problem outright

The family rosters were recorded here as differing by vocabulary, with a
string-similarity `nearest_unmatched` column that "catches the typo pairs but not
the synonym pairs". The race link catches all of them, because it never looks at
spelling. **68 of GE's 72 families now have a client counterpart, against 48 by
name matching** - 21 pairings the name match could not make, including six where
the client's English column is untranslated and still holds the Japanese working
name (romanized here; the CSVs carry the client's own characters):

| GE family | Client race | Mobs |
|---|---|---|
| Rodent | Rat | 27 |
| Landtrap | Flytrap | 24 |
| Diremite | Crab, race 1011 | 19 |
| Wisp | *youka*, provisional | 16 |
| Mole | Hedgemole | 15 |
| Fomor | Zombie | 14 |
| Amalj'aa | Amlaj'aa | 14 |
| Aurelia | Jellyfish | 12 |
| Ram | Sheep | 12 |
| Beetle | Weevil | 11 |
| Cactuar | Sabotender | 9 |
| Toad | Gigantoad | 8 |
| Moogle | *moguri* | 7 |
| Snurble | Phurble | 4 |
| Enemy Humanoid | Imperial | 3 |
| Golem | Golem 1.2 | 2 |
| Plasmoid | *wiru-o-wisupu*, Will-o'-Wisp, provisional | 2 |
| Coeurl | Couerl | 1 |
| Chimera | *kimaira*, provisional | 1 |
| Cyclopes | *saikuropusu* | 1 |
| Magitek Armor | *kiraa mashin*, Killer Machine, provisional | 1 |

"Provisional" is the U+4EEE *kari* marker the client leaves on internal working
names, as elsewhere in this file.

The full many-to-many pairing with per-race and per-family shares is
`mob-race-crosscheck.csv`, 82 rows. `Cactuar` is the case the old note called out
as unfixable - similarity proposed `Salamander` and missed `Sabotender` entirely.

### Two client races are both called Crab

Race **1011** and race **1076** carry the same English name and are different
animals: 1011 is GE's `Diremite` (19 mobs, no exceptions) and 1076 is GE's `Crab`
(18 mobs, no exceptions). Joining the taxonomies on the English name merges them
into one bucket that then appears to straddle two GE families. **Key the join on
the race id.** `--verify` asserts these two stay distinct, and fails if anything
reverts to a name join.

### The four families with no race pairing, and the 113 mobs with no named race

`Elemental` and `Primal` are unpaired only because the pairing is reported at
majority: the client splits Elemental into Air / Earth / Fire / Ice / Lightning /
Water so no single race is a majority of GE's ten, and `Primal` divides between
races `Ifrit` and `Garuda`. Both are visible in `mob-race-crosscheck.csv`.
`Hyur` (1 mob) and `Unknown` (5) are GE grouping labels with nothing to pair to.

113 GE mobs derive a race id that `xtx_monsterRace.csv` does not contain. Counted
over the whole client roster rather than just GE's mobs, it is **9 field values
covering 567 of the 2,662 monster-range actors**. `mob-race-blocks.csv`, with
`client_names` as the shape column - a roster carries many display names, a single
race carries one:

| Race id | Actors | Names | Humanoid | GE mobs | Reading |
|---|---|---|---|---|---|
| 1801 | 169 | 76 | 145 | 37 | brigands, plus most of the lunatic cult |
| 1800 | 117 | 35 | 88 | 28 | Garlean imperial legion |
| 1900 | 98 | 54 | 19 | **0** | friendly NPCs that fight: hamlet militia, story allies, escort targets |
| 1620 | 61 | 24 | **0** | 16 | a second Amalj'aa roster, named by office and stronghold |
| 1802 | 44 | 23 | 42 | 13 | pirates - buccaneers, Black Crow, Kraken, Mistbeard |
| 1890 | 44 | 35 | 42 | 15 | named opponents of scripted fights |
| **1110** | 24 | **1** | **0** | 1 | **not a block: the missing race Atomos** |
| 1803 | 5 | 5 | 3 | 3 | the Serpent Reavers, plus the tail of the lunatic cult |
| 1910 | 5 | **0** | 4 | 0 | humanoids named at runtime |

**The count was 8, and it is 9.** Block 1910 has five actors and not one carries an
English name, so every survey that started from the named roster missed it. Counting
over all monster-range actors rather than only named ones is what surfaced it, and
that is now how `mob-race-blocks.csv` is built.

The readings come from the display names of the actors in each block, which are
unambiguous once grouped: 1800 is 117 variants of `imperial trooper` and GE names
the same mobs by Roman legionary rank (`Elite Bestiarius`, `Eques`, `Funditor`,
`Hoplomachus`, `Laquearius`, `Medicus`); 1802 is buccaneers. 1890 is the exception
that is not a faction at all - see below.

### 1800 is one rank ladder deployed five times, and GE is missing a whole rank

Block 1800 was the only race in the set whose 23-band zones would not pin to a single
dungeon, and reading its zones explains why: it is not scattered, it is **five separate
deployments of one roster**, and GE files them all under one name apiece.

The spine is a ladder of **seven line ranks** - secutor, hoplomachus, laquearius, eques,
sagittarius, medicus, signifer - each shipped in **three tiers**. The client lays them out
in runs of seven consecutive actor ids, five such runs across the block's 117 actors, plus
16 generic `imperial trooper` and a second vocabulary of skirmish ranks (triarius,
retiarius, hastatus, speculator, bestiarius, funditor, veles, myrmillo, imaginifer).

**What picks the deployment is the tier and the rank family, not the id band:**

| Tier + rank family | GE mobs | Level | Zones |
|---|---|---|---|
| `imperial` line | 6 | 50-55 | Castrum Novum, Coerthas Central Highlands |
| `VIIth Legion` line | 6 | 54-55 | Castrum Novum, Mor Dhona |
| `elite` line | 6 | 56 up | Castrum Novum |
| `imperial` skirmish | 6 | 22-52 | East Shroud, the Dzemael Darkhold |
| `elite` skirmish | 4 | 30 to 50 up | Central Shroud, Central Thanalan, Coerthas Eastern Lowlands, Lower La Noscea |

The level is near-constant inside a group - every `imperial` line mob is 50, every
`VIIth Legion` 54, every `elite` line 56, every `elite` skirmish 30 - which is what a
deployment looks like rather than a species. The `elite` skirmish row is the
hamlet-invasion attacker set, roaming four field zones and holding the block's only two
notorious monsters; `populaceWaveAttack.csv` calling these imperial troopers is what the
earlier hamlet reading rested on, and it turns out to describe one of the five, not
the block.

**GE is missing `sagittarius` in all three tiers.** The client carries all 7 line ranks in
each of the 3 tiers, 21 mobs; GE documents 6 of 7 in each, and the rank it omits is the
same one every time. 12 actors in the block are a sagittarius - the second most numerous
rank after the generic trooper - and no GE page mentions one. A single miss would be an
oversight; the same miss repeated across three tiers that were edited independently is a
hole in the roster GE worked from. `--verify` asserts the client ladder stays complete,
that `sagittarius` stays the only absentee in every tier, and that the ladder is measured
over exactly the block's 117 actors and not a wider slice.

**Why the zone list looks scattered, and the limit that causes.** GE documents by *name*,
and one name owns actors in several bands - `Imperial Hoplomachus` has actors in 21, 22
and 23 - so its page's zone list is the union over deployments and cannot be split back
per actor. That is the whole of race 1800's apparent scatter.

### The 2380001-2380008 run, and the display-name id is its own namespace

That run was left here as a prediction: eight consecutive band-23 actors, three of them
placed by GE in the Dzemael Darkhold, so the five line ranks beside them were probably
Darkhold content too. Following it up **broke the premise**. The run is not one block by
the only client evidence available - it points into two separate runs of the name table:

| Actors | Names | Name ids |
|---|---|---|
| 2380001-2380003 | veles, myrmillo, speculator | 3207007-3207009 |
| 2380004-2380008 | hoplomachus, laquearius, sagittarius, signifer, medicus | 3307002-3307006 |

The three GE places in the Darkhold are exactly the first group. Each name run is also
headed by an `imperial primus ordinarius` row - 3207005 and 3307001 - which reads like two
squads each under an officer, but reads is all it does. **The prediction is neither
confirmed nor refuted, and the "single deployment" wording that framed it was wrong.**

Chasing those name ids corrected something that matters more widely. **A display-name id
is not the actor id with its leading 2 turned into a 3.** That parallel holds for 1,587 of
the 2,662 monster-range actors and fails for the other 1,075, and the name table contains
rows no actor of the parallel id claims - name id 3307002 exists while actor 2307002 exists
separately and points at 3307001. The two sequences were allocated alongside each other,
not derived from one another, so anything reasoning from an id has to follow the pointer.
What the off-pattern rows carry is name *sharing*: 227 name rows are pointed at by more
than one actor, which is where `actor_id_count` comes from. `--verify` fails if either
property stops holding, because both are assumptions this tool is built on.

### Race 1070 and block 1800 are the Garleans in two namespaces

The same split the Amalj'aa have across race 1065 and block 1620. Named race **1070**
holds the officer ranks over 13 actors - centurion, pilus prior, primus ordinarius - and
block **1800** holds the line and skirmish ranks over 117. Every named actor in both
spaces carries one of the three tier prefixes, which is what makes them one faction across
two id spaces rather than a resemblance; `--verify` checks that purity, anchors it on named
ranks so it cannot pass by finding nothing, and proves the test still discriminates against
a control name, since its true answer over both spaces is empty.

GE's coverage of the officer ranks is patchy rather than systematic, unlike the sagittarius
hole: it documents `VIIth Legion centurion`, `imperial pilus prior` and `imperial primus
ordinarius`, and misses `imperial centurion` (**6** actors across bands 21 and 22 - an
earlier draft here said 5), `VIIth Legion pilus prior` (1) and `imperial guy` (1, which is
a working name rather than content).

### Why `imperial centurion` has no mob page: GE's quest pages were never mined

`imperial centurion` was one of the 48 unbracketed gap names, and the reason it has no mob
page is not that GE never saw it. **GE wrote it up inside a quest.** `Futures Perfect`
(revision 176321, 2012-07-28) is an `Infobox Quest` page for a main-scenario quest whose
objectives are to chase a fleeing Imperial Centurion inside an instance. A mob mine sees
`Infobox Mob`, `Mob Row` and `Infobox Mob Family`, so instanced quest content written up
as walkthrough steps was invisible to it.

The same walkthrough **corroborates the sagittarius hole from the section above**: it
names the Hoplomachus and the Sagittarius escorting the Centurion. So the rank GE has no
mob page for anywhere, across all three tiers, is attested in GE's own quest text.

`mob-quest-attribution.csv` generalises this. **71 of the 468 undocumented client mob
names are mentioned in one of GE's 273 quest pages**, 35 of them `ge-gap`, and the page
names the content the mob belongs to - `clay golem` to `Their Finest Hour`, `coincounter`
to `What Glitters Always Isn't Gold`, `bloodhound` to `Of Men They Sing`. That is a
harder attribution than any of the neighbour hints above, because it identifies actual
content rather than interpolating between other mobs.

**These pages are a better tier than the behavior-code templates.** All 273 were last
edited in 2011 or 2012, so unlike the ARR-era `Template:Mob Notes-*` revisions they are
contemporaneous 1.x observation. `--verify` fails if that stops being true.

Three limits on the file:

- **Only the attribution is stored, never the walkthrough text.** The register this
  corpus is harvested under excludes verbatim GE prose, and some of these walkthroughs
  carry observations worth having - one records a Rank 46 Thaumaturge taking 9,200 from an
  Imperial Juggernaut's cannon. Read them in the corpus; they are not copied here.
- **A name that only occurs inside a longer one is dropped.** `billygoat` is an
  undocumented client name in its own right, but in this corpus it appears only within
  `death-marked billygoat`, so each hit is the longest undocumented name matching at that
  point in the page. `--verify` asserts `billygoat` stays unattributed, which is what
  catches the rule failing.
- **Short species names are unreliable even so.** `amalj'aa` collects 13 quest pages
  because the word appears in prose about the tribe, not because a mob called exactly
  `amalj'aa` features in all 13. Rows whose `likely_cause` is `race-name-only` should be
  discounted for that reason.

The corpus is local-only and gitignored, so this one output is skipped rather than emptied
when it is absent, and the committed CSV stays the canonical product.

### The quest infobox turns the attribution into the best level statement in the set

The mention alone says which content a mob belongs to. The quest's own infobox says at what
level, and `Minimum Level` is filled on **263 of the 273** pages. Measured against the
documented mobs those pages mention, it is a **floor** rather than an estimate:

| Claim | Support |
|---|---|
| the mob's `level_low` is at or above the quest's minimum level | 150 of 167 pairs, 0.898 |
| ... and within 10 levels above it | 0.754 |
| median distance above | +5 |

That beats the flanking bracket outright - 0.754 inside a 10-level band against 0.530 - and
it is the only level statement here derived from the content the mob appears in rather than
interpolated between other mobs. `quest_level_floor` carries it. **49 of the 71 rows get
one, 28 of them `ge-gap`**, spanning level 10 to 46 with a median of 27.5, and six of the
48 names that no bracket could reach now have a level: `clay golem`, `goblin robber`,
`good king moggle mog xii`, `imperial centurion`, `nael deus darnus` and `nael van darnus`.
Where a name appears in several quests the floor is the *lowest* of them, which is what a
floor means.

`quest_classification` is carried alongside - Class Quest 21, Sidequest 19, Grand Company
Quest 17, Main Scenario 17 - and Class Quests are the weakest group, at 0.63 above rather
than 0.90, since a class quest is level-gated to the class rather than to the mob.

#### What decides eligibility is the client's capitalisation, not the word count

The floor was first withheld from every one-word name, on the reasoning that a one-word
mention is the species in prose. Splitting that population by the client's own casing - the
same proper-name signal `undocumented_cause` already uses - shows the word count was a proxy
for the wrong thing:

| Population | Pairs | Floor holds | Within 10 above |
|---|---|---|---|
| multi-word | 167 | 0.898 | 0.754 |
| one word, capitalised in the client | 15 | 0.867 | 0.867 |
| one word, lower case in the client | 37 | **0.595** | 0.459 |

A capitalised one-word name holds the floor as well as a multi-word one and is *better* on
the 10-level band; a lower-case one is a coin flip. So the rule is now multi-word **or**
capitalised, which brings `Audhumbla` and `Coincounter` in at level 45 and leaves
`bloodhound`, `shrieker`, `minemite`, `nannygoat` and `hellhound` out. `client_proper_name`
records the signal so the rule is auditable from the file, and `--verify` pins it in both
directions - a column that always claimed "proper name" would otherwise satisfy the
lower-case invariant by itself.

**Two causes are excluded whatever the casing**, because the floor is a claim about a mob's
level and neither marks a mob. `race-name-only` is the species-word class by definition -
`Amalj'aa` is capitalised and appears in 13 quests as the tribe. `not-a-monster` is the 1900
block of friendly NPCs, where Thancred, Y'shtola, Papalymo and the Ishgardian knights have
no level to floor; that also correctly removed `brazen-faced broker`, which the word-count
rule had given one.

The support floor in `--verify` is 0.88 rather than 0.85 deliberately: the eligible
population scores 0.896 and every name regardless of casing scores 0.859, so a gate in
between fails if the figure is ever measured over a wider population than the floor is
published for.

#### The 21 rows with no floor are all explained

| Why | Rows |
|---|---|
| `not-a-monster` - story NPCs, no level to floor | 12 |
| one word, lower case in the client - measured at 0.595 | 5 |
| `race-name-only` - `amalj'aa` and `elemental`, tribe and element words in prose | 2 |
| eligible, but their quest leaves `Minimum Level` empty | 2 |

The last two are `deadly nightshade` in `Oil Crisis` and `kikkiroon irongut` in `It's a
Piece of Cake to Bake a Poison Cake`, and both quests have the field present and blank - a
gap in GE, not a rule. Nothing further is extractable here: every remaining blank is either
a deliberate exclusion with a measurement behind it or an empty field upstream.

**One defect worth recording, because it read as healthy.** The first version of the
infobox parser matched field lines with `^\s*\|...$`. Its `\s*` crosses a newline, so a
match starting at one line's `^` could swallow the next field's line, and it silently
dropped roughly every other field - 52 pages with a level instead of 263. Nothing looked
wrong; it was caught only because an exploratory script and the tool disagreed. The parser
now splits on the leading pipe of each line, and `--verify` requires at least 250 pages to
parse a level, which is what makes that class of bug loud.

Two synthetic mutations of this section deliberately go uncaught, and both are benign:
splitting fields on every `|` rather than each line's leading one only corrupts values that
contain a pipe, and neither field used here does; and relaxing the 2013 era limit cannot
produce a false claim while every page in the corpus is 2011 or 2012.

### The client dump has no actor-to-anything table

Worth stating once, because it bounds every zone and level question in this file. All 803
files of the client dump were searched for monster-range actor class ids; the only ones
that carry them are `actorclass.csv` and `actorclass_graphic.csv`. The two apparent
further hits, `var_equip.csv` and `var_wep.csv`, are float tables keyed by model id and
the match was a substring collision inside a longer number. **There is no spawn table, no
actor-to-zone link and no level anywhere in the dump.** Every zone and level statement in
this set therefore comes from GE, which is why the hints above are hints.

### 1803 is the Serpent Reavers, and blocks are not closed sets

Recorded here first as "Serpent Reaver body parts and strays". Both halves were
wrong. The block is five actors: `Serpent Reaver claw`, `Serpent Reaver fin`,
`Serpent Reaver eye`, `lunatic lamb` and `lunatic shepherd`.

**The Serpent Reavers are an organization, and `claw` / `fin` / `eye` are its
ranks** - not parts of one creature. GE carries a `Serpent Reavers` page as an
`{{Infobox Organization}}`, describing a group of pirates with Sahagin connections
operating around Limsa Lominsa, and its quest dialogue puts it plainly: they are
men and women who sold their swords to the Sahagin. The rank reading is confirmed
mechanically rather than by lore - GE gives each a class, `Claw` a Gladiator, `Eye`
an Archer and `Fin` a Marauder, which body parts do not have. All three are level 45
in `Mistbeard Cove`, one of this set's 1.x-only zones, and GE's own quest text says
"All Serpent Reavers are level 45". So 1803 continues the faction run: 1802 is the
ordinary pirates, 1803 is the Sahagin-sworn ones.

**The other two are not strays either.** They are the tail of a cult: the client
also ships `lunatic follower`, `lunatic priest` and three more `lunatic lamb`
actors, and GE's `Blood Price` quest has the player defeat four Lunatic Lambs and
the Lunatic Shepherd. But those other five actors sit in block **1801**, so the cult
is split 5-2 across 1801 and 1803 - and `lunatic lamb` itself appears in both, three
actors in 1801 and one in 1803.

That generalizes something seen once before and now twice: **an organization can
span two blocks.** The Amalj'aa are split across race 1065 and block 1620, the
lunatic cult across blocks 1801 and 1803. A block is an allocation, not a closed
set, so do not treat "same block" as "same group" or "different block" as
"different group". `--verify` asserts the cult still spans at least two blocks, so
the pattern stays witnessed rather than remembered.

**The 18xx blocks are faction, not species, and GE proves it.** GE files 95 of the
113 as the single family `Enemy Humanoid`, while GE's `subfamily` for them is a *playable race* that
varies inside every block - 1801 spans Miqo'te, Lalafell and Hyur; 1890 spans Hyur,
Lalafell, Roegadyn and Miqo'te. A species axis cannot do that. So for humanoid
enemies the client's field carries the organization and the species lives in GE's
`subfamily`; the two are orthogonal and neither source has both. **That argument is
specific to 18xx** and does not carry to 1620, where every member is one species -
see below.

**No table in the client dump names these blocks.** All 803 CSVs were searched by
row key in both the raw form (`801`, `800`) and the offset form (`1801`, `1800`);
the only hit was a coincidental id overlap in `xtx__fixedPhrase.csv`.
`tribe.csv` and `xtx_tribe.csv` are the 16 playable clans, ids 0-15, and are not
it. Naming them would need a decomp or a later client.

Four of the nine are not factions - 1110, 1890, 1900 and 1910, each below.

### 1910 is five humanoids named at runtime

Recorded here first as unknown, on the grounds that no actor carries an English name.
That was the wrong conclusion from the right observation: the name is not missing, it
is **deliberately variable**, and the client says so.

All five actors point at the same `xtx_displayName` row, **id 2**, whose Japanese
reads U+53EF U+5909 - *kahen*, "variable" - and which carries the same U+4EEE
provisional marker used elsewhere for internal working names. Its English, German and
French columns are the untranslated placeholders `[en]`, `[de]`, `[fr]`, which is why
every name-based survey saw nothing. Row 2 is a sentinel, not a name. **129 actors
point at it, 116 of them in the 10 quest-actor range**, so a runtime-assigned name is
mainly a quest-actor device and these five are its monster-range members. Row 1 is
the same kind of thing, a row of dashes.

They are people rather than creatures, and that is measurable: **4 of the 5 populate
the humanoid appearance run** in `actorclass_graphic` columns 15-21, which no actor of
any named monster race populates at all. Their overall column shape matches the
humanoid faction blocks - a median of 21 populated columns against 20 for those
blocks and 6 for monsters.

So: five humanoid actors whose name is supplied at runtime. **What supplies it is not
in the sheets**, and unlike the other blocks there is no roster to read, no GE mob and
no dialogue table to corroborate against. That part stays unknown, and it is a
different kind of unknown from before - the block is characterised, only unnamed.

### 1110 is not a block at all: it is the missing race Atomos

This was recorded here as "possibly a truncated race rather than a faction". It can
be settled, and it is a race. Four things line up:

- **It has the shape of a race, not a roster.** All 24 of its actors carry the single
  display name `Atomos`. Every genuine block is a roster of many names - 76 for 1801,
  54 for 1900, 35 each for 1800 and 1890, down to 5 for the smallest - running 1.0 to
  3.3 actors per name. 1110 runs **24 actors per name**, the most lopsided value
  anywhere in the space.
- **That shape is exactly what the single-creature races look like.** Eleven named
  races also have one display name each, and they are the same kind of thing:
  `Titan`, `Ascian`, `Dragon`, `Wyvern`, `Juggernaut`, `Hellhound`, and
  Air / Lightning / Water Elemental at 13 actors apiece. GE files its one Atomos mob
  under the family `Primal`, alongside Titan.
- **It is contiguous with the table.** Race ids 1100 to 1109 are all present and
  populated, and 1110 is the immediately following value. The next block after it is
  1620, far away. A faction namespace does not begin one step past the end of the
  race table.
- **The table was still growing.** Its last four rows, 1106 to 1109, are untranslated
  Japanese working names, so this dump caught `xtx_monsterRace` mid-append. There are
  also 20 unused gaps inside 1001-1109, which is the one point against - a new race
  could have reused a gap instead of extending the end.

`Atomos` appears nowhere in `xtx_monsterRace` under any id, so nothing contradicts
the reading. `--verify` asserts 1110 stays at one display name and that no roster
block falls below five, which is what keeps the discriminator meaningful.

### 1890 is the scripted-opponent block, not a faction

This was first recorded here as "Ala Mhigan resistance and tempered captives". That
was two visible name clusters mistaken for the whole: the block is 44 actors and
**35 distinct names**, and once they are all listed the Ala Mhigans are 6 of them.
The rest are job-quest champions (`Curious Gorge`, `Estinien Wyrmblood`,
`Widargelt the Watcher`, `Jenlyns Straightblade`, `Rowland of the 99 Blades`),
coliseum challengers (`Toothless Gladiator`), Grand Company and bandit duel squads
(`maelstrom marauder` / `brute` / `archer`, `immortal bladedancer` /
`lightspinner` / `speardancer` / `shadowspinner`, `bandit butcher` / `lancer` /
`grappler` / `archer`), and a dozen one-off named characters.

What they have in common is not who they fight for but **that each is a scripted
fight**, and two measurements separate the block from every other:

| Block | GE mobs | Notorious | Tied to a named quest |
|---|---|---|---|
| **1890** | 15 | **14, 93%** | 13, 87% |
| 1801 | 37 | 0, 0% | 30, 81% |
| 1800 | 28 | 2, 7% | 14, 50% |
| 1802 | 13 | 1, 8% | 7, 54% |
| 1620 | 16 | 2, 12% | 0 |
| every named race | 699 | 86, 12% | 258, 37% |

93% notorious against a 12% baseline is the discriminator; `--verify` asserts the
block beats the baseline by at least three times, and fails if pointed at any of the
rank-and-file blocks. The quests are named in `mob-locations.csv` and are the
ordinary 1.x story and side content - `Thrill of the Fight`,
`All Bark and No Bite` and `The House Always Wins` in Ul'dah at levels 20 to 36,
`Return of the King...of Ruin` in Mor Dhona at 53 to 55,
`Into the Dragon's Maw`, `Parley on High Ground`, `Unalienable Rights`,
`Two Sides to Every Chip`, `Lord Errant`.

The id itself supports the reading: the faction run is 1800, 1801, 1802, 1803 and
then stops, and **1890 sits past a deliberate 86-value gap** rather than continuing
the run as 1804 would.

`Tempered Captive` is the one GE mob here filed outside `Enemy Humanoid` - GE gives
it the family `Hyur`, which is reasonable for a captive person and is the single
family exception in the block.

### 1900 is the ally side of the same battle as 1800

98 actors, 54 distinct names, **all of them in the 22 range** with variant digits
running 01 to 98 as one flat sequence, so the client does not subdivide it. What
they are, grouped by name:

| Group | Names | Actors |
|---|---|---|
| Hamlet militia | 7 | 42 |
| Named story allies | 28 | 32 |
| Escort and quest targets | 14 | 19 |
| Grand Company scouts | 3 | 3 |
| Placeholders | 2 | 2 |

The militia is the largest component and the one that identifies the block:
`militia barber`, `militia cook`, `militia outfitter`, `militia smith`, and
`militia front line archer` / `second line archer` / `third line archer` - trade
NPCs given battle positions. `populaceWaveAttack.csv`, the 22-row dialogue table
for that content, says what they are for: a hamlet is invaded, the Grand Companies
do not come, and *"my kinsmen and I have formed a militia"*. The same table calls
the attackers **imperial troopers**, which is the display name of all 117 actors in
block **1800**.

So the two blocks are the two sides of one fight, and that is the reading:
**1900 is friendly NPCs that take part in combat.** It independently corroborates
1800 as the Garlean legion, which had rested only on the actor display names.
`PopulaceHamletCaptain.csv` is the same content's captain, 39 rows of battle
dialogue including a desertion branch.

The rest of the block fits: the three Grand Company units are one each -
`flame scout`, `storm scout`, `serpent patrol` - the named allies are the 1.0 story
cast who fight alongside the player (`Y'shtola`, `Papalymo`, `Yda`, `Thancred`,
`F'lhaminn`, `Sthalmann`, `Niellefresne`, `Grinnaux`, `Handeloup`), and the generic
entries are escort objectives (`missing miner`, `frightened foreman`,
`wounded rebel warrior`, `beleaguered botanist`).

Three checks that the reading holds:

- **Zero GE mobs land in the block**, which is what `--verify` asserts, along with
  the militia names still being in it.
- **GE documents 25 of the 54 as `Infobox NPC` pages**, so GE filed them correctly
  as NPCs rather than missing them as mobs. 28 have no GE page at all.
- **Exactly one has an `Infobox Mob` page: `spriggan`**, and that is a name
  collision, not a misfiling - real spriggan mobs exist on actors `2106208` and
  `2106209` in race 1062, and the 1900 entry is a separate actor that happens to
  share the name.

Consequence for the roster list: 52 of the 468 rows in
`client-mobs-without-ge-page.csv` are this block, and they are **not gaps in GE's
coverage** - they were never monsters. That file now carries the race field so they
can be excluded. The 53rd and 54th names are not block rows at all: `???` belongs to
race **1101** and `****` to race **1106**, both of them named races whose *display*
name is a placeholder, so neither is attributed to a block.

**The Amalj'aa are split across both namespaces**, which is the clearest single
illustration: 15 GE Amalj'aa mobs carry race **1065** (`Amlaj'aa`, the client's own
typo) and 16 carry block **1620**. Anything keying on race alone will treat them as
two unrelated groups. What the split actually is, below.

### 1620 is a second Amalj'aa roster, named by office rather than job

It is the only 6xx value, which is itself worth noting: every other beast tribe -
Ixal, Kobold, Sylph, Qiqirn, Goblin - has an ordinary `xtx_monsterRace` entry and
no second block. Only the Amalj'aa got one.

| | Race 1065 (`Amlaj'aa`) | Block 1620 |
|---|---|---|
| Client actors | 89 | 61 |
| Distinct names | 30 | 24 |
| Actor-id ranges | 21 and 22 | 21 only |
| GE mobs | 14 | 16 |
| GE levels | 30 to 65 | 27 to 59 |

**The naming is near-disjoint**: 28 names appear only in 1065, 22 only in 1620, and
just two in both (`Amalj'aa bowyer`, `Amalj'aa lancer`). The two vocabularies are
different in kind, not just in content:

- **1065 names a job or a species trait** - archer, augur, drudge, grappler, grunt,
  halberdier, impaler, mesmerizer, pugilist, shaman, striker, trooper, warrior, plus
  three notorious monsters.
- **1620 names an office or a place** - the `Zahar'ak` garrison carries clerical
  titles (`chandler`, `feretrar`, `illuminator`, `ostiary`, `scriniary`), which suits
  a tribe organized around Ifrit worship, and the `Burned Brother` / `Burned Sister`
  / `Burned Scrivner` set reads as converts. The rest are hunting-party roles -
  hunter, ranger, scout, seer, stargazer, harpooner, javelineer.

**What this is not.** It is not a map split: `Zahar'ak` accounts for 9 of the 16 GE
mobs but 5 more sit in Western Thanalan at level 27 and one in Eastern Thanalan,
which race 1065 also occupies. It is not a level tier either - 27 to 59 against 30
to 65. And it is not tied to the place id: `Zahar'ak` is `xtx_placeName` 3521,
already classified in `zone-client-crosscheck.csv` as `client-place-not-a-zone` with
12 sightings, and 3521 has nothing to do with 620.

**What is not established.** The organizational reading here rests only on the
naming. The 18xx blocks could be shown to be a faction axis because GE's species
field varied inside them; block 1620 is one species and one GE family throughout, so
that test has nothing to work on. Read 1620 as a second allocation whose naming is
organizational - not as a proven faction axis.

One date is available, from the item side rather than the mob side: the four
`Zahar'ak Coffer Key` items carry `patch_introduced` **1.19**, so the content this
block serves existed by 1.19 and the block is not a late-1.x addition.

### Only 4 races split across GE families, and each one is a GE defect

- `Opo-opo` (1005) splits 13/1 because **GE spells the same family two ways**,
  `Opo-opo` and `Opo-Opo`, which is why the family count reads 72.
- `Bomb` (1016) splits 13/1: one mob is filed under GE `Wisp`.
- `Ifrit` (1073) and `Garuda` (1095) split 1/1 between GE's `Primal` and `Unknown`.

Nothing else. The taxonomies agree wherever both sides are clean.

## Family taxonomies do not line up, in both directions

This section is what the name-only comparison showed, and it is kept because it
documents *why* the two vocabularies differ. For the mapping itself, use
`evidence_counterpart` and `mob-race-crosscheck.csv`, not `counterpart` -
name matching pairs 48 of GE's 72 families, the race id pairs 68.

`mob-family-crosscheck.csv` lists both rosters. 48 of GE's 72 families have a
client counterpart by name, after allowing for the client's plural and compound
forms (`Aldgoats`, `Wolf/Hyena/Hellhound`). The residual is vocabulary, not
missing content, and it cuts both ways:

- **The client uses internal dev names**: 67 of its 89 Japanese race names still
  carry the provisional marker "kari" (U+4EEE). Where GE writes the player-facing
  name, the client writes its own - `Cactuar`/`Sabotender`, `Aurelia`/`Jellyfish`,
  `Rodent`/`Rat`, `Ram`/`Sheep`, `Landtrap`/`Flytrap`, `Toad`/`Gigantoad`,
  `Mole`/`Hedgemole`.
- **The client is more granular in places**: GE's single `Elemental` is
  Air/Earth/Fire/Ice/Lightning/Water Elemental client-side, and it carries a
  patch-annotated `Golem (1.2)` alongside `Golem`.
- **The client has typos of its own**: `Amlaj'aa` for Amalj'aa and `Couerl` for
  Coeurl. GE has both right. Neither source is clean.
- GE carries grouping labels the client has no concept of at all -
  `Enemy Humanoid`, `Primal`, `Unknown`.

The `nearest_unmatched` column suggests a counterpart by string similarity, which
catches the typo pairs but not the synonym pairs: it proposes `Salamander` for
`Sabotender` and misses `Cactuar` entirely. Read it as a hint, not a mapping - the
race id is the mapping, and it gets `Cactuar` right.

## Two upstream data defects fixed while doing this

Both were in `tools/mine_gamerescape.py` and both are now fixed, with the CSVs
regenerated from the local corpus:

- **HTML entities were not decoded.** 127 item names and 14 mob names carried
  `&#39;` instead of an apostrophe (`Amalj&#39;aa Grappler`). `clean()` now runs
  `html.unescape` first. The item column map was unaffected because its
  `ge_page_title` fallback happened to rescue all 127, but anything keying on
  `item_name` or `mob_name` would have missed them.
- **Template-namespace pages were mined as content.** The `Infobox Mob`
  definition pages carry a sample call of the template they define, so
  `Template:Infobox Mob`, `Template:Infobox Mob2` and
  `Template:Infobox Mob/Preload` mined as three mobs named
  `{{subst:PAGENAME}}`, plus 6 phantom sightings. `load_pages` now skips
  non-article namespaces.

Net effect on the set: mobs 827 -> 824 rows, mob sightings 1,507 -> 1,501,
distinct mobs in `mob-locations.csv` 825 -> 822. Items stayed at 5,665, and every
other quoted statistic (769 `level_low`, 458 `hp_low`, 106 notorious monsters, 72
families, 51 zones) is unchanged - the removed rows were empty placeholders.
