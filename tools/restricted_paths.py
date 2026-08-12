"""Paths that exist only when the restricted corpus is present.

The corpus and the archives are never tracked, so a checkout without them
is missing files that the catalog, the validator, and the link checker
must treat as legitimately absent rather than as defects.
"""

from __future__ import annotations

from pathlib import Path


EXCLUDED_DERIVED_IDS = frozenset({"gam_name_candidates"})


def is_present_without_corpus(relative_path: str | Path) -> bool:
    """Return whether a path is expected to exist with no corpus present."""
    parts = Path(relative_path).as_posix().split("/")
    if not parts:
        return True

    if parts[0] == "archives":
        return False

    if parts[0] == "sources" and len(parts) >= 2:
        if len(parts) >= 3 and parts[2] == "objects":
            return False

    if parts[0] == "derived" and len(parts) == 2:
        name = parts[1]
        for dataset_id in EXCLUDED_DERIVED_IDS:
            if name in {f"{dataset_id}.json", f"{dataset_id}.meta.yaml"}:
                return False

    return True
