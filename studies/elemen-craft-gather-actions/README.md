# eLeMeN FF14 1.x Crafter and Gatherer Actions - Web Tables

Web-table transcription of the 1.x non-combat class actions from eLeMeN - FF14
(`elemen.sakura.ne.jp`), "データ資料 > クラス" section: the eight Disciples of
the Hand (crafter) and three Disciples of the Land (gatherer) action pages
(`class/action/~patch2.00_*`). Sibling to `elemen-battle-actions` (the seven
Disciplines of War/Magic). The same pipeline and cross-check apply.

## Study contents

- 11 class detail pages (Carpenter/木工, Blacksmith/鍛冶, Armorer/板金,
  Goldsmith/彫金, Leatherworker/革細工, Weaver/裁縫, Alchemist/練成,
  Culinarian/調理, Miner/採掘, Botanist/園芸, Fisher/漁釣) transcribed verbatim
  into `sources/elemen-craft-gather-actions/objects/pages/*.md`, source HTML preserved in the `elemen-site-archive` set.
- `derived/craft-gather-actions.csv` - 167 rows (120 distinct names), JP columns
  verbatim with interleaved `*_en`: discipline (hand/land), class, section,
  name (JP + client EN), `client_command_id`, level, TP, cast, recast, duration,
  equip-condition, description.
- `derived/evidence-map.md` - cross-check outcome. `derived/glossary.md` - EN
  gloss maps.

Each page has an **アクション** section (general equippable actions - Throw,
sling, non-combat utility) and a **ゴッドセンド** section (the crafting /
gathering abilities: Hasty Hand, Grandmastery, Sharp Vision, ...).

### Client-first tiering

Check `xivl-client-data` FIRST. The client ships the ability **names and
descriptions** (`xtx_command.csv`) - primary evidence there, and every EN here
is joined from that sheet, not authored (167/167 resolve. The DoH/DoL abilities
are the client's `29xxx` command rows). This set's web-unique value is the
**level learned**, the **equip-condition grouping** (which discipline/class each
ability belongs to), and the アクション metadata (TP/cast/recast/duration).
ゴッドセンド rows carry no TP/cast on the source page.

Evidence tier: **wiki** (packet captures > video breakdown > wiki) -
CALIBRATION-grade until corroborated by a `command.csv` decode or packet
evidence.

## Start here

- `derived/evidence-map.md` - the client cross-check and caveats.
- `derived/craft-gather-actions.csv`.
- `derived/glossary.md` - EN gloss maps and column units.
- `manifest.yaml` `sources` list - per-page URLs and retrieval date.

## Source material

- `sources/elemen-craft-gather-actions/objects/pages/<Class>.md` - per-class アクション + ゴッドセンド tables,
  verbatim (`<br>` markers preserved).
- Source HTML - preserved verbatim in the `elemen-site-archive` set; see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping.

## Promoted conclusions

`derived/craft-gather-actions.csv` supplies client-command-keyed action metadata
to downstream Disciples of the Hand and Land implementation work. The
observation-only values remain CALIBRATION-grade.

## Source note (edition)

`~patch2.00` is the site's forward-facing label. The content is the final 1.x
state at the 2012-11-11 world-down (patch 1.23b) per the site's own header, not
ARR (2.0).

## Topics

- 8 Disciples of the Hand + 3 Disciples of the Land; 167 rows (92 ゴッドセンド
  abilities + 75 アクション).
- Crafting abilities: Byregot's, Tender Touch, Hasty Hand, Grandmastery, ...
- Gathering abilities: Sharp Vision, Earthen Favor, the deity Wards, ...

## Evidence gaps

- The `~patch1.20` / `~patch1.22` historical snapshots and `class/level/`
  (level/exp growth) are not included.
- `icon` (per-ability image) not transcribed.
- ゴッドセンド rows have no TP/cast/recast/duration on the source page (crafting
  resource/success detail is in the description prose only).
- No unreadable cells. No `GAP` marks were needed.

## Further research

- EN columns are already cross-checked against the 1.23b client. The matrix, join
  gotchas, and method are in
  `studies/elemen-bestiary/derived/client-crosscheck.md`.
- Level values remain uncorroborated against a decode of `command.csv` and are
  not retail-confirmed.
