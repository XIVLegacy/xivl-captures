# Client Position Report 0x00CA Observations

Every figure below is aggregated from the sent client-to-server `0x00ca`
reports in two Gridania captures. The products hold counts and
statistics only. They hold no coordinates, timestamps, or payload bytes.

## Record shape

Every record is a 64-byte sub-event. Offsets below
count from the start of the 48-byte wrapped-actor body that follows the
16-byte sub-event header.

| Body offset | Size | Field |
|---:|---:|---|
| 8 | 8 | timestamp copy, equal to the payload timestamp |
| 16 | 8 | timestamp, low dword only, steps of one second between reports |
| 24 | 4 | x as float32 |
| 28 | 4 | y as float32 |
| 32 | 4 | z as float32 |
| 36 | 4 | rotation as float32 radians |
| 40 | 2 | moveState as u16 |
| 42 | 6 | reserved, varying bytes |

The field names and offsets agree with
xivl-client-structs:manifests/c2s_payload_decoding.json `c2s_0x00ca`.

## Capture checks

| Quantity | `move_around_gridania` | `moving_around_gridania` |
|---|---:|---:|
| Source SHA-256 | `bea7ae86444fa3ef9acc08f148f60dff1e5992188ee85136dec50c64e09236d0` | `bf6abf7ccc7a16e071846036477c1fadbc3b46385ef6e747b543d836f3f51017` |
| Records | 600 | 2402 |
| Timestamp copy equals timestamp | 600 | 2402 |
| Timestamp high dword nonzero | 0 | 0 |
| Timestamps non-decreasing | yes | yes |
| Distinct reserved values | 23 | 59 |
| Rotation minimum | -3.1018 | -3.1252 |
| Rotation maximum | 2.9109 | 3.138 |

## moveState values

| Quantity | `move_around_gridania` | `moving_around_gridania` |
|---|---:|---:|
| moveState 0 | 24 | 24 |
| moveState 2 | 576 | 2378 |
| Position-changing reports | 574 | 2375 |
| Position-changing with moveState 0 | 1 | 1 |
| Position-changing with moveState 2 | 573 | 2374 |

A report is position-changing when its x, y, or z differs from the
previous report in stream order. Only values 0 and 2 occur. Every idle
record with value 0 sits before or after the single run of value 2.
Stream order is the reconstructed client-to-server stream order.

## Rotation against travel direction

For each step between consecutive reports, dx is the x change and dz is
the z change. The travel heading is atan2(dx, dz) in radians. A heading
of 0 points along +z and a positive heading turns toward +x. The offset
is the rotation of the report that ends the step minus that heading,
wrapped into the range from -pi to pi. Only steps ending in a moveState
2 report and with a nonzero horizontal length are counted. The
resultant length is the circular mean resultant length of the offsets,
where 1 means every offset is identical.

| Capture | Step set | Steps | Resultant length | Mean offset rad |
|---|---|---:|---:|---:|
| `move_around_gridania` | all steps | 573 | 0.981 | -0.0055 |
| `move_around_gridania` | length 1.0 or more | 279 | 0.993 | 0.003 |
| `move_around_gridania` | length under 1.0 | 294 | 0.9697 | -0.0137 |
| `moving_around_gridania` | all steps | 2374 | 0.9921 | -0.0009 |
| `moving_around_gridania` | length 1.0 or more | 1177 | 0.9928 | -0.0036 |
| `moving_around_gridania` | length under 1.0 | 1197 | 0.9913 | 0.0018 |
| both captures | length 1.0 or more | 1456 | 0.9929 | -0.0023 |

Horizontal step lengths fall into two groups of similar size, one under
0.5 and one between 1 and 2. A single step length is therefore not a
speed. The rows split by length show the relation holds in both groups.

| Horizontal step length | `move_around_gridania` | `moving_around_gridania` |
|---|---:|---:|
| bin lt_0.5 | 291 | 1192 |
| bin 0.5_to_1 | 4 | 6 |
| bin 1_to_2 | 278 | 1175 |
| bin ge_2 | 1 | 2 |

## Horizontal speed over the moveState 2 run

Each capture holds one unbroken run of moveState 2 reports. Mean speed is
the horizontal path length of the run divided by the timestamp span of
the run. Timestamps have a resolution of one second, so the span carries
an error of up to one second at each end. The run can include pauses
and unchanged reports, which lower the minimum rows. Second buckets sum the step
lengths of reports that share a timestamp second, using only seconds
strictly inside the run. Window rows average 10 consecutive interior
seconds.

| Quantity | `move_around_gridania` | `moving_around_gridania` |
|---|---:|---:|
| Run holds only moveState 2 | yes | yes |
| Run reports | 576 | 2378 |
| Run timestamp span seconds | 104 | 423 |
| Run horizontal path length | 502.1 | 2081.9 |
| Mean speed units per second | 4.83 | 4.92 |
| Interior seconds | 103 | 422 |
| Interior seconds with 4 reports | 14 | 42 |
| Interior seconds with 5 reports | 20 | 85 |
| Interior seconds with 6 reports | 69 | 286 |
| Interior seconds with 7 reports | 0 | 9 |
| Second bucket n | 103 | 422 |
| Second bucket mean | 4.8515 | 4.9278 |
| Second bucket median | 5.3148 | 5.2467 |
| Second bucket p5 | 3.5354 | 3.517 |
| Second bucket p95 | 5.5015 | 5.5 |
| Second bucket min | 0.1146 | 2.4358 |
| Second bucket max | 5.7152 | 5.6313 |
| 10 second window n | 10 | 42 |
| 10 second window mean | 4.8556 | 4.9298 |
| 10 second window median | 4.9392 | 4.9532 |
| 10 second window p5 | 4.2817 | 4.7951 |
| 10 second window p95 | 5.043 | 5.0533 |
| 10 second window min | 4.2817 | 4.4409 |
| 10 second window max | 5.043 | 5.1239 |

The 0x00d0 on-foot baseline pair recorded in
studies/movement-speed-band-observations/derived/observed-bands.md
carries 2.0 in slot 0 and 5.0 in slot 1. The observed mean speed lies
near 5.0. This study
does not establish that the 0x00d0 value governs the reported movement,
that the unit is the same, or which gait the run was.

## Not established

- Whether moveState 2 means walk, run, or another gait.
- The moveState values for any other gait, for sprint, for mounts, for
  jumping or swimming, or for combat states.
- Any zone other than Gridania.
- Any collision, slope, or terrain effect on speed.
- The meaning of the reserved bytes, which vary between records.
- Whether the alternation of long and short steps is a client timer
  artifact or deliberate.
- Anything beyond on-foot play by one character in two sessions.
