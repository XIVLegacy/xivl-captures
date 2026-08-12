# Evidence map - elemen-level-exp

Transcription of the eLeMeN - FF14 `class/level/` page (データ資料 > クラス >
レベル/経験値): the per-level growth curve (physical-bonus allotment + quest/leve
unlocks + EXP-to-next) and the max-base-EXP-per-kill caps by party size, plus the
link/chain/rest EXP-bonus modifiers. Evidence tier: **wiki** (packet captures >
video breakdown > wiki), so CALIBRATION-grade.

## Client-first finding (the crux for this section)

This section's data is **web-unique server-economy data** - the client does not
ship it in decoded form. Established by searching every `xivl-client-data/csv/
*.csv` for the printed sequences:

- The EXP-to-next curve `570, 700, 880, 1100, 1500, 1800, 2300, 3200, 4300,
  5000, ...` - **no client CSV** contains it as a contiguous run.
- The max-base-EXP-per-kill curve `225, 225, 225, 300, 300, 425, 450, 475,
  500, ...` - **no client CSV** contains it.

The only EXP-named decoded sheet is `exp_BPCost.csv` (29 rows, column types
`s16, s8, s16, s16`). Its 1-29 index and its values
(`15,20,25,...,184` in col0; `1,1,...,4` in col1) do **not** correspond to the
per-level (1-50) EXP curve, the physical-bonus point curve (`5..45`), or the
physical-bonus max curve (`3..23`) on this page; its meaning is a separate,
unresolved sub-system. So unlike the `elemen-*-actions` sets - where every action
name is a client string and the harvest only adds observation fields - here the
**entire payload is web-only**. That is precisely why this harvest exists: the
1.x EXP economy (level thresholds, per-kill caps, link/chain/rest bonuses) is
server-side and absent from the shipped client sheets.

No client name-join applies (there are no game-string names on this page - only
numbers plus the site's own annotation markers). See `glossary.md`.

## Best tables (unique value)

- `derived/level-growth.csv` - 50 rows, one per class level 1-50:
  - `exp_to_next_level` / `next_level` - the EXP threshold to advance (570 at L1
    -> 110000 at L50->51). The core level-gating curve.
  - `physical_bonus_point` / `physical_bonus_max_per_attribute` - the attribute-
    point allotment on level-up (final 1.x system; physical *level* removed in
    1.19). `-` below L10; point = `level-5` from L10, max steps 3->23 (+1 / 2
    levels). The `最大値` cell is `rowspan="2"` on the source (two equal levels
    merged); expanded per-level here.
  - `quest_main_jp` / `quest_class_jp` / `leve_regional_jp` / `leve_local_jp` -
    site annotations (新規追加 / 発生 / 追加 / -) for when new quests/leves of
    each type open at that level. Verbatim JP; glossed in `glossary.md`.
- `derived/max-exp-per-kill.csv` - 86 value rows (long form: level, party_size
  1-8, max_base_exp, estimated). The per-level cap on base EXP from one kill,
  before bonuses. Sparse on the source (solo mostly filled L1-40; larger parties
  partial); **22 values are estimated** (源 faint text 薄字 = 推測値, or the one
  literal `582?` at L35 / party_size 4) and carry `estimated=yes`. Blank source
  cells produce no row.
- `derived/exp-bonuses.csv` - 10 rows: the link (+25/50/75/100%), chain
  (+20..50%, with shrinking valid-time window), and rest (+50%) EXP multipliers
  applied on top of the base cap.

## Source note (edition)

The page describes the **final 1.x** state: it explicitly records that physical
level was removed in patch 1.19 and that 修錬値->経験値 / ランク->レベル were
renamed at the same time. This is the 1.23b economy, not ARR (2.0).

## Gaps / caveats

- Every value is the site's observed/estimated figure at world-down. Wiki tier,
  so CALIBRATION-grade until corroborated by packet evidence or a server-formula
  decode. The 22 `estimated=yes` cells in `max-exp-per-kill.csv` are the site's
  own guesses (薄字) - weakest of all.
- `max-exp-per-kill.csv` is intentionally sparse: only the party-size/level cells
  the source actually printed are present. Missing (level, party_size) pairs are
  simply not on the source, not zero.
- The physical-bonus point/max linear patterns are noted for internal-consistency
  only; the CSV holds the verbatim per-level values, not a formula.
- `icon`-style image columns do not exist on this page. No unreadable cells; no
  `GAP` marks were needed.

## Verdict

Confirmed as a faithful transcription of the source page (values verbatim,
`rowspan` expanded, estimated cells flagged, `582?` kept as printed). Client-first
check run and recorded: the EXP/growth curves are **not** in the decoded client
data, so the harvest is justified web-unique evidence. No claim promoted to
retail-confirmed.
