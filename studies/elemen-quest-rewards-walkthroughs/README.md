# eLeMeN FF14 1.x Quest EXP Rewards and Walkthroughs - Web Tables

The web-unique slices of the eLeMeN - FF14 (`elemen.sakura.ne.jp`) quest section
are the quest **EXP reward amounts** (server-side and largely absent from the
client) and the per-quest **walkthroughs** (step order, prereq chain, reward
patch-history). A client-first recon found the rest of the section redundant with
`xivl-client-data`; these are the parts that clear the bar.

## Study contents

- `derived/quest-exp-rewards.csv` - 281 quests across all 5 categories (main,
  sub, grand-company, class, job): `category`, `group`, name (JP + client EN),
  `client_quest_id`, `recommended_level`, `exp_reward`, `exp_class`. The
  `exp_reward` is the payload.
- `derived/quest-walkthroughs.csv` - 112 quests with detail pages (main 19, class
  51, job 42): `prereq`, `exp_reward`, `prev_quest`, `next_quest`,
  `reward_patch_notes`, `walkthrough_steps`, joined to `client_quest_id`.
- `sources/elemen-quest-rewards-walkthroughs/objects/pages/quest-rewards.md` - the 5 index reward tables verbatim.
  `sources/elemen-quest-rewards-walkthroughs/objects/pages/walkthroughs-{main,class,job}.md` - the walkthroughs
  verbatim (in-game journal text dropped; see below).
- `derived/evidence-map.md` - client-first scoping + cross-check.
  `derived/glossary.md` - columns, notation, and the client join.

### Client-first tiering (why these two slices)

Check `xivl-client-data` FIRST. The client ships quest **names + full dialogue/
script** (`xtx_quest.csv`, 1.9 MB), **NPC + coords** (`quest_marker.csv`), and
**gil + item rewards** (`quest_new_reward.csv`) as primary evidence - all dropped
here. What the client does NOT carry in usable form:

- **Quest EXP reward amounts** - joining 262 quests to their client reward row,
  the gil is present but the EXP is absent in ~83% of cases (e.g. 気合がっつり:
  gil 10000 present, exp 1120 absent). The 1.x quest EXP economy is server-side,
  the same finding as `elemen-level-exp`.
- **Walkthroughs** - the readable step order, choice selections, and prereq chain
  (the client has the script, not a solution), plus the **reward patch-history**
  annotations the client never carried. The in-game journal text is client-
  primary (`xtx_quest`) and was dropped from the walkthroughs.

Evidence tier: **wiki** (packet captures > video breakdown > wiki) -
CALIBRATION-grade until corroborated by packet/client evidence. Note the EXP
figure is `～N` (up-to / level-scaled).

## Start here

- `derived/evidence-map.md` - client-first scoping, the 281/281 + 112/112 client
  join, the variant overrides.
- `derived/quest-exp-rewards.csv`, `derived/quest-walkthroughs.csv`.
- `derived/glossary.md` - columns, notation, cross-check.
- `manifest.yaml` `sources` list - per-category URLs and retrieval date.

## Source material

- `sources/elemen-quest-rewards-walkthroughs/objects/pages/quest-rewards.md` - the 5 index reward tables verbatim
  (name / condition / reward).
- `sources/elemen-quest-rewards-walkthroughs/objects/pages/walkthroughs-<cat>.md` - per-quest walkthroughs verbatim
  (prereq, reward patch notes, chain, steps; journal text dropped).
- Source HTML - preserved verbatim in the `elemen-site-archive` set; see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping.

## Promoted conclusions

Downstream reference work consumes the walkthrough and EXP-reward tables, while
downstream planning uses the client-keyed reward table as the quest-EXP
calibration anchor.

## Source note (edition)

`~patch2.00`-era eLeMeN = the final 1.x state at the 2012-11-11 world-down (patch
1.23b), not ARR - confirmed by the 281/281 join to the 1.x client quest table.
The reward patch-history notes reference 1.x patches (e.g. patch 1.20).

## Topics

- 281 quests' EXP rewards (main/sub/GC/class/job); the server-side quest EXP
  economy (`経験値：～N`).
- 112 quest walkthroughs (main/class/job): prereq chains, step order, choice
  selections, quest linkage, reward patch-history.
- Every quest carries its `client_quest_id` for join-back to `xtx_quest.csv` /
  `quest_new_reward.csv` / `quest_marker.csv`.

## Evidence gaps

- Sub and Grand Company quests have EXP rewards but no walkthroughs (none on the
  source).
- EXP amounts and steps are the site's observation, wiki tier -> CALIBRATION.
- Client-primary fields (names/dialogue, NPC/coords, gil/item rewards, journal
  text) are deliberately NOT here - reach them via `client_quest_id`.
- content_kind is `side-quest` as the umbrella. The study spans all five quest
  categories (see the `category` column and tags).

## Further research

- Specific EXP rewards and walkthrough steps need packet/client corroboration
  before retail confirmation.
