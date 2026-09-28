# Retail repair verdicts

## Evidence identity

- Client build: `2012.09.19.0001` (FFXIV 1.23b).
- Client executable SHA-256:
  `9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
- Image base: `0x00400000`.
- Capture: `sources/pcap-1.23b/objects/repair_items.pcapng`, SHA-256
  `bbd829cbd3f42b2cbfb3aa8a74a1cc35d4e2c16c99e5a4a20ca76573f02dd90f`.
- Capture provenance: owner-attested retail live-server traffic in the
  `shop-vendor-buy-sell-repair` scenario; it is not emulator traffic.

## Capture-proven NPC repair facts

All six repair confirmations arrived server-to-client on the clear map lane as
opcode `0x0130` RunEventFunction. Each subpacket was 176 bytes and each complete
application body was 152 bytes. The application-body layout observed by the
client is:

| Offset | Size | Observation |
|---|---:|---|
| `+0x00` | 8 | Opaque generic application prefix; preserved without interpretation. |
| `+0x08` | 4 | Trigger actor ID, little-endian. |
| `+0x0C` | 4 | Owner actor ID, little-endian. |
| `+0x10` | 1 | Event type. |
| `+0x11` | 32 | NUL-padded event name, `talkDefault`. |
| `+0x31` | 32 | NUL-padded function name, `confirmRepairItem`. |
| `+0x51` | 64 | Typed Lua parameter area. |
| `+0x91` | 7 | Opaque trailing bytes; preserved without interpretation. |

The confirmation parameter sequence was identical in shape for all six rows:
actor tag `0x06` plus a four-byte big-endian actor ID, followed by three tag
`0x00` four-byte big-endian integers. Joined to the client function signature,
those integers were quoted tariff `1`, the item catalog ID in the CSV, and the
observed value `1`. The last value is retained as a presentation/count argument;
the capture does not independently establish a server inventory identity for it.

Each positive answer was sent client-to-server on the same map lane as opcode
`0x012E` EventUpdate. Each subpacket was 120 bytes and each application body was
96 bytes. The accepted confirmation payload had this bounded layout:

| Offset | Size | Observation |
|---|---:|---|
| `+0x00` | 8 | Opaque generic application prefix. |
| `+0x08` | 16 | Four generic event-context dwords; meanings are not assigned here. |
| `+0x18` | 64 | Event-return data. The accepted repair specimens begin `01 03 0f`; remaining bytes are preserved as observed padding/data. |
| `+0x58` | 8 | Opaque trailer. |

After each accepted reply, the next server inventory transaction contained
opcode `0x0148` with a 144-byte subpacket and 120-byte application body. Inside
that body, the catalog ID at `+0x14` was `1000001` (Gil) and the signed quantity
at `+0x10` formed the exact sequence 1,346,697 through 1,346,692. Each update
was bracketed by `0x016D` and `0x016E`, whose application bodies were 16 bytes.
The sequence and the six quoted tariff values prove six accepted one-gil NPC
repair charges for the captured item levels 15 through 30. They do not prove
that every NPC repair in the build costs one gil.

The NPC event later received `finishTalkTurn` through s2c `0x0130` at capture
packet 250, timestamp `1356920886.160453`, decoded s2c event 405. The client
script delegates that function only to `finishCliantTalkTurn`.

## Client-contract join

The pinned Lua corpus SHA-256 is
`0e8f902f7a2f592fc1220d41b89a3f35ec395cfb261806d4bd590a530099ae31`.
The relevant script identities and locators are:

- `chara/npc/populace/populaceitemrepairer.lua`, SHA-256
  `027ac93ef6e805ee4c2197d5fa7353a0ebdff125f6d52f0d6c08bedfb5218ea3`,
  lines 683-742: confirmation/facility UI and cleanup.
- `judge/craft/craftjudge.lua`, SHA-256
  `5019a3e9acaf99a23210a451e0df2b0f4a73e5d44f764a480bb3b23953c9076f`,
  lines 473-588: `startRepair` UI selection and returned-item resolution.
- `widget/desktopwidget_connector.lua`, SHA-256
  `9c33f21c1f70a0056147e716d53300634efabe5b744ef6e8690114db21613a01`,
  lines 13739-13786 and 14705-14730: ready-command routing and command 22013.
- `item/itembaseclass_common.lua`, SHA-256
  `7620492917230c3e060ed84d3197bf164c234a3ab73e48a0939bc65107f6b7fa`,
  lines 1170-1307, 3958-4054, and 4215-4250: repair metadata,
  eligibility, and the player-to-player commission amount.

The 100/200/300/400/500 `getRepairAmount` bands are used by the player repair
commission UI. They contradict a direct reuse as the NPC tariff because all
six captured NPC confirmations quote one gil across item levels 15-30.

Self-repair resolves a UI package/slot to an item object, then executes ordinary
CraftCommand ID 22013 through the generic ready-command path. `startRepair` is
a UI selection/resume delegate; it is not a command emitter and does not mutate
durability. There is no retained self-repair packet witness in the corpus.

## First-party intent, not runtime proof

The retained 1.x Lodestone manual states that self-repair restores condition to
100 percent and consumes the appropriate grade of dark matter, without shards
or crystals. It states only that NPC repair is less extensive and does not
restore mint condition. The manual does not supply an NPC result percentage or
tariff. These statements are design-intent evidence, not a captured server
transaction.

## Exact gates

- NPC result condition: unresolved. No target item in this capture has an
  attributable before/after durability update, and the client script neither
  computes nor applies one.
- NPC tariff generalization: unresolved outside the six captured level 15-30
  specimens. One gil is directly proven only for those rows.
- Self-repair server result, material consumption, rejection, and wire/resume
  values: unresolved at runtime because no retained execution is available.
- Server-side revalidation and atomicity for either route: unresolved.
- Repair licence column semantics: the accessor and value zero on all six
  specimens are observed, but the meaning is not established.

The large `0x018F/0x0190/0x0191` transaction near event teardown is not used as
durability evidence. The canonical transaction census leaves its keys and
vectors opaque, and no record is attributable to a repaired target item.
