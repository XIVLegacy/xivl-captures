#!/usr/bin/env python3
"""Fail when an authored Markdown link has a missing in-repo target.

Scans root, studies, docs, and catalog Markdown. Raw source objects are valid
targets but are not scanned. Web links, anchors, and paths outside the repo are
skipped.
"""
from __future__ import annotations

import re
import os
import sys
from pathlib import Path
from urllib.parse import unquote

from restricted_paths import is_present_without_corpus

REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ["studies", "docs", "catalog"]
SKIP_SCHEMES = ("http://", "https://", "mailto:", "tel:", "ftp://", "data:")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
CORPUS_ABSENT = os.environ.get("XIVL_CORPUS_ABSENT") == "1"


def md_files() -> list[Path]:
    files: list[Path] = sorted(REPO_ROOT.glob("*.md"))
    for d in SCAN_DIRS:
        files.extend(sorted((REPO_ROOT / d).rglob("*.md")))
    return files


def link_target(raw: str) -> str | None:
    """Normalize a raw `](...)` payload to a bare local path, or None to skip."""
    t = raw.strip()
    if t.startswith("<") and t.endswith(">"):
        t = t[1:-1].strip()
    for sep in (' "', " '"):
        if sep in t:
            t = t.split(sep, 1)[0].strip()
    if not t or t.startswith("#") or t.lower().startswith(SKIP_SCHEMES):
        return None
    t = t.split("#", 1)[0].split("?", 1)[0]
    return t or None


def resolves(md_file: Path, target: str) -> bool | None:
    """True/False if the target is in-repo; None if it escapes the repo (skip)."""
    for candidate in (target, unquote(target)):
        dest = (md_file.parent / candidate).resolve()
        if not dest.is_relative_to(REPO_ROOT):
            return None
        relative = dest.relative_to(REPO_ROOT).as_posix()
        if CORPUS_ABSENT and not is_present_without_corpus(relative):
            return None
        if dest.exists():
            return True
    return False


def main() -> int:
    broken: list[str] = []
    checked = 0
    for md in md_files():
        rel = md.relative_to(REPO_ROOT).as_posix()
        for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for m in LINK.finditer(line):
                target = link_target(m.group(1))
                if target is None:
                    continue
                verdict = resolves(md, target)
                if verdict is None:
                    continue
                checked += 1
                if verdict is False:
                    broken.append(f"{rel}:{lineno} -> {target}")

    if broken:
        print(f"check_markdown_links.py: {len(broken)} dangling link(s):")
        for b in broken:
            print(f"  {b}")
        return 1
    print(f"check_markdown_links.py: OK ({checked} in-repo links resolve)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
