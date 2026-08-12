"""Shared JSON writer and repository paths.

Generated JSON uses two-space indentation, literal UTF-8, LF endings, and one
trailing newline so regeneration stays byte-stable across platforms.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "derived"
OBJECTS_DIR = REPO_ROOT / "sources" / "pcap-1.23b" / "objects"


def write_json(path, obj) -> None:
    """Write indent-2 UTF-8 JSON with LF and one trailing newline."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")
