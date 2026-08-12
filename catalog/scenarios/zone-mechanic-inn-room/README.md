# Inn Room (The Roost)

## What this scenario contains

Private inn-room captures (Gridania's Roost): checking the bed, the room map, and
leaving the room.

This view summarizes opcode evidence from packet captures.

- Raw captures: `sources/pcap-1.23b/objects/`.
- Evidence class: packet captures, which outrank video breakdowns and wiki sources.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from
  `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/move_out_of_room.pcapng` (83,412 B, 69 opcodes).
- `sources/pcap-1.23b/objects/checkbed.pcapng` (26,276 B, 14 opcodes).
- `sources/pcap-1.23b/objects/check_room_map.pcapng` (28,032 B, 4 opcodes).

## Key entities/topics

- inn-room
- housing
- the-roost
- private-quarters

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only -
  not decoded field semantics (those live in this repo's
  `derived/payload_layouts.json`).
- Service split across members: map 94, world 6.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
