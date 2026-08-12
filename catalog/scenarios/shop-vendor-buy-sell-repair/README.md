# Vendor - Buy, Sell, Repair

## What this scenario contains

NPC-vendor transactions: buying a square maple shield, selling an item, and repairing gear.

This is a **packet-capture reference scenario**. The raw pcaps live in this repo's shared `sources/pcap-1.23b/objects/` corpus; this view distils the opcode evidence those captures carry. Evidence tier: packet captures > video breakdown > wiki; this is packet evidence.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/buy_square_maple_shield.pcapng` (54,088 B, 18 opcodes).
- `sources/pcap-1.23b/objects/sell_item.pcapng` (57,580 B, 23 opcodes).
- `sources/pcap-1.23b/objects/repair_items.pcapng` (63,400 B, 24 opcodes).

## Key entities/topics

- shop
- vendor
- buy
- sell
- repair
- gil

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only - not decoded field semantics (those live in this repo's `derived/payload_layouts.json`).
- Service split across members: map 68.

## Next agent steps

- Use `file-inventory.csv` to pick the member pcap that isolates the opcode you need, then open it from `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check any opcode here against its full entry in this repo's `derived/opcode_names.json` before promoting a claim; that mapping was promoted from xivl-opcodes:opcodes.json and carries no freshness promise against the sibling catalog.
