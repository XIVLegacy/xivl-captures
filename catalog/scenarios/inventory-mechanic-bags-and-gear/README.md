# Inventory and Gear Changes

## What this scenario contains

Inventory projection plus body/helm/soul-crystal/weapon equip changes through the gear
menu.

This view summarizes opcode evidence from packet captures.

- Raw captures: `sources/pcap-1.23b/objects/`.
- Evidence class: packet captures, which outrank video breakdowns and wiki sources.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from
  `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/inventory.pcapng` (27,908 B, 5 opcodes).
- `sources/pcap-1.23b/objects/open_gear_menu.pcapng` (25,940 B, 5 opcodes).
- `sources/pcap-1.23b/objects/change_bodyarmor.pcapng` (54,536 B, 17 opcodes).
- `sources/pcap-1.23b/objects/change_helm.pcapng` (39,660 B, 18 opcodes).
- `sources/pcap-1.23b/objects/gear_changesoul.pcapng` (23,784 B, 12 opcodes).
- `sources/pcap-1.23b/objects/gear_changeweapon.pcapng` (21,352 B, 18 opcodes).

## Key entities/topics

- inventory
- equipment
- gear-change
- soul-crystal
- armor
- weapon

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only -
  not decoded field semantics (those live in this repo's
  `derived/payload_layouts.json`).
- Service split across members: map 81.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
