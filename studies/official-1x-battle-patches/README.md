# Official FFXIV 1.x battle patch notes

This study records selected first-party announcements for patches 1.19, 1.20,
1.20a and 1.21: passive recovery, link EXP, crowd-control cooldowns, movement
and casting, an enemy casting-graphics fix, and the class-action lists.
It also identifies the separate per-item market-history announcement.

- [Evidence and source locators](derived/evidence-map.md) own the bounded
  announced rules and their limits.
- [Post comparison](derived/post-comparison.json) records which selected
  official posts matched the preserved historical snapshots.
- [Source manifest](../../sources/official-1x-battle-patches/manifest.yaml)
  owns the original and archive URLs, retrieval identities, member sizes and
  SHA-256 values. Restricted HTML bodies remain outside the public surface.

The source class is `web-tables`, tier 3. These are version-qualified official
announcements, not observed 1.23b client execution or authoritative server
transactions. A historical snapshot preserves its source; it does not change
the evidence class.

## Source scope

The source preserves four current official thread pages and three available
historical page snapshots. It covers the selected posts listed in the finding,
not every page or attachment in each thread. The selected 1.19 and 1.21 Battle
posts matched their historical snapshots after the documented text extraction.
The 1.20 snapshot lacks the selected class-action and market posts; no snapshot
was returned for the exact 1.20a URL.

The existing [Lodestone dev and patch study](../lodestone-dev-patch/README.md)
owns the earlier saved Lodestone topic collection and timer announcements.
This source has a separate identity because its originals are official forum
pages and snapshots, rather than members of that saved Lodestone archive.

## Verification

Verify every available source member against its manifest before inspection.
The finding describes the HTML selectors and text-hash comparison, and bounds
the class-action name check to seven identified tables. Repository refresh
checks validate the source/study/catalog contract; they do not reproduce a
retail game session.
