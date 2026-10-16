# Battle-Result Actor Join

## Study contents

This study joins every row of the battle-result backfit to the actor state
carried by the `0x0137` property stream. For both the source and the target
actor of each row it takes the nearest-preceding record of class, level,
hpMax, hp, mp, mpMax and tp in the same capture, and tags each value with a
join tier (T0 own preceding record, T1 capture-static value, T2 cross-capture
stat-ceiling bridge, T3 inferred). It adds no decoding and no capture.

With the join in place, the study evaluates recorded combat anchors: hit
outcome rates, damage bands, mob and player TP steps, engage order, Cure
values, actor identities, and a table of mob level and hpMax pairs. Each
anchor has a verdict of REPRODUCED, CONFLICT or UNRESOLVABLE.

## Start here

- `derived/evidence-map.md` - join tiers, methods, every anchor with its
  computed value, tier mix and verdict, and the conflict and gap notes.
- `derived/anchor-summary.csv` - one row per anchor: counts, bands, k
  interval, tier mix and verdict.
- `derived/joined-rows.csv` - the 622 rows with joined values, tiers and
  source record indices for both actors.
- `derived/tp-series.csv` - every tp record step per actor with its window
  classification and k bounds.
- `derived/engage-order.csv` - `0x0187`, `0x0195` and hateType events of each
  engagement.
- `derived/mob-level-hp.csv` - every spawned actor with a single level and
  hpMax value in a capture.
- `derived/accounting.json` - input digests, hard-assert counts, parameters,
  tier counts and bridges.

Regenerate or verify the products from this repository:

```text
python tools/extractors/extract_battle_result_actor_join.py
python tools/extractors/extract_battle_result_actor_join.py --check
python tools/extractors/extract_battle_result_actor_join.py --check --public-shape
```

The engage order reads the restricted `pcap-1.23b` objects. `--public-shape`
reuses the committed `derived/engage-order.csv` and regenerates every other
product from the retained CSV inputs. `--hash-names` optionally checks the
property names against an explicit copy of
`xivl-client-structs:manifests/gam_hash_names.json`; the extractor recomputes
the property hashes itself and reads no sibling checkout by default.

`tools/extractors/extract_wire_order.py` gives an independent view of the
`0x0187`/`0x0195` order. Its indices are its own subevent order, not the
`frame_index` used here:

```text
python tools/extractors/extract_wire_order.py sources/pcap-1.23b/objects/combat_autoattack.pcapng --direction s2c --around 0x0187 --before 0 --after 40
```

## Source material

- `xivl-captures:studies/battle-result-backfit/derived/battle-result-rows.csv`
  - the 622 decoded battle-result rows.
- `xivl-captures:studies/property-stream-hash-catalog/derived/property-records.csv`
  - the 9,307 decoded `0x0137` records.
- `xivl-captures:sources/pcap-1.23b` - the walked captures for engage order.
- Property names: `xivl-client-structs:manifests/gam_hash_names.json`.
- Command names: `xivl-client-data:derived/command_battle_params.csv`.

## Promoted conclusions

- The join reproduces the hit-outcome rates, damage bands, TP steps, k
  intervals, engage order and identity anchors listed in the evidence map.
- The 151, 152 and 166 Cure values reproduce, but row 176 (value 166) has
  source 43723073 and target 43722707, the reverse of its anchor statement.
- Mob hpMax at Lv8, Lv9, Lv11 and Lv17 in the 1.23b corpus differs from
  earlier-version comparison values; both are recorded.
- `xivl-captures:studies/battle-result-backfit/derived/promotion-decision.md`
  ruled its contradictions INSUFFICIENT-DATA for lack of this join. This join
  supplies levels and HP, MP and TP pools, but no gear or attributes.

## Topics

- Battle-result actor state join
- Hit outcome rates and damage bands
- TP gain and spend steps
- Engage order
- Mob level and hpMax

## Evidence gaps

- The join takes `source_actor_id` as the `0x0137` subject. A hp-delta check
  supports it on 149 of 234 damage rows, which is not proof.
  `xivl-captures:studies/player-hp-calibration/derived/evidence-map.md`
  records the same boundary.
- Gear and attributes are not joined, so damage stays banded.
- Class ids 2, 3 and 4 are not named.
- The Lv30 level of 43723073 in `war_quest_update2` is T3, and its Lv26 level
  in `party_battle_leve` is T2.
- 43723073 has no identity tuple in `combat_autoattack`, `combat_skills` and
  `war_quest_update2`.
- Mobs 1163947556-59 in `war_quest_update2` have k intervals near 0.469 but no
  level or hpMax record.

## Further research

Attribute and gear joins, or independent class identities, are needed before
these anchors can bound damage or HP formulas.
