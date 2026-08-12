# Glossary - elemen-bestiary EN layer

English glosses applied to the derived CSVs. The JP columns remain verbatim;
each `*_en` column is derived from the maps below.

**Provenance.** `skill_name_en` is AUTHORITATIVE: the official 1.x client EN
action name from `xivl-client-data/csv/xtx_command.csv`, joined on the JP
name, with `client_command_id` carrying the matching command id(s) for a
direct cross-reference (same-named variants share one EN and list every id).
187 of 195 distinct skill names resolve there; the 8 that do not are the
descriptive placeholders (normal/ranged attack, magic) plus 3 genuinely
absent names left as a `(?)`-flagged reconstruction (Eye of the Beholder,
Flying Mareen, Fated Gaze). Status effects (the 効果 column) are also
client-authoritative: the official status name from
`xivl-client-data/csv/xtx_status.csv` (col 4, NFKC-matched on the JP
token) - e.g. アビリティ不可 = Amnesia, WS不可 = Pacification, 沈黙 = Mute,
全ステータス－ = Imperiled, 詠唱妨害無効 = Glossolalia. NM range-cell spell
lists resolve against xtx_command.csv. Elements, cast colors,
damage/interrupt flags, AoE geometry, and taxonomy labels are the standard
FFXIV mechanics vocabulary; non-status effect tokens (Knockback, HP drain,
flavor parentheticals) keep an authored gloss.

NM names (`scope_en` where `is_nm=y`) are the client actor name from
`xivl-client-data/csv/xtx_displayName.csv` (all 36 resolve), with
`client_actor_id` for cross-reference; the client stores a lowercase base
form, shown here in in-game title case (minor words lowercased).

## Elements

| JP | EN |
|---|---|
| 火 | Fire |
| 炎 | Fire |
| 氷 | Ice |
| 風 | Wind |
| 雷 | Lightning |
| 土 | Earth |
| 水 | Water |
| - | none |

## Cast-effect colors

| JP | EN |
|---|---|
| 赤 | Red (damage) |
| 黄 | Yellow (buff) |
| 紫 | Purple (debuff) |
| 青 | Blue (special) |
| - | none |

## Deals-damage (Dmg)

| JP | EN |
|---|---|
| ○ | Yes |
| （○） | Yes (conditional) |
| - | no |

## Interruptible

| JP | EN |
|---|---|
| ○ | Yes |
| × | No |
| - | n/a |

## AoE geometry

| JP | EN |
|---|---|
| 敵単体 | single target |
| 単体 | single target |
| 近接単体 | melee single |
| 前方単体 | frontal single |
| 遠隔単体 | ranged single |
| 敵範囲 | area (enemies) |
| 範囲 | area |
| 前方範囲 | frontal cone |
| 後方範囲 | rear cone |
| 前方直線 | frontal line |
| 対象範囲 | targeted area |
| 目視中前方範囲 | frontal gaze cone (while in sight) |
| ドーナツ状範囲 | donut/ring AoE |
| 右側前方範囲 | right-frontal cone |
| 左側前方範囲 | left-frontal cone |
| 範囲+敵単体 | area + single target |
| メインアームに準拠 | per main-hand weapon |
| メインアームのWSを使用（関連 : クラス_アクション/特性/ゴッドセンド） | uses main-hand weaponskill (see class actions / Godsend) |

## Status effects and stat mods (効果)

| JP | EN |
|---|---|
| HP回復 | HP recovery |
| TPをすべて失う | removes all TP |
| アビリティ不可 | Amnesia  [client status] |
| ガード | Guard |
| スタン | Stun  [client status] |
| ステータスエフェクト1～3つの効果（アビリティ不可/WS不可/沈黙） | 1-3 status effects (Amnesia / Pacification / Mute) |
| ステータスエフェクト2つの効果（スロウ/麻痺） | 2 status effects (Slow / Paralysis) |
| ステータスエフェクト3つの効果（スロウ/暗闇/睡眠） | 3 status effects (Slow / Blind / Sleep) |
| ステータスエフェクト4つの効果（バインド/WS不可/アビリティ不可/静寂） | 4 status effects (Bind / Pacification / Amnesia / Silence) |
| スロウ | Slow  [client status] |
| ノックバック | Knockback |
| バインド | Bind  [client status] |
| バーサク | Berserk  [client status] |
| パーフェクトドッジ（物理攻撃を完全に回避する状態。/効果時間1分） | Perfect Dodge (fully evades physical attacks; 1 min) |
| ファストキャスト | Fastcast  [client status] |
| ヘイスト | Haste  [client status] |
| ヘイトリセット | enmity reset |
| ヘヴィ | Heavy  [client status] |
| ミッドナイトウルフ（月の影響下におかれた状態。） | Midnight Wolf (state under the moon's influence) |
| レベルが5の倍数の場合石化 | Petrify if level is a multiple of 5 |
| 中毒 | Poison  [client status] |
| 全ステータス－ | Imperiled  [client status] |
| 合計100ダメージ | 100 damage total |
| 対象の強化エフェクトを1つ削除 | removes one buff from target |
| 引き寄せ | draw-in |
| 弱体ステータスを移す | transfers its debuffs to target |
| 強化ステータスを吸収 | absorbs target's buffs |
| 敵対心リセット | enmity reset |
| 敵視上昇率－ | Sonorous Blast  [client status] |
| 暗闇 | Blind  [client status] |
| 物理命中－ | Accuracy Down  [client status] |
| 物理回避＋ | Evasion Up  [client status] |
| 物理攻撃＋ | Attack Up  [client status] |
| 物理攻撃－ | Attack Down  [client status] |
| 物理防御＋ | Defense Up  [client status] |
| 物理防御－ | Defense Down  [client status] |
| 特技ランク－ | special-move rank down |
| 状態異常回復 | cures status ailments |
| 睡眠 | Sleep  [client status] |
| 石化 | Petrification  [client status] |
| 詠唱妨害無効 | Glossolalia  [client status] |
| 閃光 | Glare  [client status] |
| 静寂 | Silence  [client status] |
| 魔法防御－ | Magic Defense Down  [client status] |
| 麻痺 | Paralysis  [client status] |
| （ガード） | (Guard) |
| （サイズアップ） | (size up) |
| （ターゲット解除） | (target released) |
| （ヒゲに電気が溢れる） | (whiskers surge with electricity) |
| （吸い込み） | (inhale / pull-in) |
| （赤く光る） | (glows red) |
| （髭に雷を蓄える） | (stores lightning in whiskers) |
| ＨＰを回復 | HP recovery |
| ＨＰ吸収 | HP drain |
| ＴＰをすべて失う | removes all TP |
| ＴＰを全て失う | removes all TP |
| ＴＰ吸収 | TP drain |
| ＴＰＤｏＴ | TP Bleed  [client status] |
| ＷＳ不可 | Pacification  [client status] |

## Taxonomy - 門 (gate)

| JP | EN |
|---|---|
| 衆生門 | Sentient Gate |
| 無情門 | Unfeeling Gate |
| 超常門 | Supernatural Gate |
| ？？？ | ??? |

## Taxonomy - 綱 (class)

| JP | EN |
|---|---|
| 百獣綱 | Beasts |
| 草木綱 | Plantlife |
| 水棲綱 | Aquatic |
| 六識綱 | Beastmen |
| 甲鱗綱 | Reptilian |
| 百蟲綱 | Insects |
| 有翼綱 | Winged |
| 死屍綱 | Undead |
| 呪具綱 | Cursed-object |
| 妖異綱 | Aberrant |
| 機関綱 | Mechanical |
| 不明 | unknown |
