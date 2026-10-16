# Local Guildleve Dialogue Calls

The retained `local_leve_complete.pcapng` contains three main-lane
server-to-client `0x0130` calls whose function string is `delegateEvent` and
whose serialized method string is `processPgEvent`.

- [Calls](derived/calls.json) preserve complete parameter blocks, hashes,
  typed values, and connection, frame, subevent, packet and byte locators.
- [Accounting](derived/accounting.json) records source identity, framing,
  selection and the full admitted `0x0130` function census.
- [Source manifest](../../sources/pcap-1.23b/manifest.yaml) owns the retained
  capture's provenance and restricted distribution.

## Observations

Each call contains actor values `0x029B2941` and `0xA0F1D58A`, the string
`processPgEvent`, two integers, two nil values, and an END tag.
The RunEvent owner field at application offset 4 is little-endian
`0x44B00005` in each call; it is separate from the serialized actor values.

| Main s2c frame | Subevent | Capture packet | First integer | Second integer |
|---|---|---|---|---|
| 14 | 0 | 38 | 365 | `0x151A9000` |
| 25 | 0 | 79 | 366 | `0x04136000` |
| 497 | 0 | 1734 | 368 | `0x04140000` |

Frame and subevent indexes are zero-based. Capture packet indexes are
one-based and identify the earliest packet completing each outer frame in
reconstructed TCP sequence space. This order belongs to the main connection's
s2c stream, and does not establish cross-direction order or server causality.

## Byte interpretation

The application payload starts after the 8-byte inner header and 8-byte game
message preamble. Its function field is `[0x29, 0x49)`. The serialized parameter
block is exactly 64 bytes at `[0x49, 0x89)`. The following seven application
bytes are recorded separately and excluded from parameter decoding.

The bounded decoder reads tag `0x06` as an actor followed by a big-endian
32-bit value, tag `0x02` as a NUL-terminated string, tag `0x00` as a big-endian
32-bit integer, tag `0x05` as nil, and tag `0x0F` as END. These forms are the
only ones needed for the retained calls. The first integer has tag offset 26
and value offset 27 within the parameter block. END is at offset 38; all
remaining parameter bytes are zero.

The tag interpretation is supported by
`xivl-client-scripts:docs/passivegl-craft-columns.md`, section "Native bindings
and event decoding", which records the retail binary identity, parameter
walker `0x007906C0`, and jump table `0x007909E0`. This is an interpretation
citation; reproduction uses only this repository's capture and decoder.

These are typed wire observations. The two integer positions alone do not
establish a dialogue table, text identity, packing scheme, or client-data
source-column selection. The bytecode-qualified positional roles of the two
integers are recorded in `xivl-client-scripts:docs/passivegl-craft-columns.md`,
section "Supplied dialogue consumer". The actor values do not independently
identify native actor classes.
This study covers one retained capture and makes no corpus-wide absence claim.

## Reproduction

The extractor pins `local_leve_complete.pcapng` to 358296 bytes and SHA-256
`4f0793f354140478725bf2c30642a3458a854460f47fb11a7af635c8881d95cd`.
It uses canonical TCP reconstruction, requires the recorded lane and framing
accounting, and rejects drift in the three call locations or typed values.
The capture has zero discarded trailing stream bytes and zero admitted
unparsed stream bytes in either direction.

With the restricted source restored at its documented cache location:

```text
python tools/extractors/extract_local_guildleve_dialogue.py
python tools/extractors/extract_local_guildleve_dialogue.py --check
python tools/refresh.py --check
```

`--out-dir` can direct reproduction to a separate directory.
`XIVL_PCAP_OBJECTS_DIR` can select an explicit restored object directory.
