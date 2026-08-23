# Contributing

XIVLegacy Captures accepts focused pull requests against `main`. Contributions
are licensed under the repository licenses that cover the changed material.

## Before contributing

Follow the [public and restricted material](docs/catalog-guide.md#public-and-restricted-material)
boundary when selecting inputs and outputs. Manifests may cite restricted
files that are not present in your checkout.

Hosted CI detects the missing corpus and runs validation in public-shape mode.
Checks that require raw evidence are skipped instead of failed. Public
contributions should add derived analysis and study material, not new raw
captures.

Do not submit retail client binaries or assets, packet captures, decompiler
project files, credentials, or personal data of any kind. Published
observations must not contain player names or chat text; those fields are
stripped from published datasets and must stay stripped.

AI-assisted contributions are welcome, but the contributor owns the result. A
contributor who cannot explain their diff and evidence in detail
should not open a pull request.

## Code and documentation

The policy pages under `docs/ai_agents/` are authoritative:

- [Contribution and documentation policy](docs/ai_agents/README.md)
- [Evidence and claims](docs/ai_agents/evidence-and-claims.md)
- [Comments and prose](docs/ai_agents/comments-and-prose.md)

Edit canonical manifests, sidecars, pipeline declarations, or tools rather
than generated catalog and dataset outputs. Regenerate affected products from
their owning inputs.

Every change to a study, derived dataset, or catalog entry must cite evidence
by stable id: a study or scenario id, the capture set, or the derived artifact.
State the citation in the artifact that relies on it. Pull request prose alone
is not a durable evidence record.
The [evidence and claims guide](docs/ai_agents/evidence-and-claims.md) is the
authority for this rule.

## Pull requests

Fork the repository and open a pull request onto `main`. Keep each pull request
small and focused on one study, dataset, documentation batch, or tool change.
Use a draft pull request for work in progress.

CI must be green before merge. Describe the stable evidence ids and changed
artifacts a reviewer needs. Commit subjects are one
line and 50 characters or fewer, with no body, trailers, or attribution lines.

## Issues and community

Join the [project Discord](https://discord.gg/PxK5RJYQjm) for questions,
research discussion, and community support. Use the
[issue tracker](https://github.com/XIVLegacy/xivl-captures/issues) for durable
corrections and reverse-engineering findings.

Include stable ids, reproduction steps, and supporting evidence in reports.

Report suspected security problems through private vulnerability reporting
under the repository Security tab. Do not open a public security issue.
