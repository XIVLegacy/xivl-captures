# Published Hamlet Defense rules

The official manual describes supply preparation, repeated instanced defense
battles, discipline-specific tasks, and success and reward conditions. These
are documented rules, not observations of 1.23b enforcement or settlement.

## Source identity and scope

The retained [Hamlet Defense manual](http://lodestone.finalfantasyxiv.com/pl/guide/hamletdef01.html)
is inventory row `hamlet-defense` in the
[per-page inventory](../studies/lodestone-manual/derived/file-inventory.csv).
Its member is `sources/lodestone-manual/objects/pages/hamlet-defense.md`,
8,927 bytes, SHA-256
`55319d6cd7cbae8dc3c3e814e1ca1bfb6ed96eba34f995c7fdac0a3c4bde2968`.
The matching entry in the [source manifest](../sources/lodestone-manual/manifest.yaml)
pins that transcription. The manifest's 2015-01-08 snapshot dates
preservation, not authorship or an executable version.

The source and [study](../studies/lodestone-manual/README.md) retain evidence
class `web-tables`, tier 3. First-party manual text establishes documented
intent. Packet and video observations outrank it for actual runtime behavior.
Line locators below refer to the pinned Markdown member. Its images are not
used, including the phase chart. Text alone supplies the durations below.

## Preparation and supply rating

Under "Preparing for Battle," paragraph at line 17, each hamlet begins its
50-hour non-combat preparation phase with supply rating zero. Donations add
points to a cumulative total, and reaching an unspecified threshold raises
the rating. The text identifies level 2 as the highest achievable rating
and allows unlimited contributions during preparation. The rating determines
beastman strength and the type of combat-phase rewards. No point conversion,
threshold table, or strength/reward formula is given.

"Participation and Individual Contributions" distinguishes two routes:

- War and Magic, lines 23-31: after joining a Grand Company, completing its
  listed caravan escort benefits the corresponding hamlet's supply rating
  in addition to standard escort rewards. The mapping is Twin Adder to
  Hyrstmill, Maelstrom to Aleport, and Immortal Flames to the Golden Bazaar.
- Land and Hand, line 35: delivering quartermaster-requested items or any
  materia-enhanced weapon or gear contributes to the rating and grants an
  anima boost based on the donated item type. This paragraph does not state
  the Grand Company prerequisite attached to the caravan route.

The quartermaster table, lines 37-40, labels the last hamlet "The Gold
Bazaar"; the caravan list at line 29 calls it "The Golden Bazaar."

## Combat participation and timing

"Defending the Hamlet," paragraph at line 45 and participation table at
lines 49-57, sets the rating after preparation and describes a 25-hour
combat phase containing repeatable instanced battles. Its rules are:

| Subject | Documented condition | Manual locator |
| --- | --- | --- |
| Entry | Speak with the hamlet's militia captain after the non-combat phase. All jobs/classes, levels 45-50, may participate in a full party of 8. | Paragraph 45; table rows 54-55 |
| Attempt duration | Each battle has a 30-minute time limit. This is distinct from the 25-hour combat phase. | Table row 56 |
| Class and equipment | No class restriction, but main hand weapons and soul crystals cannot change during battle. Battle Flow also says entry locks jobs and classes. | Table row 54; Battle Flow step 1, line 71 |
| Repeat attempts | Unlimited attempts during the combat phase, subject to participation conditions and a wait of 15 minutes after victory or 5 minutes after defeat. | Table row 57; Battle Flow step 7, line 122 |

"Hamlet Defense Phases," line 13, places the next-attack countdown in
Attributes' Timers tab. The separate
[patch 1.22b timer announcement](../studies/lodestone-dev-patch/derived/timer-announcements.md#announced-rules)
adds a condition of at least one previous Hamlet participation. The manual
does not state a first-appearance condition. Neither source proves immediate
discovery of a particular hamlet's timer or a native timer unit.

## Discipline roles during battle

"Defending the Hamlet," lines 59-65, assigns direct combat to War and
Magic, allied enhancement through synthesis to Hand, and enemy enfeeblement
through item delivery to Land. "Battle Flow" gives the following details:

| Discipline | Documented task and constraints | Manual locator |
| --- | --- | --- |
| War and Magic | Draw invaders away from unarmed Hand/Land players and lightly guarded supply carts. | Step 2, line 75 |
| Hand | Craft with parts found in the hamlet and deliver an unspecified number of completed items to the quartermaster to enhance militia allies. Carry either one part or one completed item at a time. Being attacked while crafting or holding a completed item loses the item. | Step 2, paragraph 79 and notes 81-83 |
| Land | Deliver intact alchemical pots to the quartermaster to weaken enemies. An effect is cast after three pots, either all the same type or three different types. Carry only one pot at a time. Being attacked while carrying it breaks and loses it. Different combinations produce different enfeeblements. | Step 2, paragraph 87 and notes 89-93 |

The page does not identify a color-to-effect combination, an exact synthesis
delivery count, effect IDs, magnitudes, or durations. Step 3, line 110, says
a powerful beast tribe leader joins after an unspecified time and changes
soldiers' attack focus through orders. It gives neither a complete enemy
roster nor named variant-specific action sets.

## Success, evaluation and rewards

The opening combat paragraph at line 45 calls the protected objectives four
supply caches. "Battle Flow" calls them four supply carts and states:

- Step 4, line 112: losing all four carts fails the mission.
- Step 5, line 116: defeating the beast tribe leader or protecting at least
  one cart for the duration of the invasion succeeds. Overall performance
  then determines a tallied score.
- Step 6, line 118: speak with the militia captain before leaving to receive
  payment. Rewards depend on battle performance and individual contributions
  to the supply caches during preparation.
- The note at line 120 ejects players 5 minutes after victory. Step 7,
  line 122, also permits leaving through the captain's relevant option.

These statements provide no score formula, evaluation point values, exact
reward quantities, item IDs, or observed contribution debit or payout.
Supply rating is not a documented formula for individual evaluation.

## Version qualifications and runtime limits

The [patch 1.22a Hamlet fix finding](../studies/official-1x-battle-patches/derived/evidence-map.md#hamlet-defense-bug-fix-announcements-in-122a)
owns the version-qualified announcement in official post `682107`, displayed
05-09-2012 07:03 PM. It states a correct 15-minute wait after abandonment,
distinct from the manual's victory/defeat waits. The manual says nothing
about abandonment. It also does not supply the patch finding's gathering-class
evaluation condition or top-twenty provisioner recognition. These are separate,
version-qualified announced fixes. The undated manual neither contradicts nor
independently confirms them. Neither source proves 1.23b policy.

The existing client findings at `xivl-client-scripts` revision
`d34ad3e47f563a46adabfd7f724bf8620441c682` retain their narrower scope:

- `xivl-client-scripts:docs/content-director-ui-contracts.md`, "Hamlet
  defense director," describes supplied HUD values and score presentation.
- `xivl-client-scripts:docs/hamlet-supply-ui-contract.md`, opening contract,
  separates supply, ranking and defense-score presentation from server policy.
- `xivl-client-scripts:docs/hamlet-delivery-selection-flow.md`, opening
  contract, describes menu results rather than accepted supply or payment.

The manual does not join those client values to a historical actor or
variant, prove phase enforcement or reset/cleanup order, or establish
actual buffs, scoring, completion, or settlement. Confirming those rules for
1.23b requires an attributable encounter lifetime with participation and phase
transitions, relevant actions and objectives, and completion-to-grant evidence.
