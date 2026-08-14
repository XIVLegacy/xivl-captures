# Director Wire Identity Verification

## Study contents

This study independently tests four wire hypotheses against the 53 retained
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

Regenerate or verify the canonical products:

```text
python tools/extractors/extract_director_wire_identity.py
python tools/extractors/extract_director_wire_identity.py --check
```

The extractor deliberately excludes login captures through the repository's
canonical `default_corpus_paths()` boundary. Group application payload begins
after the 8-byte inner header and 8-byte game-message preamble.

## Source material

The sole runtime source is the repository's `pcap-1.23b` set: 53 canonical
retail captures selected by `default_corpus_paths()`. The static cross-check is
linked by repository-qualified path and is not treated as packet evidence.

## Promoted conclusions

The promoted results are the four bounded verdicts in `derived/verdicts.md`:
two same-ID EventStart/content-member correlations use high nibble 4 without
proving director identity; party-battle headers carry type 30001; and the
proposed offsets conflate the large Group member packet with the compact
content-member packet.

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

## Further research

No broader retail corpus exists. Catalog consumers may adopt the corrected
packet offsets now; stronger class naming would require an independent static
client identity chain rather than another interpretation of these bytes.
