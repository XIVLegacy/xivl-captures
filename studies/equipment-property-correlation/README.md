# Equipment Transition Census

## Study contents

This study scans the complete canonical 54-capture retail corpus. It balances
the nested 0x0146/0x0147 inventory-set framing inside nearby 0x016D/0x016E
change scopes, decodes all 0x0148-0x014C item-row cardinalities and
0x014D-0x0151 linked-item cardinalities, and joins observed equipment slots to
item-package slots and catalog item IDs.

Nearby 0x0137 property projections are compared only when their capture-local
actor tokens, lane, and property hashes match on both sides of a framed event.
The census preserves order and distance without treating chronology as
causality.

## Start here

- `derived/evidence-map.md` - result classes, promoted facts, and claim limits.
- `derived/capture-accounting.csv` - one row for each canonical capture.
- `derived/matrix.csv` - one row for each equipment link or missing-carrier event.
- `derived/property-joins.csv` - before/after property observations around carrier events.

Regenerate or byte-check all four products:

```text
python tools/extractors/extract_equipment_property_correlation.py
python tools/extractors/extract_equipment_property_correlation.py --check
```

## Source material

All carrier locators come from the canonical `pcap-1.23b` source declared by
this study manifest. Property locators come from the deterministic record-level
0x0137 decode in `studies/property-stream-hash-catalog/derived/property-records.csv`.
Capture identities remain canonical in `sources/pcap-1.23b/manifest.yaml`.

## Promoted conclusions

The corpus contains one exact property-bearing transition: equipment slot 8
joins catalog item `0x007A3F58` while property hash `0x8cae90db` changes from
141 to 161. Six exact aggregate snapshots separately bind the old catalog item
`0x007A3D64` to equipment slot 8, closing the old-link state gap without
turning a snapshot into a transition.

## Topics

- Equipment item and linked-slot correlation
- Nested inventory transaction framing
- Actor-scoped property chronology
- Retransmission and repeated aggregate accounting
- Retail packet evidence gaps

## Sanitization

Published actor labels are capture-local tokens assigned in first-observed
order. They preserve actor equality within a capture without publishing actor,
session, endpoint, TCP sequence, or raw payload identifiers. Catalog item IDs,
property hashes, decoded values, slots, and canonical lane/frame/subevent/row
positions remain citation-grade packet facts.

## Evidence gaps

`EXACT-TRANSITION` requires a single-slot 0x014D item/link join and a changed
property hash present in both nearest actor-scoped projections.
`BOUNDED-CANDIDATE` retains a single-slot carrier when a comparable property
side is absent. `AGGREGATE-SNAPSHOT` retains 0x014E state without promoting it
to a transition. `MISSING-CARRIER` identifies framed inventory activity without
an equipment link, plus the named soul capture's property-only gap.

Exact repeated TCP payload segments are counted before reconstruction, and
repeated aggregate equipment states are counted separately. Opcodes
0x018F-0x0191 are counted only as excluded nearby traffic.

No gameplay meaning is assigned to `generalParameter[18]` or another indexed
property field.

## Further research

Body and weapon still require comparable before-side property values. Soul
still requires an item and equipment-link carrier in the same retained
evidence path. Aggregate snapshots can confirm slot state, but cannot by
themselves establish when or why a transition occurred.
