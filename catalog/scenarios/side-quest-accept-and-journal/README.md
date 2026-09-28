# Quest - Accept, Journal, Update

## What this scenario contains

Generic quest-state captures: accepting a quest, the quest journal projection, and a
quest update.

This view summarizes opcode evidence from packet captures.

- Raw captures: `sources/pcap-1.23b/objects/`.
- Evidence class: packet captures, which outrank video breakdowns and wiki sources.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from
  `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/accept_quest.pcapng` (53,180 B, 15 opcodes).
- `sources/pcap-1.23b/objects/quest_journal.pcapng` (32,264 B, 5 opcodes).
- `sources/pcap-1.23b/objects/quest_update.pcapng` (66,756 B, 14 opcodes).

## Key entities/topics

- quest
- accept
- journal
- quest-update

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only -
  not decoded field semantics (those live in this repo's
  `derived/payload_layouts.json`).
- Service split across members: map 37.
- Caveat: content_kind side-quest is the generic quest-state reading; the captures do
  not identify the specific quest, so it could be a class/job/story quest. Refine if the
  quest is identified.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
