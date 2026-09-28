# Map 0x00DA and 0x00E1 Wire Comparison

## Study contents

This study compares every admitted `0x00DA`, `0x00E0`, and `0x00E1`
occurrence across all 54 retained retail captures. It records exact bytes,
numeric words, transport actor identifiers, capture and outer-frame timing,
and a three-event window on either side without merging connections or
directions.

## Start here

- `derived/verdicts.md` - bounded comparative conclusions.
- `derived/occurrences.csv` - one row for every observed target opcode.
- `derived/neighborhoods.csv` - connection-direction-local context around
  each occurrence.
- `derived/accounting.json` - corpus reconciliation, exact distributions,
  per-capture identities, and limitations.

Regenerate or verify the canonical products:

```text
python tools/extractors/extract_00da_00e1_comparison.py
python tools/extractors/extract_00da_00e1_comparison.py --check
```

## Source material

The sole runtime source is the `pcap-1.23b` set: 54 canonical retail captures
selected by `default_corpus_paths()`. The extractor uses the shared clear-game
lane reducer, which admits reconstructed TCP 54992 lanes and excludes TLS,
lobby traffic, non-game connections, and retransmitted duplicate bytes.

The map/clientbound classification is independently recorded at
`xivl-opcodes:opcodes.json`. That catalog retains the numeric placeholder for
`0x00DA`; this study does not import the implementation-derived packet noun
attached to `0x00E1`.

## Promoted conclusions

The promoted conclusions are limited to the exact census, payload-shape
differences, numeric equality relationships, and direction-local chronology in
`derived/verdicts.md`. No filename is used to assign meaning to an occurrence.

## Topics

- Full retained-corpus opcode census
- Numeric payload and actor-ID comparison
- Same-connection bounded chronology
- Explicit complete-corpus negative evidence

## Evidence boundary

Capture timestamps identify the earliest captured packet that completes each
reconstructed outer frame. The raw outer 8-byte value remains separate and is
not promoted as wall-clock time. Events within one outer frame are ordered by
sub-event offset and share the frame timestamp.

The application body is retained as uninterpreted bytes plus little-endian
word projections. Equality between a word and an actor identifier is reported
only as a numeric relation. Adjacency does not establish causality.

## Evidence gaps

The corpus does not establish semantic field names for the application words,
a packet noun for either family member, or the reason `0x00E0` is absent. A
complete-corpus negative establishes only non-observation in these retained
inputs.

## Further research

A new retail capture containing `0x00E0` would be required for a three-way
payload comparison. Independent static client structure may name fields, but
those names must remain separate from what the packet bytes alone prove.

## Verification

The unified repository checks reproduce all study artifacts. Focused tests
reject incomplete frame witnesses, prevent chronology from crossing a
connection or direction, and mutation-check little-endian word projection.
