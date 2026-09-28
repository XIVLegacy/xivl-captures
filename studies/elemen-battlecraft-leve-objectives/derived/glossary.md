# Glossary - elemen-battlecraft-leve-objectives

This set harvests only the **web-unique slice** of the eLeMeN regional
battlecraft leve pages: the readable objective choreography. Every other column
the source shows (reward, contract period, level band) is client-carried and was
deliberately dropped - see `evidence-map.md` for the client-first reasoning.

## Client cross-check (provenance)

`leve_name_en_client` and `client_leve_id` are AUTHORITATIVE: joined from
`xivl-client-data/csv/xtx_guildleve.csv` on the verbatim JP leve name
(JP col10 -> EN col11, id col0), NFKC-normalized. 177/177 leves resolve to a
client leve id (174 direct; 3 via the audited overrides below). The join both
supplies the official EN name and confirms each eLeMeN leve is a real 1.x client
leve rather than an ARR-era entry. `objective_text` is the site's own content
(verbatim JP) and is the reason this set exists.

### Name-match overrides (site vs client transcription variants)

Three eLeMeN names differ from the client string by a transcription variant; the
`client_leve_id` was assigned by hand and flagged in `name_match_note`:

| eLeMeN name (site) | client id | client EN | variant |
|---|---|---|---|
| 急募！ 「ナットの触覚」の調達 | 13022 | Undercutting the Competition | site 触覚 vs client 触角 (antenna); ｢｣/「」 brackets |
| 駅馬車の積荷：ナットの触覚の調達 | 12222 | Tuning In | site 触覚 vs client 触角 (antenna) |
| 募集：アントリングワーカーの追跡者 | 12225 | Antling Invasion | site drops ・ in アントリング・ワーカー |

The client string is authoritative (触角 = antenna/feeler is correct for the
insect; 触覚 = sense of touch is the site's error).

## Objective notation (`objective_text`)

The site's terse objective shorthand, kept verbatim. Common tokens:

| token | meaning |
|---|---|
| `【 X 1体】` | engage enemy X, one creature (体 = creature counter) |
| `【 X 2体PT】` | engage a party (PT) of X, two members |
| `【 X 1体 Y 1体のPT】` | a mixed party of X and Y |
| `×N` | the engagement repeats N times |
| `倒すと1体追加` / `倒すと同PT追加` | on defeat, one more (or the same party) is added |
| `から Z N個` | from the enemy, obtain N of item Z |
| `当たり探し×N` | "find-the-right-one" lottery, N attempts |
| `当たり` / `ハズレ` | a hit (correct) / a miss (wrong) outcome |
| `が出現` | (an enemy) appears / spawns |
| `逃げ` | an enemy flees |
| `地面の光` | the light on the ground (the objective marker to reach/inspect) |
| `到達巡回地点` | a patrol point to reach |
| `メインクエスト` | the leve gates or overlaps a main-quest step |
| ` / ` | a step separator (collapsed from the source `<br>` / line breaks) |

The enemy and item names inside `objective_text` are the site's JP; cross-
reference them via the `elemen-bestiary` set or `xivl-client-data` if needed
- they are not separately resolved here.

## Columns

- `city` - the issuing city-state (Limsa Lominsa / Gridania / Ul'dah).
- `camp_jp` - the camp/levemete location on the source page (client-derivable
  context; kept for navigability, not part of the web-unique payload).
- `leve_name_jp` - verbatim site JP name.
- `leve_name_en_client` / `client_leve_id` - the client join (see above).
- `objective_text` - the web-unique objective choreography, `<br>`/newlines
  collapsed to ` / `.
- `name_match_note` - non-empty only for the 3 override rows.
