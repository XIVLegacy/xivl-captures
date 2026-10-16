# Friend search retained wire exchange

`friendlist_search.pcapng` contains one c2s `0x01DD`, followed by s2c `0x01DF`
and `0x01E0` in the same decoded outer frame. No `0x01DC` or `0x01DE`
occurs in either direction. Evidence class: packet-capture.

| Direction/opcode | Capture packet | Frame/subevent | Subevent bytes | Application bytes |
| --- | --- | --- | --- | --- |
| c2s `0x01DD` | 131 | 41/1 | 296 | 264 |
| s2c `0x01DF` | 148 | 27/0 | 968 | 936 |
| s2c `0x01E0` | 148 | 27/1 | 648 | 616 |

The 32-byte difference consists of the 16-byte subevent header and 16-byte
game-message prefix. Frame and subevent indexes are zero-based per connection
direction; capture packet indexes are one-based. The two responses have an
unambiguous same-frame subevent order. Timing in
[exchange.csv](derived/exchange.csv) measures captured frame completion,
without establishing client dispatch or server processing latency.

[Accounting](derived/accounting.json) pins the capture's source-member size
and SHA-256 and records the selected-opcode counts in both directions. The
[source manifest](../../sources/pcap-1.23b/manifest.yaml) owns corpus
provenance. The extractor checks the complete source member identity,
canonical game-connection admission, compression flags, and frame extents.

Run `python tools/extractors/extract_friendlist_search_exchange.py --check`
to reproduce the products. Add `--public-shape` to check public source pins,
row accounting, and extents without reading restricted capture bytes.
The native route and interpretation belong to
`xivl-opcodes:data/client_opcode_semantics.json`; this table supplies the
bounded retained wire witness.

The 936-byte and 616-byte applications are authenticated observations.
Nonzero-byte totals and SHA-256 identify their bounded contents without
emitting names, comments, or raw payload bytes. Independent native evidence
in `xivl-client-structs:manifests/search_recruitment_wire_contract.json`
establishes the `0x01DF` row stride of 92 bytes and the `0x01E0` comment
stream and completion mask `0x02`. Those meanings are not inferred from
capture sizes or plausible strings. This capture census does not decode
those records or prove pagination, request/response causality, or partial
comment-entry continuation between packets.
