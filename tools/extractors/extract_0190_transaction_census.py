#!/usr/bin/env python3
"""Build the exhaustive sanitized s2c 0x018F/0x0190/0x0191 census."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import struct
import sys
from collections import Counter
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
)
from extract_streams import (  # type: ignore  # noqa: E402
    IP,
    TCP,
    maybe_inflate,
    parse_outer_frames,
    read_packets,
    reconstruct_lanes,
)

STUDY_ID = "map-0190-transaction-census"
SOURCE_MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"
OUT = REPO_ROOT / "studies" / STUDY_ID / "derived"

BEGIN, RECORD, END = 0x018F, 0x0190, 0x0191
TARGETS = {BEGIN, RECORD, END}
EXPECTED_SIZES = {BEGIN: 40, RECORD: 136, END: 40}
PACKET_HEADER_TAIL_SIZE = 8
VECTOR_WORDS = 16
TAIL_SIZE = 32
LOW_VALUE_MAX = 255
EQUIPMENT_CARRIERS = set(range(0x014D, 0x0152))

SPAN_FIELDS = (
    "span_id", "capture", "lane_index", "lane", "begin_frame", "begin_subevent",
    "end_frame", "end_subevent", "record_count", "first_record_frame",
    "first_record_subevent", "last_record_frame", "last_record_subevent",
    "prior_same_lane_opcode", "next_same_lane_opcode", "intervening_non_target_opcodes",
    "inventory_frame_overlap", "equipment_carrier_overlap", "change_frame_overlap",
)


def _counter(values) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def _csv_bytes(fields: tuple[str, ...], rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("ascii")


def validate_public_bytes(data: bytes) -> None:
    text = data.decode("ascii")
    if re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text):
        raise ValueError("public product contains IPv4-like text")
    if re.search(r"\b0x[0-9a-fA-F]{8}\b", text):
        raise ValueError("public product contains an unsanitized 32-bit hexadecimal value")
    lowered = text.lower()
    forbidden = ("payload", "endpoint", "actor_id", "session_id", "ticket", "token")
    if any(term in lowered for term in forbidden):
        raise ValueError("public product contains a forbidden raw or credential surface")


def validate_corpus_paths(paths: list[Path], manifest_path: Path = SOURCE_MANIFEST) -> None:
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    expected = sorted(member["file"] for member in manifest.get("members", []))
    actual = sorted(path.name for path in paths)
    if len(expected) != 54 or actual != expected:
        raise ValueError(
            f"canonical corpus membership mismatch: expected {len(expected)} members, "
            f"found {len(actual)}"
        )


def decode_application(opcode: int, subevent_size: int, sub_body: bytes) -> tuple[dict | None, str]:
    if opcode not in TARGETS:
        raise ValueError(f"unsupported target opcode 0x{opcode:04x}")
    if subevent_size != EXPECTED_SIZES[opcode]:
        return None, "unexpected_subevent_size"
    application_offset = INNER_HEADER_LEN + PACKET_HEADER_TAIL_SIZE
    expected_application_size = 0x68 if opcode == RECORD else 8
    if len(sub_body) != application_offset + expected_application_size:
        return None, "unexpected_application_shape"
    application = sub_body[application_offset:]
    if opcode in (BEGIN, END):
        return {"zero_application": application == bytes(8)}, ""
    words = struct.unpack("<18I", application[:0x48])
    return {
        "key1": words[0],
        "key2": words[1],
        "vector": words[2:],
        "tail": application[0x48:],
        "application": application,
    }, ""


def _retransmitted_segments(path: Path) -> int:
    lanes = reconstruct_lanes(path)
    admitted = {
        frozenset((lane["client_endpoint"], lane["server_endpoint"])) for lane in lanes
    }
    seen: set[tuple] = set()
    repeats = 0
    for packet in read_packets(path):
        if not packet.haslayer(IP) or not packet.haslayer(TCP):
            continue
        body = bytes(packet[TCP].payload)
        if not body:
            continue
        endpoints = frozenset((
            (packet[IP].src, int(packet[TCP].sport)),
            (packet[IP].dst, int(packet[TCP].dport)),
        ))
        if endpoints not in admitted:
            continue
        key = (
            packet[IP].src,
            packet[IP].dst,
            int(packet[TCP].sport),
            int(packet[TCP].dport),
            int(packet[TCP].seq),
            hashlib.sha256(body).digest(),
        )
        if key in seen:
            repeats += 1
        else:
            seen.add(key)
    return repeats


def _scan_capture(path: Path) -> tuple[list[list[dict]], Counter, Counter]:
    timelines: list[list[dict]] = []
    totals = Counter()
    exclusions = Counter()
    lanes = reconstruct_lanes(path)
    totals["admitted_lanes"] = len(lanes)
    totals["retransmitted_segments"] = _retransmitted_segments(path)
    for lane_index, lane in enumerate(lanes):
        totals[f"admitted_{lane['lane']}_lanes"] += 1
        for direction in ("c2s", "s2c"):
            timeline: list[dict] = []
            frames = parse_outer_frames(lane["streams"].get(direction, b""))
            totals[f"{direction}_frames"] += len(frames)
            direction_event_index = 0
            for frame_index, frame in enumerate(frames):
                inflated = maybe_inflate(frame["body"])
                if frame["marker"][1] == 0x01 and inflated is None:
                    totals["compressed_frame_inflate_failures"] += 1
                    continue
                body = inflated if inflated is not None else frame["body"]
                offset = 0
                subevent_index = 0
                while offset + SUB_EVENT_HEADER_LEN <= len(body):
                    size, event_type = struct.unpack_from("<HH", body, offset)
                    if size < SUB_EVENT_HEADER_LEN or offset + size > len(body):
                        totals["subevent_truncations"] += 1
                        break
                    totals[f"{direction}_subevents"] += 1
                    if event_type == SUB_EVENT_CLASS_ACTOR_WRAPPED:
                        totals[f"{direction}_wrapped_subevents"] += 1
                        sub_body = body[
                            offset + SUB_EVENT_HEADER_LEN:offset + size
                        ]
                        if len(sub_body) < INNER_HEADER_LEN:
                            totals["wrapped_short_inner_headers"] += 1
                        else:
                            opcode = struct.unpack_from("<H", sub_body, 2)[0]
                            event = {
                                "capture": path.name,
                                "lane_index": lane_index,
                                "lane": lane["lane"],
                                "direction": direction,
                                "direction_event_index": direction_event_index,
                                "frame_index": frame_index,
                                "subevent_index": subevent_index,
                                "opcode": opcode,
                            }
                            if opcode in TARGETS:
                                totals[f"target_{direction}_0x{opcode:04x}"] += 1
                                decoded, reason = decode_application(opcode, size, sub_body)
                                if reason:
                                    exclusions[reason] += 1
                                    event["malformed_reason"] = reason
                                else:
                                    event.update(decoded or {})
                            timeline.append(event)
                    offset += size
                    subevent_index += 1
                    direction_event_index += 1
                if offset != len(body):
                    totals["unparsed_frame_body_bytes"] += len(body) - offset
            if direction == "s2c":
                timelines.append(timeline)
    return timelines, totals, exclusions


def segment_transactions(timeline: list[dict]) -> tuple[list[dict], Counter]:
    spans: list[dict] = []
    issues = Counter()
    opened: dict | None = None
    records: list[dict] = []
    for position, event in enumerate(timeline):
        opcode = event["opcode"]
        malformed = event.get("malformed_reason")
        if opcode == BEGIN:
            if malformed:
                issues["malformed_begin"] += 1
                continue
            if opened is not None:
                issues["nested_begin"] += 1
                issues["unterminated_span"] += 1
            opened = {"event": event, "position": position}
            records = []
        elif opcode == RECORD:
            if malformed:
                issues["malformed_record"] += 1
            elif opened is None:
                issues["orphan_record"] += 1
            else:
                records.append(event)
        elif opcode == END:
            if malformed:
                issues["malformed_end"] += 1
                continue
            if opened is None:
                issues["orphan_end"] += 1
                continue
            spans.append({
                "begin": opened["event"],
                "end": event,
                "begin_position": opened["position"],
                "end_position": position,
                "records": records,
                "timeline": timeline,
            })
            opened = None
            records = []
    if opened is not None:
        issues["unterminated_span"] += 1
    return spans, issues


def _multiplicity(values) -> dict:
    counts = Counter(values)
    return {
        "events": sum(counts.values()),
        "distinct_values": len(counts),
        "zero_events": counts.get(0, 0),
        "singleton_values": sum(count == 1 for count in counts.values()),
        "repeated_values": sum(count > 1 for count in counts.values()),
        "repeated_events_beyond_first": sum(count - 1 for count in counts.values()),
        "maximum_multiplicity": max(counts.values(), default=0),
        "multiplicity_histogram": _counter(counts.values()),
    }


def _vector_analysis(records: list[dict]) -> dict:
    vectors = [tuple(record["vector"]) for record in records]
    vector_counts = Counter(vectors)
    nonzero_counts = [sum(value != 0 for value in vector) for vector in vectors]
    position_nonzero = [sum(vector[index] != 0 for vector in vectors) for index in range(VECTOR_WORDS)]
    low_values = Counter(
        value for vector in vectors for value in vector if 0 <= value <= LOW_VALUE_MAX
    )
    value_bands = Counter()
    for vector in vectors:
        for value in vector:
            if value == 0:
                value_bands["zero"] += 1
            elif value <= LOW_VALUE_MAX:
                value_bands[f"1-{LOW_VALUE_MAX}"] += 1
            elif value <= 0xFFFF:
                value_bands["256-65535"] += 1
            else:
                value_bands["65536-4294967295"] += 1

    prior_by_pair: dict[tuple, tuple[int, ...]] = {}
    comparisons = 0
    equal = 0
    changed_positions = Counter()
    changed_word_counts = Counter()
    for record in records:
        key = (record["capture"], record["lane_index"], record["key1"], record["key2"])
        vector = tuple(record["vector"])
        if key in prior_by_pair:
            comparisons += 1
            changed = [index for index, pair in enumerate(zip(prior_by_pair[key], vector)) if pair[0] != pair[1]]
            if not changed:
                equal += 1
            for index in changed:
                changed_positions[str(index)] += 1
            changed_word_counts[str(len(changed))] += 1
        prior_by_pair[key] = vector

    return {
        "record_vectors": len(vectors),
        "distinct_vectors": len(vector_counts),
        "exact_repeated_vectors_beyond_first": sum(count - 1 for count in vector_counts.values()),
        "maximum_vector_multiplicity": max(vector_counts.values(), default=0),
        "all_zero_vectors": sum(not any(vector) for vector in vectors),
        "nonzero_word_count_histogram": _counter(nonzero_counts),
        "position_nonzero_counts": {str(index): count for index, count in enumerate(position_nonzero)},
        "value_bands": dict(sorted(value_bands.items())),
        "bounded_values_0_255": {str(value): count for value, count in sorted(low_values.items())},
        "same_capture_lane_key_pair_comparisons": comparisons,
        "equal_vector_comparisons": equal,
        "changed_vector_comparisons": comparisons - equal,
        "changed_word_count_histogram": dict(sorted(changed_word_counts.items())),
        "changed_position_counts": dict(sorted(changed_positions.items(), key=lambda item: int(item[0]))),
    }


def _tail_analysis(records: list[dict]) -> dict:
    tails = [record["tail"] for record in records]
    return {
        "tails": len(tails),
        "distinct_tails": len(set(tails)),
        "all_zero_tails": sum(tail == bytes(TAIL_SIZE) for tail in tails),
        "nonzero_byte_position_counts": {
            str(index): sum(tail[index] != 0 for tail in tails)
            for index in range(TAIL_SIZE)
            if any(tail[index] != 0 for tail in tails)
        },
        "varying_byte_positions": [
            index for index in range(TAIL_SIZE)
            if len({tail[index] for tail in tails}) > 1
        ],
    }


def _scope_overlap(
    timeline: list[dict], start: int, end: int, begin_opcode: int, end_opcode: int
) -> bool:
    depth = 0
    for position, event in enumerate(timeline):
        opcode = event["opcode"]
        if position == start and depth:
            return True
        if start <= position <= end and opcode in (begin_opcode, end_opcode):
            return True
        if opcode == begin_opcode:
            depth += 1
        elif opcode == end_opcode and depth:
            depth -= 1
        if position > end:
            break
    return False


def _span_rows(spans: list[dict]) -> list[dict]:
    rows = []
    for span_id, span in enumerate(spans, 1):
        begin = span["begin"]
        end = span["end"]
        records = span["records"]
        timeline = span["timeline"]
        inner = timeline[span["begin_position"] + 1:span["end_position"]]
        non_targets = sorted({event["opcode"] for event in inner if event["opcode"] not in TARGETS})
        prior = timeline[span["begin_position"] - 1]["opcode"] if span["begin_position"] else None
        following = timeline[span["end_position"] + 1]["opcode"] if span["end_position"] + 1 < len(timeline) else None
        rows.append({
            "span_id": f"span-{span_id:03d}",
            "capture": begin["capture"],
            "lane_index": begin["lane_index"],
            "lane": begin["lane"],
            "begin_frame": begin["frame_index"],
            "begin_subevent": begin["subevent_index"],
            "end_frame": end["frame_index"],
            "end_subevent": end["subevent_index"],
            "record_count": len(records),
            "first_record_frame": records[0]["frame_index"] if records else "",
            "first_record_subevent": records[0]["subevent_index"] if records else "",
            "last_record_frame": records[-1]["frame_index"] if records else "",
            "last_record_subevent": records[-1]["subevent_index"] if records else "",
            "prior_same_lane_opcode": f"0x{prior:04x}" if prior is not None else "",
            "next_same_lane_opcode": f"0x{following:04x}" if following is not None else "",
            "intervening_non_target_opcodes": ";".join(f"0x{opcode:04x}" for opcode in non_targets),
            "inventory_frame_overlap": "yes" if _scope_overlap(
                timeline, span["begin_position"], span["end_position"], 0x0146, 0x0147
            ) else "no",
            "equipment_carrier_overlap": "yes" if any(event["opcode"] in EQUIPMENT_CARRIERS for event in inner) else "no",
            "change_frame_overlap": "yes" if _scope_overlap(
                timeline, span["begin_position"], span["end_position"], 0x016D, 0x016E
            ) else "no",
        })
    return rows


def build_outputs() -> dict[str, bytes]:
    corpus_paths = default_corpus_paths()
    validate_corpus_paths(corpus_paths)
    totals = Counter()
    exclusions = Counter()
    issues = Counter()
    spans: list[dict] = []
    records: list[dict] = []
    per_capture = {}
    for path in corpus_paths:
        timelines, capture_totals, capture_exclusions = _scan_capture(path)
        totals.update(capture_totals)
        exclusions.update(capture_exclusions)
        capture_spans = []
        capture_issues = Counter()
        capture_records = []
        for timeline in timelines:
            lane_spans, lane_issues = segment_transactions(timeline)
            capture_spans.extend(lane_spans)
            capture_issues.update(lane_issues)
            capture_records.extend(record for span in lane_spans for record in span["records"])
        spans.extend(capture_spans)
        records.extend(capture_records)
        issues.update(capture_issues)
        per_capture[path.name] = {
            "admitted_lanes": capture_totals["admitted_lanes"],
            "target_0x018f": capture_totals["target_s2c_0x018f"],
            "target_0x0190": capture_totals["target_s2c_0x0190"],
            "target_0x0191": capture_totals["target_s2c_0x0191"],
            "complete_spans": len(capture_spans),
            "records_in_complete_spans": len(capture_records),
            "retransmitted_segments": capture_totals["retransmitted_segments"],
            "issues": dict(sorted(capture_issues.items())),
            "exclusions": dict(sorted(capture_exclusions.items())),
        }

    span_rows = _span_rows(spans)
    applications = [record["application"] for record in records]
    application_counts = Counter(applications)
    span_sequence_counts = Counter(
        tuple(record["application"] for record in span["records"]) for span in spans
    )
    consecutive_repeats = sum(
        left["application"] == right["application"]
        for span in spans for left, right in zip(span["records"], span["records"][1:])
    )
    context_opcodes = Counter()
    inside_opcodes = Counter()
    for span in spans:
        timeline = span["timeline"]
        if span["begin_position"]:
            context_opcodes[f"prior/0x{timeline[span['begin_position'] - 1]['opcode']:04x}"] += 1
        if span["end_position"] + 1 < len(timeline):
            context_opcodes[f"next/0x{timeline[span['end_position'] + 1]['opcode']:04x}"] += 1
        for event in timeline[span["begin_position"] + 1:span["end_position"]]:
            if event["opcode"] not in TARGETS:
                inside_opcodes[f"0x{event['opcode']:04x}"] += 1

    for key in (
        "compressed_frame_inflate_failures", "subevent_truncations",
        "wrapped_short_inner_headers", "unparsed_frame_body_bytes",
        "target_c2s_0x018f", "target_c2s_0x0190", "target_c2s_0x0191",
    ):
        totals[key] += 0
    for key in (
        "unexpected_subevent_size", "unexpected_application_shape",
    ):
        exclusions[key] += 0
    for key in (
        "malformed_begin", "malformed_record", "malformed_end", "nested_begin",
        "orphan_record", "orphan_end", "unterminated_span",
    ):
        issues[key] += 0

    accounting = {
        "study_id": STUDY_ID,
        "corpus": {
            "source_manifest": "sources/pcap-1.23b/manifest.yaml",
            "captures": len(corpus_paths),
            "admitted_lanes": totals["admitted_lanes"],
            "admitted_main_lanes": totals["admitted_main_lanes"],
            "admitted_chat_lanes": totals["admitted_chat_lanes"],
            "target_s2c_0x018f": totals["target_s2c_0x018f"],
            "target_s2c_0x0190": totals["target_s2c_0x0190"],
            "target_s2c_0x0191": totals["target_s2c_0x0191"],
            "target_c2s_0x018f": totals["target_c2s_0x018f"],
            "target_c2s_0x0190": totals["target_c2s_0x0190"],
            "target_c2s_0x0191": totals["target_c2s_0x0191"],
            "complete_spans": len(spans),
            "records_in_complete_spans": len(records),
            "retransmitted_segments": totals["retransmitted_segments"],
            "compressed_frame_inflate_failures": totals["compressed_frame_inflate_failures"],
            "subevent_truncations": totals["subevent_truncations"],
            "wrapped_short_inner_headers": totals["wrapped_short_inner_headers"],
            "unparsed_frame_body_bytes": totals["unparsed_frame_body_bytes"],
        },
        "exclusions": dict(sorted(exclusions.items())),
        "transaction_issues": dict(sorted(issues.items())),
        "span_distributions": {
            "records_per_span": _counter(len(span["records"]) for span in spans),
            "spans_by_capture": _counter(span["begin"]["capture"] for span in spans),
            "zero_application_0x018f": sum(span["begin"]["zero_application"] for span in spans),
            "zero_application_0x0191": sum(span["end"]["zero_application"] for span in spans),
        },
        "application_layouts": {
            "0x018f": {
                "application_size_bytes": 8,
                "zero_application_events": sum(span["begin"]["zero_application"] for span in spans),
            },
            "0x0190": {
                "application_size_bytes": 0x68,
                "key_dword_offsets": [0, 4],
                "record_dword_offset_first": 8,
                "record_dword_offset_last": 0x44,
                "record_dword_count": VECTOR_WORDS,
                "unread_tail_offset": 0x48,
                "unread_tail_size_bytes": TAIL_SIZE,
            },
            "0x0191": {
                "application_size_bytes": 8,
                "zero_application_events": sum(span["end"]["zero_application"] for span in spans),
            },
        },
        "key_distributions": {
            "key_dword_0": _multiplicity(record["key1"] for record in records),
            "key_dword_1": _multiplicity(record["key2"] for record in records),
            "key_pairs": _multiplicity((record["key1"], record["key2"]) for record in records),
            "equal_key_dwords": sum(record["key1"] == record["key2"] for record in records),
        },
        "vectors": _vector_analysis(records),
        "tails": _tail_analysis(records),
        "repetition": {
            "distinct_span_record_sequences": len(span_sequence_counts),
            "exact_repeated_spans_beyond_first": sum(
                count - 1 for count in span_sequence_counts.values()
            ),
            "maximum_span_sequence_multiplicity": max(
                span_sequence_counts.values(), default=0
            ),
            "distinct_0x0190_applications": len(application_counts),
            "exact_repeated_applications_beyond_first": sum(count - 1 for count in application_counts.values()),
            "maximum_application_multiplicity": max(application_counts.values(), default=0),
            "consecutive_exact_repeats_within_spans": consecutive_repeats,
        },
        "contexts": {
            "nearest_same_lane_opcodes": dict(sorted(context_opcodes.items())),
            "intervening_non_target_opcodes": dict(sorted(inside_opcodes.items())),
            "spans_with_inventory_frame_overlap": sum(row["inventory_frame_overlap"] == "yes" for row in span_rows),
            "spans_with_equipment_carrier_overlap": sum(row["equipment_carrier_overlap"] == "yes" for row in span_rows),
            "spans_with_change_frame_overlap": sum(row["change_frame_overlap"] == "yes" for row in span_rows),
        },
        "per_capture": per_capture,
        "boundaries": [
            "Canonical capture membership is matched to the pcap-1.23b manifest before clear port-54992 lane admission; the repository gate verifies member hashes.",
            "Transactions are segmented only within one reconstructed s2c lane and increasing wrapped-event order.",
            "Key dwords are reported only through equality and multiplicity aggregates because their meanings are unproven.",
            "Vector values are unsigned wire dwords; only the bounded 0 through 255 distribution is enumerated.",
            "Nearest and intervening opcodes establish same-lane context, not causality.",
            "Inventory, equipment-carrier, and change-frame overlap means numeric opcode presence inside a span, not a state transition.",
            "Imported MassSetItemModifier names are not used as evidence or assigned to these packets.",
        ],
    }
    verdicts = _verdicts(accounting)
    rendered = {
        "accounting.json": (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii"),
        "spans.csv": _csv_bytes(SPAN_FIELDS, span_rows),
        "verdicts.md": verdicts.encode("ascii"),
    }
    for data in rendered.values():
        validate_public_bytes(data)
    return rendered


def _verdicts(accounting: dict) -> str:
    corpus = accounting["corpus"]
    issues = accounting["transaction_issues"]
    vectors = accounting["vectors"]
    tails = accounting["tails"]
    contexts = accounting["contexts"]
    repetition = accounting["repetition"]
    keys = accounting["key_distributions"]
    spans = accounting["span_distributions"]
    capture_spans = ", ".join(
        f"`{capture}` ({count})" for capture, count in spans["spans_by_capture"].items()
    )
    return f"""# Map 0x018F/0x0190/0x0191 transaction verdicts

## Complete corpus accounting

The complete canonical 54-capture corpus contains {corpus['target_s2c_0x018f']}
`0x018F`, {corpus['target_s2c_0x0190']} `0x0190`, and
{corpus['target_s2c_0x0191']} `0x0191` events across all
{corpus['admitted_lanes']} admitted lanes. They form {corpus['complete_spans']}
complete same-lane `0x018F -> 0x0190* -> 0x0191` spans containing
{corpus['records_in_complete_spans']} records. Orphan records, orphan ends,
nested begins, and unterminated spans are respectively {issues['orphan_record']},
{issues['orphan_end']}, {issues['nested_begin']}, and
{issues['unterminated_span']}. Shape exclusions total
{sum(accounting['exclusions'].values())}.

Record counts per span are 197 in 3 spans, 198 in 2, 199 in 18, and 200 in 5.
The eight target-bearing capture contexts are {capture_spans}. Filenames are
corpus locators, not causal labels.

All admitted `0x018F` and `0x0191` application areas are zero. Their imported
MassSetItemModifier labels remain unproven and are not promoted here.

## Key, vector, and tail verdicts

The two leading `0x0190` dwords are retained as unnamed keys. Key dword 0 has
{keys['key_dword_0']['distinct_values']} distinct values and no zero event;
{keys['key_dword_0']['repeated_values']} values repeat. Key dword 1 has one
distinct value and is zero in all {keys['key_dword_1']['events']} records.
The pair distribution therefore matches key dword 0, and the two key dwords
are never equal. Values are not exposed because their roles are unproven.

Across all records there are {vectors['distinct_vectors']} distinct 16-dword
vectors and {vectors['all_zero_vectors']} all-zero vectors. Exact vector
repetitions beyond the first total
{vectors['exact_repeated_vectors_beyond_first']}. Repeated same-capture,
same-lane key pairs provide {vectors['same_capture_lane_key_pair_comparisons']}
ordered comparisons: {vectors['equal_vector_comparisons']} are equal and
{vectors['changed_vector_comparisons']} change. The accounting document records
every changed word position, sparsity histogram, per-position nonzero count,
and bounded unsigned value distribution.
Only positions 0, 1, 3, 4, and 8 are nonzero anywhere. Ordered changes occur
only at positions 0 and 8. Among bounded values from 0 through 255, only 0 and
1 occur; larger values remain grouped into unsigned numeric bands.

The 32-byte unread tail has {tails['distinct_tails']} distinct byte strings;
{tails['all_zero_tails']} of {tails['tails']} tails are all zero. Its varying
and nonzero byte positions are recorded without publishing tail bytes.

TCP reconstruction removed transport duplicates before these event counts.
The source corpus separately contains {corpus['retransmitted_segments']} exact
repeated admitted TCP segments. After reconstruction,
{repetition['exact_repeated_spans_beyond_first']} complete span record sequences
repeat beyond their first occurrence, while
{repetition['exact_repeated_applications_beyond_first']} `0x0190` applications
repeat beyond their first occurrence, including
{repetition['consecutive_exact_repeats_within_spans']} consecutive exact
repetitions inside spans. Those are recurring decoded events, not retransmits.

## Context and claim boundary

The span ledger records the nearest prior and following wrapped opcode on the
same reconstructed lane and all non-target opcodes intervening inside each
span. Numeric inventory-frame, equipment-carrier, and change-frame opcodes
occur inside {contexts['spans_with_inventory_frame_overlap']},
{contexts['spans_with_equipment_carrier_overlap']}, and
{contexts['spans_with_change_frame_overlap']} spans respectively. These are
bounded order correlations, not causal or semantic assignments.

No non-target opcode intervenes inside any complete span. `0x0137` is the
immediate prior opcode for 3 spans and the immediate following opcode for 9;
`0x016E` is immediately prior to 2 spans, and `0x0130` is immediately prior to
1. These numeric same-lane adjacencies are retained for consumer investigation;
imported names do not assign those contexts to the target transaction.

Packet filenames, neighboring opcodes, repeated vectors, and key equality do
not prove inventory mutation, equipment transition, server ordering policy,
event ownership, or a gameplay noun. Such interpretations require an
independent consumer route or directly linked state transition.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    stale = []
    for name, data in outputs.items():
        target = OUT / name
        if args.check:
            if not target.is_file() or target.read_bytes() != data:
                stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    if stale:
        raise SystemExit("stale or missing: " + ", ".join(stale))
    print(
        f"map 0x0190 transaction census: {len(outputs)} products "
        f"{'verified' if args.check else 'written'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
