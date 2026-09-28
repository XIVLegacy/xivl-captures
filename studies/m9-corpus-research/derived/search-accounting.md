# M9 Search Accounting

## Immutable search space

`derived/corpus-inventory.csv` enumerates every searched object. All 54 local
objects matched the size and SHA-256 recorded by
`sources/pcap-1.23b/manifest.yaml`; total object bytes were 7,242,352. The
canonical corpus content digest was
`3e39bfbffdf5a7efa0f42fc221f42dc2d1d28af8f19378d28921a3b903c0c7ee`.

The canonical game decoder covered 53 members. It excludes `login.pcapng` from
game framing. The raw TCP scan included that member, so every manifest object
participated in at least one search pass.

## Decode passes

1. TCP segments were read from all 54 members and classified client-to-server,
   server-to-client, or other-port traffic. This pass covered 1,506,344 c2s
   bytes in 8,979 segments, 1,513,800 s2c bytes in 13,110 segments, and 700,488
   other-port bytes in 962 segments. The other-port class covers encrypted and
   non-game traffic rather than assigning a game direction.
2. TCP directions were reconstructed by sequence offset so retransmissions did
   not duplicate bytes. Complete outer frames were retained. This pass covered
   1,506,828 reconstructed c2s bytes in 8,980 frames and 2,107,519 reconstructed
   s2c bytes in 10,818 frames.
3. Server frame bodies beginning `78 9c` were zlib-inflated. Complete frame
   bodies contributed 6,984,089 searched bytes.
4. Variable sub-events were walked by their little-endian included size. Actor
   wrapper `0x0003` exposed its 8-byte inner header and inner opcode at `+2`.
   Actor-event payloads contributed 5,603,346 searched bytes.
5. Lane classification assigned connections with compressed server output to
   main and connections with raw framed server output to chat. It found 54 main
   connections, 34 chat connections across 30 captures, and no unknown lane.
   Main streams contributed 1,494,880 c2s and 1,455,858 s2c bytes; chat streams
   contributed 11,948 c2s and 651,661 s2c bytes.
6. As an independent capped cross-check, all 3,104 records and 447,688 bytes in
   `derived/payload_samples.json` were scanned. It found no `02 1d` marker.

The decoder contract is `docs/pcap-decoding.md`. TCP reconstruction and lane
classification are implemented by `tools/extractors/extract_streams.py`; the
sub-event and inner-opcode layout is implemented by
`tools/extractors/extract_observations.py`. The search did not use
`derived/sequences.json` as capture chronology.

## Autotranslate pattern passes

The cross-reference contained 758 fixed-phrase rows. For every row, the search
constructed `02 1d` followed by these selector hypotheses:

- row ID as u16 and u32, little-endian and big-endian;
- category and index as one-byte pairs in both orders;
- category and index as two-byte pairs, little-endian and big-endian, in both
  orders;
- `(category << 16) | index` and `(index << 16) | category`, little-endian and
  big-endian;
- the applicable forms both with and without trailing byte `03`.

After deduplication, 9,048 byte patterns were tested. A positive term candidate
required `02 1d`, an exact selector derived from one table row, and terminal
`03` wholly inside a decoded body or actor payload. No term candidate matched.
The no-terminator forms were retained only as a collision control and produced
the rejected `0x0137` property-payload matches described in `verdicts.md`.

This method would find any specimen using one of the enumerated byte grammars
because it scanned both raw directions, reassembled frame bodies after
decompression, and parsed payloads without the tracked sample cap or text
scrubbing. It cannot find an encoding outside those hypotheses.

## Chat opcode passes

For each parsed actor wrapper in each direction and lane, the inner opcode at
header `+2` was compared with `0x0003` and `0x00c9`. The scan retained capture,
direction, lane, event index, outer-frame index and byte offset, inflated-body
sub-event offset, source actor, and sub-event size. These filters found every
row in `chat-relay-specimens.csv` and no other target-lane match.

This method would find a framed specimen because it tests every complete
wrapped actor event after reconstruction and decompression rather than a sample
or opcode summary. Raw TCP scanning separately covered the decoder-excluded
member. TLS plaintext remains outside the observable corpus.

## Cross-repository identity

The fixed-phrase input was `xivl-client-data:csv/xtx__fixedPhrase.csv`, client
extraction `2012.09.19.0001`, game version `1.23b`, 82,373 bytes, SHA-256
`a9ce38b0b4ca33e1c03bf22bc854e054bb46db1cef9edfb4e9c55c5d0516a16c`,
760 lines and 758 data rows. Its identity is recorded in
`xivl-client-data:manifests/tables.json`.

The independent opcode interpretation was read from
`xivl-opcodes:opcodes.json` and its generated Map and World payload headers.
No sibling checkout is a build or regeneration dependency of this study.
