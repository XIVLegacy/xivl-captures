# Glossary - instanced-content entry rules

## Field labels (site vocabulary)

| JP label | meaning | CSV column |
|---|---|---|
| 作戦名 | operation name (JP flavor name for the duty) | operation_jp |
| 名称 | name (stronghold field) | operation_jp |
| 場所 | location (entry zone + coords) | location_zone_jp / location_coords |
| エリア | area (the instance's own place) | area_jp |
| レベル制限 | level restriction | level_restriction |
| 推奨レベル | recommended level (stronghold; embeds party size) | level_restriction |
| 人数制限 | party-size cap | party_limit |
| 制限時間 | time limit | time_limit |
| 再挑戦 | re-challenge cooldown | rechallenge |
| 必要な条件 / クエスト受注条件 | prerequisite condition (quest gate) | prereq_condition |
| クエスト名 | associated unlock quest | unlock_quest_jp |
| 関連クエスト | related quest (stronghold) | prereq_condition |
| 獣人 | beastmen tribe | beastmen_jp |
| 参考ページ | reference page (dated Lodestone topic) | reference |

## Fixed phrases

| JP | meaning |
|---|---|
| ファイターもしくはソーサラー | Disciple of War or Magic |
| レベルNN以上 | level NN or above |
| N～M人PT限定 | N-M player party only |
| N分 | N minutes |
| 討伐成功 / 討伐失敗 | clear success / clear failure |
| 開始時間からカウント | counted from start time |
| 討伐戦 / 討滅戦 | subjugation / annihilation (normal / hard duty suffix) |
| 真 / 極 | Hard / Extreme difficulty prefix |

## Client cross-check tables

- Operation names (raids + primals) -> `xtx_raidDungeon.csv` (JP col26 -> id col0,
  EN col27). The client's localized name is the place (e.g. the Howling Eye), not
  the JP operation flavor name (ガルーダ討伐戦).
- Zones / instance areas / stronghold names -> `xtx_placeName.csv` (JP col1 ->
  id col0, EN col2).
- Beastmen -> `xtx_monsterRace.csv` (JP col1 -> id col0, EN col2). Note the client
  string for アマルジャ is `Amlaj'aa` (a client-side typo for Amalj'aa); recorded
  verbatim as the cross-check value.

## Cross-check ids

| JP operation / place | client id | client EN |
|---|---|---|
| オーラムヴェイル霧中行軍 | 6 | Aurum Vale |
| カッターズクライ流砂迷宮 | 7 | Cutter's Cry |
| トトラク威力偵察指令 | 1 | the Thousand Maws of Toto[@1F]Rak |
| ゼーメル要塞奪還作戦 | 2 | Dzemael Darkhold |
| ガルーダ討伐戦 / 真ガルーダ討滅戦 | 12 / 11 | the Howling Eye / (Hard) |
| 善王モグル・モグXII世 討滅戦 | 5 | Thornmarch |
| イフリート討伐戦 / 真 / 極 | 4 / 3 / 14 | the Bowl of Embers / (Hard) / (Extreme) |
| カストルム・ノヴム | 5009 | Castrum Novum |
| シュポシェの霊窟 | 1122 | Shposhae |
| ウ・ガマロ武装鉱山 | 1125 | U'Ghamaro Mines |
| ナタラン入植地 | 4503 | Natalan |
| ザハラク戦陣 | 3521 | Zahar'ak |
