# The GE NPC roster vs the client's non-mob actors

`Infobox NPC` was the largest template family in the corpus nobody had mined - 1,335
pages against 1,051 mob pages - and it is the **best-dated GE material in this set**:
263 of those pages were last edited in 2010, contemporaneous with 1.0's launch, and
none after 2012. Every other GE source here drifts toward late 1.x or, for the
behavior-code templates, into the ARR era.

Generation provenance is recorded in `file-inventory.csv`. The verification
guarantees described throughout this file are the checks used to pin each
reading.

## What the pages carry

`npcs.csv` - 1,333 rows over 16 columns, one per `Infobox NPC` call. The dense fields
are `race` (1,282), `zones` (1,261), `gender` (1,242), `map_coords` (1,182),
`locations` (1,116), `affiliation` (1,077), `clan` (935), `occupation` (577) and
`sells` (170).

| Field | Top values |
|---|---|
| `race` | Hyur 411, Lalafell 249, Elezen 221, Roegadyn 176, Miqo'te 153 |
| `clan` | Midlander 292, Wildwood Elezen 134, Sea Wolves 87, Seekers of the Sun 84 |
| `affiliation` | Ul'dah 400, Limsa Lominsa 327, Gridania 303, Ishgard 24, Ala Mhigo 21 |

**No client sheet carries any of this.** The client ships an NPC's *name* and model,
not their race, clan, occupation or where they stood. `map_coords` on 1,182 of them is
the only positional record for 1.0's town population in this repo.

The prose params are deliberately not mined, for the same register reason as the mob
family pages: `Dialogue` (1,144 filled), `Notes` (661) and `Biography` (40) are the
verbatim GE prose these pages exist to host. `Image` is a wiki filename, not a fact.

## The join, and what the actor-id prefix means

**1,272 of 1,333 GE NPCs (95.4%) resolve to a named client actor** outside the monster
ranges - better than the mob side's coverage in the other direction, and close to the
mob join's own hit rate. 1,247 join on the name exactly; the other 25 need one of four
passes, all described below.

The interesting part is where they land. Non-mob actor ids are **not one space**:

| Prefix | Matched NPCs | Merchants |
|---|---|---|
| `10` | 907 | 0.030 |
| `15` | 248 | 0.226 |
| `16` | 120 | **0.967** |
| `17` | 24 | 0.042 |

**Prefix 16 is the merchant space** - 116 of the 120 NPCs in it that GE documents carry
a merchant occupation, against 3.0% of the general `10` population. `15` is mixed shop and
service staff at 23%, which reads as the same kind of role without being reserved for it.
`--verify` holds both halves: the `16` purity above 0.90, and no other space being as
merchant-heavy - a floor alone would pass if the whole roster turned into merchants.

Two small tails also matched: `12` (2), `30` (1), `60` (3) and `91` (4). `Baderon
Tenfingers` is one of the `91` cases, holding actors in both `10` and `91`.

## The unmatched roster, read properly

The first pass through this left 82 unmatched under two guessed causes, and one of them
was wrong: it said "most are actors that sit in a monster range instead". Checking rather
than asserting puts it at **34 of 82, a large minority**, and splits the rest into two
kinds that are not the same problem at all. A spelling pass cleared 7 and a name-form pass 15 more,
leaving 61:

| Cause | Rows | What it is |
|---|---|---|
| `mob-range-actor` | 34 | the name *does* have a client actor, in a monster range, so it is the mob tool's to account for |
| `no-client-actor` | 7 | GE gives them a zone; this dump has no actor of that name anywhere |
| `lore-figure` | 20 | no actor and no zone - documented from other pages' text, never placed |

**The 34 are the corroboration the mob side wanted.** 14 are the rental chocobos on actors
`2210504` to `2210518`, and **12 are the hamlet militia** - `Militia Barber`, `Cook`,
`Smith`, `Outfitter` and the Front, Second and Third Line Archers, on `229005x` to
`229007x`, which is race 1900. Those are the exact names `map_client_mobs.py --verify`
leans on for its ally-side reading of the 1900 block, now attested from GE's own NPC
roster rather than from the client's naming alone. `Bombard` and `Bombard King` are there
too, on race 1016 Bomb - GE filed two monsters as NPCs.

Each militia role also appears **twice** in `npcs.csv` with different races - Miqo'te and
Hyur, or Elezen and Lalafell - because the client ships a race variant per role. That is
most of the gap between 1,333 rows and 1,311 distinct names.

**`lore-figure` is a measured class, not a shrug.** 0.958 of the NPCs that join an actor
carry a zone, so an NPC page with neither is a different kind of record: `Frandelont
Raimdelle` of the Raimdelle Codex, the Ishgardian saints `Daniffen`, `Moergynn` and
`Tothor the Ratcatcher`, and a dozen full names that only ever appear in other pages'
text. `--verify` holds the zone correlation above 0.90 and fails if any `lore-figure` row
turns out to have a zone after all.

### The `no-client-actor` rows were a locale I was not reading

Those 21 were called the real residue - "GE saw them standing somewhere and this dump
carries no actor by that name". That was wrong twice over, and the second correction
matters more than the first.

**`xtx_displayName` is a five-language table with a singular and a plural per language:**

| Columns | Locale |
|---|---|
| 1 | Japanese |
| 2 / 3 | English singular / plural |
| 7 / 9 | German singular / plural |
| 14 / 15 | French singular / plural |
| 20 | Chinese |

Untranslated cells read `[de]` / `[fr]`, and German adjective endings are left as an `[a]`
placeholder. `puk hatchling` is the row that shows it plainly: `puk hatchlings`,
`jung[a] Puk`, `jeune puk`, `jeunes puks`.

An earlier draft of this file called columns 3, 7 and 14 "the full personal name, the given
name and the full personal name again". That reading came from looking only at NPC rows -
**for a personal name every locale reads the same or nearly the same, so the languages are
invisible.** It took a common noun to falsify it. `--verify` now pins the layout on
`puk hatchling` for exactly that reason, and puts a control row through the same check,
since a property that holds cannot otherwise be shown to be tested.

The real finding is better than the wrong one: **1.0's locales did not name Grand Company
NPCs the same way.** The English client shows a rank where the others show the person -
`Storm Sergeant Allond` in English, `Brielle Allond` in French, `Allond` in German - and
GE titles its pages by the personal name. So **15 of the 21 join once the other locales are
indexed**, every one of them Grand Company personnel across all three companies, all on
prefix `10`. The join rate goes 0.944 to **0.954**, and the pass is `other-locale`, not a
name-form pass.

Three needed one more index. `Brooks`, `Cotter` and `Friont` are family names that stand
alone in *no* column - the client has `Storm Sergeant Brooks` and `Alain Brooks`, never
`Brooks` - so the last word of each rendering is indexed too. `Mimio` needs the opposite,
a given name whose family name is `Mio`. Those two are the fixtures that keep the non-English
columns are required; on English alone the pass finds 10 of the 15.

**389 renderings point at more than one person** - every `<adjective> adventurer` shares
the German `adventurer` - so the pass takes a unique winner only. Just one GE name reaches
an ambiguous rendering, `Adventurer`, and it joins exactly instead, so nothing in the dump
exercises the rule; `--verify` puts a control through the same function, requiring it to
decline a rendering that resolves two ways and accept one that resolves once.

**The 7 that remain are each explained:**

- **3 `Faire Chaperone`**, one per city. The client's name row is `Faire Chaperone Judye` -
  GE documents the seasonal *role*, the client names the individual filling it. Joining a
  role to a person is the loose kind of match that produced the Storm Captain error, so
  these stay unmatched on purpose.
- **`Dryfhund` and `Wahlbert`**, whose client spellings are `dyrfhund` and `walhbert` -
  plausible but under the 0.88 ratio, and left alone for that reason.
- **`Niellefresne` and `Snobby Young Man`**, which are in no English column of the name
  table at all. `Niellefresne` does appear in the Gladiator and Lancer guild script files,
  so the client knows the name somewhere; it has no display-name row.

## One wrong join, and the right answer behind it

GE sometimes titles a page with a full name where the client labels the actor with the
short form: `Owyne Cosserand` against `owyne`. Allowing the last word to be dropped also
matched **`Storm Captain Roemannsyn` to the unrelated generic actor `storm captain`** - a
named person collapsed into a rank label. Requiring the short form to be a single word
stopped that, but it was still the wrong answer twice over: **the client does carry that
NPC, spelled `storm captain roehmannsyn`**, one letter apart.

So a spelling pass now runs *before* the surname one, and it joins 7 names that were
counted as gaps: `Bizzare Blacksmith` to `bizarre blacksmith` (GE's typo),
`Debauched Daemoness` to `debauched demoness` (GE's archaism), `Faucullien`, `Kinkina`,
`Marette`, `Margerete` and the Storm Captain. It requires a **unique** winner above a
0.88 ratio, which is what stops it picking arbitrarily between two similar names.

No GE NPC is currently ambiguous that way, so no value in the dump can prove the
uniqueness rule still works - `--verify` runs a control through the same function
instead, requiring it to decline `gerard` against both `gerarde` and `gerardo` and to
accept `gerarde` alone. The wrong target is pinned as well: it is not enough that the
Storm Captain joins, it must join to the spelling and not to the generic rank.

Three names stay unmatched that a looser ratio would take - `Dryfhund`/`dyrfhund`,
`Wahlbert`/`walhbert`, `Rhuya Nelhah`/`rhaq nelhah`. All three are plausible, none is
certain, and a pass that invents joins is worse here than one that misses three.

## What this settles on the mob side

`client-mobs-without-ge-page.csv` now carries `ge_npc_page` and `ge_npc_zones`, so the
468 undocumented mob names say when GE does document them - as a person rather than a
monster. **53 do**, and they fall where the triage predicted:

| Cause | NPC-documented |
|---|---|
| `not-a-monster` | 32 |
| `mount-or-companion` | 15 |
| `ge-gap` | 2 |
| `faction-filler` | 2 |
| `named-boss-gap` | 1 |
| `placeholder` | 1 |

47 of the 53 are the two causes that mean "never a monster", which turns both from a
reading of the name into a corroborated one: the 1900 block really is friendly NPCs, and
race 1105 really is the rental chocobo roster - GE gives every one of those birds
`race = Chocobo` and a zone. `--verify` requires that share to stay inside [0.85, 1.0),
both ends on purpose: below it GE files these as people for a reason the triage has not
found, and at exactly 1.0 the test has stopped discriminating, since `bombard king` and
five others are known to sit outside.

The `placeholder` hit is worth naming: **`???` has a GE NPC page and a zone, Mor Dhona**,
so the client's placeholder display name belongs to an actor GE could actually see.
