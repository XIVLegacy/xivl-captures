# Inventory and Gear Changes

## What this scenario contains

Inventory projection plus body/helm/soul-crystal/weapon equip changes through the gear menu.

This is a **packet-capture reference scenario**. The raw pcaps live in this repo's shared `sources/pcap-1.23b/objects/` corpus; this view distils the opcode evidence those captures carry. Evidence tier: packet captures > video breakdown > wiki; this is packet evidence.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from `derived/opcode_names.json`, plus caveats and gaps.
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

- This scenario carries opcode identity, direction, service, and payload lengths only - not decoded field semantics (those live in this repo's `derived/payload_layouts.json`).
- Service split across members: map 81.

## Next agent steps

- Use `file-inventory.csv` to pick the member pcap that isolates the opcode you need, then open it from `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check any opcode here against its full entry in this repo's `derived/opcode_names.json` before promoting a claim; that mapping was promoted from xivl-opcodes:opcodes.json and carries no freshness promise against the sibling catalog.
