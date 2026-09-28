# Attributes and Class Switching

## What this scenario contains

Character-sheet captures: allocating STR, querying attributes, and switching class to
Botanist and Weaver.

This view summarizes opcode evidence from packet captures.

- Raw captures: `sources/pcap-1.23b/objects/`.
- Evidence class: packet captures, which outrank video breakdowns and wiki sources.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from
  `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/add_str.pcapng` (20,056 B, 11 opcodes).
- `sources/pcap-1.23b/objects/attributes.pcapng` (22,624 B, 5 opcodes).
- `sources/pcap-1.23b/objects/change_to_botanist.pcapng` (41,500 B, 21 opcodes).
- `sources/pcap-1.23b/objects/switch_to_weaver.pcapng` (33,364 B, 23 opcodes).

## Key entities/topics

- attributes
- stat-allocation
- class-change
- botanist
- weaver

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only -
  not decoded field semantics (those live in this repo's
  `derived/payload_layouts.json`).
- Service split across members: map 64.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
