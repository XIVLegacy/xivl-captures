# Monster Actor-Class Paths

## Study contents

This study tests the 52 actor class IDs in the supplied Lower La Noscea and Mor
Dhona monster-population snapshot against retained FFXIV 1.23b packets, decoded
actor identity, and client-script class metadata. It does not modify or promote
the source project data.

## Start here

- `derived/mappings.csv` - one verdict for every configured actor class.
- `derived/taxonomy.csv` - era family and decoded-race cross-check for every
  configured monster.
- `derived/occurrences.csv` - precise retained packet-lifetime joins.
- `derived/verdicts.md` - conclusions and population-catalog boundary.
- `derived/accounting.json` - corpus coverage and pinned input identity.
- `inputs/target_actor_classes.csv` - minimal reviewed population/catalog
  snapshot used by the deterministic join.

Regenerate or verify the canonical products:

```text
python tools/extractors/extract_monster_actor_class_paths.py
python tools/extractors/extract_monster_actor_class_paths.py --check
```

## Sources and identity

The runtime source is the 54-member `pcap-1.23b` corpus. The study's target
snapshot records source revision `453691c2ad619234beb448aaefc3b234294c2539`; the
exact source files are pinned in `derived/accounting.json` by SHA-256. The
snapshot supplies population identity, configured and catalog path candidates,
and the actor identity fields used by the join. Its path values are input data,
not paths decoded from the client tables below.

The actor-class/display-name and actor-graphic/base fields derive from the
FFXIV 1.23b client tables pinned by `xivl-client-data` revision
`bd3515848fe5564bab9eb901558ab918c427a709`. The source `actorclass.csv` and
`actorclass_graphic.csv` digests are recorded in `derived/accounting.json`.
The target snapshot also records each display-name/base pair's cardinality in
the complete 7,831-row graphic catalog so a shared pair cannot be promoted as
an exact actor-class identity.

The taxonomy cross-check joins every configured pool name against
`studies/gamerescape-tables/derived/mob-client-crosscheck.csv`. It records the
preserved era family and decoded client race beside the catalog, configured,
and observed instance paths. Family agreement is a sanity check, not proof of
an internal class-path association.

The extractor reads the application `u32` identity field at bytes `+16..+19`
for both s2c `0x00D6` appearance and `0x013D` name records. The joined record
indexes and decoded values are retained in `derived/occurrences.csv`; the
packet-field digest pins are in `derived/accounting.json`.

Client-script corroboration is revision
`9e564598c3804e543bb6dce2081e90ef559f4c4b`:

- `lua/registry.json`, SHA-256
  `957060c79fcce34f90b1840251c889ef8ee354f8380000518b1feb96f65dd78f`,
  contains `CactusLesserStandard` and `GoblinBommerGlaStandard`.
- `manifests/scripts.json`, SHA-256
  `86798306f71336ee494f12d395db3b8ea571a21224fbd99e2ef87ecd18c61300`,
  records their decoded Lua files.

These script artifacts prove class existence and inheritance only. Their
schemas contain no actor-class ID, display-name ID, or mob-name association.

## Method

Network actor IDs are reused, so the extractor starts a new lifetime at every
s2c `0x00CC` ActorInstantiate. Within that lifetime it joins:

- the `0x00CC` class path;
- `0x00D6` application `u32 +0x00`, the actor graphic base/model ID; and
- `0x013D` application `u32 +0x00`, the display-name ID.

The display-name/base pair is then matched to the decoded actor tables. A
globally unique pair identifies the actor-class row associated with the
lifetime. It does not turn the lifetime's instance class into the static
actorclass path.
The generated occurrence rows retain capture name, decoded record indexes,
network actor ID, both identity fields, instance name, base class, and path.

## Findings

The supplied population snapshot lists Puroboros actor class 2101608 as
`/Chara/Npc/Monster/Bomb/BombNormalStandard`. The preserved Gamer Escape join
also classifies Puroboros as Bomb, matching the decoded race. Two joined
retained Puroboros lifetimes show the instance path
`/Chara/Npc/Monster/Cactus/CactusLesserStandard`. This is a catalog/instance
path mismatch for those lifetimes; neither path is established here as the
static actor-class path.

Kobold Ascetic 2106637 and Kobold Pickman 2106628 remain unresolved. Neither
decoded identity pair occurs in a retained class-path lifetime, and each pair
is shared by multiple actor-class rows. The configured Goblin fallback is not
evidence of either mapping. Its spelling also differs from the script registry:
the registry class is `GoblinBommerGlaStandard`, not
`GoblinBommerglaStandard`. The era family and decoded race both identify these
rows as Kobold. The configured Goblin class therefore remains an implementation
calibration, not a taxonomy or mapping claim.

Nine other paths are present in the pinned population snapshot, but this corpus
provides no joined instance occurrence for them. Their paths remain unverified
catalog candidates. The other 42 rows remain unresolved; configured
family/job-compatible paths are retained only as candidates.

## Population-catalog boundary

The existing population catalog paths remain input candidates, not
retail-verified actor-class mappings. The two observed Cactus instance paths do
not establish a static replacement for the Puroboros Bomb candidate. The other
catalog paths are likewise unverified, while configured fallbacks remain
provisional implementation choices. No configured fallback, including either
Kobold fallback, is established here as an actor-class mapping.

## Evidence boundary

A class file, registry record, family resemblance, display name alone, graphic
base alone, reused network actor ID, or per-instance class path is insufficient
to establish a static actor-class path. Missing retained coverage is an
irreducible historical limitation. No live client, runtime probe, or new
capture is requested.
