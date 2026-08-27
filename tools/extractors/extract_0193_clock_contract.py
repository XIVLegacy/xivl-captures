#!/usr/bin/env python3
"""Build the exhaustive sanitized s2c 0x0193 clock/value study."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from decimal import Decimal
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

STUDY_ID = "map-0193-clock-contract"
TARGET_OPCODE = 0x0193
EXPECTED_SUBEVENT_SIZE = 40
PACKET_HEADER_TAIL_SIZE = 8
APPLICATION_SIZE = 8
SENTINEL = 0xFFFFFFFF
WINDOW_RADIUS = 3
SOURCE_MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"
OUT = REPO_ROOT / "studies" / STUDY_ID / "derived"

OCCURRENCE_FIELDS = (
    "occurrence", "capture", "lane_index", "lane", "direction",
    "direction_event_index", "capture_completion_packet", "frame_index",
    "subevent_index", "same_frame_target_ordinal", "same_frame_target_count",
    "subopcode", "packet_header_clock_u32", "application_value_u32",
    "derived_modular_sum_u32", "special_sentinel",
    "header_clock_minus_capture_completion_us",
    "derived_sum_minus_capture_completion_us",
    "header_clock_minus_outer_floor_seconds",
    "outer_value_scaled_minus_capture_completion_us", "prior_same_pair_distance",
)
NEIGHBOR_FIELDS = (
    "occurrence", "capture", "lane_index", "relative_event",
    "neighbor_direction_event_index", "same_frame", "neighbor_frame_index",
    "neighbor_subevent_index", "neighbor_opcode",
    "neighbor_capture_delta_us", "neighbor_clock_minus_anchor_clock",
)
IPV4_RE = re.compile(rb"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
RAW_HEX_RE = re.compile(rb"0x[0-9a-fA-F]{8}(?![0-9a-fA-F])")
TOKEN_RE = re.compile(rb"(?i)(?:token|ticket|authorization|password)")


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
    """Reject endpoint, token, payload, and raw identifier surfaces."""
    if IPV4_RE.search(data):
        raise ValueError("public CSV contains an IPv4-like endpoint")
    if RAW_HEX_RE.search(data):
        raise ValueError("public CSV contains an unsanitized 32-bit hexadecimal value")
    if TOKEN_RE.search(data):
        raise ValueError("public CSV contains a credential-like label")


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


def _capture_time_us(packet) -> int:
    return int(Decimal(str(packet.time)) * 1_000_000)


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
        if payload and ((ip.src, tcp.sport), (ip.dst, tcp.dport)) == expected:
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
    """Return the first captured packet that completes all reconstructed frame bytes."""
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
    expected_len = INNER_HEADER_LEN + PACKET_HEADER_TAIL_SIZE + APPLICATION_SIZE
    if len(sub_body) != expected_len:
        return None, "unexpected_application_shape"
    packet_header_clock, packet_header_reserved = struct.unpack_from("<II", sub_body, INNER_HEADER_LEN)
    if packet_header_reserved != 0:
        return None, "nonzero_packet_header_reserved"
    subopcode, value = struct.unpack_from(
        "<II", sub_body, INNER_HEADER_LEN + PACKET_HEADER_TAIL_SIZE
    )
    return {
        "subopcode": subopcode,
        "packet_header_clock": packet_header_clock,
        "application_value": value,
        "derived_modular_sum": (packet_header_clock + value) & 0xFFFFFFFF,
        "special_sentinel": value == SENTINEL,
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
            spans = _packet_spans(path, connection, direction) if blob else []
            overlap, trailing = _segment_accounting(path, connection, direction)
            totals["retransmitted_overlap_bytes"] += overlap
            totals[f"retransmitted_{direction}_overlap_bytes"] += overlap
            totals["discarded_trailing_stream_bytes"] += trailing
            totals[f"discarded_{direction}_trailing_stream_bytes"] += trailing
            frames = parse_outer_frames(blob)
            totals[f"{direction}_frames"] += len(frames)
            direction_event_index = 0
            for frame_index, frame in enumerate(frames):
                completion = _frame_completion(frame["offset"], frame["size"], spans)
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
                        direction_event_index += 1
                        continue
                    totals[f"{direction}_wrapped_subevents"] += 1
                    start = event["offset"] + SUB_EVENT_HEADER_LEN
                    sub_body = body[start:event["offset"] + event["size"]]
                    if len(sub_body) < INNER_HEADER_LEN:
                        totals["wrapped_short_inner_headers"] += 1
                        direction_event_index += 1
                        continue
                    opcode = struct.unpack_from("<H", sub_body, 2)[0]
                    header_clock = None
                    if len(sub_body) >= INNER_HEADER_LEN + PACKET_HEADER_TAIL_SIZE:
                        header_clock = struct.unpack_from("<I", sub_body, INNER_HEADER_LEN)[0]
                    timeline_event = {
                        "capture": path.name,
                        "lane_index": lane_index,
                        "lane": lane,
                        "direction": direction,
                        "direction_event_index": direction_event_index,
                        "capture_packet_index": completion["packet_index"] + 1,
                        "capture_time_us": completion["capture_time_us"],
                        "outer_value": struct.unpack("<Q", frame["timestamp"])[0],
                        "frame_index": frame_index,
                        "subevent_index": subevent_index,
                        "opcode": opcode,
                        "header_clock": header_clock,
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
                            targets.append({**timeline_event, **decoded})
                            totals["decoded_target_events"] += 1
                    direction_event_index += 1
                totals["admitted_unparsed_frame_body_bytes"] += len(body) - consumed
    return targets, timeline, totals, exclusions


def _annotate_targets(targets: list[dict]) -> None:
    frames: defaultdict[tuple, list[dict]] = defaultdict(list)
    lanes: defaultdict[tuple, list[dict]] = defaultdict(list)
    for target in targets:
        frames[(target["capture"], target["lane_index"], target["direction"], target["frame_index"])].append(target)
        lanes[(target["capture"], target["lane_index"], target["direction"])].append(target)
    for frame_targets in frames.values():
        for ordinal, target in enumerate(frame_targets, 1):
            target["same_frame_target_ordinal"] = ordinal
            target["same_frame_target_count"] = len(frame_targets)
    for lane_targets in lanes.values():
        last_seen: dict[tuple[int, int], int] = {}
        for index, target in enumerate(lane_targets):
            pair = (target["subopcode"], target["application_value"])
            target["prior_same_pair_distance"] = (
                "" if pair not in last_seen else index - last_seen[pair]
            )
            last_seen[pair] = index


def _occurrence_rows(targets: list[dict]) -> list[dict]:
    rows = []
    for occurrence, target in enumerate(targets, 1):
        capture_time_us = target["capture_time_us"]
        header_us = target["packet_header_clock"] * 1_000_000
        derived_us = target["derived_modular_sum"] * 1_000_000
        outer_scaled_us = target["outer_value"] * 1_000
        rows.append({
            "occurrence": occurrence,
            "capture": target["capture"],
            "lane_index": target["lane_index"],
            "lane": target["lane"],
            "direction": target["direction"],
            "direction_event_index": target["direction_event_index"],
            "capture_completion_packet": target["capture_packet_index"],
            "frame_index": target["frame_index"],
            "subevent_index": target["subevent_index"],
            "same_frame_target_ordinal": target["same_frame_target_ordinal"],
            "same_frame_target_count": target["same_frame_target_count"],
            "subopcode": f"0x{target['subopcode']:02x}",
            "packet_header_clock_u32": target["packet_header_clock"],
            "application_value_u32": target["application_value"],
            "derived_modular_sum_u32": target["derived_modular_sum"],
            "special_sentinel": "yes" if target["special_sentinel"] else "no",
            "header_clock_minus_capture_completion_us": header_us - capture_time_us,
            "derived_sum_minus_capture_completion_us": derived_us - capture_time_us,
            "header_clock_minus_outer_floor_seconds": (
                target["packet_header_clock"] - target["outer_value"] // 1000
            ),
            "outer_value_scaled_minus_capture_completion_us": (
                outer_scaled_us - capture_time_us
            ),
            "prior_same_pair_distance": target["prior_same_pair_distance"],
        })
    return rows


def _neighbor_rows(targets: list[dict], timeline: list[dict]) -> list[dict]:
    groups: defaultdict[tuple, list[dict]] = defaultdict(list)
    for event in timeline:
        groups[(event["capture"], event["lane_index"], event["direction"])].append(event)
    rows = []
    for occurrence, target in enumerate(targets, 1):
        group = groups[(target["capture"], target["lane_index"], target["direction"])]
        position = next(
            index for index, event in enumerate(group)
            if event["direction_event_index"] == target["direction_event_index"]
        )
        start = max(0, position - WINDOW_RADIUS)
        end = min(len(group), position + WINDOW_RADIUS + 1)
        for neighbor_position in range(start, end):
            if neighbor_position == position:
                continue
            neighbor = group[neighbor_position]
            clock_delta = ""
            if neighbor["header_clock"] is not None:
                clock_delta = neighbor["header_clock"] - target["packet_header_clock"]
            rows.append({
                "occurrence": occurrence,
                "capture": target["capture"],
                "lane_index": target["lane_index"],
                "relative_event": neighbor_position - position,
                "neighbor_direction_event_index": neighbor["direction_event_index"],
                "same_frame": "yes" if neighbor["frame_index"] == target["frame_index"] else "no",
                "neighbor_frame_index": neighbor["frame_index"],
                "neighbor_subevent_index": neighbor["subevent_index"],
                "neighbor_opcode": f"0x{neighbor['opcode']:04x}",
                "neighbor_capture_delta_us": neighbor["capture_time_us"] - target["capture_time_us"],
                "neighbor_clock_minus_anchor_clock": clock_delta,
            })
    return rows


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
            "decoded_events": len(targets),
            "frame_shaped_connections": capture_totals["frame_shaped_connections"],
            "admitted_lanes": capture_totals["admitted_lanes"],
            "admitted_main_lanes": capture_totals["admitted_main_lanes"],
            "admitted_chat_lanes": capture_totals["admitted_chat_lanes"],
            "target_s2c_events": capture_totals["target_s2c_events"],
            "target_c2s_events": capture_totals["target_c2s_events"],
            "retransmitted_overlap_bytes": capture_totals["retransmitted_overlap_bytes"],
            "discarded_trailing_stream_bytes": capture_totals["discarded_trailing_stream_bytes"],
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
        "unexpected_application_shape", "nonzero_packet_header_reserved",
    ):
        exclusions[key] += 0

    _annotate_targets(all_targets)
    occurrence_rows = _occurrence_rows(all_targets)
    neighbor_rows = _neighbor_rows(all_targets, all_timeline)
    header_deltas = [row["header_clock_minus_capture_completion_us"] for row in occurrence_rows]
    derived_deltas = [row["derived_sum_minus_capture_completion_us"] for row in occurrence_rows]
    outer_deltas = [
        row["outer_value_scaled_minus_capture_completion_us"] for row in occurrence_rows
    ]
    compound_frames = {
        (row["capture"], row["lane_index"], row["frame_index"])
        for row in occurrence_rows if row["same_frame_target_count"] > 1
    }
    repeated_rows = sum(row["prior_same_pair_distance"] != "" for row in occurrence_rows)
    accounting = {
        "study_id": STUDY_ID,
        "corpus": {
            "captures": len(paths),
            "corpus_sha256": _corpus_digest(paths),
            **{key: totals[key] for key in sorted(totals)},
        },
        "exclusions": {key: exclusions[key] for key in sorted(exclusions)},
        "distributions": {
            "events_by_capture": _counter(row["capture"] for row in occurrence_rows),
            "events_by_lane": _counter(row["lane"] for row in occurrence_rows),
            "events_by_direction": _counter(row["direction"] for row in occurrence_rows),
            "subopcodes": _counter(row["subopcode"] for row in occurrence_rows),
            "application_values": _counter(row["application_value_u32"] for row in occurrence_rows),
            "subopcode_value_pairs": _counter(
                f"{row['subopcode']}/{row['application_value_u32']}" for row in occurrence_rows
            ),
            "special_sentinel": _counter(row["special_sentinel"] for row in occurrence_rows),
            "compound_target_frames": len(compound_frames),
            "repeated_same_pair_events": repeated_rows,
        },
        "clock_correlations": {
            "capture_completion_pairs": len(occurrence_rows),
            "header_clock_delta_us_min": min(header_deltas),
            "header_clock_delta_us_max": max(header_deltas),
            "header_clock_delta_us_max_abs": max(abs(value) for value in header_deltas),
            "header_clock_equals_outer_floor_pairs": sum(
                row["header_clock_minus_outer_floor_seconds"] == 0
                for row in occurrence_rows
            ),
            "outer_value_scaled_delta_us_min": min(outer_deltas),
            "outer_value_scaled_delta_us_max": max(outer_deltas),
            "derived_sum_delta_us_min": min(derived_deltas),
            "derived_sum_delta_us_max": max(derived_deltas),
            "target_events_in_login_capture": sum(
                row["capture"] == "login.pcapng" for row in occurrence_rows
            ),
            "same_capture_lobby_clock_pairs": 0,
            "same_session_server_utc_pairs": 0,
        },
        "chronology": {
            "neighborhood_radius": WINDOW_RADIUS,
            "neighborhood_rows": len(neighbor_rows),
            "compound_target_frames": len(compound_frames),
            "repeated_same_pair_events": repeated_rows,
        },
        "per_capture": per_capture,
        "boundaries": [
            "Only canonical clear port-54992 game lanes are admitted; retransmitted bytes are reconstructed once.",
            "Capture deltas use the earliest packet that completes every byte of the reconstructed outer frame.",
            "The packet-header clock is the u32 at game-message header +0x08; the following reserved u32 must be zero.",
            "No target event occurs in login.pcapng, and no public artifact joins another capture to its lobby connection or SERVER_UTC session.",
            "Neighbor rows contain only same-lane wrapped-event order and bounded numeric deltas; they do not establish a state transition or cause.",
            "No raw payload, endpoint address, actor identifier, name, token, session identifier, or capture timestamp field is published; the required header clock and exact delta permit capture-time reconstruction.",
            "Application values and derived sums establish client arithmetic; subopcode nouns, UI divisions, and server policy require their own evidence tiers.",
        ],
    }
    verdicts = f"""# Map 0x0193 clock/value verdicts

## Complete corpus accounting

The complete frozen 54-capture corpus contains {len(all_targets)} valid s2c
`0x0193` events in eight captures after canonical TCP reconstruction. Every
event is a 40-byte wrapped subpacket with an 8-byte application payload. There
are {totals['target_c2s_events']} c2s targets and
{sum(exclusions.values()) - exclusions['tls_signature_connections'] - exclusions['lobby_54994_connections']} malformed target exclusions.

Subopcode `0x12` occurs once with application value 900. Subopcode `0x14`
occurs eight times: value 2 occurs six times and value 15 occurs twice. No
application value is the `0xffffffff` sentinel. One reconstructed outer frame
contains two ordered targets, `0x12/900` followed by `0x14/2`; no same-lane
subopcode/value pair repeats.

## Clock and arithmetic verdict

The packet-header u32 at game-message header `+0x08` equals the floor of the
outer-header numeric value divided by 1000 in all nine events. Together with
the capture-time correlation, this establishes millisecond scaling for that
outer value in these target frames without assigning the outer field globally.
The packet-header value differs
from the earliest
frame-completion capture time by {min(header_deltas)} through
{max(header_deltas)} microseconds across all nine events. Its values therefore
occupy the Unix-compatible whole-second domain evidenced by capture chronology,
not an arbitrary counter domain. For every non-sentinel input, the retail
client arithmetic produces `(header_clock + application_value) mod 2^32`.

The application value is an offset in the packet-header clock's integer unit,
and the arithmetic result is an absolute Unix-compatible sum. The sole
observed `0x12` branch stores that sum as an endpoint; its value 900 produces a
stored endpoint 900.013696 seconds after frame completion. The eight `0x14`
rows prove the same arithmetic inputs, but that setup branch does not persist
or present the derived sum.

## Correlation limits

No target event occurs in `login.pcapng`. The preserved public evidence has no
session identity joining the other eight target-bearing capture files to that capture's
clear lobby client-number observations or to a `SERVER_UTC` launch value, so
the same-session `SERVER_UTC` comparison count is zero. Numeric proximity
across capture files is not promoted to a session link.

The three-event same-lane neighborhoods preserve frame order, completion-time
deltas, and packet-header clock deltas. They contain no canonical event that
independently measures when a derived endpoint is reached. Repeated values in
different capture files are distribution witnesses, not countdown samples.

## Claim boundary

The packet evidence proves complete occurrence accounting, seconds-scale
Unix-compatible header clocks, and the arithmetic domain. Retail client and
Lua evidence can separately identify storage routes and presentation
divisions, but UI text does not name the packet or establish server intent.
This study does not infer eligibility, reset schedules, content availability,
login causality, or authoritative server policy.

## Remaining discriminator

To prove server policy rather than client arithmetic, a preserved same-session
sequence must contain `0x0193`, an independently anchored server clock, and a
directly linked state or presentation transition at the derived value. A
sentinel-bearing packet is separately required to observe the exceptional wire
case. Neither discriminator exists in the frozen corpus.
"""
    occurrence_csv = _csv_bytes(OCCURRENCE_FIELDS, occurrence_rows)
    neighborhood_csv = _csv_bytes(NEIGHBOR_FIELDS, neighbor_rows)
    validate_public_csv(occurrence_csv)
    validate_public_csv(neighborhood_csv)
    return {
        "occurrences.csv": occurrence_csv,
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
    print(f"map 0x0193 clock contract: {len(outputs)} products {'verified' if args.check else 'written'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
