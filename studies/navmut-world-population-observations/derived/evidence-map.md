# Navmut World Population Observations

## Confirmed

- The immutable source member sources/navmut-world-population-observations/objects/observations.jsonl is 262971 bytes with SHA-256 8bf6fb2a872e417f3cc94851d84fbf5bc7b76faca0d9164e493affdaeff40214.
- The source contains 650 unique schema-v2 observations.
- Zone counts are 128=237, 159=168, 190=245.
- Case-folded subject-type counts are misc=41, mmonster=1, monster=590, npc=18.
- Raw misc spellings are misc=40, Misc=1; case-folded misc=41.
- Canonical zone facets are 128=Lower La Noscea, 159=The Thousand Maws of Toto-Rak, 190=Mor Dhona.
- Review categories are a provisional deterministic partition: ambient=396, encounter=195, misc=41, npc=18.
- Monster classification promotes only Toto-Rak monsters and explicit quest/Grand Company/GC/boss/content note markers to encounter candidates; remaining overworld monsters are ambient candidates. NPC and misc records remain in their source categories.
- Zone 159 resolves to client internal name fst0Dungeon03 from xivl-client-data:manifests/zone_internal_names.json.

## Unverifiable

- Subject names remain raw Navmut labels. No client actor identity is promoted without a supported static-data join.
- Zones 128 and 190 remain numeric-only because no exact client zone binding for these ids is present in the reviewed client manifest.
- Position, map bounds, and rotation are not interpreted as a home point, spawn slot, respawn point, or respawn rule.

## Derived review products

- studies/navmut-world-population-observations/derived/observations.csv carries one row per observation with category and identity-status columns.
- studies/navmut-world-population-observations/derived/review-by-zone.md carries the same 650 records grouped by zone and category.

## Gaps

- Client actor ids, canonical display names, population slots, and home locations require a supported join or a separate retail observation; none is asserted here.
- Promotion gap: video URL is missing.
- Promotion gap: video title is missing.
- Promotion gap: video time ranges are missing.
- Promotion gap: source patch is missing.
- Promotion gap: respawn timing is missing.
- Promotion gap: confidence is missing; no per-record confidence grade is asserted.
- Promotion gap: respawn behavior remains unresolved and is not asserted.
