# Official battle patch announcements

These findings transcribe the rules announced in selected official posts.
They retain each patch's scope and do not assign 1.23b packet fields, native
state, server formulas or observed outcomes. The
[source manifest](../../../sources/official-1x-battle-patches/manifest.yaml)
owns complete HTML member identities and URLs; member names below are relative
to its restricted `objects/pages/` storage.

## Selected source posts

| Patch and member | Publisher and post | Displayed publication time | Selected section |
| --- | --- | --- | --- |
| `24910-patch1.19-Patch-1.19-Notes.html` | NOC_NA, `361386` | `09-30-2011 09:22 AM` | Battle, `dev1132` and `dev1151` |
| `32606-patch1.20-Patch-1.20-Notes.html` | NOC_JP, `476417` | `12-12-2011 08:29 PM` | Battle, class reforms |
| Same 1.20 member | NOC_JP, `476429` | `12-12-2011 08:39 PM` | Seven class action/trait tables |
| Same 1.20 member | NOC_JP, `476421` | `12-12-2011 08:31 PM` | System, `dev1250` and `dev1251` |
| `34137-patch1.20a-1.20a-Patch-Notes.html` | NOC_JP, `497816` | `12-27-2011 07:40 PM` | Item, `dev1291`; System, `dev1293`; Bug Fixes, casting graphics, Seeking Party and Thornmarch |
| `39024-patch1.21-Patch-1.21-Notes.html` | NOC_JP, `580990` | `03-08-2012 10:46 PM` | Battle, `dev1071` and `dev1302` |
| `43599-patch1.22-Patch-1.22-Notes.html` | NOC_JP, `660452` | `04-25-2012 09:24 PM` | Event, `dev1362`, `dev1363` and `dev1365` |
| `45067-patch1.22a-Patch-1.22a-Notes.html` | NOC_JP, `682107` | `05-09-2012 07:03 PM` | Event, `dev1404` and `dev1406`; Fixed Bugs, Garuda Hard Aerial Blast |

These are the forum's displayed times. No independent display-time timezone
or per-post revision identifier was established. Retrieval and archive times
are distinct source metadata in the manifest.

## Passive recovery in 1.19

Post `361386`, `dev1151`, announces stationary HP/MP recovery and separately
excludes players described as incurring enmity. Recovery grows with time spent
stationary. The recovery amount resets when the player is attacked, moves or
performs an action.
The paragraph supplies no numeric tick, growth curve or enmity-field test.
Source: [Patch 1.19 Notes][patch-119], Battle, `dev1151`.

## Link EXP in 1.19

The same post's second `dev1132` section announces these link bonuses:

| Additional linked enemies | Announced EXP bonus |
| ---: | ---: |
| 1 | 25% |
| 2 | 50% |
| 3 | 75% |
| 4 or more | 100% |

This is the Link Bonus table, distinct from the following EXP Chain table.
It does not identify a wire counter, a 1.23b scaling implementation or final
rounding. Source: [Patch 1.19 Notes][patch-119], Battle, `dev1132`, Link Bonus.

## Crowd control and movement casting in 1.21

Post `580990`, `dev1071`, announces category cooldowns:

| Category | Seconds |
| --- | ---: |
| Heavy | 180 |
| Slow | 180 |
| Petrification | 300 |
| Paralysis | 180 |
| Silence | 180 |
| Blind | 180 |
| Pacification | 300 |
| Amnesia | 300 |
| Stun | 30 |
| Bind | 180 |
| Sleep | 180 |

The announced progression applies to repeated successful uses on a target.
The first successful use starts the corresponding cooldown. Effect durations
on that target progress from full to half to quarter, followed by complete
resistance until the cooldown expires; expiry restores the initial step. The
notes separately state that target resistance is unchanged before the final
resistance step. They do not provide client status IDs or a native timer field.

The following `dev1302` paragraph announces that casting cannot begin during
movement and that movement interrupts an active cast. It does not quantify a
movement threshold, packet delay or interrupt probability. Source:
[Patch 1.21 Notes][patch-121], Battle, `dev1071` and `dev1302`.

## Interrupted enemy casting graphics in 1.20a

Post `497816` lists a fix for enemy casting graphics that persisted after
damage or a status ailment had interrupted the cast. This is a visual-state
bug-fix announcement. It neither says every damaging hit interrupts nor
establishes a chance or server-result sequence. Source:
[1.20a Patch Notes][patch-120a], Bug Fixes, enemy casting-graphics item.

## Equipped repair requests and player search in 1.20a

Post `497816`, `dev1291`, announces equipped-gear repair requests. Placing
a request requires gil and a dark-matter grade determined by repair level:

| Repair level | Gil required | Dark-matter grade |
| --- | ---: | ---: |
| 1-10 | 100 | 1 |
| 11-20 | 200 | 2 |
| 21-30 | 300 | 3 |
| 31-40 | 400 | 4 |
| 41-50 | 500 | 5 |

An open request shows a repair icon beside the player's name. Gear > Cancel
Request offers cancellation; repairing all gear alone does not automatically
close the request. The repairer's current class must match the item's repair
class, and Repair All selects the items that player can repair. The requester
supplies all dark matter. The announced repairer reward is gil and EXP based
on repaired-item level. Both players must remain nearby for repairs to be
possible; no distance number is supplied.

The same post's `dev1293` announces current online statuses in search results
and automatic Your Settings saving on Close, with Accept removed. Bug Fixes
also identifies an online-status reversion after leaving or disbanding a party
joined through Seeking Party: the erroneous restored value came from before
Seeking Party settings were made.

These are announced 1.20a rules. They do not establish direct 24244 acceptance
or settlement, an observed 1.23b debit/material/condition transition, or numeric
distance and EXP rewards. Source: [1.20a Patch Notes][patch-120a], post
`497816`, `dev1291` Making/Accepting a Repair Request, `dev1293`, and the
Seeking Party Bug Fixes item. Existing client contracts remain separate:

- `xivl-client-scripts:docs/repair-request-client-contract.md`.
- `xivl-client-scripts:docs/party-matching-client-contract.md`.
- `xivl-client-scripts:docs/search-recruitment-native-boundaries.md`.
- `xivl-client-structs:docs/repair-contract.md`.

## Thornmarch bug-fix announcements in 1.20a

Post `497816`, Bug Fixes nested items 10-14, announces fixes for these
pre-fix conditions:

| Item | Condition addressed |
| --- | --- |
| 10 | Enmity reset in the Good King Moggle Mog XII battle left the enemy no longer acting. |
| 11 | Opening its treasure chest with little time remaining failed to extend time. |
| 12 | Moogle-Go-Round, Mognesia and Pom Flare took effect with no targets in range. The item excludes Pukla Puki the Pomburner's Pom Flare. |
| 13 | Moogles healed at the point of death regained HP and continued fighting instead of dying. |
| 14 | Moogles using weaponskills at the point of death completed them before dying. |

The announcement supplies no reset algorithm, added-time amount, range
geometry, actor-to-command ID or weaponskill/death evaluation sequence.
The death items do not bind a staged-death resource or model state to a court
actor, revival or king-entry phase. These announced fixes are not observed
1.23b action/state/reset timelines. Source: [1.20a Patch Notes][patch-120a],
post `497816`, Bug Fixes items 10-14 and item 12's attached exception.

## Raise names in the 1.20 class tables

Post `476429` has seven class action/trait tables. Selecting their `Name`
columns by the header, the Conjurer table includes action `Raise` at level 18
and trait `Enhanced Raise` at level 48. No selected Name cell equals `Raise II`
or `Rebirth`. Post `476417` separately announces replacement of upper action
tiers with level-based scaling.

The name absence is confined to those complete player-class tables. It does
not establish absence from enemy actions, client resources, another patch or
all retail content. Source: [Patch 1.20 Notes][patch-120], posts `476417` and
`476429`, class reforms and the Conjurer table.

## Separate per-item market history announcement

Post `476421` announces a per-item display of the latest twenty transactions,
with histories cleared during maintenance. This is item-search history,
distinct from an individual retainer's aggregate sold-count report. The
announcement does not supply a request/reply schema, field encoding or an
offline-owner transaction. Source: [Patch 1.20 Notes][patch-120], System,
`dev1250`/`dev1251`, item-search changes.

## Preservation and reproduction

The current official pages and returned archive pages were preserved as
complete HTML responses. SHA-256 and byte size verification covers each
member listed in the source manifest. No images or linked detail pages are
part of this source selection.

Python 3.12.0 and BeautifulSoup 4.14.3 with `html.parser` selected
`li[id^="post_"]` and each post's `.postcontent`. Text extraction used
`get_text("\n", strip=True)`, then UTF-8 encoding for SHA-256.
Whitespace-normalized equality compares extracted texts after
`re.sub(r"\s+", " ", text).strip()`; the recorded text hashes
still identify the unnormalized extraction. The retained
[comparison receipt](post-comparison.json) contains no post bodies.
Its `both_posts_present` field requires the selected post in both a current
member and an archive member. Equality is `null` when either member or post
is unavailable, rather than reporting an unperformed comparison as different.
The extracted text of `361386` matched the 1.19 snapshot
`20120625214919`; `580990` matched the 1.21 snapshot `20120626004028`.
Those are exact extracted-text matches, not equal HTML files.

The 1.20 snapshot `20121025185324` contains only the opening post and lacks
`476417`, `476429` and `476421`. The reform, class-table and market findings
therefore use the pinned current official page.
The exact-URL archive availability lookup returned no 1.20a snapshot; its
finding also uses the current official page. Neither result proves absence
from other archive URLs.

For the action-name check, select post `476429`, take its seven leaf tables
(tables containing no nested table), derive the name-column index from each
header and compare stripped cell names. Keep the action and trait rows
separate; a textual occurrence check on the reforms paragraph is insufficient.
Other claims use the named post and section locators above. No game execution
or capture correlation is implied by these HTML checks.

[patch-119]: https://forum.square-enix.com/ffxiv/threads/24910-patch1.19-Patch-1.19-Notes
[patch-120]: https://forum.square-enix.com/ffxiv/threads/32606-patch1.20-Patch-1.20-Notes
[patch-120a]: https://forum.square-enix.com/ffxiv/threads/34137-patch1.20a-1.20a-Patch-Notes
[patch-121]: https://forum.square-enix.com/ffxiv/threads/39024-patch1.21-Patch-1.21-Notes

## Garuda admission and Aerial Blast announcements

### Patch 1.22 Event post

[Official post 660452](https://forum.square-enix.com/ffxiv/threads/43599-patch1.22-Patch-1.22-Notes#post660452), NOC_JP, displayed 04-25-2012 09:24 PM, dev1362/dev1363:

| Announced rule | The Howling Eye | The Howling Eye (Hard) |
| --- | --- | --- |
| Combat class level | 40+ | 45+ |
| Party size | 4-8 | 8 |
| Time limit | 30 minutes | 30 minutes |
| Victory reentry wait | 15 minutes | 15 minutes |
| Defeat reentry wait | 5 minutes | 5 minutes |
| Quest | City versions of In for Garuda Wakening | Taming the Tempest |
| Quest prerequisite | Deus ex Machina, Shadow of the Raven, or Careless Whispers completed | In for Garuda Wakening completed |
| Participant quest state | Same Wakening stage or completed | No additional quest-state condition listed |

The Hard quest was repeatable. An exit note allowed reentry after unclaimed
victory rewards without restarting the quest. Hard chest eligibility required
vortex fletchings at clear; nonstarting participants could enter without them
but forgo chest rewards. Vortex headdresses entered loot lists before inventory
and could be passed. Aurum Vale and Cutter's Cry changed from eight entrants
to four through eight, retaining difficulty designed for eight.

### Patch 1.22a Event and Fixed Bugs post

[Official post 682107](https://forum.square-enix.com/ffxiv/threads/45067-patch1.22a-Patch-1.22a-Notes#post682107), NOC_JP, displayed 05-09-2012 07:03 PM:

- Dev1404 added a participant option: undertaking the Garuda quest and having
  defeated Garuda, before quest completion. This post spells its title
  `In for Garuda Awakening`; the 1.22 post uses `Wakening`.
- Dev1406 announced a party commencement block when any member was synthesizing,
  gathering, mounted, seated or in active mode, naming raids, primal battles
  and hamlet defense as content classes.
- Fixed Bugs identified Garuda in the Hard battle failing to use Aerial Blast
  after HP fell to an unspecified level. This supports an announced HP/action
  relationship, without a numeric threshold or complete phase policy.

### Source comparison and behavior limits

The selected 1.22a post matched its snapshot at `20121025185209` after the
documented whitespace normalization. The 1.22 snapshot at `20121025113122`
preserved only opening post 660197, so the selected Event post was not
comparable. Display timestamps, archive timestamps and retrieval times remain
separate; no independent per-post revision identifier or display timezone was
available.

These are version-qualified official announcements. They do not prove a
1.23b actor/command binding, exact HP trigger, attack cadence, rock mitigation,
add sequence, reset order, accepted admission or reward settlement. The source
title spellings do not independently identify quest IDs.

## Local guildleve performance rewards in 1.22

Post `660452`, `dev1365`, announced these item rewards:

| Condition | Award |
| --- | --- |
| Successful completion | One item |
| Performance reaches 100 | One additional item |
| Performance reaches 300 | Another item becomes possible |

Crystal rewards also changed; quantities, item identities and odds were
unspecified. The source did not establish an evaluation formula or observed
1.23b rewards. The selected Event post was absent from the retained 1.22
snapshot, as recorded in the [post comparison](post-comparison.json).
