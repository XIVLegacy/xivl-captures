# Regional Guildleve Publisher Contract Verdicts

The acceptance inputs are `accept_leve.pcapng`, SHA-256
`42b87e6c095db130def1de5bc382e428b4f4c12c8069c4682d6fa4bc7681967a`,
and the independent local comparison `accept_local_leve.pcapng`, SHA-256
`3b4b071d88742a5d3c94a1e29ca6a4074cb6b9a9a60207118302fe22f932bd7c`.
The retained-row activation/completion comparison remains
`party_battle_leve.pcapng`, SHA-256
`6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f`.

| Question | Verdict | Evidence boundary |
|---|---|---|
| Regional publisher actor | SUPPORTED | EventStart and all ten regional RunEvent callbacks carry owner actor `0x44D8000A`. The callback family binds the interaction to the retail `PopulaceGuildlevePublisher` client class; no static actor-row identity is inferred. |
| Offered Guildleve identity | SUPPORTED | The first `eventTalkCard` offers 12483 in card 1 and 12482 in card 4. After card 1 is selected, the detail callback carries 12483; after card 4 is selected, the detail callback carries 12482. |
| Acceptance intent | SUPPORTED | The client returns card indexes 1 and 4, then returns boolean true from each matching `eventTalkDetail`. Retail Lua defines that true only as successful confirmation UI, not server mutation. |
| Acceptance acknowledgement | SUPPORTED | In the same bounded EventStart-EndEvent window, server `0x0137` writes 12483 to synchronized `work.guildleveId[3]` and 12482 to `work.guildleveId[4]`. These are the first captured client-visible accepted-row acknowledgements. |
| Client journal insertion | SUPPORTED | The two nonzero synchronized slot writes place the accepted IDs in the client's retained journal state. |
| Durable persistence | INSUFFICIENT | No reconnect or relog specimen proves that either accepted row survives the captured session. |
| Allowance check or decrement | INSUFFICIENT | No selected callback argument, synchronized property, or adjacent packet is identified as an allowance amount, check, or decrement. A paired allowance-bearing before/after state is required. |
| Publisher-state mutation | INSUFFICIENT | No packet in the bounded window writes an identified field on owner actor `0x44D8000A`. A named publisher property before/after transition is required. |
| Director creation or activation | INSUFFICIENT | The acceptance window has no `eventGLStart`, content-group start, director member, or identified director actor. A subsequent structurally linked activation specimen is required. |
| Regional/local shared contract | REFUTED | Both use EventStart, RunEvent, EventUpdate, synchronized journal work, and EndEvent, but local uses `talkOfferWelcome`/`askOffer*`/`talkOfferDecide`, owner `0x44D80009`, and `work.guildleveId[8]=202`; regional uses `eventTalk*`, owner `0x44D8000A`, and slots 3/4. Only the outer envelope is shared. |
| Bounded Bahamut publisher acceptance | SUPPORTED WITH BOUNDARIES | The capture supports offer cards, selected-card returns, detail confirmation, subsequent offer-list closure, and synchronized insertion of the selected IDs. Offer eligibility, allowance policy, durable persistence, and later activation remain separate requirements. |
| Hand-in, reward grant, or journal removal | INSUFFICIENT | The acceptance captures end after offer closure and contain no identified hand-in, attributable grant, or nonzero-to-zero accepted-slot transition. The party comparison supports reward presentation only. |

## Regional acceptance sequence

Owner `0x44D8000A` starts `talkDefault`. The server presents type and pack
selection, then cards containing 12483 and 12482. Card result 1 plus a true
detail result for 12483 appears before `work.guildleveId[3]=12483` in capture
order. The next card list retains only 12482; card result 4 plus a true detail
result appears before an empty card list and `work.guildleveId[4]=12482`.
Pack/type closure and EndEvent complete the bounded transaction.

## Local comparison

Owner `0x44D80009` uses `talkOfferWelcome`, `askOfferPack`, `askOfferRank`,
`askOfferQuest`, `talkOfferDecide`, and `finishTalkTurn`. The quest selector
offers 120222 and 120202 and returns index 2. The capture then records
synchronized `work.guildleveId[8]=202` plus a separate
`playerWork.questGuildleve[0]` record whose value semantics remain unpromoted.
This supports a local accepted row while proving that the regional callback
and slot contract is not shared.

## Packet, script, static, and inference boundary

- Packet facts are the actor IDs, function strings, typed Lua values, property
  records, hashes, and ordering in `timeline.csv`.
- Retail client scripts establish card-index and detail-confirmation UI
  behavior. They do not establish authoritative persistence or allowance
  policy.
- Property names are exact backward-MurmurHash2 resolutions promoted from the
  pinned `xivl-client-structs` revision. They identify synchronized client
  fields, not the server's durable storage model.
- `accounting.json` reconciles every main-lane packet in each bounded window;
  excluded opcode families remain numeric sidecars unless another study
  supplies their semantics.
