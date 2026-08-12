# eLeMeN FF14 1.x Food and Medicine Effect Magnitudes - Web Tables

The web-unique slice of the eLeMeN - FF14 (`elemen.sakura.ne.jp`) `etc/food`
(食事効果) and `etc/medicine` (薬品効果) sections: the **per-item effect
magnitude specifications** for 1.x food and medicine. A client-first recon found
item names, category, effect duration, and recast time client-primary
(`xtx_itemName`, `itemData`), and the effect magnitudes - percentage/cap stat
buffs, recovery formulas, buff/debuff status specs - absent from any decoded
client sheet. Those magnitudes are the payload. They are server-side tuning.

## Study contents

- `derived/food-effects.csv` - 108 food items across 10 food-type groups. Each
  row: group (food type) + category (primary stat), item (JP + client id/EN),
  `effect_jp` (verbatim per-attribute `attr:+X%(cap Y)` spec), `effect_en`
  (gloss), and recast/duration (site value + client `itemData` value).
- `derived/medicine-effects.csv` - 66 medicine items across 5 groups (Recovery,
  Remedy, Restorative, Poison, Elixir). Same schema. Effects cover HP/MP recovery
  `+X%(cap Y)`, status cures/debuffs, self-buff `stat:+X%(cap Y)`, enmity deltas,
  Protect/Shell grants, and raises.
- `derived/glossary.md` - every attribute token (28) and status token (8) mapped
  to its client param/status string + id. The site supplies fixed phrases.
- `derived/evidence-map.md` - client-first verdict, cross-check results, and the
  one cross-source contradiction (status-cure recast).

## Start here

- `derived/evidence-map.md` - the reasoning, cross-check, and caveats.
- `derived/food-effects.csv` + `derived/medicine-effects.csv` - the data.

## Source material

- `sources/elemen-consumable-effects/objects/pages/food-effects.md`, `medicine-effects.md` - verbatim
  transcription incl. the universal-rule page notes (EXP +3%, 30:00, HQ +10%).
- Source HTML - preserved verbatim in the `elemen-site-archive` set; see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping.

## Promoted conclusions

`derived/food-effects.csv` and `derived/medicine-effects.csv` have been consumed
by downstream reference work and are named calibration inputs for item-use and
status-effect work. Their effect magnitudes remain CALIBRATION-grade.

## Topics

- Food buff formula: `attribute:+X%(cap Y)`, 1-3 attributes per dish; universal
  EXP +3%, 30:00 duration, 0:05 recast, HQ +10%.
- Medicine: %-of-max HP/MP recovery with caps; status cure/debuff items; stat
  potions/tonics/elixirs (薬/妙薬/秘薬 tiers) with per-tier caps; enmity items;
  Protect/Shell; phoenix-down raises.
- Client cross-check: 174/174 items, 28 attribute + 8 status tokens all resolved.

## Evidence gaps

- Effect magnitudes are uncheckable against the client (server-side). Wiki tier,
  CALIBRATION-grade.
- 9 status-cure recasts contradict the client (client authoritative). See
  evidence-map. Signals some page values pre-date 1.23b.
- HQ magnitudes (NQ x 1.10) not transcribed; the +10% rule is recorded instead.

## Further research

- Effect magnitudes remain uncorroborated against pcap or client evidence and are
  not retail-confirmed.
- The status ids can be cross-referenced with `status-effect-mechanic` pcap
  evidence.
