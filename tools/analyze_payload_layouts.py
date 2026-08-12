"""Infer constant, zero-pad, and variable runs in sampled opcode payloads.

Only the most common sub-size is analyzed. Other observed sizes are flagged.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from _json_io import write_json

# Bump when analysis changes output; record the version in pipelines/*.yaml and derived/*.meta.yaml.
GENERATOR_VERSION = "1"

DEFAULT_IN = Path(__file__).parent.parent / "derived" / "payload_samples.json"
DEFAULT_OUT = Path(__file__).parent.parent / "derived" / "payload_layouts.json"


def classify_offset(values: list[int]) -> dict:
    """Classify a single byte offset across samples."""
    distinct = sorted(set(values))
    if len(distinct) == 1:
        v = distinct[0]
        return {
            "role": "zero_pad" if v == 0 else "constant",
            "value": v,
            "distinct": 1,
        }
    return {
        "role": "variable",
        "distinct": len(distinct),
        "sample_values": distinct[:8],
    }


def group_runs(per_offset: list[dict]) -> list[dict]:
    """Merge consecutive offsets with the same role+value into a single run."""
    runs: list[dict] = []
    for offset, info in enumerate(per_offset):
        if not runs:
            runs.append({"offset": offset, "width": 1, **info})
            continue
        last = runs[-1]
        last_end = last["offset"] + last["width"]
        if last_end != offset:
            runs.append({"offset": offset, "width": 1, **info})
            continue
        if (
            last["role"] == info["role"]
            and last["role"] in ("constant", "zero_pad")
            and last.get("value") == info.get("value")
        ):
            last["width"] += 1
            continue
        if last["role"] == "variable" and info["role"] == "variable":
            last["width"] += 1
            # Keep first-position samples; downstream treats variable runs as byte-wise distinct.
            continue
        runs.append({"offset": offset, "width": 1, **info})
    return runs


def analyze_key(samples: list[dict]) -> dict:
    """Compute the layout report for one (direction, opcode) bundle."""
    sizes = Counter(s["sub_size"] for s in samples)
    most_common_size, _ = sizes.most_common(1)[0]
    aligned = [s for s in samples if s["sub_size"] == most_common_size]

    # Wire fact: sub_size includes the 16-byte sub-event header, but `bytes` starts after it.
    expected_body_len = most_common_size - 16
    bytes_per_sample = [bytes.fromhex(s["bytes"]) for s in aligned]
    bytes_per_sample = [b for b in bytes_per_sample if len(b) == expected_body_len]
    if not bytes_per_sample:
        return {
            "common_sub_size": most_common_size,
            "sub_size_distribution": dict(sizes),
            "sample_count": 0,
            "fields": [],
            "warning": "no samples matched expected body length",
        }

    body_len = len(bytes_per_sample[0])
    per_offset_classes: list[dict] = []
    for offset in range(body_len):
        column = [b[offset] for b in bytes_per_sample]
        per_offset_classes.append(classify_offset(column))

    return {
        "common_sub_size": most_common_size,
        "sub_size_distribution": dict(sizes),
        "sample_count": len(bytes_per_sample),
        "body_length": body_len,
        "fields": group_runs(per_offset_classes),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=str(DEFAULT_IN))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    payload_samples = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    out_struct = {
        "captureCount": payload_samples.get("captureCount"),
        "layouts": {"c2s": {}, "s2c": {}},
    }

    for direction in ("c2s", "s2c"):
        keys = payload_samples["samples"].get(direction, {})
        for hex_key, bundle in keys.items():
            samples = bundle.get("samples", [])
            if not samples:
                continue
            out_struct["layouts"][direction][hex_key] = {
                "opcode": bundle["opcode"],
                **analyze_key(samples),
            }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, out_struct)
    print(f"wrote {out_path}")

    print()
    print("Spot summary - high-frequency opcodes:")
    for direction, opcodes_of_interest in (
        ("c2s", [0x0001, 0x00CA, 0x012D]),
        ("s2c", [0x0001, 0x00CA, 0x00CF, 0x00D0, 0x00D2]),
    ):
        for op in opcodes_of_interest:
            entry = out_struct["layouts"][direction].get(f"0x{op:04x}")
            if not entry:
                continue
            variable_runs = [f for f in entry["fields"] if f["role"] == "variable"]
            const_runs = [f for f in entry["fields"] if f["role"] != "variable"]
            print(
                f"  {direction} 0x{op:04x}: body={entry['body_length']}B, "
                f"variable_runs={len(variable_runs)}, const_runs={len(const_runs)}, "
                f"samples={entry['sample_count']}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
