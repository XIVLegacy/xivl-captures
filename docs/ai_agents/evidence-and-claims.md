# Evidence and claims

The canonical registry is
[schemas/evidence-classes.yaml](../../schemas/evidence-classes.yaml). Its
order is packet capture > video breakdown > wiki. Archive is preservation-only
and has no evidence tier.

## Evidence classes

| Class | Tier | Meaning |
|---|---:|---|
| packet-capture | 1 | Retail packet captures (pcap corpus) and their canonical decode/digestion. |
| video-breakdown | 2 | AI breakdowns distilled from retail 1.x gameplay videos. |
| notes-and-transcripts | 2 | Freeform notes and transcripts, mapped to the video breakdown tier. |
| web-tables | 3 | Community 1.0-era web-source table transcriptions (stat growth, formulas). |
| archive | no tier | Source preservation only. It is not ranked evidence (no tier). |

The tier is a conflict rule, not a guarantee that every claim in a higher
class is correct. A lower-tier source does not become stronger because it is
more detailed. Preserve the assigned class in manifests, study notes,
derived, and catalog entries.

## What supports a claim

Start from an identified source artifact and state the narrowest claim it
directly supports. A source manifest establishes identity, provenance,
distribution, members, and evidence class. A study README, manifest, and
derived file show how findings were distilled. A dataset sidecar records the
inputs and class for a generated or promoted product. Catalog views are the
discovery layer, not independent evidence.

Repository code, tests, schemas, and docs establish this repository's storage
and regeneration contracts. They do not by themselves prove retail behavior.
Agent output, summaries, search snippets, and unattributed statements are
leads. Inspect the underlying source, study, or dataset before promoting a
fact.

Make observation, interpretation, and implementation consequence distinct.
State uncertainty when a value, name, date, region, or interpretation is not
resolved. Do not merge conflicting sources into one assertion. For packet
order questions, use the wire-order extractor and its source evidence rather
than treating derived/sequences.json as ordered wire truth.

## Ownership and boundary

The [catalog guide](../catalog-guide.md#public-and-restricted-material) owns the
distribution boundary. A source manifest establishes identity and provenance
without proving that its restricted or cold-stored object is available
locally.

Keep the finding's evidence citation and verdict here. A consumer project
promotes a durable implementation or behavior conclusion on its own side with
an immutable citation to this record.

## Numbers in prose

Every figure in authored prose has to carry its sentence's claim. Ask of each
one: is this number the finding, or is it scene-setting?

Figures that carry the claim stay verbatim. Row counts, coverage ratios, per-file byte
sizes and hashes, offsets, and extraction diffs are the claim itself - the
sentence exists to state them. Removing one destroys evidence.

Incidental figures go and the claim stays. When the sentence is about
something else, a count is throat-clearing: it tells the reader nothing they
can act on, and it invites doubt when their own run differs by one. Keep what
was found. Drop the size of the haystack.

A hedge is the strongest tell. "approximately", "roughly", "about", or a
leading "~" before a figure means the author had already decided the figure
did not matter. Make it exact or cut it. Where an exact source exists, name
that source instead of restating its number in prose.

This governs prose the repository authors. A figure inside a quoted or
transcribed source is source content and stays verbatim, hedge included.

## Citations

Facts promoted from another repository use this shape:

    repository-name:path/to/file

Within this repository, retain the stable source or study id, member filename,
SHA-256, source citation, evidence class, and recorded date. Add a row, symbol,
section, or derived-file locator when it narrows the claim. Commit hashes and
date pins are not citations: repository histories are rewritten before
publication, and dated "as of" claims rot. External sources' own revision
identifiers and observation dates (harvest, retrieval, capture dates) are
source metadata and stay verbatim. Branch names, working-tree paths, and
default sibling paths are not citations.
