#!/usr/bin/env python3
"""Generate or verify per-study derived checksum anchors.

A manifest `checksum_file` covers every other file in its derived tree. Entries
use sorted sha256sum syntax with study-relative paths.

    python tools/build_checksums.py           # rewrite each checksum file
    python tools/build_checksums.py --check    # verify, write nothing, exit 1 if stale
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
STUDIES = REPO_ROOT / "studies"


def studies_with_checksums() -> list[tuple[Path, str]]:
    out = []
    for manifest in sorted(STUDIES.glob("*/manifest.yaml")):
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        checksum_file = (data.get("distilled") or {}).get("checksum_file")
        if checksum_file:
            out.append((manifest.parent, checksum_file))
    return out


def compute(study_dir: Path, checksum_file: str) -> str:
    checksum_path = study_dir / checksum_file
    derived = checksum_path.parent
    entries = []
    for f in derived.rglob("*"):
        if f.is_file() and f != checksum_path:
            rel = f.relative_to(study_dir).as_posix()
            entries.append((rel, hashlib.sha256(f.read_bytes()).hexdigest()))
    entries.sort()
    return "".join(f"{digest}  {rel}\n" for rel, digest in entries)


def parse(text: str) -> dict[str, str]:
    out = {}
    for line in text.splitlines():
        if line.strip():
            digest, rel = line.split(None, 1)
            out[rel.strip()] = digest
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate or verify study checksum anchors.")
    parser.add_argument("--check", action="store_true",
                        help="verify only, write nothing, exit 1 if any anchor is stale")
    args = parser.parse_args()

    problems: list[str] = []
    count = 0
    for study_dir, checksum_file in studies_with_checksums():
        checksum_path = study_dir / checksum_file
        expected = compute(study_dir, checksum_file)
        count += 1
        if not args.check:
            checksum_path.write_text(expected, encoding="utf-8", newline="\n")
            continue
        if not checksum_path.exists():
            problems.append(f"{study_dir.name}: {checksum_file} is missing")
            continue
        actual = parse(checksum_path.read_text(encoding="utf-8"))
        want = parse(expected)
        for rel in sorted(set(want) | set(actual)):
            if rel not in actual:
                problems.append(f"{study_dir.name}: {rel} not anchored (add to {checksum_file})")
            elif rel not in want:
                problems.append(f"{study_dir.name}: {rel} listed but not on disk")
            elif actual[rel] != want[rel]:
                problems.append(f"{study_dir.name}: {rel} hash stale (regenerate)")

    if not args.check:
        print(f"build_checksums.py: wrote {count} checksum file(s)")
        return 0
    if problems:
        print(f"build_checksums.py: {len(problems)} problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"build_checksums.py: OK ({count} checksum file(s) verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
