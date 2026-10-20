# Request Warden and NMRush caller bindings

Fourteen selected retained captures contain one class-bearing `PopulaceRequestWarden`
creation record. It serializes actor class 1500038 and the tail
`false,false,0,1,"TEST",3,2`. The selected records contain no matching Warden
or NMRush event call. This binds serialized initialization values to a retail
NPC class; it does not identify normal or company Behest, a recruitment
decision, or a Skirmish instance.

## Source and query

The [retail source manifest](../../sources/pcap-1.23b/manifest.yaml) owns
membership and provenance. These fourteen original members, totaling 5,041,820
bytes, matched their manifest sizes and SHA-256 values:

| Capture | Bytes | SHA-256 | s2c `00CC` class fields | s2c `0130` function fields | c2s `012D` owner fields |
| --- | ---: | --- | ---: | ---: | ---: |
| `teleport_to_camp_tranquil.pcapng` | 67920 | `488318351cdedb2e2b650dc68c55014b160fbbc26753c200922402c1ba6c4dd7` | 19 | 3 | 1 |
| `teleport_to_camp_nine_ivies.pcapng` | 80004 | `fac2b485608247d299a406a7065e19918789118e7e544ca85cec4d772da0e3ab` | 15 | 5 | 1 |
| `party_battle_leve.pcapng` | 1429864 | `6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f` | 108 | 7 | 55 |
| `gridania_to_coerthas.pcapng` | 939832 | `63152a1ed6e446df5cc4750fe50a0839f9e45ad270c79abfc72b5c09cc47e547` | 232 | 0 | 6 |
| `gather_wood.pcapng` | 157688 | `c308aa4c984eb3e1912383c06e5115c6924713978df43cdb8075335e1bac7d32` | 2 | 43 | 2 |
| `from_gridania_to_blackshroud.pcapng` | 196308 | `eff300de679230653953ea3399939a15ce9d6aeafd202c7ebcf5f55e6d24930f` | 27 | 0 | 2 |
| `login.pcapng` | 856236 | `28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62` | 10 | 0 | 0 |
| `teleport_to_gridania.pcapng` | 67620 | `779141dc79a4bcf4bfc2e265f8b9510607d5a6b6e78d32f8940e5a847e598fa0` | 13 | 3 | 1 |
| `move_around_gridania.pcapng` | 220128 | `bea7ae86444fa3ef9acc08f148f60dff1e5992188ee85136dec50c64e09236d0` | 33 | 0 | 0 |
| `moving_around_gridania.pcapng` | 855000 | `bf6abf7ccc7a16e071846036477c1fadbc3b46385ef6e747b543d836f3f51017` | 281 | 0 | 0 |
| `gridania_map.pcapng` | 16184 | `13e26b2d68f195b8e2daf7c355a2741c155a1036b80d79c90aab982157290795` | 0 | 0 | 0 |
| `move_out_of_room.pcapng` | 83412 | `a7a03a1d688f3feb264f8da9fae3519c55b7e267aa3802472f0221f4d729b37b` | 53 | 1 | 1 |
| `accept_quest.pcapng` | 53180 | `a207109240254b1398a36f877afc7ac34a08466cfbd3cdd3f2eb5f4a50718057` | 0 | 2 | 1 |
| `small_talk_louisoix.pcapng` | 18444 | `58b620d90370ba69202e63f7f70edb79004ccbb8068e11e2e112a825d84dcafe` | 1 | 2 | 1 |

Framing validation used [validate_framing.py](../../tools/validate_framing.py).
Reconstruction used `_decode_capture` in
[extract_00da_00e1_comparison.py](../../tools/extractors/extract_00da_00e1_comparison.py)
at revision `e7d0d8dc45479566e988f5eb690d307202909853`.
That revision supplied the first six table rows. The other eight used the
same entry point at revision `773697caf6edfd3a2da8ecf6a91d9fe5b70b7b05`.
Complete admitted streams had zero unparsed bytes, truncated subevents,
short wrapped inner headers, inflation failures or compression mismatches.
The canonical reducer discarded six raw trailing s2c bytes in eleven inputs,
66 bytes total; this is distinct from admitted-stream framing. Only canonical
clear TCP 54992 game lanes were admitted; lobby 54994 and TLS were excluded.

The query compared all 794 s2c `0x00CC` class fields with the exact names
`PopulaceRequestWarden`, `RequestDirector`, `PopulaceNMRushGuide`,
`QuestDirectorNMRush01` and `QuestDirectorNMRush02`. It inspected all 66 s2c
`0x0130` function fields and their fixed 64-byte parameter spans for
`eventTalkRequest` prefixes and the seven Guide methods `processWarpAsk`,
`processNotWarp`, `processBattleAsk`, `processNotBattle`, `processReturnAsk`,
`processContentEndAsk` and `processBattleEnd`. This includes inner method-name
literals in reflective calls. The only match was the Warden creation below.
None of the 71 c2s `0x012D` owner fields matched its actor in the same capture.
Full application interpretation was limited to this 264-byte match.
The class query used application `[0x24,0x44)`, the function query
`[0x29,0x49)` and its parameter span `[0x49,0x89)`, and the owner query
little-endian u32 `[0x04,0x08)`. Each function had a full 64-byte parameter
span; the eight-input group had no short selected fields. A filename selected
a candidate input, not a content identity.

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
