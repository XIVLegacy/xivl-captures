# Historical BattleCommand Workbook

This study preserves and mechanically extracts `BattleCommand.ods`, a
historical secondary research workbook about FFXIV 1.x battle commands. The
workspace owner reports that it originated during the early Project Meteor
period, close to the 1.x shutdown era. The workbook itself records only a
2019-02-03 save and a LibreOffice 6.1.2.1 generator, so those facts do not date
its original research.

The original is immutable under
`sources/historical-battlecommand-workbook/objects/`. The generated
`derived/commands.json` keeps displayed cell text for selected fields in `raw`,
typed conversions in `normalized`, formulas for those selected fields in
`cached_formulas`, and the unfinished analyst weapon-skill table in a separate
array. Its field map marks workbook fields, cached formulas, analyst custom
columns, and analyst notes. It does not reproduce the complete cell matrix:
the original workbook is the canonical raw artifact, and the incomplete
auxiliary region after column FC remains unextracted.

This evidence is provisional at the field level. It may fill a gap when no
stronger retail evidence exists. It does not override retail captures, video,
client data, or client scripts. Analyst notes and uncertain labels remain
leads.

Regenerate or verify the structured artifact with:

```powershell
python tools/extract_historical_battlecommand.py
python tools/extract_historical_battlecommand.py --check
```

See `derived/evidence-map.md` for the first Bahamut-relevant records, retail
cross-check, conflicts, and unresolved meanings.
