# Evidence map - Historical BattleCommand Workbook

## Evidence verdict

The source object
`sources/historical-battlecommand-workbook/objects/BattleCommand.ods` is
historical secondary research and provisional
field-level evidence. The workspace owner reports that it originated during
the early Project Meteor period, close to the FFXIV 1.x shutdown era. Embedded
metadata records a 2019-02-03 save and LibreOffice 6.1.2.1; it does not establish
the original research date.

Retail captures, retail video, decoded client data, and client scripts take
precedence over conflicting workbook values. Analyst notes, custom columns,
cached formulas, and the explicitly unfinished weapon-skill table do not become
retail facts through extraction.

## Extraction

The `Command` sheet yields 1,237 records with 1,237 unique command ids. The
`Sheet2` unfinished weapon-skill table yields 230 rows for 224 unique ids. Six
ids are duplicated there: 23049, 23082, 23129, 23145, 23490, and 23614.

The `Command` sheet contains 30,648 cached formula cells, including 30,645 in
the mapped command-record region. Twenty cells cache `#VALUE!`. An auxiliary
`ER:JB` block at rows 1061:1063 has incomplete headers and remains an unresolved
raw workbook region rather than being joined into command records.

The structured artifact is a selected-field projection through column FC, not
a complete raw cell matrix. Its `cached_formulas` objects contain formulas only
for selected mapped fields. The preserved source object remains authoritative
for omitted cells and formulas, including the rest of the `ER:JB` region.

Mechanical conversion found 26 non-numeric values across 12 commands in fields
otherwise normalized as numbers. The raw strings, including `?`, `1042?`,
`54-59`, and cached `#VALUE!` results, remain in `raw`; their normalized values
are null and their field names appear in `normalization_issues`.

The tables below reproduce workbook values. A dash means an empty cell. Pi
values are workbook coefficients; the structured artifact separately preserves
the cached radians formulas and results. The unfinished weapon-skill summary is
ordered as self/allies/enemies, followed by its AoE type, AoE location,
resistability code, and damage code.

## Provisional facts: identity and animation

| ID | Name | User / genus | Animation type / model / effect | Full animation |
|---:|---|---|---|---|
| 23058 | Backflip | Puk / 45 | 19 / 2 / 0 | 318775296 (`0x13002000`) |
| 23059 | Tail Chase | Puk / 45 | 19 / 3 / 0 | 318779392 (`0x13003000`) |
| 23144 | Foul Bite | Wolves / 3 | 19 / 4 / 0 | 318783488 (`0x13004000`) |
| 23311 | Bomb Toss | Goblins / - | 19 / 2 / 0 | 318775296 (`0x13002000`) |
| 23312 | Bomb Toss | Goblins / - | 19 / 3 / 0 | 318779392 (`0x13003000`) |
| 23313 | Hail Mary | Goblins / - | 19 / 4 / 0 | 318783488 (`0x13004000`) |
| 23314 | Hail Mary | Goblins / - | 19 / 6 / 0 | 318791680 (`0x13006000`) |
| 23315 | Firecracker Shower | Goblins / - | 19 / 5 / 0 | 318787584 (`0x13005000`) |
| 23456 | Breath of the Lion | Chimera / - | 19 / 1 / 0 | 318771200 (`0x13001000`) |
| 23457 | Voice of the Lion | Chimera / - | 19 / 2 / 0 | 318775296 (`0x13002000`) |
| 23458 | Breath of the Dragon | Chimera / - | 19 / 3 / 0 | 318779392 (`0x13003000`) |
| 23459 | Voice of the Dragon | Chimera / - | 19 / 4 / 0 | 318783488 (`0x13004000`) |
| 23460 | Breath of the Ram | Chimera / - | 19 / 5 / 0 | 318787584 (`0x13005000`) |
| 23461 | Voice of the Ram | Chimera / - | 19 / 6 / 0 | 318791680 (`0x13006000`) |
| 23462 | Dissent of the Bat | Chimera / - | 19 / 7 / 0 | 318795776 (`0x13007000`) |
| 23463 | Chaotic Chorus | Chimera / - | 19 / 8 / 0 | 318799872 (`0x13008000`) |
| 23464 | the Scorpion's Sting | Chimera / - | 19 / 9 / 0 | 318803968 (`0x13009000`) |

## Provisional facts: range and geometry

| ID | Range max / best / min / fallback | Width / rotation pi / cone pi | AoE type / target / height | Target self / ally / enemy | Main / valid mask |
|---:|---|---|---|---|---|
| 23058 | 8 / -1 / 0 / 0 | 2 / 0 / 0 | 3 / 1 / 10 | true / false / false | 31 / 384 |
| 23059 | 6 / -1 / 0 / 0 | 2 / 0 / 2 | 1 / 1 / 10 | true / false / false | 31 / 384 |
| 23144 | 6 / -1 / 0 / 0 | 2 / 0 / 0 | 0 / 0 / 10 | false / false / true | 384 / 384 |
| 23311 | 20 / -1 / 0 / 6 | 2 / 0 / 2 | 1 / 0 / 10 | false / false / true | 384 / 384 |
| 23312 | 8 / -1 / 0 / 0 | 2 / 0 / 2 | 1 / 1 / 10 | true / false / false | 31 / 129 |
| 23313 | 6 / -1 / 0 / 0 | 2 / 0 / 0 | 0 / 0 / 10 | false / false / true | 384 / 384 |
| 23314 | 20 / -1 / 0 / 8 | 2 / 0 / 2 | 1 / 0 / 10 | false / false / true | 384 / 384 |
| 23315 | 8 / -1 / 0 / 0 | 2 / 0 / 2 | 1 / 1 / 10 | true / false / false | 31 / 384 |
| 23456 | 12 / -1 / 0 / 0 | 2 / 0 / 0.5 | 2 / 1 / 10 | true / false / false | 31 / 384 |
| 23457 | 20 / -1 / 0 / 0 | 2 / 0 / 0 | 0 / 1 / 10 | true / false / false | 31 / 384 |
| 23458 | 12 / -1 / 0 / 0 | 2 / 0.25 / 0.666667 | 2 / 1 / 10 | true / false / false | 31 / 384 |
| 23459 | 22 / -1 / 15 / 0 | 2 / 0 / 2 | 1 / 1 / 10 | true / false / false | 31 / 384 |
| 23460 | 12 / -1 / 0 / 0 | 2 / -0.25 / 0.666667 | 2 / 1 / 10 | true / false / false | 31 / 384 |
| 23461 | 10 / -1 / 0 / 0 | 2 / 0 / 2 | 1 / 1 / 10 | true / false / false | 31 / 384 |
| 23462 | 16 / -1 / 0 / 0 | 2 / 0 / 0.666667 | 2 / 1 / 10 | true / false / false | 31 / 384 |
| 23463 | 16 / -1 / 0 / 0 | 2 / 0 / 2 | 1 / 1 / 10 | true / false / false | 31 / 384 |
| 23464 | 12 / -1 / 0 / 0 | 2 / 1 / 0.5 | 2 / 1 / 10 | true / false / false | 31 / 384 |

## Provisional facts: cast, damage, taxonomy, and notes

| ID | Hits | Cast / recast / cast type | Potency; attr / weight; element / weight | Raw / interpreted command type | Command note | Geometry notes | WS table |
|---:|---:|---|---|---|---|---|---|
| 23058 | 1 | 4 / 3 / 11 | 0; 1 / 1; -1 / 0 | 0 / 5 Weaponskill | Knockback | - | false/false/true; aoe 2 at 2; resist 1; damage 1 |
| 23059 | 1 | 5 / 3 / 12 | 0; 1 / 1; -1 / 0 | 0 / 5 Weaponskill | - | - | false/false/true; aoe 1 at 2; resist 1; damage 1 |
| 23144 | 1 | 1 / 3 / 12 | 0; 1 / 1; -1 / 0 | 0 / 5 Weaponskill | - | - | false/false/true; aoe 1 at 1; resist 1; damage 1 |
| 23311 | 1 | 2 / 3 / -1 | 0; 13 / 1; 5 / 0 | 0 / 5 Weaponskill | Toss at target | - | false/false/true; aoe 1 at 1; resist 2; damage 1 |
| 23312 | 1 | 5 / 3 / -1 | 0; 13 / 1; 5 / 0 | 0 / 5 Weaponskill | Self aoe | - | true/false/true; aoe 1 at 2; resist 2; damage 1 |
| 23313 | 1 | 2 / 3 / -1 | 0; 13 / 1; 5 / 0 | 0 / 5 Weaponskill | Tosses bomb in the air | - | false/false/false; aoe 1 at 1; resist 2; damage -1 |
| 23314 | 1 | 0 / 3 / 0 | 0; 13 / 1; 5 / 0 | 0 / 5 Weaponskill | Bomb lands? | - | false/false/true; aoe 1 at 3; resist 2; damage 1 |
| 23315 | 1 | 2 / 3 / -1 | 0; 13 / 1; 5 / 0 | 0 / 5 Weaponskill | Stun | - | false/false/true; aoe 1 at 2; resist 2; damage -1 |
| 23456 | 1 | 3 / 0 / -1 | 0; 13 / 0; 5 / 0 | 0 / 5 Weaponskill | Dispels an effect | - | absent |
| 23457 | 1 | 2.5 / 0 / -1 | 0; 13 / 0; 5 / 0 | 0 / 5 Weaponskill | Used when lion eyes are blue, Heavy | Line aoe? | absent |
| 23458 | 1 | 3.5 / 0 / -1 | 1350; 13 / 0; 9 / 0 | 0 / 5 Weaponskill | Paralysis | To Chimera's front left; It looks like 120 degrees in arr | false/false/true; aoe 1 at 1; resist 1; damage 1 |
| 23459 | 1 | 4 / 0 / -1 | 1300; 13 / 0; 9 / 0 | 0 / 5 Weaponskill | Used when dragon eyes are blue, physical defense - | Circle AOE | absent |
| 23460 | 1 | 3.5 / 0 / -1 | 1350; 13 / 0; 6 / 0 | 0 / 5 Weaponskill | Poison | To Chimera's front right | false/false/true; aoe 1 at 1; resist 1; damage 1 |
| 23461 | 1 | 4 / 0 / -1 | 0; 13 / 0; 6 / 0 | 0 / 5 Weaponskill | Used when ram eyes are blue, silence | Circle AOE | absent |
| 23462 | 1 | 1 / 0 / -1 | 0; 13 / 0; 7 / 0 | 0 / 5 Weaponskill | Knockback | Assuming 120 degrees too | absent |
| 23463 | 1 | 1.5 / 0 / 12 | 0; 13 / 0; 12 / 0 | 0 / 5 Weaponskill | Draw in | - | absent |
| 23464 | 1 | 3 / 0 / 13 | 0; 13 / 0; 12 / 0 | 0 / 5 Weaponskill | Used when someone is attacking from behind, Poison | Rear | false/false/true; aoe 1 at 1; resist 1; damage 1 |

## Retail cross-check

On 2026-09-06, the 17 focus records were mechanically joined by `command_id`
against `xivl-client-data:derived/command_battle_params.csv` at commit
`c041fc0de097f3188deabd65e1099a16feddaf0e`. All 204 compared cells agreed
across `name_en`, `cast_time`, `recast_time`, `range`, `best_range`,
`min_range`, `effect_range`, `magnitude`, `dmg_attr`, `dmg_attr_weight`,
`dmg_elem`, and `dmg_elem_weight`. The same retail artifact assigns all 17
records the Lua class path
`/Command/Game/WeaponSkill/MonsterAttackWeaponSkill`, which agrees with the
workbook's cached `Weaponskill` interpretation at that broad level.

No conflict was found with the existing retail-backed fields compared above.
The agreement does not upgrade workbook-only fields, and `magic_potency` and
`magnitude` remain distinct labels even where their numeric cells agree.

## Conflicts and unresolved meanings

- Every focus row stores animation type 19, while the animation header says
  captures seem to use 33 instead of 19 for monster attacks. No capture citation
  is embedded, so both the explanation and the 19-versus-33 discrepancy remain
  unresolved.
- Every focus row has raw command type 0, which the workbook header includes for
  enemy skills. A cached formula reclassifies every focus row as code 5,
  `Weaponskill`, using analyst columns and the unfinished weapon-skill list.
  Retail client scripts support the broad monster weapon-skill class, but do not
  validate the workbook's reclassification formula.
- The target flags, cached target masks, cached AoE type/target, and unfinished
  weapon-skill target columns disagree for several focus records. Their
  semantics may differ. The extraction retains each representation and makes no
  merged target-mask claim.
- Cast and recast numbers agree with decoded client data, but the workbook does
  not state their units. It does not establish animation lock, hit timing, status
  application timing, or damage timing.
- Status text such as `Knockback`, `Stun`, `Paralysis`, `Poison`, `Heavy`,
  `silence`, `Draw in`, and `Dispels an effect` is analyst note text. It remains
  a lead until retail evidence identifies the applied status or effect.
- The unfinished damage column is a provisional code. It is absent for six of
  the nine Chimera records and uses -1 for two goblin records. It does not define
  damage formulas or prove that a zero workbook potency means no damage.
- `Line aoe?`, `It looks like 120 degrees in arr`, and `Assuming 120 degrees
  too` are explicit uncertainty or ARR comparison. They do not establish 1.23b
  geometry.
- Cached formulas were preserved, not recalculated. Formula-cache freshness is
  unresolved wherever the workbook does not provide an independent source cell.
