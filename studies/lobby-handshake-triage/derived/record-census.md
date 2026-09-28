# Decrypted Lobby Record Census

## Source and scope

This record inventories every complete frame and subrecord in both retained
port-54994 connections in `login.pcapng`. TCP reconstruction uses the same
sequence-offset placement as the canonical capture tooling. The encrypted
extent of each applicable subrecord payload is rounded down with `len &
0xFFE0` and decrypted with the confirmed recipe in `decrypt-recipe.md`.

The census publishes framing, numeric route keys, and cross-session structure
only. It does not publish payload bytes, values, hashes, names, tickets, keys,
addresses, ports, or inferred field nouns. It does not alter or extend the
ordinary port-54992 game decoder.

## Complete stream inventory

The two reconstructed connections contain 16 complete outer frames and 20
complete subrecords with no trailing stream bytes. In the subrecord column,
each tuple is `frame offset / declared length / clear type / encrypted length /
inner opcode`. A dash means the clear type has no decrypted game-message
header.

| Session | Direction | Stream offset | Outer length | Count | Subrecords |
|---|---|---:|---:|---:|---|
| 1 | c2s | 0 | 648 | 1 | `16 / 632 / 0x0009 / 0 / -` |
| 1 | c2s | 648 | 192 | 1 | `16 / 176 / 0x0003 / 160 / 0x0005` |
| 1 | c2s | 840 | 40 | 1 | `16 / 24 / 0x0008 / 0 / -` |
| 1 | s2c | 0 | 40 | 1 | `16 / 24 / 0x0007 / 0 / -` |
| 1 | s2c | 40 | 672 | 1 | `16 / 656 / 0x000A / 640 / -` |
| 1 | s2c | 712 | 640 | 1 | `16 / 624 / 0x0003 / 608 / 0x000C` |
| 2 | c2s | 0 | 648 | 1 | `16 / 632 / 0x0009 / 0 / -` |
| 2 | c2s | 648 | 40 | 1 | `16 / 24 / 0x0008 / 0 / -` |
| 2 | c2s | 688 | 192 | 1 | `16 / 176 / 0x0003 / 160 / 0x0005` |
| 2 | c2s | 880 | 64 | 1 | `16 / 48 / 0x0003 / 32 / 0x0003` |
| 2 | c2s | 944 | 72 | 1 | `16 / 56 / 0x0003 / 32 / 0x0004` |
| 2 | s2c | 0 | 40 | 1 | `16 / 24 / 0x0007 / 0 / -` |
| 2 | s2c | 40 | 672 | 1 | `16 / 656 / 0x000A / 640 / -` |
| 2 | s2c | 712 | 640 | 1 | `16 / 624 / 0x0003 / 608 / 0x000C` |
| 2 | s2c | 1352 | 3072 | 5 | `16 / 528 / 0x0003 / 512 / 0x0015`; `544 / 528 / 0x0003 / 512 / 0x0015`; `1072 / 528 / 0x0003 / 512 / 0x0016`; `1600 / 496 / 0x0003 / 480 / 0x0017`; `2096 / 976 / 0x0003 / 960 / 0x000D` |
| 2 | s2c | 4424 | 200 | 1 | `16 / 184 / 0x0003 / 160 / 0x000F` |

All encrypted lengths are relative to subrecord payload offset 16. Clear types
`0x0007` and `0x0009` occur before key establishment. Clear type `0x0008` has
only an eight-byte payload, so its `len & 0xFFE0` transformed extent is zero.
The fixture assigns no further noun to those clear types.

## Cross-session correspondence

Six exact frame shapes occur once in each session: clear types `0x0007`,
`0x0008`, `0x0009`, and `0x000A`, plus type-`0x0003` inner routes `0x0005`
and `0x000C`. The client-direction order of the shared `0x0008` and
type-`0x0003`/`0x0005` frames is reversed between sessions. Direction-local
stream offsets do not establish a combined arrival order.

After the acknowledgement, the records shared by both sessions are c2s clear
type `0x0008`, c2s type-`0x0003` inner `0x0005`, and s2c type-`0x0003` inner
`0x000C`. The second session alone continues through c2s inner `0x0003` and
`0x0004`, then s2c inner `0x0015`, `0x0016`, `0x0017`, `0x000D`, and
`0x000F`.

The acknowledgement comparison remains part of the full fixture. Its first
32 bytes are invariant, its byte-comparison runs partition all 672 bytes, and
its eight repeated aligned value groups retain only offsets and cross-session
variance. Equality does not assign semantics to any opaque value.

## Client-dispatch correspondence

Clear type `0x0003` is the game-message wrapper. Only its decrypted inner
opcode is compared with existing retail-client dispatch evidence. The route
names below come from `xivl-client-structs:manifests/symbols.json`; they are not
derived from payload content.

| Direction | Inner opcode | Supported route | Exact client boundary |
|---|---:|---|---|
| c2s | `0x0003` | Get-characters request | `ServiceLoginOperation::SendRequest`, `FUN_00DAA070` (BCS-Y-0290) |
| c2s | `0x0004` | Select-character request | `GameLoginOperation::SendRequest`, `FUN_00DAA740` (BCS-Y-0293) |
| c2s | `0x0005` | Session request | `LobbyLoginOperation::SendRequest`, `FUN_00DA9880` (BCS-Y-0286) |
| s2c | `0x000C` | Session response | `LobbyLoginOperation::ReceiveDispatcher`, `FUN_00DA9EC0` (BCS-Y-0287) |
| s2c | `0x000D` | Character-list route | `ServiceLoginOperation::ReceiveDispatcher` -> `FUN_00DA76B0` (BCS-Y-0017) |
| s2c | `0x000F` | Select-character response | `GameLoginOperation::ReceiveDispatcher` -> `FUN_00DA64B0` (BCS-Y-0294) |
| s2c | `0x0015` | World-list route | `ServiceLoginOperation::ReceiveDispatcher` -> `FUN_00DA6320` (BCS-Y-0017) |
| s2c | `0x0016` | Import-list route | `ServiceLoginOperation::ReceiveDispatcher` -> `FUN_00DA4C20` (BCS-Y-0017) |
| s2c | `0x0017` | Retainer-list route | `ServiceLoginOperation::ReceiveDispatcher` -> `FUN_00DA4D80` (BCS-Y-0017) |

The captured `0x000F` record follows the captured select-character request,
and the existing decrypt confirmation records a handoff-form string in that
response. This supports the select-character response as the next
world-handoff consumer boundary. It does not establish fields within the
response or promote the recovered string value.

The clear-type boundary is separate from the inner-opcode table:

| Clear type | Supported status | Exact next boundary |
|---:|---|---|
| `0x0003` | Game-message wrapper | Decrypted inner opcode, then the matching operation boundary above |
| `0x0007` | Numeric placeholder | Client envelope parser `FUN_00DA2330`, then dispatcher `FUN_00DA25D0`; the case consumer is not promoted |
| `0x0008` | Numeric placeholder | Client envelope parser `FUN_00DA2330`, then dispatcher `FUN_00DA25D0`; the case consumer is not promoted |
| `0x0009` | Client-produced initial record | Last client producer is `LobbyCryptEngine` slot 1, `FUN_00DA1590`; the next consumer is remote and absent from client evidence |
| `0x000A` | Framework secure-session setup record | `FUN_00DA2330` -> `FUN_00DA25D0` -> `FUN_00DA1670` -> `FUN_00DB34A0` |

The `0x000A` path is independently mapped by
`xivl-decomp:config/lobby_acknowledgement_consumer.json`; it is not an
application opcode. The `0x0009` producer is tracked in
`xivl-client-structs:manifests/symbols.json` (BCS-Y-0007). Clear types
`0x0007` and `0x0008` retain numeric placeholders until their dispatcher cases
are promoted from retail-client evidence.

## Sanitized fixture and checks

`lobby-record-census.json` contains the complete numeric inventory, exact
coverage relations, shared frame shapes, shared post-acknowledgement records,
and the bounded acknowledgement comparison. Schema
`schemas/lobby-record-census.schema.json` fixes its public shape.

Run restricted reproduction with:

```powershell
python tools/extractors/extract_lobby_record_census.py --check
```

With the capture absent, `--check --public-shape` validates the committed
fixture, relational assertions, and privacy boundary without claiming source
reproduction.
