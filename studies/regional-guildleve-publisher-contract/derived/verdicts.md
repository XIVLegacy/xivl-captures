# Regional Guildleve Publisher Contract Verdicts

The sole input is `party_battle_leve.pcapng`, SHA-256
`6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f`.
`timeline.csv` orders the earliest captured packet that completes each selected
outer frame; same-frame rows retain subevent order.

| Question | Verdict | Evidence boundary |
|---|---|---|
| Publisher acceptance | INSUFFICIENT | The opening calls `eventAetheryteChildSelect`, `eventGLSelect`, `eventGLSelectDetail`, `eventGLDifficulty`, and `eventGLStart`. No `eventTalkCard` or `eventTalkDetail` publisher-acceptance call occurs. Guildleve 12487 is already retained when selection begins, so no offered list or acceptance response is captured. |
| Director start | SUPPORTED | `eventGLStart` carries guildleve ID 12487 before the first type-30001 content-group snapshot. The compact member list contains director actor `0x45100D44`, player `0x029B2941`, peer `0x029B27D3`, and content actor `0x45100D45`. This is one observed activation, not a universal creation recipe. |
| Completion | SUPPORTED | The director-targeted `0x0137` row at s2c frame 3374 carries property `0xAFEDF257=FF` and `0xD2C67973=00000000`. Tracked client evidence interprets these as signed signal -1 and startTime zero, sufficient for generic Guildleve UI `finish`; the packet does not settle success policy or rewards. |
| Publisher hand-in | INSUFFICIENT | The post-completion `talkDefault` owner is dynamic actor `0x45100D5B`. The server invokes `eventGuildleveReward` and `eventTalkGuildleveWarp`, but no tracked packet or static row identifies that actor as a regional publisher or exposes an authoritative hand-in operation. |
| Reward | SUPPORTED | `eventGuildleveReward` carries guildleve ID 12487 and precedes the client response and warp presentation. This supports reward presentation only, not grant, selection, authorization, or persistence. |
| Journal mutation | INSUFFICIENT | Selection proves row 12487 was already retained before activation. No selected row identifies its insertion, accepted-state write, removal, or retention after reward. The final `talkDefault` is unanswered before capture end. |

## Bounded negative

This held specimen does not contain the publisher offer/confirmation functions
needed to reconstruct acceptance, does not identify the reward actor as a
publisher, and ends before the final interaction receives a response. It cannot
establish offered-card identity, acceptance mutation, authoritative hand-in,
reward grant, or journal-row removal/retention.

## Packet, script, static, and inference boundary

- Packet facts are limited to the numeric rows and byte-attributable fields in
  `timeline.csv`.
- Client-script behavior supplies the meanings of `eventGL*`,
  `eventGuildleveReward`, signed finish signal, and presentation flow. It does
  not become packet evidence for server mutation.
- The tracked client lifecycle report records row 12487 as
  "Necrologos: Celeritous Impetus"; the pinned data repository inventories the
  source tables but does not distribute their decoded rows.
- The statement that the opening uses an already retained journal row is a
  packet-plus-script inference: `eventGLSelect` selects a retained ID, and the
  following calls carry 12487. No packet writes that row.
