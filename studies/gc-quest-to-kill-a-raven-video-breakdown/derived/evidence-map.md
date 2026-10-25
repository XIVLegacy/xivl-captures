# To Kill a Raven (Gridania): sampled quest video

> Use the stable source-object citations below to locate this study's evidence.

## Source and scope

Source: [FFXIV Patch 1.23 Company Quest - To Kill a Raven (Gridania Final Battle)](https://www.youtube.com/watch?v=6EHb-aUk0Hc) by RydiaMist, duration 39:32.
The [source manifest](../../../sources/gc-quest-to-kill-a-raven-video-breakdown/manifest.yaml) pins the single
immutable observation document, to_kill_a_raven_video_breakdown.md (`sources/gc-quest-to-kill-a-raven-video-breakdown/objects/to_kill_a_raven_video_breakdown.md`).
Upload/publication metadata is `2012-07-27T06:32:40-07:00`. It dates
publication, not recording. The 1.x HUD/action-bar vocabulary supports the
version family; exact recording patch remains unestablished.

Evidence class: `notes-and-transcripts`, video-breakdown tier. Observation,
reference and inference are kept separate. No implementation or tuning
recommendation follows from these records.

The observation record contains 48 accepted source-player positions, with its
stale seeks, advertisements and unrelated autoplay excluded. It is bounded
still sampling, not continuous viewing or an exhaustive transcript. Audio was
not reviewed. Source-player times locate retained pictures and log rows, not
their exact retail emission times. The source record does not establish exact retained video/frame identity. Client-text agreement
cannot certify that a string appeared in a particular picture. No media,
screenshot files or frame hashes were retained.

## Confirmed

These are bounded displayed-source readings, filtered by the text verdicts
below. A client match corroborates wording, not source pixels or mechanics.

| Source locator | Sampled observation | Bound |
| --- | --- | --- |
| 0:00;0:15 | Fulke's Gridania quest topic is highlighted, then an offer appears requiring Serpent Private Third Class or higher and recommending DoW/DoM level 45. It lists approximate 5,340 EXP and 6,000 Serpent Seals. | The intervening input and acceptance click were not sampled. These are advertised values, not receipts. |
| 1:00;5:54 | Retained accepted/journal/Heartstream/instance text; later Cid target with displayed four-to-eight DoW/DoM level 45 and one-of-three-quest requirements. | Text emission and transport causes are unsampled. No denial branch or enforcement was tested. |
| 12:11;12:51 | Rivenroad entering line and retained Hodder safety prompt; later Bard (Archer Level: 50) header and full-party UI. | Opening header reads Dragoon (Lancer Level: 50). Job-change operation, gear and soul-crystal transition were not observed. |
| 15:48;16:48 | First-form Thermionic Beam misses; later two separated fragment-defeat rows and the elemental-field notice. | No readies/casting precursor for Beam, exact event timing or spawn census. |
| 16:48;18:48;20:46;21:46 | Countdown readings 25:08, 18:20, 16:23, 22:30 across battle/cinematic samples; van/deus displayed-name change and a retained first-form defeat row. | The displayed discontinuity does not establish an exact timer-reset amount/cause, unedited clock mapping, actor lifetime or gauge meaning. |
| 25:43;27:40;28:40 | Lunar Dynamo readies, later named miss, and later golem territory/defeat text. | Not proof that these are the same execution or that Dynamo caused the co-displayed player defeat. Golem model/spawn/action pool were not sampled. |
| 31:07;35:34 | Unnamed bright orange effect; later Cid's victory narrative with retained journal/instance rows in a wooden room. | No readable Megaflare name/damage. The retained journal row alone establishes no new post-battle step or arrival cause. |
| 36:38-39:29 sampled positions | Garden ceremony. | No completion banner or actual EXP/seal receipt was observed in these samples. |

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
One source-selected pass authenticated all 803 members for three initially unresolved literal phrases. Named-table follow-ups identified their control-encoded templates; absence of a plain sentence was not treated as absence of behavior.

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
| QTXT001 / 0:00 | `To Kill a Raven (Gridania).` | title label terminal period distinct | `xtx_quest.csv:111633 f2` | Title words match the exact quest cell; the source topic's terminal period is not in that cell. Topic selection and any menu-added punctuation were not evaluated. |
| QTXT002 / 0:15 | `To Kill a Raven (Gridania)` | exact title label | `xtx_quest.csv:111633 f2` | Exact title cell; not a historical numeric quest argument or a reward receipt. |
| QTXT003 / 0:15 | `Serpent Private Third Class or higher` | compatible rank requirement components | `xtx__text_ui.csv:5057,5058,5059 f1`; `xtx_gcRank.csv:11 f10` | Rank name is exact at rank11 field 10. Three UI rank-column variants preserve or higher; actual selector and enforcement were not evaluated. Do not infer acceptance/denial behavior. |
| QTXT004 / 0:15 | `Disciples of War or Magic. Level 45` | eligibility level components full sentence unproved | `quest.csv:111633 f51`; `xtx_quest.csv:111633 f27,41` | The quest's discipline label and scalar45 corroborate the displayed components. The combined punctuation and rendered sentence are not a single literal cell; this does not test active-class runtime eligibility. |
| QTXT005 / 0:15 | `~5,340 experience points` | compatible approximate EXP offer format | `xtx__text_ui.csv:5054 f1` | Offer only. UI5054 has U+FF5E and a quantity control; the record uses ASCII ~. The displayed amount is not a received award. No EXP formula, selector evaluation or exact recording build is established by this text check. |
| QTXT006 / 0:15 | `6,000 Serpent Seals` | compatible seal offer static count corroborated | `quest_new_reward.csv:111633 f55,57`; `xtx__text_ui.csv:5041 f1`; `xtx_itemName.csv:1000202 f5,6,7` | Offer only. Static fields 55/57 contain item 1000202/count-shaped 6000 and itemName names Serpent Seal(s). Quantity/noun formatting remains dynamic. This is not a grant, balance change, final reward or receipt. |
| QTXT007 / 0:15 | `And she left specific instructions that you were to join her.[...]` | words agree; recorded punctuation convention differs | `gcl107.csv:242 f1`; `xtx_displayName.csv:1000114 f1` | U+2014 in the observation record is a transcription convention, not a pixel-certified encoded codepoint. Original gcl107 cell uses U+2500; word agreement does not certify source punctuation bytes or runtime speaker identity. |
| QTXT008 / 0:20 | `I sense you wonder at this invitation\u2014wonder that you should [...]` | words agree; recorded punctuation convention differs | `gcl107.csv:244 f1`; `xtx_displayName.csv:1000114 f1` | U+2014 in the observation record is a transcription convention, not a pixel-certified encoded codepoint. Original gcl107 cell uses U+2500; word agreement does not certify source punctuation bytes or runtime speaker identity. |
| QTXT009 / 0:20 | `Well, those around you\u2014myself included\u2014think it no wonder.` | words agree; recorded punctuation convention differs | `gcl107.csv:245 f1`; `xtx_displayName.csv:1000114 f1` | U+2014 in the observation record is a transcription convention, not a pixel-certified encoded codepoint. Original gcl107 cell uses U+2500; word agreement does not certify source punctuation bytes or runtime speaker identity. |
| QTXT010 / 1:00 | `"To Kill a Raven (Gridania)" accepted.` | compatible accept templates quote style distinct | `worldMaster.csv:25224,50152 f1`; `xtx_quest.csv:111633 f2` | Quest-label substitution templates; one has a quest/guildleve conditional. Source ASCII quotes differ from literal U+201C/U+201D. No selector, actual acceptance click or numeric quest ID was recovered. |
| QTXT011 / 1:00 | `"To Kill a Raven (Gridania)" has been updated in your journal.` | compatible journal template quote style distinct | `worldMaster.csv:25116 f1`; `xtx_quest.csv:111633 f2` | Journal25116 substitutes a quest title; source ASCII quotes differ from client curly quotes. No actual quest argument, exact advance trigger or completion reward is established. |
| QTXT012 / 1:00 | `Moving to the Heartstream.` | compatible moving place templates | `worldMaster.csv:60004 f1`; `xtx__text_ui(2).csv:203 f1`; `xtx__text_ui.csv:203 f1`; `xtx_placeName.csv:2091 f1,2` | WorldMaster and two UI203 cells have different place substitution paths. Article the and the historical path/argument were not evaluated. No transport trigger, duration, exact place ID or loading event follows. |
| QTXT013 / 1:00 | `You have entered an instance.` | exact system text | `worldMaster.csv:34108 f1` | Exact whole client cell. A retained row is not the exact entry execution timestamp or a resource binding. |
| QTXT014 / 1:00 | `The legatus has been discovered to the south and east of Camp[...]` | exact dialogue body | `gcl107.csv:253 f1`; `xtx_displayName.csv:2700006 f1,6,13,14` | Case and punctuation match the whole body cell. Speaker labels are checked separately; source timing, event dispatch, actor binding and attack pairing remain unproved. |
| QTXT015 / 1:00 | `Urianger of the Circle of Knowing informs us that many Allaga[...]` | exact dialogue body | `gcl107.csv:254 f1`; `xtx_displayName.csv:2700006 f1,6,13,14` | Case and punctuation match the whole body cell. Speaker labels are checked separately; source timing, event dispatch, actor binding and attack pairing remain unproved. |
| QTXT016 / 1:00 | `The workings of the legatus's mind are beyond our knowing.` | exact dialogue body | `gcl107.csv:255 f1`; `xtx_displayName.csv:2700006 f1,6,13,14` | Case and punctuation match the whole body cell. Speaker labels are checked separately; source timing, event dispatch, actor binding and attack pairing remain unproved. |
| QTXT017 / 3:57 | `What in the world was that explosion!? And what in the seven [...]` | exact dialogue body | `gcl107.csv:305 f1`; `xtx_displayName.csv:4000658 f1`; `xtx_gcRank.csv:27 f10` | Case and punctuation match the whole body cell. Speaker labels are checked separately; source timing, event dispatch, actor binding and attack pairing remain unproved. |
| QTXT018 / 5:54 | `Magdelin Vaire wishes to teleport you to Gridania.` | compatible teleport invitation template | `worldMaster.csv:34107 f1`; `xtx__text_ui(2).csv:100622,100851 f1,2,3`; `xtx__text_ui.csv:11319,74402,100622,100851 f1,2,3`; `xtx_placeName.csv:2001 f1,2,4,6` | Player Magdelin Vaire and destination grammar/lookup are dynamic. Complete Gridania label matches are retained; no actual destination numeric ID, acceptance or execution is established. |
| QTXT019 / 5:54 | `Teleporting...` | exact system text | `worldMaster.csv:34105 f1` | Three ASCII periods match. Retained Teleporting text does not identify the trigger or exact travel timestamp. |
| QTXT020 / 5:54 | `To travel to Rivenroad, you must be in a party consisting of [...]` | compatible entry requirement template controls unevaluated | `gcl107.csv:138,170,327 f1`; `xtx__text_ui.csv:11350 f1`; `xtx_placeName.csv:4073 f1,2`; `xtx_raidDungeon.csv:15 f26` | Three equal gcl107 cells use a duty-sheet substitution and encoded count/level controls. Four/eight/45 are video readings; these controls were not evaluated, so neither runtime parameters nor fixed client constants are assigned. No enforcement, mode or actual duty ID is established. |
| QTXT021 / 5:54 | `Furthermore, each party member must also have fulfilled the e[...]` | requirement body quote style distinct | `gcl107.csv:139,171 f1`; `xtx_quest.csv:111433,111633,111833 f2` | Two equal cells say fulfilled entry requirements for one of three quests, with curly quotes rather than source ASCII quotes. Related328 says completed To Kill a Raven and Living on a Prayer and is materially distinct, not a replacement. No server gate was tested. |
| QTXT022 / 9:51 | `There it is!` | exact dialogue body | `gcl107.csv:334 f1`; `xtx_displayName.csv:2700004 f1,6,13,14` | Exact body cell; any Nael Van Darnus speaker label is separately case-distinct from the lowercase-van name cell. No attack or actor-resource assignment. |
| QTXT023 / 11:51 | `And I, first among Thy servants, shall be honored to attend t[...]` | exact dialogue body | `gcl107.csv:197 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Exact body cell; any Nael Van Darnus speaker label is separately case-distinct from the lowercase-van name cell. No attack or actor-resource assignment. |
| QTXT024 / 11:51 | `I shall rend their bodies asunder and adorn Thy sanctuary wit[...]` | exact dialogue body | `gcl107.csv:198 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Exact body cell; any Nael Van Darnus speaker label is separately case-distinct from the lowercase-van name cell. No attack or actor-resource assignment. |
| QTXT025 / 12:11 | `Now entering Rivenroad.` | compatible entry template | `worldMaster.csv:52008 f1`; `xtx__text_ui.csv:11350 f1`; `xtx_placeName.csv:4073 f1,2`; `xtx_raidDungeon.csv:15 f26` | Duty label is substituted. Duplicate Battle/General panels are one retained reading; no runtime duty ID or transport input is recovered. |
| QTXT026 / 12:11 | `As a matter of form, I must mention at this juncture that you[...]` | exact dialogue body multiple equal cells | `gcl107.csv:179,333 f1`; `xtx_displayName.csv:1000232 f1` | Two equal safety-question cells remain candidates; Hodder's separate name cell does not select one. Prompt answer and original interaction were not sampled. |
| QTXT027 / 12:11 | `transport you and your comrades to the floating isle.` | partial literal suffix hold | `gcl107.csv:178,332 f1` | Keep only the observed suffix. Sentence start and speaker remain obscured/unknown; fuller client cells do not authorize completing the video transcription or naming its speaker. |
| QTXT028 / 12:51 | `You eat a haunch of smoked raptor, and find it to be divine.` | compatible food template | `worldMaster.csv:25209 f1`; `xtx_itemName.csv:3010011 f5,6` | Eat/eats, item noun/article and find/finds are conditional; the exact inline noun is haunch of smoked raptor. No renderer, numerical buff, potency or food effect magnitude is inferred. |
| QTXT029 / 13:51 | `Surrender yourselves to purity!` | exact dialogue body | `worldMaster.csv:34284 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Exact body; speaker capitalization and actor binding remain separate. No particular command is paired to the speech. |
| QTXT030 / 13:51 | `Nael van Darnus is no longer blinded.` | compatible status end components | `worldMaster.csv:30331,30338 f1`; `xtx_displayName.csv:2700001 f1,6,13,14`; `xtx_status.csv:223007 f4` | Status field4 contains dynamic subject/is-are plus no longer blinded without a final period. WorldMaster wrappers contain status-sheet substitutions and a final period. No renderer, actual status ID, source, resistance, duration or immunity is inferred. |
| QTXT031 / 14:51 | `Nael van Darnus is no longer slowed.` | compatible status end components | `worldMaster.csv:30331,30338 f1`; `xtx_displayName.csv:2700001 f1,6,13,14`; `xtx_status.csv:223003 f4` | Dynamic subject/is-are plus no longer slowed is a status component; wrappers carry final punctuation. No exact status lifetime, source, duration or runtime ID is proved. |
| QTXT032 / 14:51 | `Nael van Darnus suffers 570 points of damage from Bloodletter.` | compatible status damage template | `worldMaster.csv:32106 f1`; `xtx_command.csv:27235,27536 f2,3`; `xtx_displayName.csv:2700001 f1,6,13,14`; `xtx_status.csv:223127,223241 f3` | Suffer/suffers, subject,570 and point/points are dynamic. Raw32106 refers to xtx/status; two Bloodletter status-name rows and two command-name rows are retained separately. This is not a directly observed hit by a named attacker, a tier change or a damage coefficient. |
| QTXT033 / 14:51 | `I grow weary of this mummer's farce!` | exact dialogue body | `worldMaster.csv:34293 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Body punctuation including ASCII apostrophe matches; speaker capitalization is separate. No action pairing. |
| QTXT034 / 15:48 | `Nael van Darnus's Thermionic Beam misses.` | compatible named miss resolution | `worldMaster.csv:30311 f1`; `xtx_command.csv:23603 f2,3`; `xtx_displayName.csv:2700001 f1,6,13,14` | Preserve misses as a resolution verb, with dynamic possessive/command/optional-target grammar. No readies or begins-casting precursor, actual numeric command ID or repetition count is recovered. |
| QTXT035 / 16:48 | `Lunar debris is caught in the elemental field over Rivenroad.` | exact system text | `worldMaster.csv:34316 f1` | Exact elemental-field message; no spawn, landing, event total or action pairing follows. |
| QTXT036 / 16:48 | `Azran Hayat defeats the lunar fragment.` | compatible fragment defeat template | `worldMaster.csv:30108,30116,30117 f1`; `xtx_displayName.csv:3210903,3210904 f1` | Three equal defeat templates and two lunar-fragment name rows remain. Player name/You, defeats/defeat and article are dynamic. Duplicate panels and retained/repeated rows do not establish spawn totals or a new event at each sample. |
| QTXT037 / 16:48 | `Pathetic!` | exact dialogue body | `worldMaster.csv:34285 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Whole body matches with exact case and punctuation; speaker remains separately checked and unbound. No dialogue/command causal pairing or form/runtime ID is established. |
| QTXT038 / 17:48 | `Howl like the beasts that you are!` | exact dialogue body | `worldMaster.csv:34286 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Whole body matches with exact case and punctuation; speaker remains separately checked and unbound. No dialogue/command causal pairing or form/runtime ID is established. |
| QTXT039 / 19:46 | `...And for that would I gladly offer up both body and soul.` | exact dialogue body | `gcl107.csv:209 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Whole body matches with exact case and punctuation; speaker remains separately checked and unbound. No dialogue/command causal pairing or form/runtime ID is established. |
| QTXT040 / 19:46 | `O Mighty Dalamud! Red moon of destruction!` | exact dialogue body | `gcl107.csv:210 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Whole body matches with exact case and punctuation; speaker remains separately checked and unbound. No dialogue/command causal pairing or form/runtime ID is established. |
| QTXT041 / 19:46 | `Grant unto me Thy power, that I might carry out Thy will!` | exact dialogue body | `gcl107.csv:211 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Whole body matches with exact case and punctuation; speaker remains separately checked and unbound. No dialogue/command causal pairing or form/runtime ID is established. |
| QTXT042 / 20:46 | `Ahhh, yes! Yes!` | literal words interrupted by italic controls | `gcl107.csv:212 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Observed words and punctuation agree around two static italic-control tokens. They are not contiguous in the raw cell; no rich-text renderer was implemented or action paired. |
| QTXT043 / 20:46 | `The power...it courses through my being! I am... I am...` | partial literal prefix hold | `gcl107.csv:213 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Keep the observed prefix, including ellipsis spacing. The following scream remains untranscribed despite a longer client cell; do not complete missing pixels. |
| QTXT044 / 20:46 | `The hour is come.` | exact body substring multiple members | `gcl107.csv:236 f1`; `worldMaster.csv:34302 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Body matches within identical italic-wrapped cells in worldMaster and gcl107. Speaker Deus capitalization differs from lowercase-deus name cells; neither member nor runtime call site is selected. |
| QTXT045 / 20:46 | `Receive of me the gift of purity.` | exact body substring | `gcl107.csv:237 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Exact case-sensitive body occurs within gcl107 italic controls. The longer worldMaster Come lost child line has only a case-insensitive partial overlap and is not the same body or a mode binding. |
| QTXT046 / 21:46 | `You defeat Nael van Darnus.` | compatible first form defeat template | `worldMaster.csv:30108,30116,30117 f1`; `xtx_displayName.csv:2700001 f1,6,13,14` | Three equal defeat rows; You and victim are dynamic. Retained first-form defeat is not a sampled final-form killing action or exact timestamp. |
| QTXT047 / 22:46 | `Nael deus Darnus's Thermionic Beam misses.` | compatible named miss resolution | `worldMaster.csv:30311 f1`; `xtx_command.csv:23603 f2,3`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Preserve misses as a resolution verb, with dynamic possessive/command/optional-target grammar. No readies or begins-casting precursor, actual numeric command ID or repetition count is recovered. |
| QTXT048 / 22:46 | `Nael deus Darnus is no longer blinded.` | compatible status end components | `worldMaster.csv:30331,30338 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14`; `xtx_status.csv:223007 f4` | Status field4 contains dynamic subject/is-are plus no longer blinded without a final period. WorldMaster wrappers contain status-sheet substitutions and a final period. No renderer, actual status ID, source, resistance, duration or immunity is inferred. |
| QTXT049 / 23:43 | `I shall not suffer death.` | exact body substring | `worldMaster.csv:34307 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Body including terminal period matches inside italic controls. Speaker capitalization is separate; co-display with fragment rows is not an action pairing. |
| QTXT050 / 24:43 | `Nael deus Darnus suffers 570 points of damage from Bloodletter.` | compatible status damage template | `worldMaster.csv:32106 f1`; `xtx_command.csv:27235,27536 f2,3`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14`; `xtx_status.csv:223127,223241 f3` | Suffer/suffers, subject,570 and point/points are dynamic. Raw32106 refers to xtx/status; two Bloodletter status-name rows and two command-name rows are retained separately. This is not a directly observed hit by a named attacker, a tier change or a damage coefficient. |
| QTXT051 / 25:43 | `Nael deus Darnus readies Lunar Dynamo.` | compatible named ready template | `worldMaster.csv:30126,30127 f1`; `xtx_command.csv:23612,23627 f2,3`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Preserve readies: two equal ready templates and two Lunar Dynamo name IDs remain. No uses/casts replacement, execution time, numeric command ID or causal kill attribution is made. |
| QTXT052 / 25:43 | `Just so...` | exact body substring | `worldMaster.csv:34297 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Body matches within italic controls, preserving three ASCII periods. Co-display does not prove that Lunar Dynamo caused a defeat. |
| QTXT053 / 25:43 | `Nael deus Darnus defeats Level Ninetynine.` | compatible player defeat template | `worldMaster.csv:30108,30116,30117 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Subject/victim player Level Ninetynine and grammatical branch are dynamic. The row alone does not attribute the defeat to a co-displayed command. |
| QTXT054 / 26:43 | `You regain consciousness.` | compatible regain consciousness template | `worldMaster.csv:30109,33401 f1` | Two equal cells have dynamic subject and regain/regains. The source sentence is not a literal raw cell; KO cause and revival method remain unsampled. |
| QTXT055 / 26:43 | `I shall not suffer life.` | exact body substring | `worldMaster.csv:34306 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Body including period matches within italic controls. No particular attack or revival cause follows. |
| QTXT056 / 26:43 | `Protect` | exact label multiple name domains | `xtx_command.csv:27351,29015,29462 f2,3`; `xtx_status.csv:223129,223239 f3` | Literal Protect exists in three command and two status name rows. Floating text alone selects none, proves no caster/application/magnitude and does not authorize adding a tier suffix. |
| QTXT057 / 27:40 | `Nael deus Darnus's Lunar Dynamo misses.` | compatible named miss resolution | `worldMaster.csv:30311 f1`; `xtx_command.csv:23612,23627 f2,3`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Preserve misses resolution; ready event at another sample is not proved the same action. No casting classification, actual command ID or resource binding. |
| QTXT058 / 27:40 | `Oblivion... Well do I know thee...` | exact body substring | `worldMaster.csv:34309 f1`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Client body preserves the observed spaces after three-period ellipses inside italic controls. No punctuation normalization or attack pairing. |
| QTXT059 / 28:40 | `The lunar golem returns to its territory.` | compatible territory return template | `worldMaster.csv:34222 f1`; `xtx_displayName.csv:3208905 f1` | Preserve returns to its territory; related34223 says has returned and is distinct. Subject/article capitalization are dynamic. No golem model, movement trigger, leash rule or spawn count follows. |
| QTXT060 / 28:40 | `Level Ninetynine defeats the lunar golem.` | compatible golem defeat template | `worldMaster.csv:30108,30116,30117 f1`; `xtx_displayName.csv:3208905 f1` | Dynamic player and victim/article with three equal defeat rows. One retained row is not a total golem spawn count or action identification. |
| QTXT061 / 28:40 | `The target is too far above you.` | exact system text | `worldMaster.csv:32540 f1` | Exact error cell. It is not a complete distance/height targeting rule or a measured threshold. |
| QTXT062 / 29:40 | `Divinus Aequitas defeats the lunar fragment.` | compatible fragment defeat template | `worldMaster.csv:30108,30116,30117 f1`; `xtx_displayName.csv:3210903,3210904 f1` | Three equal defeat templates and two lunar-fragment name rows remain. Player name/You, defeats/defeat and article are dynamic. Duplicate panels and retained/repeated rows do not establish spawn totals or a new event at each sample. |
| QTXT063 / 30:17 | `You defeat the lunar fragment.` | compatible fragment defeat template | `worldMaster.csv:30108,30116,30117 f1`; `xtx_displayName.csv:3210903,3210904 f1` | Three equal defeat templates and two lunar-fragment name rows remain. Player name/You, defeats/defeat and article are dynamic. Duplicate panels and retained/repeated rows do not establish spawn totals or a new event at each sample. |
| QTXT064 / 30:40 | `Eden Rayne defeats the lunar fragment.` | compatible fragment defeat template | `worldMaster.csv:30108,30116,30117 f1`; `xtx_displayName.csv:3210903,3210904 f1` | Three equal defeat templates and two lunar-fragment name rows remain. Player name/You, defeats/defeat and article are dynamic. Duplicate panels and retained/repeated rows do not establish spawn totals or a new event at each sample. |
| QTXT065 / 30:40 | `You cannot use an item now.` | compatible conditional item error branch | `worldMaster.csv:32544 f1` | WorldMaster32544 contains the source words as ASCII hex in one conditional branch, with a literal terminal period outside it. The selector is unevaluated. Do not infer why the item was blocked or claim literal raw-cell equality. |
| QTXT066 / 31:02 | `Battle Voice` | exact tooltip label multiple name domains | `xtx_command.csv:27227 f2,3`; `xtx_status.csv:223253 f3` | Exact command27227 name and status223253 name; tooltip selection is not successful execution, application, magnitude or an actual command/status-ID binding. |
| QTXT067 / 31:12 | `Nael deus Darnus's Thermionic Beam misses.` | compatible named miss resolution | `worldMaster.csv:30311 f1`; `xtx_command.csv:23603 f2,3`; `xtx_displayName.csv:3210901,3210902 f1,2,6,8,13,14` | Preserve misses as a resolution verb, with dynamic possessive/command/optional-target grammar. No readies or begins-casting precursor, actual numeric command ID or repetition count is recovered. |
| QTXT068 / 35:34 | `Well, are you coming or what!?` | exact dialogue body | `gcl107.csv:214 f1`; `xtx_displayName.csv:2700004 f1,6,13,14` | Exact Cid body cell. Retained dialogue does not identify the preceding interaction's execution timestamp or prove reward receipt. |
| QTXT069 / 35:34 | `It's customary for the hero to attend the victory parade!` | exact dialogue body | `gcl107.csv:215 f1`; `xtx_displayName.csv:2700004 f1,6,13,14` | Exact Cid body cell. Retained dialogue does not identify the preceding interaction's execution timestamp or prove reward receipt. |
| QTXT070 / 35:34 | `You did it, Karina. You defeated van Darnus and stopped Dalam[...]` | compatible player name substitution | `gcl107.csv:216 f1`; `xtx_displayName.csv:2700004 f1,6,13,14` | gcl107216 contains a split control where Karina appears in the video. The name-substitution operation was not evaluated. Cid's narrative claim is not a seal/EXP receipt or independent mechanism proof. |
| QTXT071 / 35:34 | `"To Kill a Raven (Gridania)" has been updated in your journal.` | compatible journal template quote style distinct | `worldMaster.csv:25116 f1`; `xtx_quest.csv:111633 f2` | Journal template/title compatible, with ASCII-versus-curly quote difference. This is a retained row in the wooden room; arrival/emission and update cause are unobserved. The row alone establishes no new post-battle journal step, quest argument, completion or reward. |
| QTXT072 / 35:34 | `You have entered an instance.` | exact system text | `worldMaster.csv:34108 f1` | Exact whole client cell. A retained row is not the exact entry execution timestamp or a resource binding. |

### Exact distinctions

Speaker labels and dialogue bodies are separate. Recorded Van/Deus casing
is not silently changed to the lower-case van/deus name cells. Surrounding
italic controls are retained in the client comparison, not evaluated.
Straight recorded quotes remain distinct from literal U+201C/U+201D
(UTF-8 e2 80 9c / e2 80 9d). Three ASCII periods remain three periods; no
ellipsis or punctuation normalization was used.

U+2014 in QTXT007-009 is explicitly a transcription convention; pixels do
not establish the encoded punctuation. The corresponding gcl107 cells use
U+2500. QTXT005 records ASCII `~`, while UI5054 has U+FF5E and a number
placeholder. No EXP formula or multiplier was inferred from this text
check. Seal fields 55/57 are item 1000202/count-shaped
6000, with Serpent Seal(s) item-name cells; this corroborates an offer
component, not a grant. Entry count/level controls were not evaluated as
either fixed constants or runtime parameters. gcl107139/171's fulfilled
one-of-three condition is distinct from328's completed-two-quests condition.
QTXT027/QTXT043 remain partial. Protect/Battle Voice labels establish no
successful application or tier change; Bloodletter status/command names
remain separate. Job headers do not establish an intervening gear/crystal
change. Retained 35:34 journal text establishes no new post-battle step.

The static offer calculation is documented separately in
`xivl-client-scripts:docs/quest-offer-reward-display.md`. It is a client display
consumer finding, without establishing this recording's historical arguments,
build or reward receipt.

### Selected client-member pins

These `xivl-client-data:csv/` members were used for named-table or retained
cell comparisons. The archive/manifest owns the complete corpus identity.

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `gcl107.csv` | 183824 | `6443eae90fbf3572c553194c85658e54b0689a04aca8b2b5020efc52976cafa1` |
| `quest.csv` | 65577 | `bdadece1907b7050aaeee7c94a2a2d395fe76b504e47cbb1616b57ba380209dc` |
| `quest_new_reward.csv` | 326803 | `496d5e7d2e5057852f990e18f404524426d456c52cbcbd95544652494350ff66` |
| `worldMaster.csv` | 1851138 | `2e2e2dd5cd9651388f6fa575b4229081ad0452165e78b725df0a5b5b7cf7c643` |
| `xtx__text_ui(2).csv` | 397517 | `e33205165bda559ed69bb63664514f0e12b7c29fc219d13ae17fa740985eca82` |
| `xtx__text_ui.csv` | 1284564 | `23762a422118d99c4144a48b3495c52511b1b1b865e4fc50fdc61a973e3c6ece` |
| `xtx_command.csv` | 987740 | `2aa0b20822df0b2270918d9ac5525c86a34a941d7c66d17a106add1b2d6567d3` |
| `xtx_displayName.csv` | 838262 | `36c5dfba312695d9f4ee090dba123dfd7792feba55d88b0062c070d98abc0505` |
| `xtx_gcRank.csv` | 8390 | `79da51d4bd70e78f3af2dbcfccc018d6d9a85b93ef524ec187da2abb6663f297` |
| `xtx_itemName.csv` | 4428170 | `917c34eb0621b7d7a8261145023d0bb95cd8ca9eb52288ceb66e80d08f0d78c2` |
| `xtx_placeName.csv` | 357220 | `81467ef42e8aeba82fe95f6c4249356550c02e41e6734abf9fdd194051dc1714` |
| `xtx_quest.csv` | 2953504 | `938640466b314242916f1f8877a90154c4f4db7aa63de6223e6af4aa194e6719` |
| `xtx_raidDungeon.csv` | 2381 | `24c7e9a071c5a16b8a38254588e350e7e7b043e2dfe4129ecd5363d2f05f6059` |
| `xtx_status.csv` | 331062 | `60eca3b76d1d9799589d9059adeb1e7c3d142e07609a1ad0a053c5e75d9b96ee` |
| `xtx_text_skillName.csv` | 14017 | `170fd51685ab160989dd836c1d67ddf87e95627180cf17ab86dee271d04ab746` |

## Contradicted

No positive packet/client behavioral contradiction was established. Recorded
punctuation conventions and later-snapshot cell differences are textual
qualifications, not proof of what an earlier client rendered.

## Unverifiable

QTXT027 and QTXT043 remain partial. No client cell supplies their missing
start, speaker or continuation. Source times do not establish retained-row
arrival, a new 35:34 journal step, exact transition inputs or execution times.
The offer is not a receipt; the source does not prove that an unsampled award
was absent. The exact recording build, job-change operation, equipment,
soul-crystal transition, gauge meaning, actor continuity, threshold, timer
mechanism, spawning, ability pool, damage formula and final killing action
remain unresolved. No numeric runtime ID, resource/AI binding or shared
quest/repeatable-normal/Hard implementation follows.

## Unique value

The record provides an explicit Gridania company-quest offer and displayed
entry requirements, separate job headers, named readiness/miss/status/defeat
text, countdown discontinuity and return-room narrative. It preserves the
difference between an advertised reward and an observed transaction, and
between a retained journal line and a newly established progression step.

## Reference and inference

Patch 1.23 belongs to the original uploader title, not authenticated runtime
identity. The later 1.23b cells corroborate vocabulary/templates only.
The [Hard video](../../side-quest-rivenroad-hard-video-breakdown/derived/evidence-map.md)
and [Hard historical guide](../../se-forum-rivenroad-hard-51632/derived/evidence-map.md)
are separate evidence. Neither fills this source's unreadable effect/action
text or establishes a repeatable-normal option. In particular, an unnamed
orange effect is not promoted to Megaflare from those references.

## Gaps

Acceptance and transport inputs, refusal/failure branches, emission timing,
full combat/party state, precise countdown cause, full dialogue/action coverage,
post-battle journal causality and actual reward receipt remain unobserved.
No matching packet timeline was used to infer missing actions or causes.
