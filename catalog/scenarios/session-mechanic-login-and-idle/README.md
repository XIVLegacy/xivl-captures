# Login Handshake and In-World Idle

## What this scenario contains

Session-layer captures: the connection/login handshake and an in-world idle keepalive baseline.

This is a **packet-capture reference scenario**. The raw pcaps live in this repo's shared `sources/pcap-1.23b/objects/` corpus; this view distils the opcode evidence those captures carry. Evidence tier: packet captures > video breakdown > wiki; this is packet evidence.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/login.pcapng` (856,236 B, 58 opcodes).
- `sources/pcap-1.23b/objects/idling.pcapng` (42,608 B, 4 opcodes).

## Key entities/topics

- session
- login
- handshake
- keepalive
- idle

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only - not decoded field semantics (those live in this repo's `derived/payload_layouts.json`).
- Service split across members: map 69, world 11.
- Caveat: login.pcapng contains TLS account-service connections, raw lobby connections on TCP 54994, and raw game connections on TCP 54992. The 54992 game lanes are included in the canonical decode. The 54994 lobby lanes are a different protocol and remain outside the game decode; their recipe is recorded in studies/lobby-handshake-triage/. TLS account-service traffic also remains outside the game decode.

## Next agent steps

- Use `file-inventory.csv` to pick the member pcap that isolates the opcode you need, then open it from `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check any opcode here against its full entry in this repo's `derived/opcode_names.json` before promoting a claim; that mapping was promoted from xivl-opcodes:opcodes.json and carries no freshness promise against the sibling catalog.
