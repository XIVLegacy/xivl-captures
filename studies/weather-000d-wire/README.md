# Map Weather 0x000D Wire Contract

The frozen retail corpus contains 11 admitted game-lane clientbound
`0x000D` messages, all with weather value `8030` and duration byte `5`.
It contains no admitted `0x000D` weather `8007` witness. The Limsa `8007`
case therefore has native field support, with its retail transmission and
transition duration unverified by these captures.

The [evidence map](derived/evidence-map.md) owns the capture identities,
connection-local locators, field bytes, reproduction method and qualified
sender consequence. The source is
[`pcap-1.23b`](../../sources/pcap-1.23b/manifest.yaml), evidence class
`packet-capture`. The [decode contract](../../docs/pcap-decoding.md) owns
connection admission, framing and order limits.
