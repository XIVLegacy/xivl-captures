# Project Meteor Wiki - RE Residual

> Use the stable source-object citations below to locate this study's evidence.

## Study contents

Three reverse-engineering / design-notes pages salvaged from the Project Meteor
(FFXIV Classic, fragmenterworks) wiki: the server-side command MP-cost and
quest-XP formulas, the client `animationId` bit packing plus animation/VFX
folder taxonomies, and the retail boot chain (version-check protocol, BitTorrent
patch handshake, `rsa_verify` bypass, `ffxivlogin` string obfuscation).

The source export was 316 pages. The other 313 were dropped as already covered
better in the XIVLegacy research repositories. The
per-page keep/drop reasoning is in [derived/evidence-map.md](derived/evidence-map.md).

**Evidence tier.** Wiki, CALIBRATION-grade (packet captures > video breakdown >
wiki). The source wiki states no license, so facts and formula values are
paraphrased into our own words and no third-party prose is transcribed verbatim.
Values taken only from here are calibration inputs, not runtime-confirmed. This
is the evidence layer.

## Start here

- [derived/index.md](derived/index.md) - one-line map of the three pages.
- [derived/evidence-map.md](derived/evidence-map.md) - additive-vs-redundant call
  on every candidate page, plus gaps.

## Source material

- `sources/project-meteor-wiki/objects/pages/math-formula.md`
- `sources/project-meteor-wiki/objects/pages/animations-and-vfx.md`
- `sources/project-meteor-wiki/objects/pages/retail-patcher-and-login.md`

Source of record for the harvest was the public Project Meteor MediaWiki at
`http://ffxivclassic.fragmenterworks.com/wiki`. Per-page URL, revision, and
timestamp are in
[derived/file-inventory.csv](derived/file-inventory.csv) and the manifest
`sources` list.

### Tool inputs (verbatim, not paraphrased)

`sources/project-meteor-wiki/objects/tool-inputs/` holds two upstream pages kept
**verbatim** as historical data-table evidence, not as the paraphrased design
notes above:

- `0004-weather.wikitext` - the per-region weather presence table, retained
  verbatim as historical source evidence.
- `0181-full-quests.wikitext` - the quest ID/name/level table, the extraction
  source used at research time for an external derived quest output, which is
  not bundled here.

The quest page is the manifest's source record. Both pages remain raw evidence
rather than distilled prose.

## Promoted conclusions

The weather table remains historical raw evidence, and the quest table remains
the source record for the extracted quest catalog. The formula, animation, and
retail-boot notes remain CALIBRATION inputs.

## Topics

- Command MP cost: 8-band level scaling, per-command base costs (thousandths).
- Quest XP: `ceil(expTable[lvl] * weight/100)`.
- `animationId`: bits 0-11 VFX Number, 12-23 Animation Number, 24-31 VFX
  Category.
- Retail boot: `ver01.ffxiv.com:54996` vercheck, `SqexPatchSystem v01`,
  `rsa_verify` bypass, `sqex0002` launch arg, `ffxivlogin` 0x22AF obfuscation.

## Evidence gaps

- Formulas are the wiki author's best-fit / server values, not decompiled
  constants. The `51-60` vs `61-70` MP band discontinuity is reproduced as
  written and unverified.
- Several VFX-category rows are unlabelled in the source.

## Further research

- MP-cost bands remain uncorroborated against observed 1.23b MP costs.
- No captured animation opcode payload has yet been linked to the `animationId`
  packing.
