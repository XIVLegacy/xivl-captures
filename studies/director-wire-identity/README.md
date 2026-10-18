# Director Wire Identity Verification

## Study contents

This study independently tests four wire hypotheses against the 54 retained
retail 1.23b captures. It decodes all observed `0x017A`, `0x017C`, `0x017D`,
`0x017E`, `0x017F`, `0x0183`, `0x0187`, and `0x018B` packets, all c2s
`0x012D` EventStart role rows, and both member-list forms. Numeric packet
fields remain uninterpreted unless the static client layout supplies the name.

## Start here

- `derived/verdicts.md` - claim verdicts, exact counts, and static cross-check.
- `derived/accounting.json` - corpus reconciliation and distributions.
- `derived/group-packets.csv` - one row per Group-family packet.
- `derived/group-members.csv` - transposed `0x017F` and `0x0183` member rows.
- `derived/event-role-candidates.csv` - EventStart owner actors and event names.
- `derived/zone-controller-identity.md` - seven paired retail observations of
  the numeric SetMap field and ZoneMaster actor-ID encoding.

Regenerate or verify the canonical products:

```text
python tools/extractors/extract_director_wire_identity.py
python tools/extractors/extract_director_wire_identity.py --check
```

The extractor uses the repository's canonical `default_corpus_paths()`
boundary, including the raw 54992 game lanes from `login.pcapng`. It does not
decode the capture's raw 54994 lobby lanes or TLS account traffic. Group
application payload begins after the 8-byte inner header and 8-byte
game-message preamble.

## Source material

The sole runtime source is the repository's `pcap-1.23b` set: 54 canonical
retail captures selected by `default_corpus_paths()`. The static cross-check is
linked by repository-qualified path and is not treated as packet evidence.

## Promoted conclusions

The promoted results are the four bounded verdicts in `derived/verdicts.md`:
two same-ID EventStart/content-member correlations use high nibble 4 without
proving director identity; party-battle headers carry type 30001; and the
proposed offsets conflate the large Group member packet with the compact
content-member packet.

The separate `derived/zone-controller-identity.md` records observed ZoneMaster
object identities and does not change these four director verdicts.

## Topics

- Director-role actor correlation
- Group header type values
- Group and content-member layouts
- Retail packet counts and field distributions

## Evidence boundary

EventStart `owner_actor_id` is role-bearing, but an event name alone does not
prove a server-side class name. GroupHeader application `+0x08` is a sequence
or session value, not an actor ID. A role/member match therefore means only
that the same retail actor ID is both an EventStart owner and a content-member
entry in the same capture. It does not establish server implementation.

## Evidence gaps

No retained packet names a server-side director class. The static Group path
does not mask the actor-ID high nibble or compare a member ID with a director
identity. EventStart names establish bounded roles only, and the 30001 result
is scoped to one party-battle capture.

## Selected commandJudgeMode request vectors

The complete EventStart owner census contains five `commandJudgeMode`
requests. Their complete encoded argument vectors were read from the four
original members below. Each locator is main connection 0, c2s, subevent 1,
at decoded-body offset 64. Frames and subevents are zero-based; completing
capture packet numbers are one-based.

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `add_str.pcapng` | 20056 | `246e4948a7ca1e4dc620e724677bfd9153ce76f6445a557967d309e9946021ed` |
| `gather_wood.pcapng` | 157688 | `c308aa4c984eb3e1912383c06e5115c6924713978df43cdb8075335e1bac7d32` |
| `harvest.pcapng` | 60680 | `8522a844b6904207c3465ae1d1038599eddb8b9dc47800d5230c8a1c3ad0e440` |
| `local_leve_complete.pcapng` | 358296 | `4f0793f354140478725bf2c30642a3458a854460f47fb11a7af635c8881d95cd` |

All nine positions in each vector are explicit wire tokens. `nil` denotes
tag `0x05`; integers use tag `0x00` and four big-endian signed-int32 bits.
`ref` denotes tag `0x06` and serialized binding-reference bits, not an
identified native object or Lua table.

- V0: `[nil,nil,nil,nil,ref(0x029B2941),nil,nil,nil,nil]`.
- V1: `[int(20002),int(0),nil,int(15),ref(0x44B00031),nil,nil,nil,nil]`.
- V2: `[int(20006),int(0),nil,int(15),ref(0x44B00039),nil,nil,nil,nil]`.

| Member | c2s frame | Completing packet | Owner bits / qualified command ID | Vector | END offset in parameters |
| --- | ---: | ---: | --- | --- | ---: |
| `add_str.pcapng` | 6 | 19 | `0xA0F02EE5` / `12005` | V0 | 13 |
| `gather_wood.pcapng` | 10 | 54 | `0xA0F055F3` / `22003` | V1 | 25 |
| `harvest.pcapng` | 9 | 30 | `0xA0F055F7` / `22007` | V2 | 25 |
| `harvest.pcapng` | 47 | 181 | `0xA0F055F7` / `22007` | V2 | 25 |
| `local_leve_complete.pcapng` | 43 | 121 | `0xA0F055F1` / `22001` | V0 | 13 |

The 184-byte application starts after the subevent, inner header and
game-message preamble. Parameters occupy `[49,177)`, exactly 128 bytes.
END is one `0x0F` byte; the remaining 114 bytes for V0 or 102 for V1/V2 are
zero padding. The final byte of the encoded integer 15 belongs to that
integer, rather than an earlier terminator. The seven application bytes
after the parameter span remain outside argument decoding.

The interpretation follows
`xivl-client-structs:manifests/player_command_wire_contract.json`,
`wire.fields`, `serializer` and `terminator`, SHA-256
`5dd48415ad06282cdfac097d08e886509117137ed019d520ac0cfce3562ddc50`.
Nine emitted tokens do not recover the original Lua supplied argument count:
omission and reference serialization can lose input distinctions.

`add_str` frame 6 and `local_leve_complete` frame 43 have different owners
but identical complete parameter blocks and CRC field `0x228A54EA`.
All five CRC fields equal CRC32 over their respective 128-byte blocks.
Thus the block and CRC cannot uniquely identify a request or prove a causal
request-to-callback transfer. No executed producer assigns these observed
integer positions a variation role. These five requests supply no materia
command owner, executed materia variation or `delegateCommand` callback join.

To reproduce, use the source manifest's exact members and the canonical TCP
reconstruction, then select the frame/subevent locators above and decode only
the stated parameter span through END. Preserve explicit nils, END, padding
and the remainder separately. Source identity, admission and framing match
the per-member accounting in
`studies/local-guildleve-dialogue/derived/accounting.json`, SHA-256
`3c349ec3dacba303d26c9666e487353193b7f662a967587dce52c4fd090dec15`.
The four members have zero c2s tails and zero admitted unparsed stream bytes.
Their 18 discarded s2c trailing bytes are outside these c2s observations.

## Winter snowman packet boundary

The retained clear-game packet records supplied no witness for Winter Is Not
Coming, quest `110801`, or its five snowman callbacks. This is a bounded
negative over the canonical decoded corpus, not proof about uncaptured retail
sessions or every possible encoding.

The input was all 54 members of
[pcap-1.23b](../../sources/pcap-1.23b/manifest.yaml), with every local member's
size and SHA-256 checked against that manifest. Its byte identity was
`baaa15f99f7f5d865bf2ec0dbcc1e454d034382b0559edccb0085c57c4061cf5`.
The manifest pins archive `pcap-1.23b-objects.zip`, 2,622,720 bytes, SHA-256
`20a78b9f40ff2393037c9a160c957783cf590b4f01797493d22fcd2039e9cbff`.
The archive container itself was not read for this check. The sorted member
digest from `tools/extractors/extract_00da_00e1_comparison.py:corpus_digest`
was `1293490808399dd5e1015d921a388f0fe4931dfa3ef678f30d790f5296025e6a`.

Canonical reconstruction admitted 84 clear TCP 54992 connections. Both
directions were inspected, including main and chat lanes:

| Direction | Complete outer frames | Complete subevents |
| --- | ---: | ---: |
| c2s | 8,970 | 21,201 |
| s2c | 10,790 | 44,663 |

The query domain was every byte offset in each decoded outer-frame body,
after inflation when flagged, including subevent headers, direct session
records, wrapped application payloads and padding. Every query below had
zero occurrences. Numeric byte searches did not require alignment.

| Query | Encoding |
| --- | --- |
| `processEventSnowMan`, `processEventSnowManOk`, `processEventSnowManEvent`, `processEventSnowMandefo`, `processEventSnowMandefo2` | Five separate case-sensitive ASCII literal searches. |
| `Spl0i3` | Case-insensitive ASCII substring, also covering the class path. |
| `110801`, `1b0d1` | Decimal ASCII and case-insensitive hexadecimal ASCII. |
| Quest `110801` / `0x0001B0D1` | Separate little- and big-endian u32 byte sequences. |
| Static actor key `0xA0F1B0D1` | Separate little- and big-endian u32 byte sequences. |

The last key follows `0xA0F00000 | low_id`, documented in
`xivl-decomp:docs/resource/static-actor-registry.md`, File contract and retail
coverage. `xivl-client-data:manifests/staticactor_class_paths.json`, records
row `id=110801`, maps that ID to `/Quest/Scenario/Spl/Spl0i3`; the manifest
SHA-256 is `d612438827e5997422ab6f64a807e567ddf1b953c532e8a319d67b93c53c9db0`.
This static identity does not prove a captured quest invocation.

Field checks counted all 126 c2s `0x012D` EventStart records and all 200 s2c
`0x0130` RunEventFunction records. None had the selected quest owner or a
selected snowman name. The whole-body searches also covered callback names
inside typed arguments, rather than only the outer function-name field.
No `0x016C` occurred in either direction; its adopted local catalog name is
`SetEmoteEventCondition`. That name supplies no additional field layout.
There was therefore no matching candidate whose full argument vector could
establish the selected callback or P3.

### Decode limits and reproduction

The producer was a read-only Python 3.12.0 traversal of the repository's
`default_corpus_paths`, `reconstruct_lanes`, `parse_outer_frames`,
`maybe_inflate` and `parse_sub_events`, using Scapy 2.7.0 and zlib 1.2.13.
The functions were inspected at repository revision
`dcd125c4ef2dac6152c96881db03df9341affd2d`. Reproduction requires the exact
manifest members, both directions of every admitted connection, the complete
query domain and encodings above, and comparison with the frame/subevent
totals. The existing `_decode_capture` in
`tools/extractors/extract_00da_00e1_comparison.py` supplies frame, subevent
and completing-packet locators for any candidate. Its event dictionaries
alone omit direct-session bodies, so search the decoded frame bodies before
reducing to wrapped events.

Compression flags agreed with complete zlib decoding. There were zero
admitted unparsed stream bytes, truncated subevents, short wrapped inner
headers or nonzero unparsed decoded-body bytes. Reconstruction had no
sequence gaps. It discarded 228 trailing s2c bytes outside complete frames,
and excluded 381 other payload-bearing TCP connections. TLS and lobby traffic
were outside the clear-game query domain.

`extract_streams.py:_reconstruct_direction` sorts segments by sequence number
and overwrites overlapping bytes in that stable order. In the admitted
connections, 11,497 overlapping byte writes disagreed with the preceding
value across 57 directional streams. No alternate overlap reconstruction was
performed. The negative result applies to the canonical resolved streams,
not every conflicting byte alternative, excluded traffic, discarded tails,
arbitrary encodings or uncaptured sessions. Frame/subevent order is local to
one connection and direction; no cross-connection chronology was inferred.

The existing packet corpus therefore did not close the Winter callback
mapping or supply P3. `xivl-client-scripts:docs/winter-is-not-coming-client-contract.md`
owns the callback consumers and conditional NPC delegate argument map. A
Winter-specific producer or correlated invocation outside this searched
evidence would be needed to establish the historical selection and quantity.

## Impish question packet boundary

The same exact 54-member source set and canonical decoded byte domain in
[Winter snowman packet boundary](#winter-snowman-packet-boundary) contained
no identified Impish Impositions question/answer producer or invocation.
Every member's size/hash and the canonical decoder pins matched that census.
The source identity, 84 admitted connections, frame/subevent counts, strict
framing checks, exclusions and overlap-resolution limits were unchanged.
The functions were inspected at revision
`53f2b6fd4b2a91bb84da949a607a98a641a5355c`.

Every byte offset of every decoded frame body, in both directions, was
searched for these 16 separate queries. All returned zero:

| Query | Encoding |
| --- | --- |
| `firstTalkAskEvent`, `firstTalkNomalEvent`, `firstUboa`, `getSweets`, `processEventHWLStart`, `processEventHWGStart`, `processEventHWUStart` | Seven case-sensitive ASCII literals. |
| `Spl0i2`, `PopulaceHalloweenTrans`, `HalloweenDirector` | Three case-insensitive ASCII substrings. |
| `110800`, `1b0d0` | Decimal ASCII and case-insensitive hexadecimal ASCII. |
| Quest `110800` / `0x0001B0D0` | Separate little- and big-endian u32 byte sequences. |
| Static actor key `0xA0F1B0D0` | Separate little- and big-endian u32 byte sequences. |

The static key uses the same documented `0xA0F00000 | low_id` encoding.
`xivl-client-data:manifests/staticactor_class_paths.json`, row `id=110800`,
maps the quest to `/Quest/Scenario/Spl/Spl0i2`; its digest is the one recorded
above. This is a static search identity, not an observed invocation.

The generic census again parsed all 126 c2s `0x012D` and 200 s2c `0x0130`
name/owner fields, with no selected method or quest-owner match. Whole-body
searching also covered an inner callback selector inside typed parameters.
No matching candidate supplied a question, three choices, expected answer
or complete typed invocation vector. The existing canonical decoder and
query procedure in [Decode limits and reproduction](#decode-limits-and-reproduction)
reproduce this result with the Impish query set above.

This negative applies to the canonical resolved clear-game records, with the
same excluded connections, 228 trailing bytes and conflicting-overlap limits.
It does not prove historical absence or choose a direct-call/delegate route.
`xivl-client-scripts:docs/impish-impositions-client-contract.md`, Question
bank and producer boundary, owns the preserved text bank and callback inputs.
The retained packets did not close their producer gap.

## Further research

No broader retail corpus exists. Catalog consumers may adopt the corrected
packet offsets now; stronger class naming would require an independent static
client identity chain rather than another interpretation of these bytes.
