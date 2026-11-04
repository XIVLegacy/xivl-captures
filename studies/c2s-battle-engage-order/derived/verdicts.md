# Client Battle Engage and Disengage Order

Every figure below is aggregated from the client-to-server `0x00cc`,
`0x00cd`, and `0x012d` records in the retail captures and joined to the
server records that complete in later capture packets. The products hold
shape classes, counts, packet locators, field-value classes, and
millisecond deltas. They hold no actor ids, absolute timestamps, or raw
payloads.

## Record shapes

Offsets count from the first application byte after the 16-byte
game-message header.

| Record | Offset | Size | Field |
|---|---:|---:|---|
| c2s `0x00cc`, `0x00cd` | 0x00 | 4 | actor, or `0xc0000000` |
| c2s `0x00cc`, `0x00cd` | 0x04 | 4 | second dword |
| c2s `0x012d` | 0x04 | 4 | owner actor |
| c2s `0x012d` | 0x0c | 4 | parameter CRC |
| c2s `0x012d` | 0x11 | 32 | event name |
| c2s `0x012d` | 0x31 | 128 | typed parameter window |
| s2c `0x0139`-`0x013c` | 0x00 | 4 | source actor |
| s2c `0x0139`-`0x013c` | 0x24 | 2 | command id |
| s2c `0x0139`-`0x013c` | 0x28 | 4 | first target actor |
| s2c `0x00d2`, `0x00d3` | 0x00 | 4 | actor, or `0xc0000000` |

A `0x00cc` shape is `clear` when its actor field is `0xc0000000`.
Otherwise it is `actor, zero` or `actor, nonzero` by its second dword.
A `0x00cd` shape names the actor field as `self` when it equals the
wrapper source, `actor` otherwise, and the second dword as
`0xe0000000`, `same actor`, or `other`.

## Capture set

Captures with at least one counted record.

| Capture | SHA-256 | Counted records |
|---|---|---|
| `accept_leve.pcapng` | `42b87e6c095db130def1de5bc382e428b4f4c12c8069c4682d6fa4bc7681967a` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x3, 0x00cd clear, 0xe0000000 x1, 0x00cd self, 0xe0000000 x1 |
| `accept_local_leve.pcapng` | `3b4b071d88742a5d3c94a1e29ca6a4074cb6b9a9a60207118302fe22f932bd7c` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x2, 0x00cd clear, 0xe0000000 x1 |
| `accept_quest.pcapng` | `a207109240254b1398a36f877afc7ac34a08466cfbd3cdd3f2eb5f4a50718057` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x1, 0x00cd clear, 0xe0000000 x1 |
| `battle_mode_passive_mode.pcapng` | `5a8290df1d11781f4f5fa1f6990651c679e57ee3b8c5549021f06767bb172d4b` | mode 21001 x1, mode 21002 x1 |
| `buy_square_maple_shield.pcapng` | `aab582bd9658c89cd4d56e132500481f442b9f2dc2179f1a5829ea09776bce6b` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x2, 0x00cd clear, 0xe0000000 x1 |
| `checkbed.pcapng` | `9e05a05de6ec44eded13761fcb3546eb248c0c68e537051eef575e29dfff1b79` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x2, 0x00cd clear, 0xe0000000 x1 |
| `combat_autoattack.pcapng` | `2f677ab61047b25c4168a3dd9496f372d48de3bba018d582dd5a968b9272f7b2` | 0x00cc actor, nonzero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x1, 0x00cd actor, same actor x1, 0x00cd clear, 0xe0000000 x1, mode 21001 x1, mode 21002 x1 |
| `combat_skills.pcapng` | `7fe66d92f6f62584e57562e51355d310546935690e0b96c2c689b83bbe8a07a7` | 0x00cc actor, nonzero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x1, 0x00cd actor, same actor x1, 0x00cd clear, 0xe0000000 x1, mode 21001 x1, mode 21002 x1 |
| `cutscene_book.pcapng` | `c2cf85e02d8d15fe2aa9261e8b796c29c0a3d9dd9cdf287ce0f75f3a666b2b4d` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x2, 0x00cd clear, 0xe0000000 x1 |
| `gather_wood.pcapng` | `c308aa4c984eb3e1912383c06e5115c6924713978df43cdb8075335e1bac7d32` | 0x00cd actor, 0xe0000000 x1, 0x00cd clear, 0xe0000000 x1 |
| `local_leve_complete.pcapng` | `4f0793f354140478725bf2c30642a3458a854460f47fb11a7af635c8881d95cd` | 0x00cc actor, zero x2, 0x00cc clear x2, 0x00cd actor, 0xe0000000 x4, 0x00cd clear, 0xe0000000 x2 |
| `move_out_of_room.pcapng` | `a7a03a1d688f3feb264f8da9fae3519c55b7e267aa3802472f0221f4d729b37b` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x2, 0x00cd clear, 0xe0000000 x1 |
| `party_battle_leve.pcapng` | `6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f` | 0x00cc actor, nonzero x12, 0x00cc actor, zero x2, 0x00cc clear x14, 0x00cd actor, 0xe0000000 x17, 0x00cd actor, same actor x14, 0x00cd clear, 0xe0000000 x18, 0x00cd self, 0xe0000000 x5, 0x00cd self, same actor x5, mode 21001 x7, mode 21002 x7 |
| `quest_update.pcapng` | `e31aa9738dd523b7703eefa6d38527135f16d8b5ff2fc314fd7e5b808d7e4787` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x2, 0x00cd clear, 0xe0000000 x1 |
| `repair_items.pcapng` | `bbd829cbd3f42b2cbfb3aa8a74a1cc35d4e2c16c99e5a4a20ca76573f02dd90f` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x2, 0x00cd clear, 0xe0000000 x1 |
| `sell_item.pcapng` | `1cd808fff6501c53e4c113f1fdef090e50dfe0fd7fe86ceaa552b3a53c1b5aac` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x2, 0x00cd clear, 0xe0000000 x1 |
| `small_talk_louisoix.pcapng` | `58b620d90370ba69202e63f7f70edb79004ccbb8068e11e2e112a825d84dcafe` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x2, 0x00cd clear, 0xe0000000 x1 |
| `war_quest_update1.pcapng` | `ce64e429063cc7e49a2045e2f7b0e18b1991f5908368b791b93c72419841e890` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x1, 0x00cd clear, 0xe0000000 x1 |
| `war_quest_update2.pcapng` | `bf43b5ee32c58e5dc6f8149b071bd9c5cd5cc0aaa55ea3528872308fd7be2429` | 0x00cc actor, nonzero x2, 0x00cc clear x2, 0x00cd actor, 0xe0000000 x2, 0x00cd actor, same actor x2, 0x00cd clear, 0xe0000000 x2, mode 21001 x2, mode 21002 x2 |
| `war_quest_update3.pcapng` | `52279e8cbc13d3f4751b5ee3cb9c91df1895ed5c41d30672629db3ec1c9efd05` | 0x00cc actor, zero x1, 0x00cc clear x1, 0x00cd actor, 0xe0000000 x2, 0x00cd clear, 0xe0000000 x1 |

## EventStart census

| Quantity | Messages |
|---|---:|
| c2s `0x012d` messages | 126 |
| CRC field equals zlib CRC-32 of the 128-byte parameter window | 126 |
| owner low 16 bits equal attack command 22104 | 0 |

## Mode requests

c2s `0x012d` messages whose owner is static command 21001 or 21002.
Typed tags are `0x05` nil, `0x00` int, `0x06` actor reference, and
`0x0f` end. An actor reference is named by its relation to the most
recent actor `0x00cc`.

| Command | Event name | Selector | Trigger is sender | Typed tail | CRC | Messages |
|---:|---|---:|---|---|---|---:|
| 21001 | `commandForced` | 0 | True | nil,nil,int 1,nil,nil,nil,nil,nil,nil | `0xbbbac113` | 12 |
| 21002 | `commandForced` | 0 | True | nil,nil,int 1,nil,actor=lock target,nil,nil,nil,nil | `0x8e123be4` | 1 |
| 21002 | `commandForced` | 0 | True | nil,nil,int 1,nil,nil,nil,nil,nil,nil | `0xbbbac113` | 11 |

The reply frame is the s2c frame holding the first `commandForced`
`0x0131` from the requester after the request. It lists that frame's
requester records in subevent order. Prior state is the first byte of
the last s2c `0x0134` from the requester before the request.

| Command | Prior state | Typed tail | Reply frame | Requests |
|---:|---|---|---|---:|
| 21001 | 00 | nil,nil,int 1,nil,nil,nil,nil,nil,nil | 0x0134 02 bf + 0x0139 command=request + 0x0131 commandForced | 7 |
| 21001 | none | nil,nil,int 1,nil,nil,nil,nil,nil,nil | 0x0134 02 bf + 0x0139 command=request + 0x0131 commandForced | 5 |
| 21002 | 02 | nil,nil,int 1,nil,nil,nil,nil,nil,nil | 0x0134 00 bf + 0x0139 command=request + 0x0131 commandForced | 11 |
| 21002 | 03 | nil,nil,int 1,nil,actor=lock target,nil,nil,nil,nil | 0x0131 commandForced | 1 |

| Quantity | n | min | median | max |
|---|---:|---:|---:|---:|
| Request to reply, ms | 24 | 289 | 558.5 | 589 |

c2s `0x00cc` or `0x00cd` records completing between a request and its
reply: 0.

## Lock records

Mode is the most recent mode request in client stream order, or `none`.
The next record is the following c2s record in the same frame.

| Shape | Mode | Same-frame next record | Records |
|---|---|---|---:|
| actor, nonzero | 21001 | 0x00cd actor, same actor | 16 |
| actor, zero | 21002 | 0x012d talkDefault | 1 |
| actor, zero | none | 0x00cd actor, 0xe0000000 | 1 |
| actor, zero | none | 0x012d talkDefault | 15 |
| clear | 21001 | 0x00cd clear, 0xe0000000 | 15 |
| clear | 21002 | 0x00cd clear, 0xe0000000 | 2 |
| clear | none | 0x00ca | 1 |
| clear | none | 0x00cd clear, 0xe0000000 | 15 |

Second dword values. A value equal to an actor id seen in the same
capture would print as `actor id`.

| Shape | Value | Records |
|---|---|---:|
| actor, nonzero | `0x00000040` | 3 |
| actor, nonzero | `0x0466e6a4` | 12 |
| actor, nonzero | `0x048ae2a4` | 1 |
| actor, zero | `0x00000000` | 17 |
| clear | `0x00000000` | 17 |
| clear | `0x00000020` | 1 |
| clear | `0x00000040` | 2 |
| clear | `0x00000058` | 2 |
| clear | `0x008b000a` | 1 |
| clear | `0x00cf97aa` | 1 |
| clear | `0x03918eb0` | 8 |
| clear | `0x65440100` | 1 |

## Set records

| Shape | Records |
|---|---:|
| actor, 0xe0000000 | 51 |
| actor, same actor | 18 |
| clear, 0xe0000000 | 38 |
| self, 0xe0000000 | 6 |
| self, same actor | 5 |

## Engage order

One row per `actor, nonzero` lock. The select is the nearest earlier
c2s `0x00cd` with the same actor and `0xe0000000`, searched back to the
previous `0x00cc` of any shape. Frame shapes omit `0x00ca`. The search
window for the server records runs from the lock to the next `actor,
zero` or `actor, nonzero` lock. A clear inside the window does not end
it. Clear is the first clear lock in the window. Attack is the first s2c
result from the sender with command 22104 and the lock actor as first
target. A trailing `*` marks a record that completes after the clear.
Deltas are milliseconds between completing capture packets.

| Capture | Select frame / packet | Lock frame / packet | Frame gap | Select to lock | Lock to `0x00d2` | Lock to clear | Lock to attack | Lock frame shape |
|---|---|---|---:|---:|---:|---:|---:|---|
| `combat_autoattack.pcapng` | 12 / 29 | 13 / 46 | 1 | 365 | 564 | 30843 | 2765 | 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `combat_skills.pcapng` | 10 / 44 | 11 / 47 | 1 | 365 | 561 | 19760 | 5170 | 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `party_battle_leve.pcapng` | 230 / 662 | 231 / 664 | 1 | 364 | 561 | 20342 | 1292 | 0x00cc actor, nonzero + 0x00cd actor, same actor + 0x0001 |
| `party_battle_leve.pcapng` | 290 / 834 | 291 / 837 | 1 | 334 | 528 | 23737 | 1258 | 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `party_battle_leve.pcapng` | 871 / 2583 | 872 / 2586 | 1 | 337 | 529 | 23839 | 529 | 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `party_battle_leve.pcapng` | 933 / 2775 | 934 / 2777 | 1 | 364 | 530 | 28369 | 1486 | 0x00cc actor, nonzero + 0x00cd actor, same actor + 0x0001 |
| `party_battle_leve.pcapng` | 1176 / 3481 | 1176 / 3481 | 0 | 0 | 226 | 20230 | 1931 | 0x00cd actor, 0xe0000000 + 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `party_battle_leve.pcapng` | 1282 / 3814 | 1283 / 3816 | 1 | 365 | 528 | 29282 | 893 | 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `party_battle_leve.pcapng` | 1355 / 4085 | 1356 / 4088 | 1 | 334 | 559* | 365 | 896* | 0x00cc actor, nonzero + 0x00cd actor, same actor + 0x0001 |
| `party_battle_leve.pcapng` | 1359 / 4094 | 1360 / 4096 | 1 | 333 | 529 | 7806 | 3781 | 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `party_battle_leve.pcapng` | 1385 / 4159 | 1386 / 4161 | 1 | 366 | 529 | 28946 | 3323 | 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `party_battle_leve.pcapng` | 1518 / 4564 | 1519 / 4567 | 1 | 335 | 560 | 23804 | 892 | 0x0001 + 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `party_battle_leve.pcapng` | 1579 / 4784 | 1580 / 4788 | 1 | 333 | 476 | 36865 | 476 | 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `party_battle_leve.pcapng` | - | 1688 / 5155 | - | - | 545 | 4354 | - | 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `war_quest_update2.pcapng` | 90 / 245 | 92 / 250 | 2 | 667 | 561 | 1033 | - | 0x00cc actor, nonzero + 0x00cd actor, same actor |
| `war_quest_update2.pcapng` | 96 / 258 | 101 / 269 | 5 | 1794 | 527 | 5585 | - | 0x00cc actor, nonzero + 0x00cd actor, same actor + 0x012d commandDefault |

| Quantity | Value |
|---|---:|
| `actor, nonzero` locks | 16 |
| with a select | 15 |
| select in the lock frame | 1 |
| `0x00d3` for the actor completes before the lock | 4 |
| with a clear before the next actor lock | 16 |
| with a later `0x00d2` for the actor | 16 |
| first `0x00d2` completes after the clear | 1 |
| with a later attack result | 13 |
| first attack result completes after the clear | 1 |
| with an attack result after the clear | 2 |
| attack results after the clear | 2 |
| first attack result on `0x0139` | 13 |

| Interval, ms | n | min | median | max |
|---|---:|---:|---:|---:|
| select to lock, select in an earlier frame | 14 | 333 | 364 | 1794 |
| lock to first `0x00d2` | 16 | 226 | 529.5 | 564 |
| lock to first attack | 13 | 476 | 1292 | 5170 |
| clear to each attack result after it | 2 | 196 | 363.5 | 531 |

| Select frame shape | Selects |
|---|---:|
| 0x0001 + 0x00cd actor, 0xe0000000 | 3 |
| 0x00cc clear + 0x00cd clear, 0xe0000000 + 0x00cd actor, 0xe0000000 + 0x0133 + 0x0133 + 0x0133 | 1 |
| 0x00cd actor, 0xe0000000 | 5 |
| 0x00cd actor, 0xe0000000 + 0x0001 | 5 |
| 0x00cd actor, 0xe0000000 + 0x00cc actor, nonzero + 0x00cd actor, same actor | 1 |

| Lock frame shape | Locks |
|---|---:|
| 0x0001 + 0x00cc actor, nonzero + 0x00cd actor, same actor | 1 |
| 0x00cc actor, nonzero + 0x00cd actor, same actor | 10 |
| 0x00cc actor, nonzero + 0x00cd actor, same actor + 0x0001 | 3 |
| 0x00cc actor, nonzero + 0x00cd actor, same actor + 0x012d commandDefault | 1 |
| 0x00cd actor, 0xe0000000 + 0x00cc actor, nonzero + 0x00cd actor, same actor | 1 |

c2s records completing after the lock frame and before the first attack,
for locks whose first attack completes before any clear.

| Record | Records |
|---|---:|
| 0x0001 | 22 |
| 0x00ca | 113 |
| 0x012d commandDefault | 2 |

## Clear records

One row group per `clear` lock. After lock is the shape of the most
recent actor lock. Next mode is the first mode request before the next
actor lock. Echo names the first s2c `0x00d2` and `0x00d3` for
`0xc0000000` after the clear.

| After lock | Same-frame next record | Next mode | Echo | Records |
|---|---|---|---|---:|
| actor, nonzero | 0x00cd clear, 0xe0000000 | 21002 | 0x00d2 then 0x00d3, one frame | 7 |
| actor, nonzero | 0x00cd clear, 0xe0000000 | none | 0x00d2 then 0x00d3, one frame | 9 |
| actor, zero | 0x00ca | none | other | 1 |
| actor, zero | 0x00cd clear, 0xe0000000 | 21001 | 0x00d2 then 0x00d3, one frame | 1 |
| actor, zero | 0x00cd clear, 0xe0000000 | none | 0x00d2 then 0x00d3, one frame | 15 |

| Interval, ms | n | min | median | max |
|---|---:|---:|---:|---:|
| clear after `actor, nonzero` to next mode request | 7 | 1096 | 5278 | 10632 |

## Talk starts

Same-frame neighbors of each `talkDefault` c2s `0x012d`. Owner columns
say whether the neighbor's actor field equals the EventStart owner.

| Selector | Previous record | Previous is owner | Next record | Next is owner | Messages |
|---:|---|---|---|---|---:|
| 1 | 0x00cc actor, zero | True | 0x00cd actor, 0xe0000000 | True | 16 |
| 101 | 0x00ca | False | 0x00cc clear | False | 1 |

## Same-actor set records

Every c2s `0x00cd` whose second dword equals its actor field.

| After same-frame lock | Self | Mode | Same-frame next record | Records |
|---|---|---|---|---:|
| False | False | 21001 | frame end | 1 |
| False | False | 21002 | 0x00ca | 1 |
| False | True | 21001 | 0x0001 | 1 |
| False | True | 21001 | 0x00ca | 1 |
| False | True | 21001 | 0x012d commandDefault | 1 |
| False | True | 21002 | 0x00ca | 1 |
| False | True | 21002 | 0x012d commandDefault | 1 |
| True | False | 21001 | 0x0001 | 3 |
| True | False | 21001 | 0x00ca | 11 |
| True | False | 21001 | 0x012d commandDefault | 1 |
| True | False | 21001 | frame end | 1 |
