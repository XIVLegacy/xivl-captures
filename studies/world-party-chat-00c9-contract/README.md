# World Party-Chat 0x00C9 Contract

## Study contents

This study exhaustively reconciles every World chat-lane `0x00C9` event in the
54-member retained retail corpus. It separates c2s and s2c framing, publishes a
Bahamut-ready field matrix, and preserves unsupported fields as opaque
tokens.

## Start here

- `derived/accounting.json` - complete corpus, direction, capture, and privacy accounting.
- `derived/occurrences.csv` - one sanitized tokenized row per retained event with lane-local frame locators.
- `derived/field-matrix.csv` - outer, wrapper, game-message, and application offsets.
- `derived/normalized-fixtures.json` - generated synthetic c2s and s2c subevents.
- `derived/verdicts.md` - promoted contract and Bahamut adoption boundary.

Regenerate or verify all five products:

```text
python tools/extractors/extract_world_party_chat_00c9.py
python tools/extractors/extract_world_party_chat_00c9.py --check
```

## Source material

The packet source is `pcap-1.23b`. The extractor scans all admitted clear TCP
54992 connections after retransmission-safe reconstruction and checks its 37
target locators against
`studies/m9-corpus-research/derived/chat-relay-specimens.csv`.

Read-only client corroboration is
`xivl-client-structs:manifests/symbols.json#BCS-Y-0309` and
`xivl-opcodes:data/client_opcode_semantics.json#c2s-00c9`. It establishes the
c2s Chat-channel emitter, opcode, selector, and text-field extent. Capture
evidence owns the direction-specific field matrix.

## Promoted conclusions

The corpus contains 11 c2s and 26 s2c World chat-lane `0x00C9` events in two
distinct capture files. C2s uses a 552-byte actor-wrapped subevent; s2c uses 584
bytes and inserts a 32-byte sender-name buffer before the shared 512-byte
message buffer. All retained text fields are NUL-terminated, zero-padded, and
UTF-8-roundtripping.

The wrapper actor fields, c2s nonzero counter, application context u32, and c2s
tail remain opaque. The context differs between the two s2c capture contexts,
while the sender-name bytes are equal. This does not establish separate login
sessions or a stable numeric sender identifier.

## Bahamut boundary

The retail recipient route is World clientbound `0x00C9` on the raw chat lane.
It is not Map clientbound `0x0003` on the main lane. The study establishes the
wire shape needed to implement that route, but it does not prescribe how a
server obtains opaque wrapper or context values.

## Sanitization

Actor, counter, context, tail, name, and message values are replaced with
equality-preserving tokens. Names and messages are not hashed, so short private
text cannot be recovered by dictionary matching. The only packet bytes in the
public fixture are generated synthetic values.

## Claim boundary

The study does not infer audience membership, moderation, persistence,
delivery policy, server causality, or independently proven session identity.

## Topics

- World chat-lane party messages
- Direction-specific packet framing
- Sender-name and message buffers
- Opaque actor, context, counter, and tail fields
- Bahamut recipient-route replacement

## Evidence gaps

The corpus has one sender-name equality class across both capture files. It
does not distinguish name encoding beyond the observed UTF-8-roundtripping
bytes or assign semantics to the context u32, c2s counter, or c2s tail.

## Further research

A retained relay from a second sender name would test name-field variation. A
client receiver route or controlled retail differential is required before an
opaque field receives a semantic noun.

## Verification

Repository validation reproduces all products and validates the accounting schema
and checksum anchor, compares the complete M9 locator set, runs malformed-shape
and mutation tests, and enforces the public privacy boundary.
The focused extractor validates corpus membership and shape, but source member
size and SHA-256 integrity remain owned by the full refresh object-hash check.
