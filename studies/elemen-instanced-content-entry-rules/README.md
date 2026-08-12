# eLeMeN FF14 1.x Instanced-Content Entry Rules - Web Tables

The one web-unique slice of the eLeMeN - FF14 (`elemen.sakura.ne.jp`)
`gamecontents/` section: the **entry-rule parameters** for 1.x instanced content -
the 4 instanced raids, the primal battles (Hard/Extreme tiers), and the 5
open-world stronghold fields. A client-first comparison of the full `gamecontents/`
section found everything else client-redundant (Materia value grid = `materia.csv`
exact; Grand Company ranks/seals = `gcRank`/`gcSealShopItem`) or video-breakdown
territory (per-boss strategy prose). The entry gates - level/party/time/re-challenge -
are the piece the client does not decode.

## Study contents

- `derived/instanced-content-entry-rules.csv` - 15 rows (4 raids + 6 primal
  operations + 5 strongholds). Each row: content class, instance + operation name
  (JP + client raidDungeon id/EN), difficulty variant, entry zone + coords + area
  (client placeName id/EN), level restriction, party cap, time limit, re-challenge
  cooldown, prerequisite condition, unlock quest, beastmen tribe, and the dated
  reference page.
- `derived/glossary.md` - field-label vocabulary, fixed phrases, and the client
  cross-check id table.
- `derived/evidence-map.md` - client-first verdict, cross-check results, and the
  "why the rest of gamecontents was skipped" record.

## Start here

- `derived/evidence-map.md`
- `derived/instanced-content-entry-rules.csv`

## Source material

- `sources/elemen-instanced-content-entry-rules/objects/pages/instanced-content-entry-rules.md` - verbatim transcription.
- Source HTML - preserved verbatim in the `elemen-site-archive` set; see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping.

## Promoted conclusions

`derived/instanced-content-entry-rules.csv` is the named calibration input for
the instance-entry investigation, covering level, party, time,
cooldown, and prerequisite constraints.

## Topics

- Instanced raids: Aurum Vale, Cutter's Cry, the Thousand Maws of Toto Rak,
  Dzemael Darkhold.
- Primals: Garuda, Moggle Mog XII, Ifrit (normal/Hard/Extreme).
- Strongholds: Castrum Novum, Shposhae, U'Ghamaro Mines, Natalan, Zahar'ak.
- Entry gates: level restriction, party cap, time limit, re-challenge cooldown,
  prerequisite quest - server-side, absent from the client.

## Evidence gaps

- Entry gates are uncheckable against the client (server-side). They use the wiki tier.
- Strongholds fold party size into recommended level. `party_limit` is blank there.
- Unlock/prereq quests kept verbatim, not re-joined to quest ids (owned by
  `elemen-quest-rewards-walkthroughs`).

## Further research

- Gate values remain uncorroborated against a pcap or instance definitions.
- Per-boss fight mechanics are outside this web-table set and belong to
  video-breakdown evidence.
