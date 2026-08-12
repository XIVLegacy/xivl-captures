# Integrating New Captures

This guide is the standard process for adding a video breakdown to
`xivl-captures`. A video breakdown is an observation document based on a
retail 1.x gameplay video and the [`video-breakdown-template.md`](video-breakdown-template.md).
It distills what packets never carry: damage magnitudes, heal amounts,
timing/pacing, and visual
state.

## Goal

Each new breakdown receives a stable id, with the raw document preserved under
`sources/<id>/`, a compact evidence-map packet under `studies/<id>/`, and a
recorded evidence verdict that a consumer project can promote on its own side
with an immutable citation.

## Quick Version

1. Complete the breakdown document using the guidance in
   `video-breakdown-template.md`.
2. Decide whether to reuse an existing id or create a new one:
   `<content_kind>-<short-name>-video-breakdown`.
3. Place the document under `sources/<id>/objects/` with its filename
   unchanged (or record its cold-storage / local-only location in the
   manifest if it is not kept in-repo).
4. Build the distilled evidence packet in `studies/<id>/derived/` -
   `evidence-map.md` alone.
5. Add or update `sources/<id>/manifest.yaml`.
6. Add or update `studies/<id>/manifest.yaml` and `studies/<id>/README.md`.
7. Run `python tools/refresh.py` to regenerate `catalog/index.yaml`,
   `catalog/aliases.yaml`, the scenario views, and the axis views
   (`by-content-kind.md`, `by-zone.md`, `by-system.md`, `by-progression.md`,
   `by-city-state.md`) so the new entry appears everywhere.
8. Run the verification checklist below before marking the study
   `distilled`, and record the verdicts in `studies/<id>/derived/evidence-map.md`.
9. Record the evidence id, exact source or study path, and verdict here. A
   consumer project promotes conclusions on its own side with an immutable
   citation.
10. Optionally run `python tools/refresh.py --check` for local feedback; hosted
    CI enforces the validation chain on the pull request.

## Step 1: Land The Document

- The breakdown document itself is the raw original: place it under
  `sources/<id>/objects/` with its filename unchanged, and never edit it.
- The source video is normally NOT archived - record its title/filename or
  URL in the source manifest `notes`. If the video file is held, the normal
  `>25 MB` cold-storage rule applies to it.
- A video breakdown is a single Markdown file and is never extracted.

## Step 2: Choose The Right Id

Reuse an existing id when the new document is more evidence for the same
content or investigation and the same `studies/<id>/README.md` and
`sources/<id>/manifest.yaml` would still describe the combined material
accurately.

Create a new id when the document covers different content, a different
system, or a different reverse-engineering thread, or when combining it with
existing material would make the evidence harder to understand or search.

## Step 3: Pick An Id

Use lowercase kebab-case. Prefer the content name over a vague label. The same
id names both halves of an evidence bundle: `sources/<id>/` (the original) and
`studies/<id>/` (the distillation). Video breakdowns use
`<content_kind>-<short-name>-video-breakdown`.

Good examples:

- `primal-battle-ifrit-bowl-of-embers-video-breakdown`
- `behest-camp-bearded-rock-lower-la-noscea-video-breakdown`
- `hamlet-defense-aleport-wave-structure-video-breakdown`

Rules:

- prefer the content or fight name over a label like `misc`
- keep it stable once created
- one id per evidence bundle, not per file
- 48-char ceiling on the id itself; 180-char ceiling on any git-tracked path
  under it (both enforced by `tools/validate_schemas.py`)

## Step 4: Update `sources/<id>/manifest.yaml`

Every source needs `sources/<id>/manifest.yaml`, validated against
`schemas/source.schema.json`.

Required fields:

- `id`
- `title`
- `evidence_class` - `notes-and-transcripts` for a video breakdown
- `distribution` - `public`, `restricted`, or `local-only`
- `storage` - `original_state`, `storage_id`, `path` (see the retention
  vocabulary in Step 10)
- `provenance` - free-form, but always record where the original came from
  (the source video's title/filename or URL)
- `members` - one entry per file under `objects/` (`file`, `sha256`,
  `size_bytes`); empty when the source has no in-repo `objects/` (local-only
  or cold-stored)

The public/private boundary rule (enforced by `tools/validate_schemas.py`):
`distribution: local-only` implies empty `members` and no `objects/` dir;
`storage.original_state: cold-stored` implies no `objects/` dir either. Nothing
may sit loose in `sources/<id>/` outside `objects/` and `manifest.yaml`.

## Step 5: Update `studies/<id>/manifest.yaml`

Every study needs `studies/<id>/manifest.yaml`, validated against
`schemas/study.schema.json`.

Required fields:

- `id`, `title`, `evidence_class`, `status` (usually `indexed`, `distilled`, or
  `validated`)
- `source_refs` - list of `{source: <id>}`, one entry per source the study
  distills (usually just the study's own paired source)
- `primary_paths` - the first places to open

Include a `video-breakdown` tag on the study manifest.

Optional facet fields (validated only when present; see
`tools/validate_capture_repo.py`):

- `content_kind` - what kind of 1.x content the study covers. The canonical
  list is `VALID_CONTENT_KINDS` in `tools/validate_capture_repo.py`.
- `system` - cross-cutting 1.x system (`guildleve`, `behest`, `grand-company`,
  `battle-regimen`, `aetheryte-travel`, `hamlet-defense`, `instanced-content`,
  `materia`, `surplus-fatigue`).
- `city_state` - when city-scoped: `limsa-lominsa | gridania | uldah`.
- `grand_company` - when Grand Company-scoped: `maelstrom | twin-adder |
  immortal-flames`. (Allegiance maps 1:1 to city-state.)
- `progression_track` - single primary track (`class-rank | physical-level |
  class-quest | job-quest | artifact-gear | grand-company-rank`).
- `zones` - list, soft cap of 3 primary zones. Use the canonical 1.0 human
  names. Additional incidental zones go in `search_hints`.
- `tags` - free-form mechanic tags. Examples: `video-breakdown`,
  `damage-tuning`, `dialog`, `mob-skill-list`, `entry-rules`.
- `search_hints`, `related_implementation_docs`, `notes`

There is intentionally no `expansion` field - 1.23b is a single-version target,
so there is no expansion or patch axis (record a patch as a `patch-*` tag if it
ever matters).

Picking the `content_kind` when several seem to fit: **the kind is the delivery
mechanism / instance type; the activity, the NM-ness, and the leve scope go in
`tags`; most-specific kind wins.** Concretely:

- A fight issued by a levemete is a `*-leve` (by discipline), even if the
  objective is to kill a named monster or perform a synthesis - the monster or
  craft is a tag, not the kind. (An "Official Behest" is itself a guildleve in the
  data, but capture it as `behest`: the open-world timed-wave delivery is the
  specific kind.)
- A named rare monster fought in the open world is `notorious-monster`; the same
  monster reached through a leve or behest files under that leve/behest kind with
  a `notorious-monster` tag.
- `hamlet-defense` covers the instanced Battle for Aleport / Hyrstmill / the
  Golden Bazaar - do not also reach for a generic "defense" kind.
- `npc-interaction` is the fallback only when no `shop-vendor`, `*-quest`,
  `aetheryte-mechanic`, or other specific kind applies.

## Step 6: Update The Study `README.md`

Every study needs `studies/<id>/README.md` with this section shape:

- `## Study contents`
- `## Start here`
- `## Source material`
- `## Promoted conclusions`
- `## Topics`
- `## Evidence gaps`
- `## Further research`

This is the repository-wide study contract, not a video-breakdown-only
convention. New studies must conform; migration of existing studies is handled
separately from intake.

This is the human-friendly entry point. Keep it short, current, and
skimmable. Further research records unresolved evidence questions.

## Step 7: Build The Distilled Evidence Packet

The distilled packet is just `studies/<id>/derived/evidence-map.md` - the raw
document is already hash-covered by `sources/<id>/manifest.yaml` members, so
no `checksums.sha256` is needed. No `timeline.md` (the document carries its
own timestamps) and no `file-inventory.csv` (single file, never extracted).

Use `derived/evidence-map.md` to list the highest-value evidence, anchors, and
known gaps.

## Step 8: Regenerate The Catalog

Run `python tools/refresh.py`. Its internal `tools/build_catalog.py` stage
rewrites `catalog/index.yaml` and `catalog/aliases.yaml` entirely from every
`sources/*/manifest.yaml`, `studies/*/manifest.yaml`, and
`sources/pcap-1.23b/manifest.yaml`'s `scenarios:`, then rewrites the
`by-*.md` axis views from the refreshed index. There is no hand-edited
section - never edit `catalog/index.yaml`, `catalog/aliases.yaml`, or a
`by-*.md` file directly.

Catalog rules:

- list the stable id
- include `content_kind` plus any applicable facets (`system`, `city_state`,
  `grand_company`, `progression_track`, `zones`, `tags`) on the study manifest
- make sure every `primary_paths` entry actually exists
- keep the search hints concrete enough for future searches

## Step 9: Record The Consumer Citation

Record the stable id, exact repo-relative source or study path, and evidence
verdict here. A consumer project promotes an implementation conclusion on its
own side with an immutable citation to this record.

## Step 10: Apply Retention And Verify

Retention vocabulary (`storage.storage_id` in `sources/<id>/manifest.yaml`):

- `repo` - the original is a plain in-repo file under `sources/<id>/objects/`,
  not Git-LFS-tracked (the normal case for a Markdown breakdown document).
- `repo-lfs` - the original is an actual Git LFS object under
  `sources/<id>/objects/`, tracked by one of the patterns in `.gitattributes`
  (`*.zip`, `*.rar`, `*.7z`, `*.mp4`, `*.mkv`). Do not use this id for a file
  that merely has one of those extensions but isn't actually LFS-tracked -
  check `.gitattributes` covers the path.
- a cold id (for example `local-cold-storage`) - the original lives in the
  gitignored `archives/<id>/` folder at the repo root; `storage.path` records
  the archive-relative location. Configured in `config/cold-storage.example.yaml`
  / `config/cold-storage.local.yaml`.

Original retention rule:

- keep compressed originals in Git (plain or LFS per the vocabulary above)
  when each file is `<=25 MB`
- move larger originals to the gitignored `archives/<id>/` folder at the repo
  root, then update `sources/<id>/manifest.yaml` (`storage.original_state:
  cold-stored`, `storage.storage_id: local-cold-storage`,
  `storage.path: archives/<id>/<file>.<ext>`) and remove them from `objects/`
  entirely (the public/private boundary check fails if `objects/` still
  exists alongside cold-stored storage)
- override `archives/` to a separate drive via `config/cold-storage.local.yaml`
  if needed; the default is repo-relative

Verification checklist:

- the evidence has both `studies/<id>/README.md` and `sources/<id>/manifest.yaml`
- every path in `sources/<id>/manifest.yaml` and `studies/<id>/manifest.yaml`
  exists
- every path listed in `catalog/index.yaml` exists
- the raw document is under `sources/<id>/objects/`, or the manifest correctly
  records its local-only / cold-stored location
- the distilled packet exists for every `distilled` or `validated` study
- the evidence map records the stable id, exact source or study path, and verdict
- `python tools/refresh.py --check` passes

## Video Breakdown Intake

A video breakdown is a distinct evidence class with its own tier rule:

**Packet captures > video breakdown > wiki.** Where a breakdown disagrees with a
packet source (`xivl-opcodes`), the packets win. Where it disagrees with the
decoded client data (`xivl-client-data`), the client data wins. A breakdown's
unique value is what packets never carry: damage magnitudes, heal amounts,
timing/pacing, and visual state.

In this repo, the pcap corpus covers a fixed set of scenario families, so a
breakdown's content often has no packet counterpart. So in practice the
verification that actually runs is step 1 (dialogue vs the client strings)
and the client-data half of step 2; the packet diff is a bonus for the
uncommon case where a matching `xivl-opcodes` capture is on hand. The
decoded client data is the everyday source of truth here.

Run this checklist at intake, BEFORE marking the study `distilled`, and record
the verdicts in `studies/<id>/derived/evidence-map.md`:

1. **Dialogue:** check every quoted NPC/enemy line against the decoded client
   strings in `xivl-client-data` - `worldMaster.csv` for system/combat-log
   lines and the `xtx_*` dialogue tables for the zone/NPC. A line that does not
   match (allowing for the player-name token) is unsupported or misread - flag
   it. The 1.x client renders dialogue from these tables, so they are the
   authoritative text.
2. **Action names:** the breakdown should preserve the log verb that tells action
   types apart - `begins casting X` (magic) vs `readies X` (weaponskill /
   ability / TP move). Cross-check every action name against
   `xivl-client-data/csv/xtx_command.csv` (the localized command-name strings;
   the numeric `command.csv` sheet carries the action data but not the display
   names); a name with no row is misread or ARR-era. If a `xivl-opcodes` packet
   capture exists for the same content, diff the breakdown's action names against
   it - "begins casting X" vs "readies X" confusions and ARR-name substitutions
   are the most common errors. Grade a claim contradicted only when packet
   evidence positively conflicts (the same logged moment shows a different
   action); absence from a single packet run downgrades the claim to
   video-observed/packet-unsampled, not contradicted - a packet run samples a
   mob's pool, it does not exhaust it.
3. **Counts and attribution:** check observed-tier repetition counts and
   dialogue-to-action pairings against packet/client timelines. Wiki (usually
   ARR-era) contamination shows up here - "uses it multiple times" when every
   capture shows one, or an ARR cadence/number presented as observed.
4. **Version sanity:** confirm the footage is 1.x at all. The breakdown's
   Uncertainties section should flag any doubt; if the HUD, action bar, or zone
   names look ARR, treat the whole document as suspect until the version is
   settled.
5. Structure the evidence map as: confirmed / contradicted (with severity) /
   unverifiable / unique value / gaps. Contradicted claims stay in the raw
   document untouched - the evidence map is the filter every later reader goes
   through first.

Record observations and their evidence verdicts here, not design decisions
suggested by the breakdown. A consumer project settles tuning, thresholds, and
deviations on its own side while citing this record immutably.

## Template Snippets

### New Source + Study Folder Layout

```text
sources/<id>/
  manifest.yaml
  objects/

studies/<id>/
  README.md
  manifest.yaml
  derived/
```

### New Source Manifest Skeleton

```yaml
id: <id>
title: <Human Title>
evidence_class: notes-and-transcripts
distribution: <public|restricted|local-only>
provenance:
  sources: []
storage:
  original_state: in-repo
  storage_id: repo
  path: objects/
members: []
```

### New Study Manifest Skeleton

```yaml
id: <id>
title: <Human Title>
evidence_class: notes-and-transcripts
status: indexed
content_kind: <one of VALID_CONTENT_KINDS; see tools/validate_capture_repo.py>
source_refs:
- source: <id>
primary_paths:
- derived/evidence-map.md
tags:
- video-breakdown
related_implementation_docs: []
search_hints:
- <term>
```

Optional facets (`system`, `city_state`, `grand_company`, `progression_track`,
`zones`) go on the study manifest alongside `content_kind`.

## Retention and consumer guidance

- Raw evidence under `sources/<id>/objects/` is immutable.
- Derived notes belong in `studies/<id>/derived/`; cross-topic notes belong in
  `docs/`.
- Large originals belong in cold storage after distillation.
- Downstream consumers promote durable conclusions on their own side with
  immutable citations to this repo's evidence ids and verdicts.
