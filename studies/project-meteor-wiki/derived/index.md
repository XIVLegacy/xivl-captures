# Project Meteor wiki - reverse-engineering residual

> Use the stable source-object citations below to locate this study's evidence.

Three reverse-engineering / design-notes pages from the Project Meteor (FFXIV
Classic, fragmenterworks) wiki remain as additive evidence. The wiki's opcode
series, quest/lore pages, and ID/model tables are covered better elsewhere in the
XIVLegacy research repositories.

## Pages

| page | what it carries |
|------|-----------------|
| math-formula.md (`sources/project-meteor-wiki/objects/pages/math-formula.md`) | Server-side command MP-cost formula (full 8-band level scaling + base-cost sample) and the scaled quest-XP reward formula, both in Lua. |
| animations-and-vfx.md (`sources/project-meteor-wiki/objects/pages/animations-and-vfx.md`) | The `animationId` 32-bit packing (VFX Number / Animation Number / VFX Category) and the animation-folder + VFX-category taxonomies. |
| retail-patcher-and-login.md (`sources/project-meteor-wiki/objects/pages/retail-patcher-and-login.md`) | Retail boot chain: version-check HTTP protocol, BitTorrent `SqexPatchSystem` handshake, `rsa_verify` bypass, and the `ffxivlogin` string obfuscation. |

## Provenance

Per-page source URL, revision id, and timestamp are in
[file-inventory.csv](file-inventory.csv) and the manifest `sources` list. Base
wiki: `http://ffxivclassic.fragmenterworks.com/wiki`.

## Evidence tier

Wiki tier, CALIBRATION-grade (packet captures > video breakdown > wiki). The
source wiki states no license; facts and formula values are paraphrased into our
own words, no third-party prose is transcribed verbatim. See
[evidence-map.md](evidence-map.md) for the additive-vs-redundant call on every
candidate page.
