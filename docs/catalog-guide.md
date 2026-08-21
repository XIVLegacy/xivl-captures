# Catalog and Evidence

This page is the public consumer map for the evidence layers in
`xivl-captures`. It explains where to discover a finding, which evidence
class supports it, and which tree owns the durable artifact.

## Discovery layer

- `catalog/index.yaml` is the generated machine-readable registry for sources,
  studies, pcap scenarios, and derived.
- `catalog/aliases.yaml` resolves stable ids and pre-reshape path prefixes to
  their current public homes.
- `catalog/by-content-kind.md`, `catalog/by-zone.md`, `catalog/by-system.md`,
  `catalog/by-progression.md`, and `catalog/by-city-state.md` are generated
  axis views for browsing the registry.
- `catalog/scenarios/<id>/` contains the generated pcap scenario views. These
  views join the local numeric observations with the promoted opcode-name
  snapshot while keeping the scenario ids stable.
- [`docs/pcap-decoding.md`](pcap-decoding.md) explains how to interpret the
  packet framing, lane products, nested event fields, and stream-order limits.

The catalog is a discovery and projection layer. Source and study manifests,
dataset sidecars, and pipeline declarations remain the authoritative inputs for
the generated views.

## Evidence classes and tier

`schemas/evidence-classes.yaml` is the canonical evidence-class registry,
ranked packet captures > video breakdowns > wiki. See
[docs/ai_agents/evidence-and-claims.md](ai_agents/evidence-and-claims.md) for
the full class table and the tier rule.

## Ownership of the evidence layers

- `sources/<id>/manifest.yaml` owns source identity, provenance, storage,
  evidence class, and member hashes. `sources/<id>/objects/` holds original
  files only when retention policy permits them; the `pcap-1.23b` manifest
  instead names its restricted private archive as canonical and treats local
  objects and archives as caches.
- `studies/<id>/manifest.yaml`, `README.md`, and `derived/` own the distilled
  analysis for a source or a cross-source investigation.
- `derived/*.json` and their `*.meta.yaml` sidecars own canonical decoded or
  digested products. Sidecars record inputs, generator identity, output hashes,
  and evidence class.
- `pipelines/*.yaml` own the declarative regeneration graph. Generator code
  remains under `tools/` and `tools/extractors/`.

`schemas/` validates the structured contracts, while `catalog/` publishes the
generated discovery views. Neither replaces the source, study, dataset, or
pipeline that it describes.

## Public and restricted material

The restricted boundary is `sources/*/objects/`, `archives/`, and the named
private retail-input repository. These trees contain original or cold-stored
material that may be licensed, local-only, or otherwise unsuitable for the
public surface.

The public surface is the manifests, member and output hashes, `studies/`,
`derived/`, `pipelines/`, `schemas/`, and `catalog/`. Public checkouts retain
the ids, manifests, hashes, and derived findings that describe restricted
objects.
