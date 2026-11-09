# NPC nameplate startup work

Two retained 1.23b captures place a PopulaceStandard opening immediately
before a work message that carries value 1 for both nameplate properties
and follows those entries with `/_init`.

## Inputs and method

The [packet source manifest](../sources/pcap-1.23b/manifest.yaml) identifies
these members as packet-capture evidence. Authenticate each member before
using its main server-to-client lane.

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `small_talk_louisoix.pcapng` | 18444 | `58b620d90370ba69202e63f7f70edb79004ccbb8068e11e2e112a825d84dcafe` |
| `moving_around_gridania.pcapng` | 855000 | `bf6abf7ccc7a16e071846036477c1fadbc3b46385ef6e747b543d836f3f51017` |

The [packet decode guide](pcap-decoding.md) defines connection reconstruction
and lane scope. Use `tools/extractors/extract_streams.py` to reconstruct the
lanes, read and inflate outer frames, and `extract_observations.py` to walk
the subevents. Use `extract_gam_keys.py` and
`extract_property_stream_catalog.py` to check the declared property block
and record offsets. Check completion marker spans through the end of each
block, including markers after the final property. The two main directions
had no uncovered sequence bytes or nonzero subevent tails.

## Selected openings

The locators are zero-based within each reconstructed main s2c lane.
Each pair uses the same wrapped source and destination, with no removal or
reopening between the class-bearing `0x00CC` and `0x0137`.

| Member | Lane and frame | `0x00CC` subevent | `0x0137` subevent |
| --- | --- | ---: | ---: |
| `small_talk_louisoix.pcapng` | 0, 5 | 13 | 14 |
| `moving_around_gridania.pcapng` | 0, 13 | 9 | 10 |

Both openings carry `PopulaceStandard` and
`/Chara/Npc/Populace/PopulaceStandard`. From the first length byte in
the `0x0137` property stream, the two selected width-one entries are at
offsets 1 and 13. Their hashes are `0xE14B0CA8` and `0xFBFBCFB1`, the canonical
`charaWork.property[0]` and `charaWork.property[4]`, and both values
are 1. The next item at offset 19 has lead `0x88` and target `/_init`.
See the [property index convention](https://github.com/XIVLegacy/xivl-client-structs/blob/8ee5be22e27b63b0442d4a413d584238796a744c/docs/actor-hostility-classification.md#wire-inputs).

The small capture has one main s2c `0x0137` stream and the larger has
303. Neither contains `charaWork/property` or `charaWork/_init` at a
recognized completion lead. In the larger capture, the selected actor
has a later removal at frame 23 subevent 0 and a new opening at frame 49
subevent 13. A join by the wrapped identity alone would merge those
openings.

These observations establish wire order for the selected captures.
Native context state, work application, Lua notification and visibility
remain separate from the packet observations.
