# Cross-Zone Travel (Gridania / Black Shroud / Coerthas)

## What this scenario contains

Cross-zone travel exercising the map-server handoff between Gridania, the Black
Shroud, and Coerthas.

This view summarizes opcode evidence from packet captures.

- Raw captures: `sources/pcap-1.23b/objects/`.
- Evidence class: packet captures, which outrank video breakdowns and wiki sources.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from
  `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/gridania_to_coerthas.pcapng` (939,832 B, 65 opcodes).
- `sources/pcap-1.23b/objects/from_gridania_to_blackshroud.pcapng` (196,308 B, 55
  opcodes).

## Key entities/topics

- zone-travel
- zone-handoff
- region-change
- map-ui

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only -
  not decoded field semantics (those live in this repo's
  `derived/payload_layouts.json`).
- Service split across members: map 125, world 12.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
