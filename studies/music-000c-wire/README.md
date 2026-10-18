# Map music wire samples

Five retained combat, stance, action and mount captures contained six admitted
map/clientbound `0x000C` messages. The two combat samples each carried
song/mode pairs `13/1`, then `57/4`; the mount sample carried `83/4`, then
`57/4`. These observations establish those sequences, without recovering a
general combat-trigger or restoration policy.

The [combat map-context check](derived/map-context.md) found a nearby numeric
154 candidate and matching actor bits, but retained TCP coverage gaps prevented
assigning an active map or zone to the four combat music requests.

The [evidence map](derived/evidence-map.md) owns the selected member hashes,
byte fields, connection-local locators, reproduction method and limits. The
source is [`pcap-1.23b`](../../sources/pcap-1.23b/manifest.yaml), evidence
class `packet-capture`. The [decode contract](../../docs/pcap-decoding.md)
owns game-lane admission, framing and order limits.
