#!/usr/bin/env python3
"""Build the exhaustive sanitized World party-chat 0x00C9 contract."""

from __future__ import annotations

import argparse
import base64
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
    SUB_EVENT_CLASS_ACTOR_WRAPPED,
    SUB_EVENT_HEADER_LEN,
    default_corpus_paths,
    parse_sub_events,
)
from extract_streams import (  # type: ignore  # noqa: E402
    _is_game_connection,
    maybe_inflate,
    parse_outer_frames,
    reconstruct_connections,
)

STUDY_ID = "world-party-chat-00c9-contract"
TARGET_OPCODE = 0x00C9
SOURCE_MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"
LOCATOR_SOURCE = REPO_ROOT / "studies" / "m9-corpus-research" / "derived" / "chat-relay-specimens.csv"
OUT = REPO_ROOT / "studies" / STUDY_ID / "derived"

EXPECTED = {
    "c2s": {"subevent_size": 552, "application_size": 528, "name": None, "message": (12, 512), "tail": (524, 4)},
    "s2c": {"subevent_size": 584, "application_size": 560, "name": (12, 32), "message": (44, 512), "tail": (556, 4)},
}

OCCURRENCE_FIELDS = (
    "occurrence", "capture", "lane_index", "direction", "lane_frame_index",
    "subevent_index", "subevent_size", "outer_size", "single_subevent_frame",
    "source_actor_token", "destination_actor_token", "wrapper_counter_token",
    "header_tag", "opcode", "header_reserved", "chat_group_selector",
    "prefix_reserved", "context_token", "sender_name_token",
    "sender_name_length", "message_token", "message_length",
    "message_utf8_roundtrip", "tail_token", "tail_zero",
)

FIELD_MATRIX_FIELDS = (
    "direction", "layer", "offset_basis", "offset", "application_offset", "width", "wire_type",
    "field", "observed_status", "observed_values", "consumer_boundary",
)

IPV4_RE = re.compile(rb"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
SENSITIVE_RE = re.compile(rb"(?i)(?:authorization|password|private chat|account data|player name|session token)")


def _csv_bytes(fields: tuple[str, ...], rows: list[dict]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("ascii")


def validate_public_bytes(data: bytes) -> None:
    if IPV4_RE.search(data):
        raise ValueError("public product contains an IPv4-like endpoint")
    if SENSITIVE_RE.search(data):
        raise ValueError("public product contains a forbidden sensitive label")
    data.decode("ascii")


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


def validate_corpus_paths(paths: list[Path]) -> None:
    manifest = yaml.safe_load(SOURCE_MANIFEST.read_text(encoding="utf-8")) or {}
    expected = sorted(member["file"] for member in manifest.get("members", []))
    actual = sorted(path.name for path in paths)
    if len(expected) != 54 or actual != expected:
        raise ValueError(f"canonical corpus membership mismatch: expected {len(expected)}, found {len(actual)}")


def _text_field(field: bytes) -> dict:
    nul = field.find(b"\0")
    if nul < 0:
        return {"valid": False, "reason": "missing_nul"}
    if any(field[nul:]):
        return {"valid": False, "reason": "nonzero_after_nul"}
    used = field[:nul]
    try:
        text = used.decode("utf-8")
    except UnicodeDecodeError:
        return {"valid": False, "reason": "not_utf8"}
    if text.encode("utf-8") != used:
        return {"valid": False, "reason": "utf8_roundtrip"}
    return {"valid": True, "length": len(used), "bytes": used}


def decode_subevent(direction: str, raw: bytes) -> dict:
    expected = EXPECTED[direction]
    if len(raw) != expected["subevent_size"]:
        raise ValueError("unexpected_subevent_size")
    size, event_type, source_actor, destination_actor, counter = struct.unpack_from("<HHIII", raw, 0)
    if size != len(raw) or event_type != SUB_EVENT_CLASS_ACTOR_WRAPPED:
        raise ValueError("unexpected_wrapper")
    header_tag, opcode, header_reserved = struct.unpack_from("<HHI", raw, SUB_EVENT_HEADER_LEN)
    if opcode != TARGET_OPCODE:
        raise ValueError("unexpected_opcode")
    application = raw[24:]
    if len(application) != expected["application_size"]:
        raise ValueError("unexpected_application_size")
    selector, prefix_reserved, context = struct.unpack_from("<III", application, 0)
    if header_tag != 0x0014 or header_reserved != 0 or selector != 10 or prefix_reserved != 0:
        raise ValueError("unexpected_invariant")
    name = None
    if expected["name"] is not None:
        offset, width = expected["name"]
        name = _text_field(application[offset:offset + width])
        if not name["valid"]:
            raise ValueError("invalid_sender_name_" + name["reason"])
    message_offset, message_width = expected["message"]
    message = _text_field(application[message_offset:message_offset + message_width])
    if not message["valid"]:
        raise ValueError("invalid_message_" + message["reason"])
    tail_offset, tail_width = expected["tail"]
    tail = application[tail_offset:tail_offset + tail_width]
    return {
        "size": size,
        "event_type": event_type,
        "source_actor": source_actor,
        "destination_actor": destination_actor,
        "counter": counter,
        "header_tag": header_tag,
        "opcode": opcode,
        "header_reserved": header_reserved,
        "selector": selector,
        "prefix_reserved": prefix_reserved,
        "context": context,
        "name": name,
        "message": message,
        "tail": tail,
    }


def _token_map(values: list[bytes | int], prefix: str) -> dict[bytes | int, str]:
    ordered = []
    for value in values:
        if value not in ordered:
            ordered.append(value)
    return {value: f"{prefix}-{index}" for index, value in enumerate(ordered, 1)}


def collect_records(paths: list[Path]) -> tuple[list[dict], dict, dict]:
    records = []
    totals = Counter()
    per_capture = {}
    for path in paths:
        capture = Counter()
        frame_base = {"c2s": 0, "s2c": 0}
        event_base = {"c2s": 0, "s2c": 0}
        stream_base = {"c2s": 0, "s2c": 0}
        connections = reconstruct_connections(path)
        capture["frame_shaped_connections"] = len(connections)
        for connection in connections:
            if not _is_game_connection(connection):
                if any(blob.startswith(b"\x16\x03") for blob in connection["streams"].values()):
                    capture["excluded_tls_connections"] += 1
                elif connection["server_endpoint"][1] == 54994:
                    capture["excluded_lobby_connections"] += 1
                else:
                    capture["excluded_other_connections"] += 1
                continue
            capture["admitted_lanes"] += 1
            capture[f"admitted_{connection['lane']}_lanes"] += 1
            lane_index = capture["admitted_lanes"] - 1
            for direction in ("c2s", "s2c"):
                stream = connection["streams"].get(direction, b"")
                frames = parse_outer_frames(stream)
                capture[f"{direction}_frames"] += len(frames)
                direction_event_index = event_base[direction]
                for frame_index, frame in enumerate(frames):
                    inflated = maybe_inflate(frame["body"])
                    if frame["marker"][1] == 1 and inflated is None:
                        capture["inflate_failures"] += 1
                        continue
                    body = inflated if inflated is not None else frame["body"]
                    events = parse_sub_events(body)
                    for subevent_index, event in enumerate(events):
                        global_event_index = direction_event_index
                        if event.get("type") == SUB_EVENT_CLASS_ACTOR_WRAPPED:
                            direction_event_index += 1
                        if event.get("truncated"):
                            capture["subevent_truncations"] += 1
                            continue
                        capture[f"{direction}_subevents"] += 1
                        if event.get("inner_opcode") != TARGET_OPCODE:
                            continue
                        capture[f"target_{direction}_events"] += 1
                        if connection["lane"] != "chat":
                            capture["target_wrong_lane"] += 1
                            continue
                        if frame["marker"] != b"\x01\x00\x00\x00" or frame["type"] != 1:
                            capture["target_unexpected_outer_header"] += 1
                            continue
                        if frame["size"] != EXPECTED[direction]["subevent_size"] + 16:
                            capture["target_unexpected_outer_size"] += 1
                            continue
                        start = event["offset"]
                        raw = body[start:start + event["size"]]
                        try:
                            decoded = decode_subevent(direction, raw)
                        except ValueError as exc:
                            capture[str(exc)] += 1
                            continue
                        records.append({
                            "capture": path.name,
                            "lane_index": lane_index,
                            "direction": direction,
                            "frame_index": frame_index,
                            "global_frame_index": frame_base[direction] + frame_index,
                            "global_frame_offset": stream_base[direction] + frame["offset"],
                            "global_event_index": global_event_index,
                            "body_offset": event["offset"],
                            "subevent_index": subevent_index,
                            "outer_size": frame["size"],
                            "outer_marker": frame["marker"],
                            "outer_type": frame["type"],
                            "single_subevent_frame": len(events) == 1 and event["offset"] == 0 and event["size"] == len(body),
                            **decoded,
                        })
                        capture["decoded_target_events"] += 1
                frame_base[direction] += len(frames)
                event_base[direction] = direction_event_index
                stream_base[direction] += len(stream)
        per_capture[path.name] = dict(sorted(capture.items()))
        totals.update(capture)
    return records, dict(sorted(totals.items())), per_capture


def validate_locator_coverage(records: list[dict], locator_source: Path = LOCATOR_SOURCE) -> None:
    with locator_source.open(newline="", encoding="ascii") as handle:
        rows = [row for row in csv.DictReader(handle) if row["opcode"].lower() == "0x00c9"]
    expected = {
        (
            row["capture"], row["direction"], int(row["event_index"]),
            int(row["frame_index"]), int(row["frame_offset"], 16),
            int(row["body_offset"], 16), int(row["source_actor"], 16),
            int(row["subevent_size"]),
        )
        for row in rows
    }
    actual = {
        (
            record["capture"], record["direction"], record["global_event_index"],
            record["global_frame_index"], record["global_frame_offset"],
            record["body_offset"], record["source_actor"], record["size"],
        )
        for record in records
    }
    if len(rows) != 37 or len(expected) != 37 or actual != expected:
        raise ValueError("M9 0x00C9 locator coverage changed")


def validate_observed_contract(records: list[dict]) -> None:
    c2s_records = [record for record in records if record["direction"] == "c2s"]
    s2c_records = [record for record in records if record["direction"] == "s2c"]
    if len(c2s_records) != 11 or len(s2c_records) != 26:
        raise ValueError("direction accounting changed")
    if len({record["counter"] for record in c2s_records}) != 1 or not all(record["counter"] != 0 for record in c2s_records):
        raise ValueError("c2s opaque counter contract changed")
    if not all(record["counter"] == 0 for record in s2c_records):
        raise ValueError("s2c zero counter contract changed")
    if not all(record["source_actor"] == record["destination_actor"] for record in c2s_records):
        raise ValueError("c2s wrapper actor equality changed")
    if any(record["source_actor"] == record["destination_actor"] for record in s2c_records):
        raise ValueError("s2c wrapper actor inequality changed")
    if {record["source_actor"] for record in c2s_records} != {record["destination_actor"] for record in s2c_records}:
        raise ValueError("cross-direction wrapper actor relation changed")
    if len({record["context"] for record in c2s_records}) != 1 or len({record["context"] for record in s2c_records}) != 2:
        raise ValueError("opaque context distribution changed")
    if _context_sets_equal_by_capture(records) != {
        "party_battle_leve.pcapng": True,
        "war_quest_update2.pcapng": False,
    }:
        raise ValueError("per-capture context relation changed")
    if len({record["name"]["bytes"] for record in s2c_records}) != 1:
        raise ValueError("s2c sender-name equality class changed")
    if len({record["tail"] for record in c2s_records}) != 2 or any(not any(record["tail"]) for record in c2s_records):
        raise ValueError("c2s opaque tail distribution changed")
    if any(any(record["tail"]) for record in s2c_records):
        raise ValueError("s2c zero tail contract changed")
    if _shared_message_value_count(records) != 1:
        raise ValueError("cross-direction message overlap changed")


def _shared_message_value_count(records: list[dict]) -> int:
    c2s_values = {
        record["message"]["bytes"] for record in records if record["direction"] == "c2s"
    }
    s2c_values = {
        record["message"]["bytes"] for record in records if record["direction"] == "s2c"
    }
    return len(c2s_values & s2c_values)


def _context_sets_equal_by_capture(records: list[dict]) -> dict[str, bool]:
    result = {}
    for capture in sorted({record["capture"] for record in records}):
        c2s_values = {
            record["context"]
            for record in records
            if record["capture"] == capture and record["direction"] == "c2s"
        }
        s2c_values = {
            record["context"]
            for record in records
            if record["capture"] == capture and record["direction"] == "s2c"
        }
        result[capture] = c2s_values == s2c_values
    return result


def _field_matrix() -> list[dict]:
    shared = [
        ("wrapper", "subevent", 0, "", 2, "u16le", "subevent_size", "direction-fixed", "c2s=552; s2c=584", "Use the direction-specific fixed size."),
        ("wrapper", "subevent", 2, "", 2, "u16le", "subevent_type", "invariant", "0x0003", "Actor-wrapped subevent class."),
        ("wrapper", "subevent", 4, "", 4, "u32le", "source_actor", "invariant-per-corpus", "one opaque value per direction; values differ", "Preserve as an opaque wrapper actor field; do not substitute the sender name field."),
        ("wrapper", "subevent", 8, "", 4, "u32le", "destination_actor", "invariant-per-corpus", "one opaque value per direction", "Preserve as an opaque wrapper actor field; semantic ownership is not established."),
        ("wrapper", "subevent", 12, "", 4, "u32le", "counter", "direction-specific", "c2s=one nonzero token; s2c=0", "Neither direction exhibits a sequence."),
        ("game-message", "subevent", 16, "", 2, "u16le", "header_tag", "invariant", "0x0014", "This is a fixed tag, not a packet length."),
        ("game-message", "subevent", 18, "", 2, "u16le", "opcode", "invariant", "0x00c9", "World party-chat opcode on the chat lane."),
        ("game-message", "subevent", 20, "", 4, "u32le", "header_reserved", "invariant", "0", "Write zero."),
        ("application", "subevent", 24, 0, 4, "u32le", "chat_group_selector", "invariant", "10", "Retail client evidence establishes a u32 selector; all retained rows use 10."),
        ("application", "subevent", 28, 4, 4, "u32le", "unknown_zero_u32", "invariant", "0", "Write zero; no noun is supported."),
        ("application", "subevent", 32, 8, 4, "u32le", "unknown_context_u32", "dynamic", "c2s=1 token; s2c=2 tokens", "Preserve or source explicitly; it is not proven to be a stable sender ID or sequence."),
    ]
    rows = []
    for direction in ("c2s", "s2c"):
        outer_size = 568 if direction == "c2s" else 600
        outer_rows = [
            ("outer", "outer-frame", 0, "", 4, "bytes[4]", "marker", "invariant", "01 00 00 00", "Raw chat-lane body in both directions."),
            ("outer", "outer-frame", 4, "", 2, "u16le", "outer_size", "direction-fixed", str(outer_size), "Includes the 16-byte outer header."),
            ("outer", "outer-frame", 6, "", 2, "u16le", "outer_type", "invariant", "1", "Observed chat-lane outer type."),
            ("outer", "outer-frame", 8, "", 8, "u64le", "outer_value", "dynamic", "not published", "Preserve framing value; this study does not classify it as a message sequence."),
            ("outer", "outer-frame", 16, "", outer_size - 16, "bytes", "body", "direction-fixed", "one subevent", "Raw body; no zlib inflation."),
        ]
        for row in outer_rows:
            rows.append(dict(zip(FIELD_MATRIX_FIELDS, (direction, *row))))
        for layer, basis, offset, app_offset, width, wire_type, field, status, values, boundary in shared:
            observed = values if field != "subevent_size" else ("552" if direction == "c2s" else "584")
            observed_status = status
            if field == "counter":
                observed = "one nonzero token" if direction == "c2s" else "0"
            elif field == "unknown_context_u32":
                observed = "1 token" if direction == "c2s" else "2 tokens"
                observed_status = "invariant-per-corpus" if direction == "c2s" else "dynamic"
            rows.append(dict(zip(FIELD_MATRIX_FIELDS, (direction, layer, basis, offset, app_offset, width, wire_type, field, observed_status, observed, boundary))))
        if direction == "c2s":
            extras = [
                (36, 12, 512, "bytes[512]", "message", "dynamic", "11 distinct; lengths 3..92", "NUL-terminated, zero-padded, UTF-8-roundtripping in every retained row."),
                (548, 524, 4, "bytes[4]", "unknown_tail", "dynamic", "2 nonzero tokens; non-monotonic", "Preserve unnamed; do not treat as a sequence."),
            ]
        else:
            extras = [
                (36, 12, 32, "bytes[32]", "sender_name", "invariant-per-corpus", "1 token; length 21", "NUL-terminated, zero-padded sender name; no other sender-identity field is proven."),
                (68, 44, 512, "bytes[512]", "message", "dynamic", "26 distinct; lengths 2..115", "NUL-terminated, zero-padded, UTF-8-roundtripping in every retained row."),
                (580, 556, 4, "bytes[4]", "unknown_tail", "invariant", "all zero", "Write zero; no noun is supported."),
            ]
        for offset, app_offset, width, wire_type, field, status, values, boundary in extras:
            rows.append(dict(zip(FIELD_MATRIX_FIELDS, (direction, "application", "subevent", offset, app_offset, width, wire_type, field, status, values, boundary))))
    return rows


def _synthetic_subevent(direction: str) -> bytes:
    expected = EXPECTED[direction]
    source_actor = 0x01020304
    destination_actor = source_actor if direction == "c2s" else 0x05060708
    counter = 0x21222324 if direction == "c2s" else 0
    application = bytearray(expected["application_size"])
    struct.pack_into("<III", application, 0, 10, 0, 0x11121314)
    if direction == "s2c":
        application[12:12 + len(b"Synthetic Sender\0")] = b"Synthetic Sender\0"
        message_offset = 44
    else:
        message_offset = 12
    application[message_offset:message_offset + len(b"synthetic party message\0")] = b"synthetic party message\0"
    if direction == "c2s":
        application[524:528] = b"\xa1\xb2\xc3\xd4"
    raw = bytearray(expected["subevent_size"])
    struct.pack_into("<HHIII", raw, 0, len(raw), 3, source_actor, destination_actor, counter)
    struct.pack_into("<HHI", raw, 16, 0x14, TARGET_OPCODE, 0)
    raw[24:] = application
    return bytes(raw)


def _normalized_fixtures() -> dict:
    fixtures = []
    for direction in ("c2s", "s2c"):
        raw = _synthetic_subevent(direction)
        decode_subevent(direction, raw)
        fixtures.append({
            "direction": direction,
            "encoding": "base64",
            "synthetic": True,
            "subevent_size": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "subevent": base64.b64encode(raw).decode("ascii"),
        })
    return {
        "format": "xivl-world-party-chat-00c9-synthetic-v1",
        "privacy": "Generated values only; no retained actor, name, message, endpoint, clock, or raw payload value is present.",
        "fixtures": fixtures,
    }


def build_outputs(paths: list[Path] | None = None) -> dict[str, bytes]:
    paths = paths or default_corpus_paths()
    validate_corpus_paths(paths)
    records, totals, per_capture = collect_records(paths)
    if len(records) != 37:
        raise ValueError(f"expected 37 decoded target events, found {len(records)}")
    validate_locator_coverage(records)
    validate_observed_contract(records)

    context_tokens = _token_map([record["context"] for record in records], "context")
    name_values = [record["name"]["bytes"] for record in records if record["name"] is not None]
    name_tokens = _token_map(name_values, "sender-name")
    message_tokens = _token_map([record["message"]["bytes"] for record in records], "message")
    tail_tokens = _token_map([record["tail"] for record in records], "tail")
    counter_tokens = _token_map([record["counter"] for record in records], "counter")
    actor_tokens = _token_map(
        [
            value
            for record in records
            for value in (record["source_actor"], record["destination_actor"])
        ],
        "actor",
    )
    occurrence_rows = []
    for occurrence, record in enumerate(records, 1):
        name = record["name"]
        occurrence_rows.append({
            "occurrence": occurrence,
            "capture": record["capture"],
            "lane_index": record["lane_index"],
            "direction": record["direction"],
            "lane_frame_index": record["frame_index"],
            "subevent_index": record["subevent_index"],
            "subevent_size": record["size"],
            "outer_size": record["outer_size"],
            "single_subevent_frame": str(record["single_subevent_frame"]).lower(),
            "source_actor_token": actor_tokens[record["source_actor"]],
            "destination_actor_token": actor_tokens[record["destination_actor"]],
            "wrapper_counter_token": counter_tokens[record["counter"]],
            "header_tag": "0x0014",
            "opcode": "0x00c9",
            "header_reserved": record["header_reserved"],
            "chat_group_selector": record["selector"],
            "prefix_reserved": record["prefix_reserved"],
            "context_token": context_tokens[record["context"]],
            "sender_name_token": name_tokens[name["bytes"]] if name is not None else "",
            "sender_name_length": name["length"] if name is not None else "",
            "message_token": message_tokens[record["message"]["bytes"]],
            "message_length": record["message"]["length"],
            "message_utf8_roundtrip": "true",
            "tail_token": tail_tokens[record["tail"]],
            "tail_zero": str(not any(record["tail"])).lower(),
        })

    by_direction = {}
    for direction in ("c2s", "s2c"):
        rows = [record for record in records if record["direction"] == direction]
        by_direction[direction] = {
            "events": len(rows),
            "captures": dict(sorted(Counter(record["capture"] for record in rows).items())),
            "subevent_sizes": {str(key): value for key, value in sorted(Counter(record["size"] for record in rows).items())},
            "outer_sizes": {str(key): value for key, value in sorted(Counter(record["outer_size"] for record in rows).items())},
            "single_subevent_frames": sum(record["single_subevent_frame"] for record in rows),
            "source_actor_distinct": len({record["source_actor"] for record in rows}),
            "destination_actor_distinct": len({record["destination_actor"] for record in rows}),
            "context_distinct": len({record["context"] for record in rows}),
            "name_distinct": len({record["name"]["bytes"] for record in rows if record["name"] is not None}),
            "message_distinct": len({record["message"]["bytes"] for record in rows}),
            "message_length_min": min(record["message"]["length"] for record in rows),
            "message_length_max": max(record["message"]["length"] for record in rows),
            "zero_counters": sum(record["counter"] == 0 for record in rows),
            "counter_distinct": len({record["counter"] for record in rows}),
            "zero_tails": sum(not any(record["tail"]) for record in rows),
            "tail_distinct": len({record["tail"] for record in rows}),
        }

    c2s_records = [record for record in records if record["direction"] == "c2s"]
    s2c_records = [record for record in records if record["direction"] == "s2c"]
    context_relations = _context_sets_equal_by_capture(records)
    accounting = {
        "study_id": STUDY_ID,
        "corpus": {
            "captures": len(paths),
            "corpus_sha256": _corpus_digest(paths),
            "decoded_target_events": len(records),
            "target_c2s_events": sum(record["direction"] == "c2s" for record in records),
            "target_s2c_events": sum(record["direction"] == "s2c" for record in records),
            **totals,
        },
        "directions": by_direction,
        "cross_capture_context": {
            "target_captures": len({record["capture"] for record in records}),
            "s2c_context_tokens": len({record["context"] for record in s2c_records}),
            "s2c_sender_name_tokens": len({record["name"]["bytes"] for record in s2c_records}),
            "c2s_s2c_source_actor_values_equal": (
                {record["source_actor"] for record in c2s_records}
                == {record["source_actor"] for record in s2c_records}
            ),
            "c2s_source_equals_destination": all(
                record["source_actor"] == record["destination_actor"] for record in c2s_records
            ),
            "s2c_source_equals_destination": all(
                record["source_actor"] == record["destination_actor"] for record in s2c_records
            ),
            "c2s_source_equals_s2c_destination": (
                {record["source_actor"] for record in c2s_records}
                == {record["destination_actor"] for record in s2c_records}
            ),
            "party_capture_context_sets_equal_across_directions": context_relations["party_battle_leve.pcapng"],
            "war_capture_context_sets_equal_across_directions": context_relations["war_quest_update2.pcapng"],
            "message_values_shared_across_directions": _shared_message_value_count(records),
        },
        "per_capture": per_capture,
        "boundaries": [
            "Opaque actor and context values are normalized to equality-preserving tokens and are not published.",
            "Sender names and message bytes are never published or hashed; only tokens, lengths, termination, padding, and UTF-8 roundtrip status are retained.",
            "The unnamed c2s tail is nonzero and non-monotonic; no sequence interpretation is supported.",
            "The wrapper counter is one invariant nonzero token c2s and zero s2c; no sequence behavior is observed.",
            "The context u32 varies across s2c capture contexts and is not promoted as a stable sender identifier.",
            "Audience membership, moderation, persistence, delivery policy, and server causality are outside this study.",
            "Only World chat-lane 0x00C9 framing is established; Map 0x0003 is a separate route.",
        ],
    }

    verdicts = """# World Party-Chat 0x00C9 Verdicts

## Corpus accounting

The complete 54-member retained corpus contains 37 World chat-lane `0x00C9`
events: 11 c2s and 26 s2c. The c2s rows are nine in
`party_battle_leve.pcapng` and two in `war_quest_update2.pcapng`; the s2c rows
are 25 and one respectively. Every target occupies one raw chat-lane outer
frame and one actor-wrapped subevent. No target occurs on the main lane.

## Direction-specific contract

Both directions use outer type 1 with raw, not zlib-compressed, frame bodies.
The c2s outer/subevent sizes are 568/552 bytes and the s2c sizes are 600/584
bytes. The common 24-byte prefix is the 16-byte actor wrapper followed by tag
`0x0014`, opcode `0x00c9`, and a zero u32. Application bytes begin at subevent
offset 24.

The c2s application is selector u32 10, zero u32, an unnamed u32, a 512-byte
message field, and an unnamed four-byte tail. The s2c application inserts a
32-byte sender-name field before the 512-byte message and ends with four zero
bytes. Every observed name and message has a NUL terminator, zero padding to
field width, and exact UTF-8 roundtrip. This proves the observed encoding; it
does not exclude other byte sequences in unobserved retail messages.

## Identity and sequence boundary

The wrapper exposes distinct u32 source-actor and destination-actor fields, but
their values do not substitute for the s2c sender-name field. The unnamed
application u32 at `+8` has one c2s value and two s2c values across the retained
capture contexts; the same sender-name bytes occur in both files. It is therefore
not promoted as a stable sender identifier. The wrapper counter is one
invariant nonzero value c2s and zero in all s2c rows. The c2s tail has two
nonzero equality classes and is non-monotonic.
Neither field supplies an observed message sequence.

## Bahamut adoption boundary

A retail-shaped recipient packet is World clientbound `0x00C9` on the chat
lane, not Map clientbound `0x0003` on the main lane. A consumer may adopt the
fixed s2c offsets, widths, selector, sender-name buffer, message buffer, and
zero fields in `field-matrix.csv`. It must source or preserve the wrapper actor
values and unnamed context u32 explicitly; this study does not define how a
server synthesizes them. It must not translate the relay into a Map message
type or infer recipients, moderation, persistence, delivery policy, or
causality from these captures.

## Evidence reconciliation

`xivl-client-structs:manifests/symbols.json#BCS-Y-0309` and
`xivl-opcodes:data/client_opcode_semantics.json#c2s-00c9` independently place
the c2s emitter on the Chat forwarder, establish opcode `0x00c9`, the fixed
record extent, a u32 selector, and a 512-byte text field. The capture corpus
establishes the direction-specific wire prefixes and the additional s2c
sender-name field. No client receiver evidence used here assigns a noun to the
remaining context or tail bytes.
"""

    outputs = {
        "accounting.json": (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii"),
        "occurrences.csv": _csv_bytes(OCCURRENCE_FIELDS, occurrence_rows),
        "field-matrix.csv": _csv_bytes(FIELD_MATRIX_FIELDS, _field_matrix()),
        "normalized-fixtures.json": (json.dumps(_normalized_fixtures(), indent=2, sort_keys=True) + "\n").encode("ascii"),
        "verdicts.md": verdicts.encode("ascii"),
    }
    for data in outputs.values():
        validate_public_bytes(data)
    return outputs


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
    print(f"world party-chat 0x00c9 contract: {len(outputs)} products {'verified' if args.check else 'written'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
