# Map context of the combat music requests

Neither combat capture supplies a SetMap/ZoneMaster witness for the retained
`13/1 -> 57/4` requests. Their active location remains unresolved. The nearest
earlier sample with matching TCP endpoints carries numeric value 154 and
`ZoneMasterFstF0`. Missing TCP payload
coverage prevents carrying that context into the music requests. This is a
qualified candidate, not a confirmed zone assignment or regional music rule.

## Selected packet domain

The four request locators and two combat member identities are in
[Map music wire evidence](evidence-map.md#source-identities). Every local
member used matched its size/SHA-256 in
[`pcap-1.23b`](../../../sources/pcap-1.23b/manifest.yaml). All 54 retained
members were checked only for the cross-capture discriminator below, not as
a new full-corpus music census. No archive container was rechecked here.

Both directions of every admitted clear-game connection were inspected:

| Member | Direction | Complete frames | Complete subevents |
| --- | --- | ---: | ---: |
| `combat_autoattack.pcapng` | c2s | 118 | 286 |
| `combat_autoattack.pcapng` | s2c | 156 | 899 |
| `combat_skills.pcapng` | c2s | 80 | 181 |
| `combat_skills.pcapng` | s2c | 117 | 535 |

Autoattack includes one main and one chat connection; skills includes one
main connection. All four music requests are connection 0, main s2c:

| Member | Song/mode | Frame / decoded subevent offset | Completing capture packet |
| --- | --- | --- | ---: |
| `combat_autoattack.pcapng` | 13/1 | 18 / 0 | 62 |
| Same member | 57/4 | 128 / 0 | 283 |
| `combat_skills.pcapng` | 13/1 | 25 / 168 | 85 |
| Same member | 57/4 | 85 / 0 | 177 |

Connection/frame indexes are zero-based; capture packets are one-based.
Offsets count decoded frame-body bytes, not pcap-file bytes.

Neither selected capture contains an admitted opcode `0x0005` in either
direction. Every decoded frame body, including wrappers, direct-session
records and padding, was searched for `ZoneMaster` in ASCII, UTF-16LE and
UTF-16BE, with no occurrence. These are finite encoding/domain negatives.
Autoattack's five s2c `0x00CC` class fields at application `+0x24` contain
`SlugLesserStandard` or `MonkeyLesserStandard`; skills has no s2c `0x00CC`.
Each also contains two c2s `0x00CC` requests without that class field.
Numeric opcode equality does not make those requests object-role witnesses.

The selected high-nibble-4 wrapper actor references all have bits 19..27
equal to 154, but none is `0x44D00001`. The published
[SetMap/ZoneMaster relation](../../director-wire-identity/derived/zone-controller-identity.md)
concerns role-associated ZoneMaster objects. Applying its inverse to arbitrary
actor IDs does not establish the player's active map. The observed monster
classes likewise supply no independent location identity.

## Nearest retained map candidates

The two selected main endpoint tuples are equal. All 54 retained members
were searched for that exact tuple, then compared by capture time and
IP-declared TCP sequence/ACK spans. The observed spans advance without
cross-file overlap or sequence reuse. This is compatible with a persistent
connection, but does not prove continuity or retained map state through gaps.
No connection blocks were concatenated into a capture-wide chronology.

The nearest preceding and following SetMap candidates are the same for both
combat samples. All locators below are connection 0, main s2c:

| Candidate | Member | SetMap frame / body offset / packet | Application u32 values | Later ZoneMaster frame / body offset / packet |
| --- | --- | --- | --- | --- |
| Before the music spans | `teleport_to_camp_tranquil.pcapng` | 45 / 0 / 211 | `[103,154,40,0]` | 57 / 1432 / 222 |
| After the music spans | `teleport_to_gridania.pcapng` | 58 / 0 / 181 | `[103,206,40,0]` | 69 / 2608 / 193 |

The class field is `ZoneMasterFstF0` in both candidates. Their wrapper sources
are `0x44D00001` and `0x46700001`, respectively, as recorded in the linked
ZoneMaster finding. The member filenames do not establish a physical location.
The four SetMap dwords remain numeric observations here.

Even the union of all matching-tuple retained IP-declared s2c payload spans
leaves these intervals uncovered between the preceding map frame's end and
each first song-13 frame's start. Sequence intervals are half-open:

| Music member | Uncovered sequence intervals | Missing bytes |
| --- | --- | ---: |
| `combat_autoattack.pcapng` | `[1873659077,1873688949)`, `[1873690971,1873696910)` | 35,811 |
| `combat_skills.pcapng` | The same two intervals plus `[1873718335,1873726532)` | 44,008 |

Thus endpoint equality, ascending spans and the actor-bit pattern do not
close the map-state join. An unobserved change cannot be excluded by these
samples, including when the later candidate also carries first dword 103.

## Framing, padding and reproduction

Python 3.12.0 and Scapy 2.7.0 used the existing `reconstruct_lanes`,
`parse_outer_frames`, `maybe_inflate` and `_decode_capture` APIs at repository
revision `ef46895ef821bdf78bac231aca17afd5877a1da2`. Canonical framing checks
passed for both selected captures and `gridania_to_coerthas.pcapng`.
That positive control reproduced its three published SetMap/ZoneMaster pairs
at numeric values 150, 152 and 145.

All selected admitted directions had zero internal sequence gaps, unparsed
outer/body bytes, compression-flag mismatches or unused/unconsumed zlib bytes.
Reconstructing only `IP.len - 4*IP.ihl - 4*TCP.dataofs` payload bytes per
IPv4/TCP packet produced exactly each admitted stream. The apparent canonical
overlap conflicts were Scapy `Padding` overwritten by `Raw` at outer-header
offsets 0, 1, 4 or 5; no conflicting application byte survived. Skills' six
discarded raw-reconstruction bytes came from Padding-only capture packet 285,
whose IP-declared TCP payload length is zero. The framing validator sees the
already-trimmed stream and therefore reports zero trailing bytes. This is
separate from the genuine cross-capture coverage gaps above.

To reproduce, verify the manifest-pinned members and decode the selected
connections in each direction. Locate the four music records and scan the
complete decoded bodies for SetMap and the stated ZoneMaster encodings.
For the cross-file check, select the exact endpoint tuple of combat main
connection 0. Retain only IP-declared TCP payload extents, compare sequence,
ACK and capture-time spans, and find the nearest SetMap candidates on that
tuple. Clip every retained s2c extent to each map-end/music-start interval,
sort and union the half-open ranges, then take their complement. Preserve
the gap intervals instead of filling them from another sample's map state.
Nonadmitted traffic and unobserved intervals remain outside the claim.

A contemporaneous retained location witness, or uninterrupted retained map
context through these gaps, is needed to close this context join.
The result does not authenticate track titles, audible playback, combat
eligibility, restoration policy or every zone sharing a regional candidate.
