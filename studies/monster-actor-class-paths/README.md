# Monster Actor-Class Paths

## Study contents

This study tests the 52 actor class IDs used by Bahamut's current Lower La
Noscea and Mor Dhona monster populations against retained FFXIV 1.23b packets,
decoded actor identity, and client-script class metadata. It does not modify or
promote Bahamut data.

## Start here

- `derived/mappings.csv` - one verdict for every configured actor class.
- `derived/occurrences.csv` - precise retained packet-lifetime joins.
- `derived/verdicts.md` - concise conclusions and Bahamut adoption boundary.
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
snapshot was taken read-only from Bahamut revision
`453691c2ad619234beb448aaefc3b234294c2539`; the exact inventory and catalog
files are pinned in `derived/accounting.json` by SHA-256.
The snapshot keeps only pool identity, the configured candidate path, the
historical catalog path, and the two decoded identity fields used by the join.

The actor-class/display-name and actor-graphic/base fields derive from the
FFXIV 1.23b client tables pinned by `xivl-client-data` revision
`bd3515848fe5564bab9eb901558ab918c427a709`. The source `actorclass.csv` and
`actorclass_graphic.csv` digests are recorded in `derived/accounting.json`.
The target snapshot also records each display-name/base pair's cardinality in
the complete 7,831-row graphic catalog so a shared pair cannot be promoted as
an exact actor-class identity.

The packet field locators are pinned to Bahamut revision
`453691c2ad619234beb448aaefc3b234294c2539`:
`src/common/protocol/game/s2c/0x00d6_set_actor_appearance.cpp:48` writes the
model ID first (SHA-256
`2edd15504afb2025665f9fafc98b925f331318756a9eb154f6e7fca9302623ef`),
and `src/common/protocol/game/s2c/0x013d_set_actor_name.cpp:66` writes the
display-name ID first (SHA-256
`23ee664cefd9c57c99a18de567e0d439b2eb4db8bf4bdaf3c26beee339e33e81`).

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

The display-name/base pair is then matched to the decoded actor tables. An
exact actor-class mapping requires a pair with global catalog cardinality one.
The generated occurrence rows retain capture name, decoded record indexes,
network actor ID, both identity fields, instance name, base class, and path.

## Findings

Puroboros actor class 2101608 is the only externally verified mapping. Two
separate retained lifetimes uniquely join it to
`/Chara/Npc/Monster/Cactus/CactusLesserStandard`. Both contradict Bahamut's
historical `/Chara/Npc/Monster/Bomb/BombNormalStandard` actorclass row.

Kobold Ascetic 2106637 and Kobold Pickman 2106628 remain unresolved. Neither
decoded identity pair occurs in a retained class-path lifetime, and each pair
is shared by multiple actor-class rows. The configured Goblin fallback is not
evidence of either mapping. Its spelling also differs from the script registry:
the registry class is `GoblinBommerGlaStandard`, not
`GoblinBommerglaStandard`.

Nine other paths are exact associations in Bahamut's pinned historical
actorclass catalog, but this corpus provides no independent retail occurrence
for them. They are labeled `catalog_only`, not retail-verified. The other 42
rows remain unresolved; configured family/job-compatible paths are retained
only as candidates.

## Bahamut boundary

Bahamut can safely adopt the retail-supported Puroboros path and should not use
the conflicting Bomb path. The nine `catalog_only` paths can preserve
Bahamut's own historical catalog authority, but this study does not upgrade
them to independent retail proof. No configured fallback, including either
Kobold fallback, is safe to present as an actor-ID mapping.

## Evidence boundary

A class file, registry record, family resemblance, display name alone, graphic
base alone, or reused network actor ID is insufficient. Missing retained
coverage is an irreducible historical limitation. No live client, runtime
probe, or new capture is requested.
