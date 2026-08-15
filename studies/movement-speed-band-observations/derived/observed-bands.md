# Movement Speed Band Observations

This bounded packet-study artifact formalizes the observed float pairs in
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

The canonical payload layout reports variable width-4 fields at inner offsets
24 and 32 at `derived/payload_layouts.json:4368-4401`; the surrounding 168-byte
sub-event and 152-byte inner body are recorded at
`derived/payload_layouts.json:4300-4307`. The inner-packet byte zero is the
eight-byte inner header, so these fields are wrapped-actor sub-event offsets
`+40` and `+48` after the 16-byte sub-event header.

## Observed pairs and counts

The exact little-endian bytes, decoded IEEE-754 values, state-local labels, and
counts are:

Counts include every selected `0x00d0` record in each capture; they are not a
player-actor-only sample. "On-foot baseline" describes the Gridania movement
capture context and the repeated pair, not a server-side state name.

| capture | bounded state label | band A bytes / value | band B bytes / value | count |
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

The result is packet evidence only. It does not establish which field is walk
or run speed, a scalar-to-band conversion, world units, a server formula, or a
general mount-speed rule; alternate and zeroed pairs remain uninterpreted.

## Verification

The relevant framing check passes for all three selected pcaps:

```text
python tools/validate_framing.py sources/pcap-1.23b/objects/mount_unmount_chocobo.pcapng sources/pcap-1.23b/objects/move_around_gridania.pcapng sources/pcap-1.23b/objects/moving_around_gridania.pcapng
```
