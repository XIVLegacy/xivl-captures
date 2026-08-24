#!/usr/bin/env python3
"""Compare the complete retained wire census for 0x00DA, 0x00E0, and 0x00E1."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import struct
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

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
    maybe_inflate,
    parse_outer_frames,
    read_packets,
    reconstruct_lanes,
)

TARGET_OPCODES = (0x00DA, 0x00E0, 0x00E1)
GAME_MESSAGE_PREAMBLE_LEN = 8
WINDOW_RADIUS = 3
STUDY_ID = "map-00da-00e1-comparison"
OUT = REPO_ROOT / "studies" / STUDY_ID / "derived"

OCCURRENCE_FIELDS = [
    "capture", "lane_index", "lane", "direction", "direction_event_index",
    "frame_index", "frame_stream_offset", "capture_packet_index",
    "capture_timestamp_utc", "outer_timestamp_or_seq_hex", "outer_frame_size",
    "inflated_frame_body_size", "subevent_index", "subevent_offset",
    "subevent_size", "subevent_type", "transport_source_actor_id_hex",
    "transport_target_actor_id_hex", "transport_counter_hex", "inner_header_word0",
    "opcode", "inner_reserved_hex", "inner_body_size", "inner_body_hex",
    "inner_payload_size",
    "game_message_preamble_hex", "preamble_word0_u32_hex",
    "preamble_word1_u32_hex", "application_size", "application_hex",
    "application_u16_le", "application_u32_le", "inner_body_sha256",
]

NEIGHBOR_FIELDS = [
    "anchor_index", "capture", "lane_index", "lane", "direction", "opcode",
    "relative_event", "neighbor_direction_event_index", "same_frame",
    "frame_index", "subevent_index", "subevent_offset", "subevent_type",
    "neighbor_opcode", "transport_source_actor_id_hex",
    "transport_target_actor_id_hex", "capture_delta_us", "outer_value_delta",
]

VERDICTS_TEXT = """# Comparative verdicts

## Complete census

The 54-capture canonical clear-game corpus contains 31 `0x00DA` occurrences
across seven captures and three `0x00E1` occurrences across three captures.
All 34 occur server-to-client on the main lane. No target opcode occurs
client-to-server or on a chat or unknown lane.

The same complete admitted corpus contains zero `0x00E0` occurrences in either
direction. `occurrences.csv` therefore has no synthetic `0x00E0` row;
`accounting.json` records the zero census explicitly.

No admitted target occurrence is truncated or lacks the 8-byte inner header or
8-byte game-message preamble. Across the raw reconstructed admitted
connections, the canonical reducer discards 228 trailing bytes: six s2c bytes
in each of 38 captures. The retained complete-frame streams have zero unparsed
bytes. The complete decoder pass also records zero truncated sub-events, zero
wrapped sub-events with a short inner header, and zero compressed-frame
inflation failures.

## Payload distinction

Every `0x00DA` occurrence is a 40-byte sub-event with a 16-byte payload after
the inner header and an 8-byte application body after the shared 8-byte
preamble. Its second application u32 is zero in all 31 occurrences. The first
application u32 has ten distinct values; `0x040C9000` occurs 11 times,
`0x04000FFA` and `0x04000FFB` occur six times each, and the remaining seven
values occur one or two times.

Every `0x00E1` occurrence is a 48-byte sub-event with a 24-byte payload after
the inner header and a 16-byte application body after the shared preamble. All
three exact application byte strings differ. Their fourth application u32 is
zero, while the first three u32 positions vary across the three rows.

The two observed opcode sets share no exact application byte string. Their
different fixed application sizes already distinguish the retained wire
shapes without assigning a noun to either one.

## Actor-identifier relationships

All 34 sub-event transport targets are `0x029B2941`. For `0x00DA`, transport
source equals transport target in 16 of 31 rows; the other 15 rows use 14
distinct source identifiers. For `0x00E1`, source equals target in two of three
rows, while the remaining row uses `0x029B27D3` as source. That source also
appears twice among `0x00DA`, so the two opcode sets share transport actor
identifiers even though their application bodies do not match.

The preamble's first u32 equals neither transport source nor transport target
in any target row. This is a negative numeric equality result, not a semantic
field identification.

## Bounded chronology

No immediate predecessor or follower is invariant for `0x00DA`. Its most
frequent immediate predecessor is `0x0169` in 10 of 31 rows, and its most
frequent immediate follower is `0x0130` in seven of 31. Two `0x00DA` rows are
directly adjacent to each other, contributing one predecessor and one follower
relationship.

Two of the three `0x00E1` rows have `0x0001` immediately before and after. The
remaining row has `0x00CF` immediately before and `0x00CE` immediately after.
This repeated bounded neighborhood does not prove a causal relation or packet
meaning.

`neighborhoods.csv` retains three events on each available side within one
reconstructed connection direction. Same-frame neighbors have zero capture
and outer-value delta and remain ordered only by sub-event offset.

## Claim boundary

Capture and scenario filenames served only to locate rows and are not semantic
evidence. The study promotes numeric opcode identities, byte shapes,
distributions, actor-ID equality, and bounded chronology only. It does not
promote emote, animation, effect, action, or causal packet nouns.
"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def corpus_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("ascii"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def _capture_time_us(packet) -> int:
    return int(Decimal(str(packet.time)) * 1_000_000)


def _timestamp_utc(value_us: int) -> str:
    value = datetime.fromtimestamp(value_us / 1_000_000, tz=timezone.utc)
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _packet_spans(path: Path, connection: dict, direction: str) -> list[dict]:
    """Return capture-ordered spans for one reconstructed connection direction."""
    server = connection["server_endpoint"]
    client = connection["client_endpoint"]
    expected = (server, client) if direction == "s2c" else (client, server)
    matched = []
    for packet_index, packet in enumerate(read_packets(path)):
        if not packet.haslayer("IP") or not packet.haslayer("TCP"):
            continue
        ip = packet["IP"]
        tcp = packet["TCP"]
        payload = bytes(tcp.payload)
        if not payload:
            continue
        if ((ip.src, tcp.sport), (ip.dst, tcp.dport)) != expected:
            continue
        matched.append((int(tcp.seq), len(payload), packet_index, _capture_time_us(packet)))
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


def _frame_completion(frame_offset: int, frame_size: int, spans: list[dict]) -> dict:
    """Return the earliest captured packet that completes all frame bytes."""
    frame_end = frame_offset + frame_size
    covered: list[tuple[int, int]] = []
    for span in sorted(spans, key=lambda row: row["packet_index"]):
        start = max(frame_offset, span["start"])
        end = min(frame_end, span["end"])
        if start >= end:
            continue
        covered.append((start, end))
        merged: list[list[int]] = []
        for interval in sorted(covered):
            if not merged or interval[0] > merged[-1][1]:
                merged.append([interval[0], interval[1]])
            else:
                merged[-1][1] = max(merged[-1][1], interval[1])
        if merged[0][0] == frame_offset and merged[0][1] >= frame_end:
            return span
    raise ValueError(f"captured segments do not complete frame at {frame_offset}")


def _hex32(value: int) -> str:
    return f"0x{value:08x}"


def _word_vector(data: bytes, width: int) -> str:
    if len(data) % width:
        return ""
    code = "H" if width == 2 else "I"
    return " ".join(f"0x{value:0{width * 2}x}" for value in struct.unpack(f"<{len(data) // width}{code}", data))


def _counter(values) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items(), key=lambda row: str(row[0]))}


def _decode_capture(path: Path) -> tuple[list[dict], Counter, dict]:
    events: list[dict] = []
    totals = Counter()
    lane_counts = Counter()
    for lane_index, connection in enumerate(reconstruct_lanes(path)):
        lane_counts[connection["lane"]] += 1
        totals["lanes"] += 1
        for direction in ("c2s", "s2c"):
            blob = connection["streams"].get(direction, b"")
            spans = _packet_spans(path, connection, direction) if blob else []
            direction_event_index = 0
            frames = parse_outer_frames(blob)
            raw_reconstructed_size = max((span["end"] for span in spans), default=0)
            totals[f"{direction}_discarded_trailing_stream_bytes"] += (
                raw_reconstructed_size - len(blob)
            )
            totals[f"{direction}_admitted_unparsed_stream_bytes"] += len(blob) - sum(
                frame["size"] for frame in frames
            )
            for frame_index, frame in enumerate(frames):
                totals[f"{direction}_frames"] += 1
                completion = _frame_completion(frame["offset"], frame["size"], spans)
                body = maybe_inflate(frame["body"])
                if frame["marker"][1] == 0x01 and body is None:
                    totals[f"{direction}_compressed_frame_inflate_failures"] += 1
                if body is None:
                    body = frame["body"]
                parsed = parse_sub_events(body)
                for subevent_index, subevent in enumerate(parsed):
                    if subevent.get("truncated"):
                        totals[f"{direction}_subevent_truncations"] += 1
                        continue
                    totals[f"{direction}_subevents"] += 1
                    opcode = subevent.get("inner_opcode")
                    if subevent["type"] == SUB_EVENT_CLASS_ACTOR_WRAPPED:
                        totals[f"{direction}_wrapped_subevents"] += 1
                        if opcode is None:
                            totals[f"{direction}_wrapped_short_inner_headers"] += 1
                    outer_value = struct.unpack("<Q", frame["timestamp"])[0]
                    event = {
                        "capture": path.name,
                        "lane_index": lane_index,
                        "lane": connection["lane"],
                        "direction": direction,
                        "direction_event_index": direction_event_index,
                        "frame_index": frame_index,
                        "frame_stream_offset": frame["offset"],
                        "capture_packet_index": completion["packet_index"] + 1,
                        "capture_time_us": completion["capture_time_us"],
                        "capture_timestamp_utc": _timestamp_utc(completion["capture_time_us"]),
                        "outer_timestamp_or_seq_hex": frame["timestamp"].hex(),
                        "outer_value": outer_value,
                        "outer_frame_size": frame["size"],
                        "inflated_frame_body_size": len(body),
                        "subevent_index": subevent_index,
                        "subevent_offset": subevent["offset"],
                        "subevent_size": subevent["size"],
                        "subevent_type": subevent["type"],
                        "transport_source_actor_id": subevent["src_actor"],
                        "transport_target_actor_id": subevent["dst_actor"],
                        "transport_counter": subevent["counter"],
                        "inner_header_word0": subevent.get("inner_size"),
                        "opcode_value": opcode,
                    }
                    if opcode is not None:
                        start = subevent["offset"] + SUB_EVENT_HEADER_LEN
                        sub_body = body[start:subevent["offset"] + subevent["size"]]
                        event["sub_body"] = sub_body
                    events.append(event)
                    direction_event_index += 1
    return events, totals, dict(sorted(lane_counts.items()))


def _occurrence_row(event: dict) -> dict:
    sub_body = event["sub_body"]
    inner_payload = sub_body[INNER_HEADER_LEN:]
    preamble = inner_payload[:GAME_MESSAGE_PREAMBLE_LEN]
    application = inner_payload[GAME_MESSAGE_PREAMBLE_LEN:]
    preamble_words = struct.unpack("<II", preamble) if len(preamble) == 8 else (0, 0)
    return {
        "capture": event["capture"],
        "lane_index": event["lane_index"],
        "lane": event["lane"],
        "direction": event["direction"],
        "direction_event_index": event["direction_event_index"],
        "frame_index": event["frame_index"],
        "frame_stream_offset": event["frame_stream_offset"],
        "capture_packet_index": event["capture_packet_index"],
        "capture_timestamp_utc": event["capture_timestamp_utc"],
        "outer_timestamp_or_seq_hex": event["outer_timestamp_or_seq_hex"],
        "outer_frame_size": event["outer_frame_size"],
        "inflated_frame_body_size": event["inflated_frame_body_size"],
        "subevent_index": event["subevent_index"],
        "subevent_offset": event["subevent_offset"],
        "subevent_size": event["subevent_size"],
        "subevent_type": f"0x{event['subevent_type']:04x}",
        "transport_source_actor_id_hex": _hex32(event["transport_source_actor_id"]),
        "transport_target_actor_id_hex": _hex32(event["transport_target_actor_id"]),
        "transport_counter_hex": _hex32(event["transport_counter"]),
        "inner_header_word0": event["inner_header_word0"],
        "opcode": f"0x{event['opcode_value']:04x}",
        "inner_reserved_hex": sub_body[4:8].hex(),
        "inner_body_size": len(sub_body),
        "inner_body_hex": sub_body.hex(),
        "inner_payload_size": len(inner_payload),
        "game_message_preamble_hex": preamble.hex(),
        "preamble_word0_u32_hex": _hex32(preamble_words[0]),
        "preamble_word1_u32_hex": _hex32(preamble_words[1]),
        "application_size": len(application),
        "application_hex": application.hex(),
        "application_u16_le": _word_vector(application, 2),
        "application_u32_le": _word_vector(application, 4),
        "inner_body_sha256": hashlib.sha256(sub_body).hexdigest(),
        "_transport_source_actor_id": event["transport_source_actor_id"],
        "_transport_target_actor_id": event["transport_target_actor_id"],
        "_preamble_word0": preamble_words[0],
        "_application": application,
    }


def _neighbors(all_events: list[dict], occurrences: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for event in all_events:
        groups[(event["capture"], event["lane_index"], event["direction"])].append(event)
    rows = []
    for anchor_index, anchor in enumerate(occurrences):
        group = groups[(anchor["capture"], anchor["lane_index"], anchor["direction"])]
        position = next(i for i, event in enumerate(group) if event is anchor)
        for neighbor_position in range(max(0, position - WINDOW_RADIUS), min(len(group), position + WINDOW_RADIUS + 1)):
            if neighbor_position == position:
                continue
            neighbor = group[neighbor_position]
            neighbor_opcode = neighbor.get("opcode_value")
            rows.append({
                "anchor_index": anchor_index,
                "capture": anchor["capture"],
                "lane_index": anchor["lane_index"],
                "lane": anchor["lane"],
                "direction": anchor["direction"],
                "opcode": f"0x{anchor['opcode_value']:04x}",
                "relative_event": neighbor_position - position,
                "neighbor_direction_event_index": neighbor["direction_event_index"],
                "same_frame": "yes" if neighbor["frame_index"] == anchor["frame_index"] else "no",
                "frame_index": neighbor["frame_index"],
                "subevent_index": neighbor["subevent_index"],
                "subevent_offset": neighbor["subevent_offset"],
                "subevent_type": f"0x{neighbor['subevent_type']:04x}",
                "neighbor_opcode": f"0x{neighbor_opcode:04x}" if neighbor_opcode is not None else "",
                "transport_source_actor_id_hex": _hex32(neighbor["transport_source_actor_id"]),
                "transport_target_actor_id_hex": _hex32(neighbor["transport_target_actor_id"]),
                "capture_delta_us": neighbor["capture_time_us"] - anchor["capture_time_us"],
                "outer_value_delta": neighbor["outer_value"] - anchor["outer_value"],
            })
    return rows


def _distributions(rows: list[dict], neighbors: list[dict]) -> dict:
    result = {}
    for opcode in TARGET_OPCODES:
        key = f"0x{opcode:04x}"
        selected = [row for row in rows if row["opcode"] == key]
        selected_neighbors = [row for row in neighbors if row["opcode"] == key]
        result[key] = {
            "occurrences": len(selected),
            "captures": _counter(row["capture"] for row in selected),
            "lanes": _counter(row["lane"] for row in selected),
            "directions": _counter(row["direction"] for row in selected),
            "subevent_sizes": _counter(row["subevent_size"] for row in selected),
            "inner_header_word0_values": _counter(row["inner_header_word0"] for row in selected),
            "inner_payload_sizes": _counter(row["inner_payload_size"] for row in selected),
            "application_sizes": _counter(row["application_size"] for row in selected),
            "application_hex": _counter(row["application_hex"] for row in selected),
            "application_u16_le": _counter(row["application_u16_le"] for row in selected),
            "application_u32_le": _counter(row["application_u32_le"] for row in selected),
            "transport_source_actor_ids": _counter(row["transport_source_actor_id_hex"] for row in selected),
            "transport_target_actor_ids": _counter(row["transport_target_actor_id_hex"] for row in selected),
            "transport_actor_pairs": _counter(
                f"{row['transport_source_actor_id_hex']}->{row['transport_target_actor_id_hex']}"
                for row in selected
            ),
            "preamble_word0_values": _counter(row["preamble_word0_u32_hex"] for row in selected),
            "relations": {
                "transport_source_equals_target": sum(
                    row["_transport_source_actor_id"] == row["_transport_target_actor_id"]
                    for row in selected
                ),
                "preamble_word0_equals_transport_source": sum(
                    row["_preamble_word0"] == row["_transport_source_actor_id"]
                    for row in selected
                ),
                "preamble_word0_equals_transport_target": sum(
                    row["_preamble_word0"] == row["_transport_target_actor_id"]
                    for row in selected
                ),
                "zero_transport_target": sum(row["_transport_target_actor_id"] == 0 for row in selected),
            },
            "immediate_previous_opcodes": _counter(
                row["neighbor_opcode"] or f"subevent:{row['subevent_type']}"
                for row in selected_neighbors if row["relative_event"] == -1
            ),
            "immediate_following_opcodes": _counter(
                row["neighbor_opcode"] or f"subevent:{row['subevent_type']}"
                for row in selected_neighbors if row["relative_event"] == 1
            ),
        }
    actor_sets = {
        key: set(result[key]["transport_source_actor_ids"]) | set(result[key]["transport_target_actor_ids"])
        for key in result
    }
    result["cross_opcode"] = {
        "shared_transport_actor_ids_0x00da_0x00e1": sorted(actor_sets["0x00da"] & actor_sets["0x00e1"]),
        "shared_application_hex_0x00da_0x00e1": sorted(
            set(result["0x00da"]["application_hex"]) & set(result["0x00e1"]["application_hex"])
        ),
    }
    return result


def build_outputs() -> dict[str, bytes]:
    paths = default_corpus_paths()
    if len(paths) != 54:
        raise ValueError(f"expected complete 54-capture corpus, found {len(paths)}")
    all_events = []
    totals = Counter()
    captures = []
    for path in paths:
        events, capture_totals, lanes = _decode_capture(path)
        all_events.extend(events)
        totals.update(capture_totals)
        captures.append({
            "capture": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "admitted_lanes": lanes,
            "discarded_trailing_stream_bytes": {
                "c2s": capture_totals["c2s_discarded_trailing_stream_bytes"],
                "s2c": capture_totals["s2c_discarded_trailing_stream_bytes"],
            },
            "target_occurrences": {
                f"0x{opcode:04x}": sum(event.get("opcode_value") == opcode for event in events)
                for opcode in TARGET_OPCODES
            },
        })
    occurrences = [event for event in all_events if event.get("opcode_value") in TARGET_OPCODES]
    occurrence_rows = [_occurrence_row(event) for event in occurrences]
    neighbor_rows = _neighbors(all_events, occurrences)
    distributions = _distributions(occurrence_rows, neighbor_rows)
    expected = {
        "captures": 54,
        "lanes": 84,
        "c2s_occurrences": 0,
        "s2c_0x00da": 31,
        "s2c_0x00e0": 0,
        "s2c_0x00e1": 3,
        "subevent_truncations": 0,
        "wrapped_short_inner_headers": 0,
        "target_short_game_message_preambles": 0,
        "discarded_trailing_stream_bytes": 228,
        "admitted_unparsed_stream_bytes": 0,
        "compressed_frame_inflate_failures": 0,
    }
    actual = {
        "captures": len(paths),
        "lanes": totals["lanes"],
        "c2s_occurrences": sum(row["direction"] == "c2s" for row in occurrence_rows),
        "s2c_0x00da": sum(row["direction"] == "s2c" and row["opcode"] == "0x00da" for row in occurrence_rows),
        "s2c_0x00e0": sum(row["direction"] == "s2c" and row["opcode"] == "0x00e0" for row in occurrence_rows),
        "s2c_0x00e1": sum(row["direction"] == "s2c" and row["opcode"] == "0x00e1" for row in occurrence_rows),
        "subevent_truncations": totals["c2s_subevent_truncations"] + totals["s2c_subevent_truncations"],
        "wrapped_short_inner_headers": totals["c2s_wrapped_short_inner_headers"] + totals["s2c_wrapped_short_inner_headers"],
        "target_short_game_message_preambles": sum(
            len(event["sub_body"]) < INNER_HEADER_LEN + GAME_MESSAGE_PREAMBLE_LEN
            for event in occurrences
        ),
        "discarded_trailing_stream_bytes": (
            totals["c2s_discarded_trailing_stream_bytes"]
            + totals["s2c_discarded_trailing_stream_bytes"]
        ),
        "admitted_unparsed_stream_bytes": (
            totals["c2s_admitted_unparsed_stream_bytes"]
            + totals["s2c_admitted_unparsed_stream_bytes"]
        ),
        "compressed_frame_inflate_failures": (
            totals["c2s_compressed_frame_inflate_failures"]
            + totals["s2c_compressed_frame_inflate_failures"]
        ),
    }
    if actual != expected:
        raise ValueError(f"corpus reconciliation changed: {actual}")
    accounting = {
        "schema_version": 1,
        "study": STUDY_ID,
        "coverage": {
            **actual,
            "c2s_frames": totals["c2s_frames"],
            "s2c_frames": totals["s2c_frames"],
            "c2s_subevents": totals["c2s_subevents"],
            "s2c_subevents": totals["s2c_subevents"],
            "c2s_wrapped_subevents": totals["c2s_wrapped_subevents"],
            "s2c_wrapped_subevents": totals["s2c_wrapped_subevents"],
            "occurrence_rows": len(occurrence_rows),
            "neighborhood_rows": len(neighbor_rows),
        },
        "inputs": {
            "source": "pcap-1.23b",
            "corpus_digest_sha256": corpus_digest(paths),
            "captures": captures,
        },
        "distributions": distributions,
        "boundaries": [
            "Only canonical clear port-54992 game lanes are admitted; TLS, lobby, retransmitted duplicate bytes, and non-game connections are excluded upstream.",
            "Capture timestamps identify the earliest packet that completes each reconstructed outer frame.",
            "The outer 8-byte value is retained separately and is not interpreted as wall-clock time.",
            "Chronology is bounded to three preceding and three following sub-events in one reconstructed connection direction.",
            "Application words and actor-ID equality tests are numeric comparisons, not semantic field names or causal claims.",
            "Capture and scenario filenames are not used to assign packet meaning.",
            "The complete admitted corpus contains no 0x00E0 occurrence in either direction; no synthetic occurrence row is emitted.",
        ],
    }
    return {
        "occurrences.csv": csv_bytes(occurrence_rows, OCCURRENCE_FIELDS),
        "neighborhoods.csv": csv_bytes(neighbor_rows, NEIGHBOR_FIELDS),
        "accounting.json": (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii"),
        "verdicts.md": VERDICTS_TEXT.encode("ascii"),
    }


def csv_bytes(rows: list[dict], fields: list[str]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("ascii")


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
                stale.append(str(target))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    if stale:
        print("stale 0x00DA/0x00E1 comparison outputs:\n  " + "\n  ".join(stale))
        return 1
    print(("verified" if args.check else "wrote") + f" {len(outputs)} 0x00DA/0x00E1 comparison artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
