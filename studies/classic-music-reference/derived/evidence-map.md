# Music crosswalk evidence

## Result and source

The [crosswalk](music-crosswalk.csv) accounts for all 109 Music List rows,
IDs 1 through 109, once each. Every title and usage description comes from
the community wiki. None receives independent official-title or per-zone
playback confirmation from the selected retail evidence.

Source identity belongs to
[`classic-music-reference`](../../../sources/classic-music-reference/manifest.yaml):
`music.html`, revision 1196, 23,576 bytes, SHA-256
`53ec28c33e7134de4e5417dc76259afc0f66028cdc5aba19bdb52e9c9239ccdb`.
Its source Last-Modified was `Wed, 02 Jun 2021 07:09:14 GMT`. This identifies
the retained page, not a retail-era source or the current live revision.
The original HTML remains local-only and no permanent archive is declared.

The page's footer attributed most usage descriptions to
`http://finalfantasy.wikia.com/wiki/Before_Meteor:_Final_Fantasy_XIV_Original_Soundtrack`.
That downstream page was not independently inspected. The study retains
`web-tables` evidence class even where a numeric ID intersects a retail
observation. The cited retail finding remains the authority for that field.

## Independent dimensions

| Crosswalk field | Meaning |
| --- | --- |
| `music_id`, `source_name`, `source_usage`, `source_line` | The three Music List cells, with HTML entities decoded and surrounding whitespace removed, plus the one-based HTML row-start line. Source spelling, punctuation and qualifiers are preserved. Music ID is the table row locator. |
| `title_confidence` | `secondary-named` for a reported name, `secondary-tentative` for a questioned name, `descriptive-only` for the opening-movie label, or `unresolved-placeholder` / `unresolved-unknown`. These are evidence labels, not probability scores. |
| `usage_confidence` | `secondary` for a reported description, `secondary-incomplete` for explicit needs-more-info wording, `secondary-note-only` for placeholders, variant/event glosses or removal notes, or `unspecified` for an empty cell. No value means independently verified zone usage. |
| `wiki_version_scope` | The page's explicit pre-1.18, 1.18-onward, 1.19-onward or removed-post-launch claim. `unspecified` supplies no patch guarantee. |
| `numeric_id_evidence` | `shipped-lua-reference`, `retail-packet-request` or `wiki-only`, using only the selected intersections below. This is not a complete client or packet ID census. |
| `computed_resource_key`, `resource_availability` | The native request-key formula applied to the listed ID, with availability `not-checked`. A computed key does not establish a resource file, a title, audible output or selection policy. |

## Retail numeric intersections

`xivl-decomp:docs/net/music-control-runtime.md`, Binary and method, Wire
fields and Lua caller boundary, owns the original executable identity and
the authenticated decoded-source locators used here. The packet path consumes
a u16 song and derives `0x07FE0000 + songID` when requesting a resource. It
does not select a track from a zone. The key arithmetic does not establish
that any particular resource exists.

| IDs | Selected retail evidence | Supported intersection |
| --- | --- | --- |
| 7, 25 | The published Lua caller boundary records `man0u0.lua:407-411` with `(7,2)` and `1714-1718,1836-1840` with `(25,1)`. | Shipped script references to numeric IDs. The native receiver binding and actual execution remain separate. |
| 7, 61 | The same boundary records `populacecutsceneplayer.lua:220-224,315-319` with `(7,2)` before replay and `(61,2)` after replay. | Additional shipped script references. The cleanup reference to 61 does not establish every inn's soundtrack. |
| 13, 57, 83 | [Map music wire evidence](../../music-000c-wire/derived/evidence-map.md), Captured layout and locators, owns six requests in five selected captures: combat-named members carried `13/1 -> 57/4`, and the mount-named member carried `83/4 -> 57/4`. | Captured numeric requests and connection-local sequences. The filenames do not identify an exact zone or authenticate the wiki titles. |

Thus 7, 25 and 61 have selected shipped-script references, and 13, 57 and
83 have selected packet requests. The remaining rows have only the wiki ID
in this crosswalk's evidence set. This does not imply that those IDs are absent
from other shipped scripts or captures. No audio payload was inspected or
played, and no new native trace or packet census was performed for this study.

## Title and version qualifications

IDs 7 and 31 have empty Name cells and `Placeholder` Usage cells. ID 96 is
`???`; 20 questions its title and suggests a multi-track variant of 5.
ID 32 supplies the descriptive label
`Opening Movie music`. In particular, the shipped references to ID 7 prevent
interpreting its placeholder name as proof of an unused or invalid ID.
IDs 29 and 30 share `Answers`; name equality does not collapse their IDs.

The page labels 30 and 32 removed in post-launch versions. This is a source
claim, not an independently checked 1.23b file-absence result. It labels
52, 60 and 67 as pre-1.18 field tracks, 53, 57 and 62 as their later regional
candidates, and 95 as used from 1.19 onward. Retained older music can remain
addressable without being the later ordinary field selection.

## Regional usage candidates

These are the page's candidate associations, not accepted server zone rows:

| Region or city | Normal candidate | Battle candidate | Source scope |
| --- | --- | --- | --- |
| La Noscea | 53, Freedom | 21, Nail of the Heavens | Normal described from 1.18 onward; 60 described before 1.18. |
| Black Shroud | 57, Whisper of the Land | 13, The Forest's Pulse | Normal described from 1.18 onward; 52 described before 1.18. |
| Thanalan | 62, Widdershins | 25, Quicksand | Normal described from 1.18 onward; 67 described before 1.18. |
| Coerthas | 55, Unspoken | 15, Pennons Aloft | No explicit patch bound in these cells. |
| Mor Dhona | 49, Tears for Mor Dhona | 11, Phantoms on the Lake | No explicit patch bound in these cells. |
| Limsa Lominsa | 59, Navigator's Glory - The Theme of Limsa Lominsa | Unspecified | City association only. |
| Gridania | 51, Born of the Boughs - The Theme of Gridania | Unspecified | City association only. |
| Ul'dah | 66, The Twin Faces of Fate - The Theme of Ul'dah | Unspecified | City association only. |

The packet ID 57 intersects the later Shroud candidate, but the
[retained map-context check](../../music-000c-wire/derived/map-context.md)
does not establish that zone or every Shroud subarea.
The page gives ID 68 the name `With these Hands` with no usage description;
it does not supply a Thanalan normal association for that ID. Neither fact
authorizes replacing a consumer's authored zone values without its own
zone/content acceptance decision. Interiors, private areas, tutorials,
levequests, bosses and seasonal overrides require their specific joins.

## Reproduction and boundary

Use the exact manifest-pinned HTML, not a newly fetched live page:

```text
python tools/extract_classic_music_reference.py --html <music.html>
python tools/extract_classic_music_reference.py --html <music.html> --check
```

The standard-library parser selects the Music List table by its three
headers, verifies the complete source digest and revision, and requires
exactly IDs 1 through 109 in order. It preserves the source cells and derives
only the confidence/version labels, selected numeric intersections and
resource-key arithmetic documented above. It does not read sibling checkouts,
download a page or open audio. Ordinary public checks validate the retained
products and checksum anchor without claiming to replay absent HTML bytes.

The crosswalk provides a disposition for every selected source row. A stable
official title needs an independent title-to-resource or authenticated audio
identity join. A historical zone assignment needs a target-specific retail
request/context or another authenticated selection source. This study supplies
candidates with explicit limits, rather than a complete 1.23b soundtrack policy.
