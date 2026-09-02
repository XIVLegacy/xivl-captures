# Regional Guildleve Publisher Contract

## Study contents

This study isolates regional Guildleve publisher acceptance in
`accept_leve.pcapng`, compares the local publisher path in
`accept_local_leve.pcapng`, and retains the independent activation/completion
boundary from `party_battle_leve.pcapng`.

The regional capture supports offer-card presentation, client confirmation,
and synchronized insertion of Guildleves 12483 and 12482 into client journal
slots. It does not establish offer eligibility, allowances, durable
persistence, publisher mutation, director activation, hand-in, reward grant,
or journal removal.

## Start here

- `derived/verdicts.md` - the required SUPPORTED, REFUTED, and INSUFFICIENT
  verdict matrix.
- `derived/timeline.csv` - selected outer frames and attributable fields from
  all three captures.
- `derived/accounting.json` - immutable capture identities, complete bounded
  transaction accounting, and exclusions.

Regenerate or verify the canonical products:

```text
python tools/extractors/extract_regional_guildleve_publisher_contract.py
python tools/extractors/extract_regional_guildleve_publisher_contract.py --check
```

## Source material

The three runtime sources are:

- `accept_leve.pcapng`, SHA-256
  `42b87e6c095db130def1de5bc382e428b4f4c12c8069c4682d6fa4bc7681967a`
- `accept_local_leve.pcapng`, SHA-256
  `3b4b071d88742a5d3c94a1e29ca6a4074cb6b9a9a60207118302fe22f932bd7c`
- `party_battle_leve.pcapng`, SHA-256
  `6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f`

The extractor uses canonical TCP reconstruction and records the earliest
captured packet that completes each selected outer frame. Capture completion
order is not server causality. The regional capture's separate chat lane is
excluded from the main-lane transaction accounting.

The interpretation cross-check used these exact read-only revisions:

- `xivl-client-scripts` `d925bd787f9abbdff7419987460b70d17650df39`
  - `docs/guildleve-journal-lifecycle.md`
- `xivl-client-data` `fbca4715222fcaeb4b1c6ea8bb5166f59d59363f`
  - `manifests/tables.json`, `tools/mappings/guildleve.py`
- `xivl-client-structs` `b602c9d76c283d9e32116d51f63304d86adf583d`
  - `manifests/guildleve_lifecycle.json`,
    `manifests/gam_hash_names.json`
- `xivl-opcodes` `cd0469403450f9a0911194703796b65ce0621ed8`
  - `data/client_receivers.json`, `data/client_opcode_semantics.json`

These are immutable interpretation citations, not runtime or build
dependencies.

## Promoted conclusions

Regional owner actor `0x44D8000A` runs the `eventTalk*` publisher callback
family. The client selects card 1 for Guildleve 12483 and card 4 for 12482,
then confirms each detail. In capture order, the server then emits
property-stream writes of 12483 to `work.guildleveId[3]` and 12482 to
`work.guildleveId[4]`. Those writes are the first captured client-visible
acknowledgements and support synchronized client journal insertion.

The local comparison uses owner `0x44D80009`, the distinct
`talkOffer*`/`askOffer*` callback family, and a different journal-slot
representation. The paths share only the outer EventStart, RunEvent,
EventUpdate, property-stream, and EndEvent envelope.

The party capture remains an already-retained Guildleve comparison. It
supports Aetheryte activation of row 12487, director completion, reward
presentation, and retirement, but does not connect acceptance to activation or
prove publisher hand-in, payout, or journal mutation.

## Topics

- regional Guildleve publisher acceptance
- local publisher comparison
- synchronized journal insertion
- retained-row activation boundary
- allowance and persistence evidence gaps

## Evidence boundary

Packet facts are the actor IDs, function strings, typed Lua values, property
records, hashes, and ordering in `derived/timeline.csv`. Retail scripts explain
card selection and confirmation UI behavior but do not prove authoritative
server persistence or allowance policy. Property names come from exact hash
resolutions in the pinned client-structs revision and identify synchronized
client fields, not the server's storage model.

## Evidence gaps

The captures do not identify an allowance field or publisher-state mutation,
prove durable storage, connect acceptance to later director activation, or
show an identified publisher hand-in with attributable reward and journal
removal effects.

## Further research

The smallest specimens required to close the remaining boundaries are:

- a paired allowance-bearing state before and after publisher acceptance;
- a named publisher property transition in the same transaction;
- acceptance followed by a structurally linked activation sequence;
- reconnect or relog evidence for durable journal persistence; and
- an identified publisher hand-in with an attributable grant and a nonzero to
  zero journal-slot transition.
