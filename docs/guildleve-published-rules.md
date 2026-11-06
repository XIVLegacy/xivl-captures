# Published Guildleve rules and reform intent

The official manual describes offer renewal, regional participation and
completion, faction credits, and Leve History Evaluation. The 2011-06-29
"Guildleve Reforms" post announces a shift toward solo-oriented content and
changes to skill-point and item rewards beginning with patch 1.18. These add
documented intent to the selected retail observations. They do not establish
server behavior or unchanged shipment in 1.23b.

## Source identity and locators

Both retained sets use evidence class `web-tables`. Their first-party text
supports intended or announced rules, with the qualifications in the
[manual study](../studies/lodestone-manual/README.md) and
[dev/patch study](../studies/lodestone-dev-patch/README.md).

- Manual: [Guildleves](http://lodestone.finalfantasyxiv.com/pl/guide/guildleve01.html),
  inventory row `guildleves` in the
  [per-page inventory](../studies/lodestone-manual/derived/file-inventory.csv).
  Retained member `sources/lodestone-manual/objects/pages/guildleves.md`,
  8,037 bytes, SHA-256
  `6ced977bff76a843368c8baa1a1200ee6dbc166396ce41c47240596678085953`.
  The [source manifest](../sources/lodestone-manual/manifest.yaml), matching
  member entry, pins the transcription. Its 2015-01-08 archive snapshot is a
  preservation date, not a rule-authorship date or executable-version pin.
- Announcement: [Guildleve Reforms](http://lodestone.finalfantasyxiv.com/pl/topics/detail?id=04f9c77fc710c28b41266d6bb29a51563e165108),
  published 2011-06-29, inventory row `guildleve-reforms-2011-06-29` in the
  [per-page inventory](../studies/lodestone-dev-patch/derived/file-inventory.csv).
  Retained member
  `sources/lodestone-dev-patch/objects/pages/guildleve-reforms-2011-06-29.md`,
  2,755 bytes, SHA-256
  `e14964aa05a283e1c4d650a6eb026630b90b367ff8e94fa99c40cceff1608755`.
  The [source manifest](../sources/lodestone-dev-patch/manifest.yaml), matching
  member entry, pins the transcription.

Line locators below refer to these exact Markdown members. Images are not
used. The manual's general allowance, holding-capacity, Retry and Abandon
instructions are in lines 9-15. They do not establish actual allowance debit
or Retry execution.

## Manual acceptance and renewal

"Regional Guildleves," line 21, describes browsing with an allowance,
offers arranged by difficulty, and reviewing details and rewards before
acceptance. It says the counter list renews when allowances are added and
when levequests are completed or failed. "Local Guildleves," lines 61-63,
gives the same renewal conditions and separate lists for each Disciple of
the Hand class. Neither passage identifies the offer-pool producer or a
refusal transaction.

The Company-leve exception in line 17 allows acceptance regardless of the
number of held guildleves. It does not state an exemption from allowance
use. Line 7 separately restricts Grand Company levequests to full-fledged
Company members. These statements do not extend the regional or local
holding rules to Company leves.

## Manual regional participation and completion

The following rules come from "Undertaking Regional Levequests."

| Player decision or outcome | Documented rule | Manual lines |
| --- | --- | --- |
| Start and link | Start at the aetheryte named in the objectives. Party members can participate; members holding the same guildleve can also receive its specified rewards through leve linking. | 31 |
| Target visibility and attacks | Quest targets are visible only to participants, and only participants may attack objective targets. | 39, 49 |
| Success, return and reward | Success produces an aetherial node. Returning to the starting aetheryte through it is optional. The text places receipt of specified rewards at this completion stage without resolving reward timing relative to optional node use. Failure produces no node. | 43 |
| KO, area change or logout | A KO'd player can continue after returning to the home point. Changing area or logging out fails the quest for that participant while other party members may continue. | 43, 45 |
| Participation membership | Activation includes party members who are not already in another levequest. Later party changes do not alter participation status. The page also describes joining the leader's levequest by seeking its triggering aetheryte, without specifying the timing of that action. | 47, 51 |

These are published participation rules. They supply no paired-recipient
observation, actual mid-leve admission, reconnect delivery, or authoritative
reward transaction.

## Manual faction, local and history distinctions

"Faction Credits and Faction Leves," lines 55-57, links successful regional
completion to performance-based faction credits and regional factional
influence. Credits buy access to faction leves, with a stated holding cap of
1,000 credits. The page gives no performance formula or access price.

"Local Guildleves," line 77, directs players to the client after fulfilling
the request to receive payment, varied by overall performance. This is a
local hand-in description, distinct from the regional aetherial node. It
does not quantify evaluation or settlement.

"Leve History Evaluation Bonus," lines 81-85, permits a bonus levequest when
Leve History contains more than six leves. The type and number of completed
leves determine a special completion bonus. Accepting the bonus guildleve
clears the history and consumes one allowance. No selection or bonus formula
is provided.

## Reforms announced beginning with patch 1.18

"Guildleves Reborn," line 7, describes solo-oriented content with changes
beginning in 1.18 and continuing in future patches. This does not assign
every announced change exclusively to 1.18 or prohibit party play.

| Subject | Announced change | Announcement lines |
| --- | --- | --- |
| Regional skill points and linking | Remove the battlecraft skill-point bonus, reduce points per defeated enemy, and add completion skill points. Recommended versus actual rank, completion time, and partial participation affect the award. Reduce linking/sharing bonuses while raising the maximum linkable leves. | 11 |
| Regional and faction objectives | Revise certain leves' enemy counts, spawn conditions and target-item drop rates. Adjust enemy rank variation by difficulty. Revise excessive travel and introduce different routes for simultaneous groups. | 13-15 |
| Local skill points | Replace synthesis bonus skill points with completion rewards. Local skill-point awards require the corresponding class; regional completion as a class outside those recommended yields no skill points. | 19, 25 |
| Gil, marks and items | Adjust regional/local gil and guild-mark awards and revise item rewards to reflect city-state characteristics. Restrict guild-mark rewards to the city hosting the relevant guild, with an increased yield. The examples are Blacksmiths' marks in Limsa Lominsa and Conjurers' marks in Gridania. | 25 |
| Usability | Cancel returns from guildleve selection to the previous menu. Adjust commencement/completion messages and automatically update minimap marker positions. | 31-35 |

The post supplies no numeric reward formula, revised link limit, drop rate,
rank range, or per-leve route. These are announced changes, not measured
values. The manual's party and linking descriptions are compatible with a
solo-oriented design goal, but agreement does not authenticate runtime
implementation or an exact common version.

The guild-mark passages describe different scopes: the announcement plans
completion rewards, while manual "Guild Marks," lines 89-93, addresses
previously earned marks, exchange for items or four gil per mark, and planned
abolition in Version 2.0. They cannot be flattened into a single undated
reward schedule.

## Comparison with existing findings

The [publisher verdicts](../studies/regional-guildleve-publisher-contract/derived/verdicts.md)
own captured offer presentation, confirmation and synchronized journal
insertion. Their missing allowance check/decrement, offer eligibility,
durable persistence and payout remain missing. The manual adds intended
renewal and participation conditions; it does not fill those runtime gaps.

The [12487 lifecycle](guildleve-12487-observed-lifecycle.md) owns the selected
Director, content-group and object-lifetime observations. Manual target
visibility and party rules do not identify that leve's enemies, prove
objective causality, or generalize one recipient's records into delivery
policy.

The later [patch 1.22 local performance rewards](../studies/official-1x-battle-patches/derived/evidence-map.md#local-guildleve-performance-rewards-in-122)
already own their announced item thresholds and unspecified crystal changes.
That later announcement is distinct from this post's earlier skill-point
reform and the manual's unquantified performance payment.

Confirming these rules for 1.23b still requires attributable allowance and
offer transitions, participant and recipient observations, per-leve objective
and difficulty producers, history/credit mutations, and completion-to-grant
evidence for the relevant content type. The two pages provide neither actual
Retry execution nor settlement or persistence observations.
