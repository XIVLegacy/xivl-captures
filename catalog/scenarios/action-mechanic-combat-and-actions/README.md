# Combat and Action Bar

## What this scenario contains

Combat-system captures: auto-attack, basic skills, battle/passive stance toggle, and the
action-and-traits bar.

This view summarizes opcode evidence from packet captures.

- Raw captures: `sources/pcap-1.23b/objects/`.
- Evidence class: packet captures, which outrank video breakdowns and wiki sources.

## Load first

- `evidence-map.md` - the per-capture opcode rollup, names from
  `derived/opcode_names.json`, plus caveats and gaps.
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

- This scenario carries opcode identity, direction, service, and payload lengths only -
  not decoded field semantics (those live in this repo's
  `derived/payload_layouts.json`).
- Service split across members: map 104, world 5.

## Using this view

- Use `file-inventory.csv` to choose a member pcap for the opcode, then open it from
  `sources/pcap-1.23b/objects/` for byte-level work.
- Cross-check the full opcode entry in this repo's `derived/opcode_names.json` before
  citing it.
- Mapping provenance: xivl-opcodes:opcodes.json. The promoted copy is not synchronized
  automatically.
