# Combat sight detection evidence

No inspected 1.x-authenticated evidence establishes that monster sight aggro
requires an unobstructed line of sight. The retained packets show combat
state and presentation, but supply no controlled wall/rock obstruction test.
The selected contemporary sources describe unprovoked attacks, approach and
level dependence without defining an occlusion rule. This does not establish
that retail ignored obstructions, or that range, facing and level alone were
its complete detection algorithm.

The [Gamer Escape behavior-code qualification](../studies/gamerescape-tables/derived/mob-client-crosscheck-notes.md#the-behavior-codes-are-a-six-code-vocabulary-not-a-one-letter-flag)
remains applicable. Its defining revisions are from 2017-2022. Their
line-of-sight wording, level threshold and later abilities cannot establish
1.23b detection mechanics. A 1.x mob page carrying `S` or `H` does not date
every later definition of those letters to 1.x.

## Retained packet search

Source id `pcap-1.23b`, evidence class `packet-capture`, is owner-attested
retail 1.23b. The complete 54-member source set and its member SHA-256 values
are in the [source manifest](../sources/pcap-1.23b/manifest.yaml).
The original archive matched `config/retail_inputs.json`: 2622720 bytes,
SHA-256 `20a78b9f40ff2393037c9a160c957783cf590b4f01797493d22fcd2039e9cbff`.
Every original member and local cache copy matched the manifest.

The producing tools were Python `zipfile`/`hashlib`,
[`validate_framing.py`](../tools/validate_framing.py), and
[`extract_group_combat_contracts.py`](../tools/extractors/extract_group_combat_contracts.py)
`events`, using `reconstruct_lanes`, `parse_outer_frames` and `maybe_inflate`
from [`extract_streams.py`](../tools/extractors/extract_streams.py).
Framing checks preceded decoding and reported zero compression-flag
mismatches in all members. The event walker checked complete admitted frame
and subevent extents. Clear port-54992 connections remained distinct.
TLS/lobby traffic and incomplete stream tails were outside this search.

The finite census selected s2c `0x0195`, `0x0187`, `0x000C`, `0x00D3`,
and c2s `0x00CC`/`0x00CD` from every admitted connection. These numeric
records were selected as possible enmity, occupancy, music and targeting
witnesses, not as authenticated causes of spontaneous aggro. Counts were
149, 44, 26, 167, 66 and 118 respectively. Adopted packet names are indexed
by [`opcode_names.json`](../derived/opcode_names.json); their names alone
do not identify a detection test.

All retained s2c `0x0195` records occurred in these four members. Locators
below refer to connection 0, main s2c. Frame and subevent ordinals are
zero-based; capture-packet ordinals are one-based.

| Member / SHA-256 | Indicator count | First `0x0195`: frame / subevent / completing capture packet |
| --- | ---: | --- |
| `combat_autoattack.pcapng` / `2f677ab61047b25c4168a3dd9496f372d48de3bba018d582dd5a968b9272f7b2` | 4 | 26 / 0 / 70 |
| `combat_skills.pcapng` / `7fe66d92f6f62584e57562e51355d310546935690e0b96c2c689b83bbe8a07a7` | 4 | 32 / 0 / 88 |
| `party_battle_leve.pcapng` / `6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f` | 114 | 383 / 15 / 580 |
| `war_quest_update2.pcapng` / `bf43b5ee32c58e5dc6f8149b071bd9c5cd5cc0aaa55ea3528872308fd7be2429` | 27 | 97 / 1 / 183 |

The [occupancy and enmity study](../studies/group-combat-wire-contracts/README.md)
owns the layouts and exact state sequences. The eight-byte `0x0195`
application carries a target actor, indicator value and two-byte tail.
It does not carry an identified acquisition cause or obstruction result.
The initial indicator need not be the first hostile action, and occupancy
does not by itself distinguish detection from a player action, link or
scripted encounter.

The [music study](../studies/music-000c-wire/derived/evidence-map.md#captured-layout-and-locators)
binds the two combat members' song/mode `13/1` requests at s2c frame 18 and
frame 25, followed later by `57/4`. It explicitly leaves aggro-only versus
drawn-weapon eligibility unresolved. Its
[map-context check](../studies/music-000c-wire/derived/map-context.md)
finds no SetMap/ZoneMaster witness in either combat member and does not
carry map identity across the retained TCP gaps. Neither music onset nor
matching endpoints authenticates a location or a wall between two actors.

Target lock is also not an aggro-specific witness: c2s `0x00CC` occurs in
the retained vendor, quest and NPC-talk members as well as combat members.
For example, `small_talk_louisoix.pcapng` contains two such records and no
`0x0195`. No selected targeting record identifies a monster sight test.

Positions and rotation can support a range/facing reconstruction only after
actor identity, map state and time are joined. The
[position-report study](../studies/c2s-00ca-position-report/README.md)
binds player position/heading data and explicitly lacks collision/terrain
data. A coordinate pair alone does not classify the connecting segment as
clear or obstructed. No retained obstruction observation or authenticated
geometry join was identified for the four indicator members. The packet
search therefore cannot compare otherwise eligible players on opposite
sides of an obstruction, or establish a sight-aggro onset behind it.

## Contemporary sources

### Preserved 2012 wiki revisions

Earlier members of the same preserved Gamer Escape archive do independently
corroborate sight/hearing terminology. The source is
[`gamerescape-tables`](../sources/gamerescape-tables/manifest.yaml),
evidence class `web-tables`. Python `zipfile`, `json` and `hashlib` inspection
authenticated the archive SHA-256
`5591a0544c57475b461ca25ae164e9f6c94b9d7d2c993703274f5c6bf5d28a8b`,
its `corpus-manifest.json` SHA-256
`cb75c4b5ca08be0075eafbc1e35bdc5280a9763aee877048231e93a369dff982`,
and these exact member bytes. Member frontmatter preserves original revision
URLs and timestamps. Paths below are archive members, not public files.

| Original member / line | Revision / timestamp | SHA-256 and observation |
| --- | --- | --- |
| `pages/Category_Aggressive.wiki:10` | 40311 / `2012-08-07T19:18:22Z` | `804ffe883b5783218e97fdab9066161b58ae33a6966930c52e3cd1c863fa6785`. Describes unprovoked attack subject to a broad level-difference condition, and links sight and sound detection. |
| `pages/Category_Detects_by_Sound.wiki:10` | 40003 / `2012-08-08T19:09:06Z` | `dfc6a673e26fabe3fd01f9a7b0eee9137ef1c144a048e5740fc47b86997ebcf3`. Describes nearby non-walking movement, with a broad level-difference condition. |
| `pruned/Template_Mob_Notes-S.wiki:8` | 283275 / `2012-08-08T19:07:01Z` | `fdb04f30d106193db866261d62d3d613aa88cbc465f1273faa301a7d379d3d55`. Supplies the sight-detection gloss and category link. |
| `pruned/Template_Mob_Notes-H.wiki:8` | 6802 / `2012-08-08T19:02:40Z` | `deea0d97749c1deb8f1f78c98aa7d13b99b0e05815872fa1facb0c56b830c541`. Supplies the hearing-detection gloss and category link. |

These are dated contemporary wiki claims, not a recorded retail detection
test. None defines obstruction, a sight radius, a facing cone or an exact
level threshold. The linked sight-category article is not present under a
`Detects_by_Sight` or `Detects by Sight` member path in this archive. The
2012 members do not authenticate the later rows' additional mechanics or
the unobstructed-line-of-sight claim.

### Patch, help and observation contexts

The source manifests preserve member identities and dates. The producing
method for the following retained originals was HTML-to-Markdown
transcription; the manifests do not identify the executable that performed
it. Current inspection used `rg` with surrounding-context reads and Python
`hashlib`, comparing member hashes to the manifests. First-party help and
patch text describe documented or announced behavior, rather than an
observed 1.23b server decision. Community reports retain their narrower
observation and era limits.

| Original locator / SHA-256 | Observation and limit |
| --- | --- |
| `sources/lodestone-beginners/objects/pages/beginners-2010-11-15.md:70-72` / `30426adf98ddb70cf318437ba7da0a051cec36a319fad5f16bf631811fd719b3` | The 2010-11-15 answer describes aggressive enemies attacking nearby players without provocation. It supplies no facing, hearing, wall or occlusion condition. |
| `sources/lodestone-manual/objects/pages/the-game-screen.md:25-55` / `dcd2256d07d93d3732e28553295f80006a77396903f9c8c03637e399384f3be4` | The retained manual distinguishes hostile/claimed display state, enmity indicators and active/passive enemies. Active enemies attack approaching players, with suppression when player level is considerably higher. No numeric threshold or clear-sight requirement is given. Source snapshot: 2015-01-08, preserved 1.0 manual. |
| `sources/lodestone-dev-patch/objects/pages/producer-letter-3-2011-02-17.md:74-83` / `65a2b58e6b2512a50b299e84a3a41ea6a5a486221b846070c8abe63ed6200717` | Planned enemy positioning, ranged attacks, claiming and environment-collision work are listed separately. Movement-response collision work does not specify visibility-based aggro. |
| `sources/lodestone-dev-patch/objects/pages/version-update-details-2010-11-25.md:153-165` / `78d19b91f5fb03d7d789d814aa0d5039f63f1d5b64aae93a2b114d89a8705e5c` | Territory and return behavior are described. Neither establishes how an idle monster detects a player. |
| `sources/kanican-tables/objects/five-months-in.md:218-226` / `c97839cdb3e0755e21f19877825b238b5cdc5fc12a4f0d893afdc7f18528a925` | The 2011-02-02 report calls Onrush a line-of-sight AoE, avoided by moving out of the NM's front. This concerns an engaged attack's geometry, not wall obstruction or acquisition of aggro. |
| `sources/elemen-bestiary/objects/pages/NM_LaNoscea.md:197-215` / `3d7982181114adc062fd3fe76b79a52613505a248714d7c6f30cb9c0975f957d` | The Chaotic Eye move has a front/visual-area description in its attack-scope cell. The table does not describe idle detection. The source manifest provides no retrieval date; implementation dates in the page do not date every table assertion. |

The two promoted quest-video observation records also leave acquisition
unresolved. `sources/main-scenario-lord-errant-video-breakdown/objects/lord_errant_video_breakdown.md:17`
(SHA-256 `5f28e75ff95a8b829766b37c458824a08ffb971071f805a9ed6b48a95276db69`)
and `sources/main-scenario-toll-warden-video-breakdown/objects/toll_of_the_warden_video_breakdown.md:17`
(SHA-256 `6c2f1d48b4dce63ec75a77626789fe65a7591d5a476094a9a5ff01c8341d1a44`)
explicitly establish no aggro transition. These manually authored sampled
frame records contain no controlled obstruction comparison. Their exact
patches are unknown, and the latter is 2010 footage. They are
`notes-and-transcripts` evidence, not synchronized video of the packet
windows above.

In addition to the four wiki members above, the detailed context search
covered these 29 originals, each matched to its
source-manifest member hash. Paths in this table start under
`sources/<source-id>/objects/`:

| Source id | Selected originals |
| --- | --- |
| `lodestone-dev-patch` | `pages/balancing-2010-11-19.md`, `pages/more-on-monsters-2010-12-13.md`, `pages/notorious-monsters-2011-04-13.md`, `pages/producer-letter-3-2011-02-17.md`, `pages/version-update-details-2010-11-25.md`, `pages/chocobos-airships-2011-09-22.md`, `pages/all-new-gear-2012-04-23.md` |
| `lodestone-manual` | `pages/configuration.md`, `pages/the-game-screen.md`, `pages/classes-and-jobs.md`, `pages/immortal-flames.md`, `pages/order-of-the-twin-adder.md` |
| `lodestone-beginners` | `pages/beginners-2010-11-15.md` |
| `bluegartr-stat-tests` | `pages/bg-107403-stats-and-how-they-work.md` |
| `kanican-tables` | `five-months-in.md`, `combat-sp-part-1.md` |
| `elemen-bestiary` | `pages/NM_LaNoscea.md` |
| `se-forum-monster-spawn-rate-35341` | `35341.html` |
| `mooglebox-regional-mob-maps` | `blackshroud.html`, `coerthas.html`, `la-noscea.html`, `thanalan.html` |
| `elemen-quest-rewards-walkthroughs` | `pages/walkthroughs-job.md` |
| `lodestone-lore` | `pages/firefall-2011-08-08.md`, `pages/hunters-moon-2011-09-02.md`, `pages/last-word-2011-06-17.md` |
| `monster-population-reported-observations` | `NM guessed HP per level.md` |
| The two video source ids above | Their named observation records |

The candidate search used sight, vision, detection, aggro/aggressive,
enmity/claim/engagement, obstruction, wall, hearing/sound, stealth and
front/back terms, with Japanese equivalents for vision, sensing, sound,
obstruction and facing. The additional promoted-source query used
`aggro|line.of.sight|unobstruct|sight aggr|detect.{0,25}(player|sight|sound)|hearing|behind.{0,25}(wall|rock)`.
Context reads distinguished attack geometry, map aggression markers, spawn
reports, quest titles and lore from sensing. The population compilation
lacks source dates and its underlying reported videos, so it cannot
authenticate contemporary detection. No selected original supplies a
wall-suppression rule. This is a bounded source search, not an assertion
that every historical document is silent.

## Client-consumed data

Original client scripts establish a presentation field, not a sight sensor.
Decoded paths below are relative to `lua/scripts/` in `xivl-client-scripts`.
Original LPBs, decoded chunks and reproduced sources matched that repository's
`manifests/retail_lua_coverage.json` and `manifests/scripts.json`, extraction
`2012.09.19.0001`. The producing tools were `tools/retail_script.py`, pinned
`unluac_2025_12_23.jar` (SHA-256
`98be0fa84ac73ca66dce2842a2e4512226f4c611b6500dc96415571fc5538fcc`),
and a Python Lua 5.1 operand parser. PCs and decoded-chunk offsets are
zero-based.

| Original script / LPB path relative to `client/script/` | LPB SHA-256 / decoded chunk SHA-256 |
| --- | --- |
| `chara/npc/npcbaseclass_battle.lua` / `729s9/wu7/wu789r57y9rr_89qqy5.le.lpb` | `feea4b9c4d4e2336dc3f4b4d6d1128212d78628df20249d7157a401693d57dc5` / `2f80ba2e710c6a4a762f280c778cd96db31a8996c9b4369a0399e96bbc8aa965` |
| `chara/npc/monster/monsterbaseclass.lua` / `729s9/wu7/xvwrq5s/xvwrq5s89r57y9rr.le.lpb` | `cba83c5cc287d48b83a950a7a9375e8543f7dbdae14b6ff58c992392297c92b9` / `c195bdd1abdde12a9917b16a710142463ae61a9d727e242ca31a6b2cd392b95e` |
| `chara/npc/monster/monsterdefault.lua` / `729s9/wu7/xvwrq5s/xvwrq5s6549pyq.le.lpb` | `d19625c82522aa713cdee127480c15537fd643aa7c79ce81a4795c062be10953` / `92bcb2dce0ca6efb5988f4d97b6e93572996046b970e13cd771c0eaca2404327` |
| `chara/npc/npcbaseclass_battletest.lua` / `729s9/wu7/wu789r57y9rr_89qqy5q5rq.le.lpb` | `2bf679aca47aab7736c53bee1e7fa830be02653f57b469ce92751b621f1fac3b` / `7402c8224b5579477d61f9160c326c9fce72bce179bc62645d5851983555beb0` |
| `judge/depictionjudge.lua` / `0p635/65u17q1vw0p635.le.lpb` | `9eb9b7054434cd5281cb52c89a2d5b43a40913dc47ab4d11cc18fdda4ade6e76` / `756fa626bf9703afb5f97a36eb5bc3643eaf216cc602137dde5f034f678b9f19` |

`NpcBaseClass.initForBattleCommon` declares
`npcWork.battleCommon.aggro` as `integer8` and assigns the first variadic
value (`npcbaseclass_battle.lua:13-68`, `root/proto1`, PCs 14-25,
chunk `0x192..0x1BE`). `getAggro` returns it unchanged
(`:96-104`, `root/proto4`, PCs 0-3, `0x3CC..0x3D8`). The same work
declaration contains `partsName` and eight `partsExists` booleans, without
a sight distance, cone, level threshold or occlusion field.

`DepictionJudge.judgeNameplate` reads `getAggro` in the eligible non-player
branch and selects icon 517 when the value is positive, otherwise 518
(`depictionjudge.lua:154-182`, `root/proto0`, PCs 128-142,
chunk `0x2DE..0x316`). The preceding checks are `isRetailDealer`,
`isPlayer`, property 3 and battalion not equal to 1. This is display
selection after the value is supplied. It does not compute detection
range, compare player/monster facing, raycast or acquire enmity.

`MonsterBaseClass` and `MonsterDefault` are only inheritance declarations
in their complete eight-line chunks. The required battle-test chunk contains
only a local declaration. None supplies an AI sensor implementation.
A finite query over all 2671 authenticated canonical source members found
`getAggro` only at its definition and the depiction consumer. Searches for
sight/detection-range and view/sight-angle names identified no such field
in that source corpus. Names and selected work declarations cannot prove
the absence of a native implementation, computed/numerically keyed data,
other actor work or server policy. No client-consumed monster perception
range, facing threshold or obstruction test is authenticated by this check.

## Remaining discriminator

The needed evidence is an already retained 1.x observation with the same
identified monster and player, known levels and idle state, synchronized
geometry and positions/headings, and a verified wall or rock intersecting
the relevant sight segment. It must show that the player is otherwise
eligible for detection: a clear-path control at comparable range and facing
acquires aggro, while the obstructed case does not, followed by acquisition
when the obstruction is cleared. Repeated controls must separate detection
delay, monster turning, height, disengagement, linking and scripted triggers.
No player attack, spell or party action may substitute for spontaneous
acquisition. An identified enmity/target transition or contemporaneous visible
reaction should accompany the geometry evidence; battle music alone is
insufficient. Conversely, acquisition through a verified obstruction under
those controls would refute a universal unobstructed-sight requirement for
that tested case. The missing evidence is a preservation discriminator, not
a request to collect new retail wire captures.
