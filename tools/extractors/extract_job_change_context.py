#!/usr/bin/env python3
"""Extract the bounded job-update/request context from retail captures.

The product is an extension of the c2s 0x012d study. It retains decode
locators, numeric application words and actor-equality booleans only; actor
values, endpoints and payload bytes never reach the output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools" / "extractors"
SOURCE_ROOT = REPO_ROOT / "sources" / "pcap-1.23b"
OBJECTS = Path(os.environ.get("XIVL_PCAP_OBJECTS_DIR", SOURCE_ROOT / "objects"))
MANIFEST = SOURCE_ROOT / "manifest.yaml"
OUT = (
    REPO_ROOT
    / "studies"
    / "c2s-012d-event-start"
    / "derived"
    / "job-change-context.json"
)

sys.path.insert(0, str(TOOLS))

JOB_OPCODE = 0x01A4
REQUEST_OPCODE = 0x012D
TARGET_SELECTOR = 0x04000030
PACKED_MASK = 0xFF000FFF
PACKED_VALUE = TARGET_SELECTOR
JOB_REQUEST_APPLICATION_04_LOW16 = 12017
ANIMATION_OPCODES = {0x00DA, 0x00E0, 0x00E1}
COMBAT_OPCODES = {0x0139, 0x013A, 0x013B, 0x013C}
WINDOW = 3


def packed_selector(value: int) -> bool:
    return (value & PACKED_MASK) == PACKED_VALUE


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def typed_tail(data: bytes) -> list[dict]:
    """Decode only the witnessed 12017 integer/nil/terminator shape."""
    values: list[dict] = []
    offset = 0
    while offset < len(data):
        tag_offset = offset
        tag = data[offset]
        offset += 1
        if tag == 0x0F:
            return values + [{"tail_offset": tag_offset, "type": "terminator"}]
        if tag == 0x00:
            if offset + 4 > len(data):
                raise ValueError("12017 typed tail has truncated integer")
            values.append(
                {
                    "tail_offset": tag_offset,
                    "type": "int",
                    "value": int.from_bytes(data[offset : offset + 4], "big"),
                }
            )
            offset += 4
        elif tag == 0x05:
            values.append({"tail_offset": tag_offset, "type": "nil"})
        else:
            raise ValueError(f"unsupported 12017 typed-tail tag 0x{tag:02x}")
    raise ValueError("12017 typed tail has no terminator")


def locator(
    capture: str,
    connection_index: int,
    lane: str,
    direction: str,
    frame_index: int,
    frame_offset: int,
    subevent_index: int,
    subevent_offset: int,
    opcode: int,
) -> dict:
    return {
        "capture": capture,
        "connection_index": connection_index,
        "lane": lane,
        "direction": direction,
        "frame_index": frame_index,
        "frame_stream_offset": frame_offset,
        "subevent_index": subevent_index,
        "subevent_offset": subevent_offset,
        "opcode": f"0x{opcode:04x}",
    }


def output_row(base: dict, event: dict) -> dict:
    return {
        **base,
        "source_equals_destination": event["src_actor"] == event["dst_actor"],
        "_source_actor": event["src_actor"],
        "_destination_actor": event["dst_actor"],
    }


def all_actor_fields_equal(first: dict, second: dict) -> bool:
    return (
        first["_source_actor"]
        == first["_destination_actor"]
        == second["_source_actor"]
        == second["_destination_actor"]
    )


def designated(app: bytes, opcode: int) -> tuple[int, str] | None:
    if opcode in ANIMATION_OPCODES and len(app) >= 4:
        return 0, f"0x{int.from_bytes(app[:4], 'little'):08x}"
    if opcode in COMBAT_OPCODES and len(app) >= 8:
        return 4, f"0x{int.from_bytes(app[4:8], 'little'):08x}"
    return None


def build() -> dict:
    from extract_observations import parse_sub_events  # type: ignore
    from extract_streams import maybe_inflate, parse_outer_frames, reconstruct_lanes  # type: ignore

    manifest_bytes = MANIFEST.read_bytes()
    manifest = yaml.safe_load(manifest_bytes) or {}
    members = manifest.get("members", [])
    if len(members) != 54:
        raise ValueError(f"expected 54 source members, got {len(members)}")
    for member in members:
        path = OBJECTS / member["file"]
        if path.stat().st_size != int(member["size_bytes"]):
            raise ValueError(f"size mismatch: {member['file']}")
        if sha256(path) != member["sha256"]:
            raise ValueError(f"SHA-256 mismatch: {member['file']}")

    jobs: list[dict] = []
    requests: list[dict] = []
    streams: dict[tuple[str, int, str], list[dict]] = {}
    capture_hashes: dict[str, dict] = {}
    stats = Counter()

    for member in members:
        capture = member["file"]
        capture_hashes[capture] = {
            "sha256": member["sha256"],
            "size_bytes": int(member["size_bytes"]),
        }
        path = OBJECTS / capture
        for connection_index, connection in enumerate(reconstruct_lanes(path)):
            for direction, stream in connection["streams"].items():
                event_rows: list[dict] = []
                streams[(capture, connection_index, direction)] = event_rows
                for frame_index, frame in enumerate(parse_outer_frames(stream)):
                    stats["frames"] += 1
                    inflated = maybe_inflate(frame["body"])
                    if (frame["marker"][1] == 1) != (inflated is not None):
                        stats["compression_mismatches"] += 1
                    body = inflated if inflated is not None else frame["body"]
                    events = parse_sub_events(body)
                    complete_events = [
                        event for event in events if not event.get("truncated")
                    ]
                    body_end = (
                        max(
                            event["offset"] + event["size"] for event in complete_events
                        )
                        if complete_events
                        else 0
                    )
                    stats["body_tail_nonzero_bytes"] += sum(
                        byte != 0 for byte in body[body_end:]
                    )
                    for subevent_index, event in enumerate(events):
                        if event.get("truncated"):
                            stats["truncated_subevents"] += 1
                            continue
                        stats["complete_subevents"] += 1
                        event_bytes = body[
                            event["offset"] : event["offset"] + event["size"]
                        ]
                        for relative in range(0, len(event_bytes) - 3):
                            value = int.from_bytes(
                                event_bytes[relative : relative + 4], "little"
                            )
                            if packed_selector(value):
                                stats["packed_any"] += 1
                                stats["exact_any"] += value == TARGET_SELECTOR
                        if event.get("inner_opcode") is None:
                            continue
                        opcode = event["inner_opcode"]
                        app = event_bytes[32:] if len(event_bytes) >= 32 else b""
                        base = locator(
                            capture,
                            connection_index,
                            connection["lane"],
                            direction,
                            frame_index,
                            frame["offset"],
                            subevent_index,
                            event["offset"],
                            opcode,
                        )
                        row = output_row(base, event)
                        row["application_size"] = len(app)
                        field = designated(app, opcode)
                        if field is not None:
                            row["application_offset"], row["designated_value"] = field
                            value = int(field[1], 16)
                            if packed_selector(value):
                                stats["packed_designated"] += 1
                                stats["exact_designated"] += value == TARGET_SELECTOR
                        event_rows.append(row)
                        if opcode == JOB_OPCODE and direction == "s2c":
                            jobs.append({**row, "job_byte": app[0] if app else None})
                        elif (
                            opcode == REQUEST_OPCODE
                            and direction == "c2s"
                            and len(app) >= 8
                        ):
                            owner = int.from_bytes(app[4:8], "little")
                            application_04_low16 = owner & 0xFFFF
                            if (
                                owner >> 24 == 0xA0
                                and application_04_low16
                                == JOB_REQUEST_APPLICATION_04_LOW16
                            ):
                                name = app[0x11 : 0x11 + 32].split(b"\0", 1)[0]
                                requests.append(
                                    {
                                        **row,
                                        "application_04_low16": application_04_low16,
                                        "event_type": app[0x10]
                                        if len(app) > 0x10
                                        else None,
                                        "event_name": name.decode("ascii", "replace"),
                                        "typed_tail_application_offset": 0x31,
                                        "typed_tail": typed_tail(
                                            app[0x31 : 0x31 + 128]
                                        ),
                                    }
                                )

    if any(
        stats[key]
        for key in (
            "truncated_subevents",
            "compression_mismatches",
            "body_tail_nonzero_bytes",
        )
    ):
        raise ValueError("incomplete or inconsistent admitted subevent framing")

    candidate_codes = {f"0x{value:04x}" for value in ANIMATION_OPCODES | COMBAT_OPCODES}
    contexts = []
    for job in jobs:
        events = streams[(job["capture"], job["connection_index"], "s2c")]
        index = next(
            i
            for i, event in enumerate(events)
            if event["frame_index"] == job["frame_index"]
            and event["subevent_index"] == job["subevent_index"]
            and event["opcode"] == job["opcode"]
        )
        neighbors = []
        for distance in range(-WINDOW, WINDOW + 1):
            if distance == 0 or not 0 <= index + distance < len(events):
                continue
            event = events[index + distance]
            if event["opcode"] not in candidate_codes:
                continue
            neighbors.append(
                {
                    "relative_event": distance,
                    "opcode": event["opcode"],
                    "frame_index": event["frame_index"],
                    "frame_stream_offset": event["frame_stream_offset"],
                    "subevent_index": event["subevent_index"],
                    "subevent_offset": event["subevent_offset"],
                    "application_offset": event.get("application_offset"),
                    "designated_value": event.get("designated_value"),
                    "source_equals_job": event["_source_actor"] == job["_source_actor"],
                    "destination_equals_job": event["_destination_actor"]
                    == job["_destination_actor"],
                    "all_four_actor_fields_equal": all_actor_fields_equal(event, job),
                }
            )
        contexts.append(
            {
                key: job[key]
                for key in (
                    "capture",
                    "connection_index",
                    "lane",
                    "frame_index",
                    "frame_stream_offset",
                    "subevent_index",
                    "subevent_offset",
                )
            }
            | {
                "job_byte": job["job_byte"],
                "job_source_equals_destination": job["source_equals_destination"],
                "window_events_before_after": WINDOW,
                "candidate_neighbors": neighbors,
            }
        )

    pairs = []
    for request in requests:
        for job in jobs:
            if (request["capture"], request["connection_index"]) != (
                job["capture"],
                job["connection_index"],
            ):
                continue
            pairs.append(
                {
                    "capture": request["capture"],
                    "connection_index": request["connection_index"],
                    "lane": request["lane"],
                    "application_04_low16": request["application_04_low16"],
                    "request": {
                        key: request[key]
                        for key in (
                            "direction",
                            "frame_index",
                            "frame_stream_offset",
                            "subevent_index",
                            "subevent_offset",
                        )
                    },
                    "job_update": {
                        key: job[key]
                        for key in (
                            "direction",
                            "frame_index",
                            "frame_stream_offset",
                            "subevent_index",
                            "subevent_offset",
                        )
                    },
                    "request_source_equals_destination": request[
                        "source_equals_destination"
                    ],
                    "job_source_equals_destination": job["source_equals_destination"],
                    "request_source_equals_job_source": request["_source_actor"]
                    == job["_source_actor"],
                    "request_destination_equals_job_destination": request[
                        "_destination_actor"
                    ]
                    == job["_destination_actor"],
                    "all_four_actor_fields_equal": all_actor_fields_equal(request, job),
                }
            )

    def public_request(row: dict) -> dict:
        return {
            key: row[key]
            for key in (
                "capture",
                "connection_index",
                "lane",
                "direction",
                "frame_index",
                "frame_stream_offset",
                "subevent_index",
                "subevent_offset",
                "opcode",
                "application_size",
                "source_equals_destination",
                "application_04_low16",
                "event_type",
                "event_name",
                "typed_tail_application_offset",
                "typed_tail",
            )
        }

    return {
        "study": "c2s-012d-event-start",
        "extension": "job-change-context",
        "generator_version": "1",
        "evidence_class": "packet-capture",
        "source": {
            "manifest": "sources/pcap-1.23b/manifest.yaml",
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "manifest_member_count": len(members),
            "local_members_verified": len(members),
            "captures_in_output": {
                name: capture_hashes[name]
                for name in sorted({row["capture"] for row in jobs + requests})
            },
        },
        "scope": {
            "job_opcode": "0x01a4",
            "request_opcode": "0x012d",
            "animation_designated_field": "application +0 for 0x00da/0x00e0/0x00e1",
            "combat_designated_field": "application +4 for 0x0139/0x013a/0x013b/0x013c",
            "neighborhood": "same admitted s2c connection and direction, +/-3 decoded subevents",
            "cross_direction_order_claim": False,
        },
        "summary": {
            "job_update_count": len(jobs),
            "job_byte_counts": {
                str(k): v
                for k, v in sorted(Counter(row["job_byte"] for row in jobs).items())
            },
            "job_contexts_with_candidate_neighbor": sum(
                bool(row["candidate_neighbors"]) for row in contexts
            ),
            "request_count_for_application_04_low16_12017": len(requests),
            "request_count_by_application_04_low16": {
                str(k): v
                for k, v in sorted(
                    Counter(row["application_04_low16"] for row in requests).items()
                )
            },
            "request_job_pair_count": len(pairs),
            "request_job_pairs_all_four_equal": sum(
                row["all_four_actor_fields_equal"] for row in pairs
            ),
        },
        "selector_search": {
            "scope": "all complete decoded subevent bytes in all 54 verified members",
            "exact_value": f"0x{TARGET_SELECTOR:08x}",
            "packed_predicate": "(value & 0xFF000FFF) == 0x04000030",
            "predicate_sanity": {
                "0x04000030": True,
                "0x04001030": True,
                "0x040ff030": True,
                "0x04000029": False,
            },
            "frames": stats["frames"],
            "complete_subevents": stats["complete_subevents"],
            "truncated_subevents": stats["truncated_subevents"],
            "compression_mismatches": stats["compression_mismatches"],
            "body_tail_nonzero_bytes": stats["body_tail_nonzero_bytes"],
            "packed_any_complete_subevent_count": stats["packed_any"],
            "exact_any_complete_subevent_count": stats["exact_any"],
            "packed_designated_field_count": stats["packed_designated"],
            "exact_designated_field_count": stats["exact_designated"],
            "designated_fields": {
                "animation": "application +0 for 0x00da/0x00e0/0x00e1",
                "combat_result": "application +4 for 0x0139/0x013a/0x013b/0x013c",
            },
        },
        "job_contexts": contexts,
        "requests": [public_request(row) for row in requests],
        "request_job_pairs": pairs,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="compare without writing")
    parser.add_argument(
        "--public-shape",
        action="store_true",
        help="validate the committed product without capture inputs",
    )
    args = parser.parse_args()
    if args.public_shape:
        return validate_public_shape()
    expected = (json.dumps(build(), indent=2, sort_keys=True) + "\n").encode("ascii")
    if args.check:
        if not OUT.is_file() or OUT.read_bytes() != expected:
            print(f"out of date: {OUT}", file=sys.stderr)
            return 1
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(expected)
    return 0


def validate_request_job_context(product: dict) -> None:
    requests = product["requests"]
    contexts = product["job_contexts"]
    pairs = product["request_job_pairs"]
    summary = product["summary"]
    expected_request = {
        "application_04_low16": 12017,
        "application_size": 184,
        "capture": "gear_changesoul.pcapng",
        "connection_index": 0,
        "direction": "c2s",
        "event_name": "commandRequest",
        "event_type": 0,
        "frame_index": 19,
        "frame_stream_offset": 3416,
        "lane": "main",
        "opcode": "0x012d",
        "source_equals_destination": True,
        "subevent_index": 0,
        "subevent_offset": 0,
        "typed_tail_application_offset": 0x31,
    }
    if len(requests) != 1 or any(
        requests[0].get(key) != value for key, value in expected_request.items()
    ):
        raise ValueError("retained request identity changed")
    anchors = [row for row in contexts if row["candidate_neighbors"]]
    expected_anchor = {
        "capture": "gear_changesoul.pcapng",
        "connection_index": 0,
        "frame_index": 13,
        "frame_stream_offset": 1128,
        "job_byte": 16,
        "job_source_equals_destination": True,
        "lane": "main",
        "subevent_index": 0,
        "subevent_offset": 0,
        "window_events_before_after": 3,
    }
    if len(anchors) != 1 or any(
        anchors[0].get(key) != value for key, value in expected_anchor.items()
    ):
        raise ValueError("retained job anchor changed")
    locator_keys = (
        "frame_index",
        "frame_stream_offset",
        "subevent_index",
        "subevent_offset",
    )
    expected_pair = {
        "application_04_low16": 12017,
        "capture": "gear_changesoul.pcapng",
        "connection_index": 0,
        "lane": "main",
        "request": {
            "direction": "c2s",
            **{key: requests[0][key] for key in locator_keys},
        },
        "job_update": {
            "direction": "s2c",
            **{key: anchors[0][key] for key in locator_keys},
        },
        "all_four_actor_fields_equal": True,
        "job_source_equals_destination": True,
        "request_source_equals_destination": True,
        "request_source_equals_job_source": True,
        "request_destination_equals_job_destination": True,
    }
    if pairs != [expected_pair]:
        raise ValueError("retained request/job relation changed")
    if (
        summary["job_update_count"] != len(contexts)
        or summary["job_byte_counts"]
        != dict(Counter(str(row["job_byte"]) for row in contexts))
        or summary["request_count_for_application_04_low16_12017"] != len(requests)
        or summary["request_job_pair_count"] != len(pairs)
        or summary["request_job_pairs_all_four_equal"]
        != sum(row["all_four_actor_fields_equal"] for row in pairs)
    ):
        raise ValueError("request/job summaries disagree with retained rows")


def validate_public_shape() -> int:
    try:
        product = json.loads(OUT.read_text(encoding="ascii"))
        if product.get("study") != "c2s-012d-event-start":
            raise ValueError("study id changed")
        if product.get("extension") != "job-change-context":
            raise ValueError("extension id changed")
        if product["source"]["manifest_member_count"] != 54:
            raise ValueError("source member count changed")
        selector = product["selector_search"]
        if (
            selector["complete_subevents"] != 65864
            or selector["truncated_subevents"] != 0
            or selector["compression_mismatches"] != 0
            or selector["body_tail_nonzero_bytes"] != 0
        ):
            raise ValueError("complete-subevent accounting changed")
        for key in (
            "packed_any_complete_subevent_count",
            "exact_any_complete_subevent_count",
            "packed_designated_field_count",
            "exact_designated_field_count",
        ):
            if selector[key] != 0:
                raise ValueError(f"selector negative changed: {key}")
        if selector["predicate_sanity"] != {
            "0x04000029": False,
            "0x04000030": True,
            "0x04001030": True,
            "0x040ff030": True,
        }:
            raise ValueError("packed predicate sanity changed")
        summary = product["summary"]
        if summary["job_update_count"] != 18:
            raise ValueError("job-update count changed")
        if summary["job_byte_counts"] != {"0": 9, "15": 1, "16": 8}:
            raise ValueError("job-byte distribution changed")
        if summary["request_count_for_application_04_low16_12017"] != 1:
            raise ValueError("12017 request count changed")
        if summary["request_job_pairs_all_four_equal"] != 1:
            raise ValueError("same-actor join changed")
        requests = product["requests"]
        if len(requests) != 1 or requests[0]["application_04_low16"] != 12017:
            raise ValueError("12017 request identity changed")
        expected_tail = [
            {"tail_offset": 0, "type": "int", "value": 1},
            *[{"tail_offset": offset, "type": "nil"} for offset in range(5, 13)],
            {"tail_offset": 13, "type": "terminator"},
        ]
        if requests[0]["typed_tail"] != expected_tail:
            raise ValueError("12017 typed-tail shape changed")
        contexts = product["job_contexts"]
        if len(contexts) != 18:
            raise ValueError("job context count changed")
        witnesses = [
            neighbor
            for context in contexts
            for neighbor in context["candidate_neighbors"]
        ]
        if len(witnesses) != 1 or witnesses[0] != {
            "all_four_actor_fields_equal": True,
            "application_offset": 0,
            "designated_value": "0x04000029",
            "destination_equals_job": True,
            "frame_index": 14,
            "frame_stream_offset": 1182,
            "opcode": "0x00da",
            "relative_event": 1,
            "source_equals_job": True,
            "subevent_index": 0,
            "subevent_offset": 0,
        }:
            raise ValueError("local presentation witness changed")
        validate_request_job_context(product)
        forbidden = (
            "actor_id",
            "endpoint",
            "payload_hex",
            "_source_actor",
            "_destination_actor",
        )

        def check_keys(value: object) -> None:
            if isinstance(value, dict):
                if any(any(token in key for token in forbidden) for key in value):
                    raise ValueError("sanitized product contains forbidden field")
                for child in value.values():
                    check_keys(child)
            elif isinstance(value, list):
                for child in value:
                    check_keys(child)

        check_keys(product)
        expected = (json.dumps(product, indent=2, sort_keys=True) + "\n").encode(
            "ascii"
        )
        if OUT.read_bytes() != expected:
            raise ValueError("product is not canonically formatted")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"job-change context: public shape invalid: {exc}", file=sys.stderr)
        return 1
    print("verified job-change context public shape")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
