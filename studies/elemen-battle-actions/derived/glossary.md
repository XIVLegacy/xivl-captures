# Glossary - elemen-battle-actions EN layer

English applied to the derived CSVs. JP columns are verbatim; each `*_en` column
is derived from the maps below.

**Provenance.** `name_en_client` (actions/traits) and `ws_name_en_client`
(part-damage) are AUTHORITATIVE: the official 1.x client EN action name from
`xivl-client-data/csv/xtx_command.csv`, joined on the verbatim JP (JP col2 ->
EN col3), with `client_command_id` carrying the assigned command id. 226/226
actions and 15/15 part-damage WS resolve; there are no authored `(?)` names. The
per-class id assignment and the differing-EN twins are documented in
`evidence-map.md`. The following label columns are authored glosses (standard
FFXIV 1.x vocabulary; no per-string client id).

## Section (section_en)

| JP | EN |
|---|---|
| ジョブ専用アクション | job-specific action |
| アクション | action |
| 特性 | trait |

## Equip condition (equip_condition_en)

| JP | EN |
|---|---|
| 専用 | class-exclusive |
| ジョブ専用 | job-exclusive |
| ファイター専用 | Disciples of War only |
| 汎用 | general (any class) |
| - | (unspecified) |

## Body part (part-damage-map.csv, body_part_en)

| JP | EN |
|---|---|
| 頭 | head |
| 右腕 | right arm |
| 左腕 | left arm |
| 脚 | legs |
| 特殊（右部） | special (right) |
| 特殊（左部） | special (left) |
| 特殊（後部） | special (rear) |

## Class (class_en)

| JP | EN |
|---|---|
| 剣術 | Gladiator |
| 闘術 / 格闘 | Pugilist |
| 斧術 | Marauder |
| 槍術 | Lancer |
| 弓術 | Archer |
| 幻術 | Conjurer |
| 呪術 | Thaumaturge |

(`class/battle` labels the Pugilist row 格闘; the action pages use 闘術 - both
map to Pugilist.)

## Battle Regimen effects (tactics-battle-regimen.csv, effect_en)

Descriptive glosses; these are combo-bonus effect phrases, not `xtx_status.csv`
entries.

| JP | EN |
|---|---|
| 物理耐性の緩和 | physical resistance reduced |
| 魔法耐性の緩和 | magic resistance reduced |
| 詠唱速度ダウン＆消費ＭＰアップ | cast speed down & MP cost up |
| ＴＰ上昇抑制＆消費ＴＰアップ | TP gain suppressed & TP cost up |
| 行動適正アップ | action proficiency up |
| ダメージアップ | damage up |

## Column units

- `level` - class level at which the action/trait opens (site value).
- `tp` - TP cost (site value; `-` = none).
- `cast` / `recast_time` / `effect_duration` - seconds, printed with the source
  `秒` suffix (e.g. `10秒`); `-` = not applicable, blank = not printed.
