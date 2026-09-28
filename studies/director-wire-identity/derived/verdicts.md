# Director Wire Identity Verdicts

The input corpus and all capture hashes are recorded in `accounting.json`.
Packet rows are addressed by `(capture, frame_index, subevent_offset, opcode)`;
member rows add `slot`.

| Claim | Verdict | Retail evidence |
|---|---|---|
| Director actors use high nibble 4 rather than 6 | INSUFFICIENT-DATA | `group-members.csv` has eight same-capture EventStart-owner/content-member matches for two unique actors, `1158679899` and `1163947554`; all eight have nibble 4 and none has nibble 6. The rows are party-battle frames 3367, 3368, 3372, 3432 and war-update frames 408, 494, 587, 612. Their EventStart names are only `talkDefault` and `noticeEvent`; no retained field or client chain proves either actor is the content director. The rows favor kind 4 for these role candidates but cannot decide the director-kind contradiction. |
| Content group type is 30001 | SUPPORTED | `group-packets.csv` contains 65 `0x017C` rows with application `u32 +0x30 = 30001`, all in `party_battle_leve.pcapng`. The complete 361-row distribution in `accounting.json` is 10001:14, 10002:265, 30001:65, 30006:4, 50001:2, 80001:11. The verdict is scoped to the observed party-battle content group, not every group. |
| A content director is a member of its own content group | INSUFFICIENT-DATA | The same two role-correlated actors appear as `0x0183` content-member rows eight times: actor `1158679899` in four party-battle packets and actor `1163947554` in four war-update packets. The wire proves repeated same-ID EventStart-owner/content membership, but neither the event name nor the Group handler identifies the actor as the content director. Self-membership is therefore a supported conditional, not a proved director fact. |
| The proposed member-list offsets describe one coherent packet | REFUTED | The proposal combines two layouts. `0x017C` and `0x0183` have 0x78-byte application payloads and 0x98-byte subpackets; `0x017F` has a 0x198-byte application payload and 0x1B8-byte subpacket, eight 0x30-byte records at `+0x10`, and count at `+0x190`. `0x0183` instead uses eight 0x0C-byte records at `+0x10` and count at `+0x70`. The proposed `+0x1C` count is not coherent in either layout. |

## Packet accounting

The exact packet counts in `accounting.json` are `0x017A=272`, `0x017C=361`,
`0x017D=361`, `0x017E=361`, `0x017F=27`, `0x0183=371`, `0x0187=42`, and
`0x018B=287`. The extractor transposes 42 populated `0x017F` records and 904
populated `0x0183` records. Content-member high nibbles are 4 for 768 rows and
0 for 136 rows; this broader distribution is not itself a director classifier.

## Offset cross-check

The static client reads the `0x017C` type candidate as `u32 +0x30`; its branch
compares 10001, while other values take the alternate path. The capture value
30001 is therefore accepted wire input, not a compared client constant.
`0x017F` uses eight 48-byte records and a signed count at `+0x190`; `0x0183`
uses the compact content-member path. The isolated proposed magic value 0x3F3E
at `+0x64` is observed in some headers but is not invariant and has no promoted
semantic name. Count-minus-one semantics at `+0x10`, a member-flag meaning at
record `+0x08`, and the name `SimpleContentGroup24B` remain insufficient.

Static addresses and BCS identifiers are frozen in
`xivl-client-structs:manifests/director_group_wire_identity.json`.

## Catalog recommendations

- Retain `groupTypeId` for `0x017C` application `u32 +0x30`, with observed
  values and the client-side 10001 branch cited; do not imply that 30001 is
  universal.
- Correct `0x0183` to a compact eight-by-0x0C content-member layout with count
  at `+0x70`; do not describe it as the `0x017F` 0x30-byte record shape.
- Retain `0x017F` member count at `+0x190`. Leave the `+0x08` record field and
  `0x017C +0x64` value semantically unresolved.

## Rejected imported values

No reference-server name, actor-kind constant, struct name, or layout was used
as evidence. The names `SimpleContentGroup24B`, count-minus-one `+0x10`, count
`+0x1C`, and invariant magic `0x3F3E` were rejected as promotions. The value
30001 is retained only because 65 retail packet rows carry it.
