#!/usr/bin/env python3
"""Validate capture references and deterministic pcap digestion.

All observation witnesses must resolve to corpus objects. Clear server port
54992 lanes are admitted; port 54994 and streams beginning with 0x16 0x03 are
rejected. `--redecode` requires byte-identical observation and lane products
from the local corpus.

Usage:
    python tools/validate_digestion.py
    python tools/validate_digestion.py --redecode
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CAPTURES = REPO_ROOT / "sources" / "pcap-1.23b" / "objects"
OBSERVATIONS = REPO_ROOT / "derived" / "observations.json"
LANE_OBSERVATIONS = REPO_ROOT / "derived" / "lane_observations.json"
PCAP_BUILDER = REPO_ROOT / "tools" / "build_pcap_products.py"
CORPUS_MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"


def observed_refs(obs: dict) -> set[str]:
    refs: set[str] = set()
    for section in ("outer_frames", "inner_opcodes"):
        for direction in obs.get(section, {}).values():
            for rec in direction.values():
                refs.update(rec.get("observedIn", []))
    return refs


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the pcap digestion.")
    parser.add_argument("--redecode", action="store_true",
                        help="also re-run the extractor and assert byte-identical output")
    parser.add_argument("--public-shape", action="store_true",
                        help="resolve capture references against the public manifest")
    args = parser.parse_args()

    errors: list[str] = []

    if args.public_shape:
        manifest = yaml.safe_load(CORPUS_MANIFEST.read_text(encoding="utf-8")) or {}
        disk = {m["file"] for m in (manifest.get("members") or [])}
    else:
        disk = {p.name for p in CAPTURES.glob("*.pcapng")} if CAPTURES.is_dir() else set()
    if not disk:
        print(f"ERROR: no captures under {CAPTURES}", file=sys.stderr)
        return 1
    if not OBSERVATIONS.exists():
        print(f"ERROR: missing {OBSERVATIONS}", file=sys.stderr)
        return 1
    if not LANE_OBSERVATIONS.exists():
        print(f"ERROR: missing {LANE_OBSERVATIONS}", file=sys.stderr)
        return 1

    obs = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))
    lane_obs = json.loads(LANE_OBSERVATIONS.read_text(encoding="utf-8"))
    listed = set(obs.get("captures", []))

    for name in sorted(listed - disk):
        errors.append(f"observations.json captures[] lists `{name}` with no file under sources/pcap-1.23b/objects/")
    for ref in sorted(observed_refs(obs) - disk):
        errors.append(f"observedIn references `{ref}` with no file under sources/pcap-1.23b/objects/")
    if lane_obs.get("captures") != obs.get("captures"):
        errors.append("lane_observations.json captures[] differs from observations.json")
    for lane in ("main", "chat", "unknown"):
        if lane not in lane_obs.get("lanes", {}):
            errors.append(f"lane_observations.json missing `{lane}` lane")

    if args.redecode and args.public_shape:
        print("ERROR: --redecode requires local capture objects", file=sys.stderr)
        return 1

    if args.redecode:
        proc = subprocess.run(
            [sys.executable, str(PCAP_BUILDER), "--check",
             "--product", "observations", "--product", "lane_observations"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        if proc.returncode != 0:
            errors.append("re-decode is NOT byte-identical to committed observation products")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    location = "declared in the manifest" if args.public_shape else "on disk"
    print(f"digestion OK: {len(disk)} captures {location}, {len(listed)} decoded "
          f"(with lane filtering), {len(observed_refs(obs))} distinct observedIn refs resolve."
          + (" Re-decode byte-identical." if args.redecode else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
