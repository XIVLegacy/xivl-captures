"""Count s2c opcodes following each c2s opcode within a bounded reply window."""

from __future__ import annotations

import argparse
import struct
import sys
import warnings
import zlib
from collections import Counter, defaultdict
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

DEFAULT_OUT = Path(__file__).parent.parent.parent / "derived" / "request_response_pairs.json"

# Safety constraint: a 200ms reply window covers retail round-trip/processing latency without unrelated traffic.
WINDOW_MS = 200
# Wire quirk: omit the always-present 0x00ca/0x00cf heartbeat pair from response counts.
NOISE_OPCODES = {0x00CA, 0x00CF}


def collect_unified_events(path: Path) -> list[tuple[int, str, int]]:
    """Walk one capture and return sorted [(ts_ms, direction, inner_opcode), ...]."""
    streams = reconstruct(path)
    events: list[tuple[int, str, int]] = []
    for direction, blob in streams.items():
        if not blob:
            continue
        for f in parse_outer_frames(blob):
            ts_ms = struct.unpack_from("<Q", f["timestamp"], 0)[0]
            if ts_ms == 0:
                # Safety: timestamp-zero handshake frames cannot be response anchors.
                continue
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
                        _is, inner_opcode = struct.unpack_from("<HH", sub_body, 0)
                        events.append((ts_ms, direction, inner_opcode))
                offset += size
    events.sort()
    return events


def pair_within_window(
    events: list[tuple[int, str, int]],
    window_ms: int,
) -> Counter:
    """Return Counter[(c2s_op, s2c_op)] of co-occurrences in window."""
    pairs: Counter = Counter()
    for i, (ts_i, dir_i, op_i) in enumerate(events):
        if dir_i != "c2s" or op_i in NOISE_OPCODES:
            continue
        for j in range(i + 1, len(events)):
            ts_j, dir_j, op_j = events[j]
            if ts_j - ts_i > window_ms:
                break
            if dir_j == "s2c" and op_j not in NOISE_OPCODES:
                pairs[(op_i, op_j)] += 1
    return pairs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    paths = default_corpus_paths()

    total_pairs: Counter = Counter()
    c2s_totals: Counter = Counter()
    s2c_totals: Counter = Counter()
    pair_captures: dict[tuple[int, int], set[str]] = defaultdict(set)

    capture_count = 0
    for p in paths:
        if not p.is_file():
            continue
        capture_count += 1
        events = collect_unified_events(p)
        for _, d, op in events:
            if d == "c2s" and op not in NOISE_OPCODES:
                c2s_totals[op] += 1
            elif d == "s2c" and op not in NOISE_OPCODES:
                s2c_totals[op] += 1
        cap_pairs = pair_within_window(events, WINDOW_MS)
        for k, n in cap_pairs.items():
            total_pairs[k] += n
            pair_captures[k].add(p.name)

    per_c2s: dict[int, list[dict]] = defaultdict(list)
    for (c2s_op, s2c_op), pair_count in total_pairs.items():
        c2s_total = c2s_totals[c2s_op] or 1
        s2c_total = s2c_totals[s2c_op] or 1
        per_c2s[c2s_op].append(
            {
                "s2cOpcode": s2c_op,
                "s2cOpcodeHex": f"0x{s2c_op:04x}",
                "pairCount": pair_count,
                "captures": len(pair_captures[(c2s_op, s2c_op)]),
                "c2sShare": round(pair_count / c2s_total, 3),
                "s2cShare": round(pair_count / s2c_total, 3),
            }
        )
    for c2s_op in per_c2s:
        per_c2s[c2s_op].sort(key=lambda r: -r["pairCount"])

    out_struct: dict = {
        "windowMs": WINDOW_MS,
        "noiseOpcodesExcluded": [f"0x{op:04x}" for op in sorted(NOISE_OPCODES)],
        "captureCount": capture_count,
        "c2sOpcodes": [],
    }
    for c2s_op, rows in sorted(per_c2s.items()):
        out_struct["c2sOpcodes"].append(
            {
                "c2sOpcode": c2s_op,
                "c2sOpcodeHex": f"0x{c2s_op:04x}",
                "c2sTotal": c2s_totals[c2s_op],
                "topResponses": rows[:20],
            }
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, out_struct)
    print(f"wrote {out_path}")
    print()
    print(
        f"Top c2s -> s2c bindings (window={WINDOW_MS}ms, "
        f"sorted by pair count):"
    )
    flat: list[tuple[int, int, dict]] = []
    for c2s_op, rows in per_c2s.items():
        for r in rows:
            flat.append((c2s_op, r["s2cOpcode"], r))
    flat.sort(key=lambda x: -x[2]["pairCount"])
    for c2s_op, s2c_op, r in flat[:20]:
        print(
            f"  c2s 0x{c2s_op:04x} -> s2c 0x{s2c_op:04x}  "
            f"pairs={r['pairCount']:>4}  caps={r['captures']:>2}  "
            f"c2sShare={r['c2sShare']:.2f}  s2cShare={r['s2cShare']:.2f}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
