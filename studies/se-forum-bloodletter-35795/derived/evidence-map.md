# Evidence map - SE forum Bloodletter

This study records Bloodletter and Piety claims from five posts in the official
FFXIV forum thread "STR/DEX/PIE/ATK Testing." The selected posts were published
between 2012-01-21 and 2012-03-01. None has a named patch marker.

The forum discussion is player-authored. It is not an official mechanics
statement or a retail capture. Every source row is wiki-tier CALIBRATION
evidence with a `source-claim-only` verdict.

## Source and locators

- Stable id: `se-forum-bloodletter-35795`
- Source key: `se-forum-35795`
- Source manifest: `sources/se-forum-bloodletter-35795/manifest.yaml`
- Selected excerpt:
  `sources/se-forum-bloodletter-35795/objects/pages/thread-35795-bloodletter-posts.md`
- Derived ledger:
  `studies/se-forum-bloodletter-35795/derived/bloodletter-claims.csv`
- Source locators: post ids 524768, 527471, 527478, 533127, and 570492

## Source claims

Coglin answers yes when asked whether incremental PIE increases Bloodletter's
damage over time. The answer supplies no method, amount, or sample. Estellios
describes a preference for PIE for perceived Bloodletter and Shadowbind
reliability, without a test.

Mihana reports seeing more successful Bloodletter applications after changing
gear to 271 PIE and 298 DEX, while explicitly noting that no real test was
performed. A later post estimates a 60-70 percent application rate during one
Ifrit fight at about 290 PIE. Neither observation supplies an attempt count,
baseline, raw log, or controlled equipment and target state.

## Related evidence by tier

### Tier 1 - retail packet observations

`battle-result-backfit:derived/battle-result-rows.csv` has no retained command
27235 row. Generic damage and status message identities cannot be attributed to
Bloodletter. `status-wire-projection-census:derived/status-projections.csv`
contains no Bloodletter status projection. The retained packet corpus therefore
does not establish Bloodletter damage, status causality, application chance, or
expiry behavior.

### Tier 2 - retail video observations

`primal-battle-ifrit-bowl-of-embers:derived/evidence-map.md` covers a Conjurer
run and contains no Archer or Bloodletter observation. It cannot test the forum
claims.

### Tier 3 - web records

`elemen-battle-actions:derived/battle-actions.csv` identifies command 27235 as
the level 46 Archer action Bloodletter. It records 1500 TP, an 80-second recast,
a nominal 30-second duration, a physical attack with additional continuous
damage, Gloom Arrow as the combo condition, and qualitative damage when the
continuous effect ends. Those values remain web-table CALIBRATION evidence.

`elemen-battle-actions:derived/part-damage-map.csv` and
`lodestone-manual:derived/tables/incapacitation-weaponskills.csv` associate
Bloodletter with head incapacitation. They do not describe PIE, application
chance, or effect damage.

Generic PIE, enfeebling, magic-evasion, and Poison rows in other web studies are
not Bloodletter tests. They cannot supply a Bloodletter formula or status
mapping by analogy.

## Independent retail client-data cross-check

The public retail client-data export independently records command 27235 as
Bloodletter, a level 46 physical projectile action with a 1500 TP cost and an
80-second recast. The tracked export supports action identity and static command
parameters. It does not establish a Bloodletter status mapping, PIE behavior,
application chance, or numeric effect values.

Pinned public records:

- [Bloodletter command parameters](https://github.com/XIVLegacy/xivl-client-data/blob/76d68d2036dc99bdda2917e65efcdef4f62f4b63/derived/command_battle_params.csv#L1015)

## Claim limits

- The source does not establish that PIE changes Bloodletter damage or
  application chance as retail fact.
- No cited source establishes an Enfeebling Magic Potency causal chain,
  coefficient, cap, rounding rule, or landing formula.
- No cited source establishes an exact damage-over-time magnitude, tick
  interval, tick count, or expiry damage value.
- No retained packet or video observation binds Bloodletter to status 223127 or
  223241.
- No cited source establishes Bloodletter II behavior.
- Identity, calibration parameters, and qualitative behavior do not authorize
  numeric server policy.

## Verdict

The ledger faithfully preserves the player claims and keeps them below stronger
retail evidence. Existing records own Bloodletter identity and qualitative
action shape. PIE scaling, application chance, status assignment, effect
magnitude, expiry damage, and formulas remain unconfirmed. No numeric behavior
is promoted as retail-confirmed.

## Evidence gaps

- No patch-scoped controlled trial varies PIE while holding other inputs fixed.
- No retained result row binds command 27235 to damage or status events.
- No status projection binds either Bloodletter status id to the action.
- No observed expiry event supplies an exact damage value.
