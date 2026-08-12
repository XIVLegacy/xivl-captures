"""Compute per-opcode cadence from outer-frame timestamps.

Deltas are calculated only within a capture because session epochs differ.
"""

from __future__ import annotations

import argparse
import statistics
import struct
import sys
import warnings
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _json_io import write_json  # noqa: E402

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from extract_streams import reconstruct, parse_outer_frames  # type: ignore
from extract_observations import (  # type: ignore
    SUB_EVENT_CLASS_ACTOR_WRAPPED,
    SUB_EVENT_HEADER_LEN,
    INNER_HEADER_LEN,
    default_corpus_paths,
)

# Bump when extraction changes output; record the version in pipelines/*.yaml and derived/*.meta.yaml.
GENERATOR_VERSION = "1"

DEFAULT_OUT = Path(__file__).parent.parent.parent / "derived" / "timing.json"


def walk_capture_timings(path: Path) -> list[tuple[str, int, int]]:
    """Return list of (direction, opcode, timestamp_ms) per wrapped sub-event."""
    streams = reconstruct(path)
    out: list[tuple[str, int, int]] = []
    for direction, blob in streams.items():
        if not blob:
            continue
        for f in parse_outer_frames(blob):
            timestamp_ms = struct.unpack_from("<Q", f["timestamp"], 0)[0]
            body = f["body"]
            if direction == "s2c" and len(body) >= 2 and body[0] == 0x78 and body[1] == 0x9C:
                try:
                    body = zlib.decompress(body)
                except zlib.error:
                    continue
            offset = 0
            while offset + SUB_EVENT_HEADER_LEN <= len(body):
                size, ev_type = struct.unpack_from("<HH", body, offset)
                if size == 0 or size < SUB_EVENT_HEADER_LEN or offset + size > len(body):
                    break
                if ev_type == SUB_EVENT_CLASS_ACTOR_WRAPPED:
                    sub_body = body[offset + SUB_EVENT_HEADER_LEN : offset + size]
                    if len(sub_body) >= INNER_HEADER_LEN:
                        _inner_size, inner_opcode = struct.unpack_from("<HH", sub_body, 0)
                        out.append((direction, inner_opcode, timestamp_ms))
                offset += size
    return out


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    k = (len(sorted_values) - 1) * pct
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return float(sorted_values[f])
    return sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    paths = default_corpus_paths()

    deltas: dict[tuple[str, int], list[float]] = {}
    counts: dict[tuple[str, int], int] = {}
    captures_seen_in: dict[tuple[str, int], set[str]] = {}

    capture_count = 0
    for p in paths:
        if not p.is_file():
            continue
        capture_count += 1
        per_key: dict[tuple[str, int], list[int]] = {}
        for direction, opcode, ts_ms in walk_capture_timings(p):
            per_key.setdefault((direction, opcode), []).append(ts_ms)
            counts[(direction, opcode)] = counts.get((direction, opcode), 0) + 1
            captures_seen_in.setdefault((direction, opcode), set()).add(p.name)
        for key, ts_list in per_key.items():
            ts_list.sort()
            for i in range(1, len(ts_list)):
                d = ts_list[i] - ts_list[i - 1]
                if 0 <= d <= 60_000:  # Ignore gaps over 60 seconds between scenes.
                    deltas.setdefault(key, []).append(float(d))

    out_struct: dict = {
        "captureCount": capture_count,
        "timing": {"c2s": {}, "s2c": {}},
    }
    for (direction, opcode), ds in deltas.items():
        if not ds:
            continue
        entry = {
            "opcode": opcode,
            "totalCount": counts[(direction, opcode)],
            "deltaSamples": len(ds),
            "capturesSeen": len(captures_seen_in[(direction, opcode)]),
            "meanMs": round(statistics.fmean(ds), 2),
            "medianMs": round(percentile(ds, 0.5), 2),
            "p95Ms": round(percentile(ds, 0.95), 2),
            "minMs": round(min(ds), 2),
            "maxMs": round(max(ds), 2),
        }
        out_struct["timing"][direction][f"0x{opcode:04x}"] = entry

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, out_struct)
    print(f"wrote {out_path}  ({capture_count} captures walked)")

    print()
    print("Notable cadences (highest-volume opcodes):")
    flat = []
    for direction in ("c2s", "s2c"):
        for hex_key, entry in out_struct["timing"][direction].items():
            flat.append((direction, entry))
    flat.sort(key=lambda x: -x[1]["totalCount"])
    for direction, entry in flat[:10]:
        print(
            f"  {direction} 0x{entry['opcode']:04x}  "
            f"count={entry['totalCount']:>5}  "
            f"median={entry['medianMs']:>7.1f}ms  "
            f"p95={entry['p95Ms']:>7.1f}ms  "
            f"in {entry['capturesSeen']} captures"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
