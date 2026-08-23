#!/usr/bin/env python3
"""Extract the bounded main-lane neighborhood around login s2c 0x018A."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import struct
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from extract_observations import (  # type: ignore  # noqa: E402
    INNER_HEADER_LEN,
    SUB_EVENT_CLASS_ACTOR_WRAPPED,
    SUB_EVENT_HEADER_LEN,
    parse_sub_events,
)
from extract_streams import (  # type: ignore  # noqa: E402
    GAME_SERVER_PORT,
    TLS_RECORD_SIGNATURE,
    _is_game_connection,
    maybe_inflate,
    parse_outer_frames,
    read_packets,
    reconstruct_connections,
    reconstruct_lanes,
)

PCAP_OBJECTS = Path(os.environ.get(
    "XIVL_PCAP_OBJECTS_DIR",
    str(REPO_ROOT / "sources" / "pcap-1.23b" / "objects"),
))
CAPTURE = PCAP_OBJECTS / "login.pcapng"
CAPTURE_SHA256 = "28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62"
OPCODE_NAMES = REPO_ROOT / "derived" / "opcode_names.json"
OUT = REPO_ROOT / "studies" / "login-018a-neighborhood" / "derived"
ANCHOR_OPCODE = 0x018A
WINDOW_BEFORE = 6
WINDOW_AFTER = 6

CSV_FIELDS = [
    "scope", "relative_event", "is_anchor", "lane_index", "lane", "direction",
    "direction_event_index", "frame_index", "frame_stream_offset", "subevent_index",
    "subevent_offset", "outer_timestamp_or_seq_hex", "outer_value_delta",
    "capture_packet_index", "capture_delta_us", "opcode", "opcode_name",
    "subevent_size", "subevent_sha256",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _capture_time_us(packet) -> int:
    return int(Decimal(str(packet.time)) * 1_000_000)


def _packet_spans(path: Path, connection: dict, direction: str) -> list[dict]:
    """Map reconstructed offsets to every captured segment that supplied them."""
    server = connection["server_endpoint"]
    client = connection["client_endpoint"]
    packets = read_packets(path)
    matched = []
    for packet_index, packet in enumerate(packets):
        if not packet.haslayer("IP") or not packet.haslayer("TCP"):
            continue
        ip = packet["IP"]
        tcp = packet["TCP"]
        payload = bytes(tcp.payload)
        if not payload:
            continue
        source = (ip.src, tcp.sport)
        target = (ip.dst, tcp.dport)
        expected = (server, client) if direction == "s2c" else (client, server)
        if (source, target) != expected:
            continue
        matched.append((int(tcp.seq), len(payload), packet_index, _capture_time_us(packet)))
    if not matched:
        raise ValueError(f"no packets for {connection['lane']} {direction}")
    initial_sequence = min(row[0] for row in matched)
    return [
        {
            "start": sequence - initial_sequence,
            "end": sequence - initial_sequence + length,
            "packet_index": packet_index,
            "capture_time_us": capture_time_us,
        }
        for sequence, length, packet_index, capture_time_us in matched
    ]


def _frame_packet(frame_offset: int, frame_size: int, spans: list[dict]) -> dict:
    """Find first-byte and full-frame capture witnesses despite retransmits."""
    candidates = [span for span in spans if span["start"] <= frame_offset < span["end"]]
    if not candidates:
        raise ValueError(f"no captured segment covers frame offset {frame_offset}")
    first = min(candidates, key=lambda row: row["packet_index"])
    frame_end = frame_offset + frame_size
    covered: list[tuple[int, int]] = []
    completed = None
    for span in sorted(spans, key=lambda row: row["packet_index"]):
        start = max(frame_offset, span["start"])
        end = min(frame_end, span["end"])
        if start >= end:
            continue
        covered.append((start, end))
        merged = []
        for interval in sorted(covered):
            if not merged or interval[0] > merged[-1][1]:
                merged.append(list(interval))
            else:
                merged[-1][1] = max(merged[-1][1], interval[1])
        if merged[0][0] == frame_offset and merged[0][1] >= frame_end:
            completed = span
            break
    if completed is None:
        raise ValueError(f"captured segments do not complete frame at {frame_offset}")
    return {
        "packet_index": completed["packet_index"],
        "capture_time_us": completed["capture_time_us"],
        "start_packet_index": first["packet_index"],
        "candidate_packet_indexes": sorted({row["packet_index"] for row in candidates}),
    }


def _opcode_names() -> dict[tuple[str, int], str]:
    document = json.loads(OPCODE_NAMES.read_text(encoding="utf-8"))
    names: dict[tuple[str, int], str] = {}
    direction_names = {"c2s": "serverbound", "s2c": "clientbound"}
    for entry in document.get("entries", []):
        if entry.get("service") == "map":
            direction = next(
                (short for short, long_name in direction_names.items()
                 if entry.get("direction") == long_name),
                None,
            )
            if direction is not None:
                names[(direction, int(entry["opcodeHex"], 16))] = entry["name"]
    return names


def collect_events(path: Path = CAPTURE) -> tuple[list[dict], list[dict], list[dict]]:
    """Decode actor-wrapped events without merging directions or connections."""
    names = _opcode_names()
    connections = reconstruct_lanes(path)
    events: list[dict] = []
    frames: list[dict] = []
    for lane_index, connection in enumerate(connections):
        for direction in ("c2s", "s2c"):
            blob = connection["streams"].get(direction, b"")
            spans = _packet_spans(path, connection, direction) if blob else []
            direction_event_index = 0
            for frame_index, frame in enumerate(parse_outer_frames(blob)):
                packet = _frame_packet(frame["offset"], frame["size"], spans)
                wire_value = struct.unpack("<Q", frame["timestamp"])[0]
                frame_record = {
                    "lane_index": lane_index,
                    "lane": connection["lane"],
                    "direction": direction,
                    "frame_index": frame_index,
                    "frame_stream_offset": frame["offset"],
                    "outer_timestamp_or_seq_hex": frame["timestamp"].hex(),
                    "wire_value": wire_value,
                    **packet,
                    "events": [],
                }
                body = maybe_inflate(frame["body"])
                if body is None:
                    body = frame["body"]
                for subevent_index, subevent in enumerate(parse_sub_events(body)):
                    if (
                        subevent.get("truncated")
                        or subevent["type"] != SUB_EVENT_CLASS_ACTOR_WRAPPED
                        or subevent.get("inner_opcode") is None
                    ):
                        continue
                    offset = subevent["offset"]
                    size = subevent["size"]
                    subevent_bytes = body[offset:offset + size]
                    inner_body = subevent_bytes[SUB_EVENT_HEADER_LEN:]
                    if len(inner_body) < INNER_HEADER_LEN:
                        continue
                    opcode = subevent["inner_opcode"]
                    event = {
                        **{key: value for key, value in frame_record.items() if key != "events"},
                        "direction_event_index": direction_event_index,
                        "subevent_index": subevent_index,
                        "subevent_offset": offset,
                        "opcode": opcode,
                        "opcode_name": names.get((direction, opcode), ""),
                        "subevent_size": size,
                        "subevent_sha256": sha256_bytes(subevent_bytes),
                        "inner_body_size": len(inner_body),
                        "inner_body_sha256": sha256_bytes(inner_body),
                    }
                    events.append(event)
                    frame_record["events"].append(event)
                    direction_event_index += 1
                frames.append(frame_record)
    return connections, frames, events


def select_anchor(events: list[dict]) -> dict:
    """Require the capture's sole 0x018A to be clientbound on the main lane."""
    anchors = [event for event in events if event["opcode"] == ANCHOR_OPCODE]
    if len(anchors) != 1:
        raise ValueError(f"expected one admitted 0x018A, found {len(anchors)}")
    anchor = anchors[0]
    if anchor["lane"] != "main" or anchor["direction"] != "s2c":
        raise ValueError("admitted 0x018A is not on the main s2c lane")
    return anchor


def same_lane_window(
    events: list[dict], anchor: dict, before: int = WINDOW_BEFORE, after: int = WINDOW_AFTER,
) -> list[dict]:
    """Return a direction-local window that cannot cross a connection block."""
    lane_events = [
        event for event in events
        if event["lane_index"] == anchor["lane_index"]
        and event["direction"] == anchor["direction"]
    ]
    anchor_position = next(i for i, event in enumerate(lane_events) if event is anchor)
    return lane_events[max(0, anchor_position - before):anchor_position + after + 1]


def _bracketing_frames(frames: list[dict], anchor: dict) -> tuple[dict, dict]:
    candidates = [
        frame for frame in frames
        if frame["lane_index"] == anchor["lane_index"]
        and frame["direction"] == "c2s"
        and frame["wire_value"] != 0
    ]
    previous = max(
        (frame for frame in candidates if frame["wire_value"] < anchor["wire_value"]),
        key=lambda frame: frame["wire_value"],
    )
    following = min(
        (frame for frame in candidates if frame["wire_value"] > anchor["wire_value"]),
        key=lambda frame: frame["wire_value"],
    )
    if not (
        previous["packet_index"] < anchor["packet_index"] < following["packet_index"]
        and previous["capture_time_us"] < anchor["capture_time_us"] < following["capture_time_us"]
    ):
        raise ValueError("wire-value bracket disagrees with capture arrival order")
    return previous, following


def _timeline_rows(events: list[dict], frames: list[dict], anchor: dict) -> list[dict]:
    rows = []
    window = same_lane_window(events, anchor)
    previous, following = _bracketing_frames(frames, anchor)
    groups = [
        ("same-lane-s2c-window", window),
        ("previous-c2s-frame", previous["events"]),
        ("following-c2s-frame", following["events"]),
    ]
    for scope, group in groups:
        for event in group:
            relative = (
                event["direction_event_index"] - anchor["direction_event_index"]
                if scope == "same-lane-s2c-window" else ""
            )
            rows.append({
                "scope": scope,
                "relative_event": relative,
                "is_anchor": "yes" if event is anchor else "no",
                "lane_index": event["lane_index"],
                "lane": event["lane"],
                "direction": event["direction"],
                "direction_event_index": event["direction_event_index"],
                "frame_index": event["frame_index"],
                "frame_stream_offset": event["frame_stream_offset"],
                "subevent_index": event["subevent_index"],
                "subevent_offset": event["subevent_offset"],
                "outer_timestamp_or_seq_hex": event["outer_timestamp_or_seq_hex"],
                "outer_value_delta": event["wire_value"] - anchor["wire_value"],
                "capture_packet_index": event["packet_index"] + 1,
                "capture_delta_us": event["capture_time_us"] - anchor["capture_time_us"],
                "opcode": f"0x{event['opcode']:04X}",
                "opcode_name": event["opcode_name"],
                "subevent_size": event["subevent_size"],
                "subevent_sha256": event["subevent_sha256"],
            })
    return rows


def build_outputs(path: Path = CAPTURE) -> tuple[bytes, bytes]:
    if sha256_file(path) != CAPTURE_SHA256:
        raise ValueError("login.pcapng identity mismatch")
    connections, frames, events = collect_events(path)
    anchor = select_anchor(events)
    previous, following = _bracketing_frames(frames, anchor)
    rows = _timeline_rows(events, frames, anchor)

    raw_connections = reconstruct_connections(path)
    rejected = [connection for connection in raw_connections if not _is_game_connection(connection)]
    raw_ports = Counter(connection["server_endpoint"][1] for connection in raw_connections)
    tls_heads = sum(
        any(blob.startswith(TLS_RECORD_SIGNATURE) for blob in connection["streams"].values())
        for connection in raw_connections
    )
    admitted_counts = Counter(connection["lane"] for connection in connections)
    main_connection = connections[anchor["lane_index"]]
    segment_accounting = {}
    for direction in ("c2s", "s2c"):
        spans = _packet_spans(path, main_connection, direction)
        unique_starts = {span["start"] for span in spans}
        segment_accounting[direction] = {
            "captured_payload_segments": len(spans),
            "unique_reconstructed_starts": len(unique_starts),
            "duplicate_start_segments": len(spans) - len(unique_starts),
        }
    accounting = {
        "schema_version": 1,
        "study": "login-018a-neighborhood",
        "input": {
            "capture": path.name,
            "capture_sha256": CAPTURE_SHA256,
            "opcode_names_file": "derived/opcode_names.json",
            "opcode_names_sha256": sha256_file(OPCODE_NAMES),
        },
        "admission": {
            "game_server_port": GAME_SERVER_PORT,
            "raw_frame_shaped_connections": len(raw_connections),
            "raw_server_port_counts": {str(port): count for port, count in sorted(raw_ports.items())},
            "raw_tls_signature_connections": tls_heads,
            "admitted_connections": len(connections),
            "admitted_lane_counts": dict(sorted(admitted_counts.items())),
            "rejected_connections": len(rejected),
        },
        "main_connection_reconstruction": segment_accounting,
        "anchor": {
            "opcode": "0x018A",
            "opcode_name": anchor["opcode_name"],
            "admitted_occurrences": sum(event["opcode"] == ANCHOR_OPCODE for event in events),
            "lane_index": anchor["lane_index"],
            "lane": anchor["lane"],
            "direction": anchor["direction"],
            "direction_event_index": anchor["direction_event_index"],
            "frame_index": anchor["frame_index"],
            "frame_stream_offset": anchor["frame_stream_offset"],
            "subevent_index": anchor["subevent_index"],
            "subevent_offset": anchor["subevent_offset"],
            "outer_timestamp_or_seq_hex": anchor["outer_timestamp_or_seq_hex"],
            "capture_packet_index": anchor["packet_index"] + 1,
            "frame_start_capture_packet_index": anchor["start_packet_index"] + 1,
            "frame_start_packet_candidates": [i + 1 for i in anchor["candidate_packet_indexes"]],
            "subevent_size": anchor["subevent_size"],
            "subevent_sha256": anchor["subevent_sha256"],
            "inner_body_size": anchor["inner_body_size"],
            "inner_body_sha256": anchor["inner_body_sha256"],
        },
        "same_lane_window": {
            "before": WINDOW_BEFORE,
            "after": WINDOW_AFTER,
            "row_count": sum(row["scope"] == "same-lane-s2c-window" for row in rows),
            "immediate_previous_opcode": next(
                row["opcode"] for row in rows
                if row["scope"] == "same-lane-s2c-window" and row["relative_event"] == -1
            ),
            "immediate_following_opcode": next(
                row["opcode"] for row in rows
                if row["scope"] == "same-lane-s2c-window" and row["relative_event"] == 1
            ),
        },
        "cross_direction_bracket": {
            "previous_c2s": {
                "frame_index": previous["frame_index"],
                "outer_value_delta": previous["wire_value"] - anchor["wire_value"],
                "capture_packet_index": previous["packet_index"] + 1,
                "frame_start_capture_packet_index": previous["start_packet_index"] + 1,
                "capture_delta_us": previous["capture_time_us"] - anchor["capture_time_us"],
                "frame_start_packet_candidates": [i + 1 for i in previous["candidate_packet_indexes"]],
                "opcodes": [f"0x{event['opcode']:04X}" for event in previous["events"]],
            },
            "following_c2s": {
                "frame_index": following["frame_index"],
                "outer_value_delta": following["wire_value"] - anchor["wire_value"],
                "capture_packet_index": following["packet_index"] + 1,
                "frame_start_capture_packet_index": following["start_packet_index"] + 1,
                "capture_delta_us": following["capture_time_us"] - anchor["capture_time_us"],
                "frame_start_packet_candidates": [i + 1 for i in following["candidate_packet_indexes"]],
                "opcodes": [f"0x{event['opcode']:04X}" for event in following["events"]],
            },
            "capture_arrival_agrees_with_wire_value_order": True,
        },
        "boundaries": [
            "Connections and directions are never concatenated for chronology.",
            "Frame arrival uses the earliest capture point at which all frame bytes are present; first-byte witnesses are retained separately.",
            "The outer 8-byte value supplies numeric deltas only; it is not promoted as a wall-clock timestamp.",
            "Opcode 0x018A retains its catalog placeholder because packet chronology does not establish a packet noun.",
        ],
    }

    csv_out = io.StringIO(newline="")
    writer = csv.DictWriter(csv_out, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return (
        csv_out.getvalue().encode("ascii"),
        (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    timeline, accounting = build_outputs()
    outputs = {"timeline.csv": timeline, "accounting.json": accounting}
    stale = []
    for name, data in outputs.items():
        target = OUT / name
        if args.check:
            if not target.is_file() or target.read_bytes() != data:
                stale.append(str(target))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    if stale:
        print("stale login 0x018A timeline outputs:\n  " + "\n  ".join(stale))
        return 1
    print(("verified" if args.check else "wrote") + " 2 login 0x018A timeline artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
