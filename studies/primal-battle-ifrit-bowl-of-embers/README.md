# The Bowl of Embers (Ifrit) - Video Breakdown

## Study contents

One observation document distilled from a retail 1.x gameplay video
(`vidssave.com FFXIV 1.0 Ifrit fight 1080P.mp4`, ~12:40) of the `Ifrit` primal in
`The Bowl of Embers`: the point-of-view player (Conjurer Lv30) in a four-player
Light Party, one member tanking. Player and party character names are generalized
to roles (the player, the tank, the second healer, the melee ally). Video
evidence, not packet evidence. The tier is packet captures > video breakdown > wiki.

## Start here

- `derived/evidence-map.md` - the claim-by-claim verification ledger (read it
  BEFORE the raw document). All of Ifrit's readied actions and the spot-checked
  ally abilities were confirmed against the `xivl-client-data` client strings.
  No contradictions were found.
- `sources/primal-battle-ifrit-bowl-of-embers/objects/the_bowl_of_embers_ifrit_video_breakdown.md` - the breakdown
  exactly as produced. It is immutable. Study-facing prose generalizes player and party
  character names to roles.

## Source material

- `sources/primal-battle-ifrit-bowl-of-embers/objects/the_bowl_of_embers_ifrit_video_breakdown.md` - observation-only
  format (timestamped sequence, per-action damage, log-form-preserved action
  names). Its few inferences (the unread `Ifrit is defeated.` line) are flagged in
  the evidence map.
- Source video (`vidssave.com FFXIV 1.0 Ifrit fight 1080P.mp4`) is not archived.
- `sources/primal-battle-ifrit-bowl-of-embers/manifest.yaml` - source member
  SHA-256 and byte size.

## Promoted conclusions

The repository catalog promotes the client-verified Ifrit action pool and the
video-observed phase, pacing, recovery, and damage ranges as video-tier evidence.
No implementation value has been promoted from this single run.

## Topics

- ifrit
- the bowl of embers
- infernal nail
- vulcan burst / incinerate / eruption / crimson cyclone / hellfire
- siphon mp
- primal damage tuning
- video breakdown

## Evidence gaps

- No packets, actor IDs, or localized text - the client-data sheets carry the
  string side. No packet set covers Ifrit.
- Damage numbers are one mitigated four-player Lv30 run against a `??`-level
  Ifrit. The level delta is unknown.
- Entry interaction, `bound by duty` line, and the `Ifrit is defeated.` line are
  off clip. Defeat is inferred (see the evidence map).

## Further research

- Action cadence remains unresolved: the action pool is confirmed for 1.23b, but
  observed counts are lower bounds.
