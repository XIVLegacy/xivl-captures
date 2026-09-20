# Retail NPC and Self-Repair Contract

## Study contents

This study isolates the repair evidence in the retained retail 1.23b capture
`repair_items.pcapng` and joins it only to pinned client artifacts. It does not
use emulator behavior as evidence.

- `derived/npc-repair-observations.csv` records the six confirmation prompts,
  accepted client replies, and following gil inventory updates.
- `derived/verdicts.md` records the wire shape, client-script contract, result
  boundary, and exact remaining questions.

The source capture is
`sources/pcap-1.23b/objects/repair_items.pcapng`, SHA-256
`bbd829cbd3f42b2cbfb3aa8a74a1cc35d4e2c16c99e5a4a20ca76573f02dd90f`.
Packet locators are zero-based capture packet indices. Event locators are
zero-based decoded application-event indices inside the reconstructed
directional TCP stream.

## Scope boundary

The capture proves the displayed NPC tariff and the accepted-response/gil
sequence for six item specimens. It does not contain an attributable before
and after durability value for any repaired item. It also contains no retained
self-repair execution. Consequently this study does not assign an NPC repair
result percentage or a self-repair wire payload.

## Verification

Run the repository refresh and validation suite. `tools/build_checksums.py`
owns `derived/checksums.sha256`; the catalog builders discover the study from
its manifest.
