# Local Guildleve Dialogue Calls

The complete manifest-admitted clear-game corpus contains three
`processPgEvent` calls, all in `local_leve_complete.pcapng` on the main
server-to-client lane. Each is a `0x0130` `delegateEvent` call. This identifies
the observed wire producer as server output; the capture does not expose the
server code or selection rule.

- [Calls](derived/calls.json) preserve complete parameter blocks, hashes,
  typed values, and connection, frame, subevent, packet and byte locators.
- [Accounting](derived/accounting.json) records every manifest member's
  identity, framing, lane admission, excluded TCP connections, literal hits
  and admitted `0x0130` function census.
- [Exchanges](derived/exchanges.json) retain two bounded `talkDefault`
  conversations, grouped by connection direction, with full application
  bytes, decoded parameter blocks and exact comparisons.
- [Progression](derived/progression.json) retains selected craft calls,
  quest-keyed typed parameters and player property writes between the
  conversations, plus the property reset after the second text call.
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

## Corpus scope

The corpus scope is all 54 PCAP members of the source manifest, with 84
admitted game connections. Every member's size and SHA-256 match its manifest
record. There are no non-PCAP manifest members. Non-game TCP connections are
counted separately by observed server port, including HTTP, TLS and lobby
traffic where present, and their plaintext is outside this search. Unlisted
local files are outside scope.

The admitted streams have zero unparsed bytes, subevent truncations, short
wrapped inner headers, compressed-frame inflation failures or compression
flag mismatches. The canonical reducer discards 228 trailing s2c bytes across
the corpus, recorded per file. The three calls above are the only admitted
application payloads containing the ASCII `processPgEvent` literal. This is a
bounded corpus result, not an absence claim about unrecorded sessions or
excluded protocols.

## Bounded exchanges

Both retained conversations use EventStart `0x012D` with `talkDefault` and
owner `0x44B00005`. Their complete 184-byte application payloads are equal.
Their server `switchEvent` calls also have equal complete 144-byte application
payloads. The following EventUpdate `0x012E` applications share their first
81 bytes, including the 64-byte parameter block at offset 17, but differ in
the seven trailing bytes. Both parameter blocks decode to integers `0, 2`.
The trailing bytes remain uninterpreted and are preserved verbatim.

| Observation | First conversation packet | Second conversation packet | Comparison |
|---|---:|---:|---|
| c2s `talkDefault` EventStart | 16 | 1698 | Complete application equal |
| s2c `switchEvent` | 19 | 1701 | Complete application equal |
| c2s EventUpdate integers `0, 2` | 28 | 1722 | First 81 application bytes equal |
| s2c `delegateEvent` / `welcomeTalk` | 30 | 1724 | Complete application equal |
| c2s EventUpdate nil | 35 | 1728 | Explicit tag `0x05`, then END |
| s2c `delegateEvent` / `processPgEvent` | 38 | 1734 | First integer: 365 / 368 |

The `welcomeTalk` blocks contain actors `0x029B2941` and `0xA0F1D58A`, the
method string and four nil values. They use the same owner as the
`processPgEvent` calls. The observed first integers are 365 and 368. The
EventStart equality and EventUpdate prefix equality do not establish a
selector for either text ID. The seven trailing EventUpdate bytes differ.
The native writer analysis in
`xivl-client-structs:structs/network/event-update.md` identifies those positions
as unwritten bytes in the copied stack record and application offset 12 as
the CRC32 of the 64-byte parameter block. This qualifies the tail difference;
it does not establish a dialogue selector. Other captured activity separates
the conversations.

The first conversation also retains c2s nil EventUpdates at packets 43 and
75, s2c `simpleFadeInAndOut` at packet 49, and the 366 call at packet 79.
In the c2s stream, 43 precedes 75; in the s2c stream, the 365 call precedes
`simpleFadeInAndOut`, which precedes the 366 call. Packet provenance places
43 after the 365 frame's completion and 75 before the 366 frame's completion.
Every later EventUpdate in both windows also has an explicit nil tag followed
by END. This records wire values without inferring a one-to-one callback or
client return policy.

Each window retains every c2s EventStart/EventUpdate and every owner-matching
s2c RunEvent within the pinned direction-local frame bounds, plus the
`talkDefault` end. EventUpdate has no owner field identified here; it is
associated only by that bounded context. Both windows retain completion
updates and `finishTalkTurn`, not just the initial text calls. The two
directions are never merged to assign stream order. Capture packet indexes
are frame-completion provenance, not the server's receive or execution order.
No binding from the wire owner to a client-data actor class is established.

## Intervening observations

The selected craft calls use `0x0130` `delegateCommand`, owner `0xA0F055F1`,
and a parameter prefix of actor `0xA0F4E203`, method string, and actor
`0xA0F055F1`. The table lists every remaining parameter in each selected block.
All are big-endian integers with the tags and offsets retained in
`derived/progression.json`.

| Main s2c frame | Subevent | Capture packet | Method | Integer parameters |
|---:|---:|---:|---|---|
| 58 | 0 | 186 | `confirmLeve` | `120202, 2, 8030420, 0, 5, 1, 0` |
| 195 | 2 | 658 | `askContinueLocalleve` | `120202, 8030420, 1, 3, 4` |
| 362 | 2 | 1240 | `askContinueLocalleve` | `120202, 8030420, 2, 3, 3` |
| 464 | 2 | 1581 | `askContinueLocalleve` | `120202, 8030420, 3, 3, 2` |

The intervening c2s EventUpdate at frame 57, subevent 1, packet 184 contains
exactly actor `0xA0F1D58A`, then END. Its association is the bounded
`selectCraftQuest` / `confirmLeve` neighborhood, without a proved callback
pairing. The client interpretation of the craft arguments is owned by
`xivl-client-scripts:docs/passivegl-dialogue-producer.md#intervening-craft-progress`.
These are selected typed calls; their order alone does not prove delivery,
craft success or the server's dialogue-selection rule.

Three s2c GenericData `0x0133` streams contain the prefix string `attention`,
actor `0x5FF80001`, and an empty string, followed by these integer lists:

| Main s2c frame | Subevent | Capture packet | Integer parameters |
|---:|---:|---:|---|
| 191 | 7 | 648 | `40119, 120202, 1, 3` |
| 357 | 7 | 1230 | `40119, 120202, 2, 3` |
| 461 | 14 | 1576 | `40121, 120202` |

This records the typed values without assigning a text bank or treating
GenericData as authoritative quest state.

The same s2c stream contains these `0x0137` property writes. Both wrapped
transport actor fields equal player `0x029B2941`; none of these packets has
`0xA0F1D58A` as its transport source.

| Main s2c frame | Subevent | Capture packet | Exact hash-resolved field | Raw value |
|---:|---:|---:|---|---|
| 29 | 0 | 91 | `work.guildleveChecked[8]` | `01` |
| 461 | 18 | 1576 | `work.guildleveDone[8]` | `01` |
| 503 | 0 | 1751 | `playerWork.questGuildleve[0]` | `00000000` |
| 503 | 0 | 1751 | `work.guildleveId[8]` | `0000` |
| 503 | 0 | 1751 | `work.guildleveDone[8]` | `00` |
| 503 | 0 | 1751 | `work.guildleveChecked[8]` | `00` |

Field identities are exact backward MurmurHash2 matches in
`xivl-client-structs:manifests/gam_hash_names.json`, SHA-256
`4c6626aaec0569e8e857ae4d25ddd186614d8843c50b91904c4ac617283d2ca3`.
The product retains each hash, width, target-marker context, application
offset, complete application bytes and SHA-256. The target-marker string
does not replace the full property-path hash.

The checked write follows the 366 call in the s2c stream. The done write
precedes the second conversation and its 368 call; the zero writes follow
that call. The recording has no nonzero `guildleveId[8]` baseline linking
slot 8 to quest 120202. These state writes and the separately quest-keyed
craft calls distinguish the captured intervals, but do not establish that
slot 8 belongs to 120202, that the done write selects 368, or which
`passiveGL_craft` source column the server reads.

## Reproduction

The extractor pins `local_leve_complete.pcapng` to 358296 bytes and SHA-256
`4f0793f354140478725bf2c30642a3458a854460f47fb11a7af635c8881d95cd`.
It verifies all source manifest member identities, uses canonical TCP
reconstruction and clear-game admission, and requires the recorded framing
accounting. It rejects drift in the three call locations or typed values,
the bounded exchange locators, and the stated payload comparisons.
The capture has zero discarded trailing stream bytes and zero admitted
unparsed stream bytes in either direction.

With all 54 restricted source members restored at the documented cache location:

```text
python tools/extractors/extract_local_guildleve_dialogue.py
python tools/extractors/extract_local_guildleve_dialogue.py --check
python tools/refresh.py --check
```

`--out-dir` can direct reproduction to a separate directory.
`XIVL_PCAP_OBJECTS_DIR` can select an explicit restored object directory.
