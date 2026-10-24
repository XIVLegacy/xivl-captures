# Linkshell master-transfer capture boundary

The complete 54-member `pcap-1.23b` corpus supplies no request matching the
hypothetical rank-10 vector using the known appoint-helper shape,
`[group UID string,member string,10,nil,nil,nil,nil,nil,nil]`. All 126 c2s
`0x012D` typed parameter windows, including the 19 `commandRequest` records,
decoded through END with zero padding. None contained an encoded integer 10,
and no request owner had low word `0x5EA7`. No correlated reply, successful
transfer, or resulting member-rank mutation is established. No rank-10 producer
is proven. This is a bounded
absence in the retained corpus, not evidence that the feature was unavailable
in uncaptured retail sessions.

## Inputs and reproduction

The census used the exact 54 members in
[`sources/pcap-1.23b/manifest.yaml`](../../sources/pcap-1.23b/manifest.yaml)
at capture revision `1fd97b751e474b2024cd7d22277052903a157624`. The manifest's
SHA-256 is `baaa15f99f7f5d865bf2ec0dbcc1e454d034382b0559edccb0085c57c4061cf5`.
Every local object and every member of the 2,622,720-byte archive matched the
manifest filename, size and SHA-256. The archive SHA-256 is
`20a78b9f40ff2393037c9a160c957783cf590b4f01797493d22fcd2039e9cbff`;
the expanded members total 7,242,352 bytes. This covers the entire manifest,
with no unavailable members.

Reproduce against those inputs using the tracked decoder tools at the pinned
revision:

1. Iterate every manifest member after verifying its byte size and SHA-256.
   Use `tools/extractors/extract_streams.py:reconstruct_lanes` to admit clear
   port-54992 game connections. Iterate c2s and s2c separately, use
   `parse_outer_frames`, inflate with `maybe_inflate` when indicated, and walk
   `tools/extractors/extract_observations.py:parse_sub_events`. Do not merge
   connection blocks into a capture-wide chronology.
2. Require sequence coverage using the IP-declared spans from
   `tools/extractors/extract_login_0002_appearance_order.py:_packet_spans`.
   Check complete admitted frame extents, agreement between the compression
   flag and inflated body, complete subevent extents, and zero undecoded body
   padding. All admitted directions passed these checks. They comprised 84
   clear-game connections, 8,970 c2s frames and 10,790 s2c frames. No
   IP-declared TCP payload bytes trailed their complete frames.
3. Select wrapped c2s inner opcode `0x012D`. Application bytes start at decoded
   body `subevent.offset + 32`; the application length is 184. Read the owner
   u32 little-endian at application `+4`, event-name bytes `[17,49)`, and the
   exact 128-byte typed window `[49,177)`. Count all records before applying
   `commandRequest` or owner predicates.
4. Decode tokens from the start of that window through END `0x0F`. Tag `0x00`
   consumes four big-endian integer bytes, `0x02` consumes a NUL-terminated
   string, and `0x05` is an explicit nil. Advance every other supported token
   by its complete encoded width, including item-reference and metadata
   forms, so embedded bytes are not mistaken for tags. Require zero padding
   after END and account for the seven application bytes outside the window
   separately. Test for any tag-0 integer 10 and for the exact ordered vector
   above. Both predicates have zero matches across all 126 requests.
5. Test owner equality with `0xA0F05EA7` and owner low-word equality with
   `0x5EA7`; both have zero matches. These are explicit search predicates.
   The command object reference and scalar command-sheet ID are distinct
   domains: the static producer adds no separate command-sheet ID to the tail
   (`xivl-client-structs:manifests/player_command_wire_contract.json`,
   `wire.fields`, `commandIdentity` and `serializer`).

The full request count agrees with
[`c2s-012d-event-start/derived/accounting.json`](../c2s-012d-event-start/derived/accounting.json),
SHA-256 `124a6bb7dd9b5e9c764401802eca3f40de50a4e11c28f6905646f8bc271263f6`.
The census also reproduced all 96 s2c `0x0132` names and their counts in
[`command-registration/derived/occurrences.csv`](../command-registration/derived/occurrences.csv).
The occurrences file SHA-256 is
`c68acf6c7216205cfd58f87649bbd2a1f516b3c6c74f587583bc255965d93182`.
Its [accounting](../command-registration/derived/accounting.json) SHA-256 is
`4a5e42f992ea906825346eeb61ead5bb4443091826311ba7d2e2d6f002eee677`.
The eight names each occur 12 times. These are generic descriptor
registrations, including `commandRequest`, and establish neither an individual
command's availability nor successful execution.

The full-manifest pass counted 365 s2c `0x017C` headers and read their
little-endian type at application `+0x30`: 265 type 10002, 65 type 30001,
16 type 10001, 13 type 80001, four type 30006 and two type 50001. None was
type 20002. Separately from the absence stated for the study's retained
group-header rows, this full-corpus pass supplies no header-backed
player-linkshell specimen. This does not exclude a standalone rank stream or
identify a post-transfer update. The existing group-combat accounting SHA-256 is
`0b0c4781eb74a6e356c7968872537dbc7a334835198303e3c6583140a72c61f2`.
The group-header CSV SHA-256 is
`ae6c41bc853b64ada5d98ed90e2842ea8d98d9c8cc1cf771f30ce15fa6c31536`.

There were 200 s2c `0x0130` records. With no matching transfer request, none is
identified as a transfer reply from adjacency alone. Separate directions and
connections do not supply an inferred arrival order or causal join.

## Official historical context

The retained official manual describes linkshell invitation as available to
masters and leaders, while managing leader privileges is master-only
(`sources/lodestone-manual/objects/pages/menus.md`, rows under Main Menu).
The source URL is the official
[Menus page](http://lodestone.finalfantasyxiv.com/pl/guide/gamescreen02.html),
preserved by the [manual study](../lodestone-manual/README.md). This distinction
does not describe passing mastership. The party Promote operation in the
manual's Parties page applies to party leadership and does not supply a
linkshell master-transfer rule.

All 36 manual and 63 dev/patch page objects matched their source-manifest
sizes and SHA-256 values. Review of their linkshell contexts and occurrences
of transfer, master and leader found no description of linkshell master
transfer. The exact source-manifest SHA-256 pins are
`1d2de468effd9c7acdd740519d67276a5963ecddab42f17a64c12d86d9b8320e`
for [lodestone-manual](../../sources/lodestone-manual/manifest.yaml) and
`227c70fc0c218149d4fefa493aa1f8e5e2919b28827ec85f638f3e7c0506169c`
for [lodestone-dev-patch](../../sources/lodestone-dev-patch/manifest.yaml).
The transcribed Menus page SHA-256 is
`29f153ad9753a206cc68b36d0067b49e82064d46b2a6d2f04abac57f5a29cf4a`.
These source sets preserve official documented intent and retain the
`web-tables` evidence class. They are separate from observed packet behavior
and native client evidence. The 63-page patch subset ends at 2012-07-10.

The common master archive was also authenticated at 115,606,290 bytes and
SHA-256 `481c27e2738b0f552c754f3f25ca2028560cf13129b3b98f4b8b1028d5cbafee`.
Its actual inventory contains 215 HTML members, rather than the 208 pages
stated in the source-manifest prose. All 215 HTML members, totaling
10,671,252 bytes, passed archive CRC and declared-size checks; their individual
SHA-256 values were recorded before searching the HTML text. This expanded
search includes 2013 material, which must be separated from retail 1.x.

The official
[About the World Merge and World Transfers notice](http://lodestone.finalfantasyxiv.com/pl/topics/detail?id=13222abe211533c87814786dc7c7c72707574cb8)
of 2012-02-17, under About Linkshells / Carrying over linkshells, says that a
master moving to a different World leaves the linkshell while the linkshell
continues in its merged World. It does not describe player-invoked master
transfer or appointing a replacement. The preserved member is
`About the World Merge and World Transfers 02.17.2012.html`, 60,930 bytes,
SHA-256 `8eb947911ad9482b2678ef6f2731cad830501d01639925d09ea9b5069aaabd3d`.

Two 2013 ARR transition notices describe automatic selection of a replacement
master on World transfer. That later documented behavior does not establish
the retail 1.x command or a 1.23b producer. Review of linkshell-containing text
contexts identified no description of player-invoked linkshell master transfer
in the 1.x material.
Image-only text was not searched, and this preserved archive does not cover
every official publication.

To reproduce this archive boundary, enumerate the pinned RAR with 7-Zip
25.01, select all `.html`/`.htm` members, and verify their declared sizes and
CRC32 values after extraction to a separate research directory. Parse the
UTF-8 HTML with Python `html.parser.HTMLParser`, omit script/style content,
and inspect each case-insensitive `linkshell` occurrence with its two
neighboring text lines on either side. Search those contexts for
`master|leader|transfer|promot|appoint|privilege`, then distinguish the
publication's own date and operation. This is a text-context search, not an
exhaustive semantic classification of every archived page.
