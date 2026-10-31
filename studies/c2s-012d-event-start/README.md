# Client EventStart 0x012D Joins

This study records what the retail client sends in client-to-server `0x012d`
EventStart messages. It covers every such message in the 54 captures of
`pcap-1.23b`, 126 messages in 39 captures. The packet is `EventStartPacket` in
xivl-opcodes:opcodes.json. The study joins the selector byte at payload
offset 0x10, the server codes field, and the event name, and it counts the
`0x00cc` and `0x00cd` target messages that come before each talk start.

## Findings

- Event name fixes the selector in all but two messages. `talkDefault` carries
  selector 1 in 16 of 17 messages. The names `caution`, `exit`, and
  `regionChange` carry selector 2 in 7 of 7. The five `command` names carry
  selector 0 in 100 of 100. No message carries selector 51.
- Selector 101 appears twice. One is a `talkDefault` and one is a
  `noticeEvent`. Each directly follows an EventStart with the same owner actor
  and carries no `0x00cc` before it. The `noticeEvent` that precedes the
  second one carries selector 5.
- The published payload samples hold 60 of the 126 messages. In those 60,
  `talkDefault` carries selector 1 in 14 of 14, the selector 2 names carry it
  in 5 of 5, and the `command` names carry selector 0 in 41 of 41. Selector 101
  and selector 5 are not among them.
- The low 22 bits of the server codes field are zero in 117 of the 126
  messages and in all 60 published samples. The 9 exceptions are every message
  of `war_quest_update2.pcapng`, which carries the low value 60 on every
  start. The high 10 bits take 10 distinct values in the corpus.
- Before 16 of 17 `talkDefault` messages, the nearest wrapped-actor message
  is a `0x00cc` whose actor id is the EventStart owner and whose second dword
  is zero. A `0x00cd` with the owner as actor id and second dword
  `0xe0000000` precedes that `0x00cc` in 13 of the 16.

[Verdicts](derived/verdicts.md) holds every table. [Accounting](derived/accounting.json)
holds the same figures in machine form. It also lists the event name, selector,
zone field, and low bits of each published payload sample by sample index.

## Job-change context extension

`derived/job-change-context.json` is a bounded extension over the same 54-member
source set. It records all 18 server-to-client `0x01a4` job-update locators,
the byte at application `+0`, and the designated animation/result fields in a
same-connection, same-direction window of three decoded subevents on either
side. It also records the one request whose application `+4` static-owner low
16 value is 12017, including the witnessed integer/nil typed-tail shape.

The same product scans every complete decoded subevent for the exact
`0x04000030` value and the packed predicate `(value & 0xFF000FFF) ==
0x04000030` (high byte `0x04`, low 12 bits `0x030`). Both counts are zero in
the verified 54-member corpus, including the designated animation `+0` and
combat-result `+4` fields. The predicate accepts middle-field examples such
as `0x04001030`; `0x04000029` is not a match.
The product also requires zero truncated subevents, compression mismatches,
and nonzero undecoded frame-body tails before accepting the negative result.

The extension has one local presentation witness: in
`gear_changesoul.pcapng`, the `0x01a4` update with application byte `16` at
frame 13, stream offset 1128, subevent 0 is followed by `0x00da` at frame 14,
stream offset 1182, subevent 0. The `0x00da` application `+0` word is
`0x04000029`; all four wrapper actor fields equal those of the job update.
This is directional decode order within one server stream, not a cross-direction
request/response chronology claim.
The `0x00da` occurrence and its three-event neighborhood remain canonically
owned by [Map 0x00DA and 0x00E1 Wire Comparison](../map-00da-00e1-comparison/);
this extension adds only the job-byte/request join and the selector scan.

The same capture has one client-to-server `0x012d` request at frame 19,
stream offset 3416, subevent 0. Its event name is `commandRequest`, its
static-owner relation identifies 12017, and its typed tail begins at
application `+0x31` with integer `1`, eight nil values, and a terminator at
tail offset 13. The request and the job update have equal source fields, equal
destination fields, and all four wrapper actor fields equal. The application
`+4` low 16 value is retained as a numeric static-owner relation; it is not
treated as a serialized job mode.

Regenerate the extension with:

```text
python tools/extractors/extract_job_change_context.py
python tools/extractors/extract_job_change_context.py --check
python tools/extractors/extract_job_change_context.py --public-shape
```

## Combat stance request context

The retained `combat_skills.pcapng` has seven `0x012D` requests and four
`0x0134` state records on main connection 0. The request actor and the
state-record source are equal for the rows below. The other two state records
belong to a different actor.

| Completing packet | Direction | Frame / subevent | Stream offset | Observation |
| ---: | --- | --- | ---: | --- |
| 21 | c2s | 6 / 1 | 976 | `commandForced`, static-owner low 16 bits 21001. |
| 24 | s2c | 5 / 0 | 617 | `0x0134`, state byte 2. |
| 65 | c2s | 17 / 2 | 3120 | `commandDefault`, static-owner low 16 bits 27260. |
| 84 | c2s | 22 / 0 | 4032 | `commandDefault`, static-owner low 16 bits 27264. |
| 108 | c2s | 29 / 1 | 5168 | `commandDefault`, static-owner low 16 bits 27190. |
| 133 | c2s | 36 / 2 | 6240 | `commandDefault`, static-owner low 16 bits 27191. |
| 157 | c2s | 44 / 0 | 7640 | `commandDefault`, static-owner low 16 bits 27198. |
| 239 | c2s | 63 / 2 | 10488 | `commandForced`, static-owner low 16 bits 21002. |
| 244 | s2c | 105 / 0 | 13233 | `0x0134`, state byte 0. |

The static command catalog names 21001 Active Mode, 21002 Passive Mode,
27260 Invigorate, 27264 Blood for Blood and 27190 Heavy Swing
(`xivl-client-data:derived/command_battle_params.csv`, matching IDs).
The two forced requests have typed tail
`nil,nil,1,nil,nil,nil,nil,nil,nil`. Each of the five default requests has
`nil,0,1,nil,reference,nil,nil,nil,nil`; the selected reference is equal
across those five requests. Binding-reference equality with an actor ID is
not assigned here.

State 2 is the last observed same-actor state for all five default requests.
The state-0 publication follows the final forced request, with no later
non-stance request in this capture. This does not witness an action used
while passive, automatic weapon drawing or a passive command's server reply.
Packet completion order is observational, without a causal request/reply
association or a claim about server evaluation or rendering.

The [source manifest](../../sources/pcap-1.23b/manifest.yaml) pins the member
at 63,028 bytes, SHA-256
`7fe66d92f6f62584e57562e51355d310546935690e0b96c2c689b83bbe8a07a7`.
Frames and subevents are zero-based within each reconstructed direction;
completing packets are one-based. The selected decode retained 80 c2s and
117 s2c complete frames, zero admitted unparsed bytes and six discarded
trailing reconstructed s2c bytes. The independent framing check reported
zero trailing bytes and flag mismatches. These counters describe different
stages of the [decode contract](../../docs/pcap-decoding.md).

## Limits

The published payload samples zero-fill each event name of four or more letters.
The name join for those samples comes from the captures and is checked against
the samples byte for byte after the same zero-fill. Stream order covers only the
client-to-server direction.

## Not established

- Whether the zone field equals a zone id. No tracked product records the zone
  of each capture next to this field.
- The meaning of selector 101 and of the nonzero low 22 bits.
- The order of the client target messages against server messages.
- Whether the client sends `0x00cc` and `0x00cd` as part of the talk trigger or
  as a side effect of targeting.
- Whether the selector follows the trigger kind or the event name.
- Any trigger kind absent from the captures, including emote events.
- Whether the job-change context witness establishes server causality or the
  semantic role of `0x04000029`. The complete-corpus selector scan and native
  effect/resource evidence are separate bounded products.

Regenerate with `python tools/extractors/extract_c2s_012d_event_start.py`.
Use `--check` to compare regenerated bytes and `--public-shape` to validate
retained products without the captures.
