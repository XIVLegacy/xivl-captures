# Published Caravan Escort Duty rules

The official manual documents a four-adventurer escort limit, a recruit
exclusion, a quest exception for other companies' escorts, cargo handling,
and reward collection followed by optional return travel. These are
documented rules, not observations of 1.23b admission or settlement.

## Source identity and scope

The retained [Grand Company Guide](http://lodestone.finalfantasyxiv.com/pl/guide/cont01.html)
is row `grand-company-guide` in the
[per-page inventory](../studies/lodestone-manual/derived/file-inventory.csv),
line 30. Its member is
`sources/lodestone-manual/objects/pages/grand-company-guide.md`,
19,212 bytes, SHA-256
`daec7989504db2c4cbf289c8ce496ce417a2eb33ea6c1021ad19be25e52a5b2a`.
The [source manifest](../sources/lodestone-manual/manifest.yaml), member at
line 1065, pins that transcription. The
[immutable manifest](https://github.com/XIVLegacy/xivl-captures/blob/c5c9e7a39e3eec0a8c8fd27509475fdbff1bed8e/sources/lodestone-manual/manifest.yaml#L1065-L1067)
preserves the same identity.

Only "Caravan Escort Duty," lines 143-183 inclusive of the pinned member,
supplies the rules below. Images and other guide sections are outside this
finding. Sentence locators count prose sentences within the named line.
The source and [study](../studies/lodestone-manual/README.md) retain evidence
class `web-tables`, tier 3. First-party documentation establishes intended
behavior. Packet and video observations outrank it for actual runtime
behavior. The manifest's 2015-01-08 snapshot dates preservation. It selects
neither a retail patch nor a 1.23b ruleset.

## Participation and named recruiters

Line 149, sentences 1-3, places recruiting Grand Company NPCs near the
aetheryte at the listed locations. Participation begins by speaking to a
recruiter, then going to the caravan. A single escort permits at most four
adventurers. Line 157 excludes recruits, without assigning a numeric rank
threshold or a character-level requirement.

Line 169, sentences 1-2, ordinarily excludes duty accepted from another
Grand Company. Completing any of the "Don't Hate the Messenger" quests
permits those other-company escorts. Line 171 says rewards always use the
player's own company's seals, including when accepting another company's
escort. These statements do not supply a quest identifier or an actual
entitlement check.

The location list gives the following descriptions. Coordinates retain the
source's values. Provider names are shortened to omit rank titles.

| Company | Recruiting location | Provider name | Manual line |
| --- | --- | --- | --- |
| The Maelstrom | Camp Bloodshore / Eastern La Noscea (36, 20) | Friont | 161 |
| The Maelstrom | Camp Skull Valley / Western La Noscea (15, 18) | Larille | 163 |
| The Order of the Twin Adders | Camp Tranquil / South Shroud (38, 49) | Marquaile | 164 |
| The Order of the Twin Adders | Treespeak / North Shroud (22, 16) | Brenaile | 165 |
| The Immortal Flames | Camp Horizon / Western Thanalan (13, 29) | Mourelz | 166 |
| The Immortal Flames | Camp Drybone / Eastern Thanalan (39, 25) | Hanette | 167 |

These descriptions do not bind an NPC actor class, a historical placement
record, a destination route or a particular escort variant.

## Escort and chocobo handling

Line 151, sentences 1-2, says enemies target the cargo after departure.
Escorts protect the caravan and issue chocobo commands to reach the
destination before time expires. No numeric time limit is supplied.
Line 155 permits abandoning active duty through either the Grand Company
NPC or the caravan NPC.

Line 175, sentences 1-3, says cargo chocobos stop when they sense nearby
enemies. Enemy damage reduces their HP and may make them flee and drop
cargo. Talking to a chocobo exposes these commands:

| Command | Documented effect | Manual line |
| --- | --- | --- |
| Calm the chocobo | Restores HP. The caravan stops while that chocobo heals. | 179 |
| Feed the chocobo | Culinary items, with Gysahl greens as an example, restore HP. | 180 |
| Call the chocobo back | Appears when talking to a chocobo that fled. Selecting it returns that chocobo to the caravan. | 181 |
| Nothing | Closes the command screen. | 182 |

These descriptions provide no enemy-sensing radius, HP restoration amount,
damage-to-cargo conversion, food consumption rule or flight probability.

## Completion, rewards and return

Line 153, sentences 1-4, documents this order:

1. Reaching the caravan's destination completes the escort objectives.
2. Speak to the caravan NPC to collect the reward. Rewards vary with the
   amount of cargo delivered safely.
3. After receiving the reward, that NPC can teleport the player back to the
   Grand Company NPC from whom the escort was accepted.

Line 159 says defeating large numbers of enemies during duty may produce
rewards and bonuses on completion. This is a possibility, not a guaranteed
bonus or an enemy-count threshold. The section supplies no cargo unit,
reward formula, seal amount, bonus item identifier or contribution minimum.
It does not explicitly define a timeout result or an all-cargo-lost failure
condition.

The separate [Hamlet Defense finding](hamlet-published-rules.md#preparation-and-supply-rating)
owns the manual's corresponding-hamlet supply contribution rule. That rule
does not supply a Caravan reward calculation.

## Client and runtime boundaries

The following publications retain their distinct client evidence:

- [CaravanManager entry and question contracts](https://github.com/XIVLegacy/xivl-client-scripts/blob/051a57ef59323faf3e8f6a5ead6bb8a4d0383179/docs/caravan-entry-client-contract.md),
  "Incoming values" and "Historical admission boundary," owns argument
  frames, dialogue branches and returned choices.
- [Caravan reward guide client contract](https://github.com/XIVLegacy/xivl-client-scripts/blob/051a57ef59323faf3e8f6a5ead6bb8a4d0383179/docs/caravan-reward-client-contract.md),
  "Six-argument reward consumer" and "Reward and completion boundary,"
  owns supplied operands, reward presentation and the return-to-camp prompt.
- [Caravan entry and question text](https://github.com/XIVLegacy/xivl-client-data/blob/e37ce5ef10d189f471458305e2482dbedec4291c/docs/caravan-entry-text-contract.md),
  "Authored English content" and "Conditional caller joins," owns selected
  localized wording and conditional numeric-key matches.

Manual cargo and reward language does not assign units or producers to the
guide's six arguments or to director work fields. Recruit and quest wording
does not reinterpret the client's numeric comparisons as eligibility checks.
The manual does not prove actual manager or guide invocation, accepted
participation, contribution calculation, reward entitlement, settlement or
return travel. Confirming those for a historical variant requires attributable
retail evidence joining the provider, full call arguments, result and effect.
