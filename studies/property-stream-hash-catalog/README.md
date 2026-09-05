# Actor Property Stream Hash Catalog

## Study contents

This study decodes every property record carried by s2c `0x0137` in the 53
canonical retail 1.23b captures. The resulting 2,014 packets contain 9,118
records, 263 distinct hashes, 37 contributing captures, and 14 scenario IDs.
These totals are pinned in `derived/accounting.json`; each record is retained
in `derived/property-records.csv`.

## Start here

- `derived/accounting.json` - packet, record, width, capture, and hash profiles.
- `derived/property-records.csv` - one row per decoded property record.

Regenerate or verify both products:

```text
python tools/extractors/extract_property_stream_catalog.py
python tools/extractors/extract_property_stream_catalog.py --check
```

## Source material

The sole input is the repository's canonical `pcap-1.23b` corpus selected by
`default_corpus_paths()`. The extractor records SHA-256 for every input capture
and excludes the login artifact through that shared corpus boundary.

## Promoted conclusions

The retained corpus contains property widths 1, 2, 4, 11, and 95 bytes with
counts 3,891, 3,325, 1,658, 22, and 22 respectively. These are wire widths,
not signedness or native-type declarations. Each row preserves the raw value;
the little-endian integer and four-byte float columns are parallel decode aids.

## Topics

- Actor property stream records
- Murmur2 property hashes
- Property value-width distributions
- Per-capture and per-scenario coverage

## Evidence boundary

`source_actor_id` and `destination_actor_id` are the two wrapped subevent
header fields. The packet-only study does not rename either as the property
subject. `target_marker` is independent ASCII stream context. None of these
fields assigns server behavior.
`value_u_le` and `value_f32` do not select a semantic interpretation.

## Evidence gaps

The capture corpus alone cannot distinguish signed integers from unsigned
integers, or integer bits from float bits for every four-byte property. Name
resolution and client-side type claims therefore remain owned by the static
catalog stage.

## Further research

Join the 263 exact Murmur2 names from the client catalog, retain unresolved
rows if any future corpus adds new hashes, and probe cast timing only after a
server-time property identity is exact.
