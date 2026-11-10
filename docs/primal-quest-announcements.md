# Primal quest and battle announcements

The retained Ifrit, Good King Moggle Mog XII and Garuda previews give
version-qualified level and party design targets. Ifrit also has an explicit
quest progression statement. Thornmarch has quest and group-battle framing,
with an unquantified reward opportunity. These are first-party announcements
of intent, not observed admission, combat or reward settlement in 1.23b.

## Sources and locators

All three members belong to `lodestone-dev-patch`, class `web-tables`, tier 3.
The [source manifest](../sources/lodestone-dev-patch/manifest.yaml) owns their
byte sizes and SHA-256 values. The
[page inventory](../studies/lodestone-dev-patch/derived/file-inventory.csv)
owns their dates and original URLs. Member paths below are relative to the
source's restricted `objects/pages/` storage.

Member identities use the source manifest at `xivl-captures` revision
`4198118da10c4888c1523796f62a62551d1ce0d8`.

| Key | Original post and publication date | Explicit target patch | Retained member |
| --- | --- | --- | --- |
| I | [Ifrit Is Come!](http://lodestone.finalfantasyxiv.com/pl/topics/detail?id=d4986128a7ff000ce85d048a02baf5de2a876b43), 2011-10-04 | 1.19 | `ifrit-2011-10-04.md` |
| M | [Good King Moggle Mog XII Cometh!](http://lodestone.finalfantasyxiv.com/pl/topics/detail?id=00e41bb8c3107ca7189ae95eee233e750c07c9f8), 2011-12-12 | 1.20 | `good-king-moggle-mog-2011-12-12.md` |
| G | [Garuda, Ruler of the Skies!](http://lodestone.finalfantasyxiv.com/pl/topics/detail?id=2db6ff94d8971fb061085efefc0bcefe4ae333c8), 2012-04-24 | 1.22 | `garuda-2012-04-24.md` |

The opening paragraph means the first prose paragraph after the repeated
title/date line. Section paragraph numbers count prose paragraphs after the
named heading. These locators refer to the retained Markdown transcription,
whose [study](../studies/lodestone-dev-patch/README.md) explains its source
and announced-intent limits.

## Announced level and party framing

| Post locator | Encounter as described | Announced design target |
| --- | --- | --- |
| I, opening paragraph | Standard Ifrit battle | Level 30 light parties, four members. |
| I, opening paragraph | Ifrit hard mode | Designed with level 50 full parties, eight members, in mind. |
| M, opening paragraph | Good King Moggle Mog XII | Level 50 adventurers in groups of eight. |
| G, opening paragraph | Standard Garuda battle | Level 45 full parties, eight members. |
| G, opening paragraph | Garuda hard mode | Designed with level 50 full parties, eight members, in mind. |

These previews describe the intended audience and party form. They do not
provide a complete admission policy or identify the server checks enforcing
it. In particular, the Garuda preview's level 45/eight standard design target
must remain distinct from the later patch 1.22 announcement's level 40+
and four-to-eight admission rules. Its level 50/eight Hard design target
likewise differs from that announcement's level 45+/eight admission rules.
The [published Garuda admission finding](../studies/official-1x-battle-patches/derived/evidence-map.md#garuda-admission-and-aerial-blast-announcements)
owns those later rules, quests, reentry waits, reward conditions and the
separate 1.22a changes. The previews do not replace or reconcile them into
one level requirement.

## Quest, battle and reward statements

I's opening paragraph says both Ifrit encounters will take the form of
quests. Under `The Bowl of Embers (Hard)`, paragraph 1 gives adventurers who
defeat Ifrit at the first quest's conclusion the opportunity to fight a
stronger version. It promises spoils and powerful gear for overcoming that
version. This supplies an announced first-quest victory to harder-battle
opportunity relationship, without a named quest, repeatability rule or
Extreme encounter. The `Primal Weapons` paragraph describes Ifrit-themed
arms but supplies no item identities, quantities or acquisition transaction.

M's `Thornmarch`, paragraph 1 places the explanation for the confrontation
in a quest. Paragraph 2 says the king fights accompanied by moogle warriors
and offers a chance at rewards beyond that battle. This is group-battle and
reward framing. It supplies no warrior count, court defeat/revival sequence,
king-entry trigger, reward odds or settlement rule. The later
[Thornmarch bug-fix announcements](../studies/official-1x-battle-patches/derived/evidence-map.md#thornmarch-bug-fix-announcements-in-120a)
remain separate, patch 1.20a statements.

G's retained `The Howling Eye (Hard)` and `Garuda Weapons` sections contain
headings without body text. This post supplies no quest title, progression
prerequisite or reward rule. A heading alone does not establish those fields
or a combat phase.

## Relation to client findings and runtime limits

The design targets, Ifrit progression and Thornmarch framing above add
distinct preview statements to the existing findings. Later patch rules and
client identities retain their existing owners:

- `xivl-client-scripts:docs/primal-entry-client-contract.md`, Generic question
  and answer and Search boundary and missing join, owns the generic entry
  question and unresolved ordinary Garuda/Moogle admission binding.
- `xivl-client-scripts:docs/instance-entry-client-contracts.md`, Variant
  identities and unresolved admission fields, distinguishes Ifrit ordinary,
  Hard and Extreme and preserves the missing entry-side Hard selection.
- `xivl-client-data:docs/grand-company-quest-identities.md`, Shared classes,
  owns the static It Kills with Fire and In for Garuda Wakening title/class
  relationships.

Neither the preview titles nor these static identities select a historical
engine variant or bind an actor, Director, command, model state or phase.
Thornmarch remains its separately named battle. Accepted entry, HP thresholds,
phase transitions, court ordering, reset and actual reward settlement require
attributable runtime evidence beyond these three announcements.
