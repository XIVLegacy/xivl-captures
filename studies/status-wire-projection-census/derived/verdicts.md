# Status wire projection verdicts

## Exhaustive accounting

The complete 54-capture corpus contains 831 decoded s2c `0x0179`
events after canonical TCP reconstruction and lane admission. Five nonzero
status entries occur across four captures. They comprise 3
unique wire IDs and 3
translated retail status rows. The other status slots are zero sentinels.

## Projection witnesses

The observed complete-row name correlations are Protect (1), Resting (2), Well Fed (2). These names
label status rows only. They do not name any projected nibble value.

The three independent status rows expose Chant kind 2 and Object bits 8..11
values 7, 8, and 10. They therefore provide multiple witnesses for that shared
low-nibble projection. All three rows expose Chant kind 1 value 6, Object bits
14..15 value 1, and Object bits 12..13 value 2. Those upper projections remain
effectively single-value in this corpus despite repeated packet occurrences.

Each observed row has both a low and high reverse wire encoding under the
native transform. Only the low encodings appear on wire. The study preserves
both supported encodings and does not infer that one encoding is preferred in
unobserved cases.

## Rejected interpretations

Chronology does not establish status causality, action or cast meaning, or
server policy. Complete-row names are not evidence for nibble enums. Capture
filenames are not used to assign packet meaning. Historical chant labels,
wiki terminology, and implementation vocabulary are outside this study.

## Remaining boundary

This corpus distinguishes three values in the shared bits 8..11 projection but
only one observed value in each upper projection. Additional retail status rows
with different upper bits are required to broaden those witnesses. A capture
using a high reverse wire encoding would be required to compare encoding use.
