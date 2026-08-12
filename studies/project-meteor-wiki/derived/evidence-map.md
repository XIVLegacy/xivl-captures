# Evidence map - project-meteor-wiki

The 316-page Project Meteor wiki export at
`http://ffxivclassic.fragmenterworks.com/wiki` was screened page-by-page against
`xivl-client-data`, `xivl-client-structs`, `xivl-opcodes`, and a downstream
preservation launcher. Three paraphrased pages contain genuinely additive content;
this map records those pages and the excluded categories.

## Kept - additive RE / design notes

### math-formula.md
- **Command MP cost** - full level-banded multiplier (8 bands, `<=10` through
  `>70`) times a per-command base cost (thousandths), rounded up. A research-time
  comparison found only a truncated copy in an external GM-script source
  (`Yolo.lua`):
  `calculateCommandCost` keeps only the `>70` band and a 4-entry `commandCost`
  table. The complete bands + wider base sample are the additive value.
- **Scaled quest XP reward** - `ceil(expTable[lvl] * weight/100)`. Same
  GM-scratchpad copy exists in Yolo.lua (`calcSkillPoint`); kept here as the
  documented form with its expTable semantics.
- Confidence: the source presents these as its own best-fit / server formulas,
  not decompiled client constants. These formulas are CALIBRATION-grade;
  observed MP costs are still needed before they can be treated as runtime
  values.

### animations-and-vfx.md
- The `animationId` bit packing: bits 0-11 VFX Number, 12-23 Animation Number,
  24-31 VFX Category, over a 32-bit field.
- Animation-category folders (em1/em2/mgc/wsc/...) and the VFX-category table
  (folder name + hex + effect meaning), including the >0x20 engine-selector
  categories.
- Additive because xivl-client-structs treats `animationId` as an opaque
  `u64` payload ("single u64 (animationID)" in its action-skill catalog) and
  does not decode the packing or the folder taxonomy.

### retail-patcher-and-login.md
- Retail boot-chain RE: the `ver01.ffxiv.com:54996` version-check path/headers,
  the `SqexPatchSystem v01` BitTorrent handshake with Blowfish-encrypted
  infoHash, the `rsa_verify` bypass byte signatures, and the `ffxivlogin.exe`
  rolling-key string obfuscation (0x22AF schedule).
- Additive because a downstream preservation launcher reproduces only the parts
  it needs: its ZiPatch container reader and launch-argument handling (the
  `sqex0002` game-launch arg). The retail vercheck/torrent/RSA path and the
  `ffxivlogin` obfuscation are
  not reproduced anywhere in the stack.

## Dropped - redundant or covered better

- **ZiPatch File Structure** - fully covered by a downstream preservation
  launcher's reader, which documents the same signature and
  FHDR/APLY/APFS/ADIR/DELD/ETRY chunk layout and cross-checks the same external
  format reference. The working reader is the stronger reference.
- **Debug Commands** - Project Meteor's own GM command set; a downstream
  consumer ships its own GM scripts. The one arguably-RE part (the `graphic` appearance-slot
  -> weaponID/equipID/variantID/colorID breakdown) is the client
  equipment/appearance model array, covered by xivl-client-data
  `actorclass_graphic.csv` and the client-structs appearance surface.
- **NPC Actors** - a list of server actor class-script names; covered by
  xivl-client-data `actorclass.csv` plus the decompiled client scripts under
  `xivl-client-scripts/lua/scripts/chara/npc/` (e.g.
  `gimmick/gimmickwarp.lua`).
- **Utilities** - external tool download links only (FFXIVtool, model viewer,
  Seventh Umbral); not RE content.
- **Game Opcodes + Packet Headers series** (~100 pages) - superseded by
  `xivl-opcodes`, which is more current.
- **~150 quest / lore pages** - overlap the `xivl-client-data` quest sheets.
- **ID / model tables** (Region / Weather / Music IDs, Monster / BgObj Models,
  NPC / Populace Animation IDs) - already decoded in external client data.
- **Nav labels with no page** - "Server Flow", "Actor System" /
  "Understanding the actor system", "Event System" are red links on the wiki nav
  (no wikitext in the export). "Game Engine Specifications" is a section header,
  not a page. "Useful Utilities" resolves to the dropped Utilities page.

## Tool inputs kept verbatim

Separate from the three paraphrased pages,
`sources/project-meteor-wiki/objects/tool-inputs/` holds two upstream pages
kept **byte-for-byte** as historical data-table evidence:

- `0004-weather.wikitext` - the per-region weather presence table retained
  byte-for-byte as historical source evidence.
- `0181-full-quests.wikitext` -> external derived quest extraction target,
  consulted at research time and not bundled.

These are the only factual data-table pages retained from the whole wiki
export. Their content (weather presence grid, quest roster) is kept verbatim
and checksummed as historical evidence. The pages were dropped from the
design-notes harvest above. The weather page remains historical raw evidence;
the quest page remains the source record for its extracted catalog.

## Gaps / caveats

- Formula values are the wiki author's, not decompiled constants; the `51-60` vs
  `61-70` MP-band discontinuity is reproduced as written and is unverified.
- Several VFX-category rows are unlabelled in the source and left blank here.
- The `ffxivlogin` obfuscation is described as an algorithm (constants +
  schedule) rather than transcribed as the source's C#, per the no-license
  paraphrase rule.
