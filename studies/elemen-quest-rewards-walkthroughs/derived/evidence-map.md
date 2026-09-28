# Evidence map - elemen-quest-rewards-walkthroughs

The web-unique slices of the eLeMeN quest section: the quest **EXP reward
amounts** and the per-quest **walkthroughs** (with reward patch-history). A
client-first recon of the whole section found the rest redundant with the client;
these two are what clear the bar. Evidence tier: **wiki** (packet captures >
video breakdown > wiki), so CALIBRATION-grade.

## Client-first scoping (what was dropped and why)

The quest section was recon'd client-first. The client ships almost
all of it as primary evidence, so those fields were **dropped**:

| field the source shows | client source (primary) | kept? |
|---|---|---|
| quest name + full dialogue/script | `xtx_quest.csv` (1.9 MB, 735 quests) | join key only |
| NPC + coords | `quest_marker.csv` (867 KB) | dropped |
| gil + item rewards | `quest_new_reward.csv` (verified present) | dropped |
| completion text | `xtx_questCompleteText.csv` | dropped |
| in-game journal text | `xtx_quest.csv` | dropped from walkthroughs |
| **quest EXP reward amount** | **not in usable client form** | **KEPT** |
| **walkthrough step order / choices** | **not in usable client form** | **KEPT** |
| **reward patch-history notes** | **not in the client** | **KEPT** |

### Why the EXP reward is web-unique

Joining 262 eLeMeN quests to their client `quest_new_reward.csv` reward row: the
**gil** amount is present in the client (e.g. 45000 for ある始まり, 10000 for
気合がっつり), but the **EXP** amount is absent in **202 of 242 cases (~83%)**
(e.g. 気合がっつり: gil 10000 present, exp 1120 absent). The 1.x quest EXP economy
is server-side, the same pattern the `elemen-level-exp` set found for the level
curve. The site's `経験値：～N` (the `～` = "up to", level-scaled) is observed
CALIBRATION-grade data.

### Why the walkthroughs are web-unique

The client ships the quest *script* (dialogue/journal) but not a readable
solution: the step order, the exact `選択肢「...」を選ぶ` choices, and the
prerequisite chain are eLeMeN's synthesis. The **reward patch-history**
annotations (`（パッチ1.20で報酬に経験値が追加）`, `（パッチ1.20で報酬から
「...ギルドトークン」×2000が削除）`) are version-history the client never carried -
genuinely additive. The journal text itself was dropped (client-primary).

## Scope

- EXP rewards: all 5 categories from the index pages - **281 quests** (main 19,
  sub 100, grand-company 69, class 51, job 42).
- Walkthroughs: the detail pages that exist - **112 quests** (main 19, class 51,
  job 42). Sub and Grand Company quests have no detail/walkthrough pages on the
  source (reward table only).

## Best tables (unique value)

- `derived/quest-exp-rewards.csv` - 281 rows; the EXP reward per quest (258 carry
  a value; main-story openers and some quests list none). Joined to client ids.
- `derived/quest-walkthroughs.csv` - 112 rows; prereq chain, step order, reward
  patch-history, prev/next quest links, per quest.

## Client cross-check

Every quest name joins `xtx_quest.csv` (JP col2 -> EN col3, id col0),
whitespace-insensitive NFKC. **281/281 reward rows and 112/112 walkthrough rows
resolve to a client quest id** - most directly; a handful via audited variant
overrides (kanji/kana typos 努め/務め, 頼り/便り, 卵/タマゴ; and ` new!` / spacing
suffixes). Listed in `glossary.md`. The join confirms all are real 1.x quests
and supplies official EN names.

## Gaps / caveats

- `exp_reward` and `walkthrough_steps` are the site's observations, wiki tier ->
  CALIBRATION-grade. Corroborate a specific EXP value or step against packet/
  client evidence before treating it as retail-confirmed. Note the `～`
  (up-to/level-scaled) nature of the EXP figure.
- The in-game journal text and NPC/coord/gil/item data were deliberately dropped
  (client-primary). Reach them via `client_quest_id` in `xtx_quest.csv` /
  `quest_marker.csv` / `quest_new_reward.csv`.
- Sub and Grand Company quests have EXP rewards here but no walkthroughs (none on
  the source).
- Reward patch-history is the site's annotation (patch dates are provenance, not
  a claim about current behavior).

## Verdict

Confirmed as a faithful transcription of the web-unique quest fields, every quest
joined to its client id (281/281 rewards, 112/112 walkthroughs). Client-primary
fields dropped by design. No claim promoted to retail-confirmed.
