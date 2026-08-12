# Evidence Map - The Bowl of Embers (Ifrit) Video Breakdown

## What this is

A breakdown of a retail 1.x gameplay video (`vidssave.com FFXIV 1.0
Ifrit fight 1080P.mp4`, ~12:40) of the `Ifrit` primal fight in `The Bowl of
Embers`, ingested 2026-06-16. The point-of-view player is a Conjurer Lv30 in a
four-player Light Party (the tank, the second healer, the melee ally). The raw
document at `sources/primal-battle-ifrit-bowl-of-embers/objects/the_bowl_of_embers_ifrit_video_breakdown.md`
is preserved exactly as produced and is immutable. This study-facing map
generalizes player and party character names to roles and records what survived
verification.

Evidence tier: packet captures > video breakdown > wiki. No `xivl-opcodes`
packet set covers Ifrit, so the verification below is against the decoded client
data in `xivl-client-data` (the everyday source of truth here) - not packets.

## Verification (2026-06-16)

Action names cross-checked against `xivl-client-data/csv` (`xtx_command.csv`
command-name strings and `worldMaster.csv` battle-log strings). Dialogue: none to
check (Ifrit has no speech in 1.x; section 3 is correctly "not observed"). Result:
the entire Ifrit action pool and every spot-checked ally ability resolves to a
real 1.23b string. No ARR-only substitutions were found.

### Confirmed (safe to cite)

- Ifrit's full readied-action pool is real and contiguous in the 1.23b command
  sheet: `Vulcan Burst` (xtx_command 493), `Incinerate` (494), `Eruption` (495),
  `Crimson Cyclone` (496), plus `Hellfire`. `Infernal Nail` / "An infernal nail
  appears!" / "fades away" are real (worldMaster 1379-1381).
- The breakdown preserves the exact 1.x log forms: `readies [command]` for every
  Ifrit special; the auto-attack form `Ifrit's attack hits X for N points of
  damage` (distinct from the spell/multi-hit form); `partially blocks ... taking
  94 points of damage`;
  `resists your Slow`; the enfeeble forms `Your Dia inflicts ... with the effect
  of Dia` / `is no longer poisoned` / `magic defense is no longer decreased`.
- Ability-sourced recovery lines match the client exactly: `recovers N HP from
  Aegis Boon` / `... from Outmaneuver` / `... from Featherfoot` are worldMaster
  1119-1121, and `recovers N MP from Invigorate` is worldMaster 1407 - the same
  lines the breakdown reports for the tank and the party.
- Spot-checked ally abilities all resolve to real strings: `Second Wind`,
  `Invigorate`, `Shock Spikes`, `Featherfoot`, `Aegis Boon`, `Outmaneuver`,
  `Ambidexterity`, `Red Lotus`, `War Drum`, `Tranquility`.
- Version sanity: client visuals + filename are 1.x, and the action pool matching
  the 1.23b command sheet (not ARR names) corroborates it. No ARR contamination.

### Contradicted by stronger evidence (do not use)

- None found. (No packet set exists to contradict against; nothing in the client
  data conflicts with an observed claim.)

### Unverifiable (single-video; tuning targets only)

- All damage and heal magnitudes are one four-player Lv30-party run with shields,
  partial blocks, and a `??`-level Ifrit - tuning evidence, not values to
  hard-code (the breakdown says so at the top of section 6).
- Exact repetition counts for Vulcan Burst / Eruption / Incinerate / Crimson
  Cyclone (the log scrolls; the breakdown gives lower bounds, not totals).
- Whether Hellfire repeats in a longer or failed attempt (observed once at ~8:00).
- The exact number of simultaneous Infernal Nails (at least two "appears" lines;
  only one clearly targetable at a time).
- `Ifrit is defeated.` was not readable; defeat is inferred from the reward lines,
  `Aero II cannot be performed on a KO'd target.`, and `Now leaving the Bowl of
  Embers.` - a sound inference, but not a directly observed defeat line.

### Unique value (in no other evidence source)

- Ifrit damage magnitudes vs a defended Lv30 party: auto-attack ~29-127 (one
  partial block 94); Vulcan Burst 31-87 (AoE); Eruption 339; Incinerate ~189-205;
  Hellfire 343-420 across the party (the ~8:03 raid hit); Crimson Cyclone 260-366.
- Heal/recovery magnitudes: Cure II 251-286, Curaga II 388, Second Wind 145-265,
  Invigorate +50 MP; the Conjurer's `Siphon MP` drains 55/59 MP from Ifrit.
- Structure/pacing: 30-minute duty timer; the Infernal Nail phase at ~7:00; the
  single Hellfire at ~8:00; defeat/exit ~12:10; reward `358 experience points` +
  `358 shield experience points`. None of this is carried by packets.

## Evidence gaps

- No packets, actor IDs, or localized non-English text here.
- Damage numbers are one mitigated four-player run; the `??`-level Ifrit means the
  level delta is unknown.
- The entry interaction (what put the party into the Bowl of Embers) is off-clip,
  so no entry/`bound by duty`/level-correction line was captured.
