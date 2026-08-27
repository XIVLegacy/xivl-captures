#!/usr/bin/env python3
"""Build the exhaustive sanitized s2c 0x018D chronology study."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from extract_observations import (  # type: ignore  # noqa: E402
    INNER_HEADER_LEN,
    SUB_EVENT_CLASS_ACTOR_WRAPPED,
    SUB_EVENT_HEADER_LEN,
    default_corpus_paths,
    parse_sub_events,
)
from extract_streams import (  # type: ignore  # noqa: E402
    _is_game_connection,
    maybe_inflate,
    parse_outer_frames,
    read_packets,
    reconstruct_connections,
)

STUDY_ID = "party-marker-018d-chronology"
TARGET_OPCODE = 0x018D
EXPECTED_SUBEVENT_SIZE = 696
GAME_PREAMBLE_SIZE = 8
APPLICATION_SIZE = 664
RECORD_OFFSET = 16
RECORD_SIZE = 0x28
RECORD_CAPACITY = 16
COUNT_OFFSET = 0x290
WINDOW_RADIUS = 5
SOURCE_MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"
OUT = REPO_ROOT / "studies" / STUDY_ID / "derived"

CATEGORIES = {
    "zone_transition": frozenset({0x0005, 0x0006, 0x0007, 0x0008, 0x000F, 0x0010}),
    "actor_lifecycle": frozenset({0x0007, 0x00CA, 0x00CB, 0x00CC}),
    "group_update": frozenset({0x0143, 0x017A, 0x017C, 0x017D, 0x017E, 0x017F,
                                0x0183, 0x0187, 0x018B}),
    "group_layout_018b": frozenset({0x018B}),
    "setup_0193": frozenset({0x0193}),
}

OCCURRENCE_FIELDS = (
    "occurrence", "capture", "lane_index", "lane", "lane_event_index",
    "frame_index", "subevent_index", "source_actor", "target_actor",
    "header_u32_00", "header_u32_04", "header_u32_08", "marker_count",
    "snapshot", "chronology_shape", "prior_same_snapshot_distance",
)
RECORD_FIELDS = (
    "occurrence", "capture", "record_index", "field_u32_00", "field_u32_08",
    "field_u32_0c", "field_f32_14", "field_f32_18", "field_f32_1c",
    "field_f32_20",
)
NEIGHBOR_FIELDS = (
    "occurrence", "capture", "lane_index", "lane", "relative_event",
    "neighbor_lane_event_index", "same_frame", "neighbor_opcode",
    "zone_transition", "actor_lifecycle", "group_update",
    "group_layout_018b", "setup_0193",
)
IPV4_RE = re.compile(rb"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
RAW_ID_RE = re.compile(rb"0x[0-9a-fA-F]{8}(?![0-9a-fA-F])")


def _counter(values) -> dict[str, int]:
    return {
        str(key): count
        for key, count in sorted(Counter(values).items(), key=lambda item: str(item[0]))
    }


def _csv_bytes(fields: tuple[str, ...], rows: list[dict]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("ascii")


def validate_public_csv(data: bytes) -> None:
    """Reject endpoint-like text and unsanitized 32-bit hexadecimal identifiers."""
    if IPV4_RE.search(data):
        raise ValueError("public CSV contains an IPv4-like endpoint")
    if RAW_ID_RE.search(data):
        raise ValueError("public CSV contains an unsanitized 32-bit hexadecimal value")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _corpus_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("ascii"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(_sha256_file(path)))
    return digest.hexdigest()


def validate_corpus_paths(paths: list[Path], manifest_path: Path = SOURCE_MANIFEST) -> None:
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    expected = sorted(member["file"] for member in manifest.get("members", []))
    actual = sorted(path.name for path in paths)
    if len(expected) != 54 or actual != expected:
        raise ValueError(
            f"canonical corpus membership mismatch: expected {len(expected)} members, "
            f"found {len(actual)}"
        )


def _segment_accounting(path: Path, connection: dict, direction: str) -> tuple[int, int]:
    """Return retransmitted overlap and bytes outside complete reconstructed frames."""
    server = connection["server_endpoint"]
    client = connection["client_endpoint"]
    expected = (server, client) if direction == "s2c" else (client, server)
    segments: list[tuple[int, int]] = []
    payload_bytes = 0
    for packet in read_packets(path):
        if not packet.haslayer("IP") or not packet.haslayer("TCP"):
            continue
        ip = packet["IP"]
        tcp = packet["TCP"]
        payload = bytes(tcp.payload)
        if payload and ((ip.src, tcp.sport), (ip.dst, tcp.dport)) == expected:
            start = int(tcp.seq)
            segments.append((start, start + len(payload)))
            payload_bytes += len(payload)
    merged: list[list[int]] = []
    for start, end in sorted(segments):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    unique_bytes = sum(end - start for start, end in merged)
    return payload_bytes - unique_bytes, unique_bytes - len(connection["streams"].get(direction, b""))


def decode_application(subevent_size: int, sub_body: bytes) -> tuple[dict | None, str]:
    if subevent_size != EXPECTED_SUBEVENT_SIZE:
        return None, "unexpected_subevent_size"
    expected_len = INNER_HEADER_LEN + GAME_PREAMBLE_SIZE + APPLICATION_SIZE
    if len(sub_body) != expected_len:
        return None, "unexpected_application_shape"
    application = sub_body[INNER_HEADER_LEN + GAME_PREAMBLE_SIZE:]
    count = application[COUNT_OFFSET]
    if count > RECORD_CAPACITY:
        return None, "count_exceeds_reserved_capacity"
    if any(application[COUNT_OFFSET + 1:]):
        return None, "nonzero_reserved_tail"
    records = []
    for index in range(count):
        row = application[RECORD_OFFSET + index * RECORD_SIZE:
                          RECORD_OFFSET + (index + 1) * RECORD_SIZE]
        fields = (
            struct.unpack_from("<I", row, 0x00)[0],
            struct.unpack_from("<I", row, 0x08)[0],
            struct.unpack_from("<I", row, 0x0C)[0],
            struct.unpack_from("<f", row, 0x14)[0],
            struct.unpack_from("<f", row, 0x18)[0],
            struct.unpack_from("<f", row, 0x1C)[0],
            struct.unpack_from("<f", row, 0x20)[0],
        )
        if not all(math.isfinite(value) for value in fields[3:]):
            return None, "nonfinite_record_float"
        records.append(fields)
    return {
        "header": struct.unpack_from("<III", application),
        "count": count,
        "records": tuple(records),
        "snapshot_key": hashlib.sha256(application).digest(),
    }, ""


def _decode_capture(path: Path) -> tuple[list[dict], list[dict], Counter, Counter]:
    targets: list[dict] = []
    timeline: list[dict] = []
    totals = Counter()
    exclusions = Counter()
    connections = reconstruct_connections(path)
    totals["frame_shaped_connections"] = len(connections)
    admitted = [connection for connection in connections if _is_game_connection(connection)]
    totals["admitted_lanes"] = len(admitted)
    for connection in connections:
        connection_overlap = 0
        for direction in ("c2s", "s2c"):
            overlap, _trailing = _segment_accounting(path, connection, direction)
            connection_overlap += overlap
        totals["all_connection_retransmitted_overlap_bytes"] += connection_overlap
        if _is_game_connection(connection):
            continue
        totals["excluded_connection_retransmitted_overlap_bytes"] += connection_overlap
        if any(blob.startswith(b"\x16\x03") for blob in connection["streams"].values()):
            exclusions["tls_signature_connections"] += 1
        elif connection["server_endpoint"][1] == 54994:
            exclusions["lobby_54994_connections"] += 1
        else:
            exclusions["other_non_game_connections"] += 1

    for lane_index, connection in enumerate(admitted):
        lane = connection["lane"]
        totals[f"admitted_{lane}_lanes"] += 1
        for direction in ("c2s", "s2c"):
            blob = connection["streams"].get(direction, b"")
            overlap, trailing = _segment_accounting(path, connection, direction)
            totals["retransmitted_overlap_bytes"] += overlap
            totals[f"retransmitted_{direction}_overlap_bytes"] += overlap
            totals["discarded_trailing_stream_bytes"] += trailing
            totals[f"discarded_{direction}_trailing_stream_bytes"] += trailing
            frames = parse_outer_frames(blob)
            totals[f"{direction}_frames"] += len(frames)
            lane_event_index = 0
            for frame_index, frame in enumerate(frames):
                inflated = maybe_inflate(frame["body"])
                if frame["marker"][1] == 0x01 and inflated is None:
                    totals["compressed_frame_inflate_failures"] += 1
                    continue
                body = inflated if inflated is not None else frame["body"]
                parsed = parse_sub_events(body)
                consumed = 0
                for subevent_index, event in enumerate(parsed):
                    if event.get("truncated"):
                        totals["subevent_truncations"] += 1
                        continue
                    consumed = max(consumed, event["offset"] + event["size"])
                    totals[f"{direction}_subevents"] += 1
                    if event["type"] != SUB_EVENT_CLASS_ACTOR_WRAPPED:
                        continue
                    totals[f"{direction}_wrapped_subevents"] += 1
                    start = event["offset"] + SUB_EVENT_HEADER_LEN
                    sub_body = body[start:event["offset"] + event["size"]]
                    if len(sub_body) < INNER_HEADER_LEN:
                        totals["wrapped_short_inner_headers"] += 1
                        continue
                    opcode = struct.unpack_from("<H", sub_body, 2)[0]
                    timeline_event = {
                        "capture": path.name,
                        "lane_index": lane_index,
                        "lane": lane,
                        "direction": direction,
                        "lane_event_index": lane_event_index,
                        "frame_index": frame_index,
                        "subevent_index": subevent_index,
                        "opcode": opcode,
                    }
                    if direction == "s2c":
                        timeline.append(timeline_event)
                    if opcode == TARGET_OPCODE:
                        totals[f"target_{direction}_events"] += 1
                        decoded, reason = decode_application(event["size"], sub_body)
                        if reason:
                            exclusions[reason] += 1
                        elif direction == "s2c":
                            assert decoded is not None
                            targets.append({
                                **timeline_event,
                                "source_actor": event["src_actor"],
                                "target_actor": event["dst_actor"],
                                **decoded,
                            })
                            totals["decoded_target_events"] += 1
                    lane_event_index += 1
                totals["admitted_unparsed_frame_body_bytes"] += len(body) - consumed
    return targets, timeline, totals, exclusions


def _local_labels(events: list[dict]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for event in events:
        values = [event["source_actor"], event["target_actor"], *event["header"]]
        for record in event["records"]:
            values.extend(record[:3])
        for value in values:
            if value not in labels:
                labels[value] = f"value-{len(labels) + 1:03d}"
    return labels


def _snapshot_shapes(events: list[dict]) -> None:
    grouped: defaultdict[tuple[int, str], list[dict]] = defaultdict(list)
    for event in events:
        grouped[(event["lane_index"], event["lane"])].append(event)
    for lane_events in grouped.values():
        snapshots: dict[tuple, str] = {}
        last_seen: dict[tuple, int] = {}
        prior_nonempty = False
        previous_key = None
        previous_count = None
        for position, event in enumerate(lane_events):
            key = event["snapshot_key"]
            if key not in snapshots:
                snapshots[key] = f"snapshot-{len(snapshots) + 1:03d}"
            event["snapshot"] = snapshots[key]
            event["prior_same_snapshot_distance"] = (
                "" if key not in last_seen else position - last_seen[key]
            )
            if event["count"] == 0:
                event["chronology_shape"] = (
                    "empty-after-nonempty" if prior_nonempty else "first-observed-empty"
                )
            elif previous_key is None:
                event["chronology_shape"] = "first-observed-nonempty"
            elif key == previous_key:
                event["chronology_shape"] = "repeated-nonempty"
            elif previous_count is not None and event["count"] < previous_count:
                event["chronology_shape"] = "decreased-count-nonempty"
            elif previous_count is not None and event["count"] > previous_count:
                event["chronology_shape"] = "increased-count-nonempty"
            else:
                event["chronology_shape"] = "changed-same-count-nonempty"
            prior_nonempty = prior_nonempty or event["count"] > 0
            previous_key = key
            previous_count = event["count"]
            last_seen[key] = position


def _build_rows(all_targets: list[dict], all_timeline: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    occurrence_rows: list[dict] = []
    record_rows: list[dict] = []
    neighbor_rows: list[dict] = []
    by_capture_targets: defaultdict[str, list[dict]] = defaultdict(list)
    for event in all_targets:
        by_capture_targets[event["capture"]].append(event)
    timeline_groups: defaultdict[tuple[str, int, str], list[dict]] = defaultdict(list)
    for event in all_timeline:
        timeline_groups[(event["capture"], event["lane_index"], event["lane"])].append(event)

    occurrence_number = 0
    for capture, events in sorted(by_capture_targets.items()):
        labels = _local_labels(events)
        _snapshot_shapes(events)
        for event in events:
            occurrence_number += 1
            occurrence = f"occurrence-{occurrence_number:03d}"
            event["occurrence"] = occurrence
            occurrence_rows.append({
                "occurrence": occurrence,
                "capture": capture,
                "lane_index": event["lane_index"],
                "lane": event["lane"],
                "lane_event_index": event["lane_event_index"],
                "frame_index": event["frame_index"],
                "subevent_index": event["subevent_index"],
                "source_actor": labels[event["source_actor"]],
                "target_actor": labels[event["target_actor"]],
                "header_u32_00": labels[event["header"][0]],
                "header_u32_04": labels[event["header"][1]],
                "header_u32_08": labels[event["header"][2]],
                "marker_count": event["count"],
                "snapshot": event["snapshot"],
                "chronology_shape": event["chronology_shape"],
                "prior_same_snapshot_distance": event["prior_same_snapshot_distance"],
            })
            for record_index, record in enumerate(event["records"]):
                record_rows.append({
                    "occurrence": occurrence,
                    "capture": capture,
                    "record_index": record_index,
                    "field_u32_00": labels[record[0]],
                    "field_u32_08": labels[record[1]],
                    "field_u32_0c": labels[record[2]],
                    "field_f32_14": format(record[3], ".9g"),
                    "field_f32_18": format(record[4], ".9g"),
                    "field_f32_1c": format(record[5], ".9g"),
                    "field_f32_20": format(record[6], ".9g"),
                })
            group = timeline_groups[(capture, event["lane_index"], event["lane"])]
            position = next(
                index for index, candidate in enumerate(group)
                if candidate["lane_event_index"] == event["lane_event_index"]
            )
            start = max(0, position - WINDOW_RADIUS)
            end = min(len(group), position + WINDOW_RADIUS + 1)
            for neighbor_position in range(start, end):
                if neighbor_position == position:
                    continue
                neighbor = group[neighbor_position]
                opcode = neighbor["opcode"]
                neighbor_rows.append({
                    "occurrence": occurrence,
                    "capture": capture,
                    "lane_index": event["lane_index"],
                    "lane": event["lane"],
                    "relative_event": neighbor_position - position,
                    "neighbor_lane_event_index": neighbor["lane_event_index"],
                    "same_frame": "yes" if neighbor["frame_index"] == event["frame_index"] else "no",
                    "neighbor_opcode": f"0x{opcode:04x}",
                    **{
                        category: "yes" if opcode in opcodes else "no"
                        for category, opcodes in CATEGORIES.items()
                    },
                })
    return occurrence_rows, record_rows, neighbor_rows


def _correlations(targets: list[dict], timeline: list[dict], neighbors: list[dict]) -> dict:
    lane_timelines: defaultdict[tuple[str, int, str], list[dict]] = defaultdict(list)
    lane_targets: defaultdict[tuple[str, int, str], list[dict]] = defaultdict(list)
    for event in timeline:
        lane_timelines[(event["capture"], event["lane_index"], event["lane"])].append(event)
    for event in targets:
        lane_targets[(event["capture"], event["lane_index"], event["lane"])].append(event)

    first_marker_order = {}
    for category, opcodes in CATEGORIES.items():
        prior_count = 0
        immediately_prior_count = 0
        for key, events in lane_targets.items():
            first = events[0]
            preceding = [
                event for event in lane_timelines[key]
                if event["lane_event_index"] < first["lane_event_index"]
            ]
            if any(event["opcode"] in opcodes for event in preceding):
                prior_count += 1
            if preceding and preceding[-1]["opcode"] in opcodes:
                immediately_prior_count += 1
        first_marker_order[category] = {
            "lanes_with_any_prior": prior_count,
            "lanes_with_immediate_prior": immediately_prior_count,
            "lanes_with_first_marker": len(lane_targets),
        }

    bounded = {}
    for category in CATEGORIES:
        bounded[category] = {
            "occurrences_within_5_before": len({
                row["occurrence"] for row in neighbors
                if row[category] == "yes" and int(row["relative_event"]) < 0
            }),
            "occurrences_within_5_after": len({
                row["occurrence"] for row in neighbors
                if row[category] == "yes" and int(row["relative_event"]) > 0
            }),
            "occurrences_immediately_before": len({
                row["occurrence"] for row in neighbors
                if row[category] == "yes" and int(row["relative_event"]) == -1
            }),
            "occurrences_immediately_after": len({
                row["occurrence"] for row in neighbors
                if row[category] == "yes" and int(row["relative_event"]) == 1
            }),
        }
    return {
        "tested_opcode_sets": {
            category: [f"0x{opcode:04x}" for opcode in sorted(opcodes)]
            for category, opcodes in CATEGORIES.items()
        },
        "first_marker_order": first_marker_order,
        "bounded_neighborhood": bounded,
    }


def build_outputs() -> dict[str, bytes]:
    paths = default_corpus_paths()
    validate_corpus_paths(paths)
    all_targets: list[dict] = []
    all_timeline: list[dict] = []
    totals = Counter()
    exclusions = Counter()
    per_capture = {}
    for path in paths:
        targets, timeline, capture_totals, capture_exclusions = _decode_capture(path)
        all_targets.extend(targets)
        all_timeline.extend(timeline)
        totals.update(capture_totals)
        exclusions.update(capture_exclusions)
        per_capture[path.name] = {
            "frame_shaped_connections": capture_totals["frame_shaped_connections"],
            "decoded_events": len(targets),
            "admitted_lanes": capture_totals["admitted_lanes"],
            "admitted_main_lanes": capture_totals["admitted_main_lanes"],
            "admitted_chat_lanes": capture_totals["admitted_chat_lanes"],
            "retransmitted_overlap_bytes": capture_totals["retransmitted_overlap_bytes"],
            "all_connection_retransmitted_overlap_bytes": capture_totals["all_connection_retransmitted_overlap_bytes"],
            "excluded_connection_retransmitted_overlap_bytes": capture_totals["excluded_connection_retransmitted_overlap_bytes"],
            "discarded_trailing_stream_bytes": capture_totals["discarded_trailing_stream_bytes"],
            "target_s2c_events": capture_totals["target_s2c_events"],
            "target_c2s_events": capture_totals["target_c2s_events"],
            "exclusions": dict(sorted(capture_exclusions.items())),
        }

    for key in (
        "compressed_frame_inflate_failures", "subevent_truncations",
        "wrapped_short_inner_headers", "target_c2s_events",
        "admitted_unparsed_frame_body_bytes",
    ):
        totals[key] += 0
    for key in (
        "tls_signature_connections", "lobby_54994_connections",
        "other_non_game_connections", "unexpected_subevent_size",
        "unexpected_application_shape", "count_exceeds_reserved_capacity",
        "nonzero_reserved_tail", "nonfinite_record_float",
    ):
        exclusions[key] += 0

    occurrence_rows, record_rows, neighbor_rows = _build_rows(all_targets, all_timeline)
    correlations = _correlations(all_targets, all_timeline, neighbor_rows)
    accounting = {
        "study_id": STUDY_ID,
        "corpus": {
            "captures": len(paths),
            "corpus_sha256": _corpus_digest(paths),
            **{key: totals[key] for key in sorted(totals)},
        },
        "exclusions": {key: exclusions[key] for key in sorted(exclusions)},
        "distributions": {
            "events_by_capture": _counter(event["capture"] for event in all_targets),
            "events_by_lane": _counter(event["lane"] for event in all_targets),
            "marker_counts": _counter(event["count"] for event in all_targets),
            "chronology_shapes": _counter(row["chronology_shape"] for row in occurrence_rows),
            "records": len(record_rows),
            "unique_capture_local_snapshots": sum(
                len({row["snapshot"] for row in occurrence_rows if row["capture"] == path.name})
                for path in paths
            ),
        },
        "correlations": correlations,
        "per_capture": per_capture,
        "boundaries": [
            "All published identifier-shaped dwords use capture-local pseudonyms.",
            "Neighborhoods contain five preceding and five following s2c wrapped events in one admitted lane.",
            "Separate TCP directions and separate connection blocks are never concatenated into chronology.",
            "Snapshot shapes describe observed packet order only; they do not establish creation, removal, causality, or policy.",
            "The RaptureElementContainer+0x4D8 field is a nullable pointer gate, not packet marker data.",
            "No packet in this study is attributed to selector 0x0D creation without direct linking evidence.",
        ],
    }
    counts = accounting["distributions"]["marker_counts"]
    shapes = accounting["distributions"]["chronology_shapes"]
    first_order = correlations["first_marker_order"]
    verdicts = f"""# Party marker 0x018D chronology verdicts

## Exhaustive accounting

The complete 54-capture corpus contains {len(all_targets)} decoded s2c `0x018D`
events and {len(record_rows)} decoded marker records after canonical TCP
reconstruction. The count is 1 in {counts.get('1', 0)} events and 2 in
{counts.get('2', 0)} events. The chronology contains
{shapes.get('first-observed-nonempty', 0)} first-observed nonempty snapshots,
{shapes.get('changed-same-count-nonempty', 0)} changed same-count snapshots,
{shapes.get('increased-count-nonempty', 0)} increased-count snapshots,
{shapes.get('decreased-count-nonempty', 0)} decreased-count snapshots, and
{shapes.get('repeated-nonempty', 0)} repeated nonempty snapshots.

## Packet and snapshot shape

Every admitted event uses the 664-byte application layout: three leading u32
fields, sixteen reserved 0x28-byte record slots, a u8 count at `+0x290`, and a
seven-byte reserved tail. The union of evidenced record positions at `+0x00`,
`+0x08`, `+0x0C`, `+0x14`, `+0x18`, `+0x1C`, and `+0x20` is retained because
the canonical manifests disagree between `+0x0C` and `+0x20` for the sixth
client-read position. Identifier-shaped dwords are capture-local pseudonyms;
the four floating-point projections remain numeric.

All snapshot labels describe only packet chronology. A decreased-count or
`empty-after-nonempty` row is removal-shaped, but does not prove server intent
or client-side removal behavior. Neither shape occurs in this corpus.

## Bounded chronology

No tested category is a consistent predecessor across the 38 lanes with a
marker event. Any prior actor-lifecycle or broader group-update event appears
in {first_order['actor_lifecycle']['lanes_with_any_prior']} and
{first_order['group_update']['lanes_with_any_prior']} lanes respectively;
prior `0x018B`, `0x0193`, and zone-transition events appear in
{first_order['group_layout_018b']['lanes_with_any_prior']},
{first_order['setup_0193']['lanes_with_any_prior']}, and
{first_order['zone_transition']['lanes_with_any_prior']} lanes. The detailed
five-event preceding and following neighborhoods remain in
`neighborhoods.csv`. These are chronology correlations, not evidence that a
neighbor creates the nullable selector `0x0D` pointee or causes marker
handling.

## Rejected interpretations

The chronology does not establish party policy, permission, membership,
server causality, or nouns for coordinate and unknown numeric values. No
neighboring opcode is claimed to create selector `0x0D`. The gate at
`RaptureElementContainer+0x4D8` is a nullable pointer; marker records live in
the pointee's `+0x98` subobject and are not stored in the gate field.

## Remaining boundary

The preserved corpus can prove only the observed same-lane order and repeated
packet snapshots. Direct runtime evidence linking a specific packet or state
transition to selector `0x0D` creation would be required for a creation
boundary. An empty or decreasing-count witness would be required for a
removal-shaped packet chronology; direct runtime observation would still be
required to establish removal behavior.
"""
    occurrence_csv = _csv_bytes(OCCURRENCE_FIELDS, occurrence_rows)
    record_csv = _csv_bytes(RECORD_FIELDS, record_rows)
    neighborhood_csv = _csv_bytes(NEIGHBOR_FIELDS, neighbor_rows)
    for rendered in (occurrence_csv, record_csv, neighborhood_csv):
        validate_public_csv(rendered)
    return {
        "occurrences.csv": occurrence_csv,
        "marker-records.csv": record_csv,
        "neighborhoods.csv": neighborhood_csv,
        "accounting.json": (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii"),
        "verdicts.md": verdicts.encode("ascii"),
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
    print(f"party marker chronology: {len(outputs)} products {'verified' if args.check else 'written'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
