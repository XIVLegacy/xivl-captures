# Cross-Zone Travel (Gridania / Black Shroud / Coerthas)

## What this scenario contains

Cross-zone travel exercising the map-server handoff between Gridania, the Black Shroud, and Coerthas.

This is a **packet-capture reference scenario**. The raw pcaps live in this repo's shared `sources/pcap-1.23b/objects/` corpus; this view distils the opcode evidence those captures carry. Evidence tier: packet captures > video breakdown > wiki; this is packet evidence.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/gridania_to_coerthas.pcapng` (939,832 B, 65 opcodes).
- `sources/pcap-1.23b/objects/from_gridania_to_blackshroud.pcapng` (196,308 B, 55 opcodes).

## Key entities/topics

- zone-travel
- zone-handoff
- region-change
- map-ui

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only - not decoded field semantics (those live in this repo's `derived/payload_layouts.json`).
- Service split across members: map 125, world 12.

## Next agent steps

- Use `file-inventory.csv` to pick the member pcap that isolates the opcode you need, then open it from `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check any opcode here against its full entry in this repo's `derived/opcode_names.json` before promoting a claim; that mapping was promoted from xivl-opcodes:opcodes.json and carries no freshness promise against the sibling catalog.
