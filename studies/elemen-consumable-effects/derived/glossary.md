# Glossary - eLeMeN consumable-effects token map

Every Japanese effect token in the two CSVs, mapped to the 1.23b client string
and its id. Attribute tokens join `xivl-client-data/csv/xtx_text_paramName.csv`
(JP col1 -> EN col2, id col0); status tokens join `xtx_status.csv` (JP col2 ->
EN col4, id col0). `effect_jp` in the CSVs is the authoritative value; `effect_en`
is a convenience gloss built from this table.

## Attribute / parameter tokens

| JP token | client param EN | client param id |
|---|---|---|
| DEX | Dexterity | 15006 |
| HP | HP | 15001 |
| HP回復量 | HP Regen | 16001 |
| INT | Intelligence | 15007 |
| MND | Mind | 15008 |
| MP | MP | 15002 |
| MP回復量 | MP Regen | 16002 |
| PIE | Piety | 15009 |
| STR | Strength | 15004 |
| VIT | Vitality | 15005 |
| 回復魔法威力 | Healing Magic Potency | 15025 |
| 変質制御 | Control | 15032 |
| 操作力 | Output | 15034 |
| 攻撃魔法威力 | Attack Magic Potency | 15024 |
| 敵視 | Enmity | 15052 |
| 物理クリティカル命中力 | Critical Hit Rating | 15020 |
| 物理クリティカル攻撃力 | Critical Hit Attack Power | 15022 |
| 物理加工 | Craftsmanship | 15030 |
| 物理命中力 | Accuracy | 15016 |
| 物理回避力 | Evasion | 15017 |
| 物理攻撃力 | Attack Power | 15018 |
| 物理防御力 | Defense | 15019 |
| 獲得力 | Gathering | 15033 |
| 識質力 | Perception | 15035 |
| 魔法クリティカル威力 | Magic Critical Hit Potency | 15038 |
| 魔法加工 | Magic Craftsmanship | 15031 |
| 魔法命中力 | Magic Accuracy | 15028 |
| 魔法回避力 | Magic Evasion | 15029 |

## Status-effect tokens (cure / debuff / self-buff items)

| JP token | client status EN | client status id |
|---|---|---|
| シェル | Shell | 223130 |
| プロテス | Protect | 223129 |
| 中毒 | Poison | 223011 |
| 敵視低下 | Enmity Down (enmity reduction) | 15052-adj |
| 暗闇 | Blind | 223007 |
| 睡眠 | Sleep | 228001 |
| 静寂 | Silence | 223006 |
| 麻痺 | Paralysis | 223005 |

## Fixed phrases (site vocabulary, verbatim)

| JP | meaning |
|---|---|
| 上限 | cap (absolute ceiling on the percentage bonus) |
| 回復量 | recovery amount (% of max HP/MP) |
| 効果時間 | effect duration (buff/debuff active time) |
| リキャストタイム | recast time (reuse cooldown) |
| 取得経験値 | EXP gained |
| 秘薬 / 妙薬 / 薬 | elixir / tonic / medicine (grade tiers) |
| 毒薬 | poison (throwing debuff item) |
| ◆◆ | site display marker for special-acquisition items (not part of the name) |

