# Style guide

Repository style covers authored Python, manifests, derived tables, and
documentation. It does not establish packet semantics, evidence strength,
schema meaning, or capture provenance.

## General

- Prefer existing local patterns once they exist.
- Keep changes scoped to the study, catalog, or tool being changed.
- Use small, explicit functions and modules before adding abstractions.
- Follow the [comment policy](ai_agents/comments-and-prose.md) for source
  comments.
- Do not reformat immutable inputs or generated products for style alone.

### Documentation

The public [documentation policy](ai_agents/README.md#documentation-policy) is
canonical for authored documentation. The
[evidence policy](ai_agents/evidence-and-claims.md) owns claim wording,
citations, confidence, and provenance.

## Python

- Use 4 spaces for indentation and no tabs.
- Use `lower_snake_case` for modules, functions, and variables,
  `UpperCamelCase` for classes, and `UPPER_SNAKE_CASE` for constants.
- Group imports as standard library, third-party packages, then local modules.
- Prefer `pathlib.Path` for filesystem paths and explicit text encodings.
- Keep command entry points thin; put reusable work in importable functions.
- Raise or report specific failures. Do not hide malformed evidence behind
  broad exception handlers.
- Add type annotations where they clarify record shapes, path boundaries, or
  public helper contracts.

## Structured data

- Preserve schema-defined names, field order, identifiers, and null behavior.
- Edit canonical manifests and pipeline inputs, then regenerate owned output.
- Preserve the local indentation and ordering of hand-authored JSON and YAML.
- Keep CSV headers stable and use the owning writer for mechanical rewrites.
- Do not rename captured or source-defined values to satisfy code style.

## Verification

Use the owning commands in [tools/README.md](../tools/README.md). Formatting is
not a substitute for schema, catalog, privacy, or evidence validation.
