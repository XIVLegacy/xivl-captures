# eLeMeN FF14 1.x Level / EXP Growth - Web Tables

Web-table transcription of the 1.x level / EXP growth data from eLeMeN - FF14
(`elemen.sakura.ne.jp`), "データ資料 > クラス > レベル/経験値"
(`class/level/index.html`). It holds the per-level growth curve (physical-bonus
attribute allotment, quest/leve unlock markers, and the EXP-to-next threshold),
the max-base-EXP-per-kill caps by party size, and the link/chain/rest EXP-bonus
modifiers. Sibling to `elemen-battle-actions` / `elemen-craft-gather-actions`.
Same pipeline, but this one is a numeric growth set with no client name join.

## Study contents

- One source page transcribed verbatim into `sources/elemen-level-exp/objects/pages/level-exp.md`
  (both HTML tables + the intro and bonus-rule prose), with the captured source
  HTML preserved in the `elemen-site-archive` set.
- Three normalized derived CSVs:
  - `derived/level-growth.csv` - 50 rows, one per class level 1-50: physical-
    bonus point + max-per-attribute, the four quest/leve unlock markers (verbatim
    JP), and `exp_to_next_level` / `next_level`.
  - `derived/max-exp-per-kill.csv` - 86 value rows (long form: level, party_size
    1-8, max_base_exp, estimated). The per-kill base-EXP cap; sparse on the
    source, with 22 estimated (faint-text) values flagged.
  - `derived/exp-bonuses.csv` - 10 rows: the link / chain / rest EXP multipliers.
- `derived/evidence-map.md` - the client-first finding and caveats.
  `derived/glossary.md` - the marker glosses and column definitions.

### Client-first tiering (the crux)

Check `xivl-client-data` FIRST. Result: **this data is web-unique**. The
EXP-to-next curve (`570, 700, 880, ...`) and the max-EXP-per-kill curve (`225,
225, 225, 300, ...`) appear in **no** decoded client CSV. The only EXP-named
sheet, `exp_BPCost.csv` (29 rows), is an unrelated sub-system whose index and
values do not match any curve here. So the 1.x EXP economy is server-side and
absent from the shipped client - the reason this harvest exists. Details and the
search method are in `derived/evidence-map.md`.

Evidence tier: **wiki** (packet captures > video breakdown > wiki), so
CALIBRATION-grade. A value here alone justifies a CALIBRATION-tagged server value,
not a retail-confirmed one - corroborate against packet evidence or a server-
formula decode first. The 22 `estimated=yes` cells are the site's own guesses.

## Start here

- `derived/evidence-map.md` - the client-first finding, best tables, caveats.
- `derived/level-growth.csv`, `derived/max-exp-per-kill.csv`,
  `derived/exp-bonuses.csv`.
- `derived/glossary.md` - marker glosses and column units.
- `manifest.yaml` `sources` list - source URL and retrieval date.

## Source material

- `sources/elemen-level-exp/objects/pages/level-exp.md` - both source tables + the intro and
  bonus-rule prose, verbatim (`rowspan` expanded, estimated cells marked
  `[推測]`, the literal `582?` kept).
- Source HTML - preserved verbatim in the `elemen-site-archive` set; see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping.

## Promoted conclusions

The level-growth and EXP-bonus tables are inputs to downstream character-growth
and EXP-chain planning. They also support level and experience reference pages.
The curves remain CALIBRATION-grade.

## Source note (edition)

The page describes the **final 1.x** state: it records that physical level was
removed in patch 1.19 and that 修錬値->経験値 / ランク->レベル were renamed then.
This is the 1.23b economy at the 2012-11-11 world-down, not ARR (2.0).

## Topics

- Per-level EXP-to-next curve (L1->2 = 570 ... L50->51 = 110000).
- Physical-bonus attribute allotment: point (`level-5` from L10) and max-per-
  attribute (3->23).
- Max base EXP per kill by level x party size (sparse; 22 estimated).
- Link (+25..100%), chain (+20..50%, shrinking window), rest (+50%) EXP bonuses.

## Evidence gaps

- The EXP curves are web-only observations at world-down. No client corroboration
  exists (see the client-first finding). CALIBRATION-grade.
- `max-exp-per-kill.csv` is sparse - only cells printed on the source are
  present. Missing (level, party_size) pairs are not zero.
- The `~patch1.20` / `~patch1.22` historical snapshots and the remaining eLeMeN
  sections (equipment, quests, guildleves, areas) are not included.
- No unreadable cells; no `GAP` marks were needed.

## Further research

- This set adds no `studies/elemen-bestiary/derived/client-crosscheck.md` join cases
  because no client name join applies. Its contribution is the client-first
  *absence* result recorded in `derived/evidence-map.md`.
- EXP thresholds and per-kill caps remain uncorroborated against packet evidence
  or a server EXP-formula decode and are not retail-confirmed.
