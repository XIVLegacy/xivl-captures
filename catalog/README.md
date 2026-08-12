# Capture Catalog

Source-of-truth registry for capture sets and the views derived from it.

## Files

- `index.yaml` is the machine-readable registry. Every set has one entry. Tools
  and agents read this first.
- `by-content-kind.md` is the primary view; `by-zone.md`, `by-system.md`,
  `by-progression.md`, and `by-city-state.md` are secondary views. All are
  derived from `index.yaml`.
- `integrating-new-captures.md` documents the standard process for adding new
  evidence, including the Video Breakdown Intake checklist.
- `video-breakdown-handoff.md` is the prompt a contributor gives a
  video analysis agent to turn a retail 1.x gameplay video into an ingestable
  observation document.

Hosted CI runs the validation chain. For optional local feedback, run
`python tools/refresh.py --check`.

`index.yaml` is the authoritative list of current sets. Add a new set by
following `integrating-new-captures.md`.
