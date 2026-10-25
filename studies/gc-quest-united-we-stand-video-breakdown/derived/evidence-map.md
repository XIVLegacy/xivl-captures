# United We Stand video evidence

## Source and scope

The source is [Final Fantasy 14 - United we stand](https://www.youtube.com/watch?v=qDdvF9wpCBs)
by ValeSan87, duration 8:13. The
[source manifest](../../../sources/gc-quest-united-we-stand-video-breakdown/manifest.yaml)
pins the single observation record and source metadata. Upload/publication
metadata is 2012-07-27T14:34:44-07:00. It dates publication, not recording.
The 1.x HUD, action bar and HP/MP/TP display support the game's version family;
the exact recording patch is unestablished. Matching 1.23b text does not
authenticate the recording build.

Evidence class: `notes-and-transcripts`, video-breakdown tier. The raw record
uses the thirteen-section video template. Twenty distinct still-frame times
were inspected across two coverage sets, not continuous coverage of the
493-second source. Whole-second player times and the in-game countdown are
reproduction locators, without millisecond precision. Stale seek pictures were
excluded. No video/frame file or frame digest is claimed. No matching packet
timeline was used to infer an unobserved action or trigger.

## Confirmed

These verdicts concern displayed pixels. Client cells below corroborate names
and message shapes without selecting historical runtime rows.

| Locator | Observation | Boundary |
| --- | --- | --- |
| 0:00; 4:11 | Three simultaneously visible labeled Ceruleum Generator devices. At 4:11 horizontal blue beams run toward the labeled Magitek Transmitter, with a vertical beam above it. | Visible count and geometry; no complete actor population, coordinates or operation flags. |
| 0:49, target HUD | A suffixed Magitek Vanguard name is visible; both readers transcribed it as `Magitek Vanguard F-1`. | The last glyph/source row is unresolved against the client cell's `F-I`; see Unverifiable. No H-1 assignment. |
| 1:38 | Nonzero transmitter-damage log lines coexist with a glowing generator and horizontal beam in the picture. Values include 260, 220 and 99. | No complete attacker/action/context transcript or vulnerability predicate. A beam does not prove authoritative operation. |
| 1:38; 4:11; 7:41 | Seven Legion names across samples: Eques, Hoplomachus, Sagittarius, Medicus, signifer, Secutor and Laquearius. | Not simultaneous presence, a complete roster, spawn counts or wave order. `signifer` is the battle-log reading; no action name was transcribed. |
| 4:11 | `Paladin (Gladiator Level: 50)`, character Zack Firewing, Full Party panel with seven other rows. | Visible UI context; equipment/buffs, other jobs, NPC allies and mitigation were not inventoried. |
| 0:00 | HUD `Castrum Novum Transmission Tower`, remaining countdown 29:43. | Already inside the battlefield; no entry allowance or start time is proved. |
| 7:50; 7:51; 7:52 | Foreground glow/beam at 7:50; similarly framed device dark with countdown 21:52 at 7:51; journal/chain overlays present and countdown absent at 7:52. | Sampled visible order, not exact timing, same-actor identity, device death, transmitter defeat or the advancement cause. The transmitter is off-screen in the close ending view. |
| 7:52; 7:53 | Journal update names `United We Stand (Limsa Lominsa)`. At 7:53 chain #2, 60-second chain timer and 618 (+25%) experience are displayed. | Journal update and chain-context EXP; not a complete quest/reward transaction or seal award. |
| 8:00; 8:11 | Black picture at 8:00, then upward structure/vertical-beam view at 8:11 with chat and without combat HUD in view. | A scene transition is an interpretation; no continuous black interval or destination zone was established. |

### Client-text identity and locators

The four selected members were read from the authenticated decoded 1.23b CSV
archive declared by `xivl-client-data:manifests/private_csv_corpus.json`,
input `decoded-csv-corpus-1.23b`, extraction `2012.09.19.0001`.
Archive: `XIVLegacy/xivl-private-assets` commit
`8b38a02ce8ebf662b931092e46273251b38c58f0`,
`extracted/ffxiv-1.23b/client-data/csv.zip`, 70,110,686 bytes, SHA-256
`006f9438a8cfd9277376f0ab28474500c67e4665050aa631cae64c9e6f38a5b0`.
Member size, digest and parsed row count matched
`xivl-client-data:manifests/tables.json`. Search covered all cells of these
four members only; it is not an all-corpus absence result.

| `xivl-client-data:csv/` member | Bytes | SHA-256 |
| --- | ---: | --- |
| `worldMaster.csv` | 1851138 | `2e2e2dd5cd9651388f6fa575b4229081ad0452165e78b725df0a5b5b7cf7c643` |
| `xtx_displayName.csv` | 838262 | `36c5dfba312695d9f4ee090dba123dfd7792feba55d88b0062c070d98abc0505` |
| `xtx_raidDungeon.csv` | 2381 | `24c7e9a071c5a16b8a38254588e350e7e7b043e2dfe4129ecd5363d2f05f6059` |
| `xtx_quest.csv` | 2953504 | `938640466b314242916f1f8877a90154c4f4db7aa63de6223e6af4aa194e6719` |

Field numbers are the original numeric header labels, not guessed locale
offsets. Field 1 is physical CSV cell 3, field 2 is cell 4, and field 26 is
cell 28; the leading cell carries the original row ID.

| Source cell | Result |
| --- | --- |
| `xtx_quest.csv`, 111432 field 2 | Exact `United We Stand (Limsa Lominsa)`. Separate 111632/111832 cells name Gridania/Ul'dah. |
| `xtx_raidDungeon.csv`, 13 field 26 | Exact `Castrum Novum Transmission Tower`. |
| `xtx_displayName.csv`, 3210801/3210802 field 1 | `magitek transmitter` / `ceruleum generator`; casefold matches the displayed labels. |
| `xtx_displayName.csv`, field 1 | Casefold candidates: secutor 3180023/3280035, eques 3180024/3280038, sagittarius 3180025/3280039, hoplomachus 3280036, laquearius 3280037, medicus 3280040, signifer 3280041. Each has the `VIIth Legion` prefix. Duplicate names prevent unique row selection. |

Display-name keys do not identify the separate appearance/actor rows. No
actor-class, graphic, content or command join follows from these name matches.

### Quoted system-text verdicts

The raw record preserves four readings at 7:53. They are compatible with
client templates, with the following exact-text limitations:

| Raw candidate | Client cell and verdict |
| --- | --- |
| `"United We Stand (Limsa Lominsa)" has been updated in your journal.` | `worldMaster.csv` 25116 field 1 contains a quest-sheet substitution and curly quotes, not the literal rendered sentence. Title cell 111432 matches separately. Straight quotes are a transcription distinction; exact rendered punctuation is not certified. |
| `EXP chain #2!` and `Chain timer set to 60 seconds.` | `worldMaster.csv` 33919 field 1 is one template with two numeric placeholders and a newline. Compatible message structure; 2 and 60 are observed dynamic values. |
| `You earn 618 (+25%) experience points.` | Compatible conditional head/earn, quantity, optional percentage and point/points template family. Identical field-1 cells occur at 33934..33938, 33940..33941 and 33945..33955. Neither a unique source row nor its historical arguments is established. 618 and 25 are observed values. |

The exact 33919 cell is:

```text
EXP chain #[@number:022003e80b03]![@newline:02100103]Chain timer set to [@number:022003e80d03] seconds.
```

The exact 25116 cell, with literal U+201C/U+201D shown as ASCII escapes, is:

```text
\u201c[@sheet:02280fff0a7874782f7175657374e8020303]\u201d has been updated in your journal.
```

The EXP family's equality was checked on the full parsed cell, not keywords.
No rich-text renderer or runtime-argument evaluation was performed. These are
compatible templates, not proof of literal source sentences. No NPC/enemy
dialogue or named command/action transcript was supplied for a further match.

## Contradicted

No positive behavioral contradiction with an inspected packet/client timeline
was established. Unseen or unmatched behavior is unresolved. The candidate
suffix and punctuation differences below are exact-text limitations, not a
proved runtime contradiction.

## Unverifiable

- The target's final suffix glyph was read as `F-1` in the video. All English
  singular cells containing `magitek vanguard` in the selected member are:
  3109001/3109003/3209001 unsuffixed; 3109002/3109004 `H-I`; 3209002 `F-I`.
  Row 3209002 field 1 is exactly `magitek vanguard F-I`, suffix bytes
  `46 2d 49` (capital I), while digit 1 is `0x31`. No `F-1` candidate cell
  occurs in that bounded family. The reading, recording build and historical
  row assignment cannot be resolved from this lexical comparison. Do not
  silently replace the raw transcription or assign a runtime/appearance row.
- ASCII quotation marks in the raw journal reading differ from the template's
  curly quotes. Quote the raw reading as a candidate, without claiming exact
  client punctuation.
- The initial observer's nearly-empty-generator HP readings at 3:26, 5:54 and
  7:27 were not independently checked. They are excluded from confirmed HP/state
  evidence and cannot prove same-device death, repair, reactivation or a reset.
- Publication metadata does not establish the recording patch. No exact 1.23b
  runtime state or normal/hard assignment is certified.

## Unique value

The sampled video supplies visible device/beam geometry, a suffixed Vanguard
target, seven displayed Legion names and a narrow order of glow loss followed
by the journal display. It also preserves the dynamic chain-context EXP value.
The [historical account](../../gamerescape-tables/derived/united-we-stand-encounter.md)
is a separate secondary source; agreement with one observation does not verify
its unobserved generator, reinforcement or targeting rules.

## Gaps

Entry/exit, outer-zone gates and patrols, full party/enemy populations, actor
lifetimes, coordinates, generator/transmitter HP, operation/reactivation rules,
waves, timing predicates, enmity/aggro, the decisive hit, journal cause,
subsequent reporting and full rewards remain unestablished. No named command,
resource, animation, director or authoritative AI binding follows. There is no
complete action/dialogue transcript or exhaustive repetition count, and no
Rivenroad or normal/hard-mode evidence in this source.
