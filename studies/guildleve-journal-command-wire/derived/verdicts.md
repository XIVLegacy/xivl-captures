# Guildleve Journal Command Wire Verdicts

The input corpus and every capture SHA-256 are recorded in `accounting.json`.
Positive rows would be addressed by capture, lane, frame, subevent, opcode,
field domain, and field offset in `command-matches.csv`; the file is header-only
because the search found no row.

| Question | Verdict | Retail evidence |
|---|---|---|
| Does c2s carry JournalCommand static actor 24241? | BOUNDED-ABSENT | Across 54 captures, 84 clear game lanes, 8,970 c2s frames, and 21,109 wrapped actor events, no decoded frame body contains little-endian `B1 5E`, `B1 5E 00 00`, or `B1 5E F0 A0`. |
| Is 24241 a captured inner opcode? | BOUNDED-ABSENT | None of the 21,109 wrapped c2s records has inner opcode `0x5EB1`. The value 24241 is a static actor row identity and is not promoted as an opcode. |
| Does EventStart identify the target command? | BOUNDED-ABSENT | The corpus contains 126 c2s EventStart `0x012D` rows. None has owner `0xA0F05EB1`, and none has owner low 16 bits equal to 24241. |
| Can journal ID or subindex 2-5 be decoded? | INSUFFICIENT-DATA | The client route supplies journal ID then subindex only after selecting JournalCommand. With no structurally identified target command row, no packet field can be attributed to either argument. Small integer byte values elsewhere are numeric coincidences. |

## Coverage

Canonical reconstruction admitted 54 main lanes and 30 chat lanes with no
unknown lane. It searched 1,504,160 reconstructed c2s bytes, 1,360,640 complete
outer-frame body bytes, 21,201 complete subevents, 851,752 wrapped actor-payload
bytes, and 682,880 application-payload bytes. The search covered all locally
restored members, including the clear 54992 game lanes in `login.pcapng`.

Each decoded frame body was searched for the u16 row identity, u32 row
identity, and full static-owner identity. Wrapped records were also classified
by inner opcode. EventStart rows received the stronger field-position test at
application offset `+0x04`, so a target owner could not be manufactured from a
numeric match elsewhere in a payload.

## Static search model

The following tracked snapshots establish the conditional search model. They
do not become packet evidence or regeneration dependencies.

- [Static actor class-path catalog](https://github.com/XIVLegacy/xivl-client-data/blob/3a8034c9d567a6097dfe87c0a1ea2e9be24c544c/manifests/staticactor_class_paths.json),
  SHA-256
  `d612438827e5997422ab6f64a807e567ddf1b953c532e8a319d67b93c53c9db0`,
  identifies row 24241 as `/Command/System/JournalCommand`.
- [Guildleve journal lifecycle](https://github.com/XIVLegacy/xivl-client-scripts/blob/8eef641e666dfc8d5fa3c9c96de7ce618831118f/docs/guildleve-journal-lifecycle.md),
  SHA-256
  `ed74be2ac31a0e128fe096cfde10c87881b4e29f7bb07250288aa56e4ae9909e`,
  establishes argument order and maps regional Break, local Break, regional
  Retry, and local Retry to subindices 2, 3, 4, and 5.
- [Combat command emission catalog](https://github.com/XIVLegacy/xivl-client-structs/blob/099005ec1e6c9e0555a0ec0c819c981807fe83db/manifests/combat_command_emission.json),
  SHA-256
  `4a330d68435cdbc400aaeb50d47319c2c619d9c61d2280cb23fcb6d4235fb570`,
  establishes c2s EventStart owner offset `+0x04` and the conditional static
  actor low-16 relationship.
- [Opcode catalog](https://github.com/XIVLegacy/xivl-opcodes/blob/f46d8a2a69ef3c5386470922761a9bff559fed41/opcodes.json),
  SHA-256
  `46003891e031bb94b4e7b7cbe4c3108ce00bbc385f9ea72a019d335024173799`,
  identifies EventStart as map serverbound `0x012D` with 216-byte observations.

## Boundaries

The raw 54994 lobby lane and TLS account-service traffic remain outside the
canonical clear game decoder. No retained packet proves Break or Retry server
mutation, accepted-leve removal, director retirement, or journal retention.
