# Request Warden and NMRush caller bindings

Six retained captures contain one class-bearing `PopulaceRequestWarden`
creation record. It serializes actor class 1500038 and the tail
`false,false,0,1,"TEST",3,2`. The selected records contain no matching Warden
or NMRush event call. This binds serialized initialization values to a retail
NPC class; it does not identify normal or company Behest, a recruitment
decision, or a Skirmish instance.

## Source and query

The [retail source manifest](../../sources/pcap-1.23b/manifest.yaml) owns
membership and provenance. These six original members, totaling 2,871,616
bytes, matched their manifest sizes and SHA-256 values:

| Capture | Bytes | SHA-256 | s2c `00CC` class fields | s2c `0130` function fields | c2s `012D` owner fields |
| --- | ---: | --- | ---: | ---: | ---: |
| `teleport_to_camp_tranquil.pcapng` | 67920 | `488318351cdedb2e2b650dc68c55014b160fbbc26753c200922402c1ba6c4dd7` | 19 | 3 | 1 |
| `teleport_to_camp_nine_ivies.pcapng` | 80004 | `fac2b485608247d299a406a7065e19918789118e7e544ca85cec4d772da0e3ab` | 15 | 5 | 1 |
| `party_battle_leve.pcapng` | 1429864 | `6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f` | 108 | 7 | 55 |
| `gridania_to_coerthas.pcapng` | 939832 | `63152a1ed6e446df5cc4750fe50a0839f9e45ad270c79abfc72b5c09cc47e547` | 232 | 0 | 6 |
| `gather_wood.pcapng` | 157688 | `c308aa4c984eb3e1912383c06e5115c6924713978df43cdb8075335e1bac7d32` | 2 | 43 | 2 |
| `from_gridania_to_blackshroud.pcapng` | 196308 | `eff300de679230653953ea3399939a15ce9d6aeafd202c7ebcf5f55e6d24930f` | 27 | 0 | 2 |

Framing validation used [validate_framing.py](../../tools/validate_framing.py).
Reconstruction used `_decode_capture` in
[extract_00da_00e1_comparison.py](../../tools/extractors/extract_00da_00e1_comparison.py)
at revision `e7d0d8dc45479566e988f5eb690d307202909853`.
Complete admitted streams had zero unparsed bytes, truncated subevents,
short wrapped inner headers, inflation failures or compression mismatches.
The canonical reducer discarded six trailing s2c bytes from each input's raw
main stream; this is distinct from admitted-stream framing.

The query compared all 403 s2c `0x00CC` class fields with the exact names
`PopulaceRequestWarden`, `RequestDirector`, `PopulaceNMRushGuide`,
`QuestDirectorNMRush01` and `QuestDirectorNMRush02`. It inspected all 58 s2c
`0x0130` function fields and their fixed 64-byte parameter spans for
`eventTalkRequest` prefixes and the seven Guide methods `processWarpAsk`,
`processNotWarp`, `processBattleAsk`, `processNotBattle`, `processReturnAsk`,
`processContentEndAsk` and `processBattleEnd`. This includes inner method-name
literals in reflective calls. The only match was the Warden creation below.
None of the 67 c2s `0x012D` owner fields matched its actor in the same capture.
Full application interpretation was limited to this 264-byte match.

## Warden creation record

In `teleport_to_camp_tranquil.pcapng`, main connection 0, s2c frame 61 /
subevent 14, frame-stream offset 13107 and subevent offset 1272 identify
`0x00CC` with source actor `0x44D04940` and target `0x029B2941`.
The frame completed at capture packet 230. The application has 264 bytes,
SHA-256 `982f8ca1c5e0c1275e4ba290d49468beb27d3fb9357afb2f005fcf37641c83c4`.
Connection, frame and subevent indexes are zero-based; capture packet is one-based.
Offsets below are hexadecimal application offsets after the game-message
preamble, rather than offsets into the outer frame or subevent header.

The fixed name is `pplRequestW_fst0Fld05_Qh@09A00` at `+0x04`.
The fixed class is `PopulaceRequestWarden` at `+0x24`.
String tag `0x02` at `+0x44` precedes
`/Chara/Npc/Populace/PopulaceRequestWarden`, terminated at `+0x6E`.
Five false tags occupy `+0x6F..+0x73`.

| Application offsets | Tag | Value with big-endian numeric decoding |
| --- | --- | --- |
| `0x74..0x78` | `0x00` | 1500038 |
| `0x79` | `0x04` | false |
| `0x7A` | `0x04` | false |
| `0x7B..0x7F` | `0x00` | 0 |
| `0x80..0x84` | `0x00` | 1 |
| `0x85..0x8A` | `0x02` | `TEST`, including its NUL |
| `0x8B..0x8F` | `0x00` | 3 |
| `0x90..0x94` | `0x00` | 2 |
| `0x95` | `0x0F` | END |

All 114 application bytes after END are zero. The numeric actor class is
distinct from the transport actor ID. The internal fixed name is not a
player-facing NPC name. The native prefix/control and deferred initializer
conditions belong to `xivl-decomp:docs/net/guildleve-initializer-route.md`.
The NPC count-segment interpretation belongs to
`xivl-client-scripts:docs/request-warden-event-contract.md`, "Retained Warden
initializer". Capture bytes alone do not prove the Lua request completed.

## Remaining caller boundary

There is no matching `RequestDirector`, Guide or NMRush Director class in
these selected `0x00CC` fields, nor a selected named event call. This bounded
comparison supplies no Warden join/cancel/end arguments, Director `requestId`,
Guide talk argument, returned option consumer or synchronized content-state
producer. It is not an absence claim for the other retained captures or for
all possible caller forms. Filenames served as candidate locators and do not
establish where a content encounter ran.
