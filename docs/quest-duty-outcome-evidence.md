# Quest-duty outcome evidence

Historical walkthroughs reported several phase limits and terminal triggers.
They did not establish a common terminal policy or complete settlement for
all participants. The eLeMeN and Gamer Escape material below is `web-tables`
evidence at wiki tier. Reported behavior remains distinct from client text
and packet-observed transactions.

| Question | Observation | Evidence locator | Confidence | Unknowns |
| --- | --- | --- | --- | --- |
| Their Finest Hour participant settlement | The client has a generic item-use objective template. A retained Gamer Escape row attributes clay golems to this quest. Neither establishes successful settlement for each participant. | [Success evidence](#their-finest-hour-success), worldMaster 51075/51003 and attribution CSV line 18. | Confirmed static template and retained wiki attribution; participant policy unresolved. | Admitted roster, each participant's quest credit, Earthbreaker removal and return; all-participant versus starter-only policy. |
| Futures Perfect withdrawal attackers | eLeMeN reported an initial Centurion/Hoplomachus/Sagittarius group, carried enemy damage into combat, and Centurion flight after the other two enemies were defeated. The Secutor and Signifer names have multiple candidate client IDs. | [Withdrawal evidence](#futures-perfect-withdrawal), common11.html lines 173/175/181 and crosscheck CSV lines 342/343. | Historical report and candidate-name mapping only. | Selecting condition, creation and lifetime of Secutor 2280001 and Signifer 2280007, and their actual combat participation. |
| Named-duty terminal behavior | eLeMeN reported phase-specific limits, first-bout expiry/PC HP zero leading to battle end and an event, and separate distance/NPC-health forced ends. | [Phase reports](#reported-phases) and [terminal fields](#terminal-fields), exact HTML members and CSV lines below. | Historical source reports only; no reproduced named-duty server deadline or complete terminal transaction. | Per-trigger grace, failure classification, retry, landing, HP poststate and participant scope except the narrow reported consequences below. |

## Their Finest Hour success

The static objective boundary is canonical in
`xivl-client-scripts:docs/quest-text-and-menu-operands.md#earthbreaker-objective-and-disposal`
and `xivl-client-data:docs/message-operand-rows.md`, worldMaster 51075,
English field 1. The template takes item, display-name and group/singular
arguments in positions 1, 2 and 3. Row 51003 has no item dependency.
The actual duty emitter, Earthbreaker tuple and disposal message are
unresolved. A generic template does not prove inventory removal or credit.

The retained
[Gamer Escape attribution table](../studies/gamerescape-tables/derived/mob-quest-attribution.csv),
physical line 18, attributes clay golems to Their Finest Hour, revision
92627, `2012-07-30T21:51:43Z`
([source revision](https://ffxiv.gamerescape.com/wiki/Their_Finest_Hour?oldid=92627)).
This is quest attribution, without a participant settlement transaction.
The [eLeMeN quest study](../studies/elemen-quest-rewards-walkthroughs/README.md#evidence-gaps)
has rewards but no Grand Company walkthroughs.

Success needs an admitted roster and stable participant identities followed
through quest credit, Earthbreaker inventory removal and return destination
for each participant. Neither all-participant nor starter-only policy is
established. Success is separate from each failure trigger in the terminal
matrix below.

## Futures Perfect withdrawal

The [eLeMeN walkthrough product](../studies/elemen-quest-rewards-walkthroughs/derived/quest-walkthroughs.csv),
physical line 15, binds client quest 110019 to Futures Perfect.
The retained source is [common11.html](http://elemen.sakura.ne.jp/ff14_dated_archives/quest/MainQuest/common11.html),
identified in the source table below. Its battle inset reported one Imperial
Centurion, one Imperial Hoplomachus and one Imperial Sagittarius at line 173.
Line 175 reported that enemy HP reduced during movement carried into combat.
Line 181 reported that defeating the Hoplomachus and Sagittarius made the
Centurion flee. These statements concern this pursuit/combat sequence and
do not identify extra withdrawal attackers or their selecting condition.

The retained
[client crosscheck](../studies/gamerescape-tables/derived/mob-client-crosscheck.csv),
physical lines 342/343, places 2280001 and 2280007 among multiple IDs matching
Imperial Secutor and Imperial Signifer respectively. A display-name group
neither selects one unique ID nor proves creation in this duty.
The [quest attribution table](../studies/gamerescape-tables/derived/mob-quest-attribution.csv),
line 40, associates Imperial Centurion with Futures Perfect, revision
176321, `2012-07-28T00:41:55Z`
([source revision](https://ffxiv.gamerescape.com/wiki/Futures_Perfect?oldid=176321)).
It supplies no Secutor/Signifer lifetime or conditional spawn observation.

The missing join is a same-duty withdrawal state tied to created actor/class
identities, spawn time and position, lifetime, and actual combat. A claimed
condition also needs a contrasting state in the same phase. The selecting
condition and any frequency of extra attackers remain unknown.

## Reported phases

The HTML page title and the Japanese-name/client-ID join in the
[walkthrough glossary](../studies/elemen-quest-rewards-walkthroughs/derived/glossary.md#client-cross-check-provenance)
bind each report to its English duty name. HTML line numbers are one-based
in the exact retained member. CSV locators are physical starting lines.
The source identities are pinned by the
[archive manifest](../sources/elemen-site-archive/manifest.yaml) and
[URL map](../studies/elemen-site-archive/derived/url-map.csv).
The archive preserves bytes; the historical claims retain `web-tables` tier.

| Source URL | Archive member relative to `sources/elemen-site-archive/objects/` | Bytes | SHA-256 | Walkthrough CSV selector |
| --- | --- | ---: | --- | --- |
| [Marauder3.html](http://elemen.sakura.ne.jp/ff14_dated_archives/quest/ClassQuest/Marauder3.html) | `ff14_dated_archives/quest/ClassQuest/Marauder3.html` | 20161 | `cad23a9c61d4dfdf881ce23a69d09305630e37a5eed5ea7ad1fabd2f558291c2` | Line 61, client quest 110102, Captain's Orders. |
| [Conjurer3.html](http://elemen.sakura.ne.jp/ff14_dated_archives/quest/ClassQuest/Conjurer3.html) | `ff14_dated_archives/quest/ClassQuest/Conjurer3.html` | 21160 | `dd281187229d5dce8ea7e40ae6b7e9d5447dc22453f250d019bc437f7fbd5f26` | Line 40, client quest 110262, The Call of Nature. |
| [common11.html](http://elemen.sakura.ne.jp/ff14_dated_archives/quest/MainQuest/common11.html) | `ff14_dated_archives/quest/MainQuest/common11.html` | 24039 | `7aaa7d51c526dc78d38bca80bb738aacd02fa17b37ad873a72122b51470f9e89` | Line 15, client quest 110019, Futures Perfect. |

The walkthrough product SHA-256 is
`1749166160a7567099932e9c59b70a4616962ae34ea4cf8e79535d5490fcb269`.
The phase reports below translate the source clauses without promoting a
reported time limit to an authenticated client-sheet budget or a reproduced
server expiry deadline.

| Duty and phase | Reported limit and mode | Reported trigger and consequence | Exact HTML locator; CSV coverage |
| --- | --- | --- | --- |
| Captain's Orders, first Moenskaet bout | 5 minutes; solo. | Expiry or PC HP reaching zero ends the battle, followed by an event. | Marauder3.html lines 153/161; CSV line 61 includes the clauses. |
| Captain's Orders, second Moenskaet group bout | 30 minutes; solo. | First-bout expiry/HP-zero consequence does not establish this bout's expiry outcome. | Marauder3.html line 185; CSV line 61. |
| The Call of Nature, Morris escort | 30 minutes; solo. | Too much separation from Morris forces content end. Morris HP at about 50 percent or lower separately forces content end. | Conjurer3.html lines 161/162/163; CSV line 40 includes these escort clauses. |
| The Call of Nature, Dreadwolves fight | 30 minutes; solo. | Morris HP at about 10 percent or lower forces content end. | Conjurer3.html lines 183/189. CSV line 40 includes the fight limit but omits the battle inset containing the 10-percent clause. |
| Futures Perfect, pursuit | 30 minutes; participant mode unreported in these clauses. | Too much separation from the Centurion group forces content end. | common11.html lines 162/168; CSV line 15. |
| Futures Perfect, combat | Separate 30-minute limit; participant mode unreported in these clauses. | Enemy HP damage from movement carries into combat. The reported limit supplies no expiry consequence. | common11.html lines 170/175; CSV line 15 includes the combat limit but omits the battle inset. |

The two Morris health clauses name the NPC, retain the source's approximate
wording, and belong to different phases. They establish neither exact
thresholds nor player KO or party-wipe rules. PC HP zero in the first
Captain's Orders bout is also distinct from party wipe. The report does
not establish a 1-HP lock, post-event HP or return destination.

## Terminal fields

`U` means unknown for that exact duty/phase and trigger in the cited evidence.
Each `U` is independent: grace period, fail-or-end classification, retry in
place, landing destination, HP poststate and participant outcome scope must
be established separately. A reported solo mode describes the source's
participation mode; it does not supply an observed roster or terminal
settlement for every participant.

The first-bout expiry cell preserves the source's reported battle end and
event. Its failure-versus-silent-end classification remains unknown.
A phase limit alone leaves the expiry consequence unknown in the other rows.

| Duty and phase | Trigger | Grace | Fail or end | Retry in place | Landing | HP poststate | Participant outcome scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Captain's Orders, first bout | Party wipe | U | U | U | U | U | U |
| Captain's Orders, first bout | Time-limit expiry | U | Reported battle end, then event; failure classification U. | U | U | U | U |
| Captain's Orders, first bout | Owner leave | U | U | U | U | U | U |
| Captain's Orders, first bout | Owner disconnect | U | U | U | U | U | U |
| Captain's Orders, first bout | Abandonment | U | U | U | U | U | U |
| Captain's Orders, second bout | Party wipe | U | U | U | U | U | U |
| Captain's Orders, second bout | Time-limit expiry | U | U | U | U | U | U |
| Captain's Orders, second bout | Owner leave | U | U | U | U | U | U |
| Captain's Orders, second bout | Owner disconnect | U | U | U | U | U | U |
| Captain's Orders, second bout | Abandonment | U | U | U | U | U | U |
| The Call of Nature, Morris escort | Party wipe | U | U | U | U | U | U |
| The Call of Nature, Morris escort | Time-limit expiry | U | U | U | U | U | U |
| The Call of Nature, Morris escort | Owner leave | U | U | U | U | U | U |
| The Call of Nature, Morris escort | Owner disconnect | U | U | U | U | U | U |
| The Call of Nature, Morris escort | Abandonment | U | U | U | U | U | U |
| The Call of Nature, Dreadwolves | Party wipe | U | U | U | U | U | U |
| The Call of Nature, Dreadwolves | Time-limit expiry | U | U | U | U | U | U |
| The Call of Nature, Dreadwolves | Owner leave | U | U | U | U | U | U |
| The Call of Nature, Dreadwolves | Owner disconnect | U | U | U | U | U | U |
| The Call of Nature, Dreadwolves | Abandonment | U | U | U | U | U | U |
| Futures Perfect, pursuit | Party wipe | U | U | U | U | U | U |
| Futures Perfect, pursuit | Time-limit expiry | U | U | U | U | U | U |
| Futures Perfect, pursuit | Owner leave | U | U | U | U | U | U |
| Futures Perfect, pursuit | Owner disconnect | U | U | U | U | U | U |
| Futures Perfect, pursuit | Abandonment | U | U | U | U | U | U |
| Futures Perfect, combat | Party wipe | U | U | U | U | U | U |
| Futures Perfect, combat | Time-limit expiry | U | U | U | U | U | U |
| Futures Perfect, combat | Owner leave | U | U | U | U | U | U |
| Futures Perfect, combat | Owner disconnect | U | U | U | U | U | U |
| Futures Perfect, combat | Abandonment | U | U | U | U | U | U |
| Their Finest Hour | Party wipe | U | U | U | U | U | U |
| Their Finest Hour | Time-limit expiry | U | U | U | U | U | U |
| Their Finest Hour | Owner leave | U | U | U | U | U | U |
| Their Finest Hour | Owner disconnect | U | U | U | U | U | U |
| Their Finest Hour | Abandonment | U | U | U | U | U | U |

For every Their Finest Hour failure row, participant credit and Earthbreaker
removal also remain unknown. Its successful completion remains the separate
participant-settlement question above.

The source reports the following additional triggers independently of the
five-trigger matrix. Their unspecified terminal fields remain unknown.

| Duty and phase | Additional trigger | Reported consequence | Remaining terminal fields |
| --- | --- | --- | --- |
| Captain's Orders, first bout | PC HP reaches zero. | Battle ends, then event; Marauder3.html line 161. | Grace, failure classification, retry, landing, HP poststate and participant outcome scope U. |
| The Call of Nature, Morris escort | Too much separation from Morris. | Forced content end; Conjurer3.html line 162. | Grace, failure classification, retry, landing, HP poststate and participant outcome scope U. |
| The Call of Nature, Morris escort | Morris HP about 50 percent or lower. | Forced content end; Conjurer3.html line 163. | Grace, failure classification, retry, landing, HP poststate and participant outcome scope U. |
| The Call of Nature, Dreadwolves | Morris HP about 10 percent or lower. | Forced content end; Conjurer3.html line 189. | Grace, failure classification, retry, landing, HP poststate and participant outcome scope U. |
| Futures Perfect, pursuit | Too much separation from Centurion group. | Forced content end; common11.html line 168. | Grace, failure classification, retry, landing, HP poststate and participant outcome scope U. |

Separation during pursuit or escort is not evidence of deliberate owner leave,
connection loss or accepted abandonment. The historical forced-end wording
does not identify failure text, silent termination, retry or landing behavior.
No common default or 60-second grace follows from these reports.

## Client contract boundary

`xivl-client-scripts:docs/quest-event-client-contracts.md#simplequestbattle-client-give-up-hook`
authenticates the generic `SimpleQuestBattleBaseClass.eventContentGiveUp`
question using worldMaster 25230. Its three known child overrides concern
quest IDs 111406, 111805 and 110736. This is a client question route, without
accepted abandonment or terminal settlement for the named duties above.

`xivl-client-scripts:docs/content-director-ui-contracts.md#guildleve-timer-card-and-instruction-helpers`
documents Guildleve UI arithmetic: start time plus 60 times the retained time
limit, and that sum minus 60. The Guildleve base reads its selected guildleve
sheet column 21. These facts do not establish named quest-phase sheet budgets
or a server grace interval. Authenticated client-sheet budgets and actual
observed expiry deadlines remain unknown for the named quest phases here.
