# Combat and Action Bar

## What this scenario contains

Combat-system captures: auto-attack, basic skills, battle/passive stance toggle, and the action-and-traits bar.

This is a **packet-capture reference scenario**. The raw pcaps live in this repo's shared `sources/pcap-1.23b/objects/` corpus; this view distils the opcode evidence those captures carry. Evidence tier: packet captures > video breakdown > wiki; this is packet evidence.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from `derived/opcode_names.json`, plus caveats and gaps.
- `file-inventory.csv` - one row per member pcap (bytes, sha256, observed opcodes).

## Raw materials

- `sources/pcap-1.23b/objects/combat_autoattack.pcapng` (82,908 B, 46 opcodes).
- `sources/pcap-1.23b/objects/combat_skills.pcapng` (63,028 B, 32 opcodes).
- `sources/pcap-1.23b/objects/battle_mode_passive_mode.pcapng` (12,776 B, 9 opcodes).
- `sources/pcap-1.23b/objects/action_and_traits.pcapng` (37,584 B, 11 opcodes).

## Key entities/topics

- combat
- auto-attack
- weaponskill
- battle-stance
- action-bar
- traits

## Gaps

- This scenario carries opcode identity, direction, service, and payload lengths only - not decoded field semantics (those live in this repo's `derived/payload_layouts.json`).
- Service split across members: map 104, world 5.

## Next agent steps

- Use `file-inventory.csv` to pick the member pcap that isolates the opcode you need, then open it from `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check any opcode here against its full entry in this repo's `derived/opcode_names.json` before promoting a claim; that mapping was promoted from xivl-opcodes:opcodes.json and carries no freshness promise against the sibling catalog.
