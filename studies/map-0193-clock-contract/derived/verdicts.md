# Map 0x0193 clock/value verdicts

## Complete corpus accounting

The complete frozen 54-capture corpus contains 9 valid s2c
`0x0193` events in eight captures after canonical TCP reconstruction. Every
event is a 40-byte wrapped subpacket with an 8-byte application payload. There
are 0 c2s targets and
0 malformed target exclusions.

Subopcode `0x12` occurs once with application value 900. Subopcode `0x14`
occurs eight times: value 2 occurs six times and value 15 occurs twice. No
application value is the `0xffffffff` sentinel. One reconstructed outer frame
contains two ordered targets, `0x12/900` followed by `0x14/2`; no same-lane
subopcode/value pair repeats.

## Clock and arithmetic verdict

The packet-header u32 at game-message header `+0x08` equals the floor of the
outer-header numeric value divided by 1000 in all nine events. Together with
the capture-time correlation, this establishes millisecond scaling for that
outer value in these target frames without assigning the outer field globally.
The packet-header value differs
from the earliest
frame-completion capture time by -626868 through
192541 microseconds across all nine events. Its values therefore
occupy the Unix-compatible whole-second domain evidenced by capture chronology,
not an arbitrary counter domain. For every non-sentinel input, the retail
client arithmetic produces `(header_clock + application_value) mod 2^32`.

The application value is an offset in the packet-header clock's integer unit,
and the arithmetic result is an absolute Unix-compatible sum. The sole
observed `0x12` branch stores that sum as an endpoint; its value 900 produces a
stored endpoint 900.013696 seconds after frame completion. The eight `0x14`
rows prove the same arithmetic inputs, but that setup branch does not persist
or present the derived sum.

## Correlation limits

No target event occurs in `login.pcapng`. The preserved public evidence has no
session identity joining the other eight target-bearing capture files to that capture's
clear lobby client-number observations or to a `SERVER_UTC` launch value, so
the same-session `SERVER_UTC` comparison count is zero. Numeric proximity
across capture files is not promoted to a session link.

The three-event same-lane neighborhoods preserve frame order, completion-time
deltas, and packet-header clock deltas. They contain no canonical event that
independently measures when a derived endpoint is reached. Repeated values in
different capture files are distribution witnesses, not countdown samples.

## Claim boundary

The packet evidence proves complete occurrence accounting, seconds-scale
Unix-compatible header clocks, and the arithmetic domain. Retail client and
Lua evidence can separately identify storage routes and presentation
divisions, but UI text does not name the packet or establish server intent.
This study does not infer eligibility, reset schedules, content availability,
login causality, or authoritative server policy.

## Remaining discriminator

To prove server policy rather than client arithmetic, a preserved same-session
sequence must contain `0x0193`, an independently anchored server clock, and a
directly linked state or presentation transition at the derived value. A
sentinel-bearing packet is separately required to observe the exceptional wire
case. Neither discriminator exists in the frozen corpus.
