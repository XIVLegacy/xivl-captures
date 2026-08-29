# Equipment Property Correlation

## Study contents

This study joins 0x0137 property records to 0x0148/0x0149 item records and
0x014D equipment links in exactly four retained gear captures. The deterministic
matrix preserves packet, subevent, item-record, property-record, and slot
locators without assigning gameplay meanings to generalParameter indices.

## Start here

- `derived/evidence-map.md` - promoted facts, claim boundaries, and gaps.
- `derived/matrix.csv` - one deterministic row per named capture.

Regenerate or verify both products:

```text
python tools/extractors/extract_equipment_property_correlation.py
python tools/extractors/extract_equipment_property_correlation.py --check
```

## Source material

The item and equipment-link locators come from the four exact canonical retail
captures. Property locators come from the deterministic record-level 0x0137
decode in `studies/property-stream-hash-catalog/derived/property-records.csv`.

## Promoted conclusions

The helm capture changes `generalParameter[18]` from 141 to 161. Its new catalog
item `0x007A3F58` is linked from equipment slot 8 to item slot 113. Body links
`0x007A88D7` from equipment slot 10 to item slot 140, and weapon links
`0x003D7E3D` from equipment slot 0 to item slot 79.

## Topics

- Equipment item and slot correlation
- Actor property chronology
- Retail packet evidence gaps

## Evidence gaps

Body and weapon have after-side property projections but no comparable before
values. The helm old item's explicit equipment-slot-8 link is missing. Soul has
no item or equipment-link carrier and is NO-GO. The captures contain no
0x018F-0x0191 stream.

No gameplay meaning is assigned to `generalParameter[18]` or any other indexed
generalParameter field.

## Further research

A capture that preserves both item/link carriers and comparable before-side
properties could close the body or weapon gaps. Soul requires a capture with an
item record and equipment link before any property correlation can proceed.
