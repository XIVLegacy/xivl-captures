# Capture Repository Tools

Canonical scripts that validate, regenerate, and mine the tracked capture
products (`catalog/`, `derived/`, `studies/`). Edit a script or its input
manifest, never a generated output by hand, then regenerate.

## Gate

The [verification policy](../docs/ai_agents/verification.md) owns local checks,
and the [checks workflow](../.github/workflows/checks.yml) is authoritative for
the CI-covered gate.

## Human entry points

The supported commands for direct maintainer use are:

- `python tools/refresh.py` - regenerate every canonical product in dependency
  order.
- `python tools/extractors/extract_wire_order.py <capture.pcapng>` - inspect
  sub-events in deterministic connection order.
- `python tools/extractors/extract_battle_results.py --client-data-repo <path>
  --field-model <path>` - regenerate the active battle-result backfit study from
  the full pcap corpus and explicit client-data/client-struct evidence inputs;
  add `--check` for a byte-for-byte replay check.
- `python tools/analyze_battle_result_distributions.py` - regenerate the
  self-contained Stage 2 distribution and matched-set products from the Stage 1
  row table; add `--check` for a byte-for-byte replay check.
- `python tools/validate_framing.py [capture.pcapng ...]` - verify the outer
  frame compression invariant.
- `python tools/promote_opcode_names.py --source <opcodes.json>` - replace the
  promoted local opcode-name snapshot from an explicit source.
- `python tools/validate_capture_repo.py --recall` - audit catalog search-hint
  recall against evidence-map anchors.

The remaining scripts below are internal pipeline components, support modules,
or focused advisory checks. `refresh.py` is their normal entry point.

## Scripts

- `_json_io.py` - shared JSON writer (2-space indent, `ensure_ascii=False`,
  LF, single trailing newline) and repo-root/derived-dir path constants used
  by the other tools.
- `analyze_payload_layouts.py` - infers per-opcode field layouts (constant,
  zero-pad, variable byte ranges) from `derived/payload_samples.json`.
- `audit_study_conventions.py` - audits study README shape, manifest/catalog
  agreement, checksums, and path hygiene not covered by
  `validate_capture_repo.py`.
- `build_catalog.py` - regenerates scenario views, `catalog/index.yaml`,
  `catalog/aliases.yaml`, and `catalog/by-*.md` in dependency order. The three
  phase modules remain internal compatibility surfaces for byte-stable output.
- `build_pcap_products.py` - regenerates or byte-checks all 12 pcap-derived
  products through one cached corpus traversal. `--product NAME` selects a
  product and its dependencies without making the reducers reopen captures.
- `build_checksums.py` - regenerates or verifies (`--check`) each study's
  `derived/` checksum anchor for studies that declare a manifest
  `checksum_file`. The anchored set is every file under `derived/`.
- `build_dataset_meta.py` - generates `derived/<name>.meta.yaml` provenance
  sidecars for every committed `derived/*.json` product.
- `check_markdown_links.py` - resolves every in-repo Markdown link target
  across `studies/`, `docs/`, `catalog/`, and top-level `*.md`; fails on any
  that dangles. Skips web links and intentional sibling-repo references.
- `name_gam_hashes.py` - emits the packet-observed property hashes without
  external name assertions.
- `promote_opcode_names.py` - promotes the identification layer of an
  external opcode catalog snapshot into the local
  `derived/opcode_names.json`.
- `refresh.py` - the unified gate over every canonical product. See Gate
  above.
- `soften_source_links.py` - retains study citation paths as plain text when
  their raw source objects are excluded from the public tree.
- `validate_capture_repo.py` - validates retention and taxonomy policy across
  `sources/`, `studies/`, `catalog/scenarios/`, and `derived/`.
- `validate_digestion.py` - referential-integrity gate for the canonical pcap
  digestion (`derived/observations.json` cross-references).
- `validate_framing.py` - validates the 1.23b outer-frame model (the
  compression-flag invariant) across one or more pcap captures.
- `validate_schemas.py` - JSON-Schema validation plus cross-file referential
  checks for `schemas/`, `sources/`, `derived/`, `pipelines/`, `studies/`.
- `requirements.txt` - third-party Python dependencies (scapy, jsonschema,
  PyYAML). Most tools use only the standard library.
- `ffxiv-action-names.txt` - hand-seeded action-surface name list consulted
  by `validate_capture_repo.py`'s `--recall` pass so action names are not
  flagged as missing search hints.

## extractors/

Pure-Python pcap decoders and miners with no server-runtime dependency. Except
for the `extract_wire_order.py` diagnostic named above, these are internal
reducers invoked by `build_pcap_products.py`, not separate human entry points.
Most take `--out` and write one `derived/*.json` product. Several also take
explicit capture paths and default to a priority set when none are given.

- `extract_content_samples.py` - decodes inventory-list and event-start
  packet bodies into ground-truth game-state samples.
- `extract_gam_keys.py` - extracts SetActorProperty GAM property key hashes
  and per-key stats from the corpus.
- `extract_observations.py` - the opcode/length observation extractor. It
  produces `derived/observations.json` and `derived/lane_observations.json`.
- `extract_payload_samples.py` - samples raw payload bytes per opcode into
  `derived/payload_samples.json`.
- `extract_property_targets.py` - captures the per-target prefix each
  SetActorProperty property id appears under in the wire stream.
- `extract_request_response_pairs.py` - correlates c2s opcodes with the s2c
  opcodes that follow within a reply-time window.
- `extract_sequences.py` - builds per-capture opcode sequences and finds
  cross-capture motifs.
- `extract_spawn_observations.py` - extracts observed actor spawn positions
  from the pcap corpus.
- `extract_streams.py` - reconstructs per-direction TCP streams from a pcap
  and parses outer frames.
- `extract_timing.py` - computes per-opcode inter-emission timing statistics
  from outer-frame timestamps.
- `extract_wire_order.py` - prints sub-events in stream order within each
  deterministic connection block. It does not recover capture-wide chronology.
  `derived/sequences.json` also merges directions and collapses runs.
