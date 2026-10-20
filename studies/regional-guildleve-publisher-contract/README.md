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

The interpretation cross-check used these immutable sources:

- [Guildleve journal lifecycle](https://github.com/XIVLegacy/xivl-client-scripts/blob/da2ecbf8e8d80a07988fef80c2a8af716539d7fe/docs/guildleve-journal-lifecycle.md)
- Client-data [table catalog](https://github.com/XIVLegacy/xivl-client-data/blob/ffe929b8bebd5d6d071a98ddceb78d32bc6c0d17/manifests/tables.json)
  and [Guildleve mapping](https://github.com/XIVLegacy/xivl-client-data/blob/ffe929b8bebd5d6d071a98ddceb78d32bc6c0d17/tools/mappings/guildleve.py)
- Client-structs [Guildleve lifecycle catalog](https://github.com/XIVLegacy/xivl-client-structs/blob/9058d5a06f7ef84bcbd134d0437b8f7f0e2a0349/manifests/guildleve_lifecycle.json)
  and [GAM hash names](https://github.com/XIVLegacy/xivl-client-structs/blob/9058d5a06f7ef84bcbd134d0437b8f7f0e2a0349/manifests/gam_hash_names.json)
- Opcode [receiver catalog](https://github.com/XIVLegacy/xivl-opcodes/blob/db9e9d770698b086f19758ecc5803012308f5891/data/client_receivers.json)
  and [client semantics](https://github.com/XIVLegacy/xivl-opcodes/blob/db9e9d770698b086f19758ecc5803012308f5891/data/client_opcode_semantics.json)

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

## Retail client Director binding for 12487

The party capture directly joins Guildleve 12487 to actor `0x45100D44` and
client script `/Director/Guildleve/PrivateGLBattleOrbNormal`. In one s2c
`0x00CC` record, that actor is the transport source, the fixed text field
contains `PrivateGLBattleOrbNormal`, and the serialized parameter stream
contains both the full script path and integer 12487. This is a client script
binding for this retained activation, independent of the actor's high nibble
or content-group membership. It does not identify a server implementation
class or establish a mapping for other Guildleves.

The source is the same 1,429,864-byte `party_battle_leve.pcapng` pinned above.
All locators below are main connection 0. Frame and subevent indexes are
zero-based; completing capture packet numbers are one-based. Application
offset zero follows the 16-byte subevent header, 8-byte inner header and
8-byte game preamble.

| Record | Direction | Frame / subevent | Completing packet | Opcode | Application bytes |
| --- | --- | --- | ---: | --- | ---: |
| `eventGLStart`, owner `0x4510000C` | s2c | 40 / 2 | 94 | `0x0130` | 144 |
| One-value response | c2s | 42 / 2 | 110 | `0x012E` | 88 |
| Actor, class and Guildleve join | s2c | 50 / 17 | 118 | `0x00CC` | 264 |

The class-bearing record starts at decoded-body offset 1304 in the outer
frame at reconstructed s2c stream offset 5608. Its application SHA-256 is
`6d8094109a3c70cbf8252ef6dba9c457ccb67b112e189b6c6681c7055e933491`.
Application `+0x24..+0x43` contains the class name followed by eight NULs.
The complete parameter stream at `+0x44` is:

```text
string "/Director/Guildleve/PrivateGLBattleOrbNormal",
false, false, false, false, false,
integer 20005, integer 12487, integer 6,
integer 0, integer 0, integer 0, END
```

The string tag is `0x02` at `+0x44`, with NUL at `+0x71`. The five Boolean
false tags are `0x04` at `+0x72..+0x76`. Integer tags are `0x00` at
`+0x77`, `+0x7C`, `+0x81`, `+0x86`, `+0x8B` and `+0x90`, each followed
by four big-endian bytes. END is `0x0F` at `+0x95`; all 114 following
application bytes are zero. Their field/alignment split is unassigned.
There is no nil or reference token before END. The meaning of 20005 and
the route from this stream to formal Lua initialization arguments remain
unresolved; the six integers are not assigned initializer parameter names.

The complete `eventGLStart` argument block at application `+0x49..+0x88`
contains nine `0x00` big-endian integer tokens:

```text
(12487, 1, 3, 3, 12, 0, 0, 0, 0), END
```

END is at `+0x76`, followed by 18 zero bytes within that block. The remaining
seven application bytes are outside it. The response's 64-byte block at
`+0x11..+0x50` contains integer 1, END at `+0x16`, and 58 zero bytes;
the result count at `+0x10` is 1. Neither vector contains nil or references.
The [Aetheryte event contract](https://github.com/XIVLegacy/xivl-client-scripts/blob/add34c6b54cf55905f869fe5115766937974a21c/docs/aetheryte-guildleve-events.md#eventglstart-and-widget-argument-reshuffling)
owns the nine presentation-slot meanings and widget reshuffle. This captured
response does not prove that it caused actor creation or a reward grant.

The [script registry](https://github.com/XIVLegacy/xivl-client-scripts/blob/add34c6b54cf55905f869fe5115766937974a21c/lua/registry.json),
key `director/guildleve/privateglbattleorbnormal`, independently maps the
observed path to `PrivateGLBattleOrbNormal`, `initAsGuildleve` and require
`/Director/Guildleve/GuildleveBaseClass`. Registry metadata supplies no native
argument-routing proof. The same actor later supplies the existing
`director-finish-update` at s2c frame 3374 / subevent 0 in the selected
timeline. The class-bearing record adds identity to that client lifecycle
without connecting publisher acceptance to activation.

Reproduction uses `_decode_capture` from
`tools/extractors/extract_00da_00e1_comparison.py` at revision
`208c87e0e037f87dcbe7e542019918b53e355691`, selected by the exact locators
above. Strip the inner header and preamble, compare the application digest,
then read the fixed text and each tagged value through END. Canonical decoding
yielded 1,827 c2s and 3,516 s2c complete frames with zero admitted unparsed
stream bytes. It also reported six discarded trailing reconstructed s2c
bytes outside complete frames. No selected argument stream was truncated.
Ordering remains local to each connection and direction.

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
