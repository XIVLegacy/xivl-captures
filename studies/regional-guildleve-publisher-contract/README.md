# Regional Guildleve Publisher Contract

## Study contents

This study isolates the regional battlecraft Guildleve lifecycle visible in
`party_battle_leve.pcapng`. It follows activation of already-retained row 12487,
director completion, reward presentation, retirement, and the final unanswered
interaction. It does not promote those events into a publisher acceptance,
hand-in, payout, or journal-mutation contract.

## Start here

- `derived/verdicts.md` - SUPPORTED and INSUFFICIENT conclusions.
- `derived/timeline.csv` - selected outer frames and attributable fields.
- `derived/accounting.json` - immutable capture identity and decode totals.

Regenerate or verify the canonical products:

```text
python tools/extractors/extract_regional_guildleve_publisher_contract.py
python tools/extractors/extract_regional_guildleve_publisher_contract.py --check
```

## Source material

The sole runtime source is `sources/pcap-1.23b/objects/party_battle_leve.pcapng`
at the SHA-256 retained in every derived product. The extractor uses canonical
TCP reconstruction and records the earliest captured packet that completes each
selected outer frame. Capture completion order is not server causality.

The interpretation cross-check used these exact read-only revisions:

- `xivl-client-scripts` `3804eebcc43a48e6998371117aeeb0d04084d7a6`
  - `docs/guildleve-journal-lifecycle.md`
- `xivl-client-data` `76d68d2036dc99bdda2917e65efcdef4f62f4b63`
  - `manifests/tables.json`, `tools/mappings/guildleve.py`
- `xivl-client-structs` `5233344d39bfd5b68cf8c6e13eb6b39b9e2e3691`
  - `manifests/guildleve_lifecycle.json`, `manifests/lua_api_contract.json`
- `xivl-opcodes` `e2b156fec3256a2160da15a288225fe75c3fdc07`
  - `data/client_receivers.json`, `data/client_opcode_semantics.json`

The client-data revision inventories the Guildleve tables but does not
distribute decoded rows. The row-12487 name and type therefore remain a bounded
assertion from the tracked client lifecycle report, not a reproduced static-data
join in this study.

## Promoted conclusions

The capture supports Aetheryte activation of already-retained Guildleve 12487,
the initial type-30001 content group, a director finish signal, reward dialog
presentation, warp presentation, and event/group retirement. The opening does
not call publisher functions `eventTalkCard` or `eventTalkDetail`.

Publisher acceptance, journal insertion, publisher hand-in, reward grant, and
post-reward journal retention or removal are INSUFFICIENT. The post-completion
actor is a dynamic actor not authoritatively identified as a publisher, and the
capture ends after a final `talkDefault` without its response.

## Topics

- regional Guildleve activation
- publisher acceptance boundary
- director completion signal
- reward and warp presentation
- journal mutation bounded absence

## Evidence boundary

Packet facts are the numeric fields in `derived/timeline.csv`. Client scripts
explain UI and work-state behavior but do not prove server persistence. Tracked
static metadata describes table shape and the lifecycle report's bounded row
assertion. Statements about a retained row combine packet order with client
selection behavior and are explicitly inference.

The Bahamut revision `6de863e455c3494e6a018cb9563c7dd239d1e438`
implements the same narrow separation: publisher scripts present offer/detail
UI, Aetherytes start pre-existing rows, directors run content, and the warp point
opens reward/return UI. Its empty accepted branch and absent payout policy are
comparison boundaries, not retail evidence.

## Evidence gaps

The held capture has no publisher card/detail offer, no server response that
creates or changes a journal row, no identified publisher at completion, and no
attributable reward grant. It also ends before the response to the final
interaction, so post-reward journal state is unobserved.

## Further research

A publisher acceptance specimen must contain the offered-card/detail sequence
and the server response that creates or changes a journal row. A hand-in or
payout claim needs an identified publisher interaction plus attributable grant
and persistence effects. Do not fill those gaps from the current emulator.
