# Capture Catalog

Source-of-truth registry for capture sets and the views derived from it.

## Files

- `index.yaml` is the machine-readable registry. Every set has one entry, and
  the catalog views are derived from it.
- `by-content-kind.md` is the primary view; `by-zone.md`, `by-system.md`,
  `by-progression.md`, and `by-city-state.md` are secondary views. All are
  derived from `index.yaml`.
- `integrating-new-captures.md` explains how to add new evidence, including the
  Video Breakdown Intake checklist.
- `video-breakdown-template.md` is the observation template for
  converting a retail 1.x gameplay video into an ingestible document.
Hosted CI runs the validation chain. For optional local feedback, run
`python tools/refresh.py --check`.

`index.yaml` is the authoritative list of current sets. Add a new set by
following `integrating-new-captures.md`.
