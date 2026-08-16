# Movement Speed Band Observations

This bounded packet-study artifact formalizes the observed float profiles in
clientbound map `0x00d0` (`SetActorSpeedPacket`) records from the Chocobo
mount/unmount capture and the two Gridania movement captures. It records wire
observations only; it does not infer a server formula or convert values to
world units.

## Packet and field evidence

The mount scenario identifies `0x00d0` as map clientbound
`SetActorSpeedPacket` at
`catalog/scenarios/chocobo-mechanic-mount-unmount/evidence-map.md:5-20`; the
Gridania scenario carries the same opcode at
`catalog/scenarios/movement-mechanic-gridania-locomotion/evidence-map.md:5-40`.
The canonical observation product witnesses opcode `0x00d0`, one 168-byte
sub-event size, and the capture witnesses at `derived/observations.json:4603-4642`.
The source members and hashes are listed at
`sources/pcap-1.23b/manifest.yaml:135-146`.

Beginning at inner offset 20, the payload carries four `(slot, float32)` pairs.
The slot integers are `0`, `1`, `2`, and `3`; their float values are at inner
offsets 24, 32, 40, and 48. The surrounding 168-byte sub-event and 152-byte
inner body are recorded at `derived/payload_layouts.json:4300-4307`. The
inner-packet byte zero is the eight-byte inner header, so the float fields are
wrapped-actor sub-event offsets `+40`, `+48`, `+56`, and `+64` after the
16-byte sub-event header.

## Mount transition profile and verdict

Packet 20 contains one compressed server-to-client frame at reconstructed
stream offset `0x00aa`. Its inflated body carries opcode `0x0197`
(`SetCurrentMountChocoboPacket`), opcode `0x013c`, and three byte-identical
`0x00d0` records at sub-event offsets `0x0070`, `0x0118`, and `0x01c0`.
Packet 85 contains the later dismount-side frame at stream offset `0x0408`,
with three byte-identical `0x00d0` records at the same relative offsets.
Packet numbers are 1-based positions in the immutable capture.

| Slot | Mounted bytes / value | Dismount-side bytes / value |
|---:|---|---|
| 0 | `00 00 00 00 66 66 66 40` / 3.6 | `00 00 00 00 00 00 00 40` / 2 |
| 1 | `01 00 00 00 00 00 10 41` / 9 | `01 00 00 00 00 00 a0 40` / 5 |
| 2 | `02 00 00 00 00 00 10 41` / 9 | `02 00 00 00 00 00 a0 40` / 5 |
| 3 | `03 00 00 00 00 00 00 00` / 0 | `03 00 00 00 00 00 00 00` / 0 |

In indexed wire order the mounted profile is `3.6/9/9/0`. Written with the
zero baseline first, the observed value set is `0/3.6/9/9`.

| Band | Retail-observed value | Compared value | Verdict |
|---|---:|---:|---|
| Zero baseline | 0 | 0 | Confirmed |
| First nonzero mounted band | 3.6 | 5 | Refuted; use 3.6 |
| Second nonzero mounted band | 9 | 10 | Refuted; use 9 |
| Third nonzero mounted band | 9 | 10 | Refuted; use 9 |

The capture identifies the mounted profile but does not independently label
slots 0-2 as walk, run, or sprint. No separately marked sprint activation is
witnessed. Those finer state labels remain unobserved; the numeric refutation
does not depend on them.

## Wider observed profiles and counts

The first two slots also vary across ordinary actors in the two movement
captures. Their exact little-endian bytes, decoded IEEE-754 values,
state-local labels, and counts are:

Counts include every selected `0x00d0` record in each capture; they are not a
player-actor-only sample. "On-foot baseline" describes the Gridania movement
capture context and the repeated pair, not a server-side state name.

| capture | bounded state label | slot 0 bytes / value | slot 1 bytes / value | count |
|---|---|---|---|---:|
| `mount_unmount_chocobo.pcapng` | first run after `0x0197` | `66666640` / 3.5999999046325684 | `00001041` / 9.0 | 3 |
| `mount_unmount_chocobo.pcapng` | second run after `0x0134` | `00000040` / 2.0 | `0000a040` / 5.0 | 3 |
| `move_around_gridania.pcapng` | on-foot baseline pair | `00000040` / 2.0 | `0000a040` / 5.0 | 32 |
| `moving_around_gridania.pcapng` | on-foot baseline pair | `00000040` / 2.0 | `0000a040` / 5.0 | 267 |
| `move_around_gridania.pcapng` | other observed pair | `0000a040` / 5.0 | `00002041` / 10.0 | 1 |
| `moving_around_gridania.pcapng` | other observed pair | `00002040` / 2.5 | `00000041` / 8.0 | 4 |
| `moving_around_gridania.pcapng` | zeroed pair | `00000000` / 0.0 | `00000000` / 0.0 | 10 |

The mount sequence labels are bounded to wire order. Run
`python tools/extractors/extract_wire_order.py sources/pcap-1.23b/objects/mount_unmount_chocobo.pcapng --direction s2c --around 0x00d0 --before 8 --after 2`;
the `0x0197` and `0x0134` anchors bracket the two three-packet runs.

## Reproducible derivation

The following command uses the canonical reconstructed-stream payload walker;
it prints the exact pair counter for each selected capture:

```text
python -c "import struct,sys;from collections import Counter;from pathlib import Path;sys.path.insert(0,'tools/extractors');from extract_payload_samples import walk_capture_payloads;caps=['mount_unmount_chocobo.pcapng','move_around_gridania.pcapng','moving_around_gridania.pcapng'];print({c:Counter((struct.unpack('<f',bytes.fromhex(r['bytes'])[24:28])[0],struct.unpack('<f',bytes.fromhex(r['bytes'])[32:36])[0]) for r in walk_capture_payloads(Path('sources/pcap-1.23b/objects')/c) if r['direction']=='s2c' and r['opcode']==0xd0) for c in caps})"
```

The result is packet evidence only. It does not establish which slot is walk,
run, or sprint speed, a scalar-to-band conversion, world units, a server
formula, or a general mount-speed rule; alternate and zeroed profiles remain
uninterpreted.

## Verification

The relevant framing check passes for all three selected pcaps:

```text
python tools/validate_framing.py sources/pcap-1.23b/objects/mount_unmount_chocobo.pcapng sources/pcap-1.23b/objects/move_around_gridania.pcapng sources/pcap-1.23b/objects/moving_around_gridania.pcapng
```
