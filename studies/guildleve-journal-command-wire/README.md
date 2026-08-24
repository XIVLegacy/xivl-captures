# Guildleve Journal Command Wire Census

## Study contents

This study exhaustively searches every canonical retail capture's decoded c2s
game lanes for wire evidence associated with JournalCommand static actor 24241,
journal IDs, and subindices 2 through 5. It separates static actor identity,
inner opcode identity, and untyped payload bytes.

## Start here

- `derived/verdicts.md` - bounded negative and evidence limits.
- `derived/accounting.json` - complete corpus identity and decode accounting.
- `derived/command-matches.csv` - deterministic row schema; header-only because
  the census found no match.

Regenerate or verify the canonical products:

```text
python tools/extractors/extract_guildleve_journal_command.py
python tools/extractors/extract_guildleve_journal_command.py --check
```

## Source material

The runtime source is the 54-member `pcap-1.23b` retail corpus. The extractor
uses the canonical TCP reconstruction, clear port-54992 game-lane admission,
outer framing, and wrapped actor-event layout. Each input SHA-256 and a corpus
content digest are retained in `derived/accounting.json`.

Tracked client evidence supplies the search model but is not a runtime input.
`JournalCommand` is static actor row 24241; the generic c2s command carrier
candidate is EventStart `0x012D`, whose static-owner identity is conditionally
encoded in the owner actor field's low 16 bits after the `0xA0F00000` prefix
test. The scripts route journal ID then subindex, but do not prove wire widths.

## Promoted conclusions

The retained corpus has a bounded absence for JournalCommand 24241. No decoded
c2s frame body contains little-endian `0x5EB1`, its u32 row encoding, or the
static owner actor encoding `0xA0F05EB1`. No inner opcode is `0x5EB1`, and none
of the 126 EventStart rows has owner low 16 bits equal to 24241.

Because no structurally identified target command row exists, the corpus does
not bind a journal ID or subindex 2, 3, 4, or 5 to an outgoing packet. Arbitrary
small integers elsewhere are excluded as numeric coincidences.

## Topics

- guildleve journal commands
- EventStart command ownership
- bounded wire absence
- c2s payload census

## Evidence boundary

Command 24241 is a static actor identity, not opcode 24241. The static-owner
relationship is valid only for EventStart owners in the `0xA0F00000` block.
The semantic labels Break and Retry come from tracked client-script control
flow, not packets, and no packet here proves a server mutation.

## Evidence gaps

The canonical game decoder excludes raw lobby 54994 and TLS traffic, so this
study makes no plaintext claim about either domain. The retained captures also
do not contain a known user action specimen for any target subindex.

## Further research

Do not reinterpret byte values 2 through 5 as journal actions. Stronger wire
evidence requires a new retail specimen in which the user invokes regional or
local Break or Retry, followed by the same deterministic extractor.
