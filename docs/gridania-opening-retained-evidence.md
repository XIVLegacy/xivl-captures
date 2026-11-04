# Gridania opening accounts and named-call evidence

The retained eLeMeN Sundered Skies walkthrough explicitly gives archers,
gatherers and crafters an action-bar attack instruction. It separately
narrates an event and transfer to Gridania. The retained Gamer Escape quest
and plot accounts add generic encounter and story progression. These remain
secondary accounts, without an attributable player/session or exact client
event invocation.

A focused query of all 54 retained packet members found no selected
`Man0g0` class or `processTtrBtl001`/`002`/`003` method in the named fields
specified below. This is a finite wire-field result, not historical absence
or a complete search of every possible caller form.

The authenticated Lua/widget contracts remain owned by
`xivl-client-scripts:docs/gridania-opening-tutorial-contract.md`. Agreement
with a walkthrough does not join its scenario receiver, player state, widget
instance or subsequent server event.

## Retained source identities

The source owners preserve provenance and evidence classes:

- [eLeMeN walkthrough study](../studies/elemen-quest-rewards-walkthroughs/README.md)
  and [source manifest](../sources/elemen-quest-rewards-walkthroughs/manifest.yaml):
  `web-tables`, wiki/CALIBRATION tier.
- [eLeMeN HTML archive](../sources/elemen-site-archive/manifest.yaml):
  `archive`, preservation only. Reading the preserved HTML does not elevate
  the community account's tier.
- [Gamer Escape source](../sources/gamerescape-tables/manifest.yaml) and
  [study](../studies/gamerescape-tables/README.md): `web-tables`, wiki tier.
  Edit timestamps date revisions, not observations or a synchronized 1.23b state.
- [Retail packet source](../sources/pcap-1.23b/manifest.yaml):
  owner-attested retail 1.23b `packet-capture` evidence.

The selected eLeMeN record is
[`quest-walkthroughs.csv`](../studies/elemen-quest-rewards-walkthroughs/derived/quest-walkthroughs.csv),
physical line 2, `client_quest_id=110005`, `main`, `Gridania`, client English
title `Sundered Skies`. Its Japanese title matches the retained transcription
section and HTML title. The study's [name-join method](../studies/elemen-quest-rewards-walkthroughs/derived/glossary.md)
owns the client-ID association. This row does not independently bind that ID
to a `Man0g0` invocation.

| Retained member | Bytes | SHA-256 |
| --- | ---: | --- |
| `elemen-quest-rewards-walkthroughs/objects/pages/walkthroughs-main.md` | 77534 | `a0718742a52013356cc8e1c55dae820a8ca763ca2fae00d68e1a389f6cb94d5e` |
| `elemen-site-archive/objects/ff14_dated_archives/quest/MainQuest/Gridania1.html` | 22497 | `8f15e5eff6ff7e4a28a5dd62981abd4ab2f5f160f77eb68b921e4305c4a87843` |
| Gamer Escape `pages/Sundered_Skies.wiki` | 1612 | `73a41f17363bb217e9525cd335ff8b83156cacf4062c0adf8fc9c4df43efa11c` |
| Gamer Escape `pages/Sundered_Skies_Plot_Details.wiki` | 3011 | `edb934454b0de7dd6b10c0144226e5d869898e64cf77fae94b0a2f3bb801c2dd` |

eLeMeN member paths above are relative to `sources/`. Its
[URL map](../studies/elemen-site-archive/derived/url-map.csv), line 251, maps
the HTML to the original `quest/MainQuest/Gridania1.html` URL. The selected
transcription section is lines 9-122. The retained collection's final-1.x
edition attribution is not a dated runtime witness for these instructions.

The Gamer Escape archive's declared size/hash and embedded member-inventory
hash matched before the two exact members were interpreted. The source
manifest owns those archive coordinates. The quest's own header records
[revision 508056](https://ffxiv.gamerescape.com/w/index.php?oldid=508056),
`2012-07-20T15:49:25Z`. The plot's header names `Sundered Skies/Plot Details`,
[revision 270550](https://ffxiv.gamerescape.com/w/index.php?oldid=270550),
`2011-11-07T02:04:04Z`. Line numbers below include their six-line headers.

## Class instructions and progression accounts

These are paraphrases of the sources, not rendered client observations.
HTML and MD locators refer to the exact eLeMeN members above.

| Account | Source locator | Supported limit |
| --- | --- | --- |
| Archers, gatherers and crafters display the action bar after targeting, select an action and attack. | HTML 210-212; MD 56-58 | No particular action, accepted-use callback or completion condition is named. |
| Fighters except archers approach and confirm the target to begin repeated auto-attacks. | HTML 207-209; MD 53-55 | This is a separate class-marked instruction. |
| Fighters accumulate TP and select a weapon skill. | HTML 218-225; MD 63-69 | These headings are fighter-only and do not impose TP or weapon-skill use on Hand/Land starters. |
| A fighter-only battle note says the wolf cannot reach zero HP or the fight finish before the weapon-skill lesson is checked/confirmed. | HTML 188,194 | The wording does not explicitly identify actual weapon-skill execution, an OK acknowledgement or a server-accepted action as the trigger. This note is absent from the selected MD/CSV steps. |
| Defeat is followed by an event, automatic transfer to instanced Gridania and a quest item. | HTML 231; MD 73 | The short defeat clause does not specify a Hand/Land predicate, exact enemy count or selected code event. |
| The quest account describes an opening tutorial with three Bloodthirsty Wolves and later city/NPC quest progression. | Gamer Escape quest 30-33 | Generic walkthrough prose, without class alternatives, exact lesson or invocation. Its Non-Combat infobox label at line 10 does not erase the combat account. |
| Rescue and travel dialogue appear in the plot account. | Gamer Escape plot 66-84 | It does not independently name the wolves, repeat tutorial actions or supply the quest page's complete later progression. |

In the preserved HTML source, a shared tutorial notice opens at line 198 and
closes at 229. The final sorcerer-only defeat instruction is inside that
notice. The unqualified event/transfer paragraph at 231 follows its closing
tag, before the next Gridania heading at 236. It is page-level continuation,
without a stated Hand/Land completion predicate. Source markup order is not
a captured event trace.

The accounts' different coverage and revision histories are preserved rather
than combined into one event sequence. Agreement on generic combat or later
progression does not prove independent observations, the same player/state,
successful widget creation/closure, or a causal server event.

## Exact retained packet query

All 54 original members named by the packet source manifest, totaling
7,242,352 bytes, matched their declared sizes and SHA-256 values before
decoding. This authenticated the members directly, without reauthenticating
the containing ZIP. The source-manifest SHA-256 was
`6136e448317e5e80fba964a34038c65b6d4c76e5cbc6f338c9e663eabffc8992`.

Only canonical clear TCP 54992 game lanes were admitted. Lobby 54994 and TLS
were excluded. Offsets below are in the application after the game-message
preamble, not the outer frame or subevent header. The field layout is also
documented by the [named-event query](../studies/request-nmrush-caller-bindings/README.md#source-and-query).

| Direction / opcode | Selected field | Inspected count |
| --- | --- | ---: |
| s2c `0x00CC` | Class `[0x24,0x44)` | 831 |
| s2c `0x0130` | Function `[0x29,0x49)` | 200 |
| s2c `0x0130` | Complete typed span `[0x49,0x89)` | 200 spans, 137 string leaves |

Class equality selected exactly `Man0g0`. Function and typed-string equality
selected exactly `processTtrBtl001`, `processTtrBtl002` and
`processTtrBtl003`. Equality was case-sensitive over full byte strings, with
no prefix, alias, path or raw ASCII search. Btl001 was an earlier-stage
context selector, not evidence of continuation. There were zero matches.

Framing, compression flags, inflation and exact admitted stream/subevent
consumption passed. The canonical reducer excluded 228 raw trailing stream
bytes, separate from the admitted complete-frame streams. All selected fixed
fields had full width and zero NUL padding. Every typed span reached its
terminator with zero remaining padding; no short-field or type failure was
silently discarded.

## Reproduction and remaining boundary

The decoder was `tools/extractors/extract_00da_00e1_comparison.py`,
`_decode_capture`, at revision
`38ad4d2e08c5846a463b12ef5f8529fdcce0af4d`. Its file SHA-256 was
`c48f1224ca62d7c0ca6ca876751caaeff243e9b7f7af1507dfabbeab1f89fdc4`.
[Packet decoding](pcap-decoding.md) owns reconstruction and chronology limits.

Authenticate exact members first and validate framing with
`tools/validate_framing.py`. Query the fields and full-string predicates
above on the decoded s2c records. Traverse all 64 parameter bytes: tags
`00/01/06` have four-byte leaves, `02` a NUL-terminated string, `03/04/05`
no leaf bytes, and `0F` terminates the span with zero padding afterward.
In-memory positive controls checked class, direct-function and reflective
string matches plus rejection of changed-case values. The published Warden
creation at `teleport_to_camp_tranquil.pcapng`, main connection 0, frame 61,
subevent 14, provided a retained class-window control.

The zero result closes only these selectors in these fields of the
authenticated retained members. No match supplied a candidate for a bounded
same-connection actor/owner/state/continuation join. Alternate caller forms,
excluded protocols and unrecorded sessions remain outside the result.
The missing same-player invocation and subsequent event/state/outcome are
still unestablished. The secondary accounts do not supply that join or prove
native/rendered widget completion.
