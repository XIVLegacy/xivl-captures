# War Quest Updates

## What this scenario contains

A three-part quest-update sequence captured from the `war_quest` scenario.

This is a **packet-capture reference scenario**. The raw pcaps live in this repo's shared `sources/pcap-1.23b/objects/` corpus; this view distils the opcode evidence those captures carry. Evidence tier: packet captures > video breakdown > wiki; this is packet evidence.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/war_quest_update1.pcapng` (42,812 B, 19 opcodes).
- `sources/pcap-1.23b/objects/war_quest_update2.pcapng` (206,216 B, 67 opcodes).
- `sources/pcap-1.23b/objects/war_quest_update3.pcapng` (103,520 B, 40 opcodes).

## Key entities/topics

- quest
- quest-update
- war-quest

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only - not decoded field semantics (those live in this repo's `derived/payload_layouts.json`).
- Service split across members: map 134, world 13.
- Caveat: The `war_quest` filename is read here as a Warrior job questline, hence content_kind job-quest / progression_track job-quest. This is a filename inference only - not confirmed against the quest data - and could instead be a story or other quest. Refine when the quest is identified.

## Next agent steps

- Use `file-inventory.csv` to pick the member pcap that isolates the opcode you need, then open it from `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check any opcode here against its full entry in this repo's `derived/opcode_names.json` before promoting a claim; that mapping was promoted from xivl-opcodes:opcodes.json and carries no freshness promise against the sibling catalog.
