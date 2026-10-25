# United We Stand encounter accounts

The retained Gamer Escape walkthroughs describe a transmitter objective protected
by three generators, recurring Legionary reinforcements and a Magitek Vanguard
F-1. These are contemporaneous 2012 wiki claims, not observed packet events or
recovered server code. They add combat details absent from the shared Gcl106
client contract. Their generator-related enmity accounts differ in specificity.

## Source and revision boundary

Evidence class: `web-tables`, secondary research tier. Source bundle:
`sources/gamerescape-tables/manifest.yaml`. The three quest pages were edited
before ARR; the revision timestamps date edits, not the reported fights.
Their substantially shared wording is not three independent observations.
No gameplay video was inspected. The plot page is a dialogue transcription,
not a detailed fight log. The Ceruleum Generator page supplies a sighting and
level field, not a spawn script. The pruned page is only a disambiguation list.

| Retained member | Revision | Edit timestamp | Bytes | SHA-256 |
| --- | ---: | --- | ---: | --- |
| `pages/Ceruleum_Generator.wiki` | [355534](https://ffxiv.gamerescape.com/w/index.php?oldid=355534) | 2012-08-08T19:53:05Z | 1081 | `4077f5d6743f796c258aca02c206f97a828e29fa5a9e527bf193c277d77c927a` |
| `pages/United_We_Stand_Gridania.wiki` | [333001](https://ffxiv.gamerescape.com/w/index.php?oldid=333001) | 2012-07-30T15:13:58Z | 5218 | `552631caa9fdc4a66afbe4ce7c34c4376ac1c96c62f21dc2a1937f7b1f5145a2` |
| `pages/United_We_Stand_Gridania_Plot_Details.wiki` | [26466](https://ffxiv.gamerescape.com/w/index.php?oldid=26466) | 2012-07-28T00:01:20Z | 13326 | `16e550f3882205864c5ec129e39e58e927f7d645fd87e70ccb99ce525cd50452` |
| `pages/United_We_Stand_Limsa_Lominsa.wiki` | [333134](https://ffxiv.gamerescape.com/w/index.php?oldid=333134) | 2012-09-19T21:58:00Z | 4271 | `3926596ff0c8c9671e91b60ea857de7de19c5e36a6850292b3bab024c69f2d6a` |
| `pages/United_We_Stand_Ul_dah.wiki` | [332883](https://ffxiv.gamerescape.com/w/index.php?oldid=332883) | 2012-09-09T06:11:47Z | 4074 | `09384944ecf9bd897a121587046570b269ccd7311f299fb40ac4c3cc39a2c2b1` |
| `pruned/United_We_Stand.wiki` | [332761](https://ffxiv.gamerescape.com/w/index.php?oldid=332761) | 2012-06-06T21:39:44Z | 252 | `a80b4ce061fb1fb2ce6fac8dd774880562a4b20be0841f5bcdf1cf07e9540c70` |

The source manifest pins archive SHA-256
`5591a0544c57475b461ca25ae164e9f6c94b9d7d2c993703274f5c6bf5d28a8b`
and member-manifest SHA-256
`cb75c4b5ca08be0075eafbc1e35bdc5280a9763aee877048231e93a369dff982`.
Both hashes and all six member hashes were verified before interpretation.

## Encounter observations and limits

| Step or subject | Retained claim | Locator and limit |
| --- | --- | --- |
| Briefing and approach | Ryder in Jagged Crest Cave, then Yarborough, then Castrum Novum; bypass the level-63 Magitek Vanguard H-1 on the approach. | Gridania lines 35-39; Limsa 35-40; Ul'dah 35-39. H-1 is distinguished from the battlefield F-1. The displayed map coordinate is not a client position or spawn location. |
| Battlefield roster | Magitek Vanguard F-1, Magitek Transmitter and three Ceruleum Generators. | Gridania line 40; Limsa 41; Ul'dah 40. No actor IDs, placement, HP or F-1 attack sequence is given. |
| Reinforcements | Several level-55 VIIth Legionaries appear during the fight and accumulate if not killed. | Gridania lines 41,46; Limsa 42,47; Ul'dah 41,46. No exact count, composition, wave schedule or trigger is stated. The HP comparison is qualitative. |
| Vulnerability | Destroying one generator permits transmitter damage; the generator later reactivates and must be destroyed again. | Gridania line 44; Limsa 45; Ul'dah 44. No reactivation interval, HP threshold or all-generators bonus is specified. |
| Clear objective | Destroying the transmitter alone wins and starts a cutscene. | Gridania lines 43,47; Limsa 44,48; Ul'dah 43,47. The pages do not require defeating F-1 or all generators. No native clear flag or reward transaction is supplied. |
| Entry and duration | Four to eight Disciples of War or Magic, level 45 or above; each member meets a United We Stand variant's entry requirements; 30-minute allowance. | Each page's Journal Entries section. These are displayed rules transcribed by a wiki, not a recovered server predicate or the Gcl106 caller payload. |
| Reward | Infoboxes list 5000 seals and EXP 6231; Notes adds 1000 seals for a party representing all three companies. | Gridania lines 31-32,72; Limsa 31-32,67; Ul'dah 31-32,65. Treat as calibration; EXP is not independently established as a fixed award. |
| Post-fight completion | Gridania directs the player to Kinnison, Cid and Kan-E-Senna, then Brookstone for quest completion and rewards. | Gridania lines 48-50. Battlefield victory and later quest completion are distinct steps in this account. |
| Generator page | Level field 50; Castrum Novum sighting associated with United We Stand, behavior code P. | Ceruleum Generator Low Level and Mob Row fields. HP, coordinates and drops are empty. The behavior code is preserved without expanding its meaning from later-era terminology. |

Gridania line 45 and Limsa line 46 describe an
occasional severe enmity effect when a generator dies and recommend that the
F-1 kiter land the finishing blow. This recommendation does not establish
last-hit target selection. Ul'dah line 45 explicitly says the effect depends
on which player dealt the most generator damage. The shared observation is a
generator-destruction-related enmity effect on F-1. Neither a last-hit rule nor a
highest-damage rule is established across these revisions, and no magnitude or
reset behavior is recorded.

## Comparison with the client contract

`xivl-client-scripts:docs/united-we-stand-client-contract.md` owns the shared
Gcl106 contract. Its briefing and map messages support the transmitter objective,
sector gates, patrol-related gate narrative and all-company reward bonus. The
wiki adds three generators, the one-generator vulnerability condition,
reactivation, F-1 and Legionary reinforcement claims. Those additions remain
wiki evidence; agreement on the objective does not authenticate every combat
claim or bind any named monster to a particular actor ID.

The Gridania Plot Details Parts 1-2 repeat briefing dialogue, including the
sentry-patrol gate statement at line 30. They do not describe timed gate
observations. Part 3 narrates transmitter destruction and Nael's departure;
Part 4 narrates the later report and reward. The transcription omits the
system-style numerical briefing lines, so it cannot recover the actual A4
argument passed to Gcl106's briefing method.

The independently preserved eLeMeN Grand Company index lists the same three
quests with level 45, 5000 company seals and EXP **up to 6231**. That qualification
prevents treating the GE infobox EXP as an invariant payout. The canonical
numeric product remains
`studies/elemen-quest-rewards-walkthroughs/derived/quest-exp-rewards.csv`,
rows for quest IDs 111432, 111632 and 111832. The inspected HTML is an archived
site page without a per-page revision timestamp; it is not a contemporaneously
dated observation merely because its URL contains `ff14_dated_archives`.

| Additional retained HTML | Bytes | SHA-256 | Supported scope |
| --- | ---: | --- | --- |
| `ff14_dated_archives/quest/TheGrandCompanies/index.html` | 43370 | `c9a3b2168c4adc579dc12e0d929a67ed879c32c60f9e951c4cc5407a22663091` | Three reward/prerequisite index rows; links onward to company pages, not an inspected detailed GC walkthrough |
| `ff14_dated_archives/etc/area/MorDhona.html` | 20859 | `4a22503778e848f9a274c9901bcc533c2b4fe8b00148f58a1fd28edb47810106` | Castrum/tower area labels and a 2012-06-07 patch 1.22b introduction statement; no recovered fight AI |

Both HTML members were verified against
`sources/elemen-site-archive/manifest.yaml`. Its `archive` evidence class denotes
preservation; the reward interpretation belongs to the cited web-table study.

## Remaining evidence

No inspected source establishes enemy coordinates, wave timing, generator
reactivation delay, transmitter HP, exact enmity targeting, gate timing,
weather selection, instance director identity or historical A4 invocation.
The 2026 Navmut population records lack video URL, title, time range and source
patch provenance. Their coordinates are not retail spawn evidence and were not
used to infer any position here.

The retained Limsa page links a separate Guide:United We Stand and embeds video
ID `qDdvF9wpCBs`. Neither linked artifact was inspected in this study. They are
specific next evidence candidates for enmity targeting and reinforcement
timing, not verification of the present account.
