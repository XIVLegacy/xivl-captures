# Evidence map - elemen-instanced-content-entry-rules

The one web-unique slice of the eLeMeN - FF14 (`elemen.sakura.ne.jp`)
`gamecontents/` section: the **entry-rule parameters** for 1.x instanced content -
the 4 instanced raids, the primal battles (with Hard/Extreme tiers), and the 5
open-world stronghold fields. A client-first recon of the whole `gamecontents/`
section found everything else client-redundant or video-breakdown territory (see
"Why the rest was skipped" below); the entry gates are the piece the client does
not decode.

Evidence tier: **wiki (CALIBRATION-grade)**.

## What the client already ships (dropped or used only to corroborate)

- **Instance names** - `xtx_raidDungeon.csv` (16 rows: JP col26 -> EN col27). The
  client's localized name is the place (the Howling Eye), not the JP operation
  flavor name (ガルーダ討伐戦). Used for the name cross-check.
- **Instance geometry / gate dialogue** - `raidDungeon*.csv` (barrier, exit, light,
  poster, warp), `instanceRaidGuide{AurumVale,CuttersCry}.csv` (gate NPC lines).
  Client-primary; not harvested.
- **Zones, instance areas, stronghold places** - `xtx_placeName.csv`
  (JP col1 -> EN col2). Used for the location cross-check.
- **Beastmen** - `xtx_monsterRace.csv`. Used for the stronghold beastmen join.
- **Unlock / prerequisite quests** - `xtx_quest.csv` + the sibling
  `elemen-quest-rewards-walkthroughs` set. Kept verbatim here as the gate label,
  not re-joined (the quest set owns quest ids).

## What is web-unique (the payload)

The numeric content gates, absent from any decoded client table:

- **Level restriction** (e.g. Disciple of War/Magic Lv45+; Toto[@1F]Rak Lv25+).
- **Party-size cap** (2-4, 4-8, or 8-player; primal Hard/Extreme tighten it).
- **Time limit** (60 min raids, 30 min primals).
- **Re-challenge cooldown** (15 min on clear / 5 min on failure; some counted
  from start time).
- Plus the **patch-change annotations** the client never carried (e.g. Toto[@1F]Rak
  party cap changed in patch 1.19; its re-challenge changed in patch 1.22a
  HotFixes) and the dated Lodestone reference pages.

## Coverage

15 rows in `instanced-content-entry-rules.csv`:

- **4 instanced raids** - Aurum Vale, Cutter's Cry, the Thousand Maws of Toto[@1F]Rak,
  Dzemael Darkhold.
- **6 primal operations** - Garuda (normal + Hard), Moggle Mog XII, Ifrit
  (normal + Hard + Extreme). Difficulty tiers are separate rows (variant column).
- **5 stronghold fields** - Castrum Novum, Shposhae, U'Ghamaro Mines, Natalan,
  Zahar'ak (open-world attack fields; no time-limit/re-challenge, some carry a
  beastmen tribe).

## Cross-check results

Method per `studies/elemen-bestiary/derived/client-crosscheck.md` (NFKC).

- **Operation names (raids + primals): 9/9 resolved** to `xtx_raidDungeon.csv`.
- **Locations (zones + instance areas + strongholds): all resolved** to
  `xtx_placeName.csv` - entry zones, primal arena areas, and the 5 stronghold
  places.
- **Beastmen: 3/3 resolved** to `xtx_monsterRace.csv` (Kobold, Ixal, Amalj'aa -
  the client stores the Amalj'aa row as `Amlaj'aa`, a client typo, recorded
  verbatim).

## Why the rest of gamecontents was skipped

Recon'd client-first:

- **Materia** - client-redundant. The マテリアデータ value grid matches
  `materia.csv` **exactly** (verified 天軍 Attack Power and 雄略 Crit: byte-identical
  16-value grade grids keyed to the param id); slot compatibility is the bool-column
  matrix in `materia.csv`; names/params are `materia.csv` + `xtx_itemName`. The only
  web-unique content is qualitative overmeld-mechanic prose (禁断のマテリア装着) with
  no numeric rate table - the hoped-for melding rates do not exist as data.
- **Grand Company** - client-redundant + lore prose. Rank names `xtx_gcRank`, rank
  thresholds `gcRank`, seal-shop inventory + costs `gcSealShopItem` (403 rows,
  system shop), GC quests already in `elemen-quest-rewards-walkthroughs`.
- **Per-boss strategy** on the raid/primal sub-pages - overlaps the video-breakdown
  evidence class; out of scope for a web-tables set.
- **`gamecontents/etc/` one-off pages** - Behest and Hamlet-defense have pcap sets,
  Skirmish has a content kind, and GM events / mounts / seasonal / Rivenroad are
  event-lore or video-breakdown territory; GuildTasks / guildtoken / BlackMarketeer
  are client shop tables.

## Gaps and caveats

- Level/party/time values are transcribed verbatim (JP) with parsed EN in the
  cross-check columns; the JP cells are authoritative.
- Strongholds fold party size into 推奨レベル (recommended level) rather than a
  separate 人数制限; `party_limit` is blank for them.
- Unlock/prereq quests are kept as verbatim labels, not re-joined to quest ids
  (the `elemen-quest-rewards-walkthroughs` set owns that join).
- Entry gates are server-side and uncheckable against the client; corroborate
  against a pcap or downstream instance definitions before promotion.

## Promotion

This repo records the `elemen-instanced-content-entry-rules` evidence id, this
path, and the verdict above. A consumer project promotes durable gating values
on its own side with an immutable citation to this record.
