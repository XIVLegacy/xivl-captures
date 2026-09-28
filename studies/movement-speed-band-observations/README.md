# Movement Speed Band Observations

## Study contents

This bounded packet study records exact four-slot profiles observed in clientbound
map `0x00d0` `SetActorSpeedPacket` records from the Chocobo mount/unmount
capture and two Gridania movement captures. It does not infer a server formula,
world units, walk/run semantics, or a scalar-to-band conversion.

## Start here

- `derived/observed-bands.md` - packet fields, exact values, counts, offsets,
  anchors, and reproducible derivation.

## Source material

The mount and movement scenario evidence maps identify `0x00d0` as the
clientbound `SetActorSpeedPacket` and the canonical observations product
records its 168-byte sub-event shape (`catalog/scenarios/chocobo-mechanic-mount-unmount/evidence-map.md:5-20`,
`catalog/scenarios/movement-mechanic-gridania-locomotion/evidence-map.md:5-40`,
`derived/observations.json:4603-4642`). The source members are listed in
`sources/pcap-1.23b/manifest.yaml:135-146`.

## Verdict

The explicit mount transition carries indexed values `3.6/9/9/0`, equivalent
to `0/3.6/9/9` when the zero baseline is written first. The alternative
`0/5/10/10` simplification is refuted for all three nonzero bands. The evidence
establishes values only; it does not establish how a server chooses or converts
them.

## Promoted conclusions

The study promotes only the observed `0x00d0` field bytes, decoded float profiles,
packet offsets, and counts recorded in `derived/observed-bands.md`. The labels
for mount and on-foot rows are capture-local sequence context.

## Topics

- SetActorSpeedPacket wire fields
- Mount and movement capture observations
- Little-endian float value bands

## Evidence gaps

The captures do not identify which field is walk or run speed, how a scalar is
converted into a band, or whether either field is a general mount-speed rule.

## Further research

A controlled retail capture varying one movement state at a time, or a
client-static field map, would be needed to resolve those remaining questions.

## Verification

The framing check for the three selected captures is:

```text
python tools/validate_framing.py sources/pcap-1.23b/objects/mount_unmount_chocobo.pcapng sources/pcap-1.23b/objects/move_around_gridania.pcapng sources/pcap-1.23b/objects/moving_around_gridania.pcapng
```
