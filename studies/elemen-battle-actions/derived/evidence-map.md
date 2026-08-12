# Evidence map - elemen-battle-actions

Transcription of the eLeMeN - FF14 class/action (Disciplines of War/Magic) and
class/battle (付加効果を持つ戦術) pages. Evidence tier: wiki (packet captures >
video breakdown > wiki), so CALIBRATION-grade. This map names the best tables,
records the client-vs-site EN cross-check outcome, and lists every id
disambiguation the join required - none silently resolved.

## Scope (what was harvested)

The 7 battle classes' final-1.x action tables plus the shared battle-tactics
page:

- `class/action/~patch2.00_{Gladiator,Pugilist,Marauder,Lancer,Archer,Conjurer,Thaumaturge}.html`
- `class/battle/index.html` (部位損傷 map + バトルレジメン combos)
- `class/action/index.html` (job/action equip rules; reference only, not
  normalized)

`~patch2.00` is the site's forward-facing label; the content is the final 1.x
state at the 2012-11-11 world-down (per the site's own note - "各ページは全ワー
ルドダウンした時点での最終データ"), i.e. patch 1.23b. The older `~patch1.20` /
`~patch1.22` snapshots and the crafter/gatherer (Disciples of the Hand/Land)
action pages are outside this set; see the README.

## Best tables (unique value)

- `derived/battle-actions.csv` - 226 rows (one per class action / job action /
  trait). The observation-only payload the client's numeric sheets do NOT carry
  in usable form: **level learned, TP cost, cast time, recast time, effect
  duration, equip-condition**. `command.csv` (the 1.23b numeric action sheet) is
  sparse here - e.g. Fast Blade (id 27150) carries only recast=10 and a few
  bool flags; TP/cast/duration/level are absent. That is the harvest's reason to
  exist.
- `derived/part-damage-map.csv` - 15 rows: which weaponskill damages which body
  part (頭/腕/脚/特殊部位) per melee class. This is the shared player-WS
  part-damage reference that the `elemen-bestiary` set deliberately did NOT
  transcribe (it appeared identically on every monster page); its home is here.
- `derived/tactics-battle-regimen.csv` - 6 rows: the Battle Regimen
  additional-effect combos (通常攻撃->魔法 lowers resistance, etc.) with trigger
  pattern and worked example.

## Client cross-check (xivl-client-data)

Every EN in this set is the client string, not an authored gloss. Action /
trait / part-damage names join `xivl-client-data/csv/xtx_command.csv` on the
verbatim JP (JP col2 -> EN col3, id col0), NFKC-normalized. Result: **226/226
actions and 15/15 part-damage WS resolve to a client EN; zero authored `(?)`
names.** These are player actions the client fully ships, so the value of the
check is that it caught the names a naive romaji gloss gets wrong, e.g.:

- インビンシブル -> **Hallowed Ground** (id 27148), not "Invincible".
- 正拳 -> **Heavy Strike** (id 22102), not "Straight Punch".
- カウンター系 / native-JP names -> the official EN, not a literal reading.

### Client-id disambiguation (never first-wins)

The 1.x player class-action command ids live in the `>=27000` range, laid out
sequentially by class - canonical order by median id:
**Pugilist < Gladiator < Marauder < Archer < Lancer < Thaumaturge < Conjurer**.
A trait or action name shared across K classes has K distinct client ids (each
class its own copy, often with a slightly different EN). Picking the first row
by file order would mis-assign them, so each shared name's classes are sorted
into canonical order and zipped to the sorted candidate ids. This matters for
the generic stat traits, which the client names per class:

| trait (JP) | Pugilist | Marauder | Lancer |
|---|---|---|---|
| 物理攻撃力アップI | Enhanced Physical Attack (27127) | Enhanced Physical Attack Power (27210) | Enhanced Physical Attack Power (27288) |

`client_command_id` in the CSV is the single authoritative class-action id
chosen this way.

### Differing-EN twins (client carries two rows for one JP)

Where the client has a second row for the same JP with a **different** EN, the
class-action-block id was chosen and the twin is recorded here (not silently
dropped). All are player-facing 1.x actions; the twin is a duplicate/variant
client row.

Within the `>=27000` block:

| class | action (JP) | chosen (class action) | client twin |
|---|---|---|---|
| Lancer | 竜槍 | Power Surge (27261) | Speed Surge (27586) |
| Lancer | ドゥームスパイク | Doom Spike (27271) | Doomspike (27710) |

A `<27000` row with a different EN also exists for four names (the chosen
class-action id is the `>=27000` one):

| class | action (JP) | chosen (class action) | client also has |
|---|---|---|---|
| Marauder | シュトルムヴィント | Path of the Storm (27196) | Storm's Path (26995) |
| Lancer | ディセムボウル | Disembowel (27272) | Dragon's Grasp (23495) |
| Lancer | リングオブタロン | Ring of Talons (27277) | Ring of Thorns (23496) |
| Lancer | ドラゴンダイブ | Dragonfire Dive (27268) | Wyvern Dive (23494) |

42 further names have a same-EN duplicate client row (e.g. Aegis Boon
27141/27942, and the caster spells' 28xxx/29xxx twins such as Fire 27310/28932)
- harmless, the class-action-block id was kept, not enumerated per-row.

### Battle Regimen effects (`tactics-battle-regimen.csv`)

The 効果 column names are combo-bonus effect phrases (物理耐性の緩和,
詠唱速度ダウン＆消費ＭＰアップ, ...), not entries in `xtx_status.csv`; they are
glossed descriptively and flagged `(?)` only where no client string applies. The
worked-example weaponskill names all resolve in `xtx_command.csv` (Light Slash
22103, Heavy Strike 22102, Phantom Dart 22302, Red Lotus 26792, Brandish 26979,
Blizzard 27308, Scourge 28592, Puncture 27512) - the examples are kept verbatim
in `example_jp`.

## Gaps / caveats

- `icon` column (an image per action on the site) is not transcribed.
- The combo-tree tables are transcribed as the name+connector structure only;
  each action's combo condition/bonus is preserved verbatim in its
  `description_jp` (コンボ条件 / ボーナス) and in the client `xtx_command` EN
  description, so no combo data is lost.
- Descriptions (`description_jp`) are the site's; the client ships the
  authoritative JP+EN description for each action - reach it via
  `client_command_id` in `xtx_command.csv` rather than trusting the site prose.
- Level / TP / cast / recast / duration are the site's observed values at
  world-down; wiki tier, so CALIBRATION-grade until corroborated by a decode of
  `command.csv` or packet evidence.
- No unreadable cells; no `GAP` marks were needed.

## Verdict

Confirmed as a faithful transcription of the source pages (values verbatim,
`<br>` preserved in raw, collapsed in CSV). No claim promoted to
retail-confirmed. No authored EN names - every EN is a client string, with the
id disambiguation documented above rather than resolved by first-wins.
