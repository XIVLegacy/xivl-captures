#!/usr/bin/env python3
"""Build the exhaustive sanitized s2c 0x018D field census."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
import math
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
EXTRACTOR_DIR = SCRIPT_DIR / "extractors"
sys.path.insert(0, str(EXTRACTOR_DIR))

import extract_party_marker_chronology as marker  # type: ignore  # noqa: E402

OUT = REPO_ROOT / "studies" / marker.STUDY_ID / "derived"
ROW_REUSE_FIELDS = ("capture_a", "capture_b", "shared_distinct_rows")
FLOAT_VIEW_OFFSETS = (0x14, 0x18, 0x1C, 0x20)
CLIENT_READ_OFFSETS = (0x00, 0x08, 0x0C, 0x14, 0x18, 0x1C)
IPV4_RE = re.compile(rb"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
RAW_HEX_RE = re.compile(rb"0x[0-9a-fA-F]{8}(?![0-9a-fA-F])")
TOKEN_RE = re.compile(rb"(?i)(?:token|ticket|authorization|password)")


def _csv_bytes(fields: tuple[str, ...], rows: list[dict]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("ascii")


def validate_public_product(data: bytes) -> None:
    """Reject endpoint, credential, raw identifier, and absolute-time surfaces."""
    if IPV4_RE.search(data):
        raise ValueError("public field census contains an IPv4-like endpoint")
    if RAW_HEX_RE.search(data):
        raise ValueError("public field census contains an unsanitized 32-bit hexadecimal value")
    if TOKEN_RE.search(data):
        raise ValueError("public field census contains a credential-like label")


def _frequency_groups(values: list[int | bytes | tuple]) -> dict[str, int]:
    return {
        str(frequency): group_count
        for frequency, group_count in sorted(Counter(Counter(values).values()).items())
    }


def _unsigned_magnitude(value: int, width: int) -> str:
    if value == 0:
        return "zero"
    bits = value.bit_length()
    upper = min(width * 8, ((bits - 1) // 4 + 1) * 4)
    lower = max(1, upper - 3)
    return f"bits-{lower:02d}-{upper:02d}"


def _integer_profile(values: list[int], width: int, offset: int | None = None) -> dict:
    bits = width * 8
    sign_bit = 1 << (bits - 1)
    modulus = 1 << bits
    signed = [value - modulus if value & sign_bit else value for value in values]
    profile = {
        "width": width,
        "samples": len(values),
        "distinct_values": len(set(values)),
        "zero_count": values.count(0),
        "all_ones_sentinel_count": values.count(modulus - 1),
        "unsigned_magnitude_distribution": dict(sorted(Counter(
            _unsigned_magnitude(value, width) for value in values
        ).items())),
        "signed_sign_distribution": {
            "negative": sum(value < 0 for value in signed),
            "zero": sum(value == 0 for value in signed),
            "positive": sum(value > 0 for value in signed),
        },
        "value_frequency_groups": _frequency_groups(values),
    }
    if width == 1:
        profile["unsigned_value_distribution"] = {
            str(value): count for value, count in sorted(Counter(values).items())
        }
    if offset is not None:
        profile["offset"] = f"+0x{offset:02x}"
    return profile


def _float_profile(rows: list[bytes], offset: int) -> dict:
    values = [struct.unpack_from("<f", row, offset)[0] for row in rows]
    bits = [struct.unpack_from("<I", row, offset)[0] for row in rows]
    finite = [value for value in values if math.isfinite(value)]
    negative_zero = sum(value == 0.0 and math.copysign(1.0, value) < 0 for value in values)
    positive_zero = sum(value == 0.0 and math.copysign(1.0, value) > 0 for value in values)
    return {
        "offset": f"+0x{offset:02x}",
        "samples": len(values),
        "valid_float32_bit_patterns": len(values),
        "finite": len(finite),
        "nan": sum(math.isnan(value) for value in values),
        "positive_infinity": sum(value == math.inf for value in values),
        "negative_infinity": sum(value == -math.inf for value in values),
        "negative_finite": sum(value < 0 and math.isfinite(value) for value in values),
        "positive_finite": sum(value > 0 and math.isfinite(value) for value in values),
        "positive_zero": positive_zero,
        "negative_zero": negative_zero,
        "subnormal": sum(
            value != 0.0 and math.isfinite(value) and abs(value) < 2 ** -126
            for value in values
        ),
        "distinct_bit_patterns": len(set(bits)),
        "bit_pattern_frequency_groups": _frequency_groups(bits),
        "finite_min": format(min(finite), ".9g") if finite else None,
        "finite_max": format(max(finite), ".9g") if finite else None,
    }


def _tuple_profile(values: list[bytes | tuple]) -> dict:
    counts = Counter(values)
    return {
        "samples": len(values),
        "distinct_tuples": len(counts),
        "repeated_tuple_groups": sum(count > 1 for count in counts.values()),
        "samples_in_repeated_groups": sum(count for count in counts.values() if count > 1),
        "maximum_group_size": max(counts.values(), default=0),
        "frequency_groups": {
            str(frequency): groups
            for frequency, groups in sorted(Counter(counts.values()).items())
        },
    }


def _row_projection(row: bytes, include_hypothesis: bool) -> tuple:
    offsets = CLIENT_READ_OFFSETS + ((0x20,) if include_hypothesis else ())
    return tuple(struct.unpack_from("<I", row, offset)[0] for offset in offsets)


def _timing_bucket(delta: int) -> str:
    if delta < 0:
        return "negative"
    if delta == 0:
        return "zero"
    if delta < 1000:
        return "1-999"
    if delta < 5000:
        return "1000-4999"
    if delta < 30000:
        return "5000-29999"
    if delta < 120000:
        return "30000-119999"
    return "120000-plus"


def _load_events() -> tuple[list[dict], Counter]:
    paths = marker.default_corpus_paths()
    marker.validate_corpus_paths(paths)
    events: list[dict] = []
    totals = Counter()
    for path in paths:
        capture_events, _timeline, capture_totals, _capture_exclusions = marker._decode_capture(path)
        events.extend(capture_events)
        totals.update(capture_totals)
    return events, totals


def build_outputs() -> dict[str, bytes]:
    events, totals = _load_events()
    logical_rows = [
        row
        for event in events
        for row in event["physical_rows"][:event["count"]]
    ]
    if len(events) != 592 or len(logical_rows) != 769:
        raise ValueError("canonical 0x018D accounting changed")

    integer_profiles = []
    for width, step in ((1, 1), (2, 2), (4, 4)):
        code = {1: "B", 2: "H", 4: "I"}[width]
        for offset in range(0, marker.RECORD_SIZE - width + 1, step):
            values = [struct.unpack_from("<" + code, row, offset)[0] for row in logical_rows]
            integer_profiles.append(_integer_profile(values, width, offset))

    header_profiles = []
    for offset in (0, 4, 8):
        values = [event["header"][offset // 4] for event in events]
        header_profiles.append(_integer_profile(values, 4, offset))

    position_profiles = []
    for count in sorted({event["count"] for event in events}):
        for position in range(count):
            rows = [
                event["physical_rows"][position]
                for event in events if event["count"] == count
            ]
            client_values = {
                f"+0x{offset:02x}": [struct.unpack_from("<I", row, offset)[0] for row in rows]
                for offset in CLIENT_READ_OFFSETS
            }
            position_profiles.append({
                "event_count": count,
                "record_index": position,
                "samples": len(rows),
                "zero_rows": sum(not any(row) for row in rows),
                "distinct_rows": len(set(rows)),
                "client_field_distinct_values": {
                    offset: len(set(values)) for offset, values in client_values.items()
                },
                "client_field_zero_counts": {
                    offset: values.count(0) for offset, values in client_values.items()
                },
                "client_integer_signed_sign_distributions": {
                    offset: _integer_profile(values, 4)["signed_sign_distribution"]
                    for offset, values in client_values.items()
                    if int(offset[3:], 16) not in FLOAT_VIEW_OFFSETS
                },
                "client_float_sign_distributions": {
                    offset: {
                        "negative": sum(struct.unpack_from("<f", row, int(offset[3:], 16))[0] < 0 for row in rows),
                        "zero": sum(struct.unpack_from("<f", row, int(offset[3:], 16))[0] == 0 for row in rows),
                        "positive": sum(struct.unpack_from("<f", row, int(offset[3:], 16))[0] > 0 for row in rows),
                    }
                    for offset in client_values
                    if int(offset[3:], 16) in FLOAT_VIEW_OFFSETS
                },
                "client_read_tuple": _tuple_profile([
                    _row_projection(row, False) for row in rows
                ]),
                "extended_tuple": _tuple_profile([
                    _row_projection(row, True) for row in rows
                ]),
            })

    physical_slots = []
    for slot in range(marker.RECORD_CAPACITY):
        active = [event["physical_rows"][slot] for event in events if event["count"] > slot]
        inactive = [event["physical_rows"][slot] for event in events if event["count"] <= slot]
        physical_slots.append({
            "slot": slot,
            "active_events": len(active),
            "active_zero_rows": sum(not any(row) for row in active),
            "inactive_events": len(inactive),
            "inactive_zero_rows": sum(not any(row) for row in inactive),
            "inactive_nonzero_rows": sum(any(row) for row in inactive),
        })

    row_digests: defaultdict[bytes, list[tuple[str, int, int]]] = defaultdict(list)
    for event_index, event in enumerate(events):
        for record_index, row in enumerate(event["physical_rows"][:event["count"]]):
            digest = hashlib.sha256(b"xivl-018d-row-v1\0" + row).digest()
            row_digests[digest].append((event["capture"], event_index, record_index))
    capture_groups: defaultdict[str, set[bytes]] = defaultdict(set)
    for digest, occurrences in row_digests.items():
        for capture, _event_index, _record_index in occurrences:
            capture_groups[capture].add(digest)
    reuse_rows = []
    for capture_a, capture_b in itertools.combinations(sorted(capture_groups), 2):
        shared = len(capture_groups[capture_a] & capture_groups[capture_b])
        if shared:
            reuse_rows.append({
                "capture_a": capture_a,
                "capture_b": capture_b,
                "shared_distinct_rows": shared,
            })

    frame_groups: defaultdict[tuple, list[dict]] = defaultdict(list)
    lane_groups: defaultdict[tuple, list[dict]] = defaultdict(list)
    for event in events:
        frame_groups[(event["capture"], event["lane_index"], event["frame_index"])].append(event)
        lane_groups[(event["capture"], event["lane_index"], event["lane"])].append(event)
    target_ordinals = []
    subevent_gaps = []
    for group in frame_groups.values():
        ordered = sorted(group, key=lambda event: event["subevent_index"])
        target_ordinals.extend(range(1, len(ordered) + 1))
        subevent_gaps.extend(
            right["subevent_index"] - left["subevent_index"]
            for left, right in zip(ordered, ordered[1:])
        )
    timing_deltas = []
    frame_deltas = []
    for group in lane_groups.values():
        for left, right in zip(group, group[1:]):
            timing_deltas.append(right["outer_value"] - left["outer_value"])
            frame_deltas.append(right["frame_index"] - left["frame_index"])

    inactive_nonzero_rows = sum(
        slot["inactive_nonzero_rows"] for slot in physical_slots
    )
    raw_tuple_profile = _tuple_profile(logical_rows)
    client_tuple_profile = _tuple_profile([
        _row_projection(row, False) for row in logical_rows
    ])
    extended_tuple_profile = _tuple_profile([
        _row_projection(row, True) for row in logical_rows
    ])
    float_tuple_profile = _tuple_profile([
        tuple(struct.unpack_from("<I", row, offset)[0] for offset in FLOAT_VIEW_OFFSETS)
        for row in logical_rows
    ])
    corpus_repeated_groups = [
        occurrences for occurrences in row_digests.values() if len(occurrences) > 1
    ]
    cross_capture_groups = [
        occurrences for occurrences in row_digests.values()
        if len({row[0] for row in occurrences}) > 1
    ]

    field_census = {
        "study_id": marker.STUDY_ID,
        "coverage": {
            "captures": len(marker.default_corpus_paths()),
            "corpus_sha256": marker._corpus_digest(marker.default_corpus_paths()),
            "events": len(events),
            "logical_rows": len(logical_rows),
            "count_one_events": sum(event["count"] == 1 for event in events),
            "count_two_events": sum(event["count"] == 2 for event in events),
            "record_bytes_profiled": len(logical_rows) * marker.RECORD_SIZE,
            "integer_profiles": len(integer_profiles),
            "float_profiles": len(FLOAT_VIEW_OFFSETS),
            "target_s2c_events": totals["target_s2c_events"],
            "target_c2s_events": totals["target_c2s_events"],
        },
        "layout": {
            "application_bytes": marker.APPLICATION_SIZE,
            "leading_header_bytes": marker.RECORD_OFFSET,
            "record_offset": marker.RECORD_OFFSET,
            "record_stride": marker.RECORD_SIZE,
            "physical_record_capacity": marker.RECORD_CAPACITY,
            "count_offset": marker.COUNT_OFFSET,
            "tail_bytes": 7,
            "client_read_offsets": [f"+0x{offset:02x}" for offset in CLIENT_READ_OFFSETS],
            "hypothesis_float_offset_in_unprojected_span": "+0x20",
        },
        "integer_profiles": integer_profiles,
        "header_dword_profiles": header_profiles,
        "float_profiles": [_float_profile(logical_rows, offset) for offset in FLOAT_VIEW_OFFSETS],
        "position_profiles": position_profiles,
        "physical_slots": physical_slots,
        "row_bytes": {
            "all_zero_offsets": [
                f"+0x{offset:02x}"
                for offset in range(marker.RECORD_SIZE)
                if all(row[offset] == 0 for row in logical_rows)
            ],
            "nonzero_samples_by_offset": {
                f"+0x{offset:02x}": sum(row[offset] != 0 for row in logical_rows)
                for offset in range(marker.RECORD_SIZE)
            },
        },
        "tuple_repetition": {
            "full_wire_row": raw_tuple_profile,
            "client_read_projection": client_tuple_profile,
            "extended_projection_with_hypothesis_float": extended_tuple_profile,
            "four_float_projection": float_tuple_profile,
            "events_with_duplicate_active_rows": sum(
                len(set(event["physical_rows"][:event["count"]])) < event["count"]
                for event in events
            ),
        },
        "row_reuse": {
            "distinct_full_wire_rows": len(row_digests),
            "repeated_row_groups": len(corpus_repeated_groups),
            "rows_in_repeated_groups": sum(len(group) for group in corpus_repeated_groups),
            "cross_capture_row_groups": len(cross_capture_groups),
            "rows_in_cross_capture_groups": sum(len(group) for group in cross_capture_groups),
            "capture_pairs_with_shared_rows": len(reuse_rows),
        },
        "count_and_tail": {
            "count_distribution": {
                str(value): count for value, count in sorted(Counter(
                    event["count"] for event in events
                ).items())
            },
            "tail_samples": len(events),
            "zero_tail_samples": sum(not any(event["reserved_tail"]) for event in events),
            "nonzero_tail_samples": sum(any(event["reserved_tail"]) for event in events),
            "inactive_physical_rows": sum(slot["inactive_events"] for slot in physical_slots),
            "inactive_zero_rows": sum(slot["inactive_zero_rows"] for slot in physical_slots),
            "inactive_nonzero_rows": inactive_nonzero_rows,
        },
        "same_frame_order": {
            "frames_with_target": len(frame_groups),
            "targets_per_frame": {
                str(value): count for value, count in sorted(Counter(
                    len(group) for group in frame_groups.values()
                ).items())
            },
            "target_ordinal_distribution": {
                str(value): count for value, count in sorted(Counter(target_ordinals).items())
            },
            "intra_frame_subevent_gap_distribution": {
                str(value): count for value, count in sorted(Counter(subevent_gaps).items())
            },
        },
        "sanitized_timing": {
            "consecutive_lane_pairs": len(timing_deltas),
            "outer_delta_buckets": {
                key: count for key, count in sorted(Counter(
                    _timing_bucket(value) for value in timing_deltas
                ).items())
            },
            "frame_delta_distribution": {
                str(value): count for value, count in sorted(Counter(frame_deltas).items())
            },
            "exact_outer_values_published": False,
            "exact_capture_times_published": False,
        },
        "hypotheses": {
            "key_like_stability": "Some integer and row tuples repeat, but capture repetition does not establish an identity noun.",
            "coordinate_like_ranges": "All tested float bit patterns are finite; range alone does not establish coordinates.",
            "per_row_identity": "Repeated complete rows support stable observed tuples only, not entity identity.",
            "count_slot_behavior": "Counts one and two activate the first one or two physical rows; inactive row bytes are reported separately.",
            "semantic_nouns": "No field noun is promoted from capture statistics or filenames.",
        },
        "boundaries": [
            "Integer profiles publish signs, magnitude buckets, sentinels, and frequency shapes without raw multi-byte values.",
            "Cross-capture row equality uses salted in-memory hashes; no digest or raw comparison key is published.",
            "Capture-pair products expose only public filenames and shared-row counts.",
            "Timing publishes relative buckets and frame gaps, not exact outer values or capture times.",
            "No payload, endpoint address, actor identifier, player name, session identifier, credential, or private time is published.",
            "Published sizes, offsets, float extrema, and repetition counts can narrow candidate payload reconstruction but cannot recover the omitted bytes by themselves.",
            "Chronology and capture scenarios are correlations only; they do not establish causality, policy, or semantic field names.",
        ],
    }
    rendered_json = (json.dumps(field_census, indent=2, sort_keys=True) + "\n").encode("ascii")
    rendered_reuse = _csv_bytes(ROW_REUSE_FIELDS, reuse_rows)
    float_by_offset = {row["offset"]: row for row in field_census["float_profiles"]}
    dword_by_offset = {
        row["offset"]: row
        for row in integer_profiles if row["width"] == 4
    }
    field_verdicts = f"""# Party marker 0x018D field census verdicts

## Exhaustive accounting

The complete 54-capture corpus contains {len(events)} admitted s2c `0x018D`
events and {len(logical_rows)} count-selected rows after canonical TCP
reconstruction. Counts are one in 415 events and two in 177 events. The census
profiles all 40 byte offsets, all 20 aligned u16 views, all 10 aligned u32
views, the three client-read float32 views at `+0x14`, `+0x18`, and `+0x1C`,
and a bounded hypothesis view at `+0x20` in the unprojected span.

## Integer and physical-row shape

The u32 at `+0x00` has {dword_by_offset['+0x00']['distinct_values']} distinct
values and the u32 at `+0x08` has {dword_by_offset['+0x08']['distinct_values']}.
Each is zero only in the two all-zero second rows. The u32 at `+0x0C` is zero
in all {len(logical_rows)} count-selected rows. The unprojected u32 view at
`+0x10` contains five all-ones values; no other aligned integer view has an
all-ones witness. This shape does not establish a sentinel noun. The complete
safe signed, unsigned-magnitude, zero, uniqueness, and frequency-group
distributions are in `field-census.json`.

All {field_census['count_and_tail']['inactive_physical_rows']} rows outside the
count are byte-zero, and all {len(events)} seven-byte tails are zero. Physical
slot zero is nonzero in every event. Slot one is count-selected in 177 events,
but two selected slot-one rows are entirely zero. Slots two through fifteen
are never selected. These facts describe packet shape, not insertion or removal
behavior.

## Float32 domains

All {len(logical_rows)} bit patterns at each tested float offset are finite.
There are no NaNs, infinities, or subnormals. The observed finite ranges are
`{float_by_offset['+0x14']['finite_min']}` through
`{float_by_offset['+0x14']['finite_max']}` at `+0x14`,
`{float_by_offset['+0x18']['finite_min']}` through
`{float_by_offset['+0x18']['finite_max']}` at `+0x18`,
`{float_by_offset['+0x1c']['finite_min']}` through
`{float_by_offset['+0x1c']['finite_max']}` at `+0x1C`, and
The bounded hypothesis view is `{float_by_offset['+0x20']['finite_min']}` through
`{float_by_offset['+0x20']['finite_max']}` at `+0x20`. The sign and zero counts
are retained in the census. Finite ranges and filename scenarios do not prove
coordinate, altitude, heading, or map-space nouns.

## Tuple repetition and capture correlation

The {len(logical_rows)} complete rows form
{raw_tuple_profile['distinct_tuples']} distinct tuples. There are
{raw_tuple_profile['repeated_tuple_groups']} repeated groups containing
{raw_tuple_profile['samples_in_repeated_groups']} rows, with a maximum group
size of {raw_tuple_profile['maximum_group_size']}. Seven complete-row groups
cross capture boundaries, covering 48 rows and 14 public capture pairs. No
event contains two equal selected rows. `row-reuse.csv` publishes only the
public capture filenames and shared distinct-row counts; salted comparison
keys are not published.

Every target is the only `0x018D` event in its outer frame. The 554 consecutive
same-lane pairs fall into six outer-delta bucket observations from 1000 through
4999 numeric units and 548 from 5000 through 29999. These are sanitized
relative relationships, not private capture times, causes, or gameplay phases.

## Rejected interpretations

The capture does not establish actor, player, party-member, marker identifier,
map identifier, key, coordinate, altitude, heading, radius, color, icon, owner,
or slot-purpose nouns for any record field. It also does not establish that a
repeated tuple is entity identity. Only the packet-level presentation context,
the fixed client-read projection, count, and reserved layout are independently
corroborated; field nouns remain neutral.

## Sanitization and reconstruction boundary

No raw payload, endpoint address, actor identifier, player name, session
identifier, credential, hash key, or private time is published. Multi-byte
integer values are reduced to sign, magnitude, sentinel, uniqueness, and
frequency shapes. Exact float extrema, public capture-pair correlations, and
the published fixed layout can narrow candidate payload reconstruction, but do
not recover the omitted bytes by themselves.

The remaining discriminator is an independent public artifact that directly
assigns a field noun to one exact wire offset and width. A filename, finite
range, repetition pattern, or neighboring opcode is insufficient.
"""
    rendered_verdicts = field_verdicts.encode("ascii")
    for rendered in (rendered_json, rendered_reuse, rendered_verdicts):
        validate_public_product(rendered)
    return {
        "field-census.json": rendered_json,
        "row-reuse.csv": rendered_reuse,
        "field-verdicts.md": rendered_verdicts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    stale = []
    for name, rendered in outputs.items():
        target = OUT / name
        if args.check:
            if not target.is_file() or target.read_bytes() != rendered:
                stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(rendered)
    if stale:
        raise SystemExit("stale or missing: " + ", ".join(stale))
    print(f"party marker field census: {len(outputs)} products {'verified' if args.check else 'written'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
