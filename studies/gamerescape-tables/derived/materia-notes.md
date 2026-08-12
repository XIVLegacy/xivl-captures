# materia.csv decoded - how it was derived and how to read it

The 1.23b client ships `materia.csv` in `<client-data-csv>`: 66 rows, 80
bare integer columns, no field names. It is the whole of 1.0 materia - which stat
each line grants, at what magnitude per grade and rank, and which equipment it can
be melded into. `itemData.140` is its key, which is how the item tables reach it.

Generation provenance is recorded in `file-inventory.csv`. The verification
used to pin this reading resolved one hand-checked line -
`Lifethirst`, row 3, primary `HP` and second `MP`, both 5/7/8/10 at grade I -
and exited non-zero on any mismatch. The client-data input was
`<client-data-csv>`. Two artifacts come out:

| File | Shape |
|---|---|
| `materia-column-map.csv` | one row per `materia.csv` column: 69 high, 11 low |
| `materia-decoded.csv` | one row per materia line, ids and params resolved to names |

## Layout

| Columns | Field | How it was named |
|---|---|---|
| 0-3 | the four grade item ids, I to IV | resolve in `xtx_itemName` |
| 4 | primary parameter id | resolves in `xtx_text_paramName`, 15xxx namespace |
| 5-20 | 16 magnitudes for it, as 4 grades x 4 ranks | GE `materia_effect` |
| 21 | second parameter id, `-1` on single-stat lines | resolves in `paramName` |
| 22-37 | its 16 magnitudes, all 0 when 21 is `-1` | GE `materia_effect` |
| 38-41 | one icon id per grade, in the 61xxx materia range | matches `itemData.36`'s bands |
| 42-79 | 38 booleans, one per equipment category it melds into | GE `meld_slots` |

11 of the 66 lines carry a second stat. Row 0 is an all-zero placeholder with no
named items.

The grade x rank shape is what makes the magnitudes readable: each of the four
grade items covers four ranks, so `Bloodthirst` runs 10/14/17/20 at grade I and
25/29/32/35 at grade II, straight out of columns 5-8 and 9-12. A `0` marks a rank
the line does not use - `Chocobo Down` reads 1/2/3/0, so grade I has three ranks.

## The 38 booleans, and the 11 that cannot be resolved

GE's `meld_slots` lists the equipment categories each materia can go into, and its
**38 distinct tokens match the 38 boolean columns exactly**. Scoring each column
against "GE lists token X" over 256 joined items:

- **Columns 42-57** are the six armour slots then the ten arm categories and
  Shield, each at **0.9922 to 1.0000** with a clear runner-up gap.
- **Columns 58-68** are the eleven primary tools, each at **1.0000**.
- **Columns 69-79 cannot be resolved by any test.** All eleven are byte-identical
  across all 66 rows, and GE cannot separate them either because its eleven
  secondary-tool tokens always co-occur: every materia that melds into one
  secondary tool melds into all of them. They are labelled in the order the
  primary-tool columns establish - Carpenter through Fisher - which is a
  **convention, not a measurement**. The map marks them `low` with the reason in
  the `note` column.

Do not read a `low` row as weak evidence for a specific crafter. It means the
column is one of an indistinguishable group, and only the group is established.

## What GE agrees on, and where it renders badly

GE corroborates the magnitudes, but its formatting is too inconsistent to score
strictly. On the robust comparison - the set of nonzero values at an item's grade
window, across both parameters - GE agrees on **217 of 256 items, 0.8477**. Every
residual inspected is GE's rendering, not a decode error:

- Zero ranks are printed for some lines and dropped for others. The `Veil` lines
  give `+4, +5, +0, +6`; `Ironman's Will` gives `+4, +5, +6` for the same shape.
- Consecutive repeats are sometimes collapsed: `11, 11, 12, 12` prints as
  `+11, +12` on `Lifethirst Materia II`.
- Some rows print only the endpoints - `Touch of Rage Materia I` reads `+1 ... +10`
  where the client holds 1, 3, 7, 10.
- `Manathirst Materia III` includes one value from the previous grade.
- `Savage Aim` carries no numbers at all on three of its four grades. The client
  holds 1-16 for it; see the ramp section below before reading that as a stub.

Two stricter comparisons were tried first and both scored *worse* than the robust
one, which is how the inconsistency surfaced. Where the two sources differ, the
client is authoritative.

## Coverage against itemData

`itemData` marks 356 items as materia. `materia.csv` names only 260 of them in its
grade columns, and of those **256 carry the matching `itemData.140` key**.

The 96 items it never names all carry `140 = 56`, the `Chocobo Down` row. They are
24 lines x 4 grades - `Bloodbringer`, `Manabringer`, the six `Breath of <element>`
lines, `Byregot's Hammer`, `Everspike`, `Mana Martyr` and the rest - and **none of
the 96 has a GE page**, so they read as content that never shipped rather than as
a gap in the decode. Their effect is not recoverable from this table.

`Ahriman Gaze` is the one released line in that position: row 57 lists its four
items but is the only row in the table carrying no parameter at all, so `itemData`
routes it to 56. GE's `Heavy Resistance` for Ahriman Gaze is what row 56 grants,
so the value is not wrong for it, but whether that is by design or by falling
through is not decidable here.

## materiaBook.csv is the rules, not a table

`materiaBook.csv` sits beside `materia.csv` and is a **localized text table**, not
data: 52 rows x 5 language columns (ja, en, de, fr, zh), keyed 1-53 with key 50
absent. It is the in-game materia tome - a table of contents plus three chapters -
so it has no columns to map and no numeric content to score. What it is good for
is the opposite direction: it states the 1.0 materia rules that no numeric sheet
carries. Cited by row key, summarized rather than quoted:

| Rows | What the tome states |
|---|---|
| 8, 21 | materia is made from gear that has reached a full **spiritbond** |
| 17, 19 | conversion is done from the inventory and is irreversible |
| 18 | some items cannot be converted at all, spiritbond regardless |
| 20 | the item's **type and level** determine the resulting materia, and the same item can yield different results |
| 22 | spiritbond progress is shown on a gauge on the item |
| 23 | it accrues from battling, crafting or gathering while equipped, and stalls if the item's optimal rank is above yours or its **Condition** hits zero |
| 24 | trading or selling the item dissolves the bond |
| 25, 30-32 | melding needs a **catalyst**, gatherable only with `Fingerprints of the Gods` active; the gathering point and its grade decide which one |
| 40 | the catalyst is consumed by the meld |
| 41 | catalysts and materia are not universally compatible, and a materia only fits certain equipment |
| 42-43 | melding requires a Disciple of the Hand meeting the class and level to **craft the host item** |
| 47-48 | a second and further materia need the `Augmented Materia Melder`, and each additional one lowers the success chance |
| 49 | a failed meld destroys everything involved except the melder |
| 51-52 | Mutamix Bubblypots purges for gil, strips **all** materia, and they are lost - but see the next section, where his own dialogue never mentions a fee |

Three of those rows name a key item by id rather than by text, and they resolve in
`xtx_itemName.csv`: **2001001** `Materia Assimilator` (row 53, from the quest
"Forging the Spirit"), **2001002** `Materia Melder` (row 46) and **2001003**
`Augmented Materia Melder` (row 47).

Two things it settles for the column map. The colour macro in rows 46, 47 and 53
switches on `itemData.41`, which independently confirms that column as the rarity
tier - see `client-column-map-notes.md`. And row 42's rule, that the meld gate is
the host item's crafting requirement, is the client's own statement of what
`itemData.64` / `itemData.67` are for; the map names those from GE as
`repair_class` and `repair_level`, and the tome says the same pair gates melding.

25 of the 52 rows carry no mechanics: 15 chapter and section headings, 8 menu
strings (2, 6, 9, 16, 26, 29, 34, 39), row 1's flavour line, and row 7, the string
shown when the reader lacks the prerequisite to understand the tome. The other 27
are the rules above plus the inventory steps in rows 33, 44 and 45.

## populaceShopMateriaRemover.csv, and where it contradicts the tome

The third materia file is Mutamix's shop dialogue, the same shape as the tome:
25 rows x 5 language columns, keys 1-29 with 11, 12, 13 and 26 absent. It runs two
services and a lore branch:

| Rows | Branch |
|---|---|
| 1-7, 16-18, 29 | purge a chosen item of its materia, with a confirm prompt |
| 8-10, 28 | exchange one item for another, both supplied at runtime |
| 14-15, 19-23 | Mutamix's account of materia, gated on the player's melding experience |
| 24-25 | the meld success rules |

Rows 16 and 17 are the same string in four of the five languages and differ only
in Chinese, so the two purge entry points share English text.

**Row 24 states a rule the tome does not: the first meld never fails.** The tome
(`materiaBook.csv` row 48) says only that the chance falls with each additional
materia; Mutamix says outright that attaching the first always succeeds and the
penalty applies from the second onward. Row 25 repeats the tome's row 49 - a
failure destroys everything but the melder.

**The gil fee is not corroborated here.** The tome's row 51 says to pay Mutamix
"the requisite fee in gil", but the word gil does not appear in any of this file's
five language columns, and no row displays an amount. That is not merely an
omission in a dialogue-only table: `populaceItemRepairer.csv` row 6 quotes a repair
cost as a runtime gil figure in exactly this position, so a service that charges
gil does say so here. Neither `populaceShop*` table has a numeric column at all -
both are 6 columns of `str` - so the amount itself was never going to be in this
layer, but the purge flow does not so much as mention a cost. The tome is the only
source for the fee.

Row 23 is the tome's row 47 sentence with the item parameterized: where the tome
hard-codes `2001003`, the shop passes it at runtime. Row 22 is the same point in
Mutamix's own register - one materia per item normally, more with the special
tool.

## populaceGuildShop.csv corroborates 56 of the 66 lines

The guild-mark shop dialogue - 129 rows x 5 languages, keys 1-130 with 83 absent -
carries a hardcoded materia menu at rows 93-110: eighteen entries, each naming
three or four materia lines by name, 56 names in total. **All 56 match a
`materia.csv` line exactly**, which is an external check on the decode's line
names that does not come from GE.

Ten lines are not on that menu. One is row 0, the all-zero placeholder with no
named items. The other nine:

| Row | Line | Why it is absent |
|---|---|---|
| 32 | Savage Aim | not explained by anything found here |
| 57 | Ahriman Gaze | the no-parameter row; no GE page either |
| 82-88 | Sanguinary Might, Stellar Might, Sound of Serenity, Sound of Certainty, Sound of Suffering, Swiftwall, Evenflow | the highest and only contiguous id block in the table |

**These are not unreleased content.** Eight of the nine have complete four-grade GE
pages (Ahriman Gaze is the exception, as already recorded above), against 0.9825
GE coverage for the lines that *are* sold. Since 82-88 are the table's highest ids
and the only contiguous run above 68, the likeliest reading is that the menu is a
fixed eighteen-row list that was never extended when those seven lines were added -
but that is inference from the id layout, not something the file states.

### The 1-to-16 ramp is real tuning, not placeholder data

Five lines carry primary magnitudes of exactly `1 2 3 ... 16` - Savage Aim,
Sanguinary Might, Stellar Might, Sound of Suffering and Evenflow - and all five are
in the unsold nine, which makes them look like untuned stubs. They are not. GE
confirms the values: Sanguinary Might reads `Critical Attack Power +1, +2, +3, +4`
at grade I and `+13` at grade IV, which is the ramp split 4 grades x 4 ranks, and
Stellar Might, Sound of Suffering and Evenflow agree the same way at their grade
endpoints. The ramp is simply what 1-per-rank tuning looks like on the
small-magnitude stats these lines grant (Critical Hit Rating, Critical Attack
Power, Magic Critical Potency, Enfeebling Potency, Store TP).

Do not read a linear magnitude run in `materia-decoded.csv` as a decode fault or as
unfinished data.

### What else is in the file

Not materia, recorded so the file does not have to be re-read: guild marks buy
class actions, traits and abilities (through `xtx/command`) as well as treatises,
and rows 81-88 make all of those refundable - with the refund paid in the current
guild's marks regardless of where the purchase was made (row 87). Marks also
exchange for crystals and for gil (rows 111-113), and rows 121-130 hand over an
item to undo the attribute-point allotment of the current class. Rows 25-78 are
three description rows for each of the eighteen guilds, but the greetings at 7-23
cover only seventeen: the Culinarians' Guild has none, and row 24 is a generic
fallback. Row 1 is a shipped debug string.

## Evidence gaps

- The eleven secondary-tool columns (see above). A decomp of the meld UI would
  settle them; nothing in the shipped data can.
- The magnitudes are corroborated per item only where GE documents the item. The
  24 unreleased lines have no external check of any kind. The line *names* have a
  second, non-GE check for the 56 the guild-shop menu lists.
- `materia.csv` carries no meld success rate and no retention rate, and neither
  text gives a number. Between them they bound the curve only qualitatively: the
  first meld is certain (remover row 24) and each one after it is less likely
  (tome row 48). No source here gives the per-slot chance.
- The purge fee is asserted by the tome and absent from the NPC's dialogue, so its
  amount is unknown and even its existence rests on one source.
- The catalyst is **not** in `materia.csv`; it is on the item, in `itemData.65`,
  which holds an `-ized Matter` id on materia rows and a `Dark Matter` repair
  grade on gear. GE's `materia_catalyst` is mapped there.
