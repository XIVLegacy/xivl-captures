# Login Handshake and In-World Idle

## What this scenario contains

Session-layer captures: the connection/login handshake and an in-world idle keepalive
baseline.

This view summarizes opcode evidence from packet captures.

- Raw captures: `sources/pcap-1.23b/objects/`.
- Evidence class: packet captures, which outrank video breakdowns and wiki sources.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from
  `derived/opcode_names.json`, plus caveats and gaps.
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

- This scenario carries opcode identity, direction, service, and payload lengths only -
  not decoded field semantics (those live in this repo's
  `derived/payload_layouts.json`).
- Service split across members: map 69.
- Caveat: login.pcapng contains TLS account-service connections, raw lobby connections
  on TCP 54994, and raw game connections on TCP 54992. The 54992 game lanes are included
  in the canonical decode. The 54994 lobby lanes are a different protocol and remain
  outside the game decode; their recipe is recorded in studies/lobby-handshake-triage/.
  TLS account-service traffic also remains outside the game decode.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
