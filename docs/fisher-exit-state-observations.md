# Fisher exit state and recipient evidence

The retained retail packet query does not establish whether a Fisher exit from
state 50 reached other players or only the fishing player. Its only observed
server state-50 entry and exit belong to the Logging sequence. That receiving
stream supplies no Fisher or observer-recipient witness.

| Question | Answer | Evidence locator | Confidence and remaining gap |
| --- | --- | --- | --- |
| Did the Fisher exit state/result/movement sequence reach other clients or only self? | Unresolved. All 912 retained main-lane `0x0134` records were checked. Only `gather_wood.pcapng` contains state 50, joined to Logging command 22003. No selected Fish command 22004 or Fish variation 20003/30003 identified a Fisher exit. | [Complete field query](#complete-field-query); [Logging control](#logging-control). | High for the finite fields and Logging identity. A Fisher exit joined to its actor and a receiving observer is missing. A self receipt or absent observer cannot establish a broadcast or self-only policy. |

## Complete field query

Evidence class: `packet-capture`, source
[`pcap-1.23b`](../sources/pcap-1.23b/manifest.yaml), recorded against retail
1.23b live servers. All 54 manifest members matched their byte sizes and
SHA-256 values. The canonical decoder admitted 54 main and 30 chat connections.
Only main connections supplied state and command observations. Complete-frame
streams had zero unparsed admitted bytes, truncated subevents or inflation
failures. The reducer excluded 228 trailing reconstructed S2C bytes.

Framing validation was reused only after member and framing/decoder tool
identities matched the prior complete check. The
[decode and order contract](pcap-decoding.md) preserves direction and connection
boundaries. Separate chat connections are not additional gameplay observers.

| Field or selector | Inspected extent | Result |
| --- | --- | --- |
| S2C `0x0134` application `+0` | All 912 eight-byte applications | Values 0: 851, 2: 37, 3: 16, 30: 4, 31: 3, 50: 1. One same-source 50-to-0 transition. |
| C2S `0x012D` fixed event/key fields | All 126 records | No selected `commandJudgeMode` key `0xA0F055F4` for Fish 22004. Spearfishing key `0xA0F055F8` was a separate zero-match control. The `+4` field is route-qualified, not a universal NPC owner. |
| C2S typed requests | 120 complete 128-byte spans | No first-argument Fish variation 20003/30003 in a `commandRequest`. Six other spans stopped at unadmitted tag `0x07`; no complete request vocabulary is claimed. |
| S2C `0x0130` calls | All 200 fixed function and 64-byte parameter spans | No selected Fish 22004 or Spearfish 22008 command-key/widget argument. Logging 22003 supplied 21 positive widget-parser controls. |
| S2C `0x0137` main-skill corroborator | 2,014 packets; 286 records for exact hash `0x7532CE24` | No value 41. This hash names `charaWork.parameterSave.state_mainSkill[0]`; property source, stream target context and historical actor binding remain separate. |

The complete state scan is independent of the six incomplete C2S tails.
Those tails occur outside `gather_wood.pcapng`; its two request spans and all
43 server-call spans decoded completely. No tag meaning was invented to
classify them. Missing selected command or property values do not establish
that no fishing occurred in any historical session or through another route.

The static [Fish command lookup][fish-lookup] maps variations 20003 and 30003
to command 22004. Its [catalog row][commands] names Fish; 22008 names Spearfish.
The [property catalog][skill-property] establishes the primary-skill hash and
index convention, while [skill-name row 41][skill-name] is Fishing. These
static identities qualify selectors; they do not themselves identify a
captured Fisher, an exit animation or network recipients.

## Logging control

`gather_wood.pcapng` has 157,688 bytes and SHA-256
`c308aa4c984eb3e1912383c06e5115c6924713978df43cdb8075335e1bac7d32`.
All rows below are main connection 0, S2C. Frame and subevent indices are
zero-based; completing capture packets are one-based.

| Completing packet | Frame / subevent | Observation |
| ---: | --- | --- |
| 58 | 12 / 0 | `0x0134`, state 50; source and recipient `0x029B2941`. |
| 738 | 232 / 0 | `0x0134`, state 0; same source and recipient. |
| 738 | 232 / 1 | `0x013C`, X00, source `0x029B2941`, row count 0, command 0 and header value `0x7C000062`. |

The [land-gathering sequence](land-gathering-observed-sequence.md#request-and-kick)
owns the Logging request and judge identity. The selected exit neighborhood,
bounded by the next EndEvent, contains state 0 and X00. This is not an
authenticated Fisher four-packet sequence or proof about later carriers.
The [result field model][result-fields] keeps header presentation data and
per-target effects separate. Neither an animation-like number nor state 50
identifies fishing by itself.

The recording client's C2S position sources and event triggers both contain
`0x029B2941`, matching the selected S2C recipient. This is one receiving
client's evidence. It cannot show whether the server also delivered records
to another client. No nonlocal Fisher actor or paired observer stream was
joined by this query.

## Reproduction boundary

Use the exact manifest members and the existing
[`_decode_capture` decoder][decoder] at revision
`0d59991d51ef3436f0c7a934f49090d7743ee86f`. Application offsets start after
the full 16-byte game-message header, separately from the subevent wrapper.
The [state catalog][state-field] names only the low state byte; its adjacent
byte is discarded on the traced native route. Preserve source and recipient
from the wrapper, rather than treating a game-header timestamp as an actor.

Inspect C2S event name `+0x11`, key `+4` and request parameters
`[0x31,0xB1)`, and S2C function `+0x29` and parameters `[0x49,0x89)`.
Count full typed leaves through END and retain unknown-tag spans as incomplete.
Widget arguments require the HarvestJudge reference `0xA0F4E204`, the named
method and its documented command position; an arbitrary integer 22004 is
not an identity join. The [conditional delegate contract][delegate] owns
the supplied-frame adaptation. Preserve actor and connection lifetimes when
matching states; do not join records by numeric source alone across captures.

[fish-lookup]: https://github.com/XIVLegacy/xivl-client-scripts/blob/20ec80505035a492409b2677dff51aa439363487/docs/gathering-marker-fishing-ui.md#place-driven-judge-command-mapping
[commands]: https://github.com/XIVLegacy/xivl-client-data/blob/7c014aa2aae438527275f649f882515b59c71f74/derived/command_battle_params.csv
[skill-property]: https://github.com/XIVLegacy/xivl-client-structs/blob/b356634bd04a421769fe5fd73b336649963feff0/manifests/property_stream_hash_catalog.json
[skill-name]: https://github.com/XIVLegacy/xivl-client-data/blob/7c014aa2aae438527275f649f882515b59c71f74/docs/skill-name-rows.md
[result-fields]: https://github.com/XIVLegacy/xivl-client-structs/blob/b356634bd04a421769fe5fd73b336649963feff0/manifests/battle_result_field_semantics.json
[decoder]: https://github.com/XIVLegacy/xivl-captures/blob/0d59991d51ef3436f0c7a934f49090d7743ee86f/tools/extractors/extract_00da_00e1_comparison.py#L276-L350
[state-field]: https://github.com/XIVLegacy/xivl-opcodes/blob/8eef487105c53b7602597cd204db008693cc0b24/opcodes.json#L2895-L2929
[delegate]: https://github.com/XIVLegacy/xivl-decomp/blob/c3a751809ecf052b770bc7d46da42ac27c10e9e5/docs/script/delegate-command-producer.md#delegate-and-callback-positions
