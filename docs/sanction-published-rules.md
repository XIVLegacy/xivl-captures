# Published Sanction rules

The official Grand Company Guide describes Sanction as a temporary enhancement
for qualifying gear. It states eligibility, a real-time lifetime, loss of
benefits on KO, and an exception to the ordinary company restriction. These
are first-party documented rules, not observed 1.23b execution.

## Source identity and scope

The retained [Grand Company Guide](http://lodestone.finalfantasyxiv.com/pl/guide/cont01.html)
is inventory row `grand-company-guide` in the
[per-page inventory](../studies/lodestone-manual/derived/file-inventory.csv),
which records its original URL, 3160 words and 9 images. The
[source manifest](../sources/lodestone-manual/manifest.yaml) pins member
`sources/lodestone-manual/objects/pages/grand-company-guide.md` at 19212 bytes,
SHA-256 `daec7989504db2c4cbf289c8ce496ce417a2eb33ea6c1021ad19be25e52a5b2a`.
Its 2015-01-08 snapshot records preservation, not a selected patch or proof
that these rules shipped in 1.23b.

The source and [study](../studies/lodestone-manual/README.md) retain evidence
class `web-tables`, tier 3. The first-party manual establishes documented
intent. Packet and video observations take precedence for actual runtime
behavior. Only "Receiving Sanction," lines 303-321 of the pinned Markdown
member, supports the findings below. Its images and other sections are not
used. Sentence numbers refer to prose sentences within the cited line.

## Documented rules

| Subject | Explicit manual rule | Manual locator |
| --- | --- | --- |
| Effect | Sanction is enhancing magic that temporarily grants bonuses to certain gear. | Line 305, sentence 1 |
| Eligibility and provider | Players of chief sergeant rank or higher can receive Sanction by speaking with arcane engineer NPCs in Grand Company offices. | Line 305, sentence 2 |
| Lifetime | Sanction status lasts 3 hours in real time. | Line 305, sentence 3 |
| KO | A player who is KO'd loses all Sanction benefits. This wording describes benefit loss, without specifying the status or icon transition. | Line 305, sentence 4 |
| Equipment qualification | Activating Sanction's benefits requires equipping gear that provides Sanction bonuses. | Line 305, sentence 5 |
| Gear acquisition | That gear can be obtained in exchange for company seals. This statement concerns gear acquisition. | Line 305, sentence 6 |
| Ordinary company restriction | Ordinarily, an adventurer receives Sanction only from the NPC representing their own Grand Company. | Line 321, sentence 1 |
| Company exception | Completing any of the Don't Hate the Messenger quests permits receipt from a Grand Company outside the player's affiliation. The exception concerns company affiliation; the sentence gives no separate rank rule. | Line 321, sentence 2 |

The section lists the following names and locations. These are the manual's
published provider descriptions, not actor-class or historical placement binds.

| Location in manual | Named provider | Manual locator |
| --- | --- | --- |
| Maelstrom Command, Limsa Lominsa | Storm Private Klinmoersyn | Lines 309 and 311 |
| Adders' Nest, Gridania | Serpent Private Ganathain | Lines 313 and 315 |
| Hall of Flames, Ul'dah | Flame Private Pakipo Tabkipo | Lines 317 and 319 |

The section states no numeric service fee or scroll rule. It does not identify
bonus magnitudes, a complete equipment list, quest IDs or a runtime quest-flag
mapping. Its company-seal sentence concerns acquiring gear.

## Relationship to client evidence

These separate publications own the client findings:

- [CompanyBuffer's conditional 180-minute explanation](https://github.com/XIVLegacy/xivl-client-scripts/blob/051a57ef59323faf3e8f6a5ead6bb8a4d0383179/docs/sanction-company-buffer-contract.md#conditional-180-minute-explanation)
  explains how the supplied dialogue value can compose with minutes wording.
  The manual independently states the intended 3-hour lifetime. Agreement
  does not prove that either route applied that duration.
- [The status base contract](https://github.com/XIVLegacy/xivl-client-scripts/blob/daf704b2941991e64a01aa1dd4bbba4b47d6ae16/docs/sanction-status-base-contract.md#conditional-sanction-composition)
  preserves the conditional base-life query and default death predicate.
  The separate raw value `10800` has no established runtime unit or applied
  duration. Raw blank cells at columns 48 and 49 remain distinct from `0`
  and `-1`. Neither the manual nor that predicate proves actual status removal.
- [The static-row finding](https://github.com/XIVLegacy/xivl-client-data/blob/e37ce5ef10d189f471458305e2482dbedec4291c/docs/sanction-static-rows.md)
  owns the rank labels, equipment-condition label and separate scroll identity.
  Authored scroll use intent establishes neither item consumption nor status
  application. Static scroll offers do not price the NPC service.

The manual supplies first-party intent for eligibility, timing and gear use.
It does not demonstrate an actual grant, expiry, death removal, seal debit,
equipped-stat application or equivalence between the service and a scroll.
