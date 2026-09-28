# Guildleve - Accept and Complete

## What this scenario contains

Guildleve flow: accepting a regional leve and a local leve, a local leve completion, and
a full party battle-leve content session.

This view summarizes opcode evidence from packet captures.

- Raw captures: `sources/pcap-1.23b/objects/`.
- Evidence class: packet captures, which outrank video breakdowns and wiki sources.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from
  `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/accept_leve.pcapng` (59,576 B, 15 opcodes).
- `sources/pcap-1.23b/objects/accept_local_leve.pcapng` (50,676 B, 15 opcodes).
- `sources/pcap-1.23b/objects/local_leve_complete.pcapng` (358,296 B, 48 opcodes).
- `sources/pcap-1.23b/objects/party_battle_leve.pcapng` (1,429,864 B, 66 opcodes).

## Key entities/topics

- guildleve
- leve
- regional-leve
- local-leve
- battlecraft

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only -
  not decoded field semantics (those live in this repo's
  `derived/payload_layouts.json`).
- Service split across members: map 154, world 13.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
