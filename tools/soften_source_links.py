#!/usr/bin/env python3
"""Retain source citations without linking to excluded source objects."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STUDIES_DIR = REPO_ROOT / "studies"
NOTICE = "> Use the stable source-object citations below to locate this study's evidence."
SOURCE_LINK = re.compile(
    r"\[([^\]\n]+)\]\((?:\.\./)+(sources/[^)\s]+/objects/[^)\s]+)\)"
)


def transformed(text: str) -> tuple[str, int]:
    """Return text with excluded-object links converted to plain citations."""
    updated, count = SOURCE_LINK.subn(
        lambda match: f"{match.group(1)} (`{match.group(2)}`)",
        text,
    )
    if count and NOTICE not in updated:
        split_at = updated.find("\n\n")
        if split_at == -1:
            updated = f"{NOTICE}\n\n{updated}"
        else:
            split_at += 2
            updated = updated[:split_at] + NOTICE + "\n\n" + updated[split_at:]
    return updated, count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="report stale hard links without writing")
    args = parser.parse_args()

    stale: list[Path] = []
    changed_links = 0
    for path in sorted(STUDIES_DIR.rglob("*.md")):
        current = path.read_text(encoding="utf-8")
        updated, count = transformed(current)
        if updated == current:
            continue
        stale.append(path)
        changed_links += count
        if not args.check:
            path.write_text(updated, encoding="utf-8", newline="")

    if args.check and stale:
        print("STALE: shipping studies contain links to excluded source objects:")
        for path in stale:
            print(f"  - {path.relative_to(REPO_ROOT).as_posix()}")
        return 1

    action = "would soften" if args.check else "softened"
    print(f"{action} {changed_links} source link(s) across {len(stale)} study file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
