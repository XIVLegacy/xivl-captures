# eLeMeN FF14 1.x Regional Battlecraft Leve Objectives - Web Tables

The web-unique slice of the eLeMeN - FF14 (`elemen.sakura.ne.jp`) regional
battlecraft guildleve pages: the readable **objective choreography** per leve
(wave structure, spawns, flee/add behavior, lottery and item-gated mechanics),
joined to the client leve id. A client-first comparison of the whole guildleve
section found everything else redundant with the client. This is the one part
that clears the bar.

## Study contents

- The 3 regional battlecraft city pages transcribed verbatim into
  `sources/elemen-battlecraft-leve-objectives/objects/pages/*.md` (name / reward / period / objective, grouped by
  camp), with the source HTML preserved in the `elemen-site-archive` set.
- `derived/battlecraft-leve-objectives.csv` - 177 rows (59 per city): `city`,
  `camp_jp`, `leve_name_jp`, `leve_name_en_client`, `client_leve_id`,
  `objective_text`, `name_match_note`. The `objective_text` is the payload.
- `derived/evidence-map.md` - the client-first scoping and cross-check.
  `derived/glossary.md` - the objective-notation legend and the client join.

### Client-first tiering (why this study is narrow)

Check `xivl-client-data` FIRST. The client ships the leve **names +
descriptions** (`xtx_guildleve.csv`, 623 leves) and the objective **parameters +
rewards + period** (`guildleve.csv`: counts, mob/item ids, contract time) as
primary evidence - so those columns were **dropped**, not transcribed. What the
client does NOT carry in usable form is the **readable runtime choreography** of
each battle leve (the wave/spawn/mechanic narrative), which is this study's only
content. The site carries no reward gil/exp amounts and no star ratings, so there
is no second web-unique slice to harvest.

Evidence tier: **wiki** (packet captures > video breakdown > wiki) -
CALIBRATION-grade until corroborated by `guildleve.csv` params or packet/video
evidence.

## Start here

- `derived/evidence-map.md` - client-first scoping, the 177/177 client join, the
  3 name-variant overrides.
- `derived/battlecraft-leve-objectives.csv`.
- `derived/glossary.md` - objective notation + the client cross-check.
- `manifest.yaml` `sources` list - per-page URLs and retrieval date.

## Source material

- `sources/elemen-battlecraft-leve-objectives/objects/pages/<City>_BattlecraftLeves.md` - per-camp leve tables
  verbatim (name / reward / period / objective; JS `document.write` flavor text
  on the name dropped, `<br>` preserved in the objective).
- Source HTML - preserved verbatim in the `elemen-site-archive` set; see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping.

## Promoted conclusions

`derived/battlecraft-leve-objectives.csv` was evaluated for a downstream
consumer and deliberately not imported because its leve coverage was superseded
there. The
catalog retains the client-keyed choreography as CALIBRATION evidence.

## Source note (edition)

`~patch2.00`-era eLeMeN data = the final 1.x state at the 2012-11-11 world-down
(patch 1.23b), not ARR. Confirmed here by the 177/177 join to the 1.x client
`xtx_guildleve` leve table.

## Topics

- 177 regional battlecraft leves (59 each: Limsa Lominsa, Gridania, Ul'dah),
  grouped by camp.
- Objective choreography: wave counts, `倒すと追加` (defeat-then-add) spawns,
  `逃げ` (flee) behavior, `当たり探し` (find-the-right-one) lottery, item-gated
  triggers, `地面の光` objective markers.
- Each leve carries its client `client_leve_id` for join-back to
  `xtx_guildleve.csv` / `guildleve.csv`.

## Evidence gaps

- Regional **fieldcraft** and **local** tradecraft leves are out of scope - their
  gather/synth objectives lack the battle choreography that motivates this study,
  and are client-carried.
- Reward amounts, exp, star scaling, and contract period are NOT here (absent
  from the source or client-primary and dropped).
- Enemy/item names inside `objective_text` are the site's JP, not separately
  resolved to the client (cross-reference via `elemen-bestiary`).

## Further research

- Enemy names in `objective_text` can be cross-referenced against
  `elemen-bestiary` and `xivl-client-data`.
- Wave details remain uncorroborated against `guildleve.csv` numeric params or
  packet/video evidence and are not retail-confirmed.
