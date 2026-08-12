# Client item-column map - how it was derived and how to read it

`client-column-map.csv` names the bare-integer columns of the item tables in
`<client-data-csv>`. The 1.23b client dumps ship a header row
of indices and a type row, and no field names. Gamer Escape's 1.0 item pages do
carry field names for the same items, so joining GE item -> client item id ->
client row and scoring every (column, GE field) pair recovers the names from the
outside in.

Generation provenance is recorded in `file-inventory.csv`. The verification
used to pin this reading resolved 11 hand-checked values over
three items through the emitted map, each fetched from whichever column it names,
exiting non-zero on any mismatch:

- **Alesone's Songbow** - damage 95, delay 4.1, 1 attack, level 50, projectile
  100, accuracy -20, resale 7854. Covers the ordinary numeric columns.
- **Storm Sergeant's Hoplon** - `Set bonus: HP` 100 and worn
  `Healing Magic Potency` 5. Fails if 73/74 is folded back into `param:*`.
- **Bronze Buckler** - `HQ bonus: Evasion` 1 and worn `Evasion` 4. Fails if
  77/78 is folded back in, and reproduces the conflation exactly: worn Evasion
  then reads 1.

`--client-dir` points at `<client-data-csv>`. Nothing here promotes to a
downstream implementation; this is a decode aid for reading the client sheets.

## The item stat block is spread over six tables

All six are keyed by the same item id, and `xtx_itemName.csv` maps that id to the
localized names. There is no single "weapon row" holding an item's stats.

| Table | Rows | Carries |
|---|---|---|
| `_item.csv` | 8,403 | item class path, stack size, unique, untradeable |
| `itemData.csv` | 8,403 | durability, resale, level, category, repair, recast/duration |
| `equipment.csv` | 4,875 | every stat bonus as id/value slots, plus equip slot and race/gender restriction |
| `weapon.csv` | 1,161 | damage, delay, attack count, damage-type weight, and the crafter/gatherer tool base stats |
| `armor.csv` | 3,599 | defense (its other columns are dead) |
| `accessory.csv` | 278 | nothing live in 1.23b |

`equipment.csv` is not gear-only and `weapon.csv` is not weapon-only: the first
holds consumables (their on-use effects sit in the same bonus slots), and of the
second's 1,161 rows only 616 are weapons - 267 are crafting and gathering tools,
85 are shields and 278 are accessories, all with `damage` 0.

### The six tables share one column space

They are not six schemas. **Every populated column index is owned by exactly one
table**, so a column number alone identifies a field - `116` is armor's defense
and appears nowhere else, `140` is itemData's, `141` is weapon's. Checked across
all 15 table pairs: zero overlap.

| Table | Header | Populated indices |
|---|---|---|
| `_item` | 0..3 | 0-3 |
| `itemData` | 0..140 | 33-68 scattered, plus 140 |
| `equipment` | 0..139 | 69-90, 137-139 |
| `weapon` | 0..141 | 92-111, 135, 136, 141 |
| `armor` | 0..128 | 116-128 |
| `accessory` | 0..130 | 129, 130 |

Each header runs 0..N-1 up to that table's last owned field, which is why the
widths differ and why the low columns of the wide tables are empty. The 50
indices no table populates (4-32, 34, 37-39, 49, 51-52, 54-55, 57-58, 60, 91,
112-115, 131-134) are fields nothing in 1.23b fills.

Row membership works by item kind and nests rather than partitioning: all 278
accessories have a row in `weapon.csv` and `armor.csv` too. Do not read a row's
presence in a table as evidence of what the item is - read `equipment.69`.

### The accessory table contributes nothing

`accessory.csv` owns exactly two fields in that space, `129` and `130`, both u8
and both **0 on all 278 rows**. There is no accessory-specific data in 1.23b at
all: an accessory's stats come from `equipment.csv`'s bonus slots like everything
else, its defense from `armor.116` (nonzero on 159 of the 278), and its
durability and price from `itemData`.

Its 278 rows are exactly the accessories - `equipment.69` 45 wrists (64), 47 ears
(65), 17 neck (68) and 49 ring (81) - so the row set is the one useful thing the
table carries. What those rows hold in `weapon.csv` is filler and should not be
read as data: one attack, blunt damage type at weight 1.0, damage 0 and delay 0.

## Columns named from GE

Match rate is exact agreement over the rows where both sides carry a value.

| Column | Field | Confidence | Agreement |
|---|---|---|---|
| `itemData.47` | `optimal_level` | high | 1867/1870 |
| `itemData.40` | `item_category` | high | 5555/5606 |
| `itemData.33` | `wear_durability_points` | high | 2865/2898 |
| `itemData.65` | `required_matter_item` | high | 254/256 |
| `itemData.61` | `recast_seconds` | high | 300/305 |
| `itemData.59` | `duration_seconds` | high | 276/280 |
| `itemData.35` | `resale_price_gil` | high | 3437/3915 |
| `itemData.67` | `repair_level` | high | 690/829 |
| `itemData.64` | `repair_class` | medium | 2809/2874 |
| `weapon.136` | `delay_seconds` | high | 488/493 |
| `weapon.135` | `damage` | high | 487/493 |
| `weapon.98` | `number_of_attacks` | high | 617/617 |
| `_item.1` | `stack_max` | high | 1874/1904 |
| `_item.2` | `unique` | high | 5589/5607 |
| `_item.3` | `untradeable` | high | 5583/5607 |
| `armor.116` | `defense` | medium | 2051/2093 |
| `equipment.138` | `meldable` | high | 2722/2731 |

Confidence bands: **high** = >=98% agreement over >=25 rows with >=4 distinct GE
values, a runaway winner over a large sample (`numeric-dominant`), or a
two-valued column that beats the GE majority baseline (`numeric-skew-lift`, see
below). **medium** = >=90%, or near-perfect agreement on a low-variance column
that does not beat that baseline (`numeric-low-variance`).
**low** = >=75%. The `evidence` column records which rule fired and
`runner_up` the next-best field, so a weak call can be re-judged.
**client-named** and **client-named-offset** rows are not GE calls at all - they
are named from the client's own parameter table, and on those a GE agreement is
recorded from 3 rows up (`numeric-thin`), since it is corroborating a name rather
than supplying one.

`itemData.35` and `itemData.67` sit at 88% and 83%: the residual is GE's own
error, not ambiguity. Nothing else comes within 3x of either, and GE's resale
prices are editor-entered and go stale.

### The four boolean columns, and why they were capped too low

`_item.2`, `_item.3`, `weapon.98` and `equipment.138` carry two values each, so
they failed the >=4-distinct test for **high** and were reported at **medium** on
their match rate alone. The stated worry was that agreeing with a lopsided GE
flag is nearly free. Measuring that worry rather than assuming it settles all
four: score each against the best a constant predictor of the GE field could do,

    lift = (rate - base) / (1 - base)

where `base` is the majority share of the GE values compared. 1.0 is perfect,
0.0 is no better than always guessing GE's majority.

| Column | Field | Rate | GE base | Lift |
|---|---|---|---|---|
| `weapon.98` | `number_of_attacks` | 1.0000 | 0.9076 | 1.0000 |
| `equipment.138` | `meldable` | 0.9967 | 0.7327 | 0.9877 |
| `_item.2` | `unique` | 0.9968 | 0.8398 | 0.9800 |
| `_item.3` | `untradeable` | 0.9957 | 0.8384 | 0.9735 |

All four are now **high**. `number_of_attacks` was the column the medium cap was
written around, and it is the clearest case against it: 617 of 617 exact, so even
against a 0.9076 baseline it leaves no residual to explain.

Only these four pairs reach the low-variance path at all, and none is excluded by
the lift, so the guard currently filters nothing - the >=99.5% rate the path
already demanded was doing the work, and the cap was simply too conservative. It
is kept because it is what makes the promotion auditable: the baseline is emitted
next to the rate in the `note`, so no reader has to take the rate on trust, and a
later client-data revision could put a 99.5% rate against a 99% skew.

`equipment.138` earns its call twice over, because it is specifically `meldable`
and not a generic is-this-gear flag: against GE's `convertible` the same column
scores a lift of **-0.03**, i.e. worse than guessing.

The nine items where `equipment.138` and GE disagree all carry the same value in
GE's `meldable` and `convertible` - `Leather Eyepatch`, `Goblin Gladius`, three
dyed `Dated Hempen Dalmatica`, `Sentinel's Plate Belt` and two more. GE keeps the
two fields apart on 1,354 other rows, so these read as per-page authoring slips.

### Where GE splits a distinction the client does not

`itemData.47` is one level column. GE's `required_level` (99.4%),
`optimal_level` (99.8%) and `required_rank` (91.5%) all track it, so those three
wiki fields are one client value - and the client says why they collapse:
`populaceShopSalesman.csv` row 226 explains that being under an item's optimal
level does not usually stop you equipping it, it just reduces the stats in
proportion to the gap. One number serves as requirement, optimum and rank.

`itemData.48` is the other case, but it belongs here only halfway: it does carry
all three of GE's class fields, and it **does** make the distinction between them
- see the affinity section below. The earlier claim that it conflated
`requires_classes` and `favors_classes` was wrong.

## Bonus stats are slot-encoded, not columns

`equipment.csv` does not reserve a column per stat. It holds ten adjacent
(id, value) pairs - columns 71/72 through 89/90 - where the id selects the stat
and -1 marks an empty slot. The ten pairs are **not** interchangeable; the first
four are dedicated, and only 79/80 onward is the generic worn-stat run. See "The
first four pairs are dedicated" below. `client-column-map.csv` expands each id into a
virtual `param:<id>` row, and those rows are named from the client's own
`xtx_text_paramName.csv`, so they are **primary** evidence rather than a GE
inference. **141 distinct ids are in use**, across five namespaces:

- **15xxx** - flat stat bonuses on equipped gear (Accuracy, Attack Power,
  Strength, Piety, Craftsmanship, elemental resistances, Enmity, Parry).
- **1015xxx** - the same stat ids offset by 1,000,000, carrying **consumable
  on-use effects** rather than equipped bonuses. See below.
- **16xxx** - conditional and set bonuses: grand-company gear-count bonuses
  (Storm/Serpent/Flame), `Sanction`, `HP 75% or lower: ...`.
- **1016xxx** - two ids only, on potions and ethers: percent of max HP / MP
  restored. See below.
- **20xxx** - special effects: proc chances, equip restrictions
  (`Cannot equip gear to head`), and job-action modifiers (`Enhances Ballads`,
  `Reduces Jump recast`).

| Band | Ids in use | Named by |
|---|---|---|
| 15xxx | 62 | `paramName` directly |
| 20xxx | 48 | `paramName` directly |
| 1015xxx | 23 | `paramName` after removing the offset |
| 16xxx | 6 | `paramName` directly |
| 1016xxx | 2 | `paramName` after removing the offset |

That is 116 named straight from `paramName` and 25 through the offset, which is
where the map's two `client-named` confidence values come from.

The HQ and set-bonus slots draw on the *same* vocabulary rather than a private
one: all 37 `hqparam` ids and all 25 `condparam` ids also appear as worn params
elsewhere, so the union stays 141. That is the mechanism behind the two
conflations documented below - identical ids, different meaning by slot - and the
reason separating them by slot rather than by id was the only fix available.

### 1015xxx: what the offset band is carried on

23 ids in use over **268 distinct items, and `_item.0`'s class enum partitions
them exactly**:

| Class | Items | `use_effect_kind` | Carries |
|---|---|---|---|
| `Normal/FoodItem` | 243 | 1 | the EXP bonus in slot `75/76`, stat bonuses in `79`-`84` |
| `Normal/EnchantMedicineItem` | 21 | 2 | one stat bonus each (`Hi-potion of Strength`) |
| `Normal/CmnGoodStatusItem` | 4 | 1 | the company-issue manuals, EXP 50 |

Every one of the 268 carries a duration, and none is gear - the "consumable
on-use effect" reading of the offset holds without exception here.

Note where they sit: the EXP bonus is the only offset effect in the dedicated
`75/76` slot (243 rows), while every other consumable effect sits in the worn run
at `79`, `81` or `83`. So `75/76` is not the consumable slot in general; food's
EXP bonus is simply the one effect that uses it.

**A correction this turned up:** the map read `itemData.63` as timed-versus-instant
and that does not survive contact with the duration column. 22 of the 269 kind-1
rows carry no duration and 40 of the 73 kind-2 rows do, so duration does not track
it. What does track it is the item class - kind 1 is 243/269 food, kind 2 is
54/73 medicines and potions - so it reads as the **buff family**, which is also
what FFXIV's separate food and medicine buff slots would need. The class overlap
is not perfect (`CmnGoodStatusItem` appears under both), so the column is now
medium rather than high.

### 1016xxx: two ids, one item class, and the cleanest evidence in the band

The offset form of the 16xxx band mirrors only **2 of its 10 ids**, `1016001` and
`1016002`. They sit on 22 items, every one of them `Normal/PotionItem`, and each
carrier holds **nothing but its restore id** - unlike food, which stacks an EXP
bonus and stat bonuses in the same run. `Elixir` and `Onyx Tears` carry both.

The percent reading is on firmer ground here than the notes previously showed,
and on client data alone rather than GE's wording. Within each ladder the resale
price rises while the stored value falls:

| Item | Value | Level | Resale |
|---|---|---|---|
| Potion | 40 | 8 | 56 |
| Hi-potion | 30 | 24 | 156 |
| Mega-potion | 20 | 44 | 281 |
| Ether | 40 | 15 | 100 |
| Hi-ether | 30 | 35 | 225 |
| Mega-ether | 20 | 50 | 319 |

A flat reading requires `Mega-potion` - five times the price, 36 levels later - to
restore half of what `Potion` restores. No progression item is priced that way. A
percentage of a level-scaled pool is the only reading where the expensive item is
the better one. `Elixir` closes it: highest level, highest price and the top value
at 50.

**Restored on use, not over time** - worth stating because the base name says
otherwise. The ids resolve to `16001` / `16002`, which `paramName` calls
`HP Regen` / `MP Regen`, but all 24 carrier rows are `use_effect_kind` 2 with
`duration_seconds` 0 - the only offset carriers in the whole band with no
duration. Read the base name as the client's label for the HP-restoration
parameter, not as a regen-over-time effect. GE's descriptions corroborate the
direction independently, running "restores a few HP" for `Potion` to "restores a
large amount of HP" for `Mega-potion` while the stored number goes down.

Worth being explicit about why this claim survives while the 1015xxx one did not.
The test that retracted percent for the stat ids compares an offset id's
magnitudes against the flat bonus for the same parameter - and **that test cannot
be run here**, because `16001` and `16002` are two of the three ids with no flat
use at all. There is no flat counterpart to compare against, so the ladder is the
only available evidence. It is good evidence, but it is a different kind of
evidence, and the two families should not be treated as one result.

### 15xxx: 105 stat ids defined, 62 granted by any 1.23b item

This is the band the map scores against GE, and it is less than two-thirds
occupied:

| | Ids |
|---|---|
| in use on at least one item | 62 |
| named but granted by nothing | 24 |
| reserved and unnamed (`[@1F][@1F]`) | 19 |

Of the 62 in use, **GE corroborates 21 and the other 41 are client-only** - no
wiki field covers them, so for those the client sheet is the whole of the
evidence.

The 24 named-but-unused ids are the informative half, because they are mechanics
the 1.23b client had vocabulary for and shipped on no item:

- **A complete damage-type resistance family, entirely unused**: `15066`-`15069`
  Slashing / Piercing / Blunt / Projectile Resistance - mirroring the four
  `weapon.106` damage types exactly - plus `15070`-`15073` Sonic, Breath,
  Physical and Magic Resistance.
- **Status resistance shipped by halves**: Paralysis, Silence, Blind, Poison,
  Stun, Sleep and Heavy are used (1-5 items each); Slow, Petrification, Bind and
  Doom are defined and unused.
- **`15059 Damage` and `15060 Delay` are never used as bonus ids**, because the
  client stores both as dedicated columns (`weapon.135` / `weapon.136`) instead.
  The slot vocabulary and the fixed columns are alternative encodings of the same
  two stats, and 1.23b uses only the columns.
- The remainder: `15003 TP`, `15039 Magic Critical Hit Resilience`,
  `15053 Spikes`, `15054 Haste`, `15057 Reduced Durability Loss`,
  `15061 Fastcast`, `15062 Movement Speed`, `15063 EXP`, `15064 Resting HP`,
  `15065 Resting MP`. Note `15057` sits beside `15058 Increased Spiritbond Gain`
  and `15105 HQ Discovery Rate`, which *are* used - the durability-loss stat is
  the odd one out of that trio.

**Three ids exist only in consumable form.** `15063 EXP`, `16001 HP Regen` and
`16002 MP Regen` are unused as flat ids while `1015063`, `1016001` and `1016002`
are used, and they are the only three of the 25 offset ids in use whose flat base
is idle. So the offset band is not a mirror of the flat band: 22 of 25 offset ids
have a live flat twin, and exactly three describe an effect no item grants when
worn.

**15xxx and the low-id namespace share vocabulary but no arithmetic.** 21 of the
62 in-use ids have a low-id twin by name (`15001 HP` / `110 HP`,
`15004 Strength` / `1 Strength`), and the remaining 41 have no low-id counterpart
at all - 15xxx is the denser list. There is no offset or ordering that converts
between them: `15001`/`15002`/`15003` map to `110`/`120`/`130` on a tens grid
while `15004`-`15009` map to `1`-`6`. Do not try to derive one id from the other.
The elemental resistances show the same asymmetry from the other side: 15xxx has
six (`15010`-`15015`, all used), where the low band has one grouped
`650 Elemental Resistances`.

### 16xxx and 20xxx: conditional bonuses and flag effects

These two bands behave nothing like the 15xxx stats, and the difference is worth
knowing before reading a `param:16xxx` or `param:20xxx` row.

**16xxx - 10 ids defined, 6 in use, and the value is a real magnitude.** Two
sub-families that do not share a slot:

| Ids | In use | Where | Value |
|---|---|---|---|
| 16001-16006 conditional bonuses | 2 of 6 | the worn run (81, 85, 87, 89) | the bonus amount: 60, 50, 30, 20 |
| 16007-16010 set membership | 4 of 4 | only `71/72` | the piece threshold |

So a conditional bonus is not confined to `71/72`. Only the *set-membership*
conditions live there; `16004 HP 75% or lower: Increases critical hit attack
power` and `16006 ... potency of critical hits` sit in the worn run alongside
ordinary stats, carrying their magnitude.

Four 16xxx ids are defined and unused, and one pair of them is the interesting
case: **`16001 HP Regen` and `16002 MP Regen` are never used as flat ids, while
their +1,000,000 forms are used on 24 consumables.** A 1.23b item can restore HP
on use; no 1.23b item grants HP regeneration as a worn stat. The other two unused
ids, `16003` and `16005`, are the crit-rating and magic-crit-rating members of the
"HP 75% or lower" family - the client defined four and shipped two.

**20xxx - 57 ids defined, 48 in use, and every value is 0.** Not one of the 112
carrier rows holds anything but zero, so these are pure flags: the id *is* the
effect and the value column is inert. They partition by slot exactly, with no id
appearing in both:

| Ids | Rows | Slot | What they are |
|---|---|---|---|
| 20001-20028 | 77 | always `75/76` | item-intrinsic: proc chances, level-banded bonuses, the `Cannot equip gear to X` restrictions |
| 20029-20057 | 35 | always `79/80` | job-action modifiers |

The job-action family is the relic set, and it cross-validates `rarity_tier`
independently. Each of `20029`-`20056` is on **exactly one item**, and those 28
items are the 7 finished relics (rarity tier 4) plus 21 artifact pieces (tier 3):
`Curtana` carries `20050 Increases Spirits Within damage`, `Artemis Bow` carries
`20054 Increases song duration`, `Choral Shirt` carries `20038 Enhances Ballads`.
`Holy Shield` is the only tier-4 item with no job-action effect, which fits - it
is a shield. And `20057 Inhibits main arm spiritbond` is carried by exactly the
seven **Unfinished** relics and nothing else.

The 9 unused 20xxx ids are evidence in their own right: the client ships names for
a complete elemental proc set (`earth`, `lightning`, `water` damage) of which only
fire, ice and wind were used, plus an entire absorb-and-convert family -
`Chance to absorb HP / MP / TP`, `Converts damage to MP / TP` - and
`Chance to inflict Increased Enmity`. Those nine ids were named in the 1.23b
client and put on no item.

### The low-id half of paramName is a name table nothing points at

186 of `paramName`'s 358 rows sit below 15000, in three bands that are not stat
slots at all:

| Ids | Count | What they are |
|---|---|---|
| 1-12 | 12 | the six attributes (Strength..Piety) and six elements (Fire..Water) |
| 110-820 | 99 | a tens grid of base stats - 110 HP, 120 MP, 130 TP, 200 Attack Power, 210 Critical Hit Rating, 230 Accuracy, 240 Parry, 300 Magic Potency, 310 Magic Accuracy, 400/410/420 crafting, 500/510/520 gathering, 600 Defense, 620 Evasion, 630 Resilience, 640 Magic Defense, 650 Elemental Resistances |
| 10013-10120 | 75 | **UI labels, not params** - `Physical Level`, `Race`, `Clan`, `Nameday`, `Guardian`, `Durability`, `Condition`, `Expertise`, `Repair Materials`, `DPS`, and a run that keeps its trailing colon (`HP Cost:`, `Cast Time:`, `Level Acquired:`, `Additional Effect:`, `Use:`) |

**Nothing in the client references any of them by id.** Every column of every CSV
in `<client-data-csv>` was scanned for one whose live values fall inside the
110-820 or 10013-10120 sets, keeping columns with at least 10 live values and 3
distinct ones. The only columns clearing 90% are five in `quest_new_reward.csv`
holding just three values each (300, 301, 100), which are reward-type codes and
not parameter ids at all - 100 is not even a `paramName` id. A reference thinner
than that threshold would have been missed, but no plausible id-reference column
is.

Two consequences worth recording, because both close a line of enquiry:

- The crafter and gatherer tool assignment below matches `weapon.94-102` to
  400/410/420 and 500/510/520 **by reasoning, and no reference exists to confirm
  it**. This scan is the search for that reference, and it came back empty.
- The 10013-10120 band is the client's own vocabulary for fields this map named by
  inference (`10090 Durability` for `itemData.33`, `10088 Required Level` for
  `itemData.47`, `10099 Number of Attacks` for `weapon.98`). It corroborates that
  those concepts exist in 1.23b but cannot be joined to a column, for the same
  reason: no table cites these ids.

Two details in the low band are stale client content rather than live data:
`10118 Charisma` and `10119 Luck` are attributes absent from the live 1-12
attribute list, and **98 of the 358 rows carry `[@1F][@1F]`** - two non-breaking
hyphens, the client's "--" for a reserved-but-unnamed slot. 19 of those sit in the
15xxx range (`15055`, `15056`, `15085`-`15101`) and **no 1.23b item uses one**, so
the map never has to render a placeholder as a field name. It maps them to the
empty string anyway, so a later client revision cannot leak a control code.

GE cross-checks the 15xxx slots independently and agrees at **97.1-100%** on
every one (`Accuracy` -> `accuracy_bonus`, `Piety` -> `piety_bonus`, and so on),
ten of them at exactly 100%, which confirms the slot decode end to end.

## The first four pairs are dedicated

Reading all ten pairs as one generic run is wrong, and it costs accuracy: three
of the first four carry something other than the stat the item has when worn.

| Pair | Carries | 15xxx flat ids ever seen |
|---|---|---|
| `71/72` | the condition of a conditional bonus | 0 of 255 |
| `73/74` | the stat that condition grants | all 93 |
| `75/76` | special effects and consumable on-use effects | 0 of 320 |
| `77/78` | the high-quality bonus | all 1,574 |
| `79/80` .. `89/90` | the item as worn | 9,044 of 9,378 |

`71/72` uses only **four** ids ever - the Storm, Serpent and Flame gear-count
bonuses plus `Sanction` - and its value is the piece threshold, graded 2-5. The
parameter name settles that reading on its own: `16007` is literally
`Storm gear ([@VALUE($E8(1))] or more pieces):`, a substitution slot for the very
number `72` holds. The 162 rows at 0 are the plain city gear
(`Lominsan Knuckles`, `Ul'dahn Hora`), which count toward a set without granting
a bonus themselves; `Sanction` is always 1. `75/76` never
holds a flat stat at all: 243 of its 320 rows are the `1015063` EXP bonus on
food and the other 77 are 20xxx special effects.

All four ids resolve in `xtx_text_paramName.csv`, so the reading is the client's
own and not an inference:

| Id | paramName string | Rows |
|---|---|---|
| `16007` | `Storm gear ([@VALUE($E8(1))] or more pieces): ` | 74 |
| `16008` | `Serpent gear ([@VALUE($E8(1))] or more pieces): ` | 74 |
| `16009` | `Flame gear ([@VALUE($E8(1))] or more pieces): ` | 74 |
| `16010` | `Sanction: ` | 33 |

#### What Sanction is, and where the other side of it lives

`16010` is the odd one out: three of the four conditions are "wear N pieces of a
set", which the item can answer by itself, but Sanction is a player state. The
status table says what it is - `xtx_status.csv` row **223992**, `Sanction`, whose
description reads "Receiving the gear-enhancing benefits of your Grand Company's
sanction", with a separate line for its expiry, so it is a timed buff whose whole
function is to enhance gear. That is exactly what a condition on a stat bonus needs
to be, and it is why the 33 Sanction rows carry threshold 1 rather than a piece
count.

`populaceCompanyBuffer.csv` is where a player gets it, and it names the mechanic
outright. A dedicated company official **bestows** sanction (row 5, `Have sanction
bestowed`); it is not bought. Rows 10-14 explain it:

- Sanction is "a process which involves the casting of any one of a range of
  enhancing spells on **gear specially crafted to harbor enchantments**" (row 11).
  That is `equipment.71 = 16010` from the item's side: the column is how an item
  declares itself sanction-ready, which is why its threshold is a flag at 1 rather
  than a piece count.
- The effect lasts a number of minutes supplied at runtime and "grants a bonus to
  the efficacy of certain gear" (row 13).
- Which gear qualifies "can be identified by viewing item details in the inventory
  interface" (row 14) - the purpose of the `Sanction: ` label in `paramName`.
- It is gated on company rank: Chief Storm / Serpent / Flame Sergeant or above.

**This corrects an earlier reading.** `populaceCompanyShop.csv` row 26 does offer to
exchange seals "for the effect of" a status, and that was taken here as the
purchase route for Sanction. It is not: the status id in that row is a runtime
argument, and the buffer bestows sanction for free on rank. Whatever row 26 sells,
Sanction is not established to be it.

That also explains the negative GE result recorded below: none of the 93 `73/74`
values shows up as a worn stat because every one of them is gated behind either a
set-piece count or a bestowed buff.

The same file's grand-company material was checked against the map and changes
nothing else. Its rows 118-141 enumerate six commissions - Recruit, Enlisted, Petty
Officer, Officer, Senior Officer, Marshal - and gate shop inventory by them, which
raised the question of whether GE's `required_rank` is a commission rather than the
level it is folded into. It is not: `required_rank`'s 133 values are 7 to 50 on a
1-50 scale, so the `itemData.47` mapping stands. No client column carries the
commission at all.

Those six are shop-inventory bands, not the rank ladder itself - the buffer gates on
`Chief Storm Sergeant`, which is not among them - so do not treat the six as the
full 1.x company rank list.

For the record, since nothing else in the file touches a column:
`populaceCompanyShop.csv` is 140 rows x 5 languages, keys 2-141 with no gaps, and
runs the seal counters of all three companies. The three seal currencies are not
interchangeable, seals are capped and any issued over the cap are lost (row 32),
and besides items they buy promotions, the Sanction effect, chocobo barding, and
access to a company aetherial transport network gated by an item. Rows 53-58,
73-74 and 83-84 are Foundation Day seasonal stock.

### 73/74 is the set-bonus payload, not a worn stat

All 93 items carrying `73/74` also carry `71/72`, and none appears without it, so
the pair reads as the payload of the condition beside it. GE settles it: of the
44 rows whose attribute has a GE field trusted elsewhere in this map, **GE is
silent on 42 and disagrees on the other 2. It confirms none.** Storm Sergeant's
Hoplon stores `73/74 = (HP, 100)` and `79/80 = (Healing Magic Potency, 5)`, and
GE records the 5 and no HP at all; Storm Lieutenant's Hooks stores
`(Attack Power, 30)` beside `(Accuracy, 20)`, and GE records only the 20.

That silence is the expected shape for a conditional bonus - the wiki infobox
lists what the item gives you outright - so it is evidence for the reading rather
than a coverage gap in GE.

### 77/78 is the HQ bonus

Columns 77/78 sit in the middle of the run but are a dedicated pair. 77 is
populated on exactly 1,574 items, and on every one of them the pair is the
attribute and amount that the item's **high-quality** version adds over its
normal one - not a bonus the normal item carries. Three independent things say
so:

- GE's `hq_bonus_attribute` names the same attribute on 594 of the 599 items
  where both sources have a value (99.25%), and GE gives no magnitude for any
  of them, which is what makes this pair worth naming.
- Where an item has both an HQ bonus and a normal bonus in the same attribute,
  the client stores **two** slots with the same id: Bronze Buckler reads
  `77/78 = (Evasion, 1)` and `79/80 = (Evasion, 4)`, and GE records its
  `evasion_bonus` as 4. Aeolian Scimitar carries only `(Strength, 5)` in 77/78
  and GE records its `strength_bonus` as 0 - the +5 exists only at HQ.
- mozk-tabetai.com's client-derived 1.x database (`ffxiv.mozk-tabetai.com`,
  version 1.5.4) renders each item's parameters as
  `[paramId, normalValue, ?, ?, hqValue]`. Its `hqValue` equals this pair's
  value on 1,574 of 1,574 items, and its `normalValue` matches GE's
  corresponding `*_bonus` field on 3,206 of 3,212.

One HQ pair covers all HQ grades, and 1.23b has exactly three of them. The client
renders an item's grade as a name suffix through a `SWITCH` macro with three
branches and no fourth - `[@SWITCH($E8(2),, +1, +2, +3)]` - and that macro appears
**736 times across 12 files** (`worldMaster.csv` 469, `noc000.csv` 142,
`harvestJudge.csv` 44, the shop and repair tables, `xtx__text_ui.csv`) with no
`+4` variant anywhere and only the argument slot varying. So a grade is a display
suffix on the item, not a separate row, and the single 77/78 pair is not an
omission.

The suffix is the **HQ grade and not a melded-materia count**, which
`harvestJudge.csv` settles: its row 25 "You obtain <item>" applies the same macro
to gathering yields, and gathered materials never carry materia.

### Keeping the three apart, and what that proves

Each dedicated pair expands into its own virtual namespace, so a `param:` row is
always the item as worn:

| Namespace | From | Rows | Carriers |
|---|---|---|---|
| `param:<id>` | the worn run, plus 16xxx/20xxx/1015xxx ids wherever they sit | 116 | - |
| `hqparam:<id>` | `77/78` | 37 | 1,574 |
| `condparam:<id>` | `73/74` | 25 | 93 |

Separating them is itself evidence, and for the HQ pair it is the strongest
piece. Scoring the 15xxx `param:` rows against GE's worn-stat fields, read
straight off the emitted map:

| Configuration | Agreement | Params at exactly 1.0000 |
|---|---|---|
| both pairs fed into `param:` | 0.9094 (4,716/5,186) | 1 of 21 |
| only `73/74` fed in | 0.9958 (5,162/5,184) | 9 of 21 |
| both split out | **0.9961 (5,164/5,184)** | **11 of 21** |

Nearly all of the 9% error was HQ deltas being compared against worn values,
which is only true if 77/78 is the HQ pair.

One more confirmation, and it needs no GE data at all. **1,539 items carry the
same parameter id in two different slots, and every single case involves one of
the two dedicated pairs**: 1,536 pair slot `77` with a worn slot and 3 pair slot
`73` with one. Not one duplication is between two worn slots.

| Slots | Items |
|---|---|
| 77 + 79 | 547 |
| 77 + 81 | 534 |
| 77 + 83 | 446 |
| 77 + 85 | 9 |
| 73 + 79 | 3 |

The worn run therefore never repeats a stat - each of its six slots holds a
distinct parameter - and the only way a parameter appears twice on one item is as
an HQ bonus or a set-bonus payload. If `77` or `73` were generic slots there would
be no reason for repeats to concentrate on them, and `Bronze Buckler` carrying
Evasion at both `77` (1) and `79` (4) would be an unexplained collision rather
than the normal case.

The set-bonus split moves the total barely at all - GE omits those values rather
than contradicting them - but it is what takes `HP` and `Magic Accuracy` to
exactness. Each had exactly one disagreeing row out of 530 and 138, and in both
cases that row came from `73/74`.

### The +1,000,000 offset family

25 ids sit at a known stat id plus 1,000,000, with no `paramName` row of their
own. What they are is settled; what their numbers mean is not.

Established, and computed into the map's `note` column:

- **Consumables only.** 290 items carry an offset slot. Zero of them appear in
  `weapon.csv`, `armor.csv` or `accessory.csv`. By GE category they are food
  (`Freshwater Fare`, `Sweet`, `Meat Dish`, `Soup & Stew`, ...), `Panacea` and
  `Potion` - no gear of any kind.
- **Never both forms.** Across 534 offset-slot rows, not one item also carries
  the flat id for the same stat. The two forms are alternatives, not a
  base-plus-bonus pair.
- **Duration separates them cleanly.** 268 of 290 offset-slot items have a
  nonzero `itemData.59` duration, against 10 of 3,646 flat-slot items. The 22
  zero-duration exceptions are the instant potions. Food applies status 223999
  `Well Fed` (`xtx_status.csv`).

So the offset marks *an effect granted by consuming the item*, and the base stat
identity is sound: id minus 1,000,000 lands on a real stat in every case.

**The magnitudes are percentages for `param:1016001` and `param:1016002`** -
percent of max HP and MP restored on use. The evidence is the potion and ether
ladders, set out under "1016xxx" above rather than repeated here.

**The percent reading does not extend to the 1015xxx stat ids, and an earlier
version of this note wrongly said it did.** It is established for exactly three
of the 25 offset ids, in each case because a flat reading is impossible:

- `1016001` / `1016002` - the potion and ether ladders, above.
- `1015063` EXP - 3 on 243 food items and **50 on four**, the four being
  `Company-issue Survival Manual` and `Engineering Manual` I and II. A +50%
  EXP manual is a known 1.0 item; a +50 flat EXP manual would be pointless.

For the other 22 the evidence runs the other way. Comparing each offset id's
median value against the median of the *flat* bonus for the same parameter on
gear, the two sit in the same numeric range - the offset median is 1.2x to 2.2x
the flat median on 20 of 22 params, and lower on the remaining two:

| Param | Flat median on gear | Offset median | Ratio |
|---|---|---|---|
| Strength | 3 (n=351) | 6 (n=10) | 2.0x |
| Accuracy | 5 (n=297) | 11 (n=19) | 2.2x |
| Attack Magic Potency | 6 (n=178) | 10 (n=23) | 1.7x |
| Craftsmanship | 10 (n=492) | 16 (n=7) | 1.6x |
| HP | 19 (n=674) | 6.5 (n=10) | 0.34x |
| MP | 20 (n=520) | 7.5 (n=6) | 0.38x |

If food granted percentages while gear granted flat points, those two ranges
would not coincide - a percent and a stat point are different units and would not
land within a factor of two of each other across twenty parameters. So the stat
ids read as **flat amounts in the same unit as the gear bonus**, and the map now
says the unit is not established rather than asserting percent. HP and MP are the
two that sit below their flat counterparts and so are the two worth a second look,
but 3x is not the separation a unit change would produce either.

Per-id magnitudes are uncorroborated one at a time regardless - GE records no
numeric bonus for any of the 290 carriers - so treat an individual food's number
as CALIBRATION-grade.

`weapon.csv` uses the same shape for damage type at columns 106/107, with its own
tiny id namespace and a 0-1 float weight where GE reports a percent:

| Id | `weapon.csv` rows | Rows with damage > 0 | GE field |
|---|---|---|---|
| 1 | 199 | 135 | `slashing_attack_pct` |
| 2 | 84 | 59 | `piercing_attack_pct` |
| 3 | 753 | 200 | `blunt_attack_pct` |
| 4 | 125 | 100 | `projectile_attack_pct` |

**Read the third column, not the second.** `weapon.csv` is not weapons-only, so a
damage type is stamped on plenty of rows that do no damage - 667 of its 1,161 rows
carry damage 0. **Blunt is the filler value**: of its 753 rows, 85 are shields, 184
are crafting and gathering tools and 278 are accessories, and all 547 of those
carry damage 0, leaving 206 real one- and two-handed weapons of which 200 do
damage.

Every row fills exactly one damage-type slot, so the second and third pairs
(108/109, 110/111) are always empty. And the weight is **1.0 on all 1,161 rows**,
matching GE's `100` on every one of the 655 items that carry a percent: no 1.23b
weapon splits its damage across types. The percent is a constant in both sources,
not a distribution.

## Only equipment has a live slot run

Auditing the other five tables the same way turned up no worn/variant
conflation, because there is nothing there to conflate: their stats sit in fixed
columns and what slot runs they have are empty.

| Table | Slot run | State |
|---|---|---|
| `equipment` | 71/72 .. 89/90 - bonus | all ten live; see above |
| `weapon` | 106/107, 108/109, 110/111 - damage type | slot 1 only; 2 and 3 are `-1` on all 1,161 rows |
| `armor` | 121/122 .. 127/128 - bonus | **all four `-1` on all 3,599 rows** |
| `accessory` | none | 2 populated columns, both constant |
| `itemData` | none | one `-1` column, `63`, and it is a standalone kind flag |
| `_item` | none | 4 columns, all named |

`itemData` is the one that could have hidden a run, since it is 142 columns wide
and holds the consumable block. It does not: `63` is the only `-1`-sentinel
column, and its payload is not an adjacent value but the fixed columns `59`
(duration), `61` (recast) and the `50`/`53` float pair. `61` and `43` are exactly
co-extensive with it over all 343 consumables. The columns physically adjacent to
`63` are `64` and `65`, which are repair class and materia catalyst - unrelated to
it and already named.

Armor therefore ships its own four-slot bonus run and never uses it; equipment
serves armor bonuses instead. `find_slot_pairs` cannot see either run - it needs
one id that is not -1 - so both are declared in `EMPTY_SLOT_RUNS` and reported as
unused slots rather than as dead scalars.

The three columns where GE does disagree are GE being wrong, not a variant
column. `weapon.135` (damage) disagrees on 6 of 493, `weapon.136` (delay) on 5 of
493 and `armor.116` (defense) on 42 of 2,080, and in each case the client is
higher on some rows and lower on others with no consistent delta - the opposite
of the fixed-direction pattern an HQ or conditional value produces. The armor
residual is also smaller than it looks: those 42 rows are 22 distinct wiki pages,
since colour variants share one page and inherit its error (all five
`Dated Cotton Shepherd's Tunic` colours read 123 against the client's 23).

## Dead in 1.23b

18 columns hold one value across every row and carry no information:
`armor.117-120`, both `accessory.129-130`, `itemData.42/45/56/62/68` and
`weapon.92/93/99/100/103/104/105`. The `note` column records the constant value.
The twelve unused slot columns above are excluded - they are empty slots rather
than dead fields.

## Columns named from client structure, not from GE

30 columns are named from the client rather than from a GE field. Most are ones GE
cannot reach - it records no numbers for the items involved, or the concept is
client-internal - and each was resolved by cross-tabbing against `_item.0`'s class
enum, `equipment.69`'s kind enum, or the item populations themselves. Two,
`itemData.48` and `itemData.65`, are ones GE *does* reach but under a name too
narrow for what the column holds. Full enumerations are in the map's `note` column.

The six dedicated slot-pair columns (`equipment.71`-`74`, `77`, `78`) are in that
count and have their own sections below; the 24 in the table are the rest.

| Column | Field | Confidence | How |
|---|---|---|---|
| `_item.0` | `item_class_path` | high | 17-value runtime class enum (`Normal/FoodItem`, `Normal/MateriaItem`, ...) |
| `equipment.69` | `equip_kind` | high | 24 values; every GE `item_category` maps into exactly one |
| `equipment.70` | `race_gender_restriction` | high | an `xtx_tribe` id below 16, then race-level and collective bands - see below |
| `equipment.139` | `equip_category` | medium | item type / equipment category, not a slot - see below |
| `itemData.36` | `icon_id` | high | value bands partition by item kind - see below |
| `itemData.41` | `rarity_tier` | high | 4 tiers; tier 4 is exactly the eight 1.0 relics |
| `itemData.43` | `is_usable_consumable` | high | 1 on exactly the 343 rows where `63` is not -1 |
| `itemData.66` | `is_repairable` | high | co-extensive with `67`'s repair level; GE `repair_class` blank on every 0 row |
| `itemData.44` | `equip_category_group` | high | GE `item_category` is a strict 1:1 refinement of it - see below |
| `itemData.48` | `class_affinity` | high | the value band picks Suits / Favors / Requires - see below |
| `itemData.65` | `required_matter_item` | high | Dark Matter to repair gear, an -ized Matter to meld materia - see below |
| `equipment.137` | `additional_effect_id` | medium | 7 of 8 `AdditionalEffectEquipItem` rows carry a distinct value - see below |
| `itemData.46` | `level_requirement_hard` | high | which of GE's two mutually exclusive level fields is filled - see below |
| `weapon.141` | `paired_arrow_damage` | high | a step function of level equal to the best arrow damage at or below it - see below |
| `itemData.63` | `use_effect_kind` | medium | the buff family, not the timing: 1 is food-dominated, 2 medicine and potion, -1 not a consumable |
| `itemData.140` | `materia_row_id` | high | a key into `materia.csv`, not an enum - see below |
| `itemData.50/53` | `effect_param_a/b` | low | class-dependent floats, only a pair on shields - see below |
| `weapon.94/95/101` | Craftsmanship / Magic Craftsmanship / Control | medium | 192 crafting tools |
| `weapon.96/97/102` | Gathering / Output / Perception | medium | 75 gathering tools |

`equipment.69` identifies item kind, which makes the rest of the tables readable
and identifies the crafter and gatherer tool populations:

```
0 not equippable   2 shield        5 throwing      6 ammunition
9 head             10 undershirt   11 body         12 undergarment
13 legs            14 hands        15 feet         16 waist
17 neck            36 one-handed   37 two-handed   38 bow
39 primary tool    40 secondary tool
42 body + head     43 body + hands/legs/feet       44 legs + feet
45 wrists          47 ears         49 ring
```

Five of those values were missing from this enum until the accessory pass, and
the last three are worth reading twice. **42, 43 and 44 are multi-slot garments**,
and the client encodes that fact twice: each one's item set is *exactly* the
carrier set of the matching 20xxx restriction effect, with no item in either set
missing from the other.

| Slot | Items | Matching effect |
|---|---|---|
| 42 | 35 | `20026 Cannot equip gear to head` |
| 43 | 1 (Reindeer Suit) | `20027 Cannot equip gear to hands, legs, and feet` |
| 44 | 6 | `20028 Cannot equip gear to feet` |

Each of those three effect ids appears on one slot value and nothing else, so the
slot number and the effect are redundant encodings. Slots 5 and 6 are throwing
weapons (`Chakram`, `Firepot`, `Bomb Arm`) and ammunition (`Bronze Arrow`); both
count as `projectile` damage.

### itemData.140 is a key into materia.csv, and materia.csv is a full decode

This column was read as an abstract effect kind. It is a **row id**: the client
ships `materia.csv`, 66 rows by 80 columns, and `140` is its key. Of the 260 items
that `materia.csv` names in its grade columns, **256 carry the matching key**.

`materia.csv`'s layout, which is worth recording because it decodes 1.0 materia
outright:

| Columns | Holds |
|---|---|
| 0-3 | the four grade item ids, I to IV |
| 4 | primary parameter id, in the 15xxx namespace |
| 5-20 | 16 magnitudes for it - 4 grades x 4 ranks |
| 21 | second parameter id, `-1` on single-stat materia |
| 22-37 | its 16 magnitudes |
| 38-41 | one icon id per grade |
| 42-79 | 38 booleans, unverified - shaped like meld targets |

`Lifethirst` is the clearest read: key 3, primary `15001` HP and secondary `15002`
MP, magnitudes 5/7/8/10 for grade I on both, which is exactly GE's
`HP: +5, +7, +8, +10MP: +5, +7, +8, +10`.

**Value 56 is the default for materia with no definition of their own.** 96 of the
356 materia rows are not listed in `materia.csv` at all, and **every one of those
96 carries 140 = 56**. They are 24 lines x 4 grades - `Bloodbringer`,
`Manabringer`, the six `Breath of <element>` lines, `Byregot's Hammer` and the rest
- and **not one of the 96 has a GE page**, so they read as content that was never
released rather than as a decode gap. For them the column says nothing about the
effect.

`Ahriman Gaze` is the one released line in that position. `materia.csv` row 57
lists its four item ids but is the **only row in the table that carries no
parameter at all**, so `itemData` routes it to 56 instead - and GE's
`Heavy Resistance` for Ahriman Gaze matches what row 56 grants. Whether it shares
Chocobo Down's effect by design or by falling through is not decidable here, but
the value is not wrong for it.

GE corroborates the magnitudes but renders them too inconsistently to score
strictly. On a formatting-agnostic comparison - the set of nonzero values at the
item's grade window, across both parameters - GE agrees on **217 of 256, 0.8477**.
Every residual inspected is GE's rendering rather than a decode error, and the
inconsistency is worth knowing before anyone parses that field:

- Zero ranks are printed for some lines and dropped for others. The `Veil` materia
  give `+4, +5, +0, +6`; `Ironman's Will` gives `+4, +5, +6` for the same shape.
- Consecutive repeats are sometimes collapsed - `11, 11, 12, 12` becomes
  `+11, +12` on `Lifethirst Materia II`.
- Some rows list only the endpoints: `Touch of Rage Materia I` reads `+1 ... +10`
  where the client has 1, 3, 7, 10.
- `Manathirst Materia III` includes one value from the previous grade.
- `Savage Aim` carries no numbers at all on three of its four grades.

Because both are reachable through this key, `materia_effect` and `meld_slots` are
no longer counted among the GE fields with no client column - but the reach is
indirect, via `materia.csv`, and it is the client that is authoritative where the
two differ. `materia.csv` has its own map and decode:
`materia-column-map.csv`, `materia-decoded.csv` and `materia-notes.md`.

### itemData.44 renamed: it is a category group, not an ammo class

This column was named `weapon_ammo_class` on the strength of one observation -
value 7 covers both bows and arrows. Scoring it against GE properly shows the
grouping principle is not ammunition at all: **it is one value per class's whole
kit**, and ammunition is only in there because an archer's arrows are part of an
archer's kit.

The decisive number is that **GE's `item_category` is a strict refinement of it**:
backward purity is **1.0000 over 855 joined rows** - across 40 GE categories, not
one ever appears under two different values of `44`. Forward purity is 0.7602,
which is the point: each value deliberately spans several categories.

| Value | GE categories it groups |
|---|---|
| 2 | Pugilist's Arm + Throwing Circle |
| 3 | Gladiator's Arm + Throwing Blade |
| 4 | Marauder's Arm + Throwing Axe |
| 7 | Archer's Arm + Arrow |
| 8 | Lancer's Arm + Throwing Spear |
| 10 | Shield, alone |
| 22 | Thaumaturge's Arm + Two-Handed Thaumaturge's Arm |
| 23 | Conjurer's Arm + Two-Handed Conjurer's Arm |
| 29-36 | one per crafter: primary + secondary tool |
| 39, 40 | Miner, Botanist: primary + secondary tool |
| 41 | Fisher: primary + secondary tool + Bait + Lure |

Against `requires_classes` it scores 0.9228 forward and 0.9509 backward, high but
not exact - and the reason it is not exact is what settles the reading. **Value 10
is every shield and nothing else**, while shields are usable by GLA, PLD, CNJ, THM
and WHM. If `44` were a class field, shields could not have one value; as a
category group they must.

Neither purity direction clears the map's categorical gate, which needs both above
0.85, so this stayed unnamed-from-GE until the column was audited directly. The
right test for a coarsening is the backward direction alone.

Two incidental findings. Values `5`, `6`, `9`, `21` and `24` each hold exactly one
untranslated (`[en]`) arm - one-handed for the first three, two-handed for the
last two - so they are **reserved categories 1.23b never shipped**; the enum also
skips 11-20, 25-28 and 37-38 entirely. And GE has a category typo: one row reads
`Thamaturge's Arm`, which the client files under value 22 with the correctly
spelled ones.

### itemData.36 is the icon id, and GE cannot say so

**GE has no icon field.** None of its 68 columns is one, so this column has no
wiki counterpart and never will - the case for it is entirely client-internal. It
is a strong case, which is why the column moved from medium to high.

1. **It is set on every one of the 8,403 rows**, without exception - gil, shards,
   quest items, untranslated placeholders, all of them. Only an icon is universal
   like that, which is what rules out the obvious rival reading of a model id:
   only equipment has a model.
2. **Granularity is per-item.** 2,565 of the 3,631 distinct values belong to a
   single item.
3. **Shared values group by item kind, not by item family.** `61346` is on all 233
   weapon parts, `60747` on the 51 dyes and paints, `60038` on 31 panaceas,
   `60739` on 1,199 dummy rows, and `60000` is the fallback (223 of its rows are
   equippable, 200 of those untranslated).
4. **The value bands partition the item space** the way an icon sheet is laid out.
   Excluding the `60000` fallback:

| Band | Holds | Purity |
|---|---|---|
| 00xxx | 30 key items | 30/30 |
| 60xxx | misc, consumables, materia, dummy rows, **all 278 accessories**, ammunition, throwing weapons, fishing bait | - |
| 70xxx | weapons, tools and shields | 803 of 866 |
| 80xxx | armour | **3,116 of 3,116** |

   Accessories are 277/277 in 60xxx and armour 3,116/3,116 in 80xxx, both exact.
   The 63 weapon-group items that fall in 60xxx instead of 70xxx are fully
   accounted for: 43 ammunition, 6 throwing weapons and 14 fishing baits and
   needles, which band with consumables rather than arms. Over all 4,482
   equippable items the band predicts hand-versus-body at 0.9822.
5. **Against GE's categories it beats chance by a wide margin.** Restricting to
   the 758 icons shared by two or more joined items - singletons make the metric
   meaningless - forward purity from icon to `item_category` is **0.7808 against a
   shuffled baseline of 0.2864**.

One prediction that failed, recorded so nobody re-runs it: colour variants do
*not* share an icon. Only 71 of 791 multi-member name families resolve to a single
icon value, so the client tints per variant and gives each its own id. That is
consistent with an icon but useless as a test.

### The use-effect block, and why 50/53 are not a pair

Only **three columns are consumable-only**, each populated on exactly the same 343
rows and nothing else: `43 is_usable_consumable`, `61 recast_seconds` and
`63 use_effect_kind`. Everything else that looks like part of the block leaks.

`itemData.59` is the effect **duration**, and it is not consumable-only: 288 of its
296 live rows are consumables, and the other 8 are the whole of
`Normal/AdditionalEffectEquipItem` - the proc weapons. On those it is the duration
of the status the proc inflicts, 60 seconds on `Dated Poison Dagger`,
`Dated Blinding Dagger` and the other daggers, 30 on `Dated Silencing Dagger`,
`Dated Sleeping Dagger` and the two baghnakhs. That reads correctly: Silence and
Sleep get the short durations. `itemData.61` recast, by contrast, is on all 343
consumables and nothing else.

`itemData.50` and `itemData.53` are named `effect_param_a` / `effect_param_b`, and
the `a`/`b` should not be read as a pair - **they co-occur only on shields**:

| Column | Live rows | Shape |
|---|---|---|
| `50` | 490 across 10 item classes | a flat `1` on all 292 food, all 43 shard/crystal and all 26 medicine rows; real magnitudes (12-122) on 80 shields; fractions (0.05-0.5) on standard-item and proc-weapon rows |
| `53` | 85 rows | 80 of them shields, plus 4 good-status items at 4000/9000 and one proc weapon |

So on food `50` is a constant and `53` is absent; only on a shield do the two
behave as one quantity pair. (292 food rows exist in all; the 243 counted in the
1015xxx section above are the subset flagged usable by `43`, so 49 food-class rows
are not usable consumables at all.)

**A correction:** this note used to say `53` exceeds `50` on every one of the
shields. It does not. Of the 80 carrying both, `53` is higher on 46, equal on 8
and **lower on 26**. The direction correlates with shield type - every `Targe`
(11) and `Buckler` (10) has `53` higher, every `Scutum` (8) and `Pelta` (3) has it
lower, every `Escutcheon` (3) has them equal - which is the shape a
rate-versus-strength pair would take. But the generic `Shield` suffix (21/6/4) and
`Hoplon` (8/3) are mixed, so shield type does not determine it.

#### Why the shield pair cannot be resolved further

Both available routes are closed, so treat this as settled-unresolvable rather
than pending.

**GE has nothing to offer.** Its 68 columns contain no block field of any kind,
and while `defense` and `magic_defense` exist they are populated on **zero of the
80 joined shields**. A GE shield infobox carries durability, repair class and
level, meld and convert flags, price, required level and a handful of stat
bonuses - not one defensive number. No further wiki work changes this.

**The client's own block parameters never meet these columns.**
`15041 Block Rate` (16 carriers) and `15042 Block` (1) exist as slot params, which
would identify the pair by comparison - except that not one carrier is a shield.
All 17 are ordinary armour (`Sentinel's Cuirass`, `Heavy Darksteel Gauntlets`,
`Gallant Sollerets`), and every one of them has `50` and `53` at 0. The two
encodings are **disjoint by item**, so no row exists on which a named block value
could be compared against either column.

What the structure does say is that these two columns must be the shield's
defensive numbers. **Shields are filed in `weapon.csv` and `equipment.csv` and
never in `armor.csv`** - 85 of 85, checked all four tables - so a shield has no
`defense` column in the schema at all, and it carries `damage` 0 as well. Beyond
its bonus slots, `50` and `53` are the only per-item numbers a shield has. Which
of the two is the rate and which the strength is what stays open.

### The crafter and gatherer tool stats

`weapon.csv`'s u16 block is not weapon data at all for 267 of its rows. Two
triples of columns are populated on disjoint item sets - `{94, 95, 101}` on 192
items that are all `equip_kind` 39/40 tools with `damage` 0, and
`{96, 97, 102}` on 75 more. Within each triple the three columns are nonzero on
*identical* row sets, so each triple is one item kind's three base stats.

`xtx_text_paramName.csv` carries a low-id base-stat namespace on a tens grid
(1-12 attributes, 110 HP, 200 Attack Power, 600 Defense, ...) that includes
exactly two matching triples: 400 Craftsmanship / 410 Magic Craftsmanship / 420
Control, and 500 Gathering / 510 Output / 520 Perception. Matching them to the
columns in ascending order within each triple gives the table above.

Caveat worth keeping: the *assignment of the triple* is solid (crafting tools
carry crafting stats), but the **order within each triple is an assumption** that
the column order follows the id order. GE records no numbers for any tool, so
nothing measures it, and the id-reference scan above establishes that no client
table cites these ids either - there is no confirming reference to go and find. Magnitudes are consistent with it - Mythril Saw reads
68/63/53 for Craftsmanship/Magic Craftsmanship/Control - and the Chocobotail saw
line inverts to put its highest value in `101`, which fits a Control-biased tool
line, but that is corroboration, not proof.

### itemData.41 and itemData.66, resolved by the column beside them

Both were on the unidentified list until the slot-pair audit reached `itemData`,
which has no slot run to audit but does have a gating structure worth reading.

`itemData.41`'s four values are a **rarity tier**, and tier 4 is what proves it:
its eight members are exactly the 1.0 relic weapons - Sphairai, Curtana, Bravura,
Artemis Bow, Gae Bolg, Holy Shield, Stardust Rod, Thyrus. Tier 3's 107 rows are
the artifact tier - 43 primal and Moogle weapons (`Ifrit's Claws`,
`Garuda's Talons`, `Murderous Mogfists`) plus the 64 job artifact-armour pieces
(`Gallant Corselet`, `Choral Shirt`, `Drachen Breeches`) - tier 2's 517 are
grand-company and other named gear
(`Storm Lieutenant's Hooks`, `Gridanian Hora`), and tier 1 is everything else
including the dummy rows. An ordinary-to-relic ladder in that population order is
not something another reading produces. GE records no rarity at all.

The client then confirms the reading outright, in text rather than in data.
`materiaBook.csv` rows 46, 47 and 53 print an item name through a colour macro
that switches **on `itemData.41`** - `[@SWITCH([@SHEET(itemData,2001001,41)], ...)]`
- and it lists six colour branches: white, green, blue, purple, orange, yellow.
So `41` is the field that picks an item name's colour, which is what a rarity
tier is for. Only 4 of the 6 branches are reachable in 1.23b; the top two are
defined and unused.

`itemData.66` is **`is_repairable`**. It is set on 4,192 rows, which is every one
of the 4,191 rows carrying a repair level in `67` plus one untranslated row, and
nothing else - `67` has no live row outside it. GE agrees one-directionally:
`repair_class` is populated on 2,861 of the 2,978 joined rows where `66` is 1 and
**blank on all 2,610 joined rows where it is 0**.

### itemData.65 renamed: it is the required matter, not the materia catalyst

`materia_catalyst` was GE's name for `itemData.65` at 254/256, and the rate is
right but the name covered a fourteenth of the column. `65` holds an item id from
the client's `Catalyst` item kind (1013), and its 17 distinct values split into
two roles with **zero overlap**:

| Rows | Value | Role |
|---|---|---|
| 3,972 equipment | Grade 1-5 `Dark Matter` | repair material |
| 352 materia | one of 12 `-ized Matter` | melding catalyst |

Every row carrying an `-ized Matter` is absent from `equipment.csv`, and every
gear row carries a Dark Matter. GE only ever documents the materia side - hence
256 comparable rows against 4,324 populated ones - so it named the minority role.

The gear side is not a loose correlation either: the Dark Matter grade is a
**strict function of the level band** in `itemData.47`, with no overlap at all
between bands.

| Grade | `optimal_level` range | Rows |
|---|---|---|
| 1 | 1-10 | 451 |
| 2 | 11-20 | 460 |
| 3 | 21-30 | 713 |
| 4 | 31-40 | 823 |
| 5 | 41-50 | 1,525 |

`materia_catalyst` stays on the row as the GE cross-check, so the field is still
counted as mapped; the client name is `required_matter_item`.

### The repair dialogue corroborates four of these columns

`populaceItemRepairer.csv` is the repair NPC's dialogue - 102 rows x 5 language
columns, keys 1-102 with no gaps, three named NPCs (Braitognieux, Meara,
Gogorano) and a four-chapter in-shop treatise at rows 62-65 and 67-86. It has no
columns to map, but it states in text what four columns were named from GE:

- **`itemData.65`** - rows 80 and 86 say a crafter repairing an item must hold
  "the proper dark matter". That is the gear side of `65` named by the client
  itself, independently of the level-band argument above.
- **`itemData.64` / `itemData.67`** - row 81 says "both profession and skill will
  limit the range of what he or she may fix", and row 101 that passing Disciples
  of the Hand "who meet the specified class and level requirements" can mend gear.
  A repair class and a repair level are exactly the pair. This corroborates what
  they are, not their values, so `64` stays at medium on its 0.9774.
- **`itemData.33`** - row 69 says an item that becomes heavily damaged "will cease
  to provide any benefits", so durability gates the whole stat block rather than
  scaling it. The salesman dialogue puts the thresholds on that (below); the same
  Condition is what the materia tome's row 23 says blocks spiritbond growth at
  zero.

Two things the dialogue adds that no column carries: shop repair deliberately does
**not** restore an item to mint condition (rows 30 and 72), and the slot menu
renders wear as a percentage - `Condition: N%`, with `Empty` shown instead when
the socket holds no item.

#### equipment.69 names an item kind, not a socket

The repair menu enumerates the character's sockets, and comparing that roster with
the `69` enum shows the two are not the same thing. The menu has **19 sockets**:

| Sockets | Menu entries | `69` kinds that fill them |
|---|---|---|
| 2 | Main Hand, Off Hand | 8: shield, throwing, ammunition, one-handed, two-handed, bow, crafter tool, gatherer tool |
| 8 | Head, Undershirt, Body, Hands, Waist, Undergarment, Legs, Feet | 8: ids 9-16, one to one |
| 9 | Neck, Ears, Left Ear, Wrists, Left Wrist, Right Finger, Left Finger, Right Ring Finger, Left Ring Finger | 4: 17 neck, 45 wrists, 47 ears, 49 ring |

Only the armour block is one to one. Four accessory kinds fill nine sockets and
eight weapon kinds fill two, so `69` says what an item *is* and never which socket
it occupies - the same distinction the shared-column-space section makes about
table membership.

The four finger entries are four sockets and not a renaming, which the Japanese
settles: rows 94/95 name the right and left finger, rows 96/97 the right and left
**ring** finger - a different digit, not a reworded label. So the two unused ids
inside the accessory run, 46 and 48, cannot be the extra finger sockets either,
and what they were reserved for stays open.

The file carries two generations of the menu. Rows 12-26 cover the ten weapon and
armour sockets with hardcoded page labels that do not agree - `(1 of 2)`,
`(2 of 2)`, `(3 of 3)` across three pages - and rows 32-36 reword the first page
(`Quit` for `Cancel repairs`). Row 88 then replaces the labels with a
parameterized `(N of M)` and rows 89-97 add the nine accessory sockets, which is
consistent with accessories becoming repairable after the first version shipped.

#### equipment.139 is a finer item-type category, distinct from 69

Named `model_slot` on an early pass from its top values (the armour slots 22-26),
but the full distribution is an item-type / equipment-category code. Where `69`
says which socket-class an item belongs to (bow, ammunition, throwing, armour
kind, accessory kind), `139` cuts finer and along different lines:

- **1-10**: weapon by discipline - Hora 1, sword 2, axe 3, polearm 4, bow 5,
  shield 6, wand 7, cane 8, scepter 9, staff 10.
- **11-21, 28-38**: crafting and gathering tools, one value per tool (saw 11,
  pickaxe 19, culinary knife 35).
- **22-27**: armour slot - head 22, body 23, hands 24, legs 25, feet 26, waist 27.
- **39-42**: accessory slot - wrist 39, ear 40, neck 41, ring 42.

That rules out both earlier readings. It is not a *slot* - it separates sword
from axe from bow - and it is not appearance, since 674 differently coloured
Doublets all share 23. It is also not an ammo/throwing field: arrows and thrown
weapons are **0** here, and their kind is carried by `69` (arrow 6, thrown 5, bow
38). The open part is the **43-91** tail, near-unique per item and dominated by
relic, primal and notorious gear (Ifrit's Cane 46, Garuda's Gaze 76); whether
that tail is a per-set model id or just fine categories for special gear is not
settled, which is why the column stays medium.

#### itemData.48 is the class affinity, and its value band is the mode

`populaceShopSalesman.csv` is the general-merchant dialogue - 501 rows x 5
languages, keys 0-500 with no gaps: shop greetings, the buy/sell menu, eight
crafting-guild shopfronts of five rows each (a greeting, `Select an area.` and
three `xtx/facility` areas, which is where all 24 facility references come from),
and a mechanics primer at rows 222-234. The primer is what matters here.

Rows 223-225 describe **three renderings of one item property**, and GE splits
them into three fields accordingly:

- `Suits: All Classes` - equippable by any class or race with no stat penalty.
- `Favors` plus classes - anyone may equip it, but only the listed classes draw
  the full benefit of its stats.
- `Requires` or `Fits` plus classes or races - nothing else can equip it at all.

The three GE fields are **mutually exclusive**: across 3,521 annotated joined rows,
no item carries two of `suits_classes`, `favors_classes` and `requires_classes`.
And `itemData.48`'s value band says which rendering applies:

| Band | Meaning | Values |
|---|---|---|
| `1001` | all classes, no penalty | 1 |
| other `1xxx` | Favors this list | 27 |
| `2xxx` | Requires this list | 82 |

That rule holds on **3,504 of 3,521 rows, 0.9952**; the 17 residuals are 7
`requires` rows at 1001, 5 `favors` rows at 2xxx, 4 `requires` at 1xxx and one
`suits` at 2xxx. GE writes the all-classes case as `suits_classes` on 1,169 rows
and as `favors_classes = All Classes` on 130 more, and leaves all three blank on
1,971 others - the same client value each time.

So **`suits_classes` is mapped** and leaves the unmapped list, which drops to 6.
It is not a separate property: it is `itemData.48 = 1001`. The column is renamed
`class_affinity`, since `requires_classes` named one of its three modes.

`fits_races` stays with `equipment.70`, which is the race and gender restriction;
row 225 confirms Fits is the race form of the same hard gate.

#### Condition is a cliff at 0%, not a slope

Rows 227-232 give the wear mechanic precisely, which sharpens what the repair
dialogue only implied:

- Condition degrades through combat, gathering and synthesis.
- **Gear Damage** appears when an equipped item reaches Condition **10%**, and at
  that point the owner still receives the item's **full** stats - it is a warning,
  not a penalty.
- **Heavy Gear Damage** appears at Condition **0%**, and there the item provides
  no benefits at all.

So `itemData.33` gates the stat block as a step at zero and never scales it. That
also reconciles two statements that look contradictory: repairing "will completely
restore its stats" (rows 230, 233, 234) while shop repair does **not** restore an
item to mint condition (`populaceItemRepairer.csv` rows 30 and 72). Both hold,
because stats depend only on Condition being above zero.

Rows 230, 233 and 234 also place the three repair NPCs from that file in one city
each: Gogorano outside the Quicksand in Ul'dah, Meara at the Ebony Stalls in
Gridania, Braitognieux on West Hawkers' Alley in Limsa Lominsa.

One other number the dialogue fixes: guild facility use is charged as a **flat
fee** (row 31), not per item or per synthesis.

#### The kinds with no socket are the kinds with no durability

The repair menu has no socket for throwing weapons or ammunition, and that follows
from the data rather than being an omission: **0 of those 66 items carry
durability in `itemData.33` and 0 are flagged repairable in `itemData.66`**. They
are the only two equippable kinds with nothing to repair.

One wrinkle runs the other way. Undershirts and undergarments *are* sockets in the
menu, and all 212 of them carry a repair class and level and are flagged
repairable - yet **not one carries durability**, which GE corroborates
(`wear_durability_points` blank on all 86 joined rows). They are repairable items
with no wear to lose. 7 of the 477 feet items are in the same position.

#### weapon.141 is the arrow damage assumed for a bow

The last unidentified column, and the previous reading of it here was wrong in a way
worth recording: it was described as "a bow-only secondary damage figure at
0.56-0.79 of `damage`". **That ratio was an artifact.** `141` is independent of
damage - at level 50 nineteen bows span damage **71 to 116** while `141` stays 56,
and at level 40 four span 54-63 while it stays 36. Both values rise with level,
which is all the ratio band was measuring.

`141` is set on **exactly the 59 bows and nothing else in any table** - the only
weapon kind that needs ammunition - and it is a step function of `itemData.47` with
**no level carrying two values**. Each step is the highest damage among arrows of
that level or lower:

| Bow level | `141` | The arrow it matches |
|---|---|---|
| 1 | 4 | Warped Arrow, lvl 1 |
| 5, 6 | 5 | Dated Bronze Arrow, lvl 3 |
| 8, 10, 11 | 7 | Bronze Arrow, lvl 8 |
| 13, 14, 16 | 9 | Dated Bronze Swallowtail Arrow, lvl 13 |
| 18-22 | 13 | Iron Arrow, lvl 18 |
| 24, 25 | 15 | Dated Iron Arrow, lvl 23 |
| 28-32 | 22 | Steel Arrow, lvl 28 |
| 34, 35 | 26 | Dated Silver Arrow, lvl 33 |
| 37 | 31 | Dated White Coral Arrow, lvl 37 |
| 38, 40 | 36 | Mythril Arrow, lvl 38 |
| 42, 43, 46 | 39 | Dated Blue Coral Arrow, lvl 42 |
| 47 | 48 | Dated Red Coral Arrow, lvl 47 |
| 49, 50 | 56 | Cobalt Arrow, lvl 48 |

**30 of 30 bow levels exact, across 13 distinct values, irregular jumps included.**
The four arrow damages it never takes (6, 11, 19, 20) are the ones whose levels no
bow sits at, which is what the rule predicts.

Two readings were weighed. Coincidence between two parallel level ladders is the
alternative, but the values are the arrow numbers themselves, jumps and all, and the
column exists on exactly the one weapon kind that consumes arrows - so the pairing
is the reading. What the client *does* with the number is now largely settled.
Arrows carry their own `weapon.135` damage (18 of 21 arrow rows: Bronze 7, Iron
15, Cobalt 56), so the live shot must scale with the *equipped* arrow, not a fixed
value on the bow - which rules out `141` being the per-shot combat figure. And a
bow's `141` equals the best arrow's damage at its level (Alesone's Songbow 141 =
Cobalt Arrow 135 = 56), i.e. a bow-side cache of the best available arrow. This
mirrors FFXI, whose ranged base sums ranged-weapon DMG + ammo DMG at fire time
(LSB `GetRangedWeaponDmg`, `src/map/entities/battle_entity.cpp:768`); on that
inherited model `141` is a displayed or estimate total, with a no-ammunition
fallback the only alternative the sheets still allow. The arrow-damage and
best-arrow facts are client evidence; the FFXI-inheritance step is cross-game
inference, below the wiki tier - a strong prior, not a confirmed 1.23b behavior.

#### itemData.46 is the hard-or-soft level gate

`itemData.46` sat on the unidentified list through several passes, and the reason it
survived them is worth stating: every earlier attempt scored it against the
**values** of GE's fields. It is named by whether a field is **populated** at all.

GE carries two level fields and **never fills both** - across 5,597 joined rows, not
one carries `required_level` and `optimal_level` together. Which of the two an
editor filled is the signal:

| `itemData.46` | GE field populated | Rows |
|---|---|---|
| 1 | `required_level` | 1,065 |
| 0 | `optimal_level` | 1,847 |
| 0 | neither - not equipment | 2,656 |
| - | disagreements | 29 |

That is **0.9948 agreement against a 0.8081 majority baseline, lift 0.9730**. So `46`
says whether the level in `itemData.47` is a hard gate or an optimal level, and it
is the level counterpart of the class bands in `itemData.48` - the client stores the
hard-or-soft distinction once per axis, and GE renders it by choosing a field name.
`populaceShopSalesman.csv` row 226 states the soft case outright: below the optimal
level an item can still be equipped, at stats reduced in proportion to the gap.

**The two gates are independent.** 268 rows are hard on level with no class
restriction at all, and 640 are hard on class while soft on level, so an item can be
strict on one axis and lenient on the other.

All 29 residuals are GE-side, and 7 are a single pattern worth knowing when reading
`required_level`: **the job Souls**. GE records their rank-30 job unlock as
`required_level` while the client's `itemData.47` is 1 - they are key items in the
`2000201`-`2000207` block, not equipment, so the 30 is quest lore in an item field.
The rest are an editor picking the other wording (Chocobo Mask, Frostbite, a run of
bows and arrows) or leaving both fields blank (the three `Plundered` pieces,
Militia Spinning Wheel).

#### The item id itself encodes the equip kind

`populaceNMReward.csv` is Rowena's dialogue - the runestone and relic trader, not a
notorious-monster table as the name suggests - and it names **19 items by literal
id**, more than any other dialogue table read here. The runestone stock at rows
4-15 is three four-piece sets (Templar's, Buccaneer's, Harlequin's), and their ids
are what prompted this check: `8011709` a coif, `8031719` a haubergeon, `8081209`
sollerets, `8090807` tassets.

**The first three digits of an item id give its `equipment.69` kind**, at 0.9563
forward purity over the 4,870 equipment rows, and exactly 1.000 on 22 of the 36
prefixes:

| Prefix | Kind | Rows | Purity |
|---|---|---|---|
| 301, 302 | not equippable | 393 | 1.000 |
| 391 / 392, 394 | throwing / ammunition | 66 | 1.000 |
| 402, 404, 408 / 403 / 407 / 410 | two-handed / one-handed / bow / shield | 340 | 1.000 |
| 502, 503 | one- and two-handed **mixed** | 144 | 0.512-0.688 |
| 601-608, 701-703 | crafter and gatherer tools **interleaved** | 270 | 0.625-0.692 |
| 801 / 803 / 804 / 805 / 806 / 807 / 808 / 809 | head / body / undershirt / legs / undergarment / hands / feet / waist | 3,321 | 0.945-1.000 |
| 901 / 903 / 904 / 905 | wrists / ears / neck / ring | 278 | 1.000 |

So an item id alone identifies the slot for most of the table, with two exception
regions worth knowing: `502`/`503` mix one- and two-handed weapons, and the `6xx` /
`7xx` tool blocks interleave crafter and gatherer tools. Together with the shared
column space above, that means a bare id and a bare column index between them
locate a value with no lookup at all.

The top level is a two-tier id space, and the counts corroborate figures already in
this map rather than adding new ones - which is the point of recording it:

| Ids | Class from `_item.0` | Rows |
|---|---|---|
| 7-digit `10xxxxx` | Money | 47 |
| `20xxxxx` | ImportantItemStandard | **68** - the key-item class above |
| `30xxxxx` | Food 292 + EnchantMedicine 29 | 393 |
| `39xxxxx` | throwing and ammunition | **66** - the two kinds with no durability |
| `40xxxxx` / `41xxxxx` | weapons / ShieldItem | 316 / **85** |
| `60xxxxx`, `70xxxxx` | ToolItem | 270 |
| `80xxxxx` / `90xxxxx` | armour / accessories | 3,321 / **278** |
| 8-digit `101xxxxx` | MateriaItem | **356** - the `itemData.140` population |
| `110xxxxx`, `120xxxxx`, `130xxxxx` | DummyItem | 1,304 |

Rowena's other literal ids are the relic chain: three primal oblations (`10011151`
Inferno Totem, `10011152` Kupo Nut Charm, `10011154` Vortex Totem - note `10011153`
is skipped) and three primal seals (`10011156` Inferno, `10011157` Vortex,
`10011158` Tremor). Her row 66 and 82 cite key item `2001026`
`On the Properties of Beastmen` as the book that tells the seals apart, and her
menu offers the `2001027` Soiled Promissory Note - both from the key-item block
below, so that block now has two of its members tied to the dialogue that uses them.

#### equipment.137 is an additional-effect reference, which leaves 2 unidentified

Chasing `_item.0`'s rarer classes off the back of that id sweep named one of the
three unidentified columns. `equipment.137` is nonzero on **31** rows - not the
"~20" previously recorded - every one a weapon, with values 1001-1023.

The client names it: 7 of the 8 rows whose `_item.0` is
`Normal/AdditionalEffectEquipItem` carry a distinct value here - the Dated
Paralyzing, Poison, Blinding, Silencing and Sleeping Daggers and the Smothering and
Disabling Baghnakhs - with Dated Maddening Dagger the exception at 0. The other 23
carriers are ordinary `StandardItem` and share values by family: **1002 on all seven
Ifrit weapons, 1006 on all seven Garuda**, 1021 and 1022 across the Moogle weapons,
and Flametongue 1001, Frostbite 1003, Curtana 1023 unique.

**The competing reading is a weapon-series id**, which fits the family sharing just
as well. Two things favour the effect reading: the client's own class name for the
clearest subset, and the fact that the two classic elemental-proc weapons
(Flametongue, Frostbite) carry unique values rather than a shared "one-off weapon"
code. It is **medium**, not high, because the table these 1001-1023 ids key into is
not in the client-data dump - `boot_skillequip.csv` was checked and is unrelated -
so no effect can be resolved by name.

#### The key-item class, and an icon exclusive to one id block

`populaceChocoboLender.csv` names four items by literal id rather than at runtime -
`2001004` Storm, `2001005` Serpent and `2001006` Flame Chocobo Issuance, and
`2001007` Chocobo Whistle - which extends the `2001xxx` block the materia tome
opened (`2001001` Materia Assimilator, `2001002` Materia Melder, `2001003`
Augmented Materia Melder). Following the block out gives the whole key-item
population, and two columns are the better for it.

`_item.0` has exactly one `Important/*` value, `Important/ImportantItemStandard`,
and it covers **68 rows in two id blocks**:

| Ids | Count | What | `itemData.36` |
|---|---|---|---|
| 2000001, 2000002 | 2 | Key, Pendant | 60000 |
| 2000101-2000128 | 28 | the **treatises** - Spinning Training, Tailoring Training and the rest | 60746 |
| 2000201-2000207 | 7 | the **job Souls** - Paladin, Monk, Warrior, Dragoon, Bard, White Mage, Black Mage | 61680-61686, one each |
| 2001000-2001030 | 31 | key items proper | **798** on 30; 2001000 is an untranslated placeholder on 60000 |

Two things follow. **Icon 798 is exclusive**: all 30 named `2001xxx` rows carry it
and **no other item in the 8,403-row table does**, which is the cleanest instance of
the value-band argument that named `itemData.36` - an icon that partitions onto one
id block and nothing else. And the 28 treatises are the ones
`populaceGuildShop.csv` rows 81-86 sell for guild marks and refund, so that
vocabulary now has ids behind it.

The `2001xxx` roster also settles a cross-file question. `2001017`-`2001025` are the
nine bardings, three per city-state as half, full and crested - so **barding is a key
item, not equipment**. That is why `populaceCompanyShop.csv` sells barding for seals
while the chocobo lender only changes and displays it (its row 100 says outright
that buying is someone else's business).

Beyond those ids the file yields one hard number, which is rare in this family: row
9 requires **at least one class at level 10** to rent a chocobo. Its rental rate and
duration are runtime arguments, so neither is recoverable. The rest is mechanics
with no figures - dismounting ends the lease, the rental expiring bucks the rider,
injury makes the bird flee, and contract extensions are refused (row 65). A personal
chocobo comes from a company issuance item, is named by the player, and is summoned
with the whistle.

#### equipment.70 is an xtx_tribe id, and 1.23b ships 15 clans not 20

`populaceRetainerManager.csv` picks a retainer's clan from a 15-entry menu at rows
125-139, each entry a `xtx/tribe` reference. That table is the key to
`equipment.70`, whose note previously listed 6 of its 25 values.

**`xtx_tribe.csv` has 16 rows and it is gender-specific**, one id per clan-and-gender
combination rather than per clan:

| Ids | Clans |
|---|---|
| 0 | Clanless |
| 1, 2 | Midlander male, female |
| 3 | Highlander **Male** only |
| 4-11 | Wildwood, Duskwight, Plainsfolk, Dunesfolk, each male then female |
| 12, 13 | Seeker of the Sun, Keeper of the Moon - **Female** only |
| 14, 15 | Sea Wolf, Hellsguard - **Male** only |

That is 15 playable combinations, and the retainer menu's 15 entries are ids 1-15
exactly. Five combinations later FFXIV has are simply absent in 1.23b: Highlander
Female, both male Miqo'te clans and both female Roegadyn clans.

`equipment.70` then reads as three bands, and **GE corroborates all 25 values with
no disagreement** - `fits_races` names the clan or race and `gender_restriction`
the gender:

| Band | Meaning |
|---|---|
| 0-15 | the `xtx_tribe` id, so a clan-and-gender restriction; 0 is not equippable |
| 16-23 | race-level: 18/19 Elezen male/female, 20/21 Lalafell male/female, 22 Roegadyn, 23 Miqo'te |
| 27, 28 | all races, male and female |
| 29 | unrestricted - 4,254 of the 4,875 rows |

The race band needs only eight slots because Roegadyn is male-only and Miqo'te
female-only, the same restriction the clan band shows. `16` and `17` are unused and
sit where Hyur male and female would fall by position - Hyur gear is clan-specific
instead, at 1, 2 and 3 - but that placement is inference from the gap, not measured.
`24`, `25` and `26` are unused too.

#### Which client dialogue tables were audited, and what is still unread

Fifteen of the client's shop, book and NPC tables have been read. The
`populace*` family has **55 members**, so this is a targeted set, not the whole
family:

| File | Rows | What it gave |
|---|---|---|
| `populaceShopSalesman.csv` | 501 | the class-affinity bands, the Condition thresholds |
| `populaceItemRepairer.csv` | 102 | the socket roster, the repair gating, dark matter |
| `populaceCompanyShop.csv` | 140 | the commissions; `required_rank` checked and rejected |
| `populaceGuildShop.csv` | 129 | 56 materia line names (see `materia-notes.md`) |
| `materiaBook.csv` | 52 | the materia rules; `itemData.41` confirmed by its colour macro |
| `populaceShopMateriaRemover.csv` | 25 | the first meld never fails; no purge fee |
| `populaceBlackMarketeer.csv` | 19 | **nothing** |
| `populaceCompanyBuffer.csv` | 16 | what Sanction is and how it is granted |
| `populace.csv` | 4,208 | **nothing** for the map; the `9xxxxxx` test-id prefix |
| `populaceRetainerManager.csv` | 178 | `xtx_tribe`, which decodes `equipment.70` |
| `populaceChocoboLender.csv` | 109 | the `2001xxx` key-item ids; icon 798 |
| `populaceBranchsVendor.csv` | 28 | **nothing** |
| `populaceNMReward.csv` | 83 | 19 literal ids; the id-prefix slot encoding |
| `populaceWaveAttack.csv` | 22 | **mob side**: names the hamlet militia and the imperial troopers, tying actor race blocks 1900 and 1800 together |
| `PopulaceHamletCaptain.csv` | 39 | **mob side**: the same content's captain, battle dialogue and a desertion branch |

`populace.csv` was flagged here as the family's one real data table, on the
strength of being 4,208 rows x 67 columns. **That was a shape-only read and it was
wrong.** Only column 66 is populated - the type row declares a type for that column
and no other - so it is a one-column table with 65 reserved and unused columns, and
it carries no English at all.

What column 66 holds is a Japanese talk label, and 4,193 of the 4,208 rows read
"default talk". The remaining 15 are leftover developer strings, and they are
useful for one thing: **the `9xxxxxx` id prefix marks test NPCs.** 4,127 ids sit in
the `1xxxxxx` block and one in `3xxxxxx`, all at the default; 80 sit in `9xxxxxx`,
and **every one of the 15 non-default strings is in that block** - `test` and
`sample` at 9000001-2, four greetings in four languages at 9111101-4 (a
localization check), "I'm a guard" on three of 9111301-4, and a labelled series
`B` through `G` at 9114402-7, whose `A` slot at 9114401 was left at the default.
Any other table keyed by populace id can use that prefix to exclude test entries.

That closes the item-adjacent tables. What remains in the family is guildleve
publishers, camp masters, seasonal-event criers and the GM-event tables, none of
which touch the item columns.

`populaceBlackMarketeer.csv` is worth naming as a dead end so it is not re-read.
Three NPCs (Momoroon, Gagaroon, Lalaroon) take gil *or* company seals, and trade a
held item for seals - but **every item reference in the file is the runtime argument
`$E8(1)`, and no row carries a literal number in its visible text**. The black
market's stock, its prices and its seal rates are all supplied by the caller, so
none of it is recoverable from the dialogue. Its only incidental value is that row
19 prints the `+1/+2/+3` HQ suffix, so graded items pass through the trade.

`populaceBranchsVendor.csv` is the second dead end, and for the same reason. It is
the **Mercantile House**, the item-search service, with a branch in each city-state:
24 of its 28 rows are greetings in Limsa / Gridania / Ul'dah triples (8 triples, of
which 2 are exact duplicates of an earlier one, so 6 are distinct), and the
remaining four are the menu - `Search for an item`, `Cancel search`, `Nothing`.
A player has **one pending search at a time**, which is all the mechanics the file
carries: the cancel row names a single item, not a list. Its one item reference is
the runtime `$E8(1)` and **no row carries a literal number in its visible text**, so
neither the searchable population nor any fee is recoverable here.

## Nothing left unidentified

Every one of the 299 rows is named. `weapon.141` was the last, and its section is
above; before that `itemData.46`, `equipment.137`, `itemData.41` and `itemData.66`
came off the list in earlier passes.

Two named columns are still not fully *resolved*, which is a different thing and
worth keeping straight:

- `equipment.137` is an `additional_effect_id`, but the table its 1001-1023 values
  key into is absent from the client dump, so no effect can be named.
- `weapon.141` is the `paired_arrow_damage`, measured exactly, but what the client
  does with the number - a tooltip total, a no-ammunition fallback - is not
  decidable from the sheets.

**For both, the pcap corpus is ruled out, and structurally rather than for want of
coverage.** `captures/inventory.pcapng` and friends do carry inventory traffic, but
the decoded item records in `data/content_samples.json` hold only `itemId` and
quantity - 481 item observations across 69 distinct ids, with no stat block
anywhere. The server sends an item id and the client resolves damage, delay and
everything else from these same static sheets, so no capture of any size would
carry either value. That reasoning rules the corpus out for every static sheet
column, not just these two, and leaves a decomp of the tooltip formatter or the
item-sheet reader in `ffxivgame.exe` as the only route.

## GE fields with no client column

6 of GE's 68 fields find nothing, and each now has a reason rather than only a
negative result. **Three of the six are not per-item fields at all**, which is why
no column could carry them:

| Field | GE rows | Why there is no column |
|---|---|---|
| `base_item` | 1,425 | a **recipe ingredient restated**: the value appears verbatim inside the row's own `recipe_templates_raw` on 1,401 of the 1,410 rows that have a recipe, **0.9936** |
| `base_material` | 674 | the same, at **0.9243** of rows with a recipe |
| `dye_colors` | 1,928 | a **family of sibling item ids**, not one item's property - see below |
| `hq_effect` | 747 | the HQ grade suffix; the client renders it from a macro and stores no per-item grade - see below |
| `convertible` | 2,741 | searched exhaustively; GE keeps it strictly broader than `meldable` and the client ships only the latter - see below |
| `magic_defense` | 20 | 1.23b items appear not to carry it: no `armor` column is non-constant, no 15xxx `paramName` id is named Magic Defense, and no low-cardinality column reaches any lift against it |

### dye_colors enumerates sibling items, not a property

The client ships **each colour variant as its own item id**, with the colour in the
name, so the set of colours is a relation between items rather than a field on one.
GE writes the field on every variant page and lists the whole family each time -
1,099 of the 1,928 page names are themselves `<base> (Colour)`, 87 are
`Colour <base>`, and 742 are the plain base name.

Reconstructing the family from the page name and looking for the siblings in
`xtx_itemName.csv`: the client ships **every** listed colour for 1,813 of 1,928 rows
(**0.9404**), all but at most one for 1,892 (0.9813), and on average 0.9699 of the
colours listed. So the field is accounted for - it just resolves to a set of ids,
not a value.

### How the search was bounded

Every column of all six tables was scored against all six fields three ways: purity
of the client value against the GE string, lift on the GE value read as a boolean,
and lift on **whether the GE field is populated at all** - the reading that named
`itemData.46`.

One caution is worth recording, because it produced six false positives before it
was caught: the presence test is only valid on **low-cardinality** columns. Scored
against every column, `itemData.36` topped the presence lift for all six fields at
once, which is not a finding - with 3,631 distinct values a per-value majority vote
memorises any boolean. Restricted to the 14 columns with 2 to 6 distinct values,
only `convertible` shows any lift at all (0.8961 on `itemData.66`, and that is the
coarsening described below: repairable implies gear, and gear is what GE annotates).
The other five score exactly zero.

`suits_classes` left this list once the salesman dialogue explained it: it is not
a property of its own but the all-classes rendering of `itemData.48`, value 1001.

`materia_effect` and `meld_slots` both left this list through `itemData.140` into
`materia.csv` - `materia_effect` indirectly at 0.8477 agreement, `meld_slots`
against the 38 boolean meld-target columns.

### hq_effect is the grade suffix, and the client does not store it per item

`hq_effect` is listed above as the grade suffix; the values are what show that:
`+1` (274 rows), `1` (190), `+3` (169), `No` (85), `3` (13), `+2` (6), plus 10
rows an editor filled with something else entirely (`1248`, `Magic Accuracy+10`).
Normalized, that is 462 items at grade 1, 182 at grade 3, 6 at grade 2 and 85 at
none - the same three-grade ladder the client's `+1/+2/+3` name suffix renders
(see the 77/78 section).

No client column carries it. Scored over the 735 usable rows, the GE majority
baseline is 0.8137 and the best candidate reaches 0.9035 - `equipment.70`, the
race/gender restriction, which is spurious. Every closer-fitting column is one of
the bonus-slot machinery columns scoring on the same population, and the
low-cardinality presence test scores it at zero lift. It stays unmapped, and the
reason is on the record rather than untested.

### convertible: searched exhaustively, and it is not in the sheets

`convertible` is worth its own note because the search for it is finished rather
than untried. Every column of all six tables was scored against it, and nothing
identifies it:

- `equipment.139` reaches 0.9956 forward but 0.3966 backward - it is
  `equip_category` (see below), and appearing on gear merely implies "is gear".
- `_item.2` (`unique`) is the best symmetric candidate at 0.9475, and it is a
  correlate, not the field: 618 of 716 unique items are non-convertible, but
  **98 unique items are convertible** and 45 non-unique ones are not.
- `equipment.138` (`meldable`) scores a lift of -0.03 against it.

GE itself treats them as different properties, and consistently: `meldable` is a
strict subset of `convertible` - 691 rows are both, 1,354 convertible-only, 663
neither, and **not one row is meldable without being convertible**. So the client
ships a `meldable` flag and no `convertible` flag, which fits what the tome says
about conversion: `materiaBook.csv` row 18 states that some items cannot be
converted regardless of spiritbond, without tying it to any item property the
sheets expose.

`enhancement_magic_potency_bonus` and `enfeebling_magic_potency_bonus` were listed
here until the 15xxx pass and should not have been: `param:15026` and
`param:15027` are their columns, and GE agrees on 4 of 5 and 5 of 5 rows. They
were hidden by the 25-row sample floor, which is the right floor for *identifying*
an unknown column but the wrong one for *corroborating* a column the client has
already named. The map now records a cross-check on a client-named worn param
from 3 rows up (`numeric-thin`), which is what surfaced them. That rule is
deliberately narrow - worn `param:` rows only, both sides required to vary - and
the two constraints were added because it first attached
`number_of_attacks` to `Sanction` (constant 1 on both sides) and `evasion_bonus`
to `HQ bonus: HP` on 3 coincidental rows.

`gender_restriction` and `fits_races` are both accounted for by
`equipment.70`, which encodes them as one combined restriction id.

## Join and the two mismatch lists

The join is on the English item name from `xtx_itemName.csv`, using GE
`item_name` and falling back to `ge_page_title`, in three widening passes:
5,595 exact, 4 after normalising case and stripping the client's inline colour
codes (`Charred [@1A(1)]Necrologos[@1A(0)] Page`), 12 after folding
singular/plural where it resolved to exactly one item. 4 GE rows hit an ambiguous
name and are excluded from scoring. That leaves 5,607 of 5,665 GE rows joined.

**`ge-items-without-client-row.csv`** - 54 rows, with a `likely_cause` column:

- 24 `client-ships-colour-variants-only`: GE has an uncoloured base page
  (`Dated Cotton Acton`) where the client only ships `Dated Cotton Acton (Red)`
  and siblings. Naming difference, not missing content; the `client_variants`
  column lists what the client has.
- 30 `no-client-name-match`, three causes on inspection: GE misspellings the
  client contradicts (`Dried Majoram` vs `Marjoram`, `Rubelite *` vs
  `Rubellite *`); the 1.0-launch modular armour system that was gone by 1.23b
  (`* Half-robe Back/Front`, `* Acton Body/Sleeves`, 32 of the 54 are flagged
  `removed_before_arr`); and a handful with no client trace at all
  (`The Book of Renette`, `Fen-Yll Signature Shoes`, `Vintage Fen-Yll Boots`,
  `Luminary Leather`, `Aldgoat Meat`).

None of the 54 look like post-cutoff ARR leakage into the wiki tables.

**`client-items-without-ge-page.csv`** - 2,793 rows with a `reason` column. 934
are `no-english-name` (the client ships `[en]` or blank, so they cannot be
name-joined and are not evidence of a documentation gap). The remaining 1,859 are
`no-ge-page`: content the client carries and Gamer Escape never documented,
concentrated in `_item itemData` only (consumables, currencies, guild marks) and
`_item armor equipment itemData` (armour).
