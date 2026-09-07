# Evidence Map - The Bowl of Embers (Ifrit) Video Breakdown

## What this is

A breakdown of a retail 1.x gameplay video (`vidssave.com FFXIV 1.0
Ifrit fight 1080P.mp4`, ~12:40) of the `Ifrit` primal fight in `The Bowl of
Embers`, ingested 2026-06-16. The point-of-view player is reported as a
Conjurer Lv30 in a four-player Light Party (the tank, the second healer, the
melee ally). The raw document at
`sources/primal-battle-ifrit-bowl-of-embers/objects/the_bowl_of_embers_ifrit_video_breakdown.md`
is preserved exactly as produced and is immutable. This study-facing map
generalizes player and party character names to roles and records what survived
the available client-data cross-check.

Evidence tier: packet captures > video breakdown > wiki. No `xivl-opcodes`
packet set covers Ifrit, so the available cross-check is against the decoded
client data in `xivl-client-data` (the everyday source of truth here), not
packets. The source manifest has no URL or uploader, and the retained breakdown
identifies the clip only by download filename and duration. No video assertion
below was independently rechecked from reproducibly identified underlying
footage; this provenance gap does not establish that the reported observations
are false.

## Verification (2026-06-16)

Action names cross-checked against `xivl-client-data/csv` (`xtx_command.csv`
command-name strings and `worldMaster.csv` battle-log strings). The string
agreement corroborates spellings and available log forms only; it does not prove
that the clip showed each action, establish the clip's patch, or independently
authenticate the observation. The retained breakdown's section 3 reports no
Ifrit or NPC speech observed in this clip; that is clip-scoped and does not
establish that Ifrit has no speech across 1.x. No ARR-only substitution was found
in the checked names.

### Client-data corroboration (video observation not independently verified)

- The checked names exist in the 1.23b command sheet: `Vulcan Burst`
  (xtx_command 493), `Incinerate` (494), `Eruption` (495), `Crimson Cyclone`
  (496), plus `Hellfire`. `Infernal Nail` / "An infernal nail appears!" /
  "fades away" are present in the client strings (worldMaster 1379-1381).
- The retained breakdown uses log forms that exist in the client data:
  `readies [command]`; `Ifrit's attack hits X for N points of damage`;
  `partially blocks ... taking N points of damage`; `resists your Slow`; and
  the listed enfeeble forms. The reported value 94 remains video evidence, not a
  client-data corroboration.
- Ability-sourced recovery strings exist in the client data: `recovers N HP from
  Aegis Boon` / `... from Outmaneuver` / `... from Featherfoot` are worldMaster
  1119-1121, and `recovers N MP from Invigorate` is worldMaster 1407.
- Spot-checked ally ability names resolve to client strings: `Second Wind`,
  `Invigorate`, `Shock Spikes`, `Featherfoot`, `Aegis Boon`, `Outmaneuver`,
  `Ambidexterity`, `Red Lotus`, `War Drum`, `Tranquility`.
- The filename and reported visual details are retained source claims only.
  Matching names do not independently establish a 1.x version or exclude ARR
  contamination in the underlying footage.

### Contradicted by available client strings

- None found in the checked strings. This is not a review of the underlying video
  and does not exclude a contradiction in an unretained packet sequence.

### Unverifiable (source footage not independently identified; tuning leads only)

- All damage and heal magnitudes are one four-player Lv30-party run with shields,
  partial blocks, and a `??`-level Ifrit - tuning evidence, not values to
  hard-code (the breakdown says so at the top of section 6).
- All other video-derived action, timing, outcome, and no-dialogue assertions are
  likewise unverified from reproducibly identified underlying footage.
- Exact repetition counts for Vulcan Burst / Eruption / Incinerate / Crimson
  Cyclone (the log scrolls; the breakdown gives lower bounds, not totals).
- Whether Hellfire repeats in a longer or failed attempt (observed once at ~8:00).
- The exact number of simultaneous Infernal Nails (at least two "appears" lines;
  only one clearly targetable at a time).
- `Ifrit is defeated.` was not readable; defeat is inferred from the reward lines,
  `Aero II cannot be performed on a KO'd target.`, and `Now leaving the Bowl of
  Embers.` - a sound inference, but not a directly observed defeat line.

### Reported video values (unverified from underlying footage)

- Ifrit damage magnitudes vs a defended Lv30 party: auto-attack ~29-127 (one
  partial block 94); Vulcan Burst 31-87 (AoE); Eruption 339; Incinerate ~189-205;
  Hellfire 343-420 across the party (the ~8:03 raid hit); Crimson Cyclone 260-366.
- Heal/recovery magnitudes: Cure II 251-286, Curaga II 388, Second Wind 145-265,
  Invigorate +50 MP; the Conjurer's `Siphon MP` drains 55/59 MP from Ifrit.
- Structure/pacing: 30-minute duty timer; the Infernal Nail phase at ~7:00; the
  single Hellfire at ~8:00; defeat/exit ~12:10; reward `358 experience points` +
  `358 shield experience points`. No matching Ifrit packet sequence is retained
  here to corroborate these observations.

## Evidence gaps

- No packets, actor IDs, or localized non-English text here. The source manifest
  records no URL or uploader for the underlying video; the retained timestamps
  are the only locators in the breakdown.
- Damage numbers are one mitigated four-player run; the `??`-level Ifrit means the
  level delta is unknown.
- The entry interaction (what put the party into the Bowl of Embers) is off-clip,
  so no entry/`bound by duty`/level-correction line was captured.
