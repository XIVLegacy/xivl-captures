# Comments and prose

The repository's code and manifest comments follow the same rule: deletion is
the default. Keep a comment only when it records a current invariant, a
client or wire fact, an evidence citation, a safety constraint, or an API or
tool contract that names and types cannot show.

Compress a survivor to one line at the use site when possible. Move a longer
contract to a public documentation page, a study-derived note, or a canonical
declaration and leave a short pointer. Branch-time narration and review
scaffolding are removed before merge. When unsure, keep one line and flag the
decision in review notes.

## Repository surfaces

- In tools/ and tools/extractors/, keep comments for framing assumptions,
  packet order, extraction contracts, safety constraints, and evidence
  locators. Do not narrate the next statement or restate a function name.
- In pipelines/*.yaml, keep comments only for non-obvious inputs, outputs,
  ordering, regeneration, or safety invariants. The pipeline manifest is the
  canonical regeneration graph.
- In schemas/, keep schema descriptions and registry comments precise and
  brief. JSON Schema files do not have comments. The
  schemas/evidence-classes.yaml comments may state the tier-registry rule, not
  a second list that can drift.
- For any tracked CI workflow manifest, apply the same deletion default to
  YAML comments. Keep only a validation or release invariant that the workflow
  cannot show by itself.
- Generated catalog, scenario, axis, dataset, and sidecar output is owned by
  its generator. Change the generator or canonical input and regenerate
  instead of adding commentary to the output.

Python docstrings and command help are runtime text. Treat them as public
contracts. Tighten an inaccurate or oversized docstring, but do not delete a
docstring merely because it looks like a comment. Keep a pointer to the
symbol, file, source id, or output contract it mirrors when that pointer is
part of the interface. A docstring-only edit changes runtime documentation,
not executable behavior. Name that change in the handoff and do not claim the
exact AST is unchanged.

Preserve capture-set identifiers, hashes, source citations, evidence-class
assignments, and dates verbatim. They are not prose to shorten or normalize.
Do not put live sibling paths in comments or generated artifacts. Use a
repo-relative path and an immutable source citation where a locator is needed.

## Short examples

Keep an order-sensitive wire fact:

    # Stream order is per connection; sequences.json is a collapsed cross-stream summary.

Keep a safety invariant:

    # Leave raw objects immutable; write only to the extracted workspace.

Delete code narration:

    # Increment the index.
    index += 1

## Authored public prose

Public tier prose, meaning the README, CONTRIBUTING, the docs index, and any
page a stranger reads, uses a plain, direct register.

All tracked authored prose and structured descriptions state current evidence or
contracts. They are not prompts, assignments, review summaries, checkout state,
internal milestones, or work-session plans.

- Avoid over-hyphenation and invented compound modifiers. Established
  technical terms keep their hyphens.
- Use semicolons sparingly, preferring periods, commas, or short lists.
- Cut parenthetical asides. If the aside matters, make it a short sentence
  of its own. If it does not, delete it.
- Short declarative sentences, one idea each. A rule gets one line of
  practical justification, then stops.
- "Footgun" and "load-bearing" never ship in docs or comments. Name the
  actual hazard or dependency: "pitfall guard", "required order",
  "X relies on Y".

Internal working docs are out of scope. These rules govern the public tier.
