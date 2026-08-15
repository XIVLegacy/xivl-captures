# M9 Autotranslate and Chat Relay Search

## Study contents

This run-once study searched every immutable member of the canonical 1.23b
capture corpus for autotranslate phrase selections and for Map `0x0003` and
World `0x00c9` chat packets. It records the complete search space, methods,
specimen locators, bounded negative result, and evidence ceiling.

## Start here

- `derived/verdicts.md` - per-search verdicts and decoded payload shapes.
- `derived/search-accounting.md` - exact passes, coverage, collision controls,
  and why each pass would detect a matching specimen.
- `derived/corpus-inventory.csv` - all 54 searched objects with immutable
  identity and decode coverage.
- `derived/chat-relay-specimens.csv` - every matching chat packet with a stable
  reconstructed-stream locator.

## Source material

- `sources/pcap-1.23b/manifest.yaml` defines the 54 immutable capture members.
- The corpus content digest is
  `3e39bfbffdf5a7efa0f42fc221f42dc2d1d28af8f19378d28921a3b903c0c7ee`.
- `xivl-client-data:csv/xtx__fixedPhrase.csv` is the fixed-phrase cross-reference.
  The searched table is extraction `2012.09.19.0001`, game version `1.23b`,
  SHA-256 `a9ce38b0b4ca33e1c03bf22bc854e054bb46db1cef9edfb4e9c55c5d0516a16c`.
- `xivl-opcodes:opcodes.json` supplies the independent channel assignments and
  payload-size evidence used to interpret the observed packets.

## Promoted conclusions

- The tested autotranslate selector families have a closed-corpus bounded
  absence. No terminator-bearing candidate was found.
- Map clientbound/serverbound numbering is lane-specific. The corpus contains
  two Map main-lane client-to-server `0x0003` chat packets.
- The corpus contains 11 World chat-lane client-to-server `0x00c9` packets and
  26 World chat-lane server-to-client `0x00c9` relay packets.
- The World server-to-client shape is a shared 12-byte prefix, a 32-byte sender
  name, a 512-byte message, and a 4-byte zero tail.

## Topics

- autotranslate fixed-phrase wire search
- Map chat packet `0x0003`
- World chat relay packet `0x00c9`
- closed-corpus bounded absence
- packet payload layout

## Evidence gaps

- No permitted source establishes `02 1d` as the retail autotranslate marker or
  proves any tested selector encoding. The absence applies only to the 9,048
  enumerated encodings.
- The binary prefix and tail semantics in Map `0x0003` remain unknown.
- World `0x00c9` prefix fields are observed values; their semantic names remain
  limited to the independent client evidence cited in `derived/verdicts.md`.
- `login.pcapng` contains TLS account traffic and raw lobby traffic but no
  canonically decoded game lane. Its raw TCP payload was still byte-scanned.

## Further research

Do not repeat these corpus searches. A stronger autotranslate conclusion needs
a source-backed token grammar or a new retail specimen outside this corpus.
