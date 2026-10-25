# Rivenroad historical mode and phase descriptions

Preserved Gamer Escape walkthroughs distinguish the To Kill a Raven quest
battle from The Raven, Nevermore. The official Patch 1.23a announcement
identifies the latter with Rivenroad (Hard). These sources add historical
descriptions to the client contract; they are not packet/video observations
or recovered server logic.

## Mode attribution

| Mode or context | Supported historical evidence | Boundary |
| --- | --- | --- |
| Original To Kill a Raven quest battle | Gamer Escape's Gridania revision 14459, Limsa Lominsa 13887 and Ul'dah 13596 identify patch 1.23 and describe the quest route into the battle | Their August 13, 2012 revisions postdate the initial release; the described battle is in quest context, not explicitly the later repeatable normal mode |
| Repeatable Rivenroad | Patch 1.23a announces availability after Living on a Prayer, without additional rewards | No separately attributed repeatable-normal walkthrough was recovered in the inspected members |
| Rivenroad (Hard) | Patch 1.23a explicitly names The Raven, Nevermore, eight level-45-or-higher combat-class players, a 30-minute limit and 15/5-minute victory/defeat waits; the quest reward is first-clear only | Announcement of intended rules, not observed enforcement |

The official source is [Patch 1.23a Notes](https://forum.square-enix.com/ffxiv/threads/51545),
post 1, dated August 13, 2012, Event dev1484 and its Rivenroad (Hard) table.
The page was inspected directly; it is not a locally archived Lodestone
transcription. The retained [timer-announcement finding](../../lodestone-dev-patch/derived/timer-announcements.md)
owns the existing unlock/wait summary.

## Quest-context combat description

The following are paraphrased wiki assertions from
[To Kill a Raven (Gridania), revision 14459](https://ffxiv.gamerescape.com/w/index.php?oldid=14459),
Walkthrough, preserved member lines 48-64. The combat block is byte-identical
in the three August company pages and the October 14 Ul'dah revision 13616.
Those copies do not provide independent corroboration or demonstrate unchanged
server behavior across the interval.

| Subject | Explicit wiki description | Qualification |
| --- | --- | --- |
| Initial attacks | Chaos Thrust, Thermonic Beam, Ravensbeak, Iron Chariot, Twisting Vice and Fierce Ravensbeak are named | The source spells Thermonic this way; names do not join numeric commands or animation banks |
| First-phase fragments | Below 50% HP, Lunar Fragments appear and must be destroyed before landing; the walkthrough recommends ranged attacks from stairs | Threshold and strategy are wiki claims; no measured timing or spawn count |
| Transition | Reducing the first enemy to zero HP leads to a second phase named Nael deus Darnus | No reset amount or native actor replacement demonstrated |
| Second-phase attacks | Prior attacks except Chaos Thrust, with Lunar Dynamo added | No complete scheduler or exact sequence |
| Late sequence | At approximately 10% HP, the boss moves to the highest platform, summons meteors and two Lunar Golems, then returns for Megaflare | Preserve approximate threshold; no meteor count or spawn coordinates |
| Mitigation outcome | Destroying every meteor is said to leave Megaflare dealing approximately 2,000 damage | No equipment, target count, variance or measurement sample supplied |

The same walkthrough associates Fierce Ravensbeak with an enmity target at
another elevation and describes a meteor substitute after meteor summoning
begins. Patch 1.23a's Fixed Bugs section separately announces a correction to
Fierce Ravensbeak occurring outside intended conditions. It does not define
those conditions. The wiki cannot establish a stable anti-kiting rule for every
retail patch or identify which reported event preceded that correction.

## Hard-associated description

[The Raven, Nevermore, revision 49456](https://ffxiv.gamerescape.com/w/index.php?oldid=49456),
dated August 14, 2012, Walkthrough, preserved member lines 36-46, describes
Nael deus Darnus starting a Megaflare phase immediately on engagement.
It reports immunity to magical damage during the charge. It separately says
that fragments outside a Megaflare phase drop Deaspected Clusters, and that
such a fragment reaching the ground creates a Lunar Golem in addition to
dealing damage. The official quest-to-Hard association above supplies the
mode attribution; the wiki filename alone does not.

The page estimates unprotected Megaflare above 6,000 damage, approximately
1,000 with its listed combination of Lunar Curtain, Stoneskin, Sentinel and
Sanguine Rite, and roughly 50% reduction from Lunar Curtain. These are
uncontrolled wiki estimates, not independently measured formulas. The page
does not provide a complete Hard phase schedule, golem count, meteor cadence,
or numeric command/animation mapping.

## Corroboration and limits

The preserved Nael van Darnus (Monster) revision 26370, August 6, 2012, Notes,
explicitly assigns that name to the first To Kill a Raven phase. Its listed
map location is not a server-world spawn coordinate. The Rivenroad revision
38946 is an unfilled zone infobox. The inspected Living on a Prayer revisions
49260 and 49280 describe pilgrimage progression rather than a detailed
Rivenroad encounter. Their linked The Raven, Nevermore page supplied the
targeted additional mode evidence.

The authenticated eLeMeN Rivenroad HTML links the three company quests and
contains weather15/weather16 icon filenames (lines 179-185). These are site
tokens, not native weather IDs or proof of an encounter's weather assignment.
The archive describes a final-1.x site edition, but this individual page has
no retained revision ID or publication timestamp. Its hash proves bytes,
not a contemporaneous editing date.

No retail video or packet capture was inspected for this study. Original
quest observations are not copied into repeatable-normal or Hard behavior by
assumption. No source here binds Lesser/Normal director names to content modes,
or commands 23614/23615 to m917 WSS18/19. Wiki statements remain secondary
research at the source's web-tables tier; preservation does not raise that tier.

## Source integrity

The Gamer Escape source manifest pins archive SHA-256
`5591a0544c57475b461ca25ae164e9f6c94b9d7d2c993703274f5c6bf5d28a8b`
and embedded member-manifest SHA-256
`cb75c4b5ca08be0075eafbc1e35bdc5280a9763aee877048231e93a369dff982`.
The archive, embedded inventory and thirteen selected page members matched
their byte sizes and hashes. Page headers retain the revision timestamps;
all selected Gamer Escape revisions precede the 2012 shutdown. The selected
eLeMeN original matched its source-manifest pin. Exact page identities and
member hashes are retained in the [source identity table](rivenroad-source-identities.md).
