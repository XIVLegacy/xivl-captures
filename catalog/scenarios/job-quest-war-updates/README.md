# Warrior - Pride and Duty Updates

## What this scenario contains

Three captures of the Warrior job quest Pride and Duty (Will Take You from the
Mountain).

This view summarizes opcode evidence from packet captures.

- Raw captures: `sources/pcap-1.23b/objects/`.
- Evidence class: packet captures, which outrank video breakdowns and wiki sources.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from
  `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/war_quest_update1.pcapng` (42,812 B, 19 opcodes).
- `sources/pcap-1.23b/objects/war_quest_update2.pcapng` (206,216 B, 67 opcodes).
- `sources/pcap-1.23b/objects/war_quest_update3.pcapng` (103,520 B, 40 opcodes).

## Key entities/topics

- quest
- quest-update
- war-quest

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only -
  not decoded field semantics (those live in this repo's
  `derived/payload_layouts.json`).
- Service split across members: map 134, world 13.
- Caveat: update1 calls processEventCurious; update3 calls processEventClear and
  processEventJob. These handlers occur in quest/scenario/war/war0j1.lua, the first
  Warrior job quest script. update2 is the middle capture in the same recording series.
  The quest title is retained in
  studies/elemen-quest-rewards-walkthroughs/derived/quest-walkthroughs.csv,
  client_quest_id 111201.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
