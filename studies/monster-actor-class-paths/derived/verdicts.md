# Monster actor-class path verdicts

## Adoption boundary

Only the retained-retail join for Puroboros is externally verified. The
nine `catalog_only` rows are exact associations in Bahamut's pinned historical
actorclass catalog, but this study found no independent retail occurrence for
them. Configured family/job paths are candidates, not mappings.

| Actor class | Pool | Verdict | Path | Evidence |
|---:|---|---|---|---|
| 2101608 | puroboros | retail_supported_catalog_conflict | `/Chara/Npc/Monster/Cactus/CactusLesserStandard` | 2 retained lifetimes |

The Puroboros observations refute the historical catalog path
`/Chara/Npc/Monster/Bomb/BombNormalStandard`; both unique identity joins
use `/Chara/Npc/Monster/Cactus/CactusLesserStandard`.

## Priority Kobold results

- 2106637 `kobold_ascetic`: UNRESOLVED. The decoded identity pair (3106629, 10904) is shared by 4 actor-class rows and has no retained class-path lifetime. The configured Goblin path is only a family/job calibration.
- 2106628 `kobold_pickman`: UNRESOLVED. The decoded identity pair (3106624, 10904) is shared by 3 actor-class rows and has no retained class-path lifetime. The configured Goblin path is only a family/job calibration.

The client-script registry proves that `GoblinBommerGlaStandard` exists,
but its schema has no actor-class ID. The retained Goblin instantiate row
therefore does not identify either Kobold class.

## Historical catalog-only rows

| Actor class | Pool | Catalog path |
|---:|---|---|
| 2104004 | dire_rat | `/Chara/Npc/Monster/Lemming/LemmingStandard` |
| 2102001 | dodo | `/Chara/Npc/Monster/Dodo/DodoLesserStandard` |
| 2103904 | ladybug | `/Chara/Npc/Monster/Bug/LadyBugStandard` |
| 2102717 | musk_roseling | `/Chara/Npc/Monster/Flower/FlowerStandard` |
| 2104003 | plains_rat | `/Chara/Npc/Monster/Lemming/LemmingStandard` |
| 2102307 | ravenous_nannygoat | `/Chara/Npc/Monster/Yak/YakFemaleStandard` |
| 2104001 | wharf_rat | `/Chara/Npc/Monster/Lemming/LemmingStandard` |
| 2103901 | bumble_beetle | `/Chara/Npc/Monster/Bug/BugStandard` |
| 2102305 | aldgoat_nanny | `/Chara/Npc/Monster/Yak/YakFemaleStandard` |

## Unresolved rows

The remaining 42 rows are unresolved. Their configured paths
remain calibration candidates only; blank candidates stay blank. Exact rows
and candidates are retained in `mappings.csv`.

## Coverage and method

The extractor scanned 54 retained captures,
65665 decoded records,
831 instantiate records, and
368 lifetimes carrying both appearance
and display-name identity. It resets identity state on each `0x00CC`
instantiate, then joins `0x00D6` application `u32 +0x00` (graphic base)
and `0x013D` application `u32 +0x00` (display-name ID) for the same network
actor lifetime. Only a globally unique decoded pair can identify an exact
actor-class row.

The two positive rows are in `war_quest_update2.pcapng` at decoded record
indexes 1999/2007 and 2035/2043 (instantiate/name; appearance is recorded in
`occurrences.csv`), both on network actor `0x50e15b06`.

## Evidence boundary

Class-file or registry existence is not an actor-ID association. A matching
family name, graphic base alone, display name alone, or network actor ID
alone is insufficient. Network actor IDs are reused across lifetimes.
Missing retained coverage is an irreducible historical limitation; this
study does not request a new capture or runtime probe.
