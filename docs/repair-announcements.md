# Repair rules announced for patch 1.18

The official "Repairing Repairs" post announced dark-matter materials,
skill-qualified repair success, and reduced NPC fees for patch 1.18. These are
versioned announcements, not measured 1.23b server behavior. The distinct
contribution is the announced material and success contract, not a resolution
of the existing NPC result-condition or self-repair transaction gaps.

## Source identity

- Source set: [lodestone-dev-patch](../studies/lodestone-dev-patch/README.md),
  retained as `web-tables` with first-party announced-intent qualification.
- Post: [Repairing Repairs](http://lodestone.finalfantasyxiv.com/pl/topics/detail?id=7da5e02bc548eb716fd549102886f25c0f7e693d),
  published 2011-07-15. The [per-page inventory](../studies/lodestone-dev-patch/derived/file-inventory.csv),
  row `repairing-repairs-2011-07-15`, owns the original URL and date.
- Retained member: `sources/lodestone-dev-patch/objects/pages/repairing-repairs-2011-07-15.md`,
  1,640 bytes, SHA-256
  `709481affa5904e867746a732c9abeba74d32d97d18eb89d506f0f7650ed32a7`.
  The [source manifest](../sources/lodestone-dev-patch/manifest.yaml), matching
  member entry, pins this transcription. Line locators below refer to it.

## Announced rules

The opening paragraph explicitly targets patch 1.18, and the success paragraph
describes the rule from that patch onward. Neither statement establishes that
the announced behavior remained unchanged in 1.23b. Source: lines 5 and 25.

"Simplifying Repairs" announces replacement of all repair materials with dark
matter. Its five grades cover equipment by optimal rank as follows. Source:
lines 9 and 13-19.

| Dark-matter grade | Equipment optimal-rank range |
| --- | --- |
| 1 | 1-10 |
| 2 | 11-20 |
| 3 | 21-30 |
| 4 | 31-40 |
| 5 | 41-50 |

Within the correct range, the material is usable for equipment of any class.
This describes material compatibility; it does not waive the repairer's skill
requirement. The post also lists vendor NPCs, guildleve rewards, and gathering
as ways to obtain dark matter, without naming vendors, rewards, or gathering
tables. Source: lines 9 and 21.

"Repair System Adjustments" announces guaranteed success when the repairer has
sufficient rank in the appropriate skill, together with a small overall
increase in the chance of using no materials. It supplies neither a numeric
skill threshold nor a material-saving probability or quantity. It does not
describe separate own-item and other-player execution rules. Source: line 25.

"NPC Repairs" announces a substantial fee reduction. It supplies no numeric
tariff, cost formula, or resulting condition percentage. Source: lines 27-29.

## Comparison and adoption limits

The [retail repair verdicts](../studies/retail-repair-contract/derived/verdicts.md#first-party-intent-not-runtime-proof)
already summarize the official manual's own-item repair intent: restoration
to 100 percent, appropriate dark matter, and no shards or crystals. Those
details come from the manual summary, not this announcement. The announcement
adds the patch 1.18 success rule and material-saving adjustment but gives no
own-item result condition.

The [manual repair table](../studies/lodestone-manual/derived/tables/repair-costs.csv)
records player repair commissions and material quantities. The later
[equipped repair-request announcement](../studies/official-1x-battle-patches/derived/evidence-map.md#equipped-repair-requests-and-player-search-in-120a)
owns the distinct 1.20a request and fulfillment rules. Its bands are labeled
repair level; this post uses equipment optimal rank. Matching numeric bands
alone do not establish that those fields are identical. Neither commission
schedule is an NPC tariff, and this post does not establish a request protocol,
material supplier, reward, proximity rule, or settlement transaction.

The [capture-proven NPC findings](../studies/retail-repair-contract/derived/verdicts.md#capture-proven-npc-repair-facts)
remain six one-gil charges for captured item levels 15-30. The fee-reduction
announcement neither generalizes that tariff nor supplies a measured condition
change. The capture has no attributable before/after durability update and no
retained self-repair execution, as the [study boundary](../studies/retail-repair-contract/README.md#scope-boundary)
states.

Consumers can adopt these additions as patch 1.18 announced rules with the
source identity above. A claim that they shipped unchanged in 1.23b still
needs version-specific historical or runtime corroboration. Exact eligibility,
repair-quality behavior, dark-matter consumption and saving, server
revalidation, and atomicity remain consumer-owned questions. Attributable
same-item condition updates and repair execution/result evidence remain
necessary to resolve the corresponding runtime gaps in the
[retail verdicts](../studies/retail-repair-contract/derived/verdicts.md#exact-gates).
