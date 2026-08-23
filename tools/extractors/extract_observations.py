"""Extract raw opcode, payload-length, context, and witness observations.

This artifact assigns no opcode names or services.
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
import warnings
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _json_io import write_json  # noqa: E402

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from extract_streams import reconstruct_lanes, parse_outer_frames  # type: ignore


DEFAULT_CAP_DIR = Path(os.environ.get(
    "XIVL_PCAP_OBJECTS_DIR",
    str(Path(__file__).resolve().parent.parent.parent / "sources" / "pcap-1.23b" / "objects"),
))
# Bump when extraction changes output; record the version in pipelines/*.yaml and derived/*.meta.yaml.
GENERATOR_VERSION = "1"

DEFAULT_OUT = Path(__file__).parent.parent.parent / "derived" / "observations.json"
DEFAULT_LANE_OUT = Path(__file__).parent.parent.parent / "derived" / "lane_observations.json"


def default_corpus_paths() -> list[Path]:
    """Return all sorted corpus pcaps; lane filtering happens after reconstruction."""
    return sorted(DEFAULT_CAP_DIR.glob("*.pcapng"))


def _game_lane_streams(path: Path) -> dict[str, bytes]:
    """Merge only selected game lanes for the capture-level products."""
    merged = {"c2s": b"", "s2c": b""}
    for connection in reconstruct_lanes(path):
        for direction, blob in connection["streams"].items():
            merged[direction] += blob
    return {direction: blob for direction, blob in merged.items() if blob}


SUB_EVENT_HEADER_LEN = 16  # Wire header: [size:2][type:2][src:4][dst:4][counter:4].

# Wire fact: 0x0003 wrapped actor events carry [inner_size:2][inner_opcode:2][reserved:4] at body offset 16.
SUB_EVENT_CLASS_ACTOR_WRAPPED = 0x0003
INNER_HEADER_LEN = 8


def parse_inner(sub_body: bytes) -> dict | None:
    """Parse the inner-packet header if present. Returns None if too short."""
    if len(sub_body) < INNER_HEADER_LEN:
        return None
    inner_size, inner_opcode = struct.unpack_from("<HH", sub_body, 0)
    return {"inner_size": inner_size, "inner_opcode": inner_opcode}


def parse_sub_events(body: bytes) -> list[dict]:
    """Parse complete sub-events, stopping at padding or an overrun."""
    events = []
    offset = 0
    while offset + SUB_EVENT_HEADER_LEN <= len(body):
        size, ev_type = struct.unpack_from("<HH", body, offset)
        if size == 0:
            break
        if size < SUB_EVENT_HEADER_LEN or offset + size > len(body):
            events.append({"truncated": True, "offset": offset, "claimed_size": size})
            break
        src_actor, dst_actor, counter = struct.unpack_from("<III", body, offset + 4)
        sub_body = body[offset + SUB_EVENT_HEADER_LEN : offset + size]
        record = {
            "offset": offset,
            "size": size,
            "type": ev_type,
            "src_actor": src_actor,
            "dst_actor": dst_actor,
            "counter": counter,
        }
        if ev_type == SUB_EVENT_CLASS_ACTOR_WRAPPED:
            inner = parse_inner(sub_body)
            if inner is not None:
                record["inner_size"] = inner["inner_size"]
                record["inner_opcode"] = inner["inner_opcode"]
        events.append(record)
        offset += size
    return events


def walk_capture(path: Path) -> dict:
    """Return the observation log for one capture."""
    streams = _game_lane_streams(path)
    obs = {"capture": path.name, "directions": {}}
    for direction, blob in streams.items():
        if not blob:
            continue
        frames = parse_outer_frames(blob)
        per_dir = {
            "frames": len(frames),
            "stream_bytes": len(blob),
            "outer_types": {},
            "sub_events": [],
            "zlib_failures": 0,
            "sub_event_truncations": 0,
        }
        for f in frames:
            ot = f["type"]
            ot_bucket = per_dir["outer_types"].setdefault(
                ot,
                {"count": 0, "sizes": set()},
            )
            ot_bucket["count"] += 1
            ot_bucket["sizes"].add(f["size"])

            body = f["body"]
            if direction == "s2c" and len(body) >= 2 and body[0] == 0x78 and body[1] == 0x9C:
                try:
                    body = zlib.decompress(body)
                except zlib.error:
                    per_dir["zlib_failures"] += 1
                    continue

            for ev in parse_sub_events(body):
                if ev.get("truncated"):
                    per_dir["sub_event_truncations"] += 1
                    continue
                per_dir["sub_events"].append(
                    {
                        "outer_type": ot,
                        "sub_type": ev["type"],
                        "sub_size": ev["size"],
                        "src_actor": ev["src_actor"],
                        "dst_actor": ev["dst_actor"],
                        "counter": ev["counter"],
                        "inner_opcode": ev.get("inner_opcode"),
                        "inner_size": ev.get("inner_size"),
                    }
                )
        for ot_data in per_dir["outer_types"].values():
            ot_data["sizes"] = sorted(ot_data["sizes"])
        obs["directions"][direction] = per_dir
    return obs


def walk_capture_lanes(path: Path) -> dict:
    """Return inner-opcode observations without merging TCP connections."""
    result = {"capture": path.name, "connections": []}
    for connection in reconstruct_lanes(path):
        record = {
            "lane": connection["lane"],
            "clientEndpoint": f"{connection['client_endpoint'][0]}:{connection['client_endpoint'][1]}",
            "serverEndpoint": f"{connection['server_endpoint'][0]}:{connection['server_endpoint'][1]}",
            "directions": {},
        }
        for direction, blob in connection["streams"].items():
            opcodes = {}
            for frame in parse_outer_frames(blob):
                body = frame["body"]
                if frame["marker"][1] == 0x01:
                    body = zlib.decompress(body)
                for ev in parse_sub_events(body):
                    opcode = ev.get("inner_opcode")
                    if opcode is None:
                        continue
                    key = f"0x{opcode:04x}"
                    bucket = opcodes.setdefault(key, {"opcode": opcode, "totalCount": 0,
                                                      "innerSizes": set()})
                    bucket["totalCount"] += 1
                    bucket["innerSizes"].add(ev["inner_size"])
            for bucket in opcodes.values():
                bucket["innerSizes"] = sorted(bucket["innerSizes"])
            record["directions"][direction] = {"inner_opcodes": opcodes}
        result["connections"].append(record)
    return result


def aggregate_lanes(per_capture: list[dict]) -> dict:
    """Aggregate inner opcodes by classified retail connection lane."""
    out = {"version": "1.23b", "captures": [c["capture"] for c in per_capture],
           "lanes": {lane: {direction: {} for direction in ("c2s", "s2c")}
                     for lane in ("main", "chat", "unknown")}}
    for cap in per_capture:
        for conn in cap["connections"]:
            for direction, data in conn["directions"].items():
                dst = out["lanes"][conn["lane"]][direction]
                for key, observed in data["inner_opcodes"].items():
                    bucket = dst.setdefault(key, {"opcode": observed["opcode"], "totalCount": 0,
                                                  "innerSizes": set(), "observedIn": set()})
                    bucket["totalCount"] += observed["totalCount"]
                    bucket["innerSizes"].update(observed["innerSizes"])
                    bucket["observedIn"].add(cap["capture"])
    for lane in out["lanes"].values():
        for direction in lane.values():
            for bucket in direction.values():
                bucket["innerSizes"] = sorted(bucket["innerSizes"])
                bucket["observedIn"] = sorted(bucket["observedIn"])
    return out


def aggregate(per_capture: list[dict]) -> dict:
    """Aggregate outer types, sub-event types, and wrapped inner opcodes."""
    out = {
        "version": "1.23b",
        "captures": [c["capture"] for c in per_capture],
        "outer_frames": {"c2s": {}, "s2c": {}},
        "sub_events": {"c2s": {}, "s2c": {}},
        "inner_opcodes": {"c2s": {}, "s2c": {}},
    }

    for cap in per_capture:
        cap_name = cap["capture"]
        for direction, per_dir in cap["directions"].items():
            ot_dst = out["outer_frames"][direction]
            for ot, ot_data in per_dir["outer_types"].items():
                key = f"0x{ot:04x}"
                bucket = ot_dst.setdefault(
                    key,
                    {"opcode": ot, "totalCount": 0, "payloadLengths": set(), "observedIn": set()},
                )
                bucket["totalCount"] += ot_data["count"]
                bucket["payloadLengths"].update(ot_data["sizes"])
                bucket["observedIn"].add(cap_name)
            se_dst = out["sub_events"][direction]
            io_dst = out["inner_opcodes"][direction]
            for ev in per_dir["sub_events"]:
                key = f"0x{ev['sub_type']:04x}"
                bucket = se_dst.setdefault(
                    key,
                    {
                        "opcode": ev["sub_type"],
                        "totalCount": 0,
                        "payloadLengths": set(),
                        "observedIn": set(),
                        "outerTypeContext": {},
                    },
                )
                bucket["totalCount"] += 1
                bucket["payloadLengths"].add(ev["sub_size"])
                bucket["observedIn"].add(cap_name)
                ot_key = f"0x{ev['outer_type']:04x}"
                ctx = bucket["outerTypeContext"].setdefault(
                    ot_key, {"count": 0, "payloadLengths": set()}
                )
                ctx["count"] += 1
                ctx["payloadLengths"].add(ev["sub_size"])

                if ev.get("inner_opcode") is not None:
                    ikey = f"0x{ev['inner_opcode']:04x}"
                    ibucket = io_dst.setdefault(
                        ikey,
                        {
                            "opcode": ev["inner_opcode"],
                            "totalCount": 0,
                            "innerSizes": set(),
                            "subEventSizes": set(),
                            "observedIn": set(),
                        },
                    )
                    ibucket["totalCount"] += 1
                    ibucket["innerSizes"].add(ev["inner_size"])
                    ibucket["subEventSizes"].add(ev["sub_size"])
                    ibucket["observedIn"].add(cap_name)

    for direction in ("c2s", "s2c"):
        for bucket in out["outer_frames"][direction].values():
            bucket["payloadLengths"] = sorted(bucket["payloadLengths"])
            bucket["observedIn"] = sorted(bucket["observedIn"])
        for bucket in out["sub_events"][direction].values():
            bucket["payloadLengths"] = sorted(bucket["payloadLengths"])
            bucket["observedIn"] = sorted(bucket["observedIn"])
            for ctx in bucket["outerTypeContext"].values():
                ctx["payloadLengths"] = sorted(ctx["payloadLengths"])
        for bucket in out["inner_opcodes"][direction].values():
            bucket["innerSizes"] = sorted(bucket["innerSizes"])
            bucket["subEventSizes"] = sorted(bucket["subEventSizes"])
            bucket["observedIn"] = sorted(bucket["observedIn"])

    return out


def render_summary(aggregate_data: dict) -> str:
    """Human-readable summary derived from the clustered observations."""
    lines = []
    lines.append(f"Captures: {len(aggregate_data['captures'])}")
    for c in aggregate_data["captures"]:
        lines.append(f"  {c}")
    lines.append("")

    for direction in ("c2s", "s2c"):
        lines.append(f"=== {direction} outer frame types ===")
        rows = sorted(aggregate_data["outer_frames"][direction].items())
        for key, b in rows:
            lines.append(
                f"  {key}  count={b['totalCount']:>5}  sizes={b['payloadLengths']}  "
                f"observedIn={len(b['observedIn'])} captures"
            )
        lines.append("")

        lines.append(f"=== {direction} sub-event types ===")
        rows = sorted(aggregate_data["sub_events"][direction].items())
        for key, b in rows:
            ctxs = ",".join(sorted(b["outerTypeContext"].keys()))
            lines.append(
                f"  {key}  count={b['totalCount']:>5}  sizes={b['payloadLengths']}  "
                f"underOuter={ctxs}  observedIn={len(b['observedIn'])} captures"
            )
        lines.append("")

        lines.append(f"=== {direction} inner opcodes (real game opcodes) ===")
        rows = sorted(aggregate_data["inner_opcodes"][direction].items())
        for key, b in rows:
            lines.append(
                f"  {key}  count={b['totalCount']:>5}  innerSizes={b['innerSizes']}  "
                f"subSizes={b['subEventSizes']}  observedIn={len(b['observedIn'])} captures"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Opcode/length observation extractor.")
    ap.add_argument("captures", nargs="*", help="Paths to .pcapng files (default: full corpus).")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path.")
    ap.add_argument("--lane-out", default=str(DEFAULT_LANE_OUT), help="Per-lane output JSON path.")
    args = ap.parse_args()

    if args.captures:
        paths = [Path(p) for p in args.captures]
    else:
        paths = default_corpus_paths()

    per_capture = []
    per_capture_lanes = []
    for p in paths:
        if not p.is_file():
            print(f"skip (not found): {p}", file=sys.stderr)
            continue
        per_capture.append(walk_capture(p))
        per_capture_lanes.append(walk_capture_lanes(p))

    if not per_capture:
        print("No captures walked.", file=sys.stderr)
        return 1

    agg = aggregate(per_capture)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, agg)
    write_json(Path(args.lane_out), aggregate_lanes(per_capture_lanes))
    print(f"wrote {out_path}")
    print(f"wrote {args.lane_out}")
    print()
    print(render_summary(agg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
