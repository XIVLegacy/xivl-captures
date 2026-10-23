# Test authoring

Add a test for a demonstrated defect or a distinct supported behavior or
failure. Extend an existing check first. Changed lines, including AI-authored
lines, do not by themselves justify new fixtures or scenarios.

## Choose the smallest boundary

Start with a decoder or validator over authored bytes or records. Use a
temporary tree for storage, archive extraction, and destination protection.
Invoke a child process when argument routing, exit status, or sanitized process
output is the behavior under test. Do not replay a corpus for a pure field
decode regression.

Use small helpers in the owning test module for setup. Keep distinguishing
bytes and expected values visible instead of adding a generic fixture framework.
Public fixtures must be synthetic or redistributable. Raw evidence under
`sources/*/objects/` is immutable and is never a test output destination.

## Assert an independent wire contract

- Author literal offsets, lengths, values, ordering, and refusal reasons from
  the supported contract. Do not derive expected offsets with the production
  constants or decode the expected answer with the decoder being tested.
- Keep exact-value assertions alongside round trips and deterministic output
  comparisons. Two executions can reproduce the same wrong result.
- For a planted defect, assert the intended refusal. An unrelated schema,
  digest, or missing-input error does not demonstrate the target guard.

The [battle-result tests](../../tools/tests/test_extract_battle_results.py)
place values at literal byte offsets and check sparse-array transposition and
row-count refusal. Preserve those distinctions when extending their fixtures.
Keep names, hypotheses, and decoded values within the
[evidence policy](evidence-and-claims.md).

Ordering tests must distinguish TCP sequence reconstruction, retransmission
overlap, direction, lane, and connection boundaries when relevant to the bug.
The [party-marker chronology tests](../../tools/tests/test_extract_party_marker_chronology.py)
exercise synthetic retransmission and chronology cases. The
[wire-order contract](../pcap-decoding.md#order-and-validation-limits) limits
stream order to a direction within a connection. Concatenated connection blocks
and `derived/sequences.json` do not establish capture-wide arrival chronology.

Preserve the supported decrypt and decode boundaries. The
[lane-admission tests](../../tools/tests/test_extract_streams.py) distinguish
clear game traffic from lobby traffic and TLS. The
[lobby census tests](../../tools/tests/test_extract_lobby_record_census.py)
separately protect encrypted extents, retained accounting, and sensitive-data
rejection. A synthetic passing case does not establish new decryptability.

## Separate integrity from integration

Check every relevant manifest member, sidecar, provenance pin, and product row
when data-wide integrity is the claim. Choose integrated cases by distinct
parser, source mode, ordering rule, and output path. Do not repeat a complete
pipeline per row when a direct integrity check covers that row's invariant.

Before reducing cases, map each input/mode/assertion combination that remains.
Name omitted combinations and the coverage lost through sampling. Call a
deduplication equivalent only when it preserves every distinct assertion and
failure path. Matching command names or outputs alone is insufficient.

Keep storage pin/path checks and extraction safety checks distinct. The
[source-storage tests](../../tools/tests/test_validate_source_storage.py) and
[retail PCAP tests](../../tools/test_retail_pcap.py) protect different boundaries.
Use synthetic archives and temporary roots for traversal, links, malformed
members, invalid roots, and output-preservation cases supported by the tool.
Retain sanitized-output and no-write-on-refusal assertions where applicable.

## Preserve validation claims and control cost

The [tool guide](../../tools/README.md#human-entry-points) owns refresh commands.
Public-shape checks validate retained accounting and metadata without restricted
bytes. Full refresh checks can reproduce generated products from restored
inputs. Neither mode may be reported as the other. The
[retail-input policy](retail-input-validation.md) owns the separate restricted
archive claim, grant, and sanitized output boundary.

Keep deterministic regeneration, schema checks, provenance checks, and focused
mutation tests when they establish different properties. Fixture economy does
not replace the applicable refresh gate or authorize broader private inputs.

For material growth in corpus scans, mutation products, subprocesses, or test
source, explain the cost with representative runtime, build, or source evidence.
Do not invent quotas or benchmark every small addition. Run the focused check
that detects the defect and the applicable
[repository checks](../../.github/workflows/checks.yml). Report the source mode,
private skips, and unverified claims. Prose-only changes follow the
[contribution policy](README.md#contribution-policy).
