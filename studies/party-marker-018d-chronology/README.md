# Party Marker 0x018D Chronology

## Study contents

This study exhaustively decodes every admitted server-to-client `0x018D`
occurrence in all 54 preserved retail captures. It publishes sanitized record
fields, capture-local identifier pseudonyms, repeated-snapshot relationships,
and bounded same-lane opcode neighborhoods.

## Start here

- `derived/accounting.json` - corpus, connection, lane, retransmission,
  exclusion, distribution, and correlation accounting.
- `derived/occurrences.csv` - one sanitized row per decoded packet.
- `derived/marker-records.csv` - one row per count-admitted marker record.
- `derived/neighborhoods.csv` - five preceding and following s2c opcode events.
- `derived/verdicts.md` - promoted chronology conclusions and claim boundary.

Regenerate or verify the products:

```text
python tools/extractors/extract_party_marker_chronology.py
python tools/extractors/extract_party_marker_chronology.py --check
```

## Source material

The packet source is `pcap-1.23b`, selected by the canonical sorted corpus
reducer and admitted by the shared clear TCP 54992 lane filter. TCP sequence
reconstruction removes retransmitted duplicate bytes before framing.

The client-read packet layout is pinned to `xivl-opcodes` commit
`fabeab871efd59bdf1098850e5053a8570b3a2ba`,
`data/client_opcode_semantics.json#s2c-018d`. The pointer lifecycle and handler
boundary are pinned to `xivl-decomp` commit
`9af4faf31d4f020ac449f7595cf0b0e0d49a0dbd`,
`docs/actor/action-queue.md#element-container-0x4d8-pointer-lifecycle`.
Regeneration is repository-local; neither sibling checkout is a runtime input.

The layout contains three leading u32 values, sixteen reserved 0x28-byte
records, a u8 count at application offset `+0x290`, and a seven-byte reserved
tail. The canonical manifests agree on the 0x28-byte stride and six-dword
transposition but conflict between `+0x0C` and `+0x20` for one position. The
study therefore decodes the evidenced union: u32 positions `+0x00`, `+0x08`,
and `+0x0C`, plus f32 positions `+0x14`, `+0x18`, `+0x1C`, and `+0x20`. It
keeps every position neutral because the capture does not establish nouns for
unknown values or coordinates.

## Promoted conclusions

The promoted conclusions are the exhaustive event and exclusion counts, count
distribution, sanitized record projection, repeated-snapshot census, bounded
opcode neighborhoods, and the absence of a consistent tested first-marker
predecessor. The concise verdict is in `derived/verdicts.md`.

The tested zone-transition set is `0x0005`, `0x0006`, `0x0007`, `0x0008`,
`0x000F`, and `0x0010`. Actor lifecycle is bounded to `0x0007`, `0x00CA`,
`0x00CB`, and `0x00CC`. Group updates are `0x0143`, `0x017A`, `0x017C` through
`0x017F`, `0x0183`, `0x0187`, and `0x018B`; `0x018B` is also counted
separately. Setup correlation tests use `0x0193` alone. The accounting file
records these sets so later regeneration cannot silently change the boundary.

## Topics

- Complete retained-corpus `0x018D` census
- Sanitized marker-record projection
- Same-lane bounded packet chronology
- Repeated packet snapshots
- Zone, group, setup, and actor-lifecycle correlations

## Evidence gaps

The corpus has no count-zero or decreasing-count event, so it provides no
empty or removal-shaped witness. The analyzer would label a decreasing count
as removal-shaped chronology only; it would not prove server intent or client
removal behavior. The study does not link any neighboring packet to selector
`0x0D` creation.
`RaptureElementContainer+0x4D8` is a nullable pointer gate, not marker data;
the pointee class and application semantics remain unresolved.

## Further research

A retail trace that directly observes selector `0x0D` creation beside packet
handling would be required to establish a creation boundary. Count-zero or
decreasing-count captures would broaden the snapshot-shape comparison without
by themselves proving server intent or client removal semantics.
