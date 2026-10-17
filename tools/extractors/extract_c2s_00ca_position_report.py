#!/usr/bin/env python3
"""Build the sanitized c2s 0x00CA position-report study from two Gridania captures.

Output carries aggregate counts and statistics only. Raw coordinates,
timestamps, reserved bytes, and payload bytes stay out of the products.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools" / "extractors"
OBJECTS = Path(
    os.environ.get(
        "XIVL_PCAP_OBJECTS_DIR", REPO_ROOT / "sources" / "pcap-1.23b" / "objects"
    )
)
MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"
STUDY_ID = "c2s-00ca-position-report"
OUT = REPO_ROOT / "studies" / STUDY_ID / "derived"

sys.path.insert(0, str(TOOLS))

GENERATOR_VERSION = "1"
CAPTURES = ("move_around_gridania.pcapng", "moving_around_gridania.pcapng")
OPCODE = 0x00CA
SUB_EVENT_SIZE = 64
# Offsets into the wrapped-actor sub-event body that follows the 16-byte sub-event header.
BODY_LEN = 48
TS_PREFIX_OFFSET = 8
TS_OFFSET = 16
POS_OFFSET = 24
MOVE_STATE_OFFSET = 40
RESERVED_OFFSET = 42
LONG_STEP = 1.0
STEP_BINS = (("lt_0.5", 0.5), ("0.5_to_1", 1.0), ("1_to_2", 2.0), ("ge_2", None))
WINDOW_SECONDS = 10


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_report(body: bytes) -> dict:
    """Decode one 48-byte wrapped-actor body into the position-report fields."""
    if len(body) != BODY_LEN:
        raise ValueError(f"unexpected body length {len(body)}")
    x, y, z, rot = struct.unpack_from("<4f", body, POS_OFFSET)
    (ts,) = struct.unpack_from("<Q", body, TS_OFFSET)
    (ts_prefix,) = struct.unpack_from("<Q", body, TS_PREFIX_OFFSET)
    (move_state,) = struct.unpack_from("<H", body, MOVE_STATE_OFFSET)
    return {
        "ts": ts,
        "ts_prefix": ts_prefix,
        "x": x,
        "y": y,
        "z": z,
        "rot": rot,
        "move_state": move_state,
        "reserved": body[RESERVED_OFFSET:BODY_LEN],
    }


def circular_stats(offsets: list[float]) -> dict:
    n = len(offsets)
    c = sum(math.cos(d) for d in offsets) / n
    s = sum(math.sin(d) for d in offsets) / n
    return {
        "n": n,
        "resultant_length": round(math.hypot(c, s), 4),
        "mean_offset_rad": round(math.atan2(s, c), 4),
    }


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


def percentile(sorted_values: list[float], fraction: float) -> float:
    """Nearest-rank percentile."""
    rank = max(1, math.ceil(fraction * len(sorted_values)))
    return sorted_values[rank - 1]


def distribution(values: list[float]) -> dict:
    ordered = sorted(values)
    mid = len(ordered) // 2
    median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2
    return {
        "n": len(ordered),
        "mean": round(sum(ordered) / len(ordered), 4),
        "median": round(median, 4),
        "p5": round(percentile(ordered, 0.05), 4),
        "p95": round(percentile(ordered, 0.95), 4),
        "min": round(ordered[0], 4),
        "max": round(ordered[-1], 4),
    }


def step_bin(length: float) -> str:
    for label, upper in STEP_BINS:
        if upper is None or length < upper:
            return label
    raise AssertionError("unreachable")


def analyze_reports(reports: list[dict]) -> dict:
    """Aggregate one capture's ordered c2s 0x00CA reports."""
    steps = []
    for prev, cur in zip(reports, reports[1:]):
        dx = cur["x"] - prev["x"]
        dz = cur["z"] - prev["z"]
        steps.append(
            {
                "length": math.hypot(dx, dz),
                "heading": math.atan2(dx, dz),
                "move_state": cur["move_state"],
                "ts": cur["ts"],
                "changed": (cur["x"], cur["y"], cur["z"])
                != (prev["x"], prev["y"], prev["z"]),
                "rot": cur["rot"],
            }
        )

    changed_by_state = Counter(str(s["move_state"]) for s in steps if s["changed"])
    rotations = [r["rot"] for r in reports]
    result = {
        "records": len(reports),
        "timestamp_prefix_equals_payload": sum(
            1 for r in reports if r["ts_prefix"] == r["ts"]
        ),
        "timestamp_high_dword_nonzero": sum(1 for r in reports if r["ts"] >> 32),
        "timestamp_non_decreasing": all(
            b["ts"] >= a["ts"] for a, b in zip(reports, reports[1:])
        ),
        "reserved_distinct_values": len({r["reserved"] for r in reports}),
        "rot_min": round(min(rotations), 4),
        "rot_max": round(max(rotations), 4),
        "move_state_counts": {
            k: v
            for k, v in sorted(Counter(str(r["move_state"]) for r in reports).items())
        },
        "position_changing_by_move_state": dict(sorted(changed_by_state.items())),
        "position_changing_total": sum(changed_by_state.values()),
    }

    moving = [s for s in steps if s["changed"] and s["length"] > 0]
    result["horizontal_step_length_bins"] = {
        label: sum(1 for s in moving if step_bin(s["length"]) == label)
        for label, _ in STEP_BINS
    }

    state2 = [s for s in moving if s["move_state"] == 2]
    offsets_all = [wrap(s["rot"] - s["heading"]) for s in state2]
    offsets_long = [
        wrap(s["rot"] - s["heading"]) for s in state2 if s["length"] >= LONG_STEP
    ]
    offsets_short = [
        wrap(s["rot"] - s["heading"]) for s in state2 if s["length"] < LONG_STEP
    ]
    result["rotation"] = {
        "all_steps": circular_stats(offsets_all),
        "steps_ge_1": circular_stats(offsets_long),
        "steps_lt_1": circular_stats(offsets_short),
    }
    result["rotation_offsets"] = offsets_long

    first = next(i for i, r in enumerate(reports) if r["move_state"] == 2)
    last = max(i for i, r in enumerate(reports) if r["move_state"] == 2)
    run = reports[first : last + 1]
    run_steps = [
        {
            "length": math.hypot(b["x"] - a["x"], b["z"] - a["z"]),
            "ts": b["ts"],
        }
        for a, b in zip(run, run[1:])
    ]
    duration = run[-1]["ts"] - run[0]["ts"]
    path = sum(s["length"] for s in run_steps)
    interior = {}
    for s in run_steps:
        if run[0]["ts"] < s["ts"] < run[-1]["ts"]:
            interior.setdefault(s["ts"], []).append(s["length"])
    seconds = sorted(interior)
    contiguous = all(b - a == 1 for a, b in zip(seconds, seconds[1:]))
    bucket = [sum(interior[t]) for t in seconds]
    windows = [
        sum(bucket[i : i + WINDOW_SECONDS]) / WINDOW_SECONDS
        for i in range(0, len(bucket) - WINDOW_SECONDS + 1, WINDOW_SECONDS)
    ]
    run_info = {
        "all_reports_move_state_2": all(r["move_state"] == 2 for r in run),
        "reports": len(run),
        "duration_seconds": duration,
        "path_length": round(path, 1),
        "mean_speed": round(path / duration, 2),
        "interior_seconds": len(seconds),
        "interior_seconds_contiguous": contiguous,
        "reports_per_interior_second": {
            str(k): v
            for k, v in sorted(Counter(len(interior[t]) for t in seconds).items())
        },
        "second_bucket_speed": distribution(bucket),
        "window_10s_speed": distribution(windows),
    }
    result["run"] = run_info
    return result


def walk_reports(path: Path) -> list[dict]:
    from extract_payload_samples import walk_capture_payloads  # type: ignore

    sizes = Counter()
    reports = []
    for record in walk_capture_payloads(path):
        if record["direction"] != "c2s" or record["opcode"] != OPCODE:
            continue
        sizes[record["sub_size"]] += 1
        reports.append(decode_report(bytes.fromhex(record["bytes"])))
    if set(sizes) != {SUB_EVENT_SIZE}:
        raise ValueError(f"unexpected sub-event sizes {dict(sizes)}")
    return reports


def load_manifest_members() -> dict:
    import yaml

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    members = {m["file"]: m for m in manifest.get("members", [])}
    return {name: members[name] for name in CAPTURES}


def build_accounting() -> dict:
    members = load_manifest_members()
    captures = {}
    combined_offsets = []
    for name in CAPTURES:
        path = OBJECTS / name
        if sha256(path) != members[name]["sha256"]:
            raise ValueError(f"{name}: SHA-256 differs from the source manifest")
        analysis = analyze_reports(walk_reports(path))
        combined_offsets.extend(analysis.pop("rotation_offsets"))
        captures[name] = {
            "sha256": members[name]["sha256"],
            "size_bytes": members[name]["size_bytes"],
            **analysis,
        }
    return {
        "study": STUDY_ID,
        "generator_version": GENERATOR_VERSION,
        "evidence_class": "packet-capture",
        "opcode": "0x00ca",
        "direction": "c2s",
        "sub_event_size": SUB_EVENT_SIZE,
        "long_step_threshold": LONG_STEP,
        "captures": captures,
        "combined_rotation_steps_ge_1": circular_stats(combined_offsets),
    }


def render_verdicts(acc: dict) -> str:
    caps = acc["captures"]
    names = list(caps)
    short = {n: n.removesuffix(".pcapng") for n in names}

    def cell(value):
        return ("yes" if value else "no") if isinstance(value, bool) else str(value)

    def row(label, fn):
        return (
            "| " + label + " | " + " | ".join(cell(fn(caps[n])) for n in names) + " |"
        )

    head = "| Quantity | " + " | ".join(f"`{short[n]}`" for n in names) + " |"
    rule = "|---|" + "---:|" * len(names)
    lines = [
        "# Client Position Report 0x00CA Observations",
        "",
        "Every figure below is aggregated from the sent client-to-server `0x00ca`",
        "reports in two Gridania captures. The products hold counts and",
        "statistics only. They hold no coordinates, timestamps, or payload bytes.",
        "",
        "## Record shape",
        "",
        f"Every record is a {acc['sub_event_size']}-byte sub-event. Offsets below",
        "count from the start of the 48-byte wrapped-actor body that follows the",
        "16-byte sub-event header.",
        "",
        "| Body offset | Size | Field |",
        "|---:|---:|---|",
        "| 8 | 8 | timestamp copy, equal to the payload timestamp |",
        "| 16 | 8 | timestamp, low dword only, steps of one second between reports |",
        "| 24 | 4 | x as float32 |",
        "| 28 | 4 | y as float32 |",
        "| 32 | 4 | z as float32 |",
        "| 36 | 4 | rotation as float32 radians |",
        "| 40 | 2 | moveState as u16 |",
        "| 42 | 6 | reserved, varying bytes |",
        "",
        "The field names and offsets agree with",
        "xivl-client-structs:manifests/c2s_payload_decoding.json `c2s_0x00ca`.",
        "",
        "## Capture checks",
        "",
        head,
        rule,
        row("Source SHA-256", lambda c: f"`{c['sha256']}`"),
        row("Records", lambda c: c["records"]),
        row(
            "Timestamp copy equals timestamp",
            lambda c: c["timestamp_prefix_equals_payload"],
        ),
        row(
            "Timestamp high dword nonzero",
            lambda c: c["timestamp_high_dword_nonzero"],
        ),
        row("Timestamps non-decreasing", lambda c: c["timestamp_non_decreasing"]),
        row("Distinct reserved values", lambda c: c["reserved_distinct_values"]),
        row("Rotation minimum", lambda c: c["rot_min"]),
        row("Rotation maximum", lambda c: c["rot_max"]),
        "",
        "## moveState values",
        "",
        head,
        rule,
    ]
    states = sorted({s for c in caps.values() for s in c["move_state_counts"]})
    for s in states:
        lines.append(
            row(f"moveState {s}", lambda c, s=s: c["move_state_counts"].get(s, 0))
        )
    lines += [
        row("Position-changing reports", lambda c: c["position_changing_total"]),
    ]
    for s in states:
        lines.append(
            row(
                f"Position-changing with moveState {s}",
                lambda c, s=s: c["position_changing_by_move_state"].get(s, 0),
            )
        )
    lines += [
        "",
        "A report is position-changing when its x, y, or z differs from the",
        "previous report in stream order. Only values 0 and 2 occur. Every idle",
        "record with value 0 sits before or after the single run of value 2.",
        "Stream order is the reconstructed client-to-server stream order.",
        "",
        "## Rotation against travel direction",
        "",
        "For each step between consecutive reports, dx is the x change and dz is",
        "the z change. The travel heading is atan2(dx, dz) in radians. A heading",
        "of 0 points along +z and a positive heading turns toward +x. The offset",
        "is the rotation of the report that ends the step minus that heading,",
        "wrapped into the range from -pi to pi. Only steps ending in a moveState",
        "2 report and with a nonzero horizontal length are counted. The",
        "resultant length is the circular mean resultant length of the offsets,",
        "where 1 means every offset is identical.",
        "",
        "| Capture | Step set | Steps | Resultant length | Mean offset rad |",
        "|---|---|---:|---:|---:|",
    ]
    labels = (
        ("all_steps", "all steps"),
        ("steps_ge_1", "length 1.0 or more"),
        ("steps_lt_1", "length under 1.0"),
    )
    for n in names:
        for key, label in labels:
            r = caps[n]["rotation"][key]
            lines.append(
                f"| `{short[n]}` | {label} | {r['n']} | "
                f"{r['resultant_length']} | {r['mean_offset_rad']} |"
            )
    r = acc["combined_rotation_steps_ge_1"]
    lines += [
        f"| both captures | length 1.0 or more | {r['n']} | "
        f"{r['resultant_length']} | {r['mean_offset_rad']} |",
        "",
        "Horizontal step lengths fall into two groups of similar size, one under",
        "0.5 and one between 1 and 2. A single step length is therefore not a",
        "speed. The rows split by length show the relation holds in both groups.",
        "",
        "| Horizontal step length | "
        + " | ".join(f"`{short[n]}`" for n in names)
        + " |",
        rule,
    ]
    for label, _ in STEP_BINS:
        lines.append(
            row(
                f"bin {label}",
                lambda c, label=label: c["horizontal_step_length_bins"][label],
            )
        )
    lines += [
        "",
        "## Horizontal speed over the moveState 2 run",
        "",
        "Each capture holds one unbroken run of moveState 2 reports. Mean speed is",
        "the horizontal path length of the run divided by the timestamp span of",
        "the run. Timestamps have a resolution of one second, so the span carries",
        "an error of up to one second at each end. The run can include pauses",
        "and unchanged reports, which lower the minimum rows. Second buckets sum the step",
        "lengths of reports that share a timestamp second, using only seconds",
        "strictly inside the run. Window rows average 10 consecutive interior",
        "seconds.",
        "",
        head,
        rule,
        row(
            "Run holds only moveState 2", lambda c: c["run"]["all_reports_move_state_2"]
        ),
        row("Run reports", lambda c: c["run"]["reports"]),
        row("Run timestamp span seconds", lambda c: c["run"]["duration_seconds"]),
        row("Run horizontal path length", lambda c: c["run"]["path_length"]),
        row("Mean speed units per second", lambda c: c["run"]["mean_speed"]),
        row("Interior seconds", lambda c: c["run"]["interior_seconds"]),
    ]
    for k in sorted(
        {k for c in caps.values() for k in c["run"]["reports_per_interior_second"]}
    ):
        lines.append(
            row(
                f"Interior seconds with {k} reports",
                lambda c, k=k: c["run"]["reports_per_interior_second"].get(k, 0),
            )
        )
    for key, title in (
        ("second_bucket_speed", "Second bucket"),
        ("window_10s_speed", "10 second window"),
    ):
        for stat in ("n", "mean", "median", "p5", "p95", "min", "max"):
            lines.append(
                row(
                    f"{title} {stat}", lambda c, key=key, stat=stat: c["run"][key][stat]
                )
            )
    lines += [
        "",
        "The 0x00d0 on-foot baseline pair recorded in",
        "studies/movement-speed-band-observations/derived/observed-bands.md",
        "carries 2.0 in slot 0 and 5.0 in slot 1. The observed mean speed lies",
        "near 5.0. This study",
        "does not establish that the 0x00d0 value governs the reported movement,",
        "that the unit is the same, or which gait the run was.",
        "",
        "## Not established",
        "",
        "- Whether moveState 2 means walk, run, or another gait.",
        "- The moveState values for any other gait, for sprint, for mounts, for",
        "  jumping or swimming, or for combat states.",
        "- Any zone other than Gridania.",
        "- Any collision, slope, or terrain effect on speed.",
        "- The meaning of the reserved bytes, which vary between records.",
        "- Whether the alternation of long and short steps is a client timer",
        "  artifact or deliberate.",
        "- Anything beyond on-foot play by one character in two sessions.",
        "",
    ]
    return "\n".join(lines)


def render_products(acc: dict) -> dict[str, bytes]:
    return {
        "accounting.json": (json.dumps(acc, indent=2, sort_keys=True) + "\n").encode(
            "ascii"
        ),
        "verdicts.md": render_verdicts(acc).encode("ascii"),
    }


def build_outputs() -> dict[str, bytes]:
    return render_products(build_accounting())


def validate_public_shape() -> int:
    try:
        acc_path, md_path = OUT / "accounting.json", OUT / "verdicts.md"
        acc = json.loads(acc_path.read_text(encoding="ascii"))
        if acc.get("study") != STUDY_ID or set(acc["captures"]) != set(CAPTURES):
            raise ValueError("study or capture set changed")
        if md_path.read_bytes() != render_verdicts(acc).encode("ascii"):
            raise ValueError("verdicts.md differs from accounting.json")
        if acc_path.read_bytes() != render_products(acc)["accounting.json"]:
            raise ValueError("accounting.json is not canonically formatted")
        members = load_manifest_members()
        for name, cap in acc["captures"].items():
            if cap["sha256"] != members[name]["sha256"]:
                raise ValueError(f"{name}: source hash differs from manifest")
            if sum(cap["move_state_counts"].values()) != cap["records"]:
                raise ValueError(f"{name}: moveState counts do not sum")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(
            f"c2s 0x00ca position report: public shape invalid: {exc}", file=sys.stderr
        )
        return 1
    print("verified c2s 0x00ca position report public shape")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare, write nothing")
    parser.add_argument(
        "--public-shape",
        action="store_true",
        help="validate committed products without capture inputs",
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
        print("stale c2s 0x00ca products: " + ", ".join(stale), file=sys.stderr)
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {len(products)} c2s 0x00ca position report products")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
