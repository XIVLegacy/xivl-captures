# Mob drops, crystal gating, and party loot evidence

This document records what retained evidence establishes about per-mob item
associations, quantities and rates; crystal class or level gates; and shared
party loot, admission, rolls, passes and settlement. Static client facts,
observed wire carriers, documented intent and historical wiki associations
retain their separate evidence limits.

Confidence is claim-specific:

- **A**: directly authenticated retail artifact fact. Static client facts and
  observed wire facts are identified as such.
- **B**: first-party historical documented intent.
- **C**: historical community or wiki claim.
- **U**: unproved by the retained evidence.

## Consumer promotion

| Finding | Verdict | Confidence | What can be promoted |
| --- | --- | --- | --- |
| Ordinary per-mob item associations | Historical associations; no 1.23b rate table | C | GamerEscape has 897 nonempty `drops` cells among 1,501 rows; line 15 lists Aldgoat Billy with Aldgoat Skin, Aldgoat Chuck, Straw and Salt Leek. These are drifting 1.x wiki associations, not 1.23b kill proof, quantities or rates. The 65 retained regular eLeMeN pages separately have zero ordinary rows (`xivl-captures:studies/gamerescape-tables/derived/mob-locations.csv:1,15`, `xivl-captures:studies/elemen-bestiary/README.md:121-132`). |
| NM item associations | Associations only | C | The retained eLeMeN table has 84 rows for 35 NMs, preserving item names, client item joins, shared source groups and site rarity marks. It has no quantity or probability columns (`xivl-captures:studies/elemen-bestiary/derived/evidence-map.md:13-18`, `xivl-captures:studies/elemen-bestiary/derived/evidence-map.md:140-150`). |
| Crystal, shard and cluster identities | Item identity only | A | The 1.23b retail inventory cross-check matches observed item IDs to the client catalog. IDs 1000003-1000008 are shards, 1000009-1000014 are crystals, and 1000015-1000020 are clusters. This does not establish a mob source, quantity per kill or rate. |
| Crystal element priority | Historical observation only | C | eLeMeN records a crystal drop-priority order by genus, but the study explicitly says it is not an item-ID mapping or probability. |
| Crystal class or level gate | No retail gate | U | No retained retail source ties a crystal drop to player class, player level, mob level, or a numeric threshold. The Lodestone only documents an entitlement/low-level EXP condition, not a crystal-specific rule. |
| Party entitlement and loot-list intent | Documented intent | B | The first attacker or party is entitled; party spoils are distributed randomly to each member's loot list and later move to inventory. |
| Shared lot admission | Unproved | U | No retained retail source establishes exact admission predicates for a shared lot. |
| Roll, pass and settlement | Unproved | U | The retained retail manual, packets and client command contract do not establish the roll/pass state machine, winner selection, timeout, cancellation or final settlement. |

The eLeMeN zero-row result is a boundary of that retained
source, while GamerEscape's nonempty drops cells are C-level historical
associations; neither supports a global retail-absence claim.

## Retail drop-list evidence

### Per-mob associations

The eLeMeN study is a historical wiki-tier source. Its README says that its
unique fields are observation-only, including crystal drop-priority order,
and that a value alone supports calibration rather than a retail-confirmed
server value (`xivl-captures:studies/elemen-bestiary/README.md:51-56`).

Its canonical evidence map says the NM table has 84 rows. Each row preserves
the item name, exact client item join, site rarity glyph and `drop_group`; a
shared group means items were printed on the same source line. The map names
no quantity or chance field (`xivl-captures:studies/elemen-bestiary/derived/evidence-map.md:140-150`).
The CSV header itself has `drop_group`, `rarity_mark`, item fields and a
source, but no quantity or probability column
(`xivl-captures:studies/elemen-bestiary/derived/mob-drops.csv:1`).

The regular-page boundary is narrower than a retail absence claim. The 65
retained regular pages cover 112 mapped species, contain no ordinary-item
drop list or level band, and produce zero rows in `species-drops.csv`; the
evidence map explicitly says this does not assert that ordinary species drop
no items in retail (`xivl-captures:studies/elemen-bestiary/README.md:121-132`,
`xivl-captures:studies/elemen-bestiary/derived/evidence-map.md:165-177`).
The pinned accounting artifact states the same boundary: no ordinary item
rows, level bands, item IDs, drop groups, rarity marks or rates, and no
crystal item-ID mapping or probability
(`xivl-captures:studies/elemen-bestiary/derived/species-drop-accounting.json:341`).

GamerEscape adds historical ordinary-drop associations as well as location
rows and mob fields, but does not close the retail gap. The retained CSV has
1,501 rows and 897 nonempty `drops` cells; its example row lists Aldgoat
Billy with Aldgoat Skin, Aldgoat Chuck, Straw and Salt Leek
(`xivl-captures:studies/gamerescape-tables/derived/mob-locations.csv:1,15`).
Its evidence map describes a 1.x aggregate that drifted late in the era, not
a 1.23b snapshot, and states that these are printed fields without
interpolation or rate recovery
(`xivl-captures:studies/gamerescape-tables/derived/evidence-map.md:7-20`,
`xivl-captures:studies/gamerescape-tables/derived/evidence-map.md:23-35`,
`xivl-captures:studies/gamerescape-tables/derived/evidence-map.md:73-84`).
Its mob level fields and `drops_no_shards`/`drops_no_crystals` booleans are
historical wiki values, not a retail probability table
(`xivl-captures:studies/gamerescape-tables/derived/evidence-map.md:88-93`,
`xivl-captures:studies/gamerescape-tables/derived/evidence-map.md:213-223`).

Therefore the retained evidence supports C-level historical ordinary and NM
item associations, plus A-level observed item identities. It does not support
a 1.23b per-mob kill association, quantity, chance, independent-roll count
or shared-drop-group probability; the GamerEscape rows are useful candidates,
not calibrated retail values.

### Crystal identity and gating

The static client catalog and observed retail wire agree on the crystal
family's item identity. The inventory cross-check parsed 481 observations
from 53 captures and matched all 69 observed IDs to the client item, name and
data tables (`xivl-client-data:docs/inventory-cross-check.md:3-23`). It
lists shard IDs 1000003-1000008, crystal IDs 1000009-1000014 and cluster IDs
1000015-1000020, all in the `Money/MoneyStandard` category with max stack
9999 (`xivl-client-data:docs/inventory-cross-check.md:42-70`). This is an A
catalog and wire identity finding. The sample quantities in that ledger are
inventory observations, not quantities granted by a mob kill.

The eLeMeN crystal-priority notes remain C-level historical observations.
The study says the priority order is not corroborated by packet or direct
observation and is not a retail-confirmed drop table
(`xivl-captures:studies/elemen-bestiary/README.md:148-154`). Its accounting
artifact further states that crystal priority is not an item-ID mapping or
drop probability (`xivl-captures:studies/elemen-bestiary/derived/species-drop-accounting.json:341`).

The Lodestone manual establishes an entitlement rule, not a crystal gate.
The first character or party to attack is entitled to experience, items and
loot, while attacking an already claimed enemy gives no entitlement; the
manual also says a lower-level enemy may give no EXP
(`xivl-captures:sources/lodestone-manual/objects/pages/battle-and-being-ko.md:89-95`).
It does not say that crystal eligibility uses player class, player level,
mob level, an element, or a numeric drop threshold. Thus the retail answer
for class and level gating remains U.

## Retail party-loot evidence

The strongest retained source is the first-party Lodestone manual. It says
that party spoils are distributed randomly to the loot lists of each member,
then move automatically to inventory after a period; a full inventory loses
the items. Before inventory transfer, loot-list items are not possession and
can be transferred to another party member's list, including rare and unique
items (`xivl-captures:sources/lodestone-manual/objects/pages/battle-and-being-ko.md:135-147`).
This supports B-level documented intent for entitlement, random per-member
loot lists, delayed inventory transfer and pre-inventory transfer. It does
not name a lot/pass/roll UI, define a common pending-drop pool, select a
winner, or describe timeout, cancellation, or settlement.

The public `party_battle_leve.pcapng` scenario retains clientbound inventory
opcode observations: 0x0146 and 0x0147 at 40 bytes, 0x0148 at 144 bytes, and
0x016e at 40 bytes (`xivl-captures:catalog/scenarios/battlecraft-leve-accept-and-complete/evidence-map.md:69-81`).
The public payload sample for s2c 0x0146 includes this capture id at
`xivl-captures:derived/payload_samples.json:6833`. The scenario map says
these products establish opcode identity and framing; decoded field
semantics live in derived payload products
(`xivl-captures:catalog/scenarios/battlecraft-leve-accept-and-complete/evidence-map.md:104-111`).
Accordingly, the capture proves that inventory-related wire carriers were
observed in this retail scenario, but it does not prove a lot entry, a roll
choice, a pass choice, or a settlement result.

The static client UI contract supplies a related but narrower A finding. The
loot-list route reads package 5 and calls helper command IDs 24223, 24225 and
24226 for move, transfer and waste paths (`xivl-client-scripts:docs/loot-item-ui-contract.md:1-21`).
The contract explicitly warns that these are client-side arguments rather
than recovered wire payloads or server effects, and that package 5 is not
shown to be a global server inventory alias
(`xivl-client-scripts:docs/loot-item-ui-contract.md:23-26`). The command
table identifies the three command classes (`xivl-client-scripts:docs/loot-item-ui-contract.md:42-44`).
The retained conditional 0x012D request representation does not join any of
these commands to a pending-drop identity, ownership change, cancellation or
settlement; the contract explicitly says these routes do not establish a
lot/pass protocol (`xivl-client-scripts:docs/loot-item-ui-contract.md:79-108`).

### Selected package-4 item publication bracket

The retained `pcap-1.23b` member `party_battle_leve.pcapng` contains one
selected full item record for native/wire package `4`, capacity `10`, slot
`0`, catalog item `10006111` (`0x0098AE5F`), quantity `1`, with item-record
identity `0x0000000008368B13`. This is an A-level observed wire fact,
`packet-capture`, tier 1. Native package and slot numbering convert to Lua
package `5` and slot `1`. This binds the received package number to the
number read by the loot-list UI; it does not identify a mob source, grant
event, shared lot, owner transition or successful inventory transfer.

The source identity is
[`sources/pcap-1.23b/manifest.yaml`](../sources/pcap-1.23b/manifest.yaml),
member `party_battle_leve.pcapng`, `1429864` bytes, SHA-256
`6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f`.
The authenticated archive is `pcap-1.23b-objects.zip`, `2622720` bytes,
SHA-256 `20a78b9f40ff2393037c9a160c957783cf590b4f01797493d22fcd2039e9cbff`,
pinned by [`config/retail_inputs.json`](../config/retail_inputs.json).

The four records share transport source and target within main lane `0`,
s2c frame `1733`, at directional stream offset `212115`. The outer frame
is `100` bytes and inflates to a `304`-byte body. Lane, frame, subevent and
body offsets below are zero-based. Capture packet `3013` is one-based and
is the earliest captured packet completing all bytes of this outer frame.
It is a capture-completion locator, not a client execution timestamp.

| Subevent | Inflated body offset | Sub-event bytes | Opcode |
| --- | --- | --- | --- |
| `1` | `40` | `40` | `0x0146` |
| `2` | `80` | `144` | `0x0148` |
| `3` | `224` | `40` | `_0x0147` |
| `4` | `264` | `40` | `0x016E` |

The selected order is `0x0146 -> 0x0148 -> _0x0147 -> 0x016E`.
The only additional inspected neighbor is same-frame subevent `0`,
`0x016D`, immediately before it. This is order within one reconstructed
connection and direction, not an aggregate motif or a cross-connection
chronology. `_0x0147` retains its adopted placeholder and has no assigned
package-end or settlement effect here.

For these wrapped records, the 16-byte sub-event header precedes the
16-byte game-message prefix: an 8-byte inner header followed by an 8-byte
preamble. Application offset `+0` is therefore sub-event offset `+32`,
or `sub_body +16` in the extractors. The `0x0148` application is one
`0x70`-byte item record. These little-endian fields are the selected decode:

| Record | Application offset | Field | Value |
| --- | --- | --- | --- |
| `0x0146` | `+0x00`, u32 | Package actor | Equals the transport source actor; identifier omitted |
| `0x0146` | `+0x04`, u16 | Capacity | `10` |
| `0x0146` | `+0x06`, u8 | Native/wire package | `4` |
| `0x0148` | `+0x00`, u64 | Item-record identity, named `uniqueId` by the extractor | `0x0000000008368B13` |
| `0x0148` | `+0x08`, s32 | Quantity | `1` |
| `0x0148` | `+0x0C`, u32 | Catalog item ID | `10006111` / `0x0098AE5F` |
| `0x0148` | `+0x10`, u16 | Native slot | `0` |

The package field is one byte, not a dword. No semantics are assigned to
`0x0146` application `+7`. The eight-byte item-record identity is not a
catalog ID, a proven globally unique instance ID or a request discriminator.
Field layout and index conversion use
`xivl-client-structs:manifests/inventory_subsystem.json`,
`supporting_record_classes.InventoryItem`, and
`xivl-client-structs:docs/bazaar-native-wire-contract.md#package-and-slot-numbering`
at revision `b144a3c8a816516c6fb759bf0011e38587276705`.

The shared receive contract queues package selection before the item and
queues End at `0x016E`. End execution integrates staged packages and
publishes changed-slot callbacks when materialization is ready, or queues
a continuation otherwise
(`xivl-client-structs:docs/bazaar-native-wire-contract.md#incoming-package-operations-and-publication`,
same revision). Thus this bracket supplies the captured package/item/End
inputs to that publication path. It does not observe execution, callback
delivery, widget refresh or completion of a deferred continuation. The
first unbound causal edge is the request or source event that produced
this bracket. No request-to-item or ownership/outcome join is established.
Quantity `1` is a received record value, not a kill-drop quantity policy.

Reproduction used captures revision
`4421307fc41c0c4790f091426b3331112e075a3e`, Python `3.12.0` and Scapy
`2.7.0`. Only the named archive member was read into `BytesIO`, authenticated,
and passed to `scapy.rdpcap`. Its packets seeded the exact resolved member
path in `extract_streams.read_packets`' cache before calling
`tools/validate_framing.py:check` and
`tools/extractors/extract_00da_00e1_comparison.py:_decode_capture`.
This was an in-memory input adaptation, not a CLI run against a materialized
input. No raw file was written, and the existing local cache file was not
read. Fields were checked with
`tools/extractors/extract_content_samples.py:parse_inventory_items` and
`tools/extractors/extract_equipment_property_correlation.py:_parse_item_rows`.
Framing reported zero compression mismatches. The decoder reported zero
admitted unparsed bytes and sub-event truncations, while trimming six s2c
bytes after the last complete frame. That tail is outside this complete
selected frame. No other capture or causal neighborhood was interpreted.

## Explicit evidence gaps

The retained evidence leaves these mechanics open:

1. No retail-authenticated per-mob ordinary drop list joins a mob identity to
   an item, quantity and rate.
2. No retail-authenticated source gives a crystal shard/crystal/cluster
   quantity or probability by mob, genus, element, mob level, player level or
   player class.
3. The client catalog proves crystal item identity, not the source event that
   granted an item. Inventory sample quantities are not kill-drop quantities.
4. Lodestone establishes random per-member loot-list distribution and delayed
   transfer, but not lot/pass/roll UI, candidate admission, winner selection,
   timeout, cancellation or settlement.
5. The public packet products identify inventory-related carriers and a
   `party_battle_leve.pcapng` sample, but the retained decoded products do not
   assign those carriers to a lot entry or a loot outcome.
