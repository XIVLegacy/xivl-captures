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
