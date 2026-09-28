# Chat Channels - Say, Shout, NPC Talk

## What this scenario contains

Chat-channel captures: proximity say, broadcast shout, and an NPC small-talk exchange
(Louisoix).

This view summarizes opcode evidence from packet captures.

- Raw captures: `sources/pcap-1.23b/objects/`.
- Evidence class: packet captures, which outrank video breakdowns and wiki sources.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from
  `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/chat_say.pcapng` (8,864 B, 5 opcodes).
- `sources/pcap-1.23b/objects/chat_shout.pcapng` (7,872 B, 5 opcodes).
- `sources/pcap-1.23b/objects/small_talk_louisoix.pcapng` (18,444 B, 25 opcodes).

## Key entities/topics

- chat
- say
- shout
- npc-dialogue
- communication

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only -
  not decoded field semantics (those live in this repo's
  `derived/payload_layouts.json`).
- Service split across members: map 41.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
