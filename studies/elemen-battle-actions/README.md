# eLeMeN FF14 1.x Battle Class Actions - Web Tables

Web-table transcription of the 1.x class actions from eLeMeN - FF14
(`elemen.sakura.ne.jp`), "データ資料 > クラス" section: the seven Disciplines of
War/Magic action pages (`class/action/~patch2.00_*`) plus the shared
class/battle tactics page (`class/battle/`, 付加効果を持つ戦術). It holds per
action the level learned, TP cost, cast/recast time, effect duration, and
equip-condition, plus the part-damage weaponskill map and the Battle Regimen
combo effects.

## Study contents

- 7 class detail pages (Gladiator/剣術, Pugilist/闘術, Marauder/斧術,
  Lancer/槍術, Archer/弓術, Conjurer/幻術, Thaumaturge/呪術) transcribed verbatim
  into `sources/elemen-battle-actions/objects/pages/*.md`, with the source HTML preserved in the
  `elemen-site-archive` set. Also `_battle_tactics.md` (class/battle) and
  `_action_index.md` (the section's job/action equip rules, reference only).
- Three normalized derived CSVs, JP columns verbatim with interleaved `*_en`:
  - `derived/battle-actions.csv` - 226 rows, one per action / job action / trait:
    class, section, name (JP + client EN), `client_command_id`, level, TP,
    cast, recast, duration, equip-condition, and the site description.
  - `derived/part-damage-map.csv` - 15 rows: class x body-part -> weaponskill
    (JP + client EN + id). This is the shared player-WS part-damage reference
    for cross-study comparison.
  - `derived/tactics-battle-regimen.csv` - 6 rows: Battle Regimen
    additional-effect combos (effect, trigger pattern, worked example).
- `derived/evidence-map.md` - cross-check outcome, client-id disambiguation, and
  the differing-EN twins. `derived/glossary.md` - the EN gloss maps.

### Client-first tiering

Check `xivl-client-data` FIRST. The client ships the action **names and
descriptions** (`xtx_command.csv`, JP+EN+DE+FR) - those are primary evidence
there, and every EN in this study is joined from that sheet, not authored. The
numeric action sheet (`command.csv`) is **sparse**: it carries recast + some
flags but not TP cost, cast time, effect duration, or level-learned. Those are
this study's unique value - the observation-only fields, harvested from the web
because the client does not carry them in usable form.

Evidence tier: **wiki** (packet captures > video breakdown > wiki). A value here
alone justifies a CALIBRATION-tagged server value, not a retail-confirmed one -
corroborate level/TP/cast/recast against a decode of `command.csv` or packet
evidence before treating them as retail-confirmed.

## Start here

- `derived/evidence-map.md` - the client cross-check, the per-class id
  assignment rule, and the differing-EN twins. Read before trusting any cell.
- `derived/battle-actions.csv`, `derived/part-damage-map.csv`,
  `derived/tactics-battle-regimen.csv`.
- `derived/glossary.md` - EN gloss maps and column units.
- `manifest.yaml` `sources` list - per-page URLs and retrieval date.

## Source material

- `sources/elemen-battle-actions/objects/pages/<Class>.md` - per-class combo tree + job actions +
  actions + traits tables, verbatim (`<br>` markers preserved).
- `sources/elemen-battle-actions/objects/pages/_battle_tactics.md` - 部位損傷 map + バトルレジメン combos.
- `sources/elemen-battle-actions/objects/pages/_action_index.md` - job/action equip rules (reference).
- Source HTML - preserved verbatim in the `elemen-site-archive` set; see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping.

## Promoted conclusions

`derived/battle-actions.csv` supplies client-command-keyed level, TP, cast,
recast, duration, and equip-condition data to downstream combat planning.
`derived/part-damage-map.csv` and `derived/tactics-battle-regimen.csv` are the
named inputs for downstream part-damage and Battle Regimen systems.

## Source note (edition)

`~patch2.00` is the site's forward-facing label. The content is the final 1.x
state at the 2012-11-11 world-down, per the site's own header (各ページは全ワー
ルドダウンした時点での最終データ), i.e. patch 1.23b - confirmed by the 1.x-only
class/job system, TP economy, and the removed 盾術 class. It is not ARR (2.0)
data.

## Topics

- 7 Disciplines of War/Magic: Gladiator, Pugilist, Marauder, Lancer, Archer,
  Conjurer, Thaumaturge; 226 actions (114 アクション + 77 特性 + 35 job actions).
- Per-action fields: level, TP, cast, recast, duration, equip-condition.
- Part-damage map: 5 melee classes x 7 body parts.
- Battle Regimen: 6 combo-bonus effects.

## Evidence gaps

- Crafter/gatherer (Disciples of the Hand/Land) action pages, the `~patch1.20`
  and `~patch1.22` historical snapshots (incl. the removed 盾術/Sentinel class),
  and `class/level/` (level/exp growth) are not included.
- `icon` (per-action image) not transcribed; `攻撃特性`-style extra columns do
  not exist on these pages.
- Combo-tree tables are transcribed as name+connector structure. The per-action
  combo condition/bonus is preserved verbatim in `description_jp`.
- No unreadable cells. No `GAP` marks were needed.

## Further research

- All EN columns are already cross-checked against the 1.23b client. The matrix,
  join gotchas, and method are in
  `studies/elemen-bestiary/derived/client-crosscheck.md`.
- The observation-only fields (level/TP/cast/recast/duration) remain
  uncorroborated against a decode of `command.csv` and are not retail-confirmed.
