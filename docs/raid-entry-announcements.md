# Announced raid entry requirements

The retained Lodestone announcements described the original 1.18 entry
requirements for the Thousand Maws of Toto-Rak and Dzemael Darkhold, and the
1.21 party and level requirements for Cutter's Cry. These are dated
first-party announcements of intended behavior, not observed 1.23b admission
or server enforcement. The source and study class is `web-tables`, tier 3.

## Patch 1.18: Toto-Rak and Dzemael Darkhold

The 2011-06-20 announcement, *Instanced Raids Unveiled!*, explicitly targeted
1.18 in its opening paragraph. Its comparison table stated:

| Requirement | The Thousand Maws of Toto-Rak | The Dzemael Darkhold |
| --- | --- | --- |
| Discipline and rank | Disciple of War or Magic, rank 25 or higher | Disciple of War or Magic, rank 45 or higher |
| Party | 4 members | 8 members |
| Visit limit | 60 minutes, earth time | 60 minutes, earth time |
| Entrance location | Silent Arbor, Tinolqa | Dragonhead, Coerthas Central Highlands |
| Requisite quest titles | Imperial Devices (Gridania), Imperial Devices (Limsa Lominsa), Imperial Devices (Ul'dah) | Into the Dark (Gridania), Into the Dark (Limsa Lominsa), Into the Dark (Ul'dah) |

The table lists the city quest titles without specifying a completion stage
or requiring all three. It gives no reentry wait. The named entrance
locations are geographic descriptions, not numeric actor IDs, selected zone
copies or destination coordinates. Source locator: opening paragraph and
comparison table, retained Markdown lines 5 and 19-25.

## Patch 1.21: Cutter's Cry

The 2012-03-07 announcement, *New Instanced Raids*, explicitly targeted patch
1.21 in its opening paragraph. The first paragraph under `Features` described
Cutter's Cry for a full party of eight Disciples of War and Magic at level 45
or higher. Source locator: retained Markdown lines 5 and 13.

This post supplies no visit limit, reentry wait, requisite quest or entrance
requirement. Its opening mentions two new raids but names only Cutter's Cry.
It supplies no Aurum Vale requirements.

## Relationship to other findings

The [eLeMeN entry-rule study](../studies/elemen-instanced-content-entry-rules/derived/evidence-map.md#what-is-web-unique-the-payload)
already records wiki entry parameters and patch-change annotations. These
announcements add first-party attribution for the original versions above;
they do not replace the wiki's later-version record with original party sizes.

The [official patch study](../studies/official-1x-battle-patches/derived/evidence-map.md#patch-122-event-post)
owns the subsequent 1.22 change allowing four through eight participants in
Aurum Vale and Cutter's Cry, with difficulty still designed for eight. Its
separate [1.22a finding](../studies/official-1x-battle-patches/derived/evidence-map.md#patch-122a-event-and-fixed-bugs-post)
owns party commencement restrictions. The
[timer announcement finding](../studies/lodestone-dev-patch/derived/timer-announcements.md#announced-rules)
owns the separately sourced 1.21 reentry waits. None of those later or
separately sourced rules is a field in these two announcement bodies.

The published `xivl-client-scripts:docs/instance-entry-client-contracts.md`,
`Variant identities and unresolved admission fields`, already owns recovered
quest identities and entry-request limits.
`xivl-client-data:docs/dungeon-map-identities.md`, `Layout and place-name
joins`, owns static layout associations. Announced requirements do not join
either finding to accepted entry. Runtime confirmation still needs an
identified actor and selected method with complete supplied arguments,
selected duty/Director, accepted continuation and destination transform.
Enforcement of eligibility, visit duration and reentry policy needs an
attributable retail witness for the relevant version.

## Source identity

Source and study id: `lodestone-dev-patch`. The
[source manifest](../sources/lodestone-dev-patch/manifest.yaml) owns member
identity and preservation provenance. The
[page inventory](../studies/lodestone-dev-patch/derived/file-inventory.csv),
rows keyed by the two slugs below, owns their publication dates and original
URLs. The [study](../studies/lodestone-dev-patch/README.md#evidence-gaps)
describes the transcription and announced-intent limits.

Both members are under `sources/lodestone-dev-patch/objects/pages/`:

| Member | Publication date | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `instanced-raids-2011-06-20.md` | 2011-06-20 | 2173 | `c27e1eea2c2594248d10d34b53c157ed70641a1741d320ed37f5187d26d1a7d1` |
| `new-instanced-raids-2012-03-07.md` | 2012-03-07 | 1850 | `7b1edcad0c1255462c12d053ae5f4e52ade7b479abb8ff3983d2dfe2a4f48602` |

Only the retained Markdown text supports the claims here. The 2011 post's
images were not inspected. Neither post identifies a client executable build.
