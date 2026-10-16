#!/usr/bin/env python3
"""Reproduce the retained s2c 0x0132 byte/name census without raw payloads."""

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

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))
from extract_login_0002_appearance_order import _packet_spans  # noqa: E402
from extract_login_018a_timeline import _frame_packet  # noqa: E402
from extract_observations import parse_sub_events  # noqa: E402
from extract_streams import (  # noqa: E402
    clear_packet_cache,
    maybe_inflate,
    parse_outer_frames,
    reconstruct_lanes,
)

STUDY = "command-registration"
EXPECTED_NAMES = {
    "commandForced": (11, 0),
    "commandDefault": (10, 0),
    "commandWeak": (6, 0),
    "commandContent": (4, 0),
    "commandJudgeMode": (6, 0),
    "commandRequest": (0, 1),
    "widgetCreate": (0, 1),
    "macroRequest": (0, 1),
}
FIELDS = (
    "capture",
    "connection_index",
    "lane",
    "direction",
    "frame_index",
    "frame_stream_offset",
    "subevent_index",
    "subevent_offset",
    "capture_packet_index",
    "source_actor_id",
    "target_actor_id",
    "byte0",
    "byte1",
    "function_name",
    "subevent_size",
    "application_size",
    "name_padding_size",
    "name_padding_zero",
    "reserved_tail_size",
    "reserved_tail_zero",
    "reserved_tail_sha256",
    "remainder_size",
    "remainder_sha256",
    "application_sha256",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_application(application: bytes) -> dict:
    """Expose only whitelisted names, scalar bytes, zero shapes and hashes."""
    if len(application) != 40:
        raise ValueError("unexpected 0x0132 application size")
    name, separator, padding = application[2:34].partition(b"\0")
    name = name.decode("ascii")
    if not separator or name not in EXPECTED_NAMES:
        raise ValueError("unexpected registration name or missing terminator")
    if tuple(application[:2]) != EXPECTED_NAMES[name]:
        raise ValueError("registration byte/name mapping changed")
    if any(padding) or any(application[34:]):
        raise ValueError("nonzero registration name padding or reserved tail")
    return {
        "byte0": application[0],
        "byte1": application[1],
        "function_name": name,
        "application_size": 40,
        "name_padding_size": len(padding),
        "name_padding_zero": True,
        "reserved_tail_size": 6,
        "reserved_tail_zero": True,
        "reserved_tail_sha256": sha256(application[34:]),
        "remainder_size": 38,
        "remainder_sha256": sha256(application[2:]),
        "application_sha256": sha256(application),
    }


def locator(
    capture: str,
    connection_index: int,
    direction: str,
    frame_index: int,
    frame: dict,
    subevent_index: int,
    subevent: dict,
    packet: dict,
) -> dict:
    return {
        "capture": capture,
        "connection_index": connection_index,
        "direction": direction,
        "frame_index": frame_index,
        "frame_stream_offset": frame["offset"],
        "subevent_index": subevent_index,
        "subevent_offset": subevent["offset"],
        "capture_packet_index": packet["packet_index"] + 1,
    }


def collect_capture(path: Path) -> tuple[list[dict], list[dict], list[dict]]:
    rows, references, framing = [], [], []
    for connection_index, connection in enumerate(reconstruct_lanes(path)):
        pongs, movements = [], []
        connection_rows = []
        for direction in ("c2s", "s2c"):
            blob = connection["streams"].get(direction, b"")
            spans = _packet_spans(path, connection, direction) if blob else []
            frames = parse_outer_frames(blob)
            if sum(frame["size"] for frame in frames) != len(blob):
                raise ValueError("unaccounted reconstructed frame bytes")
            if max((span["end"] for span in spans), default=0) != len(blob):
                raise ValueError("incomplete IP-declared TCP direction")
            covered_end = 0
            for span in sorted(spans, key=lambda item: item["start"]):
                if span["start"] > covered_end:
                    raise ValueError("TCP sequence gap")
                covered_end = max(covered_end, span["end"])
            for frame_index, frame in enumerate(frames):
                inflated = maybe_inflate(frame["body"])
                if (frame["marker"][1] == 1) != (inflated is not None):
                    raise ValueError("outer compression flag/body mismatch")
                body = inflated if inflated is not None else frame["body"]
                subevents = parse_sub_events(body)
                if any(event.get("truncated") for event in subevents):
                    raise ValueError("truncated subevent")
                if any(body[sum(event["size"] for event in subevents) :]):
                    raise ValueError("nonzero undecoded subevent tail")
                relevant = [
                    event
                    for event in subevents
                    if (direction == "s2c" and event.get("inner_opcode") == 0x0132)
                    or (
                        direction == "c2s"
                        and (event["type"] == 8 or event.get("inner_opcode") == 0x00CA)
                    )
                ]
                packet = (
                    _frame_packet(frame["offset"], frame["size"], spans)
                    if relevant
                    else None
                )
                for subevent_index, event in enumerate(subevents):
                    opcode = event.get("inner_opcode")
                    if event not in relevant:
                        continue
                    position = locator(
                        path.name,
                        connection_index,
                        direction,
                        frame_index,
                        frame,
                        subevent_index,
                        event,
                        packet,
                    )
                    start, size = event["offset"], event["size"]
                    if direction == "c2s" and event["type"] == 8:
                        if size != 24:
                            raise ValueError("unexpected client pong size")
                        actor = struct.unpack_from("<I", body, start + 16)[0]
                        pongs.append({**position, "actor_id": f"0x{actor:08X}"})
                    elif direction == "c2s" and opcode == 0x00CA:
                        movements.append(
                            {**position, "actor_id": f"0x{event['src_actor']:08X}"}
                        )
                    elif direction == "s2c" and opcode == 0x0132:
                        if event["type"] != 3 or size != 72:
                            raise ValueError("unexpected registration wrapper")
                        # The shared 16-byte game-message body header follows the wrapper.
                        application = body[start + 32 : start + size]
                        row = {
                            **position,
                            "lane": connection["lane"],
                            "source_actor_id": f"0x{event['src_actor']:08X}",
                            "target_actor_id": f"0x{event['dst_actor']:08X}",
                            "subevent_size": size,
                            **decode_application(application),
                        }
                        rows.append(row)
                        connection_rows.append(row)
            framing.append(
                {
                    "capture": path.name,
                    "connection_index": connection_index,
                    "lane": connection["lane"],
                    "direction": direction,
                    "frames": len(frames),
                    "stream_bytes": len(blob),
                    "captured_payload_segments": len(spans),
                    "trailing_bytes": 0,
                    "sequence_gaps": 0,
                    "subevent_truncations": 0,
                    "compression_mismatches": 0,
                }
            )
        if connection_rows:
            if not pongs or not movements:
                raise ValueError(
                    "registration connection lacks actor-reference witnesses"
                )
            references.append(
                {
                    "capture": path.name,
                    "connection_index": connection_index,
                    "c2s_0008_body0_actor_counts": dict(
                        Counter(r["actor_id"] for r in pongs)
                    ),
                    "first_c2s_0008": pongs[0],
                    "c2s_00ca_source_actor_counts": dict(
                        Counter(r["actor_id"] for r in movements)
                    ),
                    "first_c2s_00ca": movements[0],
                }
            )
    return rows, references, framing


def summarize_rows(rows: list[dict]) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[
            (row["capture"], int(row["connection_index"]), int(row["frame_index"]))
        ].append(row)
    batches = []
    for (capture, connection, frame), group in groups.items():
        if [r["function_name"] for r in group] != list(EXPECTED_NAMES):
            raise ValueError("registration batch names or stream order changed")
        indexes = [int(r["subevent_index"]) for r in group]
        if indexes != list(range(indexes[0], indexes[0] + 8)):
            raise ValueError("registration batch is not consecutive in its frame")
        batches.append(
            {
                "capture": capture,
                "connection_index": connection,
                "frame_index": frame,
                "first_subevent_index": indexes[0],
                "capture_packet_index": int(group[0]["capture_packet_index"]),
                "name_order": [r["function_name"] for r in group],
            }
        )
    return {
        "occurrences": len(rows),
        "capture_counts": dict(Counter(r["capture"] for r in rows)),
        "mapping_counts": dict(Counter(r["function_name"] for r in rows)),
        "batches": batches,
    }


def build_outputs(repo: Path, objects: Path) -> dict[str, bytes]:
    source = repo / "sources/pcap-1.23b/manifest.yaml"
    manifest = yaml.safe_load(source.read_text(encoding="utf-8"))
    members = sorted(manifest["members"], key=lambda member: member["file"])
    if sorted(path.name for path in objects.glob("*.pcapng")) != [
        m["file"] for m in members
    ]:
        raise ValueError("retained corpus membership mismatch")
    rows, references, framing = [], [], []
    for member in members:
        path = objects / member["file"]
        data = path.read_bytes()
        if len(data) != member["size_bytes"] or sha256(data) != member["sha256"]:
            raise ValueError("retained capture identity mismatch: " + path.name)
        found, actors, frames = collect_capture(path)
        rows.extend(found)
        references.extend(actors)
        framing.extend(frames)
        clear_packet_cache()
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    csv_bytes = output.getvalue().encode("ascii")
    accounting = {
        "schema_version": 1,
        "study": STUDY,
        "source_id": manifest["id"],
        "source_manifest_sha256": sha256(source.read_bytes()),
        "inputs": members,
        "counts": summarize_rows(rows),
        "actor_references": references,
        "framing": framing,
        "occurrences_sha256": sha256(csv_bytes),
    }
    outputs = {
        "occurrences.csv": csv_bytes,
        "accounting.json": (
            json.dumps(accounting, indent=2, ensure_ascii=True) + "\n"
        ).encode("ascii"),
    }
    validate_products(outputs, source.read_bytes())
    return outputs


def validate_products(outputs: dict[str, bytes], source_bytes: bytes) -> None:
    manifest = yaml.safe_load(source_bytes)
    rows = list(csv.DictReader(io.StringIO(outputs["occurrences.csv"].decode("ascii"))))
    accounting = json.loads(outputs["accounting.json"].decode("ascii"))
    if (
        accounting["source_id"] != manifest["id"]
        or accounting["source_manifest_sha256"] != sha256(source_bytes)
        or accounting["study"] != STUDY
        or accounting["schema_version"] != 1
    ):
        raise ValueError("registration source or study identity mismatch")
    if not rows or tuple(rows[0]) != FIELDS:
        raise ValueError("registration CSV field mismatch")
    if accounting["inputs"] != sorted(manifest["members"], key=lambda m: m["file"]):
        raise ValueError("registration input pins differ from source manifest")
    if len(accounting["inputs"]) != 54 or accounting["occurrences_sha256"] != sha256(
        outputs["occurrences.csv"]
    ):
        raise ValueError("registration corpus or output identity mismatch")
    for row in rows:
        if (
            row["function_name"] not in EXPECTED_NAMES
            or (int(row["byte0"]), int(row["byte1"]))
            != EXPECTED_NAMES[row["function_name"]]
        ):
            raise ValueError("registration byte/name mapping changed")
        application = (
            bytes((int(row["byte0"]), int(row["byte1"])))
            + row["function_name"].encode("ascii").ljust(32, b"\0")
            + bytes(6)
        )
        decoded = decode_application(application)
        if any(str(row[key]) != str(value) for key, value in decoded.items()):
            raise ValueError("registration shape or application fingerprint mismatch")
        if (
            row["lane"] != "main"
            or row["direction"] != "s2c"
            or int(row["subevent_size"]) != 72
        ):
            raise ValueError("registration transport shape mismatch")
        if (
            row["source_actor_id"] != row["target_actor_id"]
            or row["target_actor_id"] != "0x029B2941"
        ):
            raise ValueError("registration wrapped actor reference changed")
    summary = summarize_rows(rows)
    if (
        summary != accounting["counts"]
        or len(rows) != 96
        or len(summary["capture_counts"]) != 9
        or len(summary["batches"]) != 12
        or any(n != 12 for n in summary["mapping_counts"].values())
    ):
        raise ValueError("retained registration census counts changed")
    if len(accounting["actor_references"]) != 9:
        raise ValueError("missing registration actor reference")
    for reference in accounting["actor_references"]:
        for key in ("c2s_0008_body0_actor_counts", "c2s_00ca_source_actor_counts"):
            if set(reference[key]) != {"0x029B2941"}:
                raise ValueError("client actor-reference agreement changed")
    if {r["capture"] for r in accounting["framing"]} != {
        m["file"] for m in accounting["inputs"]
    }:
        raise ValueError("incomplete capture framing coverage")
    for row in accounting["framing"]:
        if any(
            row[key]
            for key in (
                "trailing_bytes",
                "sequence_gaps",
                "subevent_truncations",
                "compression_mismatches",
            )
        ):
            raise ValueError("retained registration decode boundary changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--public-shape", action="store_true")
    args = parser.parse_args()
    out = args.out_dir or args.repo / "studies" / STUDY / "derived"
    if args.public_shape:
        validate_products(
            {
                name: (out / name).read_bytes()
                for name in ("occurrences.csv", "accounting.json")
            },
            (args.repo / "sources/pcap-1.23b/manifest.yaml").read_bytes(),
        )
    else:
        objects = Path(
            os.environ.get(
                "XIVL_PCAP_OBJECTS_DIR", str(args.repo / "sources/pcap-1.23b/objects")
            )
        )
        outputs = build_outputs(args.repo, objects)
        if args.check:
            stale = [
                name
                for name, data in outputs.items()
                if not (out / name).is_file() or (out / name).read_bytes() != data
            ]
            if stale:
                raise ValueError("stale registration products: " + ", ".join(stale))
        else:
            out.mkdir(parents=True, exist_ok=True)
            for name, data in outputs.items():
                (out / name).write_bytes(data)
    print(
        f"{STUDY}: verified public shape"
        if args.public_shape
        else f"{STUDY}: {'verified' if args.check else 'generated'} 96 occurrences"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
