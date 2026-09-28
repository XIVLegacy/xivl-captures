# eLeMeN FF14 1.x Bestiary and NM - Web Tables

Web-table transcription of the 1.x bestiary from eLeMeN - FF14
(`elemen.sakura.ne.jp`), "データ資料 > モンスター" section: the monster list
(`monster/bestiary/`) and the notorious-monster list (`monster/nm/`). It holds
taxonomy (類/綱/属/種), per-genus crystal drop-priority by element, and the
per-monster special-move (特殊技) tables, including all 39 NMs.

## Study contents

- 65 genus/monster detail pages + 5 NM region pages + the two index pages,
  each transcribed verbatim into `sources/elemen-bestiary/objects/pages/*.md`, with the source
  HTML preserved in the `elemen-site-archive` set.
- Two normalized derived CSVs, each with the source JP columns kept verbatim
  and an interleaved English `*_en` column beside each:
  - `derived/bestiary-taxonomy.csv` - one row per genus (65): gate/class,
    genus (JP + site EN + client EN), species list, crystal drop-priority
    order, and the site's inferred weakness/resistance attributes.
  - `derived/mob-skill-list.csv` - one row per special move (320: 194 regular +
    126 NM): cast-effect color, AoE range, attack property, deals-damage,
    interruptible, status effect, remarks.
- `derived/species-client-map.csv` - every species (112) mapped to the client
  actor table `xivl-client-data/csv/xtx_displayName.csv` (106 present). A site
  species maps to a whole family of client field mobs, so this gives the generic
  name (the bare-form actor, where one exists) plus the full variant list + ids -
  it recovers mob-granularity client names for the 15 genera that are GAP in the
  race table, without asserting a single arbitrary pick.
- `derived/glossary.md` - the English gloss maps and their provenance.

### English layer

Both CSVs carry `*_en` columns so the data is usable without reading Japanese
(full detail in `derived/glossary.md`):

- **`skill_name_en` is client-authoritative** - the official 1.x EN action name
  from `xivl-client-data/csv/xtx_command.csv`, joined on the JP name, with a
  `client_command_id` column carrying the matching command id(s) for a direct
  cross-reference into the client action tables. 187 of 195 distinct skill names
  resolve there. The 8 that do not are the descriptive placeholders (normal /
  ranged attack, magic) plus 3 names genuinely absent from the client, left as a
  `(?)`-flagged reconstruction (Eye of the Beholder, Flying Mareen, Fated Gaze).
- **Mechanics vocabulary is authoritative** - elements, cast colors,
  damage/interrupt flags, AoE geometry, status effects, and taxonomy labels are
  the standard FFXIV vocabulary with unambiguous official-EN equivalents. NM
  range-cell spell lists are resolved against the same client sheet.
- **NM names are client-authoritative** - `scope_en` for NM rows is the client
  actor name from `xivl-client-data/csv/xtx_displayName.csv` (all 36 resolve),
  with `client_actor_id` for cross-reference. The client stores a lowercase base
  form. It is shown here in in-game title case (minor words lowercased).

Evidence tier: **wiki** (packet captures > video breakdown > wiki). Raw monster
stats defer to `xivl-client-data` (higher tier). This set's unique value is
the observation-only fields the client sheets do not carry: crystal
drop-priority order, cast-effect colors, ranged-attack usage per genus, and the
NM special-move tables. A value here alone justifies a CALIBRATION-tagged server
value, not a retail-confirmed one.

## Start here

- `derived/evidence-map.md` - best tables, the 網-vs-綱 note, every `※`
  in-game-vs-official-setting class difference, and the JP->EN name GAPs. Read
  this before trusting any single cell.
- `derived/bestiary-taxonomy.csv` and `derived/mob-skill-list.csv`.
- `derived/glossary.md` - the EN gloss maps and their provenance tiers.
- `manifest.yaml` `sources` list - per-page URLs and retrieval date.

## Source material

- `sources/elemen-bestiary/objects/pages/<Genus>.md` - per-genus taxonomy + 特殊技 table.
- `sources/elemen-bestiary/objects/pages/NM_<Region>.md` - all NMs in a region (type, habitat,
  spawn condition, unique item, implementation date, 特殊技 table).
- `sources/elemen-bestiary/objects/pages/_bestiary_index.md`, `_nm_index.md` - the master grouped
  index tables.
- Source HTML - preserved verbatim in the `elemen-site-archive` set; see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping.

## Promoted conclusions

`derived/species-client-map.csv` is the actor-class reconciliation input used by
downstream consumers. Its mob skills, NM drops, and NM spawns also feed
enemy-behavior planning and monster reference pages.

## Source legend (verbatim, do not re-translate)

Taxonomy ranks, in order: **類（るい） / 綱（こう） / 属（ぞく） / 種（しゅ）**.

The index's own taxonomy note (verbatim):

> モンスターは、類（るい）、綱（こう）、属（ぞく）、種（しゅ）の順に分類されています。
> ゲーム内では綱（こう）ではなく網と記載されていますが、公式設定上では綱（こう）が正しいようです。
> 当サイトでは、公式設定上のデータに順じてモンスターの分類をしています。
> ゲーム内のデータと公式設定上のデータが異なる一部モンスターには ※ マークを付け、各ページで注釈を加えています。

Ranged-attack note (verbatim):

> 遠隔攻撃はNMと一部モンスターのみ使用します。同じ属のモンスターでもモンスター名称によって使用の有無が異なります。

Special-move column legend, 特殊技データの見方 (verbatim):

> 色 … ゲーム内での詠唱エフェクトの色（ダメージ系は赤、強化系は黄、弱体系は紫、特殊系は青、一部複合色などの例外有）
> 範囲 … 特殊技の効果範囲。敵の横や後ろに回り込んで回避可能な場合は備考に追記
> 攻撃特性 … 特殊技に付与されている攻撃特性
> ダメージ（Dmg） … 技でダメージを受けるかどうか
> 中断 … 詠唱の中断可否（一部の特殊技は発動に詠唱が必要で、詠唱時に攻撃を当てると一定確率で詠唱中断可能）
> 効果 … 特殊技に付与されている特殊効果

Field meanings (English gloss of the legend, for orientation only): 色 =
cast-effect color, 範囲 = AoE range, 攻撃特性 = attack property, ダメージ (Dmg)
= deals damage y/n, 中断 = interruptible, 効果 = status effect. Cast-color
convention per the legend: 赤 damage / 黄 buff / 紫 debuff / 青 special, with
compound colors (e.g. `赤<br>+<br>（黄）`) as documented exceptions.

## Topics

- Taxonomy: 4 門 (衆生門 / 無情門 / 超常門 / ？？？) over 12 綱; 65 genera.
- Crystal drop-priority: element order per genus (e.g. `土 > 炎 > 氷`).
- 特殊技: cast color, AoE range, damage/interrupt/effect per move.
- NMs: 39 across ラノシア / クルザス / 黒衣森 / ザナラーン / モードゥナ, with
  unique-item drops and per-NM implementation dates.

## Evidence gaps

- `攻撃特性` (attack property) is defined in the site legend but is not
  populated in any transcribed table. The CSV column is retained but empty.
- 15 genera are `GAP` in `genus_en_client` because the client *race* table
  `xtx_monsterRace.csv` has no matching genus row (a true fact at race
  granularity, left as-is). Their member mobs do resolve in the *actor* table -
  `derived/species-client-map.csv` recovers 22 of the 26 species under those
  genera. Only Moon Mouse, Vanguard, Cyclops are truly absent, and Chimera's
  actor row is an untranslated `[en]` placeholder.
- Weakness/resistance are the site's own inferred values (敵属性から推測される),
  not measured. Treat as low-confidence.
- The `部位損傷` (part-damage) field on each detail page is a shared
  player-weaponskill reference (identical across pages, a class/action topic),
  not per-monster data. It was deliberately not transcribed.

## Further research

- All EN columns are already cross-checked against the 1.23b client. The table
  matrix, join gotchas, and method are in
  `studies/elemen-bestiary/derived/client-crosscheck.md`.
- Crystal drop-priority order remains uncorroborated against packet or observation
  evidence and is not a retail-confirmed drop table.
