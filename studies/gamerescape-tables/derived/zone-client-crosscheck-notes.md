# Mob-sighting zones vs client zone data

`mob-locations.csv` carries a free-text `zone` per sighting, and those 51 strings
are not one kind of thing: most are real zones, some are sub-areas inside a zone,
and a few are guildleve battle names. `zone-client-crosscheck.csv` classifies
each one against the client's own zone tables, so the sighting table can be keyed
safely.

Generation provenance is recorded in `file-inventory.csv`. The crosscheck used
`<client-data-csv>` and a historical external zone roster as inputs.

## Client zone tables

| Table | Holds |
|---|---|
| `xtx_placeName.csv` | 923 place names; English short at index 2, long at index 3 |
| `_zoneParam.csv` | 111 zone ids, each pointing at one place-name id |
| `zoneGroupParam.csv` | 42 zone groups, over the same place-name space |

Two client spellings have to be normalised before anything matches: field-zone
names are lowercase (`lower La Noscea`), and **non-breaking hyphens are stored as
the control code `[@1F]`** - `Tam[@1F]Tara Deepcroft`, `Mun[@1F]Tuy Cellars`,
`Toto[@1F]Rak`. GE also prefixes "The" inconsistently. Folding case, the article
and all punctuation resolves every case that is resolvable.

## Results

| Classification | Strings | Sightings |
|---|---|---|
| `client-zone` | 43 | 1,429 |
| `client-place-not-a-zone` | 5 | 57 |
| `not-in-client` | 3 | 14 |

1,429 of 1,501 sightings (95%) sit in a real client zone.

- **`client-place-not-a-zone`** - `Castrum Novum`, `Natalan`, `Zahar'ak`,
  `Murmur Rills`, `Paglth'an` are place names the client knows but are *sub-areas
  inside* a zone, not zones. GE filed them in the `zone` column anyway, so these
  57 sightings have no zone id and their real zone has to come from elsewhere.
- **`not-in-client`** - `The Battle for Hyrstmill` and
  `The Battle for the Golden Bazaar` are guildleve names, not places (the client
  has `Hyrstmill` and `The Golden Bazaar` as place names but the battles are
  leves); `Y'shtola's Ship (Instance)` is an instance label.

## The Coerthas ambiguity, resolved

The evidence-map flags that GE carries both `Coerthas` and its split sub-zones.
The client settles it: `Coerthas` is **its own zone, id 146**, alongside
`Coerthas Central Highlands` (143), `Eastern Highlands` (144),
`Eastern Lowlands` (145), `Central Lowlands` (147) and `Western Highlands` (148).
It is not a grouping label - it is a distinct zone that happens to share the
region name.

The same applies to GE's duplicate `The Mun-Tuy Cellars` / `Mun-Tuy Cellars`:
both fold to client zone 157, so that inconsistency is harmless.

Note that **most zone names are simultaneously a zone and a zone group** - group
401 wraps zone 143, and so on - so the classification tries zone first. No GE
string resolved to a group without also resolving to a zone.

## One GE zone name maps to several client zone ids

1.0 shipped duplicate copies of field zones, so `North Shroud` is client zones
152, 207, 247 and more; `Western Thanalan` is 172 and 211. The crosscheck lists
all of them rather than picking one. Anything keying a sighting to a single zone
id has to decide which copy it means; the id list is deliberately not collapsed.

## Client zones with no GE sighting

`client-zones-without-ge-sightings.csv` - 23 zones. The absence is expected
rather than a gap: they are city wards (`market wards`, `Peasants Ward`,
`Merchants Ward`, `Sailors Ward`), grand company halls (`Maelstrom Command`,
`Hall of Flames`, `Adders' Nest`), water zones (`Rhotano Sea` x6,
`Strait of Merlthor`), an `inn room`, a `transmission tower`, and the
region-level entries `La Noscea` / `Thanalan` / `Black Shroud`. GE documents
field mobs, and none of these hold any.

## Historical zone-data cross-check

This study records two cross-repository findings without changing the external
consumer.

Both findings were acted on by a downstream consumer, and this file's counts are
regenerated against the historical external roster (86 zones):

- **GE-sighted client zones with no entry in the historical external roster
  consulted at research time: 2, covering 8
  sightings** - `Turtleback Island` (client 237/270, 5 sightings) and `Coerthas`
  (146, 3). It was 4 zones and 32 sightings; `Shposhae` was mapped by commit
  `3bd4c79d` and `Cutter's Cry` by `ce19f8fe`. The roster documents that it covers
  only ids carrying a map-code, so the remaining two are likely among its excluded
  placeholder rows - worth confirming rather than assuming.
- **The raw `[@1F]` control codes in `display_name` were decoded** by a
  downstream consumer
  `69a5b856`: zones 157, 158 and 159 now read `The Mun-Tuy Cellars`,
  `The Tam-Tara Deepcroft` and `The Thousand Maws of Toto-Rak`. Zones 177 and 201
  had the code as their entire display name, so decoding left them empty strings
  rather than named - still worth a look, and note that the code remains in
  client-data's own `xtx_placeName.csv`, which is the upstream table and not a
  defect there.

## Zone data path

The crosscheck imported external zone ids from the historical roster at research
time. The resulting ids are
preserved in `zone-client-crosscheck.csv`; the roster is not bundled here.
