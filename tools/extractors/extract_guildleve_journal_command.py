#!/usr/bin/env python3
"""Census c2s wire evidence for guildleve journal command 24241."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import struct
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from extract_observations import (  # type: ignore  # noqa: E402
    INNER_HEADER_LEN,
    SUB_EVENT_CLASS_ACTOR_WRAPPED,
    SUB_EVENT_HEADER_LEN,
    default_corpus_paths,
)
from extract_streams import parse_outer_frames, reconstruct_lanes  # type: ignore  # noqa: E402

COMMAND_ID = 24241
COMMAND_ID_HEX = 0x5EB1
COMMAND_OWNER_ID = 0xA0F05EB1
EVENT_START_OPCODE = 0x012D
GAME_MESSAGE_PREAMBLE_LEN = 8
OUT = REPO_ROOT / "studies" / "guildleve-journal-command-wire" / "derived"
MATCH_FIELDS = [
    "capture", "lane_index", "lane", "frame_index", "frame_offset",
    "subevent_index", "subevent_offset", "subevent_size", "inner_opcode",
    "field_domain", "field_offset", "width", "predicate", "value_hex",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_all(data: bytes, needle: bytes) -> list[int]:
    offsets: list[int] = []
    start = 0
    while True:
        offset = data.find(needle, start)
        if offset < 0:
            return offsets
        offsets.append(offset)
        start = offset + 1


def corpus_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("ascii"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(path)))
    return digest.hexdigest()


def scan() -> tuple[list[dict], dict]:
    paths = default_corpus_paths()
    matches: list[dict] = []
    totals = Counter()
    per_capture: list[dict] = []
    needle_counts = Counter()
    needles = (
        ("command_u16_le", struct.pack("<H", COMMAND_ID_HEX)),
        ("command_u32_le", struct.pack("<I", COMMAND_ID)),
        ("static_actor_u32_le", struct.pack("<I", COMMAND_OWNER_ID)),
    )
    for domain in ("frame_body", "subevent_header", "inner_header", "actor_payload", "application_payload"):
        for predicate, _needle in needles:
            needle_counts[f"{domain}:{predicate}"] = 0

    for capture in paths:
        capture_counts = Counter()
        lanes = reconstruct_lanes(capture)
        for lane_index, lane in enumerate(lanes):
            totals["lanes"] += 1
            totals[f"{lane['lane']}_lanes"] += 1
            capture_counts["lanes"] += 1
            capture_counts[f"{lane['lane']}_lanes"] += 1
            blob = lane["streams"].get("c2s", b"")
            totals["c2s_stream_bytes"] += len(blob)
            capture_counts["c2s_stream_bytes"] += len(blob)
            for frame_index, frame in enumerate(parse_outer_frames(blob)):
                totals["c2s_frames"] += 1
                capture_counts["c2s_frames"] += 1
                body = frame["body"]
                totals["c2s_frame_body_bytes"] += len(body)
                for predicate, needle in needles:
                    needle_counts[f"frame_body:{predicate}"] += len(find_all(body, needle))

                offset = 0
                subevent_index = 0
                while offset + SUB_EVENT_HEADER_LEN <= len(body):
                    size, event_type = struct.unpack_from("<HH", body, offset)
                    if size < SUB_EVENT_HEADER_LEN or offset + size > len(body):
                        break
                    totals["c2s_subevents"] += 1
                    capture_counts["c2s_subevents"] += 1
                    subevent_header = body[offset:offset + SUB_EVENT_HEADER_LEN]
                    subevent_payload = body[offset + SUB_EVENT_HEADER_LEN:offset + size]
                    totals["c2s_subevent_payload_bytes"] += len(subevent_payload)
                    for predicate, needle in needles:
                        needle_counts[f"subevent_header:{predicate}"] += len(find_all(subevent_header, needle))
                    if event_type == SUB_EVENT_CLASS_ACTOR_WRAPPED:
                        totals["c2s_wrapped_subevents"] += 1
                        capture_counts["c2s_wrapped_subevents"] += 1
                        sub = subevent_payload
                        if len(sub) >= INNER_HEADER_LEN:
                            inner_header = sub[:INNER_HEADER_LEN]
                            opcode = struct.unpack_from("<H", sub, 2)[0]
                            if opcode == COMMAND_ID_HEX:
                                totals["inner_opcode_0x5eb1"] += 1
                            payload = sub[INNER_HEADER_LEN:]
                            application = payload[GAME_MESSAGE_PREAMBLE_LEN:]
                            totals["c2s_actor_payload_bytes"] += len(payload)
                            totals["c2s_application_payload_bytes"] += len(application)
                            for predicate, needle in needles:
                                needle_counts[f"inner_header:{predicate}"] += len(find_all(inner_header, needle))
                                needle_counts[f"actor_payload:{predicate}"] += len(find_all(payload, needle))
                            if opcode == EVENT_START_OPCODE:
                                totals["event_start_rows"] += 1
                                owner = struct.unpack_from("<I", application, 4)[0] if len(application) >= 8 else None
                                if owner == COMMAND_OWNER_ID:
                                    totals["target_event_start_rows"] += 1
                                if owner is not None and (owner & 0xFFFF) == COMMAND_ID:
                                    totals["event_start_owner_low16_rows"] += 1
                            for predicate, needle in needles:
                                for field_offset in find_all(application, needle):
                                    needle_counts[f"application_payload:{predicate}"] += 1
                                    matches.append({
                                        "capture": capture.name,
                                        "lane_index": lane_index,
                                        "lane": lane["lane"],
                                        "frame_index": frame_index,
                                        "frame_offset": frame["offset"],
                                        "subevent_index": subevent_index,
                                        "subevent_offset": offset,
                                        "subevent_size": size,
                                        "inner_opcode": f"0x{opcode:04x}",
                                        "field_domain": "application_payload",
                                        "field_offset": field_offset,
                                        "width": len(needle),
                                        "predicate": predicate,
                                        "value_hex": needle.hex(),
                                    })
                    offset += size
                    subevent_index += 1

        per_capture.append({
            "name": capture.name,
            "size_bytes": capture.stat().st_size,
            "sha256": sha256(capture),
            **dict(sorted(capture_counts.items())),
        })

    expected = {
        "captures": 54,
        "lanes": 84,
        "main_lanes": 54,
        "chat_lanes": 30,
        "unknown_lanes": 0,
        "c2s_stream_bytes": 1504160,
        "c2s_frames": 8970,
        "c2s_subevents": 21201,
        "c2s_wrapped_subevents": 21109,
        "event_start_rows": 126,
        "target_event_start_rows": 0,
        "event_start_owner_low16_rows": 0,
        "inner_opcode_0x5eb1": 0,
    }
    actual = {"captures": len(paths), **{key: totals[key] for key in expected if key != "captures"}}
    if actual != expected:
        raise ValueError(f"corpus reconciliation changed: {actual}")
    if matches or any(needle_counts.values()):
        raise ValueError(f"target byte census changed: {dict(sorted(needle_counts.items()))}")

    accounting = {
        "schema_version": 1,
        "study": "guildleve-journal-command-wire",
        "target": {
            "command_static_actor_id": COMMAND_ID,
            "command_static_actor_id_hex": f"0x{COMMAND_ID_HEX:04x}",
            "event_start_owner_actor_id_hex": f"0x{COMMAND_OWNER_ID:08x}",
            "candidate_event_start_opcode": f"0x{EVENT_START_OPCODE:04x}",
            "candidate_subindices": [2, 3, 4, 5],
        },
        "coverage": {
            **actual,
            "c2s_frame_body_bytes": totals["c2s_frame_body_bytes"],
            "c2s_subevent_payload_bytes": totals["c2s_subevent_payload_bytes"],
            "c2s_actor_payload_bytes": totals["c2s_actor_payload_bytes"],
            "c2s_application_payload_bytes": totals["c2s_application_payload_bytes"],
        },
        "needle_occurrences": dict(sorted(needle_counts.items())),
        "match_rows": len(matches),
        "inputs": {
            "source": "pcap-1.23b",
            "corpus_digest_sha256": corpus_digest(paths),
            "captures": per_capture,
        },
        "boundaries": [
            "24241 is a static actor row identity, not a wire opcode identity.",
            "The EventStart owner low-16 relationship is conditional on the 0xa0f00000 static-actor prefix.",
            "Subindices 2 through 5 are tested only as arguments of a structurally identified target command row; arbitrary byte values are not semantic matches.",
            "No target command row exists, so no journal ID or subindex can be structurally decoded from this corpus.",
            "Raw lobby 54994 and TLS traffic are outside the canonical clear game-lane decoder.",
        ],
    }
    return matches, accounting


def csv_bytes(rows: list[dict]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=MATCH_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    matches, accounting = scan()
    outputs = {
        "command-matches.csv": csv_bytes(matches),
        "accounting.json": (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii"),
    }
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
        print("stale guildleve journal command outputs:\n  " + "\n  ".join(stale))
        return 1
    print(("verified" if args.check else "wrote") + f" {len(outputs)} guildleve journal command artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
