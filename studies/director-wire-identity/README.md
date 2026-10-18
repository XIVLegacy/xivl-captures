# Director Wire Identity Verification

## Study contents

This study independently tests four wire hypotheses against the 54 retained
retail 1.23b captures. It decodes all observed `0x017A`, `0x017C`, `0x017D`,
`0x017E`, `0x017F`, `0x0183`, `0x0187`, and `0x018B` packets, all c2s
`0x012D` EventStart role rows, and both member-list forms. Numeric packet
fields remain uninterpreted unless the static client layout supplies the name.

## Start here

- `derived/verdicts.md` - claim verdicts, exact counts, and static cross-check.
- `derived/accounting.json` - corpus reconciliation and distributions.
- `derived/group-packets.csv` - one row per Group-family packet.
- `derived/group-members.csv` - transposed `0x017F` and `0x0183` member rows.
- `derived/event-role-candidates.csv` - EventStart owner actors and event names.
- `derived/zone-controller-identity.md` - seven paired retail observations of
  the numeric SetMap field and ZoneMaster actor-ID encoding.

Regenerate or verify the canonical products:

```text
python tools/extractors/extract_director_wire_identity.py
python tools/extractors/extract_director_wire_identity.py --check
```

The extractor uses the repository's canonical `default_corpus_paths()`
boundary, including the raw 54992 game lanes from `login.pcapng`. It does not
decode the capture's raw 54994 lobby lanes or TLS account traffic. Group
application payload begins after the 8-byte inner header and 8-byte
game-message preamble.

## Source material

The sole runtime source is the repository's `pcap-1.23b` set: 54 canonical
retail captures selected by `default_corpus_paths()`. The static cross-check is
linked by repository-qualified path and is not treated as packet evidence.

## Promoted conclusions

The promoted results are the four bounded verdicts in `derived/verdicts.md`:
two same-ID EventStart/content-member correlations use high nibble 4 without
proving director identity; party-battle headers carry type 30001; and the
proposed offsets conflate the large Group member packet with the compact
content-member packet.

The separate `derived/zone-controller-identity.md` records observed ZoneMaster
object identities and does not change these four director verdicts.

## Topics

- Director-role actor correlation
- Group header type values
- Group and content-member layouts
- Retail packet counts and field distributions

## Evidence boundary

EventStart `owner_actor_id` is role-bearing, but an event name alone does not
prove a server-side class name. GroupHeader application `+0x08` is a sequence
or session value, not an actor ID. A role/member match therefore means only
that the same retail actor ID is both an EventStart owner and a content-member
entry in the same capture. It does not establish server implementation.

## Evidence gaps

No retained packet names a server-side director class. The static Group path
does not mask the actor-ID high nibble or compare a member ID with a director
identity. EventStart names establish bounded roles only, and the 30001 result
is scoped to one party-battle capture.

## Selected commandJudgeMode request vectors

The complete EventStart owner census contains five `commandJudgeMode`
requests. Their complete encoded argument vectors were read from the four
original members below. Each locator is main connection 0, c2s, subevent 1,
at decoded-body offset 64. Frames and subevents are zero-based; completing
capture packet numbers are one-based.

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `add_str.pcapng` | 20056 | `246e4948a7ca1e4dc620e724677bfd9153ce76f6445a557967d309e9946021ed` |
| `gather_wood.pcapng` | 157688 | `c308aa4c984eb3e1912383c06e5115c6924713978df43cdb8075335e1bac7d32` |
| `harvest.pcapng` | 60680 | `8522a844b6904207c3465ae1d1038599eddb8b9dc47800d5230c8a1c3ad0e440` |
| `local_leve_complete.pcapng` | 358296 | `4f0793f354140478725bf2c30642a3458a854460f47fb11a7af635c8881d95cd` |

All nine positions in each vector are explicit wire tokens. `nil` denotes
tag `0x05`; integers use tag `0x00` and four big-endian signed-int32 bits.
`ref` denotes tag `0x06` and serialized binding-reference bits, not an
identified native object or Lua table.

- V0: `[nil,nil,nil,nil,ref(0x029B2941),nil,nil,nil,nil]`.
- V1: `[int(20002),int(0),nil,int(15),ref(0x44B00031),nil,nil,nil,nil]`.
- V2: `[int(20006),int(0),nil,int(15),ref(0x44B00039),nil,nil,nil,nil]`.

| Member | c2s frame | Completing packet | Owner bits / qualified command ID | Vector | END offset in parameters |
| --- | ---: | ---: | --- | --- | ---: |
| `add_str.pcapng` | 6 | 19 | `0xA0F02EE5` / `12005` | V0 | 13 |
| `gather_wood.pcapng` | 10 | 54 | `0xA0F055F3` / `22003` | V1 | 25 |
| `harvest.pcapng` | 9 | 30 | `0xA0F055F7` / `22007` | V2 | 25 |
| `harvest.pcapng` | 47 | 181 | `0xA0F055F7` / `22007` | V2 | 25 |
| `local_leve_complete.pcapng` | 43 | 121 | `0xA0F055F1` / `22001` | V0 | 13 |

The 184-byte application starts after the subevent, inner header and
game-message preamble. Parameters occupy `[49,177)`, exactly 128 bytes.
END is one `0x0F` byte; the remaining 114 bytes for V0 or 102 for V1/V2 are
zero padding. The final byte of the encoded integer 15 belongs to that
integer, rather than an earlier terminator. The seven application bytes
after the parameter span remain outside argument decoding.

The interpretation follows
`xivl-client-structs:manifests/player_command_wire_contract.json`,
`wire.fields`, `serializer` and `terminator`, SHA-256
`5dd48415ad06282cdfac097d08e886509117137ed019d520ac0cfce3562ddc50`.
Nine emitted tokens do not recover the original Lua supplied argument count:
omission and reference serialization can lose input distinctions.

`add_str` frame 6 and `local_leve_complete` frame 43 have different owners
but identical complete parameter blocks and CRC field `0x228A54EA`.
All five CRC fields equal CRC32 over their respective 128-byte blocks.
Thus the block and CRC cannot uniquely identify a request or prove a causal
request-to-callback transfer. No executed producer assigns these observed
integer positions a variation role. These five requests supply no materia
command owner, executed materia variation or `delegateCommand` callback join.

To reproduce, use the source manifest's exact members and the canonical TCP
reconstruction, then select the frame/subevent locators above and decode only
the stated parameter span through END. Preserve explicit nils, END, padding
and the remainder separately. Source identity, admission and framing match
the per-member accounting in
`studies/local-guildleve-dialogue/derived/accounting.json`, SHA-256
`3c349ec3dacba303d26c9666e487353193b7f662a967587dce52c4fd090dec15`.
The four members have zero c2s tails and zero admitted unparsed stream bytes.
Their 18 discarded s2c trailing bytes are outside these c2s observations.

## Further research

No broader retail corpus exists. Catalog consumers may adopt the corrected
packet offsets now; stronger class naming would require an independent static
client identity chain rather than another interpretation of these bytes.
