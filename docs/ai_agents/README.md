# AI-agent policy

Contributions to xivl-captures follow the same repository contract whether
the contributor is a human or an agent. The contributor owns the change and
must be able to explain its evidence, scope, and verification.

This repository records retail-observation evidence. Agent output, summaries,
search results, and uncited notes are leads, not evidence. Start with the
[public docs index](../README.md), the [catalog
guide](../catalog-guide.md), and the [catalog registry](../../catalog/index.yaml).

## Contribution policy

- Do not edit raw evidence under sources/*/objects/. Extraction for browsing
  happens outside the repo. Distill findings into the relevant study bundle.
- Start an evidence change from catalog/index.yaml, the source manifest, and
  the target study README and manifest.
- Keep one stable id across the sources/<id>/ and studies/<id>/ halves.
  Preserve original filenames, source identifiers, hashes, citations, dates,
  and evidence-class assignments verbatim.
- Treat catalog/index.yaml, catalog/aliases.yaml, catalog/scenarios/,
  catalog/by-*.md, and derived/ as generated or derived products. Edit their
  owning manifest, sidecar, or tool and regenerate them.
- catalog/integrating-new-captures.md and
  catalog/video-breakdown-handoff.md are hand-authored contribution contracts.
- Keep numeric products self-contained. Do not add a sibling checkout,
  workspace path, or freshness dependency to a canonical tool or gate.
- A documentation or comment change must not alter executable behavior.
  Python docstrings and command help are runtime prose. Change them only to
  correct their public contract, and report the text change explicitly. Hosted
  CI runs the repository gate for every pull request. Local runs are optional
  feedback, including for prose-only changes.
- Use a single commit subject of <=50 chars with no parentheses or
  co-authored trailer.
- Do not push unless the user explicitly asks.

## Documentation policy

Public consumer and policy pages under docs/ describe the current contract in
a human voice. Do not add progress reports, branch state, migration diaries,
agent narration, or unresolved working notes there. Use ASCII punctuation and
short paragraphs. Keep inventories in manifests, schemas, and catalog views
instead of copying them into prose.

Study bundles are evidence records. Their manifest status, source provenance,
evidence gaps, contradictions, and further-research needs remain tracked until
the evidence resolves them.

The [comments and prose doctrine](comments-and-prose.md) is canonical for
comments in tools, extractors, pipelines, schemas, and tracked workflow
manifests. The [evidence and claims guide](evidence-and-claims.md) is
canonical for citations and uncertainty. The [verification guide](verification.md)
is canonical for the refresh gate and its limits.

## Tracked policy docs

docs/ai_agents/ is the tracked public policy tier. It contains only policy
pages that have a subject in this repository. Do not add queues, prompts,
working notes, or re-entry material to tracked docs.

When a local note becomes citation-grade evidence, promote it into the
relevant studies/<id>/ bundle or the appropriate public catalog guide. Keep
its source identifiers, hashes, citations, dates, and evidence class intact.
Remove superseded process notes from the public tree.

## Index contract

docs/README.md lists every tracked docs page, including every page in this
policy tier. This README lists every sibling policy page. Every listed target
must exist, and every new or removed page must update the relevant index in
the same change. Do not keep an empty policy shell for a surface this
repository does not have.

## Policy shelf

| Question | Page |
|---|---|
| Public docs entry point | [docs/README.md](../README.md) |
| Catalog consumer page | [docs/catalog-guide.md](../catalog-guide.md) |
| Evidence classes and claims | [evidence-and-claims.md](evidence-and-claims.md) |
| Comments and prose | [comments-and-prose.md](comments-and-prose.md) |
| Verification and the repo gate | [verification.md](verification.md) |
