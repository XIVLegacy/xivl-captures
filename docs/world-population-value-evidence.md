# World population and drop value evidence

Reported item associations, reported placements and observed actors answer
different questions. A named actor or item does not establish a retail spawn
generator, drop probability or item-grant transaction.

## Drop values

The [Gamer Escape mob crosscheck](../studies/gamerescape-tables/derived/mob-client-crosscheck.csv)
joins reported mob names to client actor classes. Join an exact actor-class
token in `mob_range_actor_ids` to `mob_name`, then inspect the same mob's
`drops` cells in the [location table](../studies/gamerescape-tables/derived/mob-locations.csv).
Compare exact item names after case, spacing and punctuation normalization.
The cells contain both `Drops` templates and plain comma-separated item names.
A supported member of a list does not establish its other members.

These are historical wiki associations, `web-tables`, tier 3. The
[study evidence map](../studies/gamerescape-tables/derived/evidence-map.md#evidence-tier-and-version---read-first)
preserves the drifting 1.x version boundary. The
[checksums](../studies/gamerescape-tables/derived/checksums.sha256) pin the
promoted products. CSV data-record ordinals exclude the header and are
distinct from physical line numbers when a quoted cell spans lines.

For example, the location record for Bandit Spearman in Coerthas Western
Highlands lists Oak Chips, Sour Red, Ala Mhigan Mustard, Wild Onion and
Buffalo Hide. The crosscheck associates that reported name with actor class
`2180125`: crosscheck data record 69 and location data record 111. This
supports the named historical associations, without proving
that every deployment or level variant produces those items.

The [drop and party-loot finding](mob-drops-party-loot-evidence.md#per-mob-associations)
owns the quantity, chance and settlement boundaries. Printed percentages or
sample counts do not establish a universal 1.23b server rate. A reported
association does not establish quantity, independent rolls, crystal gates
or an attributable retail kill-to-item grant. Crystal element inferred from
a name or family has no drop-association authority by itself.

## Reported levels and HP

The same mob and location join can establish a reported level band when the
exact named zone and both endpoints agree. For example, location data
record 206 reports Cave Bat in Central Shroud at levels `5 - 9`, and the
crosscheck joins that name to actor class `2104102`. This is a historical
wiki report about the named mob and zone. It does not measure an individual
actor's level or establish positions, facing, population size or a generator.
Retain the source's `event_or_quest` label and variant limits with each join.
A broad region or a quest-associated report does not establish an ordinary
population in a narrower zone.

The [mob table](../studies/gamerescape-tables/derived/mobs.csv) and
[client crosscheck](../studies/gamerescape-tables/derived/mob-client-crosscheck.csv)
preserve these familiar HP reports. Each has `level_low=19`, with
`level_high` and `hp_high` empty. The HP field is specifically `hp_low`.

| Reported mob | Actor class | `hp_low` | Crosscheck data record | Source page revision |
| --- | ---: | ---: | ---: | --- |
| Peiste Familiar | 2200708 | 3181 | 504 | 89085, 2011-10-02T05:54:22Z |
| Drake Familiar | 2202206 | 2650 | 192 | 89585, 2011-09-30T14:41:41Z |
| Anole Familiar | 2200205 | 2783 | 50 | 89495, 2011-09-30T13:01:58Z |

These remain wiki-tier values. They do not establish HP at another level,
variant scaling, an exact 1.23b stat producer or a private encounter's roster,
position or timing. Page revision timestamps identify edits, not observations.

## Placement and timing boundaries

The [population study's field verdicts](../studies/monster-population-reported-observations/derived/evidence-map.md#field-verdicts)
separate supplied profile values, reported positions, authored habitats,
density expansions and generated companion offsets. Its
[observation table](../studies/monster-population-reported-observations/derived/observations.csv)
preserves decimal literals and individual observation keys. The study has
`historical-research` evidence class, tier 3. A supplied actor or zone label
does not authenticate a client identity, and a profile level is not a measured
level at a sighting. Authored or generated positions do not become measured
retail homes through a matching name.

The [retained comparisons](../studies/monster-population-reported-observations/derived/evidence-map.md#comparison-with-retained-observations)
keep numeric agreement separate from actor and zone identity. The
[Navmut study](../studies/navmut-world-population-observations/derived/evidence-map.md#unverifiable)
leaves homes, slots and respawn behavior unresolved. The
[packet sightings](../derived/spawn_observations.csv) establish observed actor
positions within their retained scope, without identifying a spawn generator.
None of these sources supplies a same-actor respawn timeline or establishes
the reported population's night windows. Exact homes, full XYZ/facing,
measured levels, respawn periods and time conditions require their own
attributable evidence.
