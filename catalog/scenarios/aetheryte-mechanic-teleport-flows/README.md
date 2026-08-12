# Aetheryte Teleport Flows

## What this scenario contains

Aetheryte teleports to Camp Nine Ivies, Camp Tranquil, Gridania, and the return-to-inn
flow.

This view summarizes opcode evidence from packet captures.

- Raw captures: `sources/pcap-1.23b/objects/`.
- Evidence class: packet captures, which outrank video breakdowns and wiki sources.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from
  `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/teleport_to_camp_nine_ivies.pcapng` (80,004 B, 61
  opcodes).
- `sources/pcap-1.23b/objects/teleport_to_camp_tranquil.pcapng` (67,920 B, 61 opcodes).
- `sources/pcap-1.23b/objects/teleport_to_gridania.pcapng` (67,620 B, 65 opcodes).
- `sources/pcap-1.23b/objects/return_to_inn.pcapng` (44,012 B, 61 opcodes).

## Key entities/topics

- teleport
- aetheryte
- return
- inn
- the-roost

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only -
  not decoded field semantics (those live in this repo's
  `derived/payload_layouts.json`).
- Service split across members: map 264, world 24.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
