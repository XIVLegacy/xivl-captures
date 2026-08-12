# Party and Friend List

## What this scenario contains

Party state machine (invite/join, idle-in-party keepalive) and a friend-list search.

This is a **packet-capture reference scenario**. The raw pcaps live in this repo's shared `sources/pcap-1.23b/objects/` corpus; this view distils the opcode evidence those captures carry. Evidence tier: packet captures > video breakdown > wiki; this is packet evidence.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/invite_join_party.pcapng` (88,372 B, 16 opcodes).
- `sources/pcap-1.23b/objects/idle_in_party.pcapng` (20,168 B, 4 opcodes).
- `sources/pcap-1.23b/objects/friendlist_search.pcapng` (37,744 B, 9 opcodes).

## Key entities/topics

- party
- invite
- friend-list
- social
- group

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only - not decoded field semantics (those live in this repo's `derived/payload_layouts.json`).
- Service split across members: map 34, world 6.

## Next agent steps

- Use `file-inventory.csv` to pick the member pcap that isolates the opcode you need, then open it from `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check any opcode here against its full entry in this repo's `derived/opcode_names.json` before promoting a claim; that mapping was promoted from xivl-opcodes:opcodes.json and carries no freshness promise against the sibling catalog.
