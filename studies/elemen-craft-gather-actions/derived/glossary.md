# Glossary - elemen-craft-gather-actions EN layer

English applied to `craft-gather-actions.csv`. JP columns are verbatim; each
`*_en` column is derived from the maps below.

**Provenance.** `name_en_client` is AUTHORITATIVE: the official 1.x client EN
action name from `xivl-client-data/csv/xtx_command.csv`, joined on the
verbatim JP (JP col2 -> EN col3), with `client_command_id` carrying the matching
command id. 167/167 rows resolve; no authored `(?)` names. The label columns
below are authored glosses (standard FFXIV 1.x vocabulary).

## Discipline

| value | meaning |
|---|---|
| hand | Disciple of the Hand (crafter) |
| land | Disciple of the Land (gatherer) |

## Section (section_en)

| JP | EN |
|---|---|
| アクション | action |
| ゴッドセンド | godsend |

## Equip condition (equip_condition_en)

| JP | EN |
|---|---|
| クラフター専用 | Disciples of the Hand only |
| ギャザラー専用 | Disciples of the Land only |
| 採掘専用 | Miner only |
| 園芸専用 | Botanist only |
| 漁釣専用 | Fisher only |
| 非戦闘用 | non-combat use |
| 汎用 | general (any class) |
| 専用 | class-exclusive |
| ジョブ専用 | job-exclusive |
| - | (unspecified) |

## Class (class_en)

| JP | EN |
|---|---|
| 木工 | Carpenter |
| 鍛冶 | Blacksmith |
| 板金 | Armorer |
| 彫金 | Goldsmith |
| 革細工 | Leatherworker |
| 裁縫 | Weaver |
| 練成 | Alchemist |
| 調理 | Culinarian |
| 採掘 | Miner |
| 園芸 | Botanist |
| 漁釣 | Fisher |

## Column units

- `level` - class level at which the action/ability opens (site value).
- `tp` / `cast` / `recast_time` / `effect_duration` - populated only for
  アクション-section rows; seconds with the source `秒` suffix; `-` = n/a, blank
  = not printed (all ゴッドセンド rows).
