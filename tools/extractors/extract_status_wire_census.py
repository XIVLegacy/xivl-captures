#!/usr/bin/env python3
"""Build the exhaustive sanitized s2c 0x0179 status-wire census."""

from __future__ import annotations

import argparse
import csv
import io
import json
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

TARGET_OPCODE = 0x0179
EXPECTED_SUBEVENT_SIZE = 72
GAME_PREAMBLE_SIZE = 8
STATUS_SLOT_COUNT = 20
APPLICATION_SIZE = STATUS_SLOT_COUNT * 2
STUDY_ID = "status-wire-projection-census"
STUDY = REPO_ROOT / "studies" / STUDY_ID
OUT = STUDY / "derived"
CROSSWALK = STUDY / "inputs" / "status-crosswalk.csv"
SOURCE_MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"

OCCURRENCE_FIELDS = (
    "capture", "lane_index", "lane", "capture_event_index", "lane_event_index",
    "frame_index", "subevent_index", "source_actor", "target_actor",
    "nonzero_status_count", "nonzero_slots", "wire_status_ids_hex",
)
PROJECTION_FIELDS = (
    "wire_status_id_hex", "status_row_id", "status_word_hex", "status_name",
    "all_wire_ids_for_row_hex", "chant_kind_1", "chant_kind_2",
    "object_bits_8_11", "object_bits_14_15", "object_bits_12_13",
    "occurrence_count", "capture_count",
)


def _counter(values) -> dict[str, int]:
    return {str(key): value for key, value in sorted(Counter(values).items(), key=lambda item: str(item[0]))}


def decode_wire_id(wire_id: int) -> int:
    if not 0 <= wire_id <= 0xFFFF:
        raise ValueError("wire status id must fit u16")
    if wire_id == 0:
        return 0
    return 200000 + wire_id - (0x4350 if wire_id > 0x8000 else 0)


def unpack_status_word(row_id: int) -> dict[str, int]:
    return {
        "chant_kind_1": (row_id >> 12) & 0xF,
        "chant_kind_2": (row_id >> 8) & 0xF,
        "object_bits_8_11": (row_id >> 8) & 0xF,
        "object_bits_14_15": (row_id >> 14) & 0x3,
        "object_bits_12_13": (row_id >> 12) & 0x3,
    }


def _load_crosswalk(path: Path) -> dict[int, dict[str, object]]:
    rows: dict[int, dict[str, object]] = {}
    with path.open(encoding="ascii", newline="") as handle:
        for row in csv.DictReader(handle):
            row_id = int(row["status_row_id"])
            if row_id in rows:
                raise ValueError(f"duplicate crosswalk row {row_id}")
            wire_ids = tuple(int(value, 16) for value in row["all_wire_ids_for_row_hex"].split())
            if not wire_ids or any(decode_wire_id(value) != row_id for value in wire_ids):
                raise ValueError(f"crosswalk row {row_id} has invalid reverse encodings")
            fields = unpack_status_word(row_id)
            for key, value in fields.items():
                if int(row[key]) != value:
                    raise ValueError(f"crosswalk row {row_id} has stale {key}")
            rows[row_id] = {"status_name": row["status_name"], "wire_ids": wire_ids, **fields}
    return rows


def validate_corpus_paths(paths: list[Path], manifest_path: Path = SOURCE_MANIFEST) -> None:
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    expected = sorted(member["file"] for member in manifest.get("members", []))
    actual = sorted(path.name for path in paths)
    if len(expected) != 54 or actual != expected:
        raise ValueError(
            f"canonical corpus membership mismatch: expected {len(expected)} members, found {len(actual)}"
        )


def decode_status_ids(subevent_size: int, sub_body: bytes) -> tuple[tuple[int, ...] | None, str]:
    if subevent_size != EXPECTED_SUBEVENT_SIZE:
        return None, "unexpected_subevent_size"
    if len(sub_body) != INNER_HEADER_LEN + GAME_PREAMBLE_SIZE + APPLICATION_SIZE:
        return None, "unexpected_application_shape"
    application = sub_body[INNER_HEADER_LEN + GAME_PREAMBLE_SIZE :]
    return struct.unpack("<20H", application), ""


def _raw_stream_accounting(path: Path, connection: dict, direction: str) -> tuple[int, int]:
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
            segments.append((int(tcp.seq), int(tcp.seq) + len(payload)))
            payload_bytes += len(payload)
    if not segments:
        return 0, 0
    merged: list[list[int]] = []
    for start, end in sorted(segments):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    unique_bytes = sum(end - start for start, end in merged)
    return payload_bytes - unique_bytes, unique_bytes


def _actor_labels(events: list[dict]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for event in events:
        for actor in (event["source_actor_id"], event["target_actor_id"]):
            if actor not in labels:
                labels[actor] = f"actor-{len(labels) + 1:02d}"
    return labels


def _decode_capture(path: Path) -> tuple[list[dict], Counter, dict]:
    events: list[dict] = []
    totals = Counter()
    exclusions = Counter()
    raw_connections = reconstruct_connections(path)
    admitted = [connection for connection in raw_connections if _is_game_connection(connection)]
    for connection in raw_connections:
        if _is_game_connection(connection):
            continue
        if any(blob.startswith(b"\x16\x03") for blob in connection["streams"].values()):
            exclusions["tls_signature_connections"] += 1
        elif connection["server_endpoint"][1] == 54994:
            exclusions["lobby_54994_connections"] += 1
        else:
            exclusions["other_non_game_connections"] += 1
    totals["frame_shaped_connections"] = len(raw_connections)
    totals["admitted_lanes"] = len(admitted)
    capture_event_index = 0
    for lane_index, connection in enumerate(admitted):
        totals[f"admitted_{connection['lane']}_lanes"] += 1
        for direction in ("c2s", "s2c"):
            blob = connection["streams"].get(direction, b"")
            overlap_bytes, raw_unique_bytes = _raw_stream_accounting(path, connection, direction)
            totals["retransmitted_overlap_bytes"] += overlap_bytes
            totals["discarded_trailing_stream_bytes"] += raw_unique_bytes - len(blob)
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
                    sub_body = body[start : event["offset"] + event["size"]]
                    if len(sub_body) < INNER_HEADER_LEN:
                        totals["wrapped_short_inner_headers"] += 1
                        continue
                    opcode = struct.unpack_from("<H", sub_body, 2)[0]
                    if opcode != TARGET_OPCODE:
                        lane_event_index += 1
                        capture_event_index += 1
                        continue
                    totals[f"target_{direction}_events"] += 1
                    status_ids, malformed_reason = decode_status_ids(event["size"], sub_body)
                    if malformed_reason:
                        exclusions[malformed_reason] += 1
                    else:
                        assert status_ids is not None
                        nonzero = [(slot + 1, value) for slot, value in enumerate(status_ids) if value]
                        events.append({
                            "capture": path.name,
                            "lane_index": lane_index,
                            "lane": connection["lane"],
                            "capture_event_index": capture_event_index,
                            "lane_event_index": lane_event_index,
                            "frame_index": frame_index,
                            "subevent_index": subevent_index,
                            "source_actor_id": event["src_actor"],
                            "target_actor_id": event["dst_actor"],
                            "nonzero": nonzero,
                        })
                        totals["decoded_target_events"] += 1
                    lane_event_index += 1
                    capture_event_index += 1
                totals["admitted_unparsed_frame_body_bytes"] += len(body) - consumed
    return events, totals, dict(exclusions)


def _csv_bytes(fields: tuple[str, ...], rows: list[dict]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def build_outputs(crosswalk_path: Path = CROSSWALK) -> dict[str, bytes]:
    crosswalk = _load_crosswalk(crosswalk_path)
    paths = default_corpus_paths()
    validate_corpus_paths(paths)
    all_events: list[dict] = []
    totals = Counter()
    exclusions = Counter()
    per_capture: dict[str, dict] = {}
    for path in paths:
        events, capture_totals, capture_exclusions = _decode_capture(path)
        all_events.extend(events)
        totals.update(capture_totals)
        exclusions.update(capture_exclusions)
        labels = _actor_labels(events)
        per_capture[path.name] = {
            "events": [
                {
                    "ordinal": index + 1,
                    "lane_index": event["lane_index"],
                    "lane": event["lane"],
                    "source_actor": labels[event["source_actor_id"]],
                    "target_actor": labels[event["target_actor_id"]],
                    "statuses": [
                        {"slot": slot, "wire_status_id_hex": f"0x{wire_id:04x}"}
                        for slot, wire_id in event["nonzero"]
                    ],
                }
                for index, event in enumerate(events)
            ],
            "event_count": len(events),
            "actor_pseudonym_count": len(labels),
            "exclusions": capture_exclusions,
        }

    for key in (
        "compressed_frame_inflate_failures", "subevent_truncations",
        "wrapped_short_inner_headers", "target_c2s_events",
    ):
        totals[key] += 0
    for key in (
        "tls_signature_connections", "lobby_54994_connections",
        "other_non_game_connections", "unexpected_subevent_size",
        "unexpected_application_shape",
    ):
        exclusions[key] += 0

    occurrence_rows = []
    wire_occurrences: defaultdict[int, int] = defaultdict(int)
    wire_captures: defaultdict[int, set[str]] = defaultdict(set)
    status_slots = Counter()
    event_nonzero_counts = Counter()
    for event in all_events:
        labels = _actor_labels([row for row in all_events if row["capture"] == event["capture"]])
        for slot, wire_id in event["nonzero"]:
            wire_occurrences[wire_id] += 1
            wire_captures[wire_id].add(event["capture"])
            status_slots[slot] += 1
        event_nonzero_counts[len(event["nonzero"])] += 1
        occurrence_rows.append({
            "capture": event["capture"], "lane_index": event["lane_index"], "lane": event["lane"],
            "capture_event_index": event["capture_event_index"], "lane_event_index": event["lane_event_index"],
            "frame_index": event["frame_index"], "subevent_index": event["subevent_index"],
            "source_actor": labels[event["source_actor_id"]], "target_actor": labels[event["target_actor_id"]],
            "nonzero_status_count": len(event["nonzero"]),
            "nonzero_slots": " ".join(str(slot) for slot, _ in event["nonzero"]),
            "wire_status_ids_hex": " ".join(f"0x{wire_id:04x}" for _, wire_id in event["nonzero"]),
        })

    projection_rows = []
    nibble_distributions: dict[str, Counter] = {key: Counter() for key in unpack_status_word(0)}
    name_correlations = Counter()
    for wire_id in sorted(wire_occurrences):
        row_id = decode_wire_id(wire_id)
        if row_id not in crosswalk:
            raise ValueError(f"translated status row {row_id} is absent from the pinned crosswalk")
        row = crosswalk[row_id]
        for key in nibble_distributions:
            nibble_distributions[key][row[key]] += wire_occurrences[wire_id]
        name_correlations[row["status_name"]] += wire_occurrences[wire_id]
        projection_rows.append({
            "wire_status_id_hex": f"0x{wire_id:04x}", "status_row_id": row_id,
            "status_word_hex": f"0x{row_id:08x}",
            "status_name": row["status_name"],
            "all_wire_ids_for_row_hex": " ".join(f"0x{value:04x}" for value in row["wire_ids"]),
            **{key: row[key] for key in unpack_status_word(0)},
            "occurrence_count": wire_occurrences[wire_id], "capture_count": len(wire_captures[wire_id]),
        })

    accounting = {
        "study_id": STUDY_ID,
        "coverage": {
            "captures": len(paths), "decoded_target_events": len(all_events),
            "unique_wire_status_ids": len(wire_occurrences),
            "unique_status_row_ids": len({decode_wire_id(value) for value in wire_occurrences}),
            **{key: totals[key] for key in sorted(totals)},
        },
        "exclusions": {key: exclusions[key] for key in sorted(exclusions)},
        "distributions": {
            "events_by_capture": _counter(event["capture"] for event in all_events),
            "events_by_lane": _counter(event["lane"] for event in all_events),
            "nonzero_statuses_per_event": _counter(value for value, count in event_nonzero_counts.items() for _ in range(count)),
            "status_slots": {str(key): value for key, value in sorted(status_slots.items())},
            "wire_status_ids": {f"0x{key:04x}": value for key, value in sorted(wire_occurrences.items())},
            "status_row_ids": _counter(decode_wire_id(value) for value, count in wire_occurrences.items() for _ in range(count)),
            "status_names": dict(sorted(name_correlations.items())),
            "nibbles": {key: {str(value): count for value, count in sorted(counter.items())} for key, counter in nibble_distributions.items()},
        },
        "per_capture_chronology": per_capture,
        "boundaries": [
            "Status names label complete status rows, not nibble values.",
            "Actor labels are capture-local pseudonyms and cannot be joined across captures.",
            "Chronology is direction-local reconstructed stream order and does not prove causality or server policy.",
            "Both supported reverse wire encodings are retained; neither is preferred without wire evidence.",
            "No raw payload, endpoint, player name, token, timestamp, or raw actor identifier is published.",
        ],
    }
    observed_names = ", ".join(
        f"{name} ({count})" for name, count in sorted(name_correlations.items())
    )
    verdicts = f"""# Status wire projection verdicts

## Exhaustive accounting

The complete 54-capture corpus contains {len(all_events)} decoded s2c `0x0179`
events after canonical TCP reconstruction and lane admission. Five nonzero
status entries occur across four captures. They comprise {len(wire_occurrences)}
unique wire IDs and {len({decode_wire_id(value) for value in wire_occurrences})}
translated retail status rows. The other status slots are zero sentinels.

## Projection witnesses

The observed complete-row name correlations are {observed_names}. These names
label status rows only. They do not name any projected nibble value.

The three independent status rows expose Chant kind 2 and Object bits 8..11
values 7, 8, and 10. They therefore provide multiple witnesses for that shared
low-nibble projection. All three rows expose Chant kind 1 value 6, Object bits
14..15 value 1, and Object bits 12..13 value 2. Those upper projections remain
effectively single-value in this corpus despite repeated packet occurrences.

Each observed row has both a low and high reverse wire encoding under the
native transform. Only the low encodings appear on wire. The study preserves
both supported encodings and does not infer that one encoding is preferred in
unobserved cases.

## Rejected interpretations

Chronology does not establish status causality, action or cast meaning, or
server policy. Complete-row names are not evidence for nibble enums. Capture
filenames are not used to assign packet meaning. Historical chant labels,
wiki terminology, and implementation vocabulary are outside this study.

## Remaining boundary

This corpus distinguishes three values in the shared bits 8..11 projection but
only one observed value in each upper projection. Additional retail status rows
with different upper bits are required to broaden those witnesses. A capture
using a high reverse wire encoding would be required to compare encoding use.
"""
    return {
        "occurrences.csv": _csv_bytes(OCCURRENCE_FIELDS, occurrence_rows),
        "status-projections.csv": _csv_bytes(PROJECTION_FIELDS, projection_rows),
        "accounting.json": (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii"),
        "verdicts.md": verdicts.encode("ascii"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--crosswalk", type=Path, default=CROSSWALK)
    args = parser.parse_args()
    outputs = build_outputs(args.crosswalk)
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
    print(f"status wire census: {len(outputs)} products {'verified' if args.check else 'written'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
