# Map 0x018F/0x0190/0x0191 Transaction Census

## Study contents

This study exhaustively scans the complete canonical 54-capture corpus and all
84 admitted clear game lanes for server-to-client `0x018F`, `0x0190`, and
`0x0191`. It reconstructs transaction candidates only inside one lane and
increasing wrapped-event order.

## Start here

- `derived/accounting.json` - complete event, span, key, vector, tail,
  repetition, context, exclusion, and per-capture accounting.
- `derived/spans.csv` - one sanitized locator row per complete transaction.
- `derived/verdicts.md` - promoted observations and interpretation limits.

Regenerate or byte-check all three products:

```text
python tools/extractors/extract_0190_transaction_census.py
python tools/extractors/extract_0190_transaction_census.py --check
```

## Source material

The source is the canonical `pcap-1.23b` corpus selected by the shared sorted
corpus reducer and admitted by the clear TCP 54992 lane filter. TCP sequence
reconstruction removes retransmitted bytes before outer-frame and subevent
parsing. The study separately counts exact repeated admitted TCP segments so
transport repetition remains distinct from repeated decoded events.

The established application layouts are an 8-byte area for `0x018F`, a
104-byte area for `0x0190`, and an 8-byte area for `0x0191`. The `0x0190`
layout is two leading dwords, sixteen record dwords, and a 32-byte unread tail.
No semantic names are assigned to those fields.

## Promoted conclusions

The corpus contains 28 `0x018F`, 5,569 `0x0190`, and 28 `0x0191` events. They
form 28 complete same-lane spans with 197 through 200 records each. There are
no malformed shapes, nested begins, orphan records, orphan ends, or
unterminated spans. Every admitted `0x018F` and `0x0191` application area is
zero.

The first `0x0190` key dword has 206 distinct values; the second is zero in all
5,569 records. Their pair distribution therefore matches the first-key
distribution, and the two keys are never equal. Values are not published
because a semantic or identifier role is not established.

The record vectors have 150 distinct values. Every vector has two through four
nonzero words, and only positions 0, 1, 3, 4, and 8 are ever nonzero. Ordered
same-capture, same-lane comparisons for repeated key pairs yield 3,927 equal
vectors and 49 changed vectors; changes occur only at positions 0 and 8. The
bounded unsigned values are only 0 and 1. Larger values are reported by band,
not exposed individually.

All 5,569 unread tails are the same all-zero 32-byte string. The reconstructed
events contain 5,281 exact repeated `0x0190` applications beyond first
occurrences, but no repeats are consecutive within a span and no two complete
span record sequences are identical. The source separately contains 1,759
exact repeated admitted TCP segments.

## Topics

- Complete `0x018F -> 0x0190* -> 0x0191` transaction accounting
- Key equality and repetition without publishing identifier-like values
- Vector equality, sparsity, changed positions, and bounded value bands
- Unread-tail invariance
- Same-lane packet context and retransmission separation

## Evidence gaps

No inventory-frame, equipment-carrier, or inventory-change scope overlaps a
transaction. Two spans immediately follow `0x016E`, one immediately follows
`0x0130`, and `0x0137` is the immediate prior or following opcode for 12 spans.
Those are bounded same-lane correlations only. The eight target-bearing
capture filenames cover combat, gathering, harvesting, local leve, party
battle leve, repair, and quest-update contexts, but filenames do not establish
packet causality or ownership.

The imported MassSetItemModifier names are not proven. This study does not
promote an inventory mutation, equipment transition, server-order policy,
event role, item-modifier role, or another gameplay noun.

## Further research

A directly linked client consumer or an independently observed state change is
required to assign meanings to the two keys, the five populated vector
positions, or the aggregate transaction.

## Verification

Repository validation reproduces the three products and validates the strict
accounting schema and checksum, and runs focused tests for shape mutation,
same-lane segmentation, malformed framing, enclosing-scope detection,
retransmission separation, and public-product sanitization.
