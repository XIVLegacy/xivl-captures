# Party marker 0x018D field census verdicts

## Exhaustive accounting

The complete 54-capture corpus contains 592 admitted s2c `0x018D`
events and 769 count-selected rows after canonical TCP
reconstruction. Counts are one in 415 events and two in 177 events. The census
profiles all 40 byte offsets, all 20 aligned u16 views, all 10 aligned u32
views, the three client-read float32 views at `+0x14`, `+0x18`, and `+0x1C`,
and a bounded hypothesis view at `+0x20` in the unprojected span.

## Integer and physical-row shape

The u32 at `+0x00` has 3 distinct
values and the u32 at `+0x08` has 3.
Each is zero only in the two all-zero second rows. The u32 at `+0x0C` is zero
in all 769 count-selected rows. The unprojected u32 view at
`+0x10` contains five all-ones values; no other aligned integer view has an
all-ones witness. This shape does not establish a sentinel noun. The complete
safe signed, unsigned-magnitude, zero, uniqueness, and frequency-group
distributions are in `field-census.json`.

All 8703 rows outside the
count are byte-zero, and all 592 seven-byte tails are zero. Physical
slot zero is nonzero in every event. Slot one is count-selected in 177 events,
but two selected slot-one rows are entirely zero. Slots two through fifteen
are never selected. These facts describe packet shape, not insertion or removal
behavior.

## Float32 domains

All 769 bit patterns at each tested float offset are finite.
There are no NaNs, infinities, or subnormals. The observed finite ranges are
`-1612.62634` through
`1836.94482` at `+0x14`,
`-12` through
`149.472565` at `+0x18`,
`-1927.96228` through
`1741.29932` at `+0x1C`, and
The bounded hypothesis view is `-3.12533283` through
`3.13171029` at `+0x20`. The sign and zero counts
are retained in the census. Finite ranges and filename scenarios do not prove
coordinate, altitude, heading, or map-space nouns.

## Tuple repetition and capture correlation

The 769 complete rows form
480 distinct tuples. There are
76 repeated groups containing
365 rows, with a maximum group
size of 37. Seven complete-row groups
cross capture boundaries, covering 48 rows and 14 public capture pairs. No
event contains two equal selected rows. `row-reuse.csv` publishes only the
public capture filenames and shared distinct-row counts; salted comparison
keys are not published.

Every target is the only `0x018D` event in its outer frame. The 554 consecutive
same-lane pairs fall into six outer-delta bucket observations from 1000 through
4999 numeric units and 548 from 5000 through 29999. These are sanitized
relative relationships, not private capture times, causes, or gameplay phases.

## Rejected interpretations

The capture does not establish actor, player, party-member, marker identifier,
map identifier, key, coordinate, altitude, heading, radius, color, icon, owner,
or slot-purpose nouns for any record field. It also does not establish that a
repeated tuple is entity identity. Only the packet-level presentation context,
the fixed client-read projection, count, and reserved layout are independently
corroborated; field nouns remain neutral.

## Sanitization and reconstruction boundary

No raw payload, endpoint address, actor identifier, player name, session
identifier, credential, hash key, or private time is published. Multi-byte
integer values are reduced to sign, magnitude, sentinel, uniqueness, and
frequency shapes. Exact float extrema, public capture-pair correlations, and
the published fixed layout can narrow candidate payload reconstruction, but do
not recover the omitted bytes by themselves.

The remaining discriminator is an independent public artifact that directly
assigns a field noun to one exact wire offset and width. A filename, finite
range, repetition pattern, or neighboring opcode is insufficient.
