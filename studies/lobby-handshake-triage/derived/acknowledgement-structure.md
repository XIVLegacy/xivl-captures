# Lobby Acknowledgement Structure

## Source and scope

This record compares the first decrypted server acknowledgement in both raw
lobby connections in `login.pcapng`. The capture identity and confirmed
decryption recipe are fixed in `decrypt-recipe.md`. The comparison does not
extend the port-54992 game-opcode corpus.

## Boundaries

Both acknowledgements begin at reconstructed server-stream offset `0x28` and
end at `0x2C8`. Each record is exactly `0x2A0` (672) bytes:

| Record-relative span | Length | Supported interpretation |
|---|---:|---|
| `0x000-0x00F` | 16 | Clear outer header. The little-endian size at `+0x04` is `0x02A0`; the little-endian count at `+0x06` is one. |
| `0x010-0x01F` | 16 | Clear subrecord header. The little-endian size at `+0x10` is `0x0290`; the clear type at `+0x12` is `0x000A`. |
| `0x020-0x29F` | 640 | Blowfish-ECB region processed as 80 eight-byte blocks. |

The first 32 bytes are identical between the retained sessions. The decrypted
payload is not a static template: 615 bytes are invariant and 57 bytes differ.
Their exact bytewise invariant and dynamic runs are recorded as offset/length
triples in `lobby-acknowledgement-structure.json`. Those runs form a contiguous
partition of all 672 bytes, so a shifted boundary cannot silently preserve the
fixture.

## Repeated structure

Eight groups of nonzero, aligned eight-byte values recur at the same offsets
within both records. Three groups change value between sessions while
preserving their repeated offsets; five groups retain the same value. The
fixture publishes only the offset groups, unit length, and cross-session
variance. This proves repeated storage shape but does not identify the opaque
values as pointers, identifiers, or protocol fields.

## Sanitized fixture

`lobby-acknowledgement-structure.json` contains lengths, boundaries, the clear
header marker, comparison runs, and repeated-value offsets only. It omits all
decrypted payload values, keys, client numbers, ticket text, names, tokens,
addresses, and ports. `schemas/lobby-acknowledgement-structure.schema.json`
fixes its public shape.

Run the restricted reproduction with:

```powershell
python tools/extractors/extract_lobby_acknowledgement_schema.py --check
```

With the restricted capture absent, `--check --public-shape` validates the
committed schema and privacy-preserving structural assertions without claiming
source reproduction.

## Evidence limit

Cross-session equality alone cannot assign semantics to the encrypted payload.
The repeated values and long invariant spans may include process state copied
into the record. Publishing any of those values would expose private or bulk
plaintext without adding a supported field interpretation, so they remain a
bounded negative rather than a weakened fixture.
