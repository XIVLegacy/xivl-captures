# Glossary - elemen-level-exp

Unlike the `elemen-*-actions` sets, this is a **numeric growth-curve** harvest,
not a name-resolution one. There are no JP game-string names to join against the
client - the only non-numeric cells are the site's own annotation markers and
the party-size column labels, neither of which is a client string. So there is
no `*_en` client-join layer here; the maps below are authored glosses of the
site's UI labels, and the client-first tiering is covered in `evidence-map.md`.

## Annotation markers (quest / leve columns in `level-growth.csv`)

These flag when a new quest or guildleve of that type first becomes available at
that class level. They are the site's own annotations, kept verbatim in the
`*_jp` columns.

| JP | gloss |
|---|---|
| 新規追加 | newly added (a new quest/leve of this type opens at this level) |
| 発生 | occurs / becomes triggerable |
| 追加 | added (a further one of this type opens) |
| - | none at this level |

## Physical bonus columns (`level-growth.csv`)

`フィジカルボーナス` (physical bonus) is the attribute-point allotment the class
grants on level-up in the final 1.x system (physical *level* itself was removed
in patch 1.19; see the intro prose in the raw page).

- `physical_bonus_point` - points available to allot at this level. `-` for
  levels 1-9; from level 10 it is `level - 5` (5 at L10 rising +1/level to 45 at
  L50). Verbatim from the source; the linear pattern is noted only as an
  internal-consistency check, not a re-derivation.
- `physical_bonus_max_per_attribute` - the cap on a single attribute. Source
  tooltip: `ひとつのパラメータに振る事のできる最大値` ("the maximum that can be
  allotted to a single parameter"). `-` for L1-9; from L10 it is 3, rising +1
  every two levels to 23 at L50. On the source this cell uses `rowspan="2"` to
  merge the two equal levels; it is expanded here so each level row carries the
  value.

## EXP columns

- `exp_to_next_level` (`level-growth.csv`) - EXP required to advance from this
  level to the next (source cell e.g. `570経験値（2まで）` = 570 EXP until L2).
- `next_level` - the target level parsed from the `（Nまで）` suffix.
- `max_base_exp` (`max-exp-per-kill.csv`) - the per-level cap on base EXP from a
  single kill, before link / chain / rest bonuses (source: 最大値以内の経験値に
  各種ボーナスを足した数値が最終的な取得経験値, floored). `party_size` is the
  1人 / 2人PT ... 8人PT column (1-8). Long/tidy form: only cells printed on the
  source appear; a blank source cell yields no row.
- `estimated` - `yes` where the source rendered the value in faint text
  (薄字 = 推測値, estimated) or appended a literal `?` (the single `582?` at
  L35 party_size 4). `no` otherwise.

## EXP bonus modifiers (`exp-bonuses.csv`)

The link / chain / rest multipliers added on top of `max_base_exp`
(`exp_bonus_percent` is the `+N%`). `chain_window_seconds` is the chain's
valid-time window (有効時間); it shortens as the chain grows. Blank = n/a.
