# Stage 4 Promotion Decision

## Decision rule

`SUPPORTED` requires the retained 1.23b rows to carry the variables needed to
distinguish the competing claim. `REFUTED` requires controlled rows that
contradict it. `INSUFFICIENT-DATA` means the corpus lacks that control even
when it supplies descriptive matched sets. Cartesian candidates and
one-to-one capacity are comparison inventories, not temporal pairs or
independent trials (`distribution-accounting.json:24-65`).

## Verdicts

| Contradiction | Verdict | Retained support and ceiling |
|---|---|---|
| Crit-rate anchor | INSUFFICIENT-DATA | 20 critical rows are available; nine strict sets contain 14 critical and 27 normal rows, with one-to-one capacity 12 and 51 Cartesian candidates. Six critical rows are unmatched, and zero sets preserve controlled attack trials, gear, Crit Rate, level, or dLVL (`distribution-accounting.json:35-42`; `matched-comparison-sets.csv:2-10`). The 1.23a 26.43% and 24.32% rows remain calibration anchors, not a 1.23b rate test (`../../bluegartr-stat-tests/derived/critical-hit-rate.csv:20-21`). |
| Crit-potency ordering | INSUFFICIENT-DATA | The same nine sets yield descriptive ratios 1.047619-1.730475 across 14 critical and 27 normal rows, but zero rows carry Crit Potency or cap/floor state. Thus zero controlled pairs distinguish potency-before-boundary from potency-after-boundary (`model-fit-accounting.json:22-31`; `matched-set-ratios.csv:2-10`; `../../bluegartr-stat-tests/derived/critical-damage-bonus.csv:5-9`). |
| Block reduction | INSUFFICIENT-DATA | Eight strict sets contain all 14 block rows and 17 normals, with one-to-one capacity 12 and 34 Cartesian candidates. Four zero-valued block rows are excluded from magnitude fitting; seven usable sets retain ten positive block rows and 16 normals with ratios 0.515267-1.071429. Zero pairs control Block, VIT, level, dLVL, gear, or buffs (`distribution-accounting.json:24-33`; `model-fit-accounting.json:12-21`; `matched-set-ratios.csv:11-18`). |
| Cure model | INSUFFICIENT-DATA | Three HP-recovery rows for command 27346 observe 151, 152, and 166 against SHA-recorded static magnitude 1000. Rows 174 and 396 form one repeated-context row pair; row 176 has a different source. Zero pairs control MND, VIT, healing potency, level, gear, or buffs (`recovery-model-observations.csv:3-4,7`; `hp-recovery-clusters.csv:8-9`; `model-fit-accounting.json:32-40,48-57`). Four Aegis Boon rows, 107/209/312/416, remain a separate identity and add zero stat-controlled pairs (`recovery-model-observations.csv:2,5-6,8`; `model-fit-accounting.json:2-10`). |
| DEF/VIT curve | INSUFFICIENT-DATA | All 622 decoded rows lack an actor-stat join; zero rows and zero pairs control DEF or VIT. Unknown gear, buffs, level, dLVL, and scenario mixing prevent a curve test (`model-fit-accounting.json:42-46,81-86`; `battle-result-rows.csv:1-623`). |

No contradiction is supported or refuted by this corpus. The static Cure
magnitude 1000 is supported only as client-data field identity; its conversion
to HP and native scaling remain unresolved
(`xivl-client-data:derived/command_battle_params.csv:1101`;
`xivl-client-data:docs/command-battle-params.md:167-176,192-208`).

## Matched-set inventory

Critical-rate and critical-potency decisions share these nine strict
scenario/command/source/target sets:

- Battlecraft, 22104/43722707/1158679894: normals 304/341, critical 314
  (`matched-comparison-sets.csv:2`).
- Battlecraft, 22104/43722707/1158679897: normals 408/432/435, critical 438
  (`matched-comparison-sets.csv:3`).
- Battlecraft, 22104/43723073/1158679843: normals 277/285, critical 273
  (`matched-comparison-sets.csv:4`).
- Battlecraft, 22104/43723073/1158679894: normals 308/336/340, critical 317
  (`matched-comparison-sets.csv:5`).
- Battlecraft, 23003/1158679892/43722707: normal 187, critical 181/218
  (`matched-comparison-sets.csv:6`).
- Battlecraft, 23003/1158679898/43722707: normals 431/437, critical 404
  (`matched-comparison-sets.csv:7`).
- Battlecraft, 23005/1158679898/43722707: normal 445, critical 412/425
  (`matched-comparison-sets.csv:8`).
- Job quest, 22104/43722707/1163947558: normals 574/575/580/581, critical
  571/572 (`matched-comparison-sets.csv:9`).
- Job quest, 22104/43722707/1163947559: normals
  515/516/520/521/522/529/532/533/534, critical 514/528/530
  (`matched-comparison-sets.csv:10`).

The block decision uses these eight battlecraft sets:

- 23003/1158679889/43722707: normal 96, block 106/157
  (`matched-comparison-sets.csv:11`).
- 23003/1158679892/43722707: normal 187, block 197/208
  (`matched-comparison-sets.csv:12`).
- 23005/1158679889/43722707: normals 116/122/146/161, block 102/128/137
  (`matched-comparison-sets.csv:13`).
- 23005/1158679890/43722707: normals 98/119, block 114/131
  (`matched-comparison-sets.csv:14`).
- 23005/1158679895/43722707: normals 299/307/327/338/379, block 311/332
  (`matched-comparison-sets.csv:15`).
- 23005/1158679897/43722707: normal 407, block 415
  (`matched-comparison-sets.csv:16`).
- 23005/1158679898/43722707: normal 445, block 420
  (`matched-comparison-sets.csv:17`).
- 23091/1158679895/43722707: normals 364/371, block 385
  (`matched-comparison-sets.csv:18`).

Cure has one repeated-context row pair, 174/396, but no normal-command or
stat-controlled comparison; row 176 is a different-source singleton
(`hp-recovery-clusters.csv:8-9`). DEF/VIT has no matched-set inventory because
no row carries either actor stat (`model-fit-accounting.json:42-46`).

## Promotion boundary

No rate, multiplier, reduction coefficient, healing coefficient, or DEF/VIT
curve is promotable. The durable outputs are the decoded observations, exact
message identities, strict matched-set inventory, descriptive ratio shapes,
and the five evidence-ceiling verdicts above.
