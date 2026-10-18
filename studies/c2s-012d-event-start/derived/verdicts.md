# Client EventStart 0x012D Joins

Every figure below is aggregated from the sent client-to-server `0x012d`
messages in the retail captures. The products hold counts only. They hold
no actor ids, timestamps, or payload bytes.

## Record shape

Every message is 200 bytes: the 16-byte game-message
header and a 184-byte payload. Offsets below count from the first byte of
the header. The payload offset is the header offset minus 16.

| Offset | Size | Field |
|---:|---:|---|
| 0x10 | 4 | trigger actor |
| 0x14 | 4 | owner actor |
| 0x18 | 4 | server codes |
| 0x1c | 4 | parameter CRC32 |
| 0x20 | 1 | selector |
| 0x21 | 32 | event name, zero padded |
| 0x41 | 128 | parameter window |

The selector is the byte at payload offset 0x10. The server codes field is
split into a zone field, its high 10 bits, and the low 22 bits.

## Capture set

126 messages in 39 captures. The published
payload samples hold 60 of them. The sampler keeps at most 4
per capture, in stream order, from the captures in file name order.

| Capture | SHA-256 | Messages |
|---|---|---:|
| `accept_leve.pcapng` | `42b87e6c095db130def1de5bc382e428b4f4c12c8069c4682d6fa4bc7681967a` | 1 |
| `accept_local_leve.pcapng` | `3b4b071d88742a5d3c94a1e29ca6a4074cb6b9a9a60207118302fe22f932bd7c` | 1 |
| `accept_quest.pcapng` | `a207109240254b1398a36f877afc7ac34a08466cfbd3cdd3f2eb5f4a50718057` | 1 |
| `action_and_traits.pcapng` | `c3d30fe46d69996dc74e4864245c42675cde2388525c03063dac180df528352f` | 2 |
| `add_str.pcapng` | `246e4948a7ca1e4dc620e724677bfd9153ce76f6445a557967d309e9946021ed` | 1 |
| `battle_mode_passive_mode.pcapng` | `5a8290df1d11781f4f5fa1f6990651c679e57ee3b8c5549021f06767bb172d4b` | 2 |
| `buy_square_maple_shield.pcapng` | `aab582bd9658c89cd4d56e132500481f442b9f2dc2179f1a5829ea09776bce6b` | 1 |
| `change_bodyarmor.pcapng` | `55ee6035d24e80b97c9354a0800b86a52d0a99e1200cf6875a5b56009215021a` | 1 |
| `change_helm.pcapng` | `af1e465076c3acf6188f24f084622b22beccc932bb96effd517b2d9a44606e08` | 2 |
| `change_to_botanist.pcapng` | `8fdc448a17d19bea3d07855a8d8843d78926c50586f3656946c96b6a6cb27d26` | 2 |
| `checkbed.pcapng` | `9e05a05de6ec44eded13761fcb3546eb248c0c68e537051eef575e29dfff1b79` | 1 |
| `combat_autoattack.pcapng` | `2f677ab61047b25c4168a3dd9496f372d48de3bba018d582dd5a968b9272f7b2` | 2 |
| `combat_skills.pcapng` | `7fe66d92f6f62584e57562e51355d310546935690e0b96c2c689b83bbe8a07a7` | 7 |
| `emote_dance.pcapng` | `9e004f1e791cfc37b7d23e8986a5e69021b7b7f828295fdf7957e36aa1c57dc8` | 1 |
| `emote_kneel.pcapng` | `3381b6121f5b0789c97ededdc5394c6bc9b14c561029191fb5b3f428033c80e8` | 1 |
| `from_gridania_to_blackshroud.pcapng` | `eff300de679230653953ea3399939a15ce9d6aeafd202c7ebcf5f55e6d24930f` | 2 |
| `gather_wood.pcapng` | `c308aa4c984eb3e1912383c06e5115c6924713978df43cdb8075335e1bac7d32` | 2 |
| `gear_changesoul.pcapng` | `62af2cde3a4683fba3e09cc3dfed8001d74303b120381de577b05df492926780` | 1 |
| `gear_changeweapon.pcapng` | `3eec2c2993feeb2b8c47c1e1f553335638a7262ec13b561e2d52d768f0798080` | 1 |
| `gridania_to_coerthas.pcapng` | `63152a1ed6e446df5cc4750fe50a0839f9e45ad270c79abfc72b5c09cc47e547` | 6 |
| `harvest.pcapng` | `8522a844b6904207c3465ae1d1038599eddb8b9dc47800d5230c8a1c3ad0e440` | 4 |
| `invite_join_party.pcapng` | `34c946c3f93744d2bbd841e75f983ef12b9bbcb59afcba31414d6d3f41e7de58` | 1 |
| `local_leve_complete.pcapng` | `4f0793f354140478725bf2c30642a3458a854460f47fb11a7af635c8881d95cd` | 3 |
| `mount_unmount_chocobo.pcapng` | `e77c06799f07029feb054792eac30baa431da15a61937b1a39bcd025e4db4072` | 2 |
| `move_out_of_room.pcapng` | `a7a03a1d688f3feb264f8da9fae3519c55b7e267aa3802472f0221f4d729b37b` | 1 |
| `party_battle_leve.pcapng` | `6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f` | 55 |
| `quest_journal.pcapng` | `e1f983e9009a9ebe8b8231647229bee1672a1ac85d95a830113280f534531edc` | 2 |
| `quest_update.pcapng` | `e31aa9738dd523b7703eefa6d38527135f16d8b5ff2fc314fd7e5b808d7e4787` | 1 |
| `repair_items.pcapng` | `bbd829cbd3f42b2cbfb3aa8a74a1cc35d4e2c16c99e5a4a20ca76573f02dd90f` | 1 |
| `return_to_inn.pcapng` | `9a81e483d3dd2673081afef06ed521c190c4d42be16e95e24097f25ff81f58c1` | 1 |
| `sell_item.pcapng` | `1cd808fff6501c53e4c113f1fdef090e50dfe0fd7fe86ceaa552b3a53c1b5aac` | 1 |
| `small_talk_louisoix.pcapng` | `58b620d90370ba69202e63f7f70edb79004ccbb8068e11e2e112a825d84dcafe` | 1 |
| `switch_to_weaver.pcapng` | `b41b25bc51be1a64f41861142dc992c14493c65bcd920cadca013243480b777e` | 1 |
| `teleport_to_camp_nine_ivies.pcapng` | `fac2b485608247d299a406a7065e19918789118e7e544ca85cec4d772da0e3ab` | 1 |
| `teleport_to_camp_tranquil.pcapng` | `488318351cdedb2e2b650dc68c55014b160fbbc26753c200922402c1ba6c4dd7` | 1 |
| `teleport_to_gridania.pcapng` | `779141dc79a4bcf4bfc2e265f8b9510607d5a6b6e78d32f8940e5a847e598fa0` | 1 |
| `war_quest_update1.pcapng` | `ce64e429063cc7e49a2045e2f7b0e18b1991f5908368b791b93c72419841e890` | 1 |
| `war_quest_update2.pcapng` | `bf43b5ee32c58e5dc6f8149b071bd9c5cd5cc0aaa55ea3528872308fd7be2429` | 9 |
| `war_quest_update3.pcapng` | `52279e8cbc13d3f4751b5ee3cb9c91df1895ed5c41d30672629db3ec1c9efd05` | 1 |

## Selector by event name

All messages.

| Event name | selector 0 | selector 1 | selector 2 | selector 5 | selector 101 | Messages |
|---|---:|---:|---:|---:|---:|---:|
| `caution` | 0 | 0 | 3 | 0 | 0 | 3 |
| `commandContent` | 4 | 0 | 0 | 0 | 0 | 4 |
| `commandDefault` | 44 | 0 | 0 | 0 | 0 | 44 |
| `commandForced` | 28 | 0 | 0 | 0 | 0 | 28 |
| `commandJudgeMode` | 5 | 0 | 0 | 0 | 0 | 5 |
| `commandRequest` | 19 | 0 | 0 | 0 | 0 | 19 |
| `exit` | 0 | 0 | 3 | 0 | 0 | 3 |
| `noticeEvent` | 0 | 0 | 0 | 1 | 1 | 2 |
| `regionChange` | 0 | 0 | 1 | 0 | 0 | 1 |
| `talkDefault` | 0 | 16 | 0 | 0 | 1 | 17 |

The 60 published payload samples zero-fill every event name of four or more
letters, so the name join below comes from the captures and is checked
against the samples byte for byte after the same zero-fill.

Published samples only.

| Event name | selector 0 | selector 1 | selector 2 | Messages |
|---|---:|---:|---:|---:|
| `caution` | 0 | 0 | 2 | 2 |
| `commandContent` | 4 | 0 | 0 | 4 |
| `commandDefault` | 5 | 0 | 0 | 5 |
| `commandForced` | 10 | 0 | 0 | 10 |
| `commandJudgeMode` | 5 | 0 | 0 | 5 |
| `commandRequest` | 17 | 0 | 0 | 17 |
| `exit` | 0 | 0 | 2 | 2 |
| `regionChange` | 0 | 0 | 1 | 1 |
| `talkDefault` | 0 | 14 | 0 | 14 |

## Server codes

| Quantity | All messages | Published samples |
|---|---:|---:|
| Low 22 bits zero | 117 | 60 |
| Low 22 bits nonzero | 9 | 0 |

Zone field values, with message counts.

| Zone field | All messages | Published samples |
|---:|---:|---:|
| 145 | 3 | 2 |
| 150 | 15 | 15 |
| 151 | 1 | 1 |
| 152 | 2 | 1 |
| 154 | 12 | 9 |
| 155 | 11 | 11 |
| 162 | 55 | 4 |
| 172 | 11 | 1 |
| 206 | 3 | 3 |
| 244 | 13 | 13 |

## Joins

Event name, selector, zone field, and low 22 bits, with message counts.

All messages.

| Event name | Selector | Zone field | Low 22 bits | Messages |
|---|---:|---:|---:|---:|
| `caution` | 2 | 155 | 0 | 2 |
| `caution` | 2 | 172 | 60 | 1 |
| `commandContent` | 0 | 145 | 0 | 1 |
| `commandContent` | 0 | 150 | 0 | 1 |
| `commandContent` | 0 | 154 | 0 | 1 |
| `commandContent` | 0 | 206 | 0 | 1 |
| `commandDefault` | 0 | 154 | 0 | 5 |
| `commandDefault` | 0 | 162 | 0 | 38 |
| `commandDefault` | 0 | 172 | 60 | 1 |
| `commandForced` | 0 | 150 | 0 | 2 |
| `commandForced` | 0 | 154 | 0 | 6 |
| `commandForced` | 0 | 162 | 0 | 14 |
| `commandForced` | 0 | 172 | 60 | 4 |
| `commandForced` | 0 | 244 | 0 | 2 |
| `commandJudgeMode` | 0 | 145 | 0 | 1 |
| `commandJudgeMode` | 0 | 150 | 0 | 4 |
| `commandRequest` | 0 | 145 | 0 | 1 |
| `commandRequest` | 0 | 150 | 0 | 6 |
| `commandRequest` | 0 | 152 | 0 | 1 |
| `commandRequest` | 0 | 155 | 0 | 2 |
| `commandRequest` | 0 | 244 | 0 | 9 |
| `exit` | 2 | 155 | 0 | 2 |
| `exit` | 2 | 172 | 60 | 1 |
| `noticeEvent` | 5 | 172 | 60 | 1 |
| `noticeEvent` | 101 | 172 | 60 | 1 |
| `regionChange` | 2 | 152 | 0 | 1 |
| `talkDefault` | 1 | 150 | 0 | 2 |
| `talkDefault` | 1 | 151 | 0 | 1 |
| `talkDefault` | 1 | 155 | 0 | 5 |
| `talkDefault` | 1 | 162 | 0 | 2 |
| `talkDefault` | 1 | 172 | 0 | 2 |
| `talkDefault` | 1 | 206 | 0 | 2 |
| `talkDefault` | 1 | 244 | 0 | 2 |
| `talkDefault` | 101 | 162 | 0 | 1 |

Published samples only.

| Event name | Selector | Zone field | Low 22 bits | Messages |
|---|---:|---:|---:|---:|
| `caution` | 2 | 155 | 0 | 2 |
| `commandContent` | 0 | 145 | 0 | 1 |
| `commandContent` | 0 | 150 | 0 | 1 |
| `commandContent` | 0 | 154 | 0 | 1 |
| `commandContent` | 0 | 206 | 0 | 1 |
| `commandDefault` | 0 | 154 | 0 | 3 |
| `commandDefault` | 0 | 162 | 0 | 2 |
| `commandForced` | 0 | 150 | 0 | 2 |
| `commandForced` | 0 | 154 | 0 | 5 |
| `commandForced` | 0 | 162 | 0 | 1 |
| `commandForced` | 0 | 244 | 0 | 2 |
| `commandJudgeMode` | 0 | 145 | 0 | 1 |
| `commandJudgeMode` | 0 | 150 | 0 | 4 |
| `commandRequest` | 0 | 150 | 0 | 6 |
| `commandRequest` | 0 | 155 | 0 | 2 |
| `commandRequest` | 0 | 244 | 0 | 9 |
| `exit` | 2 | 155 | 0 | 2 |
| `regionChange` | 2 | 152 | 0 | 1 |
| `talkDefault` | 1 | 150 | 0 | 2 |
| `talkDefault` | 1 | 151 | 0 | 1 |
| `talkDefault` | 1 | 155 | 0 | 5 |
| `talkDefault` | 1 | 162 | 0 | 1 |
| `talkDefault` | 1 | 172 | 0 | 1 |
| `talkDefault` | 1 | 206 | 0 | 2 |
| `talkDefault` | 1 | 244 | 0 | 2 |

## Target messages before each talkDefault

For each `talkDefault` EventStart, the client-to-server messages since the
previous EventStart in the same capture are searched for the nearest
`0x00cc` lock and the nearest `0x00cd` set. Each carries two dwords, the
actor id and a second value. The second value is classed as zero,
`0xe0000000`, or other so no actor id appears. Stream order is the
reconstructed client-to-server order of wrapped-actor messages. The
owner is the EventStart owner actor.

| Group | Messages | Lock found | Lock immediately before | Lock actor is owner | Set found | Set actor is owner | Set before lock |
|---|---:|---:|---:|---:|---:|---:|---:|
| `selector 1` | 16 | 16 | 16 | 16 | 13 | 13 | 13 |
| `selector 101` | 1 | 0 | 0 | 0 | 1 | 1 | 0 |

| Group | Lock second dword | Set second dword |
|---|---|---|
| `selector 1` | zero x16 | 0xe0000000 x13 |
| `selector 101` | none | 0xe0000000 x1 |

## Not established

- Whether the zone field equals a zone id. No capture records its zone
  next to this field in a tracked product.
- The meaning of selector 101 and of the nonzero low 22 bits.
- The order of the client target messages against server messages. Only
  the client-to-server stream is ordered here.
- Whether the client sends the lock and set messages as part of the
  talk trigger or only as a side effect of targeting.
- Whether the selector follows the trigger kind or the event name.
- Any trigger kind absent from the captures, including emote events.
