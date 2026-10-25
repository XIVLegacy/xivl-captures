# Rivenroad Hard guide evidence

## Source and attribution

The source is carraway's [post 92 in thread 51632](https://forum.square-enix.com/ffxiv/threads/51632-Rivenroad-%28Hard%29-Discussion-and-Strategies-Thread/page10),
headed `Order of the Blue Garter's Guide to Nael deus Darnus (Hard)`.
It prints compiler Carraway Author and guide date `2012/08/15`; the forum
displays post time `08-16-2012 01:28 PM` and last edit `08-16-2012 05:15 PM`.
Their timezone is unestablished. The author describes the group's first clear.
These are source dates and an attributed player account, not an authenticated
recording build or official Square Enix mechanics documentation.

Stable id: `se-forum-rivenroad-hard-51632`. Evidence class:
`historical-research`, tier 3. The
[source manifest](../../../sources/se-forum-rivenroad-hard-51632/manifest.yaml)
pins unchanged member `rivenroad-hard-51632-page10.html`, 442,836 bytes,
SHA-256 `a45fcb9c2b33b9b898d2c869858057167773af4505cfbb15b3c2f5f6374fec2c`.
The selected HTML post container is `post_788628`; other posts and modern
profile metadata are outside this interpretation.

The post links an original Guildwork permalink and recording `nwvi79-qAjM`.
The forum copy is the retained source; byte identity with the Guildwork
original is unverified. Linked video metadata is not gameplay evidence.

The explicit Hard title supplies this guide's attribution. The separate
[historical mode account](../../gamerescape-tables/derived/rivenroad-encounter.md#mode-attribution)
owns quest-context, repeatable-normal and Hard distinctions. No behavior here
is copied into the other variants.

## Reported encounter claims

[guide-claims.csv](guide-claims.csv) contains 35 source-selected factual rows.
Each has a source section, narrow qualification and verdict
`historical_player_claim`. The ledger covers the arena, reported party context,
named abilities, fragments, both Megaflares, health-bar reset and Dive/fragment
sequences. It preserves approximate values, unspecified delays, conditional
wording and repeated relative placement descriptions.

The source's two-phase/two-Megaflare structure and its numerical HP, damage,
range, count and timing assertions remain player claims. The conditional
one-and-a-half-minute Dive description is not a fixed 90-second timer.
Reported percentages are not verified native comparisons or server thresholds.
Gear targets and tactical party recommendations are not measured mechanics and
are outside the ledger. No quest reward or persistence transaction was observed.

## Client-text qualification

[client-text-crosscheck.csv](client-text-crosscheck.csv) contains 26 literal
name/base/comparison queries and seven quoted-reading classifications. Its
row keys identify text candidates, not historical runtime commands or actors.
Duplicate names retain every candidate for the selected field. Descriptive
headings are not assumed to name commands. `Esuna` is a separate base-name
query; the source uses an inflected form with U+2019.

The authenticated input is `xivl-client-data:manifests/private_csv_corpus.json`,
`decoded-csv-corpus-1.23b`, extraction `2012.09.19.0001`:
`XIVLegacy/xivl-private-assets` commit
`8b38a02ce8ebf662b931092e46273251b38c58f0`,
`extracted/ffxiv-1.23b/client-data/csv.zip`, 70,110,686 bytes, SHA-256
`006f9438a8cfd9277376f0ab28474500c67e4665050aa631cae64c9e6f38a5b0`.
This later static snapshot does not establish the guide's recording patch.

| `xivl-client-data:csv/` member | Bytes | SHA-256 |
| --- | ---: | --- |
| `worldMaster.csv` | 1851138 | `2e2e2dd5cd9651388f6fa575b4229081ad0452165e78b725df0a5b5b7cf7c643` |
| `xtx_command.csv` | 987740 | `2aa0b20822df0b2270918d9ac5525c86a34a941d7c66d17a106add1b2d6567d3` |
| `xtx_displayName.csv` | 838262 | `36c5dfba312695d9f4ee090dba123dfd7792feba55d88b0062c070d98abc0505` |
| `xtx_itemName.csv` | 4428170 | `917c34eb0621b7d7a8261145023d0bb95cd8ca9eb52288ceb66e80d08f0d78c2` |

Member size, digest and parsed row count matched
`xivl-client-data:manifests/tables.json`. Name candidates were selected from
all rows of command field 2, item-name field 5 and display-name field 1.
The original numeric header selects the field; field N is physical CSV cell
N+2. A separate distinctive-phrase pass authenticated all 803 CSV members
before searching, without extracting them or evaluating rich text.

### Name distinctions

- The guide's `Iron Curtain` heading has no exact/casefold whole-cell match
  in the selected name check. `Iron Chariot` is a distinct command-name row,
  23611. It is not silently substituted for the source heading.
- `Thermionic Blast` and `Summon Lunar Fragment` have no whole-cell matches
  in that check. This does not prove absent behavior or a missing resource.
- `Teleport` has a candidate name row, but the heading can describe movement.
  It does not select command 24220.
- Lunar Dynamo has two candidate row keys, Megaflare four and Dalamud Dive
  three. Their names cannot select one key or divide them into normal/Hard.
- Item and actor names do not prove drops, crafting, item use, actor lifetimes
  or appearance/resource joins. The guide's reported pairings remain claims.

### Quoted readings

The CSV's seven `quoted_reading` rows carry exact UTF-8 hashes of complete
`worldMaster.csv` field-1 cells and physical source-HTML locators. Their labels
are locators, not replacement transcripts. The original guide remains unchanged.

| Guide reading label | Client row | Literal verdict |
| --- | ---: | --- |
| Debris notice | 34316 | Exact whole-cell reading. |
| Life / death phrases | 34306 / 34307 | Literal substrings; client adds terminal periods and surrounding italic controls. |
| Hope phrase | 34321 | Client includes spaces after both ellipses and italic controls. |
| Oblivion phrase | 34309 | Client includes a space after the first ellipsis and italic controls. |
| Overhead notice | 34310 | Client says `high overhead`; the guide omits `high`. |
| Purity phrase | 34322 | Complete sentence occurs inside surrounding italic controls. |

The ellipses are three ASCII periods. No rich-text renderer, historical
argument evaluation or source-text correction was performed. Only the debris
reading equals an entire plain client cell. The other readings must retain
their punctuation, control or wording qualifications. A later static-text
discrepancy does not prove what an earlier client rendered.

## Conflicts and limits

The retained Gamer Escape Hard account reports magical immunity during the
Megaflare charge. This guide's Summary describes reduced damage from both
physical and magical sources during charges, without quantifying the reduction.
An unquantified reduction does not exclude zero. The accounts differ in
specificity; their wording does not settle a shared formula, patch change or
exact charge state. Neither claim is upgraded to a measured rule.

The source's heading/text discrepancies are lexical findings. They do not
contradict an observed historical combat timeline: none was inspected here.
Archiving the guide, matching names or locating a system message does not
validate phase thresholds, timers, HP, enmity, elemental weaknesses, mitigation
success rates or spawn schedules.

Actual entry/exit, actor/class lifetimes, command execution, resource selection,
normal/Hard bindings, authored scheduler invocation, complete rewards and
authoritative AI remain unestablished. The guide's repeated relative fragment
locations do not establish distinct coordinates. No captured packet scenario
or inspected video moment was used to settle these claims.

## Reproduction

The [linked-video study](../../side-quest-rivenroad-hard-video-breakdown/derived/evidence-map.md)
owns sampled observations from the guide's video link. Its displayed Hard label,
retained combat text and journal update do not verify this guide's complete
phase schedule, thresholds or action assignments.

Authenticate the HTML member and CSV archive/member identities above. Select
post container `post_788628`, decode HTML entities and read the named sections
in each ledger row. The source quotes are at HTML lines 721, 723, 741, 743,
755 and 759; the Iron Curtain heading is at line 690.

Read CSV with UTF-8-sig, retaining its two header records, original row IDs and
numeric fields. Recompute complete candidate sets in the selected name fields.
For quoted readings, hash each listed full field-1 cell as UTF-8 and compare
the source's literal wording separately from its markup. Do not strip controls,
insert missing words or infer a runtime binding to obtain an exact match.
