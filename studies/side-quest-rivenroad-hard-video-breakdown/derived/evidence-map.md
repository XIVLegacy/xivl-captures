# Rivenroad (Hard): sampled video evidence

> Use the stable source-object citations below to locate this study's evidence.

## Source and scope

Source: [Order of the Blue Garter - Nael deus Darnus (Hard)](https://www.youtube.com/watch?v=nwvi79-qAjM) by Bluegarterls, duration 25:58.
The [source manifest](../../../sources/side-quest-rivenroad-hard-video-breakdown/manifest.yaml) pins the single
immutable observation document, rivenroad_hard_video_breakdown.md (`sources/side-quest-rivenroad-hard-video-breakdown/objects/rivenroad_hard_video_breakdown.md`).
Upload/publication metadata is `2012-08-16T00:17:37-07:00`. It dates
publication, not recording. The 1.x HUD/action-bar vocabulary supports the
version family; exact recording patch remains unestablished.

Evidence class: `notes-and-transcripts`, video-breakdown tier. Observation,
reference and inference are kept separate. No implementation or tuning
recommendation follows from these records.

The original record samples 26 distinct source-player positions. Fifteen were
reinspected: 00:00, 00:05, 00:30, 01:00, 01:05, 09:42, 10:02, 10:12, 10:17, 12:59,
15:34, 23:22, 24:22, 24:32 and 25:57. The other 11 positions are single-survey
observations: 00:15, 00:45, 02:10, 04:00, 06:00, 07:47, 09:02, 10:23, 18:10, 20:46
and 25:32. No continuous viewing, exhaustive transcript or event census is
claimed. Audio was not reviewed. Source compression obscures small text.
Whole-second player positions are reinspection locators, not exact retail
event times or proof of an unedited source/game clock relationship.
No video, screenshot file, frame digest or archived media bytes were retained.

## Confirmed

These are bounded displayed-source readings, filtered by the text verdicts
below. A client match corroborates wording, not source pixels or mechanics.

| Source locator | Sampled observation | Bound |
| --- | --- | --- |
| 00:00;00:05;00:30 | Serpent Private Dauremant nameplate/marker, then loading picture and Rivenroad (Hard) arena label. At 00:30 the countdown reads 29:30. | Entry menu selection, transport trigger and initial allowance were not observed. The 00:15 countdown remains unclear. |
| 01:05 | Tyrith Peng nameplate and polearm avatar; party UI; takes 32, Critical! 50 and Sixfold total 219 readings; lunar-curtain use reading. | Shared takes-lines do not identify an attacker/action or a damage coefficient. Job/gear/mitigation were not established. |
| 01:00;10:12 | Large purple/white effect, and later bright rings/light columns. | No readable Megaflare or Dalamud Dive execution line; naming or counting those effects is an inference from a separate account. |
| 09:42;10:02 | Nael deus Darnus is the lower target-display name in both pictures;10:02 has a bright central figure and a rear Disembowel 79 resolution. | No actor continuity or gauge meaning is assigned. Speech co-display does not pair it with a command. |
| 10:17;12:59 | Three identical retained cluster-obtain lines; later three red blocky forms including a partial left-edge form. | Not three new transactions or a complete population. The forms' names are unreadable. |
| 15:34;23:22 | Platform lightning notice, retained 15-minute warning, fire-shard and speech lines; later player's right-side Impulse Drive 308 and a separate unclear enemy readies line. | These are retained log readings; warning arrival, action pairing and the unreadable action name remain unresolved. |
| 24:22;24:32 | Lunar Dynamo miss, fragment/boss defeat readings and journal update already retained by 24:22; the journal line remains during 24:32 cinematic. |24:22 is not a before-update bound. Fatal action, exact journal arrival/cause and a full quest/reward transaction were not sampled. |
| 25:57 | Wide party cinematic with a red celestial body. | No reward window, turn-in or final amount was observed. |

### Client-text identity and method

Client corroboration uses `xivl-client-data:manifests/private_csv_corpus.json`,
input `decoded-csv-corpus-1.23b`, extraction `2012.09.19.0001`.
The archive provenance is `XIVLegacy/xivl-private-assets` commit
`8b38a02ce8ebf662b931092e46273251b38c58f0`,
`extracted/ffxiv-1.23b/client-data/csv.zip`, 70,110,686 bytes, SHA-256
`006f9438a8cfd9277376f0ab28474500c67e4665050aa631cae64c9e6f38a5b0`.
Selected member size, SHA-256 and parsed row count matched
`xivl-client-data:manifests/tables.json` before use. This later snapshot does
not authenticate the recording build.

UTF-8-sig CSV parsing used the original numeric/type headers and original
leading row IDs. Field N is physical CSV cell N+2. Name sets retain all exact
or casefold-equal cells in the named tables; equality does not select an actor
or command ID. Equal-template sets were compared on entire parsed fields.
No rich-text renderer, unknown-control evaluation or historical argument
selection was performed. Raw source excerpts below are abbreviated reading
locators; the immutable observation document preserves complete candidates.
The source-selected `Now Loading...` lookup authenticated all 803 members and found five exact UI cells.

Verdict vocabulary: exact means a whole raw cell or explicitly qualified body
span; compatible means only a template/component shape; label matches concern
vocabulary; distinct records preserve punctuation/case differences; held partial
means the missing pixels remain missing. All dynamic names, amounts, grammar,
articles, possessives and directions retain their source and template limits.


### Complete candidate verdicts

Each candidate ID locates the original reading, source time and readability
in the single observation document. Cues are shortened with `[...]`, which
is an editorial truncation marker, not added dialogue. Non-ASCII characters
in a cue are ASCII-escaped. The cell sets are literal catalog locators, not
observed runtime IDs. A held partial remains partial even when a client
cell contains a longer sentence.

| Candidate / source time | Recorded cue | Client verdict | Member:row:field set | Limit |
| --- | --- | --- | --- | --- |
| C01 / 00:00 | `Serpent Private Dauremant` | exact name | `xtx_displayName.csv:1300160 f1` | Exact displayed name candidate; no entry trigger, NPC runtime ID, menu selection or actor-resource binding. |
| C02 / 00:30 | `Now entering Rivenroad (Hard).` | compatible template | `worldMaster.csv:52008 f1`; `xtx_raidDungeon.csv:16 f26` | Entry text substitutes a raidDungeon label. The numeric duty argument and runtime row are unproved; the template is not the complete literal screenshot sentence. |
| C03 / 00:05 | `Now Loading...` | exact text multiple cells | `xtx__text_ui(2).csv:100230 f0,1`; `xtx__text_ui.csv:3147 f0`; `xtx__text_ui.csv:100230 f0,1` | Five exact matching cells across two UI members; no unique source-row or runtime UI-path assignment. |
| C04 / 00:30 | `Nael deus Darnus` | exact name multiple rows | `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Exact name has two name-row candidates; no actual actor ID, mode, lifetime or resource binding. |
| C05 / 00:30 | `Nael Deus Darnus: All shall return to nothingness.` | exact body substring speaker case distinct | `worldMaster.csv:34295 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Dialogue body is a case- and punctuation-exact literal substring inside italic controls. Speaker prefix is checked separately and is case-distinct from Nael deus Darnus; no speaker-to-row assignment. |
| C06 / 00:30 | `Lunar debris is caught in the elemental field over Rivenroad.` | exact text | `worldMaster.csv:34316 f1` | Exact whole cell; no spawn, landing, event count or mechanic follows from the text. |
| C07 / 01:05 | `Nael deus Darnus takes 32 points of damage.` | compatible template | `worldMaster.csv:30443 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Subject, take/takes, number 32, and point/points are dynamic; no literal sentence equality, source attacker, tuning value or action attribution. |
| C08 / 01:05 | `Critical! Nael deus Darnus takes 50 points of damage.` | compatible template | `worldMaster.csv:30444 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Critical! is literal; subject, takes, number 50 and plural are dynamic. Keep separate from C09; two visible equal lines do not prove two new events at the sample time. |
| C09 / 01:05 | `Sixfold attack! Nael deus Darnus takes a total of 219 points [...]` | compatible multihit template case unresolved | `worldMaster.csv:30442 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Raw template has a head-controlled count expression with encoded lowercase six followed by literal fold attack!. Preserve observed Sixfold capitalization; no renderer evaluated its capitalization or selector. Count and total 219 remain video readings, not fixed source values or mechanics. |
| C10 / 01:05 | `You use a lunar curtain.` | compatible item use templates | `worldMaster.csv:25205,40112,51007,51077 f1`; `xtx_itemName.csv:3020538 f5,6` | Item-name cells corroborate lunar curtain; templates contain noun/article/format and subject conditions. Article a is not evaluated. No exact row assignment or boss command Lunar Curtain is established. |
| C11 / 09:02 | `Carraway Author defeats the lunar fragment.` | compatible template | `worldMaster.csv:30108,30116,30117 f1`; `xtx_displayName.csv:3210903,3210904 f1` | Player Carraway Author and victim/article are dynamic. Three equal defeat-template rows cannot be distinguished by this line; no exhaustive fragment or kill count. |
| C12 / 10:02 | `Nael Deus Darnus: I shall raze the taint of gods and men alike.` | exact body substring speaker case distinct | `worldMaster.csv:34301 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Body matches literally inside italic controls; separately preserved speaker-prefix capitalization differs from the target-name cell. No action pairing. |
| C13 / 10:02 | `Your Disembowel hits Nael deus Darnus from the rear for 79 po[...]` | compatible positional template | `worldMaster.csv:30301 f1`; `xtx_command.csv:27272 f2,3`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14`; `xtx_text_directName.csv:4 f1` | Command and rear label exist; subject, target, direction selection, number 79 and point plural are dynamic. Related row 30313 has a distinct encoded spacing sequence and is not silently treated as equal. No body-part substitution was observed. |
| C14 / 23:22 | `Your Impulse Drive hits Nael deus Darnus from the right for 3[...]` | compatible positional template | `worldMaster.csv:30301 f1`; `xtx_command.csv:27275 f2,3`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14`; `xtx_text_directName.csv:2 f1` | Command and right label exist; direction selection and number 308 are dynamic. This is a player Impulse Drive reading, not an enemy Dalamud Dive reading; no body-part assignment. |
| C15 / 23:22 | `Nael deus Darnus readies [unclear].` | unreadable action verb compatible only | `worldMaster.csv:30126,30127 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Action remains [unclear]. The ready/readies template family supports only a possible verb structure; no name candidate or replacement is supplied and no screenshot pixels are repaired. |
| C16 / 10:17 | `You obtain the deaspected cluster.` | compatible obtain literal shell only | `worldMaster.csv:25022,25047,25049,25117,25228,25238,25246,33927,33932,40415,51118,51128,51129 f1`; `xtx_itemName.csv:10011254 f5,6` | Thirteen raw cells have the same literal You obtain/control-blocks/period shell; grammar, article the, quantity, formatting and historical selector were not evaluated. Three identical visible lines do not imply three spawn, drop or obtain transactions. |
| C17 / 15:34 | `Lightning crackles forth from the elementally charged platform!` | exact text | `worldMaster.csv:34318 f1` | Exact whole cell; no radius, damage, timing, target or periodicity inference. |
| C18 / 15:34 | `All party members who engaged in battle obtain a fire shard.` | compatible template | `worldMaster.csv:25034 f1`; `xtx_itemName.csv:1000003 f5,6` | Literal party-obtain prefix and item-name candidate; noun/article/quantity are dynamic. No reward total, drop source or quest-completion reward is established. |
| C19 / 15:34 | `Time remaining: 15 minutes (Earth time).` | compatible template multiple equal rows | `worldMaster.csv:52009,52092 f1` | Two whole-cell-equal templates preserve Time remaining: and (Earth time). Number 15 and minute/minutes branch are dynamic; no exact appearance time or enforced limit inferred. |
| C20 / 15:34 | `Nael Deus Darnus: Dalamud's will be done.` | exact body substring speaker case distinct | `worldMaster.csv:34319 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Body preserves ASCII apostrophe and terminal period inside italic controls. Speaker prefix is separate and case-distinct; no named Dive pairing. |
| C21 / 15:34 | `Nael Deus Darnus: I see all...` | exact body substring speaker case distinct | `worldMaster.csv:34299 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Body preserves three ASCII periods inside italic controls. Speaker prefix is separate and case-distinct; no action pairing or ellipsis normalization. |
| C22 / 24:22 | `Nael deus Darnus's Lunar Dynamo misses.` | compatible miss template | `worldMaster.csv:30311 f1`; `xtx_command.csv:23612,23627 f2,3`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Possessive speaker, command substitution, optional target and direction are dynamic. Both Lunar Dynamo name IDs remain; misses is a resolution reading, not readies or begins casting. |
| C23 / 24:22 | `Ashley Weiss defeats the lunar fragment.` | compatible template | `worldMaster.csv:30108,30116,30117 f1`; `xtx_displayName.csv:3210903,3210904 f1` | Ashley Weiss and victim/article are dynamic. Same three equal defeat-template candidates as C11; no spawn or repetition census. |
| C24 / 24:22 | `Adiyah Tulika defeats Nael deus Darnus.` | compatible template | `worldMaster.csv:30108,30116,30117 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Adiyah Tulika and victim are dynamic. Same three equal defeat-template rows; fatal action, exact instant and actual actor ID remain unproved. |
| C25 / 24:32 | `"The Raven, Nevermore" has been updated in your journal.` | compatible journal template quote style distinct | `worldMaster.csv:25116 f1`; `xtx_quest.csv:110870 f2` | Title110870 field 2 matches; journal25116 has a quest placeholder and curly quotes versus recorded ASCII quotes. Already retained by 24:22 and still visible at 24:32; exact arrival/cause and a full reward transaction remain unobserved. |
| C26 / 24:32 | `All party members who engaged in battle obtain a fire shard.` | compatible template repeated observation | `worldMaster.csv:25034 f1`; `xtx_itemName.csv:1000003 f5,6` | Same candidate wording as C18 retained later; do not double-count across timestamps or infer a separate reward transaction. |

### Exact distinctions

Speaker labels and dialogue bodies are separate. Recorded Van/Deus casing
is not silently changed to the lower-case van/deus name cells. Surrounding
italic controls are retained in the client comparison, not evaluated.
Straight recorded quotes remain distinct from literal U+201C/U+201D
(UTF-8 e2 80 9c / e2 80 9d). Three ASCII periods remain three periods; no
ellipsis or punctuation normalization was used.

C09's raw 30442 field 1 contains a head-controlled count expression with
encoded lowercase `six` (`736978`), then literal `fold attack!`. Recorded
`Sixfold` is preserved without evaluating capitalization/count controls.
C16's 13 obtain cells match a raw literal/control shell only; article,
quantity and rendering were not evaluated. C18/C26 repeat one retained
wording across pictures and do not prove two transactions. C15 is unreadable.

### Selected client-member pins

These `xivl-client-data:csv/` members were used for named-table or retained
cell comparisons. The archive/manifest owns the complete corpus identity.

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `worldMaster.csv` | 1851138 | `2e2e2dd5cd9651388f6fa575b4229081ad0452165e78b725df0a5b5b7cf7c643` |
| `xtx__text_ui(2).csv` | 397517 | `e33205165bda559ed69bb63664514f0e12b7c29fc219d13ae17fa740985eca82` |
| `xtx__text_ui.csv` | 1284564 | `23762a422118d99c4144a48b3495c52511b1b1b865e4fc50fdc61a973e3c6ece` |
| `xtx_command.csv` | 987740 | `2aa0b20822df0b2270918d9ac5525c86a34a941d7c66d17a106add1b2d6567d3` |
| `xtx_displayName.csv` | 838262 | `36c5dfba312695d9f4ee090dba123dfd7792feba55d88b0062c070d98abc0505` |
| `xtx_itemName.csv` | 4428170 | `917c34eb0621b7d7a8261145023d0bb95cd8ca9eb52288ceb66e80d08f0d78c2` |
| `xtx_quest.csv` | 2953504 | `938640466b314242916f1f8877a90154c4f4db7aa63de6223e6af4aa194e6719` |
| `xtx_raidDungeon.csv` | 2381 | `24c7e9a071c5a16b8a38254588e350e7e7b043e2dfe4129ecd5363d2f05f6059` |
| `xtx_text_directName.csv` | 226 | `f0e8df6fc67c03023563860378e0d79f1a5dd8ff8681e20f8d886c20c3821f03` |

## Contradicted

No positive behavioral contradiction with an inspected packet/client timeline
was established. Template and punctuation qualifications are not proved
runtime contradictions. A locator title containing before journal update is
not a temporal bound: the update is already retained by 24:22.

## Unverifiable

C15 remains unreadable. Gauge-fill comparisons are excluded from HP, healing,
threshold and reset conclusions. Exact actor lifetimes, source/arrival timing,
complete action pools, spawn counts, action/dialogue pairings, mitigation,
loot transactions, journal trigger, final rewards and recording patch remain
unresolved. The other 11 sample positions have no second-survey claim.
No exact runtime command/actor ID, resource, animation, director, authoritative
AI, or quest/normal/Hard equivalence follows from a name or message match.

## Unique value

The source supplies directly displayed Hard attribution, entry-context and
arena labels, contextual damage/item-use text, named resolution/defeat rows,
and a journal line already visible by 24:22. It separates a player's Impulse
Drive from the enemy's unreadable readiness text. These observations do not
identify the guide's Megaflare/Dive sequences as executed commands.

## Reference and inference

The [Carraway guide study](../../se-forum-rivenroad-hard-51632/derived/evidence-map.md)
owns the historical player account linked to this recording. Its reported
two-Megaflare phases, numerical mechanics and Dive behavior remain reference
claims. Associating the sampled bright effects with them is inference.
The separate [company-quest video](../../gc-quest-to-kill-a-raven-video-breakdown/derived/evidence-map.md)
does not establish a shared runtime mode or rule set.

## Gaps

Entry/return choices, full party/job/gear state, unobserved action text,
temporal predicates, populations, authoritative encounter conditions and a
complete reward/quest transaction remain unsampled. A matching packet timeline
was not used to fill these gaps. Source URL/time supports reinspection but not
byte identity or continuing availability of the external recording.
