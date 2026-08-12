# Evidence map - elemen-bestiary

Transcription of the eLeMeN - FF14 bestiary and NM pages. Evidence tier: wiki
(packet captures > video breakdown > wiki), so CALIBRATION-grade. This map names
the best tables, records every discrepancy marker the site itself flags, and
lists the JP->EN name gaps - none of these are silently resolved in the CSVs.

## Best tables (unique value)

- `derived/mob-skill-list.csv` - 320 special-move rows (194 regular genus + 126
  NM). Cast-effect color, AoE range, deals-damage, interruptible, and status
  effect per move. This is the payload the client sheets do not carry.
- `derived/bestiary-taxonomy.csv` - 65 genus rows: crystal drop-priority order
  by element and the site's inferred weakness/resistance attributes.
- `derived/mob-drops.csv` - 84 NM item-drop rows (the 35 NMs that drop items),
  and `derived/nm-spawns.csv` - 39 NM spawn rows (one per NM: zone, coords, spawn
  condition, patch). Both distilled from the 5 `NM_<Region>.md` pages; the raw
  per-NM metadata still lives verbatim there.

## Discrepancy markers (never silently resolved)

### 網 vs 綱 (global, from the bestiary index)

The site states the class rank is rendered in-game as 網 (net) but is 綱 (class)
in the official setting, and it classifies by the official setting (verbatim):

> ゲーム内では綱（こう）ではなく網と記載されていますが、公式設定上では綱（こう）が正しいようです。
> 当サイトでは、公式設定上のデータに順じてモンスターの分類をしています。

So every 綱 value in this set is the official-setting label, which may differ
from the in-game 網 label. Do not treat the 綱 column as the in-game string.

### Per-page ※ (in-game vs official-setting class differs)

The site flags these genera with `※`; the in-game class differs from the
official-setting class it files them under. Verbatim notes (also carried in the
`class_ingame_note` column of `bestiary-taxonomy.csv`):

| genus | site ※ note (verbatim) |
|---|---|
| ビートル / Beetle | ※ファイアフライは『（＋有翼綱）』。 |
| ナット / Gnat | ※ゲーム内では『妖異綱 （＋有翼綱）』ですが公式設定上は『百蟲綱』となっています。 |
| アプカル / Apkallu | ※ゲーム内では綱は不明ですが公式設定上は『有翼綱』となっています。 |
| ドードー / Dodo | ※ゲーム内では綱は不明ですが公式設定上は『有翼綱』となっています。 |
| ヒッポグリフ / Hippogryph | ※ゲーム内では『百獣綱』ですが公式設定上は『有翼綱』となっています。 |
| プーク / Puk | ※ゲーム内では『甲鱗綱』ですが公式設定上は『有翼綱』となっています。 |
| ウィル・オ・ザ・ウィスプ / Will-o'-the-Wisp | ※ゲーム内では『百蟲綱 （＋有翼綱）』ですが公式設定上は『妖異綱』となっています。 |
| エレメンタル / Elemental | ※ゲーム内では『有翼綱』ですが公式設定上は『妖異綱』となっています。 |
| プラズモイド / Plasmoid | ※ゲーム内では『百蟲綱 （＋有翼綱）』ですが公式設定上は『妖異綱』となっています。 |
| ボム / Bomb | ※ゲーム内では『呪具綱 （＋有翼綱）』ですが公式設定上は『妖異綱』となっています。 |

## JP -> EN name mapping (xivl-client-data)

`genus_en_client` in `bestiary-taxonomy.csv` maps each genus katakana to the
client EN name in `xivl-client-data/csv/xtx_monsterRace.csv`. Mapped values
that carry a client-side spelling or label difference (kept, not corrected):

| genus (site) | client EN | note |
|---|---|---|
| アルドゴート / Aldgoat | Aldgoats | client pluralizes (row 1023) |
| ウルフ / Wolf | Wolf/Hyena/Hellhound | client's exact combined race label (row 1014) |
| クァール / Coeurl | Couerl | client misspelling (row 1032) |
| アマルジャ / Amalj'aa | Amlaj'aa | client misspelling (row 1065) |
| イクサル / Ixali | Ixal | site Ixali vs client Ixal (row 1064) |
| カクター / Cactuar | Sabotender | client genus is Sabotender (row 1009); site labels genus Cactuar |
| フライングトラップ / Flying Trap | Flytrap | client Flytrap (row 1027) |
| スウォーム / Sworm | Swarm | client Swarm (row 1053); site romaji Sworm |
| ドレーク / Drake | Drake | client JP for Drake is サラマンダー (row 1022) |
| サラマンダー / Salamander | Salamander | client row 1013; NB client row 1022 サラマンダー maps to Drake - JP crossover |
| ゴーレム / Golem | Golem (1.2) | client's exact string incl. its "(1.2)" version tag (row 1089) |

### Client-EN GAPs (15, marked GAP in the race table, not guessed)

`genus_en_client` in `bestiary-taxonomy.csv` is keyed to the client *race* table
`xtx_monsterRace.csv`; GAP there means that table has no row for the genus - a
true fact at race granularity, kept as-is. These same creatures do exist as
individual mobs in the client *actor* table `xtx_displayName.csv`, resolved in
`derived/species-client-map.csv` (112 species; 106 present in the actor table, 6
absent).

Important: a site species (種) does NOT map one-to-one to a client actor. The
client ships a whole FAMILY of named field mobs per species (e.g. ラット / Rat
-> Rat, Wharf Rat, Pack Rat, Plague Rat), so the map gives `client_generic_name`
(the actor whose EN exactly matches the site species - the bare form, where the
client ships one) plus `client_variant_count` and the full `client_variants`
list with ids. Where the client has no bare form, `client_generic_name` is empty
and the note points to the variants (e.g. ゾンビー / Zombie -> Rotting Corpse,
Zombie Mage, Zombie Pikeman; no plain "Zombie" actor). The low-id "story" actors
(Bad Basilisk 3000001, Bad Dodo 3000002, Da Bomb 3000008, Ogre Bastard 3000042)
are members of their families, not the generic - the generic is the plain form
(Basilisk / Dodo / Bomb / Ogre). Of the 15 race-table-GAP genera, only
ムーンマウス, ヴァンガード, サイクロプス are absent from the actor table too, and
キマイラ's actor row is an untranslated `[en]` placeholder.

Per-genus race-table notes (unchanged):

- ムーンマウス / Moon Mouse - no client row.
- モール / Mole - no Mole genus; species Hedgemole = client row 1057.
- ローデント / Rodent - no Rodent genus; species Rat = client row 1040.
- オロボン / Orobon - no Orobon genus; species Angler = client row 1045.
- メガロクラブ / Megalocrab - client has generic Crab (rows 1011/1076) only.
- 人 / Human - player/imperial race; not in xtx_monsterRace.
- ビートル / Beetle - no Beetle genus; species Weevil = 1039, Firefly = 1058.
- ダイアマイト / Diremite - no client row.
- ドードー / Dodo - no Dodo genus; species Cockatrice = client row 1020.
- ザ・ダムド / The Damned - no genus row; species Zombie = client row 1018.
- ウィル・オ・ザ・ウィスプ / Will-o'-the-Wisp - client row 1100 has JP codename only.
- プラズモイド / Plasmoid - no client row.
- ヴァンガード / Vanguard - uncertain: client Juggernaut (1024) or Killer Machine (1090).
- キマイラ / Chimera - client row 1087 has JP codename only.
- サイクロプス / Cyclops - client row 1107 has JP name only, no EN.

### NM names

NM proper names (`scope_en` where `is_nm=y`) are client-authoritative: the
actor display-name from `xivl-client-data/csv/xtx_displayName.csv`, with
`client_actor_id` for cross-reference. All 36 NMs with a skill table (and all 39
in the raw pages) resolve there - the names are NOT in `actorclass.csv` (numeric
only) but in the display-name string table. The client stores a lowercase base
form, shown here in in-game title case (minor words lowercased). This replaced
the initial site-anchor romaji and corrected 3 badly-spaced names:
Guardianofthegrove -> Guardian of the Grove, Princeof Pestilence -> Prince of
Pestilence, Old Six-arms -> Old Six-Arms.

## NM drops and spawns (mob-drops.csv, nm-spawns.csv)

Only the 5 NM region pages carry item-drop and spawn data - the 65 regular
bestiary pages carry taxonomy + special moves only (no `アイテム`, no `生息域`).
So both CSVs are sourced entirely from `NM_<Region>.md`; counts by page are in
`derived/file-inventory.csv` (`nm_drop_rows` / `nm_spawn_rows`).

- **Spawns** (`nm-spawns.csv`, 39 rows = one per NM): `zone_jp` + coords +
  `spawn_condition_jp` are verbatim from the `生息域` / `出現条件` cells;
  `habitat_raw` keeps the full original cell so nothing is lost when the coords
  are split out. `zone_en_client` joins `xtx_placeName.csv` (JP col1 -> EN col2,
  id in `zone_client_place_id`) - **all zones resolved** (regions + the dungeon
  sublocations Nanawa Mines, Cassiopeia Hollow, Shposhae, U'Ghamaro Mines, The
  Mun-Tuy Cellars). No coordinates are invented; where the source gives none
  (Guardian of the Grove: bare `黒衣森`) the coord fields are empty.
- **Drops** (`mob-drops.csv`, 84 rows): `item_jp` verbatim; `item_en_client` +
  `item_client_id` join `xtx_itemName.csv` (JP col5 -> EN col6, id col0) on the
  exact JP string - **84/84 resolved**. Because the join is by exact JP, a
  client string that looks nothing like the katakana is still authoritative
  (セストソル = Fists of the Sixth Sun; プレプレ = Kple Kple). `rarity_mark` keeps
  the site's ◆ / ◆◆ drop-tier glyphs; `drop_group` preserves which items shared a
  source line (a trailing `/` before `<br>` is a visual line-wrap and is merged
  into one group). Dye/quality variants ([BK]/[RD]/DX) matched the client's
  dyed-variant row (Velveteen Tights (Black), etc.). Two `note` cells carry the
  site's own drop-relocation provenance (`パッチ1.18でNM...のドロップから変更`),
  kept verbatim.
- **NM proper names** (both CSVs, `nm_en_client` + `nm_client_actor_id`): the
  client display-name from `xtx_displayName.csv`, rendered in in-game title case
  (client stores a lowercase base form; `client_actor_id` makes the raw join
  reproducible). All 39 NM JP names resolved to exactly one actor. This corrected
  the site's mis-spaced romaji, e.g. Guardianofthegrove -> Guardian of the Grove,
  OldSix-arms -> Old Six-Arms, PrinceofPestilence -> Prince of Pestilence,
  ThirdOrderPatriarchZuGa -> Third Order Patriarch Zu Ga.
- **Monster family** (`monster_family_en_client`): reused verbatim from
  `bestiary-taxonomy.csv` `genus_en_client`. The 3 NM families whose genus is
  race-table-GAP (メガロクラブ / Megalocrab, ドードー / Dodo, オロボン / Orobon)
  carry `GAP` here too - consistent with the taxonomy set, not a new gap.

## Cross-source notes

- Weakness vs crystal drop: the `weakness_attr_inferred` / `resistance_attr_inferred`
  columns are the site's own 推測 (inferred-from-enemy-attribute) values and can
  point to a different element than the genus's crystal drop order. This is the
  site's own framing (inference), not a measured contradiction; both are recorded
  as printed.
- Some genera (クァール, グゥーブー, モルボル, オーガ, and the ？？？門/不明 group:
  ヴァンガード, ガーゴイル, キマイラ, ゴーレム, サイクロプス, トレント) print no
  crystal drop-priority; those cells are left blank, matching the source.
- Elemental and Flan print `※属性による` (varies by element) for weakness; kept
  verbatim in `remarks`.

## English layer (provenance)

Both CSVs carry interleaved `*_en` columns (JP kept verbatim). Elements, cast
colors, damage/interrupt flags, AoE geometry, and taxonomy labels are the
standard FFXIV mechanics vocabulary (authored glosses; taxonomy 門/綱 labels are
the site's own coined terms, glossed descriptively - no client equivalent).

`status_effect_en` (the 効果 column) is client-authoritative: the official status
name from `xivl-client-data/csv/xtx_status.csv` (col 4), matched on the JP
token under NFKC (so full/half-width WS不可, ＴＰ etc. join). This corrected a
batch of authored glosses that were wrong or non-canonical: アビリティ不可 =
**Amnesia** (not "ability disabled"), WS不可 = **Pacification**, 沈黙 = **Mute**
(not Silence; 静寂 = Silence), 全ステータス－ = **Imperiled**, 詠唱妨害無効 =
**Glossolalia**, 閃光 = **Glare** (not Flash), ＴＰＤｏＴ = **TP Bleed**,
ファストキャスト = **Fastcast**, and the stat-mods (物理攻撃＋ = Attack Up, etc.).
敵視上昇率－ = **Sonorous Blast** (the debuff is named after the Buffalo move that
applies it). Non-status tokens (Knockback, HP drain, enmity reset, flavor
parentheticals) keep an authored gloss. NM range-cell spell lists resolve against
`xtx_command.csv` (Absorb ACC/ATK/EVA, Siphon TP, Scourge II, Shadowsear...).

`skill_name_en` is client-authoritative: the official 1.x EN action name from
`xivl-client-data/csv/xtx_command.csv` (the 1.23b localized command sheet),
joined on the JP name, with `client_command_id` carrying the matching command
id(s). 187 of 195 distinct skill names resolve there (same-named variants share
one EN and list every id). This corrects an earlier draft of this set that
claimed the 1.x client carried no EN mob-ability strings - it does; they live in
`xtx_command.csv` alongside the player commands, not in `xtx_text_skillName.csv`
(which is only the 84 class/discipline names). The client strings also caught
several bad reconstructions in that draft - e.g. カビ散布 = Violent Sneeze (not
"Mold Scatter"), 三竦み = Ranine Glare, 猪突猛進 = Reckless Charge, サフ = Sough,
エンシェントラス = Ancient Wrath.

The 8 names not in the client are the descriptive placeholders (normal / ranged
attack, magic) plus 3 genuinely absent names left as `(?)`-flagged
reconstructions: Eye of the Beholder, Flying Mareen, Fated Gaze. NM range-cell
spell lists resolve against the same sheet where present. Full maps in
`derived/glossary.md`.

## Verdict

Confirmed as faithful transcription of the source pages (values verbatim,
`<br>` line breaks preserved in raw, collapsed in CSV). No claim is promoted to
retail-confirmed. Contradicted claims: none introduced - the site's own
discrepancy markers are surfaced above, not resolved.
