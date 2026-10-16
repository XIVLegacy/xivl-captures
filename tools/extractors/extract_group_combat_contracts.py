#!/usr/bin/env python3
"""Reproduce retained occupancy, group-work, and enmity observations."""

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

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from extract_0193_clock_contract import _frame_completion  # noqa: E402
from extract_battle_results import decode_packet  # noqa: E402
from extract_gam_keys import target_marker_length  # noqa: E402
from extract_login_0002_appearance_order import _packet_spans  # noqa: E402
from extract_observations import default_corpus_paths, parse_sub_events  # noqa: E402
from extract_streams import (  # noqa: E402
    maybe_inflate,
    parse_outer_frames,
    reconstruct_lanes,
)

REPO = SCRIPT_DIR.parents[1]
OUT = REPO / "studies/group-combat-wire-contracts/derived"
BASE = (
    "capture",
    "connection",
    "lane",
    "direction",
    "capture_packet",
    "frame",
    "subevent",
    "source_actor",
    "destination_actor",
)
COMBAT = {
    "combat_autoattack.pcapng",
    "combat_skills.pcapng",
    "party_battle_leve.pcapng",
}
RESULTS = set(range(0x139, 0x13D))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_bytes(fields, rows) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fields, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("ascii")


def parse_work(app: bytes) -> tuple[list[dict], list[dict]]:
    if len(app) != 144 or app[8] > 135:
        raise ValueError("unexpected group-work extent")
    end, pos = 9 + app[8], 9
    records, markers = [], []
    while pos < end:
        tag = app[pos]
        length = target_marker_length(tag)
        if length is not None and pos + 1 + length <= end:
            text = app[pos + 1 : pos + 1 + length]
            if all(32 <= c < 127 for c in text):
                markers.append(
                    {"offset": pos, "tag": tag, "target": text.decode("ascii")}
                )
                pos += 1 + length
                continue
        if tag == 0:
            if any(app[pos:end]):
                raise ValueError("nonzero group-work terminator tail")
            break
        if pos + 5 + tag > end:
            raise ValueError("truncated group-work property")
        value = app[pos + 5 : pos + 5 + tag]
        records.append(
            {
                "offset": pos,
                "property_id": struct.unpack_from("<I", app, pos + 1)[0],
                "width": tag,
                "value": int.from_bytes(value, "little"),
            }
        )
        pos += 5 + tag
    if any(app[end:]):
        raise ValueError("nonzero group-work unused capacity")
    return records, markers


def events(path: Path) -> list[dict]:
    result = []
    for connection_index, connection in enumerate(reconstruct_lanes(path)):
        for direction in ("c2s", "s2c"):
            blob = connection["streams"].get(direction, b"")
            spans = _packet_spans(path, connection, direction) if blob else []
            frames = parse_outer_frames(blob)
            if sum(f["size"] for f in frames) != len(blob):
                raise ValueError("unaccounted frame bytes")
            if max((s["end"] for s in spans), default=0) != len(blob):
                raise ValueError("incomplete captured TCP direction")
            for frame_index, frame in enumerate(frames):
                inflated = maybe_inflate(frame["body"])
                if (frame["marker"][1] == 1) != (inflated is not None):
                    raise ValueError("compression flag mismatch")
                body = inflated if inflated is not None else frame["body"]
                completion = _frame_completion(frame["offset"], frame["size"], spans)
                parsed = parse_sub_events(body)
                if any(e.get("truncated") for e in parsed):
                    raise ValueError("truncated subevent")
                if any(body[sum(e["size"] for e in parsed) :]):
                    raise ValueError("undecoded nonzero frame tail")
                for sub_index, e in enumerate(parsed):
                    if e["type"] != 3 or e.get("inner_opcode") is None:
                        continue
                    result.append(
                        {
                            "capture": path.name,
                            "connection": connection_index,
                            "lane": connection["lane"],
                            "direction": direction,
                            "capture_packet": completion["packet_index"] + 1,
                            "time_us": completion["capture_time_us"],
                            "frame": frame_index,
                            "subevent": sub_index,
                            "source_actor": e["src_actor"],
                            "destination_actor": e["dst_actor"],
                            "opcode": e["inner_opcode"],
                            "size": e["size"],
                            "app": body[e["offset"] + 32 : e["offset"] + e["size"]],
                        }
                    )
    return sorted(
        result,
        key=lambda e: (
            e["capture_packet"],
            e["connection"],
            e["direction"],
            e["frame"],
            e["subevent"],
        ),
    )


def build_outputs(paths: list[Path]) -> dict[str, bytes]:
    source = yaml.safe_load(
        (REPO / "sources/pcap-1.23b/manifest.yaml").read_text("utf-8")
    )
    expected = {m["file"]: (m["size_bytes"], m["sha256"]) for m in source["members"]}
    if sorted(p.name for p in paths) != sorted(expected):
        raise ValueError("incomplete canonical capture membership")
    occupancy, work, properties, enmity, timeline, joins, group_headers = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    inputs, summary, deletions = [], {}, []
    for path in paths:
        if (path.stat().st_size, sha(path)) != expected[path.name]:
            raise ValueError("capture member identity mismatch")
        inputs.append({"capture": path.name, "sha256": sha(path)})
        stream = events(path)
        headers = [
            e for e in stream if e["direction"] == "s2c" and e["opcode"] == 0x17C
        ]
        for header in headers:
            app = header["app"]
            if len(app) != 120:
                raise ValueError("unexpected group header extent")
            group_headers.append(
                {
                    **{k: header[k] for k in BASE},
                    "group_pair_18": int.from_bytes(app[24:32], "little"),
                    "group_pair_28": int.from_bytes(app[40:48], "little"),
                    "group_type": int.from_bytes(app[48:52], "little"),
                }
            )
        prior_result = {}
        last_indicator = {}
        capture_work = []
        hostile = []
        for e in stream:
            op, app = e["opcode"], e["app"]
            base = {k: e[k] for k in BASE}
            key = (e["connection"], e["direction"])
            if e["direction"] == "s2c" and op in RESULTS:
                prior_result[key] = e
            battle_header, battle_rows = (
                decode_packet(app, op)
                if op in RESULTS and e["direction"] == "s2c"
                else ({}, [])
            )
            if battle_rows and any(
                30301 <= r["world_master_text_id"] <= 30319
                and r["target_actor_id"] not in (0, battle_header["source_actor_id"])
                for r in battle_rows
            ):
                hostile.append(e)
            if path.name in COMBAT and (
                op
                in RESULTS
                | {0x12D, 0x143, 0x17A, 0x17C, 0x17D, 0x17E, 0x17F, 0x183, 0x187, 0x195}
            ):
                timeline.append(
                    {
                        **base,
                        "opcode": f"0x{op:04X}",
                        "group_pair": int.from_bytes(app[:8], "little")
                        if op in {0x17A, 0x187}
                        else int.from_bytes(app[16:24], "little")
                        if op in {0x17D, 0x17E, 0x17F, 0x183}
                        else int.from_bytes(app[24:32], "little")
                        if op == 0x143
                        else "",
                        "request_target_actor": int.from_bytes(app[:4], "little")
                        if op == 0x12D and e["direction"] == "c2s"
                        else "",
                        "request_owner_actor": int.from_bytes(app[4:8], "little")
                        if op == 0x12D and e["direction"] == "c2s"
                        else "",
                        "result_source_actor": battle_header.get("source_actor_id", ""),
                        "result_target_actors": ";".join(
                            str(r["target_actor_id"]) for r in battle_rows
                        ),
                        "result_message_ids": ";".join(
                            str(r["world_master_text_id"]) for r in battle_rows
                        ),
                    }
                )
            if e["direction"] != "s2c":
                continue
            if op == 0x143 and path.name in COMBAT:
                if len(app) != 32:
                    raise ValueError("unexpected DeleteGroup tuple extent")
                group = int.from_bytes(app[24:32], "little")
                prior = [
                    r
                    for r in occupancy
                    if r["capture"] == path.name
                    and r["connection"] == e["connection"]
                    and r["group_pair_0"] == group
                ]
                deletions.append(
                    {
                        **base,
                        **{
                            f"tuple_u64_{offset:02x}": int.from_bytes(
                                app[offset : offset + 8], "little"
                            )
                            for offset in (0, 8, 16, 24)
                        },
                        "prior_matching_occupancy_packets": len(prior),
                        "last_matching_occupancy_frame": prior[-1]["frame"]
                        if prior
                        else "",
                    }
                )
            elif op == 0x187:
                if e["size"] != 96 or len(app) != 64:
                    raise ValueError("unexpected occupancy extent")
                row = {
                    **base,
                    "group_pair_0": int.from_bytes(app[:8], "little"),
                    "header_u32_08": int.from_bytes(app[8:12], "little"),
                    "header_u32_0c": int.from_bytes(app[12:16], "little"),
                    "occupancy_work_0": int.from_bytes(app[16:20], "little"),
                    "occupancy_work_1": int.from_bytes(app[20:24], "little"),
                    "localized_name_id": int.from_bytes(app[24:28], "little"),
                    "name_length": len(app[28:].split(b"\0", 1)[0]),
                    "name_storage_zero": not any(app[28:]),
                }
                row["occupancy_reference_u64"] = int.from_bytes(app[16:24], "little")
                row["group_header_types"] = ";".join(
                    str(t)
                    for t in sorted(
                        {
                            int.from_bytes(h["app"][48:52], "little")
                            for h in headers
                            if h["connection"] == e["connection"]
                            and app[:8] in (h["app"][24:32], h["app"][40:48])
                        }
                    )
                )
                row["occupancy_reference_header_types"] = ";".join(
                    str(t)
                    for t in sorted(
                        {
                            int.from_bytes(h["app"][48:52], "little")
                            for h in headers
                            if h["connection"] == e["connection"]
                            and any(app[16:24])
                            and app[16:24] in (h["app"][24:32], h["app"][40:48])
                        }
                    )
                )
                occupancy.append(row)
                for other in stream:
                    if (
                        other["direction"] != "s2c"
                        or other["connection"] != e["connection"]
                        or not 0x17C <= other["opcode"] <= 0x186
                    ):
                        continue
                    for offset in (0, 8, 16, 24, 32, 40):
                        if (
                            len(other["app"]) >= offset + 8
                            and row["group_pair_0"]
                            and other["app"][offset : offset + 8] == app[:8]
                        ):
                            joins.append(
                                {
                                    **base,
                                    "group_pair_0": row["group_pair_0"],
                                    "matching_opcode": f"0x{other['opcode']:04X}",
                                    "matching_connection": other["connection"],
                                    "matching_frame": other["frame"],
                                    "matching_subevent": other["subevent"],
                                    "matching_capture_packet": other["capture_packet"],
                                    "matching_application_offset": offset,
                                }
                            )
            elif op == 0x17A:
                if e["size"] != 176:
                    raise ValueError("unexpected group-work subevent extent")
                records, markers = parse_work(app)
                row = {
                    **base,
                    "group_pair_0": int.from_bytes(app[:8], "little"),
                    "running_byte_total": app[8],
                    "record_count": len(records),
                    "marker_tags": ";".join(str(m["tag"]) for m in markers),
                    "targets": ";".join(m["target"] for m in markers),
                    "later_same_group_packets": 0,
                }
                row["matching_header_group_types"] = ";".join(
                    str(t)
                    for t in sorted(
                        {
                            int.from_bytes(h["app"][48:52], "little")
                            for h in headers
                            if h["connection"] == e["connection"]
                            and app[:8] in (h["app"][24:32], h["app"][40:48])
                        }
                    )
                )
                capture_work.append(row)
                for r in records:
                    properties.append(
                        {**base, "group_pair_0": row["group_pair_0"], **r}
                    )
            elif op == 0x195:
                if e["size"] != 40 or len(app) != 8:
                    raise ValueError("unexpected enmity extent")
                target, value, tail = struct.unpack("<IHH", app)
                previous = prior_result.get(key)
                actor_key = (e["connection"], e["source_actor"])
                current = (target, value)
                last = last_indicator.get(actor_key)
                row = {
                    **base,
                    "target_actor": target,
                    "value_u16": value,
                    "tail_u16": tail,
                    "changed_from_previous_indicator": ""
                    if last is None
                    else current != last,
                    "value_changed": "" if last is None else value != last[1],
                    "target_changed": "" if last is None else target != last[0],
                    "preceding_result_opcode": f"0x{previous['opcode']:04X}"
                    if previous
                    else "",
                    "preceding_result_frame": previous["frame"] if previous else "",
                    "preceding_result_subevent": previous["subevent"]
                    if previous
                    else "",
                    "preceding_result_source_actor": previous["source_actor"]
                    if previous
                    else "",
                    "preceding_result_delta_us": e["time_us"] - previous["time_us"]
                    if previous
                    else "",
                }
                enmity.append(row)
                last_indicator[actor_key] = current
        for i, row in enumerate(capture_work):
            row["later_same_group_packets"] = sum(
                r["group_pair_0"] == row["group_pair_0"]
                and r["connection"] == row["connection"]
                for r in capture_work[i + 1 :]
            )
        work.extend(capture_work)
        if path.name in COMBAT:
            selected = [e for e in stream if e["direction"] == "s2c"]
            summary[path.name] = {
                "first_hostile_result": {
                    k: hostile[0][k]
                    for k in ("capture_packet", "frame", "subevent", "opcode")
                }
                if hostile
                else None,
                "first_result": next(
                    (
                        {
                            k: e[k]
                            for k in ("capture_packet", "frame", "subevent", "opcode")
                        }
                        for e in selected
                        if e["opcode"] in RESULTS
                    ),
                    None,
                ),
                "first_occupancy": next(
                    (
                        {k: e[k] for k in ("capture_packet", "frame", "subevent")}
                        for e in selected
                        if e["opcode"] == 0x187
                    ),
                    None,
                ),
                "occupancy_count": sum(e["opcode"] == 0x187 for e in selected),
                "delete_group_count": sum(e["opcode"] == 0x143 for e in selected),
                "result_count": sum(e["opcode"] in RESULTS for e in selected),
                "enmity_count": sum(e["opcode"] == 0x195 for e in selected),
            }
    account = {
        "schema_version": 1,
        "evidence_class": "packet-capture",
        "inputs": inputs,
        "chronology": "capture packet completing each reconstructed frame, then subevent order; zero-based frame/subevent, one-based capture packet; cross-direction ties unresolved",
        "counts": {
            "occupancy": len(occupancy),
            "group_work": len(work),
            "group_work_properties": len(properties),
            "enmity": len(enmity),
        },
        "combat": summary,
        "occupancy_work_pairs": dict(
            Counter(
                f"{r['occupancy_work_0']},{r['occupancy_work_1']}" for r in occupancy
            )
        ),
        "work_marker_tags": dict(Counter(r["marker_tags"] for r in work)),
        "enmity_values": dict(Counter(str(r["value_u16"]) for r in enmity)),
    }
    return {
        "occupancy.csv": csv_bytes(
            BASE
            + (
                "group_pair_0",
                "header_u32_08",
                "header_u32_0c",
                "occupancy_work_0",
                "occupancy_work_1",
                "localized_name_id",
                "name_length",
                "name_storage_zero",
                "occupancy_reference_u64",
                "group_header_types",
                "occupancy_reference_header_types",
            ),
            occupancy,
        ),
        "group-matches.csv": csv_bytes(
            BASE
            + (
                "group_pair_0",
                "matching_opcode",
                "matching_connection",
                "matching_frame",
                "matching_subevent",
                "matching_capture_packet",
                "matching_application_offset",
            ),
            joins,
        ),
        "group-work.csv": csv_bytes(
            BASE
            + (
                "group_pair_0",
                "running_byte_total",
                "record_count",
                "marker_tags",
                "targets",
                "later_same_group_packets",
                "matching_header_group_types",
            ),
            work,
        ),
        "group-headers.csv": csv_bytes(
            BASE + ("group_pair_18", "group_pair_28", "group_type"), group_headers
        ),
        "deletions.csv": csv_bytes(
            BASE
            + (
                "tuple_u64_00",
                "tuple_u64_08",
                "tuple_u64_10",
                "tuple_u64_18",
                "prior_matching_occupancy_packets",
                "last_matching_occupancy_frame",
            ),
            deletions,
        ),
        "group-work-properties.csv": csv_bytes(
            BASE + ("group_pair_0", "offset", "property_id", "width", "value"),
            properties,
        ),
        "enmity.csv": csv_bytes(
            BASE
            + (
                "target_actor",
                "value_u16",
                "tail_u16",
                "changed_from_previous_indicator",
                "value_changed",
                "target_changed",
                "preceding_result_opcode",
                "preceding_result_frame",
                "preceding_result_subevent",
                "preceding_result_source_actor",
                "preceding_result_delta_us",
            ),
            enmity,
        ),
        "combat-timeline.csv": csv_bytes(
            BASE
            + (
                "opcode",
                "group_pair",
                "request_target_actor",
                "request_owner_actor",
                "result_source_actor",
                "result_target_actors",
                "result_message_ids",
            ),
            timeline,
        ),
        "accounting.json": (json.dumps(account, indent=2) + "\n").encode("ascii"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--public-shape", action="store_true")
    args = parser.parse_args()
    if args.public_shape:
        account = json.loads((OUT / "accounting.json").read_text("ascii"))
        manifest = yaml.safe_load(
            (REPO / "sources/pcap-1.23b/manifest.yaml").read_text("utf-8")
        )
        if {r["capture"]: r["sha256"] for r in account["inputs"]} != {
            m["file"]: m["sha256"] for m in manifest["members"]
        }:
            raise ValueError("study input identity drift")
        for name, count_key in (
            ("occupancy.csv", "occupancy"),
            ("group-work.csv", "group_work"),
            ("group-work-properties.csv", "group_work_properties"),
            ("enmity.csv", "enmity"),
        ):
            with (OUT / name).open(encoding="ascii", newline="") as handle:
                rows = list(csv.DictReader(handle))
            if len(rows) != account["counts"][count_key]:
                raise ValueError("study row accounting drift")
        print(
            "group-combat-wire-contracts: public shape verified; source bytes not replayed"
        )
        return 0
    outputs = build_outputs(default_corpus_paths())
    for name, content in outputs.items():
        path = OUT / name
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                raise ValueError(f"stale study product: {name}")
        else:
            OUT.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(
        f"group-combat-wire-contracts: {'verified' if args.check else 'generated'} {len(outputs)} products"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
