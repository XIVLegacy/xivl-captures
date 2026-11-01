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
| `34137-patch1.20a-1.20a-Patch-Notes.html` | NOC_JP, `497816` | `12-27-2011 07:40 PM` | Bug Fixes, enemy casting graphics |
| `39024-patch1.21-Patch-1.21-Notes.html` | NOC_JP, `580990` | `03-08-2012 10:46 PM` | Battle, `dev1071` and `dev1302` |

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
`get_text("\n", strip=True)`, then UTF-8 encoding for SHA-256. The retained
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
