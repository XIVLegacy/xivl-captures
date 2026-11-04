# Skirmish and Behest content evidence

Official patch notes announced Skirmish sites, admission requirements and
waits, and Behest signup and enemy-level rules. The promoted Gamer Escape
tables add named mob/site associations and Skirmish spawn descriptions.
These are announced intent and wiki evidence, respectively. Neither establishes
an observed 1.23b encounter, runtime Director identity or server policy.

## Sources and interpretation

- [Gamer Escape study](../studies/gamerescape-tables/README.md),
  [source manifest](../sources/gamerescape-tables/manifest.yaml) and
  [evidence map](../studies/gamerescape-tables/derived/evidence-map.md):
  `web-tables`, wiki tier. The tables combine page revisions from different
  versions. Revision timestamps date edits, not observations.
- [Official timer announcements](../studies/lodestone-dev-patch/derived/timer-announcements.md)
  and the [Lodestone evidence map](../studies/lodestone-dev-patch/derived/evidence-map.md):
  first-party announced intent. The later numbered patch pages are linked
  directly, outside the study's archived transcription coverage.
- [Table checksums](../studies/gamerescape-tables/derived/checksums.sha256)
  pin the normalized products used below. Empty cells mean unknown.

CSV locators below are physical lines including the header. All mob rows use
source key `ge-mob-pages`. The location table has no revision columns. A revision
listed here is an exact `mob_name` join to `mobs.csv`, preserving the distinction
between a location record and its joined page metadata. No spelling or similar
name substitution supplies a missing join.

## Skirmish admission and guide location

[Patch 1.23 Notes, Event, dev1455][patch-123] announced Locke's Lie and
Turtleback Island as Skirmish's two instanced isles. Only the party leader
could initiate battle. Both sites listed Disciples of War or Magic at level
45 or above, a party of 4-8, and every member fully enlisted in a Grand Company.
The listed battle limit was 30 minutes, separate from reentry waits of
15 minutes after victory and 5 minutes after defeat.

That official section placed Storm Captain Loetahlsyn at Limsa Lominsa,
Lower Decks (5,7). Independently,
[`npcs.csv`](../studies/gamerescape-tables/derived/npcs.csv) line 1102
records the same zone and location, with `map_coords` equal to `5-7`, page
`Storm Captain Loetahlsyn`, revision `31128`, timestamp
`2012-07-30T01:24:28Z`, source `ge-npc-pages`. This is a wiki location
association. Neither source joins a runtime actor, class path or zone instance
to that location. The separate client labels and admission text belong to
`xivl-client-data:docs/nmrush-skirmish-text.md`.

## Skirmish targets and spawn descriptions

Selecting `event_or_quest` containing `Skirmish` in
[`mob-locations.csv`](../studies/gamerescape-tables/derived/mob-locations.csv)
yields the 15 associations below. Each has one exact name match in
[`mobs.csv`](../studies/gamerescape-tables/derived/mobs.csv).
Every selected location row lists level `55`, behavior flag `A`, and an empty
`drops` cell. Locke's Lie coordinates are empty. Each Turtleback Island row
has `map_coords` equal to `1-1`. These are wiki fields, without independent
coordinate or encounter validation.

| Site | Mob | Location line | Mob line | Joined revision | Revision timestamp |
|---|---|---:|---:|---|---|
| Locke's Lie | Aetherbound Slave | 2 | 2 | 30728 | 2012-07-29T18:41:28Z |
| Locke's Lie | Akoman | 5 | 4 | 30023 | 2012-07-29T18:35:30Z |
| Locke's Lie | Akoman's Daewa | 6 | 5 | 30132 | 2012-07-29T18:37:28Z |
| Turtleback Island | Bixie | 140 | 91 | 28967 | 2012-07-28T21:22:47Z |
| Locke's Lie | Cactuar Jaques | 188 | 125 | 29814 | 2012-07-29T18:29:41Z |
| Locke's Lie | Elder Longhorn | 397 | 211 | 30520 | 2012-07-29T18:40:15Z |
| Locke's Lie | Eurylochus | 428 | 231 | 29881 | 2012-07-29T18:31:36Z |
| Locke's Lie | Great Elm | 594 | 301 | 30809 | 2012-07-29T18:43:17Z |
| Turtleback Island | Greater Buffalo | 596 | 303 | 28750 | 2012-07-28T21:18:49Z |
| Locke's Lie | Longhorn Billygoat | 786 | 418 | 30228 | 2012-07-29T18:38:57Z |
| Locke's Lie | Longhorn Nannygoat | 787 | 419 | 30368 | 2012-07-29T18:39:27Z |
| Locke's Lie | Princess of Pestilence | 986 | 529 | 29946 | 2012-07-29T18:33:41Z |
| Turtleback Island | Steropes | 1265 | 669 | 29044 | 2012-07-28T21:25:19Z |
| Turtleback Island | Stone Golem | 1267 | 671 | 29179 | 2012-07-28T21:28:01Z |
| Turtleback Island | Wadjet | 1394 | 758 | 28852 | 2012-07-28T21:21:06Z |

The retained [July 10 Skirmish announcement](../sources/lodestone-dev-patch/objects/pages/skirmish-2012-07-10.md),
Participation and Objectives, gave defeating all enemies within 30 minutes as
the overall objective. It did not specify a universal prerequisite for the
next opponent to appear. The Turtleback Island wiki notes below separately
describe predecessor-defeat or reported-time alternatives.

The joined `notes` cells describe the following spawn relationships at wiki
tier. They do not bind `QuestDirectorNMRush01` or `QuestDirectorNMRush02` to
either island. The minute values below are preserved as reported
thresholds. Their clock origin is not specified in these cells.

| Site | Mob notes and source locator in `mobs.csv` |
|---|---|
| Locke's Lie | Great Elm, line 301: final boss, appearing centrally after all other enemies are defeated. The note also reports frequent hate resets. |
| Locke's Lie | Akoman, line 4: appears with several Akoman's Daewas. Akoman's Daewa, line 5, reciprocally names Akoman. |
| Locke's Lie | Cactuar Jaques, line 125; Eurylochus, line 231; Princess of Pestilence, line 529: each names the other two as appearing together. |
| Locke's Lie | Elder Longhorn, line 211; Longhorn Billygoat, line 418; Longhorn Nannygoat, line 419: each names the other two kinds as appearing together. Counts are unspecified. |
| Turtleback Island | Greater Buffalo, line 303: appears first. |
| Turtleback Island | Wadjet, line 758: appears after Greater Buffalo's defeat or after 5 minutes. |
| Turtleback Island | Bixie, line 91: appears after Wadjet's defeat or after 10 minutes. |
| Turtleback Island | Steropes, line 669: appears after Bixie's defeat or after 15 minutes. |
| Turtleback Island | Stone Golem, line 671: appears after Steropes' defeat or after 20 minutes. The note also reports high resistance to Lightning damage. |

Aetherbound Slave's selected `notes` cell is empty. This inventory does not
establish a complete encounter roster, fixed wave sizes, a common timing origin,
actual transitions or reward settlement. Empty selected drop fields do not
establish an absence of rewards.

## Behest named associations

Selecting `event_or_quest` containing `Behest`, case-insensitively, in
`mob-locations.csv` yields 13 rows and 13 distinct names. All selected rows
are below, including the generic `Behest` label and labels combining another
event or quest with Behest. A combined label does not assign every level or
drop in that row exclusively to Behest.

| Full event or quest label | Mob | Zone | Map coords | Level range | Flag | Location line | Mob line / joined revision / timestamp |
|---|---|---|---|---|---|---:|---|
| Black Brush Behest | Bark Weevil | Central Thanalan | 24-26 | 13 | A | 120 | 77 / 344551 / 2012-04-30T02:42:45Z |
| Behest: Humblehearth | Darkeye Devilet | Central Shroud | - | - | A | 259 | 165 / 27635 / 2012-09-26T03:43:24Z |
| Underneath the Shell, Behest: Humblehearth | Darkwing Devilet | Central Shroud | - | 30-42 | A | 268 | 166 / 464363 / 2012-06-23T05:36:40Z |
| Behest | Drifting Mine | Eastern La Noscea | - | - | - | 374 | 200 / 333457 / 2011-09-25T01:19:58Z |
| Burning Down the Houses, Behest: Camp Skull Valley | Firestarter Imp | Western La Noscea | - | 10 - 40 | A | 495 | 255 / 497528 / 2012-05-30T01:50:26Z |
| Nine Ivies Behest | Hellsfire Hedgemole | East Shroud | - | 50 | P | 618 | 320 / 187049 / 2012-09-26T03:42:13Z |
| Treespeak Behest | Ill-tempered Pteroc | North Shroud | - | 45 | P | 649 | No exact match |
| Treespeak Behest | Lake Crab | North Shroud | - | 45 | P | 754 | 403 / 60390 / 2012-06-03T17:12:35Z |
| Treespeak Behest | Lightning Elemental | North Shroud | Treespeak | 46 | P | 775 | 411 / 281387 / 2012-06-06T19:45:25Z |
| Camp Skull Valley Behest | Ocean Roseling (Roselet) | Western La Noscea | - | - | A | 939 | No exact match |
| Black Brush Behest | Sand Yarzon | Central Thanalan | 24-26 | 13 | A | 1124 | 605 / 481530 / 2012-04-30T02:41:24Z |
| Treespeak Behest | Slithering Slug | North Shroud | - | 45 | P | 1199 | 645 / 326323 / 2012-06-03T16:55:40Z |
| Black Brush Behest | Spriggan | Central Thanalan | 24-26 | 13 | A | 1254 | 664 / 279184 / 2012-05-30T03:26:55Z |

Here `-` means an empty source cell. The literal `Treespeak` is in Lightning
Elemental's `map_coords` cell, not a recovered numeric position. Eleven names
have one exact revision match each. `Ill-tempered Pteroc` and
`Ocean Roseling (Roselet)` have none. Their location associations remain
usable at wiki tier, while their page revision joins remain unresolved.
No selected name has multiple exact matches. All eleven matched `notes`
cells are empty, so this selection supplies no explicit Behest phase order.

Four selected location rows carry drop strings:

| Mob and location line | Items named in `drops` |
|---|---|
| Darkeye Devilet, 259 | Imp Wing, Wildfowl Feather, Black Pepper, Chocobo Feather, Disabling Powder, Ahriman Wing |
| Darkwing Devilet, 268 | Imp Wing, Black Pepper, Wildfowl Feather, Chocobo Feather, Salt Leek |
| Firestarter Imp, 495 | Cinderfoot Olive, Imp Wing, Crow Feather, Bone Chip, Vitriol |
| Hellsfire Hedgemole, 618 | Mole Meat |

The other selected `drops` cells are empty. These strings describe mob drops,
without a demonstrated operation-completion grant, participant attribution,
reward probability or reward schedule. Combined event labels retain their
ambiguity. Raw drop-template operands remain in the cited CSV.

## Behest announced timing and phase evidence

[Patch 1.19 Notes, Event, dev1139][patch-119] announced signup delays for
consecutive Behests: success required waiting 2 minutes from the next
recruitment's start; failure required 1 minute from that same reference event.
These are signup delays, without a full recurrence period or battle budget.

The section also announced enemies at the suggested level, with the final
group one level higher. Higher party mean level raised enemy level. It listed
an increase of 1 for light parties, 4 for full parties, capped at 9 above the
suggested level. This is an announced final-group distinction, without named
members, counts, positions or a complete phase schedule.

[Patch 1.19 Notes, Battle, dev1026][patch-119] additionally restricted
engagement of content-specific enemies, including Behest enemies, to
participants. Its general claim/reward rules do not specify named Behest
completion payouts. No quantity or settlement claim follows from these notes
or the selected drop strings.

## Remaining evidence boundary

The named associations and spawn descriptions above preserve historical
content evidence without establishing runtime enforcement. They leave
per-Behest `requestId`, Director identity, complete phase rosters and counts,
spawn positions, battle timing, participant outcomes and reward amounts
unresolved. The Skirmish notes likewise leave Director/site assignment,
observed admission and timer/state publications, terminal outcomes and reward
transactions unresolved. Resolving those edges needs attributable retail
packet or video evidence for the same encounter and participant.

[patch-123]: https://forum.square-enix.com/ffxiv/threads/50278-patch1.23-Patch-1.23-Notes
[patch-119]: https://forum.square-enix.com/ffxiv/threads/24910-patch1.19-Patch-1.19-Notes
