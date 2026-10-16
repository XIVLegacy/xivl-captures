#!/usr/bin/env python3
"""Reproduce the privacy-preserving retained friend-search exchange census."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from extract_group_combat_contracts import events  # noqa: E402
from extract_observations import default_corpus_paths  # noqa: E402

REPO = SCRIPT_DIR.parents[1]
OUT = REPO / "studies/friendlist-search-wire-exchange/derived"
CAPTURE = "friendlist_search.pcapng"
FIELDS = (
    "direction",
    "connection",
    "lane",
    "capture_packet",
    "frame",
    "subevent",
    "opcode",
    "subevent_bytes",
    "game_message_prefix_bytes",
    "application_bytes",
    "application_nonzero_bytes",
    "application_sha256",
    "capture_completion_delta_us",
    "record_layout",
)


def build_outputs() -> dict[str, bytes]:
    path = next(p for p in default_corpus_paths() if p.name == CAPTURE)
    manifest = yaml.safe_load(
        (REPO / "sources/pcap-1.23b/manifest.yaml").read_text("utf-8")
    )
    member = next(m for m in manifest["members"] if m["file"] == CAPTURE)
    if (path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest()) != (
        member["size_bytes"],
        member["sha256"],
    ):
        raise ValueError("friend-search capture identity mismatch")
    selected = [e for e in events(path) if 0x1DC <= e["opcode"] <= 0x1E0]
    if not selected:
        raise ValueError("friend-search exchange absent")
    anchor_time = selected[0]["time_us"]
    rows = [
        {
            **{
                k: e[k]
                for k in (
                    "direction",
                    "connection",
                    "lane",
                    "capture_packet",
                    "frame",
                    "subevent",
                )
            },
            "opcode": f"0x{e['opcode']:04X}",
            "subevent_bytes": e["size"],
            "game_message_prefix_bytes": 16,
            "application_bytes": len(e["app"]),
            "application_nonzero_bytes": sum(b != 0 for b in e["app"]),
            "application_sha256": hashlib.sha256(e["app"]).hexdigest(),
            "capture_completion_delta_us": e["time_us"] - anchor_time,
            "record_layout": "unassigned",
        }
        for e in selected
    ]
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    accounting = {
        "schema_version": 1,
        "evidence_class": "packet-capture",
        "capture": member,
        "selected_opcodes": [f"0x{op:04X}" for op in range(0x1DC, 0x1E1)],
        "event_count": len(rows),
        "counts": {
            f"{direction}.0x{op:04X}": sum(
                e["direction"] == direction and e["opcode"] == op for e in selected
            )
            for direction in ("c2s", "s2c")
            for op in range(0x1DC, 0x1E1)
        },
        "chronology": "Capture packets completing reconstructed frames, then same-direction frame/subevent order; capture packets one-based, frame/subevent zero-based. Completion timing is not client dispatch or server processing timing.",
        "privacy": "No names, comments, endpoints, actor ids, raw packet bytes, or string-derived record fields are emitted. Payload digests identify the bounded observed applications.",
        "boundary": "One observed request followed by two clientbound application extents. This census does not assign result record counts, stride, field semantics, completeness, or causality from string placement or co-occurrence.",
    }
    return {
        "exchange.csv": out.getvalue().encode("ascii"),
        "accounting.json": (json.dumps(accounting, indent=2) + "\n").encode("ascii"),
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
        if account["capture"] != next(
            m for m in manifest["members"] if m["file"] == CAPTURE
        ):
            raise ValueError("friend-search public input drift")
        with (OUT / "exchange.csv").open(encoding="ascii", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if len(rows) != account["event_count"] or any(
            int(r["subevent_bytes"]) != 32 + int(r["application_bytes"]) for r in rows
        ):
            raise ValueError("friend-search public row accounting drift")
    else:
        for name, content in build_outputs().items():
            path = OUT / name
            if args.check:
                if not path.is_file() or path.read_bytes() != content:
                    raise ValueError(f"stale friend-search product: {name}")
            else:
                OUT.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    print(
        f"friendlist-search-wire-exchange: {'verified' if args.check else 'generated'} 2 products"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
