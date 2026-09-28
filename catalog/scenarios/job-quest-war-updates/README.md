# War Quest Updates

## What this scenario contains

A three-part quest-update sequence captured from the `war_quest` scenario.

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
- Caveat: The `war_quest` filename is read here as a Warrior job questline, hence
  content_kind job-quest / progression_track job-quest. This is a filename inference
  only - not confirmed against the quest data - and could instead be a story or other
  quest. Refine when the quest is identified.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
