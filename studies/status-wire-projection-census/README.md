# Status Wire Projection Census

## Study contents

This study exhaustively decodes every admitted server-to-client `0x0179`
occurrence in all 54 preserved retail captures. It joins each nonzero wire
status identifier to the supported retail status row and publishes the five
numeric reader projections without assigning meanings to their values.

## Start here

- `derived/accounting.json` - full corpus, lane, exclusion, distribution, and
  per-capture chronology accounting.
- `derived/occurrences.csv` - one sanitized row per decoded packet.
- `derived/status-projections.csv` - unique observed wire IDs joined to status
  rows, complete-row names, reverse encodings, and numeric projections.
- `derived/verdicts.md` - promoted conclusions and rejected interpretations.

Regenerate or verify the products:

```text
python tools/extractors/extract_status_wire_census.py
python tools/extractors/extract_status_wire_census.py --check
```

## Source material

The packet source is `pcap-1.23b`, selected by the canonical sorted corpus
reducer and admitted by the shared clear TCP 54992 lane filter. TCP sequence
reconstruction removes retransmitted duplicate bytes before framing.

The proven packet shape and native lookup are recorded in
[client opcode semantics](https://github.com/XIVLegacy/xivl-opcodes/blob/e1166d508d07eaa7f9bc17c3328f957f2de396cb/data/client_opcode_semantics.json)
under `s2c-0179`. The status-row join is pinned to the immutable
[substat crosswalk](https://github.com/XIVLegacy/xivl-client-data/blob/438bfd6f4a28bd940a25745dc2d64bd9be4a38c7/derived/substat_status_crosswalk.csv).
Its source sheet is the restricted `csv/xtx_status.csv`; the minimal
study-owned snapshot under `inputs/` makes regeneration repository-local.

The native translation is `row = 200000 + wire - adjustment`, where adjustment
is `0x4350` only when `wire > 0x8000`. A row can therefore have overlapping low
and high reverse encodings. The output retains every valid encoding and does
not select a preferred one.

## Promoted conclusions

The promoted conclusions are the exhaustive event and exclusion counts, the
three observed wire-to-row joins, the five numeric projections, their bounded
distributions, and the per-capture reconstructed chronology. The concise
verdict is in `derived/verdicts.md`.

## Topics

- Complete retained-corpus `0x0179` census
- Retail wire-to-status-row translation
- Overlapping numeric bit projections
- Sanitized per-capture chronology and actor equality

## Claim boundary

Status names label complete status rows, never individual nibble values. Actor
identifiers are replaced with capture-local pseudonyms; names, endpoints,
timestamps, tokens, raw payloads, and raw actor IDs are absent. Event order is
the reconstructed server-to-client order within admitted lanes. It does not
establish causality, action meaning, or server policy.

The study does not import historical chant labels, wiki terminology, or packet
meanings. A repeated status row is still one independent status-word sample;
event repetition does not create additional nibble witnesses.

## Evidence gaps

The observed rows vary in bits 8..11 but not in the requested upper bit
projections. No high reverse wire encoding appears in the corpus. Chronology
does not identify why a status row was sent.

## Further research

Additional retail packets containing status rows with different upper bits
would broaden those projections. A directly observed high reverse encoding
would be required to compare use of the two native encoding branches.

## Verification

Repository validation reproduces the four derived products and validates the
study checksum and schemas, and runs focused mutation tests for translation,
bit projections, reverse-encoding ambiguity, retransmission overlap, and
malformed packet exclusion.
