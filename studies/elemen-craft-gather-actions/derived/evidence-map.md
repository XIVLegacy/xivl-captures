# Evidence map - elemen-craft-gather-actions

Transcription of the eLeMeN - FF14 class/action pages for the Disciples of the
Hand (8 crafters) and Disciples of the Land (3 gatherers). Evidence tier: wiki
(packet captures > video breakdown > wiki), so CALIBRATION-grade. Sibling to
`elemen-battle-actions` (the 7 Disciplines of War/Magic); same pipeline and
cross-check method.

## Scope (what was harvested)

The 11 non-combat classes' final-1.x action pages:

- Hand: `class/action/~patch2.00_{Carpenter,Blacksmith,Armorer,Goldsmith,Leatherworker,Weaver,Alchemist,Culinarian}.html`
- Land: `class/action/~patch2.00_{Miner,Botanist,Fisher}.html`

`~patch2.00` is the site's forward-facing label; the content is the final 1.x
state at the 2012-11-11 world-down (patch 1.23b), not ARR - same as the battle
set. The older `~patch1.20` / `~patch1.22` snapshots are out of scope.

Each page has two sections: **アクション** (general equippable actions - Throw,
sling, and the non-combat utility set) and **ゴッドセンド** (the crafting /
gathering abilities themselves, e.g. Hasty Hand, Grandmastery, Sharp Vision).

## Best tables (unique value)

- `derived/craft-gather-actions.csv` - 167 rows (120 distinct names; abilities
  listed on more than one class page repeat, faithfully). Columns: discipline
  (hand/land), class, section, name (JP + client EN), `client_command_id`,
  level, TP, cast, recast, duration, equip-condition, description.
  - ゴッドセンド rows (92) carry **level + equip-condition + description** (the
    ability's page has no TP/cast columns - those cells are empty).
  - アクション rows (75) carry the full level/TP/cast/recast/duration set.

The client (`xtx_command.csv`) ships the ability **names and descriptions** as
primary evidence; this set's web-unique value is the **level learned**, the
**equip-condition grouping** (which discipline/class each ability belongs to),
and the アクション metadata. Wiki tier - CALIBRATION-grade until corroborated by
a `command.csv` decode.

## Client cross-check (xivl-client-data)

Every EN is the client string, joined on the verbatim JP against
`xivl-client-data/csv/xtx_command.csv` (JP col2 -> EN col3, id col0),
NFKC-normalized. **167/167 rows resolve to a client EN; zero authored `(?)`,
zero misses.** The DoH/DoL abilities live in the client's `29xxx` command range
(crafting `295xx`, gathering `297xx`); the general アクション actions are the
shared `22xxx` rows (Throw 22113, Stone Throw 22114).

Per-class id assignment used the same rule as the battle set (sort sharing
classes into canonical id order, zip to sorted `>=27000` candidate ids, never
first-wins), but here it was a no-op: the crafting/gathering abilities are
**shared within a discipline as a single client id** (e.g. Hasty Hand = 29502 on
every crafter page that lists it), not per-class copies, so there were **0
differing-EN twins** and **0 ambiguous picks**. Class-specific gathering
abilities (採掘専用 / 園芸専用 / 漁釣専用) each appear on one page with one id.

Client-authoritative EN the check pins down (deity/flavor names a romaji gloss
would miss): ナルザルの加護 -> **Nald'thal's Ward**, メネフィナの加護 ->
**Menphina's Ward**, 彫工の力 -> **Deep Vigor**, つぶて打ち -> **Stone Throw**.

## Gaps / caveats

- `icon` column (per-action image) not transcribed.
- ゴッドセンド abilities carry no TP/cast/recast/duration on the source page
  (crafting resource/success-rate detail lives in the description prose, not
  broken-out columns); those CSV cells are empty for ゴッドセンド rows.
- Descriptions are the site's; the client ships the authoritative JP+EN
  description - reach it via `client_command_id` in `xtx_command.csv`.
- Level values are the site's observed learn levels; wiki tier.
- No unreadable cells; no `GAP` marks were needed.

## Verdict

Confirmed as a faithful transcription (values verbatim, `<br>` collapsed in
CSV). No claim promoted to retail-confirmed. No authored EN - every EN is a
client string; the shared-ability ids are single, so no disambiguation was
needed.
