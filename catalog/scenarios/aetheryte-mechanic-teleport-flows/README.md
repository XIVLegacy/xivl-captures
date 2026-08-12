# Aetheryte Teleport Flows

## What this scenario contains

Aetheryte teleports to Camp Nine Ivies, Camp Tranquil, Gridania, and the return-to-inn flow.

This is a **packet-capture reference scenario**. The raw pcaps live in this repo's shared `sources/pcap-1.23b/objects/` corpus; this view distils the opcode evidence those captures carry. Evidence tier: packet captures > video breakdown > wiki; this is packet evidence.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/teleport_to_camp_nine_ivies.pcapng` (80,004 B, 61 opcodes).
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

- This scenario carries opcode identity, direction, service, and payload lengths only - not decoded field semantics (those live in this repo's `derived/payload_layouts.json`).
- Service split across members: map 264, world 24.

## Next agent steps

- Use `file-inventory.csv` to pick the member pcap that isolates the opcode you need, then open it from `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check any opcode here against its full entry in this repo's `derived/opcode_names.json` before promoting a claim; that mapping was promoted from xivl-opcodes:opcodes.json and carries no freshness promise against the sibling catalog.
