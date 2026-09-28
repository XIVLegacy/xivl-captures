# Evidence map - SE forum Paladin enmity

This study records three enmity claims from post 1 of the official FFXIV forum
thread "Tachi's Guide to Paladin (post 1.22b)." The author is Tango. The post
was published on 2012-06-09 and last edited on 2012-06-16.

Evidence class: web tables, wiki tier. Every row is CALIBRATION grade. The page
is a community guide hosted on the official forum, not an official Square Enix
mechanics statement or a retail capture.

## Source and locators

- Stable id: `se-forum-paladin-enmity`
- Source key: `se-forum-47393`
- Source manifest: `sources/se-forum-paladin-enmity/manifest.yaml`
- Selected excerpt: `sources/se-forum-paladin-enmity/objects/pages/thread-47393-post-1.md`
- Derived ledger: `studies/se-forum-paladin-enmity/derived/paladin-enmity.csv`
- Source locator: post 1, "Enmity Priorty Cycle," items 1, 3, and 4

## Recorded claims

| Action | Source claim | Qualifier | Verdict |
|---|---|---|---|
| Provoke | 750 enmity on use | Approximate | Source claim preserved. Not retail-confirmed. |
| Rampart | 180 enmity per affected member | No approximation marker | Source claim preserved. Not retail-confirmed. |
| Sentinel | 100 enmity per weaponskill and no effect on abilities | Approximate | Source claim preserved. Not retail-confirmed. |

The Rampart scope is narrow. The member must be hit by Rampart and already have
enmity on the current enemy. This study does not infer party size, target
selection, aggregation, or application order.

## Version scope

The `1.22b` assignment comes from the thread title. The post does not provide a
test timestamp, client build, packet sample, or independent patch attestation.
Every row therefore uses `patch_basis=thread-title-only`.

## Conflicts and related records

`bluegartr-stat-tests:derived/enmity.csv` records an approximate Provoke value
of 1000 for patch 1.21 and labels it an eyeball figure with no trial data. This
thread records an approximate 750 under a title that claims scope after patch
1.22b.
Both are community estimates from different patch scopes. The conflict remains
unresolved and the values must not be averaged.

The same BlueGartr table has a patch 1.21a Sentinel observation: its enmity
bonus appeared broken for abilities but worked for damage dealt. That is related
to the forum guide's ability exclusion, but it does not establish the numeric
value or a predicate limited to weaponskills.

## Verdict

The derived ledger is a faithful, narrow record of what the cited forum post
claims. It closes the missing public provenance record for the three source
comments. It does not by itself justify exact server policy. Provoke and
Sentinel are explicitly approximate, Rampart has no published method or sample,
and none of the three claims has retail packet or video corroboration.

## Evidence gaps

- No test method, sample size, raw log, or packet capture is attached.
- The thread title is the only patch anchor.
- The Provoke conflict is unresolved.
- Rampart aggregation and Sentinel trigger semantics are not independently
  observed.
