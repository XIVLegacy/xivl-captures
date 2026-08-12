#!/usr/bin/env python3
"""Promote an explicitly supplied opcode catalog into the local snapshot.

All catalog entries and ``observedIn`` values survive. Numeric observations do
not. The output records the source hash, and this tool is not part of refresh.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from _json_io import DATA_DIR, write_json

OUT_PATH = DATA_DIR / "opcode_names.json"


def promote(source_path: Path) -> dict:
    source_bytes = source_path.read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()

    catalog = json.loads(source_bytes.decode("utf-8"))
    lists = catalog[0]["lists"]

    entries = []
    for bucket_entries in lists.values():
        for e in bucket_entries:
            row = {
                "service": e.get("service"),
                "direction": e.get("direction"),
                "opcodeHex": e.get("opcodeHex"),
                "name": e.get("name"),
                "retail_class_name": e.get("retail_class_name"),
            }
            if "confidence" in e:
                row["confidence"] = e["confidence"]
            row["observedIn"] = sorted(e.get("observedIn") or [])
            entries.append(row)

    entries.sort(key=lambda r: (r["service"] or "", int(r["opcodeHex"], 16), r["direction"] or ""))

    return {
        "source": "xivl-opcodes:opcodes.json",
        "source_sha256": source_sha256,
        "evidenceTier": "curated identification layer promoted as local evidence; "
                         "no freshness promise against the sibling catalog",
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote the identification layer of a xivl-opcodes "
                     "opcodes.json into the local derived/opcode_names.json snapshot.")
    parser.add_argument("--source", required=True, type=Path,
                        help="path to the source opcodes.json (no default sibling path)")
    args = parser.parse_args()

    if not args.source.exists():
        print(f"ERROR: --source not found: {args.source}", file=sys.stderr)
        return 2

    mapping = promote(args.source)
    write_json(OUT_PATH, mapping)
    print(f"Wrote {len(mapping['entries'])} entries to {OUT_PATH.relative_to(DATA_DIR.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
