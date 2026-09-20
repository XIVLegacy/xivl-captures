# Evidence map

## Source members

| Region | Source object | Markers | Original URL | Archive lookup |
| --- | --- | ---: | --- | --- |
| Coerthas | sources/mooglebox-regional-mob-maps/objects/coerthas.html | 39 | http://www.mooglebox.com/coerthas/index.php | Wayback lookup |
| Black Shroud | sources/mooglebox-regional-mob-maps/objects/blackshroud.html | 74 | http://www.mooglebox.com/blackshroud/index.php | Wayback lookup |
| La Noscea | sources/mooglebox-regional-mob-maps/objects/la-noscea.html | 63 | http://www.mooglebox.com/la-noscea/index.php | Wayback lookup |
| Thanalan | sources/mooglebox-regional-mob-maps/objects/thanalan.html | 78 | http://www.mooglebox.com/thanalan/index.php | Wayback lookup |

The source manifest pins each HTML member by SHA-256 and byte size. It also
pins the owner-supplied Amalj'aa screenshot. The screenshot's displayed tuple
matches Thanalan marker 52, but the image has no independent page metadata, so
that attribution remains a content match rather than image provenance.

The
importer verifies those pins before generating the CSV, so a changed snapshot
cannot silently alter the normalized rows. The page-specific archive lookup
URLs are retained in the CSV.

## Derived fields

map_x and map_y are the OpenLayers marker pixels. coordinates is the popup's
displayed coordinate text; coordinate_x, coordinate_y, and coordinate_note
split its numeric values and optional elevation note. level_* and amount_*
preserve the displayed text and parse numeric bounds. An amount beginning with
~ is approximate; a blank amount is unresolved. aggression_marker retains the
source image marker (0 or 1).

parsed_candidates is a compact JSON list made by splitting label_raw on /. A
slash-separated label is an unresolved_shared_slot verdict because the page
does not identify which candidate occupied the map marker. A single label is
recorded as single_label; neither verdict promotes a retail spawn slot or
population claim.
