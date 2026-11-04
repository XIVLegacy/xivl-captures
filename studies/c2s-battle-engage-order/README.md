# Client Battle Engage and Disengage Order

This study records the order in which the retail client sends its battle
mode, target, and lock records, and what the server sends back. It covers
every client-to-server `0x00cc` LockTargetPacket, `0x00cd` SetTargetPacket,
and `0x012d` EventStartPacket in the 54 captures of `pcap-1.23b`. Names come
from xivl-opcodes:opcodes.json through the
[adopted opcode snapshot](../../derived/opcode_names.json). Each client record
is joined to the server records that complete in later capture packets.

The labels select, lock, decide, and clear name record shapes. They are not
claims about client intent.

| Label | Record shape |
|---|---|
| select | c2s `0x00cd` with an actor id and second dword `0xe0000000` |
| lock | c2s `0x00cc` with an actor id and a nonzero second dword |
| talk lock | c2s `0x00cc` with an actor id and a zero second dword |
| decide | c2s `0x00cd` whose second dword equals its actor id |
| clear | c2s `0x00cc` or `0x00cd` whose actor field is `0xc0000000` |

The client sheet `xivl-client-data:derived/command_battle_params.csv` names
static command 21001 Active Mode, 21002 Passive Mode, and 22104 Attack, with
script `/Command/Game/AttackCommand`. A mode request is a c2s `0x012d` whose owner is `0xa0f05209` for 21001 or
`0xa0f0520a` for 21002.

## Findings

- Every lock follows an Active Mode request. All 16 locks in the corpus
  carry mode 21001 as the most recent mode request in client order. They
  fall in `combat_autoattack.pcapng`, `combat_skills.pcapng`,
  `party_battle_leve.pcapng`, and `war_quest_update2.pcapng`. No c2s
  `0x00cc` or `0x00cd` completes between any of the 24 mode requests and its
  server reply.
- All 24 mode requests are `commandForced` with selector 0, and the trigger
  actor equals the wrapper source. 23 carry the typed tail
  `nil,nil,int 1,nil,nil,nil,nil,nil,nil` and CRC `0xbbbac113`. One 21002
  request in `war_quest_update2.pcapng` carries, in the fifth slot, an actor
  reference equal to the actor of the most recent lock, and CRC
  `0x8e123be4`.
- The CRC field at application offset 0x0c equals the zlib CRC-32 of the
  128-byte parameter window at offset 0x31 in 126 of 126 c2s `0x012d`
  messages. This extends to every EventStart in the corpus the five-request
  CRC32 result in [Director Wire Identity](../director-wire-identity/README.md)
  and the parameter CRC32 field named in the
  [c2s EventStart verdicts](../c2s-012d-event-start/derived/verdicts.md).
- The reply to all 12 Active Mode requests is one s2c frame whose records
  from the requester are, in order, `0x0134` with state byte 2 and second
  byte `0xbf`, a `0x0139` whose command id is 21001, and a `commandForced`
  `0x0131` EndEvent. 11 of 12 Passive Mode replies hold the same three
  requester records with state byte 0. The twelfth is the reply to the one
  Passive Mode request with an actor reference in its tail. Its frame holds
  only the EndEvent among the requester's records, and the last `0x0134`
  before that request carried state byte 3. Request to reply takes 289 to
  589 ms.
- A lock is followed in the same frame by a decide on the same actor in 16
  of 16 locks. Once in `war_quest_update2.pcapng` the same frame also
  carries a `commandDefault` EventStart after the decide.
- 15 of 16 locks have a select on the same actor earlier in the client
  stream. 12 sit in the previous frame, 333 to 366 ms before the lock. One
  each sits 2 and 5 frames earlier, at 667 and 1794 ms. One select shares
  the lock frame. 13 of the 15 select frames hold no other target or event
  record, only `0x0001` PingPacket or `0x00ca` position records. The
  remaining lock has no select since the previous `0x00cc`.
- The server-record window for a lock runs to the next talk lock or lock,
  and a clear inside it does not end it. Every one of the 16 locks has a
  clear in its window.
- The client sends no attack request. No c2s `0x012d` in the corpus has an
  owner whose low 16 bits are 22104. For 13 of 16 locks, an s2c `0x0139`
  from the sender with command 22104 and the lock actor as first target
  completes in the window, the first 476 to 5170 ms after the lock, median
  1292 ms. In `combat_autoattack.pcapng` it takes 2765 ms. For 12 of the 13
  the first one completes before the clear. Between each of those 12 lock
  frames and the first result the client sends only `0x0001`, `0x00ca`, and
  in `combat_skills.pcapng` two `commandDefault` EventStarts.
- The server can send an attack result onto the actor after the client
  clears. In `party_battle_leve.pcapng` the client clears 365 ms after the
  lock in c2s frame 1356, and the first 22104 result onto that actor
  completes 531 ms after the clear. After the clear that follows the lock in
  c2s frame 1360, one more 22104 result onto that lock's actor completes
  196 ms after the clear.
- s2c `0x00d2` naming the lock actor follows all 16 locks in the window, 226
  to 564 ms after the lock. For the lock in c2s frame 1356 it completes 559
  ms after the lock, after the clear. s2c `0x00d3` naming the select actor
  completes before the lock for 4 of the 15 selects.
- Disengage is one frame of a clear `0x00cc` followed by `0x00cd`
  `{0xc0000000, 0xe0000000}`. All 16 clears that follow a lock have that
  frame shape. After each of them, the first s2c `0x00d2` and `0x00d3` for
  `0xc0000000` complete in one frame, `0x00d2` first. 7 of those 16 clears
  are followed by a Passive Mode request before the next lock, 1096 to
  10632 ms later.
- No talk lock falls under Active Mode. 16 of 17 have no earlier mode
  request in their capture and one follows Passive Mode. 16 are followed in
  the same frame by a `talkDefault` EventStart. The other one, in
  `cutscene_book.pcapng`, is followed by a select on the same actor and no
  EventStart.
- After 16 of 17 `talkDefault` EventStarts, the next record in the same frame
  is a select on the EventStart owner. The seventeenth, selector 101, is
  followed by a clear lock.
- Lock second dwords take three values: `0x0466e6a4` 12 times,
  `0x00000040` 3 times, and `0x048ae2a4` once. Clear locks carry 0 in 17 of
  33 and seven other values in the rest. None equals an actor id from the
  same capture.

[Verdicts](derived/verdicts.md) holds every table and the per-lock rows.
[Accounting](derived/accounting.json) holds the same figures in machine form.

## Claim tiers

MEASURED claims are counts over the decoded captures. INFERRED claims read a
measured pattern as a rule. UNKNOWN items have no supporting record.

| Claim | Tier | Locator |
|---|---|---|
| Every lock follows an Active Mode request | MEASURED | `locks`, shape `actor, nonzero` |
| Mode request tail shape and CRC | MEASURED | `mode_requests` |
| CRC field is zlib CRC-32 of the parameter window | MEASURED | `event_start_crc` |
| Mode reply frame order and state bytes | MEASURED | `mode_replies` |
| Lock then decide in one frame | MEASURED | `engage_summary.lock_frame_shapes` |
| A select precedes 15 of 16 locks, one frame earlier for 12 | MEASURED | `engage_summary.select_frame_gap` |
| No client attack request | MEASURED | `event_start_crc`, `engage_summary.c2s_before_attack` |
| 22104 result after 13 of 16 locks and `0x00d2` after 16, window to the next actor lock | MEASURED | `engage_summary.with_attack`, `engage_summary.with_d2` |
| Attack results onto the actor after the clear, 2 results | MEASURED | `engage_summary.attacks_after_clear`, `engages[].clear_to_attack_ms` |
| Server starts the attack after the lock | INFERRED | `engages[].first_attack_ms` |
| Disengage frame and its echo | MEASURED | `clears` |
| Talk lock precedes `talkDefault`, select trails it | MEASURED | `talk_starts` |
| Lock second dword distribution | MEASURED | `lock_second_dword` |
| Meaning of the lock second dword | UNKNOWN | none |

## Limits

Cross-direction order is the order of the earliest capture packet that
completes each outer frame. It is a capture-arrival witness, not server
causality. Millisecond deltas are differences between those packet
timestamps. Client stream order covers one connection and one direction, as
the [decode contract](../../docs/pcap-decoding.md#order-and-validation-limits)
states.

## Not established

- The meaning of the lock second dword and of the int 1 in the mode tail.
- Whether the client waits for the mode reply before it sends a lock. No
  capture has a target record between a request and its reply.
- Whether the client sends a lock on a hostile actor while in Passive Mode.
  No capture has one.
- Which input produced each lock, and the server rule that times the first
  attack.
- The meaning of `0x00d2` and `0x00d3`, and why the Passive Mode reply after
  state 3 holds only the EndEvent.
- Whether the client acts on an attack result that arrives after its clear.

Regenerate with `python tools/extractors/extract_c2s_battle_engage_order.py`.
Use `--check` to compare regenerated bytes and `--public-shape` to validate
retained products without the captures.
