# Glossary - elemen-quest-rewards-walkthroughs

Two derived tables from the eLeMeN quest section, both scoped to the web-unique
slices (see `evidence-map.md` for the client-first reasoning):

- `quest-exp-rewards.csv` - the quest **EXP reward amounts** (server-side; ~83%
  absent from the client reward sheets).
- `quest-walkthroughs.csv` - the per-quest **walkthroughs** (Main/Class/Job
  detail pages): step order, prereq chain, and reward patch-history.

## Client cross-check (provenance)

`quest_name_en_client` and `client_quest_id` are AUTHORITATIVE: joined from
`xivl-client-data/csv/xtx_quest.csv` on the JP quest name (JP col2 -> EN col3,
id col0), whitespace-insensitive NFKC. **All 281 reward rows and all 112
walkthrough rows resolve to a client quest id.** The join supplies the official
EN name and confirms each quest is a 1.x client quest rather than an ARR entry.
`exp_reward` and `walkthrough_steps` are the site's own content and are the
reason this set exists.

### Name-match overrides (site vs client transcription variants)

`name_match_note` is non-empty where the eLeMeN name differs from the client
string. Two classes:

- **site suffix/space variant** - a trailing ` new!` marker or a space before a
  `（city）` suffix; the base name matches the client exactly after whitespace
  normalization. 5 reward rows (e.g. おわりの名は希望 new!, 紅月下の闘い new!).
- **site char-variant vs client** - a kanji/kana transcription difference; the
  client string is authoritative:

  | eLeMeN (site) | client id | client EN | variant |
  |---|---|---|---|
  | 木霊が努め | 110260 | Dendrological Duties | 努め vs client 務め |
  | 覚悟の頼り | 111604 | The Mail Must Get Through | 頼り vs client 便り |
  | 賢者の卵 奪還大作戦（x3 cities） | 110790 / 110795 / 110805 | The Dreamer's Dilemma | 卵 vs client タマゴ |

  (The per-city Grand Company / sub quests like 勝利への行進（city） matched the
  client directly - the client stores each city variant as its own quest id.)

## quest-exp-rewards.csv columns

- `category` - main / sub / grand-company / class / job.
- `group` - the source section: starting city (main), city/company (sub, GC), or
  class/job (class, job). Client-derivable context, kept for navigability.
- `quest_name_jp` - verbatim site JP name.
- `quest_name_en_client` / `client_quest_id` - the client join.
- `recommended_level` - the first `レベルN` in the site's condition column
  (the site's recommended level; the client stores class/level gates separately).
- `exp_reward` - the web-unique payload: the base EXP reward (site `経験値：～N`,
  the `～` = "up to", level-scaled). Blank where the quest lists no EXP reward.
- `exp_class` - the class the EXP is credited to, when the site specifies one
  (job quests: `経験値（幻術）：～N` -> `幻術`); blank otherwise.
- `name_match_note` - see above.

## quest-walkthroughs.csv columns

- `category` / `group` / names / `client_quest_id` - as above (Main/Class/Job
  only; Sub and GC have no detail pages on the source).
- `prereq` - the 条件 (unlock conditions): class/level gate + prerequisite quests.
- `exp_reward` - repeated from the detail page's 報酬 for convenience.
- `prev_quest` / `next_quest` - the 前の/次のクエスト chain links (quest names).
- `reward_patch_notes` - the site's 報酬 patch-history annotations
  (`（パッチ1.20で報酬に経験値が追加）` etc.) - web-unique version history of how
  a quest's rewards changed across 1.x patches.
- `walkthrough_steps` - the site's step-by-step instructions, ` / `-joined,
  `### <zone>` marking area sub-headings. **The in-game journal text** (the
  client's own quest script, shown collapsible on the source) **is dropped** - it
  is client-primary in `xtx_quest.csv`; only eLeMeN's walkthrough instructions
  are kept.
- `name_match_note` - see above.

## Notation inside steps / objectives

NPC names, `（zone X: n, Y: m）` coordinates, and `選択肢「...」を選ぶ` (choose
option) reflect the site's walkthrough. Zones/NPCs are client-derivable
(quest_marker.csv); the value here is the readable step order and choices.
