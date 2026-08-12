# eLeMeN -> client cross-check

eLeMeN (`elemen.sakura.ne.jp`) is a fan data site: its English names and glosses
are the site's own, and its Japanese cells are transcribed verbatim. Every EN
value we attach is cross-checked against `xivl-client-data/csv/`, the 1.23b
client's own strings, before it is trusted. This note records the check matrix
and the pitfalls found while digesting the `elemen-bestiary` set. The method
also applies to other eLeMeN sections (equipment, class/action, quest, leve,
area); the client sheets differ per topic, but the failure modes are the same.

The client-table claims below use decoded extraction 2012.09.19.0001, the
stable identity of the client-data CSV tree:

    xivl-client-data:csv/ (extraction 2012.09.19.0001)

CSV filenames below are relative to that tree.

## Rule of thumb

Do NOT ship hand-authored English (romaji reconstructions, literal kanji glosses,
"standard vocabulary" guesses). They read plausibly and are wrong often enough to
matter. Grep the client CSVs for the verbatim JP token first; author a gloss only
where no client string exists, and flag it `(?)`.

## Check matrix (bestiary set)

| eLeMeN field | client table (`xivl-client-data/csv/`) | join key -> value |
|---|---|---|
| monster special-move name (特殊技 名称) | `xtx_command.csv` | JP col2 -> EN col3; id col0 (`client_command_id`) |
| status effect (効果 tokens) | `xtx_status.csv` | JP col2 -> EN **col4**; id col0 |
| NM proper name / actor name | `xtx_displayName.csv` | JP col1 -> EN col2; id col0 (`client_actor_id`) |
| genus / race (属, race-level) | `xtx_monsterRace.csv` | EN col2 (JP codenames differ, join semantically) |
| species / individual mob | `xtx_displayName.csv` | JP col1 -> EN col2 (a family; see below) |
| NM magic spell list (in the range cell) | `xtx_command.csv` | same as special-move |
| player class action / job action / trait (class/action) | `xtx_command.csv` | JP col2 -> EN col3; id col0 (see per-class gotcha) |
| part-damage weaponskill (class/battle 部位損傷) | `xtx_command.csv` | same as class action |

`actorclass.csv` holds NO names (numeric only) - names live in `xtx_displayName`.
`xtx_text_skillName.csv` is only the 84 class/discipline names, NOT mob abilities.
Player actions AND traits both live in `xtx_command.csv` (not a separate traits
sheet); `command.csv` (numeric) is sparse - it carries recast + flags but not
TP/cast/duration/level, so those observation fields are a web-harvest, not a
client join.

## Join gotchas (all bit us at least once)

- **NFKC width.** The site mixes full/half-width (`ＷＳ不可` vs `WS不可`, `ＴＰ`
  vs `TP`). The client uses one form. Normalize both sides with
  `unicodedata.normalize("NFKC", s)` before matching, or you miss real hits
  (e.g. WS不可 = Pacification).
- **A species is a FAMILY, not one actor.** `xtx_displayName` has many named
  field mobs per species (ラット -> Rat, Wharf Rat, Pack Rat, Plague Rat). Never
  first-wins-pick one; report the generic (exact bare-form match) plus the full
  variant list + ids. First-wins by file order is biased toward the low-id
  "story/tutorial" actors (Bad Basilisk 3000001, Bad Dodo 3000002, Da Bomb
  3000008, Ogre Bastard 3000042) - those are family members, not the generic.
- **Client stores lowercase base forms.** `xtx_displayName` EN is lowercase
  ("great buffalo"); render in-game title case with minor words lowercased
  (of/the/and/o'...), even inside hyphens: `Guardian of the Grove`,
  `Old Six-Arms`, `Will-o'-the-wisp`.
- **`[en]` placeholders.** Some rows carry a literal `[en]` (untranslated) EN -
  treat as GAP, not a name (e.g. Chimera, some Golem rows).
- **Same-named variants share one EN, many ids.** Keep every id (`;`-joined) so
  the cross-reference is complete.
- **JP crossovers.** The client JP can be misleading: race row 1022 サラマンダー =
  **Drake**, while サンショウウオ (row 1013) = Salamander. Verify by EN + creature,
  not by matching the JP string.
- **Debuffs named after their move.** A status EN can be the move name
  (敵視上昇率－ = "Sonorous Blast", the Buffalo move that applies it). That is the
  authoritative client string even though it looks odd.
- **Player class actions: per-class ids, never first-wins.** A trait/action name
  shared across K classes (e.g. 物理攻撃力アップI in Pugilist/Marauder/Lancer) has
  K distinct client ids, each often with a slightly different EN (Enhanced
  Physical Attack vs Enhanced Physical Attack Power). Class-action ids are the
  `>=27000` range, laid out sequentially per class (median-id order in 1.23b:
  Pugilist < Gladiator < Marauder < Archer < Lancer < Thaumaturge < Conjurer).
  Assign by sorting the sharing classes into that order and zipping to the sorted
  candidate ids - first-wins by file order mis-assigns them. The same JP can also
  have a `<27000` twin with a different EN (シュトルムヴィント: class action 27196
  "Path of the Storm" vs 26995 "Storm's Path"); pick the `>=27000` class-action
  id and log the twin. Worked in the `elemen-battle-actions` set.

## What the checks caught (evidence the method is worth the time)

- Skill names: my katakana reconstructions were wrong for e.g. カビ散布 (=Violent
  Sneeze, not "Mold Scatter"), 三竦み (=Ranine Glare), 猪突猛進 (=Reckless Charge),
  サフ (=Sough), エンシェントラス (=Ancient Wrath), ファウルステンチ (=Fowl Stench),
  プレーンクラッカー (=Plaincracker), ヘッドバット (=Head Butt). 187/195 resolved.
- Status effects: アビリティ不可 = Amnesia, WS不可 = Pacification, 沈黙 = Mute,
  全ステータス－ = Imperiled, 詠唱妨害無効 = Glossolalia, 閃光 = Glare, ＴＰＤｏＴ =
  TP Bleed, ファストキャスト = Fastcast - all wrong or non-canonical in my first
  gloss pass.
- NM names: the site's anchor romaji was mis-spaced (Guardianofthegrove,
  Princeof Pestilence); the client fixed them.
- Genus race mappings (`xtx_monsterRace`) were clean by contrast - 48/50 exact,
  2 intentional simplifications later made verbatim (Wolf/Hyena/Hellhound,
  Golem (1.2)).

## Method

1. Build a `{JP: (id, EN)}` map from the relevant client CSV (skip `-`, `****`,
   `[en]`, empty EN).
2. For every distinct site token, look up under NFKC. Use the client EN; record
   the id column for cross-reference.
3. Where a token resolves to many actors (species), emit generic + variants, not
   one pick.
4. Only where nothing resolves, author a gloss and suffix `(?)`; list those
   explicitly in the set's `evidence-map.md`.
5. Keep the JP column verbatim beside every `*_en` column; the client id columns
   make the join reproducible.
