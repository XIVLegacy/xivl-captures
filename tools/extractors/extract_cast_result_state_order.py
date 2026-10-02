#!/usr/bin/env python3
"""Extract same-lane cast property/result/mode/status chronology.

The default command generates canonical study products from retained captures.
Output is sanitized to capture-local actor equality
hashes and numeric wire fields; raw endpoints, actor IDs, and payload bytes
are intentionally excluded.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools" / "extractors"
OBJECTS = Path(
    os.environ.get(
        "XIVL_PCAP_OBJECTS_DIR", REPO_ROOT / "sources" / "pcap-1.23b" / "objects"
    )
)
MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"
OUT = REPO_ROOT / "studies" / "cast-result-state-order" / "derived"

# extract_observations resolves its corpus through this environment variable.
os.environ.setdefault("XIVL_PCAP_OBJECTS_DIR", str(OBJECTS))

sys.path.insert(0, str(TOOLS))
from extract_battle_results import OPCODES as RESULT_OPCODES  # type: ignore  # noqa: E402
from extract_battle_results import decode_packet  # type: ignore  # noqa: E402
from extract_gam_keys import parse_property_block  # type: ignore  # noqa: E402
from extract_observations import (  # type: ignore  # noqa: E402
    INNER_HEADER_LEN,
    SUB_EVENT_CLASS_ACTOR_WRAPPED,
    SUB_EVENT_HEADER_LEN,
    default_corpus_paths,
)
from extract_status_wire_census import decode_status_ids  # type: ignore  # noqa: E402
from extract_streams import maybe_inflate, parse_outer_frames, reconstruct_lanes  # type: ignore  # noqa: E402


TARGET_PROPERTIES = {
    0xF683A451: "cast_command_client",
    0x59C40D5D: "cast_end_client",
}
RELEVANT_OPCODES = {0x0137, 0x0139, 0x013A, 0x013B, 0x013C, 0x0144, 0x0177, 0x0179}
MODE_OPCODE = 0x0144
UNSUPPORTED_CALLBACK_OPCODE = 0x0177
PROPERTY_OPCODE = 0x0137


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def actor_hash(capture: str, actor_id: int) -> str:
    """Stable equality token scoped to one capture without publishing the ID."""
    material = capture.encode("ascii") + b"\0" + struct.pack("<I", actor_id)
    return "actor-h" + hashlib.sha256(material).hexdigest()[:12]


def load_manifest() -> dict:
    import yaml

    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}


def validate_inputs() -> tuple[list[Path], dict, dict]:
    manifest = load_manifest()
    expected = {member["file"]: member for member in manifest.get("members", [])}
    paths = default_corpus_paths()
    if sorted(path.name for path in paths) != sorted(expected):
        raise ValueError("canonical corpus membership differs from manifest")
    input_hashes = {}
    hash_errors = []
    for path in paths:
        actual = sha256(path)
        input_hashes[path.name] = actual
        if actual != expected[path.name]["sha256"]:
            hash_errors.append(
                {"capture": path.name, "reason": "manifest_sha256_mismatch"}
            )
        if path.stat().st_size != expected[path.name]["size_bytes"]:
            hash_errors.append(
                {"capture": path.name, "reason": "manifest_size_mismatch"}
            )
    if hash_errors:
        raise ValueError(f"capture manifest validation failed: {hash_errors}")
    return (
        paths,
        input_hashes,
        {"path": "sources/pcap-1.23b/manifest.yaml", "sha256": sha256(MANIFEST)},
    )


def load_product_rows() -> tuple[dict, dict, dict, dict]:
    property_path = (
        REPO_ROOT
        / "studies"
        / "property-stream-hash-catalog"
        / "derived"
        / "property-records.csv"
    )
    result_path = (
        REPO_ROOT
        / "studies"
        / "battle-result-backfit"
        / "derived"
        / "battle-result-rows.csv"
    )
    status_path = (
        REPO_ROOT
        / "studies"
        / "status-wire-projection-census"
        / "derived"
        / "occurrences.csv"
    )
    property_rows = {}
    with property_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (
                row["capture"],
                int(row["lane_index"]),
                int(row["frame_index"]),
                int(row["subevent_index"]),
                row["property_hash"].lower(),
                int(row["record_in_packet"]),
            )
            property_rows[key] = row
    result_rows = defaultdict(list)
    with result_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (
                row["capture"],
                int(row["lane_index"]),
                int(row["frame_index"]),
                int(row["subevent_index"]),
            )
            result_rows[key].append(row)
    status_rows = {}
    with status_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (
                row["capture"],
                int(row["lane_index"]),
                int(row["frame_index"]),
                int(row["subevent_index"]),
            )
            status_rows[key] = row
    product_hashes = {
        "property_records": {
            "path": "studies/property-stream-hash-catalog/derived/property-records.csv",
            "sha256": sha256(property_path),
        },
        "battle_result_rows": {
            "path": "studies/battle-result-backfit/derived/battle-result-rows.csv",
            "sha256": sha256(result_path),
        },
        "status_occurrences": {
            "path": "studies/status-wire-projection-census/derived/occurrences.csv",
            "sha256": sha256(status_path),
        },
    }
    return property_rows, result_rows, status_rows, product_hashes


def locator(
    capture: str,
    lane_index: int,
    lane: dict,
    frame_index: int,
    frame: dict,
    subevent_index: int,
    lane_event_index: int,
    event: dict,
    opcode: int,
) -> dict:
    return {
        "capture": capture,
        "lane_index": lane_index,
        "lane": lane["lane"],
        "direction": "s2c",
        "lane_event_index": lane_event_index,
        "frame_index": frame_index,
        "frame_offset": frame["offset"],
        "inflated_offset": event["offset"],
        "subevent_index": subevent_index,
        "subevent_size": event["size"],
        "inner_size": event["inner_size"],
        "opcode": f"0x{opcode:04x}",
    }


def decode_mode(app: bytes) -> dict:
    if len(app) != 16:
        raise ValueError(f"0x0144 application length {len(app)} != 16")
    return {
        "application_length": len(app),
        "field0_u24": int.from_bytes(app[0:3], "little"),
        "field3_u8": app[9],
        "field5_u8": app[11],
        "field7_u16": int.from_bytes(app[14:16], "little"),
    }


def decode_status(app: bytes, subevent_size: int) -> dict:
    # Reuse the committed direct decoder and retain only numeric wire IDs.
    sub_body = b"\0" * INNER_HEADER_LEN + b"\0" * 8 + app
    ids, reason = decode_status_ids(subevent_size, sub_body)
    if reason or ids is None:
        raise ValueError(f"0x0179 decoder rejected packet: {reason}")
    return {
        "application_length": len(app),
        "nonzero_status_slots": [index + 1 for index, value in enumerate(ids) if value],
        "nonzero_status_ids": [value for value in ids if value],
    }


def result_key(row: dict) -> tuple:
    return (
        row["capture"],
        int(row["lane_index"]),
        int(row["frame_index"]),
        int(row["subevent_index"]),
    )


def sanitize_result_row(
    row: dict, decoded: dict, index: int, product_rows: list[dict], capture: str
) -> dict:
    if index >= len(product_rows):
        raise ValueError("battle-result product row missing")
    product = product_rows[index]
    if int(product["source_actor_id"]) != decoded["source_actor_id"]:
        raise ValueError("battle-result source actor differs from committed product")
    if int(product["target_actor_id"]) != decoded_row_target(decoded, index):
        raise ValueError("battle-result target actor differs from committed product")
    return {
        "row_index_in_packet": index,
        "target_actor": actor_hash(capture, decoded_row_target(decoded, index)),
        "numeric_value": decoded["rows"][index]["numeric_value"],
        "world_master_text_id": decoded["rows"][index]["world_master_text_id"],
        "effect_id": decoded["rows"][index]["effect_id"],
        "text_param": decoded["rows"][index]["text_param"],
        "row_ordinal_or_filter": decoded["rows"][index]["row_ordinal_or_filter"],
    }


def decoded_row_target(decoded: dict, index: int) -> int:
    return decoded["rows"][index]["target_actor_id"]


def scan_capture(
    path: Path, property_products: dict, result_products: dict, status_products: dict
) -> tuple[list[dict], Counter, Counter, list[dict]]:
    relevant = []
    counts = Counter()
    errors = Counter()
    framing = []
    for lane_index, lane in enumerate(reconstruct_lanes(path)):
        direction_frames = {}
        direction_info = {}
        for direction in ("c2s", "s2c"):
            stream = lane["streams"].get(direction, b"")
            frames = parse_outer_frames(stream)
            complete_frame_bytes = sum(frame["size"] for frame in frames)
            marker1_frames = sum(frame["marker"][1] == 0x01 for frame in frames)
            inflated_frames = sum(
                maybe_inflate(frame["body"]) is not None for frame in frames
            )
            marker0_inflatable = sum(
                frame["marker"][1] != 0x01 and maybe_inflate(frame["body"]) is not None
                for frame in frames
            )
            trailing_bytes = len(stream) - complete_frame_bytes
            if trailing_bytes:
                errors[f"{direction}_frame_trailing_bytes"] += trailing_bytes
            if marker0_inflatable:
                errors["marker0_inflatable_body"] += marker0_inflatable
            direction_frames[direction] = frames
            direction_info[direction] = {
                "stream_bytes": len(stream),
                "frame_count": len(frames),
                "complete_frame_bytes": complete_frame_bytes,
                "trailing_bytes": trailing_bytes,
                "marker1_frames": marker1_frames,
                "inflated_frames": inflated_frames,
                "raw_frames": len(frames) - inflated_frames,
                "marker0_inflatable_body": marker0_inflatable,
                "subevent_frames_checked": 0,
                "subevent_complete_bytes": 0,
                "subevent_trailing_bytes": 0,
            }
        framing.append(
            {
                "lane_index": lane_index,
                "lane": lane["lane"],
                "directions": direction_info,
            }
        )
        s2c_info = direction_info["s2c"]
        lane_event_index = 0
        for frame_index, frame in enumerate(direction_frames["s2c"]):
            inflated = maybe_inflate(frame["body"])
            if frame["marker"][1] == 0x01 and inflated is None:
                errors["compressed_frame_inflate_failure"] += 1
                continue
            body = inflated if inflated is not None else frame["body"]
            offset = 0
            subevent_index = 0
            while offset + SUB_EVENT_HEADER_LEN <= len(body):
                size, event_type = struct.unpack_from("<HH", body, offset)
                if (
                    size == 0
                    or size < SUB_EVENT_HEADER_LEN
                    or offset + size > len(body)
                ):
                    errors["subevent_truncation"] += 1
                    break
                event = {
                    "offset": offset,
                    "size": size,
                    "inner_size": 0,
                    "source_actor_id": struct.unpack_from("<I", body, offset + 4)[0],
                    "target_actor_id": struct.unpack_from("<I", body, offset + 8)[0],
                }
                sub_body = body[offset + SUB_EVENT_HEADER_LEN : offset + size]
                if (
                    event_type == SUB_EVENT_CLASS_ACTOR_WRAPPED
                    and len(sub_body) >= INNER_HEADER_LEN
                ):
                    inner_size, opcode = struct.unpack_from("<HH", sub_body, 0)
                    event["inner_size"] = inner_size
                    counts[f"wrapped_{opcode:04x}"] += 1
                    if opcode in RELEVANT_OPCODES:
                        loc = locator(
                            path.name,
                            lane_index,
                            lane,
                            frame_index,
                            frame,
                            subevent_index,
                            lane_event_index,
                            event,
                            opcode,
                        )
                        # 0x0137, battle-result, and 0x0179 carry the observed
                        # eight-byte game preamble; the 16-byte 0x0144/0x0177
                        # bodies follow the inner header directly.
                        app = sub_body[
                            INNER_HEADER_LEN
                            + (
                                8
                                if opcode in {PROPERTY_OPCODE, *RESULT_OPCODES, 0x0179}
                                else 0
                            ) :
                        ]
                        if opcode == PROPERTY_OPCODE:
                            if size != 168 or len(app) != 136:
                                errors["property_shape_mismatch"] += 1
                            else:
                                records, _, declared = parse_property_block(app)
                                if declared > 136:
                                    errors["property_declared_length_overrun"] += 1
                                for record_index, record in enumerate(records):
                                    prop_id = int(record["id"])
                                    if prop_id not in TARGET_PROPERTIES:
                                        continue
                                    key = (
                                        path.name,
                                        lane_index,
                                        frame_index,
                                        subevent_index,
                                        record["idHex"].lower(),
                                        record_index,
                                    )
                                    product = property_products.get(key)
                                    if product is None:
                                        raise ValueError(
                                            f"target property missing from committed product: {key}"
                                        )
                                    if int(product["value_width"]) != int(
                                        record["size"]
                                    ) or int(product["value_u_le"]) != int.from_bytes(
                                        bytes.fromhex(record["valueHex"]), "little"
                                    ):
                                        raise ValueError(
                                            "target property differs from committed product"
                                        )
                                    if (
                                        event["source_actor_id"]
                                        != event["target_actor_id"]
                                    ):
                                        errors[
                                            "property_source_target_actor_mismatch"
                                        ] += 1
                                        raise ValueError(
                                            "target property source/target actor mismatch"
                                        )
                                    relevant.append(
                                        {
                                            **loc,
                                            "event_kind": "property_write",
                                            "record_index_in_packet": record_index,
                                            "property": TARGET_PROPERTIES[prop_id],
                                            "property_hash": record["idHex"],
                                            "value_width": record["size"],
                                            "value_u_le": int.from_bytes(
                                                bytes.fromhex(record["valueHex"]),
                                                "little",
                                            ),
                                            "source_actor": actor_hash(
                                                path.name, event["source_actor_id"]
                                            ),
                                            "target_actor": actor_hash(
                                                path.name, event["target_actor_id"]
                                            ),
                                            "property_actor": actor_hash(
                                                path.name, event["source_actor_id"]
                                            ),
                                        }
                                    )
                        elif opcode in RESULT_OPCODES:
                            shape, capacity, expected_size = RESULT_OPCODES[opcode]
                            if size != expected_size:
                                errors["result_shape_mismatch"] += 1
                                raise ValueError(
                                    f"{path.name}: 0x{opcode:04x} size {size} != {expected_size}"
                                )
                            header, rows = decode_packet(app, opcode)
                            if (
                                len(app)
                                != expected_size
                                - SUB_EVENT_HEADER_LEN
                                - INNER_HEADER_LEN
                                - 8
                            ):
                                errors["result_application_length_mismatch"] += 1
                                raise ValueError(
                                    "battle-result application length mismatch"
                                )
                            if header["row_count"] > capacity or header[
                                "row_count"
                            ] != len(rows):
                                errors["result_capacity_or_count_mismatch"] += 1
                                raise ValueError(
                                    "battle-result declared capacity/count mismatch"
                                )
                            product_rows = result_products.get(
                                (path.name, lane_index, frame_index, subevent_index), []
                            )
                            if len(product_rows) != len(rows):
                                errors["result_product_row_count_mismatch"] += 1
                                raise ValueError(
                                    "battle-result product row count mismatch"
                                )
                            decoded = {**header, "rows": rows}
                            if header["source_actor_id"] != event["source_actor_id"]:
                                errors["result_source_actor_mismatch"] += 1
                                raise ValueError(
                                    "battle-result source actor differs from wrapped subevent"
                                )
                            relevant.append(
                                {
                                    **loc,
                                    "event_kind": "result_packet",
                                    "shape": shape,
                                    "declared_row_capacity": capacity,
                                    "application_length": len(app),
                                    "source_actor": actor_hash(
                                        path.name, header["source_actor_id"]
                                    ),
                                    "rows": [
                                        sanitize_result_row(
                                            row,
                                            decoded,
                                            index,
                                            product_rows,
                                            path.name,
                                        )
                                        for index, row in enumerate(rows)
                                    ],
                                    "header": {
                                        "effect_or_animation_id": header[
                                            "effect_or_animation_id"
                                        ],
                                        "row_count": header["row_count"],
                                        "header_control_value": header[
                                            "header_control_value"
                                        ],
                                        "command_id": header["command_id"],
                                        "presentation_flags": header[
                                            "presentation_flags"
                                        ],
                                    },
                                }
                            )
                        elif opcode == MODE_OPCODE:
                            if size != 40:
                                errors["mode_shape_mismatch"] += 1
                                raise ValueError("0x0144 shape mismatch")
                            relevant.append(
                                {
                                    **loc,
                                    "event_kind": "mode_update",
                                    "source_actor": actor_hash(
                                        path.name, event["source_actor_id"]
                                    ),
                                    "target_actor": actor_hash(
                                        path.name, event["target_actor_id"]
                                    ),
                                    **decode_mode(app),
                                }
                            )
                        elif opcode == 0x0179:
                            status = decode_status(app, size)
                            status_product = status_products.get(
                                (path.name, lane_index, frame_index, subevent_index)
                            )
                            if status_product is None:
                                errors["status_product_occurrence_missing"] += 1
                                raise ValueError(
                                    "0x0179 occurrence missing from committed status product"
                                )
                            expected_slots = [
                                int(value)
                                for value in status_product["nonzero_slots"].split()
                                if value
                            ]
                            expected_ids = [
                                int(value, 16)
                                for value in status_product[
                                    "wire_status_ids_hex"
                                ].split()
                                if value
                            ]
                            if (
                                expected_slots != status["nonzero_status_slots"]
                                or expected_ids != status["nonzero_status_ids"]
                            ):
                                errors["status_product_projection_mismatch"] += 1
                                raise ValueError(
                                    "0x0179 direct decode differs from committed status product"
                                )
                            relevant.append(
                                {
                                    **loc,
                                    "event_kind": "status_update",
                                    "source_actor": actor_hash(
                                        path.name, event["source_actor_id"]
                                    ),
                                    "target_actor": actor_hash(
                                        path.name, event["target_actor_id"]
                                    ),
                                    **status,
                                }
                            )
                        elif opcode == UNSUPPORTED_CALLBACK_OPCODE:
                            counts["callback_0177_omitted"] += 1
                    elif opcode == UNSUPPORTED_CALLBACK_OPCODE:
                        counts["callback_0177_omitted"] += 1
                lane_event_index += 1
                subevent_index += 1
                offset += size
            s2c_info["subevent_frames_checked"] += 1
            s2c_info["subevent_complete_bytes"] += offset
            subevent_trailing = len(body) - offset
            s2c_info["subevent_trailing_bytes"] += subevent_trailing
            if subevent_trailing:
                errors["s2c_subevent_trailing_bytes"] += subevent_trailing
    relevant.sort(
        key=lambda row: (
            row["lane_index"],
            row["lane_event_index"],
            row.get("record_index_in_packet", -1),
        )
    )
    return relevant, counts, errors, framing


def build_sequences(events_by_capture: dict[str, list[dict]]) -> list[dict]:
    sequences = []
    for capture, events in events_by_capture.items():
        by_lane = defaultdict(list)
        for event in events:
            by_lane[event["lane_index"]].append(event)
        for lane_index, lane_events in by_lane.items():
            writes = [
                event
                for event in lane_events
                if event["event_kind"] == "property_write"
            ]

            def event_position(event: dict) -> tuple[int, int]:
                return (
                    event["lane_event_index"],
                    event.get("record_index_in_packet", -1),
                )

            for anchor in writes:
                if anchor["value_u_le"] == 0:
                    continue
                follow = [
                    event
                    for event in writes
                    if event["property"] == anchor["property"]
                    and event["property_actor"] == anchor["property_actor"]
                    and event_position(event) > event_position(anchor)
                    and event["value_u_le"] == 0
                ]
                close = follow[0] if follow else None
                if close is None:
                    continue

                anchor_position = event_position(anchor)
                close_position = event_position(close)
                interval = [
                    event
                    for event in lane_events
                    if anchor_position <= event_position(event) <= close_position
                ]
                strict_intervening = [
                    event
                    for event in lane_events
                    if anchor_position < event_position(event) < close_position
                ]
                context = [
                    event
                    for event in lane_events
                    if anchor["lane_event_index"] - 8
                    <= event["lane_event_index"]
                    <= close["lane_event_index"] + 8
                ]
                result_packets = [
                    event for event in context if event["event_kind"] == "result_packet"
                ]
                matching_command = (
                    anchor["value_u_le"]
                    if anchor["property"] == "cast_command_client"
                    else None
                )
                matched_results = []
                for packet in result_packets:
                    packet_position = event_position(packet)
                    command_match = (
                        matching_command is not None
                        and packet["header"]["command_id"] == matching_command
                    )
                    source_equal = packet["source_actor"] == anchor["property_actor"]
                    row_target_equal = any(
                        row["target_actor"] == anchor["property_actor"]
                        for row in packet["rows"]
                    )
                    in_interval = anchor_position < packet_position < close_position
                    # Context keeps a preceding same-command packet even when
                    # its actor differs. It is not a matching witness.
                    if not (
                        matching_command is None or command_match or row_target_equal
                    ):
                        continue
                    matched_results.append(
                        {
                            "locator": {
                                key: packet[key]
                                for key in (
                                    "capture",
                                    "lane_index",
                                    "lane_event_index",
                                    "frame_index",
                                    "inflated_offset",
                                    "subevent_index",
                                )
                            },
                            "command_id": packet["header"]["command_id"],
                            "command_match": command_match,
                            "source_actor_equal_property_actor": source_equal,
                            "row_target_equal_property_actor": row_target_equal,
                            "in_interval": in_interval,
                            "matching_command_witness": command_match
                            and source_equal
                            and in_interval,
                            "rows": packet["rows"],
                        }
                    )
                sequences.append(
                    {
                        "capture": capture,
                        "lane_index": lane_index,
                        "property": anchor["property"],
                        "actor_equality": anchor["property_actor"],
                        "anchor_nonzero_write": anchor,
                        "close_zero_write": close,
                        "inclusive_interval_events": interval,
                        "strict_intervening_events": strict_intervening,
                        "bounded_context_events": context,
                        "bounded_result_joins": matched_results,
                        "bounded_command_match_count": sum(
                            1
                            for relation in matched_results
                            if relation["matching_command_witness"]
                        ),
                        "bounded_command_match_actor_equal_count": sum(
                            1
                            for relation in matched_results
                            if relation["matching_command_witness"]
                        ),
                        "target_equality_checked": all(
                            "source_actor_equal_property_actor" in relation
                            and "row_target_equal_property_actor" in relation
                            for relation in matched_results
                        ),
                        "interpretation_boundary": "Wire order is reconstructed s2c order within one admitted lane; it does not prove CPU/UI order or user-action causality.",
                    }
                )
    return sequences


SEQUENCE_FIELDS = (
    "capture",
    "lane_index",
    "actor_equality",
    "property",
    "anchor_frame_index",
    "anchor_subevent_index",
    "anchor_record_index_in_packet",
    "anchor_lane_event_index",
    "anchor_inflated_offset",
    "anchor_value_u_le",
    "close_frame_index",
    "close_subevent_index",
    "close_record_index_in_packet",
    "close_lane_event_index",
    "close_inflated_offset",
    "close_value_u_le",
    "strict_intervening_events",
    "inclusive_interval_events",
    "bounded_context_events",
    "bounded_result_joins",
    "bounded_command_match_count",
    "bounded_command_match_actor_equal_count",
    "matching_command_joins",
    "result_commands",
    "mode_updates",
    "status_updates",
)
EVENT_FIELDS = (
    "capture",
    "lane_index",
    "lane",
    "direction",
    "lane_event_index",
    "frame_index",
    "frame_offset",
    "inflated_offset",
    "subevent_index",
    "subevent_size",
    "inner_size",
    "record_index_in_packet",
    "opcode",
    "event_kind",
    "context_relation",
    "actor_equality",
    "property",
    "property_hash",
    "value_width",
    "value_u_le",
    "command_id",
    "row_count",
    "row_index_in_packet",
    "target_actor",
    "numeric_value",
    "world_master_text_id",
    "effect_id",
    "text_param",
    "row_ordinal_or_filter",
    "nonzero_status_slots",
    "nonzero_status_ids",
    "field0_u24",
    "field3_u8",
    "field5_u8",
    "field7_u16",
)


def _scan_products() -> tuple[dict[str, bytes], dict]:
    paths, input_hashes, manifest_hash = validate_inputs()
    property_products, result_products, status_products, product_hashes = (
        load_product_rows()
    )
    all_events = {}
    census = {}
    framing_by_capture = {}
    errors = Counter()
    omitted = Counter()
    for path in paths:
        events, counts, capture_errors, capture_framing = scan_capture(
            path, property_products, result_products, status_products
        )
        all_events[path.name] = events
        framing_by_capture[path.name] = capture_framing
        census[path.name] = {
            "relevant_event_counts": dict(
                sorted(Counter(event["event_kind"] for event in events).items())
            ),
            "wrapped_opcode_counts": {
                key: value
                for key, value in sorted(counts.items())
                if key.startswith("wrapped_")
            },
            "unsupported_callback_0177_count": counts["callback_0177_omitted"],
        }
        errors.update(
            {f"{path.name}:{key}": value for key, value in capture_errors.items()}
        )
        omitted["callback_0177"] += counts["callback_0177_omitted"]
    events_by_capture = {
        capture: events for capture, events in all_events.items() if events
    }
    sequences = build_sequences(events_by_capture)
    property_events = [
        row
        for row in property_products.values()
        if row["property_hash"].lower() in {"0xf683a451", "0x59c40d5d"}
    ]
    result_inventory = Counter()
    for rows in result_products.values():
        for row in rows:
            result_inventory[(row["capture"], row["opcode"], row["command_id"])] += 1
    status_inventory = Counter(row["capture"] for row in status_products.values())
    cast_packets = sum(
        1
        for events in all_events.values()
        for event in events
        if event["event_kind"] == "property_write"
    )
    result_packets = sum(
        1
        for events in all_events.values()
        for event in events
        if event["event_kind"] == "result_packet"
    )
    accounting = {
        "schema_version": 1,
        "scope": "same admitted s2c connection chronology for retained cast-state properties and bounded result/mode/status joins",
        "input_hashes": {
            "manifest": manifest_hash,
            "captures": input_hashes,
            "products": product_hashes,
            "native_cast_contract": {
                "path": "manifests/cast_chant_presentation.json#activeCastGauge.properties",
                "revision": "b1b36be9678832830bcc319e50a1c061c4ffabe5",
                "sha256": "33b400347c528bea4049f4461e8bd80886f3410cd87f9db632305a5e2b6ea375",
            },
            "tools": {
                "extract_streams": {
                    "path": "tools/extractors/extract_streams.py",
                    "sha256": sha256(TOOLS / "extract_streams.py"),
                },
                "extract_property_stream_catalog": {
                    "path": "tools/extractors/extract_property_stream_catalog.py",
                    "sha256": sha256(TOOLS / "extract_property_stream_catalog.py"),
                },
                "extract_battle_results": {
                    "path": "tools/extractors/extract_battle_results.py",
                    "sha256": sha256(TOOLS / "extract_battle_results.py"),
                },
                "extract_status_wire_census": {
                    "path": "tools/extractors/extract_status_wire_census.py",
                    "sha256": sha256(TOOLS / "extract_status_wire_census.py"),
                },
            },
        },
        "coverage": {
            "captures_manifest_members": len(paths),
            "captures_scanned": len(all_events),
            "captures_with_relevant_events": len(events_by_capture),
            "cast_property_records": cast_packets,
            "result_packets_decoded": result_packets,
            "sequences_nonzero_to_zero": len(sequences),
            "unsupported_0177_events_omitted": omitted["callback_0177"],
        },
        "presence_inventory": {
            "property_stream_hash_catalog": {
                "target_rows": len(property_events),
                "target_rows_by_hash": dict(
                    sorted(
                        Counter(
                            row["property_hash"].lower() for row in property_events
                        ).items()
                    )
                ),
                "target_rows_by_capture": dict(
                    sorted(Counter(row["capture"] for row in property_events).items())
                ),
                "target_rows_by_hash_and_value": dict(
                    sorted(
                        Counter(
                            f"{row['property_hash'].lower()}:{row['value_u_le']}"
                            for row in property_events
                        ).items()
                    )
                ),
                "target_rows_by_hash_zero_state": {
                    property_hash: {
                        "nonzero": sum(
                            row["property_hash"].lower() == property_hash
                            and int(row["value_u_le"]) != 0
                            for row in property_events
                        ),
                        "zero": sum(
                            row["property_hash"].lower() == property_hash
                            and int(row["value_u_le"]) == 0
                            for row in property_events
                        ),
                        "nonzero_to_zero_sequences": sum(
                            sequence["property"]
                            == (
                                "cast_command_client"
                                if property_hash == "0xf683a451"
                                else "cast_end_client"
                            )
                            for sequence in sequences
                        ),
                    }
                    for property_hash in ("0xf683a451", "0x59c40d5d")
                },
            },
            "battle_result_backfit": {
                "rows": sum(result_inventory.values()),
                "packets": result_packets,
                "priority_capture_command_rows": {
                    f"{capture}:{opcode}:{command}": count
                    for (capture, opcode, command), count in sorted(
                        result_inventory.items()
                    )
                    if capture
                    in {
                        "party_battle_leve.pcapng",
                        "combat_skills.pcapng",
                        "combat_autoattack.pcapng",
                    }
                    and command == "27346"
                },
            },
            "status_wire_projection_census": {
                "occurrences": sum(status_inventory.values()),
                "captures_with_occurrences": len(status_inventory),
            },
        },
        "census_by_capture": {
            key: value
            for key, value in sorted(census.items())
            if value["relevant_event_counts"]
            or value["unsupported_callback_0177_count"]
        },
        "framing_by_capture": framing_by_capture,
        "errors": dict(sorted(errors.items())),
        "sequences": sequences,
        "boundaries": [
            "Actor equality tokens are capture-local SHA-256-derived identifiers; raw actor identifiers and connection addresses are excluded.",
            "Property labels are retained catalog labels for the two requested hashes; values are decoded little-endian u32 observations.",
            "Mode 0x0144 fields remain generic numeric wire fields; no chant-setter meaning is assigned.",
            "0x0177 callback events are counted and omitted because no committed direct decoder is available in this capture repository.",
            "Packet order is reconstructed s2c order within one admitted connection and direction; it does not establish CPU/UI order or user-action causality.",
        ],
    }
    _reject_diagnostics(accounting)
    return {"accounting": accounting, "sequences": sequences}


def _reject_diagnostics(accounting: dict) -> None:
    errors = accounting.get("errors", {})
    if errors:
        raise ValueError(f"refusing products with parse diagnostics: {errors}")


def _render_products(accounting: dict, sequences: list[dict]) -> dict[str, bytes]:
    accounting_bytes = (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode(
        "ascii"
    )
    sequence_handle = io.StringIO(newline="")
    sequence_writer = csv.DictWriter(
        sequence_handle, fieldnames=SEQUENCE_FIELDS, lineterminator="\n"
    )
    sequence_writer.writeheader()
    for sequence in sequences:
        middle = sequence["strict_intervening_events"]
        anchor = sequence["anchor_nonzero_write"]
        close = sequence["close_zero_write"]
        sequence_writer.writerow(
            {
                "capture": sequence["capture"],
                "lane_index": sequence["lane_index"],
                "actor_equality": sequence["actor_equality"],
                "property": sequence["property"],
                "anchor_frame_index": anchor["frame_index"],
                "anchor_subevent_index": anchor["subevent_index"],
                "anchor_record_index_in_packet": anchor.get(
                    "record_index_in_packet", ""
                ),
                "anchor_lane_event_index": anchor["lane_event_index"],
                "anchor_inflated_offset": anchor["inflated_offset"],
                "anchor_value_u_le": anchor["value_u_le"],
                "close_frame_index": close["frame_index"],
                "close_subevent_index": close["subevent_index"],
                "close_record_index_in_packet": close.get("record_index_in_packet", ""),
                "close_lane_event_index": close["lane_event_index"],
                "close_inflated_offset": close["inflated_offset"],
                "close_value_u_le": close["value_u_le"],
                "strict_intervening_events": len(middle),
                "inclusive_interval_events": len(sequence["inclusive_interval_events"]),
                "bounded_context_events": len(sequence["bounded_context_events"]),
                "bounded_result_joins": len(sequence["bounded_result_joins"]),
                "bounded_command_match_count": sequence["bounded_command_match_count"],
                "bounded_command_match_actor_equal_count": sequence[
                    "bounded_command_match_actor_equal_count"
                ],
                "matching_command_joins": sequence["bounded_command_match_count"],
                "result_commands": " ".join(
                    str(event["header"]["command_id"])
                    for event in middle
                    if event["event_kind"] == "result_packet"
                ),
                "mode_updates": sum(
                    event["event_kind"] == "mode_update" for event in middle
                ),
                "status_updates": sum(
                    event["event_kind"] == "status_update" for event in middle
                ),
            }
        )

    event_handle = io.StringIO(newline="")
    event_writer = csv.DictWriter(
        event_handle,
        fieldnames=EVENT_FIELDS,
        extrasaction="ignore",
        lineterminator="\n",
    )
    event_writer.writeheader()
    for sequence in sequences:
        anchor = sequence["anchor_nonzero_write"]
        close = sequence["close_zero_write"]
        anchor_position = (
            anchor["lane_event_index"],
            anchor.get("record_index_in_packet", -1),
        )
        close_position = (
            close["lane_event_index"],
            close.get("record_index_in_packet", -1),
        )
        for event in sequence["bounded_context_events"]:
            position = (
                event["lane_event_index"],
                event.get("record_index_in_packet", -1),
            )
            relation = (
                "before_anchor"
                if position < anchor_position
                else "after_close"
                if position > close_position
                else "inclusive_interval"
            )
            base = {
                "capture": event["capture"],
                "lane_index": event["lane_index"],
                "lane": event["lane"],
                "direction": event["direction"],
                "lane_event_index": event["lane_event_index"],
                "frame_index": event["frame_index"],
                "frame_offset": event["frame_offset"],
                "inflated_offset": event["inflated_offset"],
                "subevent_index": event["subevent_index"],
                "subevent_size": event["subevent_size"],
                "inner_size": event["inner_size"],
                "record_index_in_packet": event.get("record_index_in_packet", ""),
                "opcode": event["opcode"],
                "event_kind": event["event_kind"],
                "context_relation": relation,
                "actor_equality": event.get(
                    "property_actor", event.get("source_actor", "")
                ),
                "property": event.get("property", ""),
                "property_hash": event.get("property_hash", ""),
                "value_width": event.get("value_width", ""),
                "value_u_le": event.get("value_u_le", ""),
                "command_id": event.get("header", {}).get("command_id", ""),
                "row_count": event.get("header", {}).get("row_count", ""),
                "nonzero_status_slots": " ".join(
                    str(value) for value in event.get("nonzero_status_slots", [])
                ),
                "nonzero_status_ids": " ".join(
                    str(value) for value in event.get("nonzero_status_ids", [])
                ),
                "field0_u24": event.get("field0_u24", ""),
                "field3_u8": event.get("field3_u8", ""),
                "field5_u8": event.get("field5_u8", ""),
                "field7_u16": event.get("field7_u16", ""),
            }
            rows = event.get("rows") or [None]
            for row in rows:
                event_writer.writerow({**base, **(row or {})})
    return {
        "accounting.json": accounting_bytes,
        "events.csv": event_handle.getvalue().encode("ascii"),
        "sequences.csv": sequence_handle.getvalue().encode("ascii"),
    }


def build_outputs() -> dict[str, bytes]:
    result = _scan_products()
    return _render_products(result["accounting"], result["sequences"])


def validate_public_shape() -> int:
    paths = {
        name: OUT / name for name in ("accounting.json", "events.csv", "sequences.csv")
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        print(
            "cast result state order: missing public products: " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1
    try:
        accounting = json.loads(paths["accounting.json"].read_text(encoding="ascii"))
        _reject_diagnostics(accounting)
        if accounting.get("coverage", {}).get("captures_manifest_members") != 54:
            raise ValueError("coverage does not declare 54 manifest members")
        if accounting.get("coverage", {}).get("sequences_nonzero_to_zero") != 2:
            raise ValueError("sequence count is not two")
        framing = accounting.get("framing_by_capture", {})
        if len(framing) != 54:
            raise ValueError("framing coverage does not declare 54 captures")
        for lanes in framing.values():
            for lane in lanes:
                directions = lane.get("directions", {})
                for direction in ("c2s", "s2c"):
                    info = directions.get(direction, {})
                    if info.get("complete_frame_bytes") != info.get("stream_bytes"):
                        raise ValueError("outer frame prefix has trailing bytes")
                    if info.get("marker0_inflatable_body"):
                        raise ValueError("marker-zero body is unexpectedly inflatable")
                if directions.get("s2c", {}).get("subevent_trailing_bytes"):
                    raise ValueError("s2c subevent prefix has trailing bytes")
        event_header = next(
            csv.reader(
                [paths["events.csv"].read_text(encoding="ascii").splitlines()[0]]
            )
        )
        sequence_header = next(
            csv.reader(
                [paths["sequences.csv"].read_text(encoding="ascii").splitlines()[0]]
            )
        )
        if event_header != list(EVENT_FIELDS) or sequence_header != list(
            SEQUENCE_FIELDS
        ):
            raise ValueError("public CSV header changed")
        for path in paths.values():
            text = path.read_text(encoding="ascii")
            for forbidden in (
                "endpoint",
                "payload",
                "source_actor_id",
                "target_actor_id",
                "valueHex",
                "message_class",
            ):
                if forbidden in text:
                    raise ValueError(f"forbidden public field or label: {forbidden}")
    except (OSError, ValueError, json.JSONDecodeError, IndexError) as exc:
        print(f"cast result state order: public shape invalid: {exc}", file=sys.stderr)
        return 1
    print("cast result state order: public shape valid")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="reproduce and compare restricted products"
    )
    parser.add_argument(
        "--public-shape",
        action="store_true",
        help="validate committed products without restricted inputs",
    )
    args = parser.parse_args()
    if args.public_shape:
        return validate_public_shape()
    products = build_outputs()
    stale = []
    for name, expected in products.items():
        target = OUT / name
        if args.check:
            if not target.is_file() or target.read_bytes() != expected:
                stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)
    if stale:
        print("stale cast result state products: " + ", ".join(stale), file=sys.stderr)
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {len(products)} cast result state products")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
