# Evidence map - elemen-consumable-effects

Web-table harvest of the eLeMeN - FF14 (`elemen.sakura.ne.jp`) `etc/food`
(食事効果) and `etc/medicine` (薬品効果) sections: the **per-item effect
magnitude specifications** for 1.x food and medicine. Scoped client-first - the
1.23b client ships item names, category, effect duration, and recast time, but
not these percentage/cap effect specs, which are server-side tuning.

Evidence tier: **wiki (CALIBRATION-grade)**. A web table alone justifies a
CALIBRATION-tagged server value, not a retail-confirmed one.

## What the client already ships (dropped or used only to corroborate)

Checked against `xivl-client-data/csv/` before harvesting:

- **Item names + flavor text** - `xtx_itemName.csv` (id col0, JP col5, EN col6).
  Client-primary; used only for the name cross-check below. The client's flavor
  descriptions are qualitative ("restores a few HP", "restores HP") and carry no
  numbers.
- **Effect duration and recast time** - `itemData.csv`, physical field 60
  (duration, seconds) and field 62 (recast, seconds). Confirmed exact against
  the site for recovery potions/ethers, the elixir, and every self-buff (e.g.
  Ether recast 4:00 = 240; 剛力の薬 duration 0:30 = 30, recast 3:40 = 220; all
  food duration 30:00 = 1800, recast 0:05 = 5). Kept in the CSVs
  (`client_recast_s` / `client_duration_s`) as a reproducible cross-check
  alongside the site's own `recast_s` / `duration_s`.
- **Consumable category** - `itemData.csv` field 41 (2002/2003 medicine,
  2004 ether, 2006 self-buff, 2012/2016 food). Redundant with the site's
  section/category grouping.

## What is web-unique (the payload)

None of the following appears in any populated `itemData` column (verified by
dumping fields 33-68 for potions, ethers, elixir, status-cure items, and every
stat-buff tier):

- **Food** (`food-effects.csv`, 108 items): per-item, per-attribute buff spec
  `attribute:+X%(cap Y)`, one to three attributes each, grouped by primary stat.
  Plus the universal food rules the page states in prose (captured verbatim in
  `sources/elemen-consumable-effects/objects/pages/food-effects.md`): every food grants **EXP +3%,
  duration 30:00, recast 0:05**; HQ adds **+10%** to effect and duration; raw
  ingredients (uncooked meat/fish/fruit) grant the EXP bonus only; and the four
  cap-proximity log messages (至福=at cap, ほっぺた=>=90%, おいしく=>=80%, 食べた=below).
- **Medicine** (`medicine-effects.csv`, 66 items): HP/MP recovery `+X%(cap Y)`
  (recovery is % of max HP/MP, not a fixed value - stated in the page prose);
  the status each cure/debuff item applies or removes; self-enhancement stat
  buffs `stat:+X%(cap Y)` with per-tier caps; enmity deltas (熱狂薬 +100,
  沈静薬 -80); Protect/Shell grants (鉄甲薬/亀甲薬); poison-throw debuff durations;
  and phoenix-down raises. Monster-debuff success rate is stated to be
  independent of player stats (magic accuracy etc.).

This is the same server-side tuning class as the level-EXP and quest-EXP gems -
absent from the decoded client, so the web source is the best available evidence.

## Cross-check results

Method per `studies/elemen-bestiary/derived/client-crosscheck.md` (NFKC, JP -> client id + EN).

- **Item names: 174/174 resolved** to `xtx_itemName.csv` (108 food, 66 medicine).
  The 5 `◆◆`-prefixed medicine items resolve once the `◆◆` site display marker is
  stripped (kept verbatim in `item_marker`): 軍用再生薬/軍用蘇生薬 (Company-issue),
  ダスケンドラフト, ハーバルキス, オニキスティア. No blank client ids - every listed
  consumable exists in the 1.23b client.
- **Attribute tokens: 28/28 resolved** to `xtx_text_paramName.csv`; **status
  tokens: 8/8 resolved** to `xtx_status.csv`. Full map in `glossary.md` with ids.
- **Duration/recast cross-validation** (site value vs `itemData` fields 60/62):
  all 108 food and 57 of 66 medicine agree exactly. See the one contradiction
  below.

## Cross-source contradiction (recorded, not resolved)

Nine status-cure medicines (治療薬類 / 状態異常回復) list a **recast of 1:10-1:20**
on the site but the 1.23b client `itemData` carries a **longer recast of
3:00-4:30**:

| item | client EN | site recast | client recast |
|---|---|---|---|
| 目薬 | Eye Drops | 1:10 | 4:30 |
| やまびこ薬 | Echo Drops | 1:10 | 4:00 |
| きつけ薬 | (Sleep cure) | 1:10 | 3:30 |
| 元気薬 | (Paralysis cure) | 1:20 | 4:00 |
| 沈静薬 | (Enmity down) | 1:20 | 4:00 |
| 止血薬 | (Poison cure) | 1:10 | 3:00 |
| 息継ぎ薬 | (Silence+Poison) | 1:20 | 4:00 |
| 強心薬 | (Paralysis+Poison) | 1:20 | 4:00 |
| 金の針 | Gold Needle | 1:20 | 4:00 |

Recovery potions/ethers, the elixir, and all self-buffs match the client exactly;
only the status-cure category diverges, and with no uniform ratio. Per the tier
rule (**packet > video > wiki**, and client-data outranks wiki), the **client
recast is authoritative** for these nine; the site's 1:10-1:20 is the older/lower
value (the effect page appears to predate the 1.23b cure rebalance, consistent
with the site's shopitem section carrying patch-1.22 prices). This flags that
some numeric values on the page may pre-date 1.23b - treat the effect magnitudes
(uncheckable against the client) as CALIBRATION-grade accordingly. Both values are
kept in the CSV so the divergence is visible per row.

## Files

- `food-effects.csv` - 108 food items: group (food type) + category (primary
  stat) + item (JP + client id/EN) + `effect_jp` (verbatim) + `effect_en` (gloss)
  + recast/duration (site + client).
- `medicine-effects.csv` - 66 medicine items, same schema.
- `glossary.md` - every attribute/status token -> client string + id; site fixed
  phrases.
- `sources/elemen-consumable-effects/objects/pages/food-effects.md`, `medicine-effects.md` - verbatim
  transcription incl. the universal-rule page notes.
- cached source HTML preserved in elemen-site-archive:
  `sources/elemen-site-archive/objects/ff14_dated_archives/etc/{food,medicine}/index.html`.

## Gaps and caveats

- `effect_jp` is the authoritative value; `effect_en` is a convenience gloss
  built from `glossary.md` (attribute/status tokens mapped, times normalized).
- Recovery/self-buff duration for medicine: the client stores 0 for pure recovery
  items (no lingering effect); `client_duration_s` shows 0, `duration_s` is blank
  where the site prints no 効果時間.
- HQ variants: the page states the universal +10% HQ rule but lists only NQ
  values; HQ magnitudes are NQ x 1.10 (effect and duration), not transcribed.
- No source patch stamp on either page; names resolve against 1.23b, but the
  recast contradiction shows some values are older. Corroborate any promoted
  value against a pcap or the client before treating it as retail-confirmed.

## Promotion

This repo records the `elemen-consumable-effects` evidence id, this path, and
the verdict above. A consumer project promotes durable tuning on its own side
with an immutable citation to this record.
