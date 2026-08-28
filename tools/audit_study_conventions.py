#!/usr/bin/env python3
"""Audit study conventions that are not covered by the catalog validator.

Checks required README headings, manifest/catalog agreement, declared checksum
entry shape and paths, and repository-relative paths. Exact checksum coverage
and digests are owned by build_checksums.py.

Usage:
    python tools/audit_study_conventions.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
STUDIES_DIR = REPO_ROOT / "studies"
CATALOG_PATH = REPO_ROOT / "catalog" / "index.yaml"

README_SECTIONS = [
    "## Study contents",
    "## Start here",
    "## Source material",
    "## Promoted conclusions",
    "## Topics",
    "## Evidence gaps",
    "## Further research",
]

AGREE_FIELDS = [
    "title", "content_kind", "system", "city_state", "grand_company",
    "progression_track", "zones", "tags", "status", "search_hints",
]

PATH_LIST_FIELDS = ["primary_paths", "canonical_evidence", "distilled_artifacts"]


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def check_readme(study_id: str, study_dir: Path, problems: list[str]) -> None:
    readme_path = study_dir / "README.md"
    if not readme_path.exists():
        problems.append(f"{study_id}: missing README.md")
        return
    text = readme_path.read_text(encoding="utf-8")
    for section in README_SECTIONS:
        if section not in text:
            problems.append(f"{study_id}: README.md missing section `{section}`")


def check_field_agreement(
    study_id: str, manifest: dict, catalog_entry: dict | None, problems: list[str]
) -> bool:
    """Return false when the catalog entry is absent."""
    if catalog_entry is None:
        problems.append(f"{study_id}: no catalog/index.yaml entry")
        return False

    for field in AGREE_FIELDS:
        if field not in manifest and field not in catalog_entry:
            continue
        if catalog_entry.get(field) != manifest.get(field):
            problems.append(
                f"{study_id}: field `{field}` disagrees between manifest "
                f"({manifest.get(field)!r}) and catalog ({catalog_entry.get(field)!r})"
            )

    manifest_primary = manifest.get("primary_paths") or []
    expected = [f"studies/{study_id}/{p}" for p in manifest_primary]
    catalog_primary = catalog_entry.get("primary_paths") or []
    if catalog_primary != expected:
        problems.append(
            f"{study_id}: catalog primary_paths {catalog_primary!r} does not match "
            f"manifest-derived {expected!r}"
        )
    return True


def check_checksum_file(study_id: str, study_dir: Path, manifest: dict, problems: list[str]) -> None:
    distilled = manifest.get("distilled")
    if not isinstance(distilled, dict):
        return
    checksum_file = distilled.get("checksum_file")
    if not checksum_file:
        return
    checksum_path = study_dir / checksum_file
    if not checksum_path.exists():
        return

    for line_no, raw_line in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            problems.append(
                f"{study_id}: {checksum_file}:{line_no}: malformed line `{line}`"
            )
            continue
        _digest, rel_path = parts
        if rel_path.startswith("*"):
            rel_path = rel_path[1:]
        target = study_dir / rel_path
        if not target.exists():
            problems.append(
                f"{study_id}: {checksum_file}:{line_no}: target `{rel_path}` does not exist"
            )
            continue


def _collect_path_fields(obj: object) -> list[tuple[str, str]]:
    """Collect path-list values at any depth."""
    found: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in PATH_LIST_FIELDS and isinstance(value, list):
                found.extend((key, item) for item in value if isinstance(item, str))
            else:
                found.extend(_collect_path_fields(value))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_collect_path_fields(item))
    return found


def _bad_path(path_str: str) -> bool:
    if "\\" in path_str:
        return True
    if path_str.startswith("/"):
        return True
    if len(path_str) > 1 and path_str[1] == ":":
        return True
    return False


def check_path_hygiene(scope: str, entry: dict, problems: list[str]) -> None:
    for field, path_str in _collect_path_fields(entry):
        if _bad_path(path_str):
            problems.append(f"{scope}: field `{field}` has non-repo-relative path `{path_str}`")


def audit() -> tuple[int, list[str]]:
    problems: list[str] = []
    catalog = load_yaml(CATALOG_PATH)
    catalog_entries = {entry.get("id"): entry for entry in (catalog.get("studies") or [])}

    check_path_hygiene("catalog", catalog, problems)

    study_dirs = sorted((p for p in STUDIES_DIR.iterdir() if p.is_dir()), key=lambda p: p.name) if STUDIES_DIR.is_dir() else []
    study_count = 0
    for study_dir in study_dirs:
        study_id = study_dir.name
        study_count += 1

        check_readme(study_id, study_dir, problems)

        manifest_path = study_dir / "manifest.yaml"
        manifest = load_yaml(manifest_path)
        check_path_hygiene(f"manifest/{study_id}", manifest, problems)

        catalog_entry = catalog_entries.get(study_id)
        has_catalog = check_field_agreement(study_id, manifest, catalog_entry, problems)
        if not has_catalog:
            continue

        check_checksum_file(study_id, study_dir, manifest, problems)

    return study_count, problems


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit study conventions (README shape, manifest/catalog agreement, "
        "checksum entry shape, path hygiene) not covered by validate_capture_repo.py."
    )
    args = parser.parse_args()

    # Titles/search_hints may contain Japanese; UTF-8 output avoids cp1252 console aborts.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    study_count, problems = audit()

    if problems:
        for problem in problems:
            print(f"PROBLEM: {problem}")
        print(f"{len(problems)} problem(s) across {study_count} study(ies).")
        return 1

    print(f"All clean: {study_count} study(ies) audited, no convention problems.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
