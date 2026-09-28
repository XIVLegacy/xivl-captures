# Mooglebox regional mob camp maps

This study preserves four Mooglebox map pages from the FFXIV 1.x web-table
tier. The deterministic importer records one row per embedded map marker:

- Coerthas: 39 markers
- Black Shroud: 74 markers
- La Noscea: 63 markers
- Thanalan: 78 markers

Start with derived/evidence-map.md for the source pins, field meanings, and
uncertainty boundary. derived/marker-records.csv is the complete normalized
table. The source HTML members remain under
sources/mooglebox-regional-mob-maps/objects/ and are hash-pinned by the
source manifest.

An owner-supplied screenshot is retained as a companion object. Its displayed
Amalj'aa tuple matches Thanalan marker 52; the screenshot itself does not carry
page metadata and therefore does not independently establish that attribution.

The pages describe groups of mobs. A slash-separated label is retained as a
candidate list with shared_slot_verdict=unresolved_shared_slot; this study
does not choose an individual mob for that marker or claim a retail slot,
population, or respawn rule.
