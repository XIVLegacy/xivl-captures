# eLeMeN FF14 1.x Shop Item-to-NPC Sales Edges - Web Tables

The one web-unique slice of the eLeMeN - FF14 (`elemen.sakura.ne.jp`)
`etc/shopitem/` section: the **item <-> selling-NPC sales edges** - which named
NPC stocks which item. A client-first comparison found the item names and flat prices
client-primary and the NPC roster already covered by `elemen-zone-guide`; the
edge is the piece the client does not carry in decoded form.

## Study contents

- `derived/shop-sales.csv` - 2,087 item<->seller edges (518 items x their
  sellers, 154 distinct NPCs). Each row: item (JP + client EN + id), seller NPC
  (JP + client EN + id), seller city/region + area + coords, and the source's
  verbatim price string.
- `derived/glossary.md`, `derived/evidence-map.md`.

## Source material

- `sources/elemen-shop-inventory/objects/pages/shop-sales.md` - the item -> price + seller-list
  transcription, verbatim.
- Source HTML + `db_shop.js` - preserved verbatim in the `elemen-site-archive`
  set (the item->NPC data lives in the JS, not the page); see its
  `derived/url-map.csv` for the archive-path -> source-URL mapping. This set
  carries no HTML of its own, per the eLeMeN intake rule.

### Client-first tiering (why just the edges)

Check `xivl-client-data` FIRST. Dropped as client-primary: item names
(`xtx_itemName.csv`), flat gil prices (`shopItem.csv`), and the seller roster
(already in `elemen-zone-guide/derived/shops.csv`). Kept: the **item<->NPC
edges** - the client has `shopBase` -> `shopItem` (inventory + price) and
`xtx_itemName`, but the binding from a *named NPC* to a `shopBase` is not in any
decoded client sheet (it lives in the actor-behavior binary). Also kept verbatim:
the **15 rank-scaled hamlet prices** (`備蓄ランク0/1/2`), which are not flat
`shopItem.csv` values. Full reasoning and join stats in `derived/evidence-map.md`.

Evidence tier: **wiki** (packet captures > video breakdown > wiki) -
CALIBRATION-grade until corroborated by packet/client evidence.

## Promoted conclusions

`derived/shop-sales.csv` supplies item-to-seller edges to downstream reference
work and is the named input for Grand Company shop wiring. It combines with
`elemen-zone-guide` placement and client shop tables to reconstruct inventories.

## Start here

- `derived/evidence-map.md` - client-first scoping, the client cross-check, the
  variant overrides, the one gap.
- `derived/shop-sales.csv`, `derived/glossary.md`.
- `manifest.yaml` `sources` - the section URL + `db_shop.js` + retrieval date.

## Source note (edition)

`etc/shopitem` is annotated ※パッチ1.22対応 - one patch before the 2012-11-11
(patch 1.23b) world-down. Treat as 1.22 evidence. The item/NPC joins to the 1.x
client tables confirm the era.

## Related evidence

- Pairs with `elemen-zone-guide` (shop NPC roster + coords) and the client
  `shopBase`/`shopItem` tables: NPC roster (zone-guide) + item<->NPC edge (here)
  + shopBase inventory/price (client) together reconstruct the full shop wiring.
## Topics

- 2,087 item<->NPC sales edges; 518 items all joined to `xtx_itemName`; 154
  sellers joined to `xtx_displayName`.
- 15 rank-scaled hamlet prices (`備蓄ランク`) - stockpile-rank-scaled economy not
  in flat client price data.

## Evidence gaps

- `酒保商人フォルガード` (Coerthas) not in `xtx_displayName` (removed/renamed camp
  NPC) - 11 edges carry the JP name with a blank client id.
- Flat prices (503 items) duplicate `shopItem.csv`. They are kept only as verbatim source
  annotation.
- Patch 1.22, not the 1.23b final.
- Placement coords are the source's player-map X/Y (observation), wiki tier.

## Further research

- Specific item<->NPC edges and the 15 rank-scaled prices need packet/client
  corroboration before retail confirmation.
