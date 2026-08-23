#!/usr/bin/env python3
"""Extract bounded director-role and Group-family wire evidence."""

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

from extract_observations import INNER_HEADER_LEN, SUB_EVENT_CLASS_ACTOR_WRAPPED, SUB_EVENT_HEADER_LEN, default_corpus_paths  # type: ignore  # noqa: E402
from extract_streams import maybe_inflate, parse_outer_frames, reconstruct_lanes  # type: ignore  # noqa: E402

OPCODES = {0x017A: 176, 0x017C: 152, 0x017D: 64, 0x017E: 56,
           0x017F: 440, 0x0183: 152, 0x0187: 96, 0x018B: 88}
EVENT_START = 0x012D
APP_PREFIX_LEN = INNER_HEADER_LEN + 8
OUT = REPO_ROOT / "studies" / "director-wire-identity" / "derived"


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def u64(data: bytes, off: int) -> int:
    return struct.unpack_from("<Q", data, off)[0]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan() -> tuple[list[dict], list[dict], list[dict], dict]:
    packets: list[dict] = []
    members: list[dict] = []
    roles: list[dict] = []
    for capture in default_corpus_paths():
        for lane_index, lane in enumerate(reconstruct_lanes(capture)):
            for direction in ("c2s", "s2c"):
                blob = lane["streams"].get(direction, b"")
                for frame_index, frame in enumerate(parse_outer_frames(blob)):
                    body = maybe_inflate(frame["body"]) if direction == "s2c" else frame["body"]
                    if body is None:
                        body = frame["body"]
                    off = 0
                    sub_index = 0
                    while off + SUB_EVENT_HEADER_LEN <= len(body):
                        size, event_type = struct.unpack_from("<HH", body, off)
                        if not size or size < SUB_EVENT_HEADER_LEN or off + size > len(body):
                            break
                        if event_type == SUB_EVENT_CLASS_ACTOR_WRAPPED:
                            sub = body[off + SUB_EVENT_HEADER_LEN:off + size]
                            if len(sub) >= INNER_HEADER_LEN:
                                opcode = struct.unpack_from("<H", sub, 2)[0]
                                app = sub[APP_PREFIX_LEN:]
                                base = {"capture": capture.name, "direction": direction,
                                        "lane_index": lane_index, "frame_index": frame_index,
                                        "subevent_index": sub_index, "subevent_offset": off}
                                if direction == "c2s" and opcode == EVENT_START and len(app) >= 0x30:
                                    name = app[17:49].split(b"\0", 1)[0].decode("ascii", "replace")
                                    owner = u32(app, 4)
                                    roles.append({**base, "event_name": name,
                                                  "trigger_actor_id": u32(app, 0),
                                                  "owner_actor_id": owner,
                                                  "owner_high_nibble": owner >> 28})
                                if direction == "s2c" and opcode in OPCODES:
                                    if size != OPCODES[opcode]:
                                        raise ValueError(f"{capture.name} 0x{opcode:04X}: {size}")
                                    row = {**base, "opcode": f"0x{opcode:04X}",
                                           "subpacket_size": size, "application_length": len(app),
                                           "transport_source_actor_id": u32(body, off + 4),
                                           "field_u64_0": u64(app, 0) if len(app) >= 8 else "",
                                           "field_u64_8": u64(app, 8) if len(app) >= 16 else "",
                                           "group_type_candidate": u32(app, 0x30) if opcode == 0x017C else "",
                                           "member_count": app[0x190] if opcode == 0x017F else (app[0x70] if opcode == 0x0183 else "")}
                                    packets.append(row)
                                    if opcode in (0x017F, 0x0183):
                                        stride = 0x30 if opcode == 0x017F else 0x0C
                                        count = int(row["member_count"])
                                        for slot in range(min(count, 8)):
                                            pos = 0x10 + slot * stride
                                            actor = u32(app, pos)
                                            members.append({**base, "opcode": f"0x{opcode:04X}",
                                                            "slot": slot, "actor_id": actor,
                                                            "actor_high_nibble": actor >> 28,
                                                            "record_stride": stride,
                                                            "field_at_record_plus_8": u32(app, pos + 8)})
                        off += size
                        sub_index += 1
    counts = Counter(p["opcode"] for p in packets)
    types = Counter(p["group_type_candidate"] for p in packets if p["opcode"] == "0x017C")
    owner_keys = {(r["capture"], r["owner_actor_id"]) for r in roles}
    owner_events: dict[tuple[str, int], set[str]] = {}
    for role in roles:
        owner_events.setdefault((role["capture"], role["owner_actor_id"]), set()).add(role["event_name"])
    for member in members:
        key = (member["capture"], member["actor_id"])
        member["event_role_match"] = "yes" if key in owner_keys else "no"
        member["matching_event_names"] = ";".join(sorted(owner_events.get(key, set())))
    role_member_matches = [m for m in members if (m["capture"], m["actor_id"]) in owner_keys]
    account = {
        "schema_version": 1,
        "packet_counts": dict(sorted(counts.items())),
        "group_type_candidate_distribution": {str(k): v for k, v in sorted(types.items())},
        "literal_30001_occurrences": types[30001],
        "literal_30001_captures": sorted({p["capture"] for p in packets if p["group_type_candidate"] == 30001}),
        "event_start_count": len(roles),
        "event_owner_high_nibble_distribution": {str(k): v for k, v in sorted(Counter(r["owner_high_nibble"] for r in roles).items())},
        "member_rows": len(members),
        "member_actor_high_nibble_distribution": {
            f"{opcode}:{nibble}": count for (opcode, nibble), count in sorted(
                Counter((m["opcode"], m["actor_high_nibble"]) for m in members).items())
        },
        "role_member_match_rows": len(role_member_matches),
        "role_member_match_actor_ids": sorted({m["actor_id"] for m in role_member_matches}),
        "role_member_match_high_nibble_distribution": {
            str(k): v for k, v in sorted(Counter(m["actor_high_nibble"] for m in role_member_matches).items())
        },
        "inputs": {"captures": [{"name": p.name, "sha256": sha(p)} for p in default_corpus_paths()]},
        "boundaries": [
            "EventStart ownerActorId is role-bearing but does not by itself name a content director.",
            "GroupHeader application +0x08 is a sequence/session value, not an actor identity.",
            "Numeric fields remain wire observations unless the static client layout names them.",
        ],
    }
    expected = {"0x017A": 275, "0x017C": 365, "0x017D": 365, "0x017E": 365,
                "0x017F": 31, "0x0183": 371, "0x0187": 44, "0x018B": 287}
    if dict(sorted(counts.items())) != expected:
        raise ValueError(f"corpus counts changed: {dict(sorted(counts.items()))}")
    return packets, members, roles, account


def csv_bytes(rows: list[dict]) -> bytes:
    out = io.StringIO(newline="")
    fields = list(rows[0]) if rows else []
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    packets, members, roles, accounting = scan()
    outputs = {"group-packets.csv": csv_bytes(packets), "group-members.csv": csv_bytes(members),
               "event-role-candidates.csv": csv_bytes(roles),
               "accounting.json": (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii")}
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
        print("stale director wire identity outputs:\n  " + "\n  ".join(stale))
        return 1
    print(("verified" if args.check else "wrote") + f" {len(outputs)} director wire identity artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
