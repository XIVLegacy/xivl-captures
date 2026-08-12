#!/usr/bin/env python3
"""Regenerate the catalog/by-*.md axis views from catalog/index.yaml.

Each view groups studies and scenarios by one taxonomy field. Values and ids
are sorted. `zones` is list-valued, and missing fields are omitted.

Usage:
    python tools/build_catalog_axes.py            # rewrite the axis files
    python tools/build_catalog_axes.py --check    # diff-only, exit 1 if stale
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG = REPO_ROOT / "catalog"

# filename, title, field, list-valued, rendered note
AXES = [
    ("by-content-kind.md", "Content Kind", "content_kind", False,
     "Generated from `catalog/index.yaml`. Primary axis: `content_kind`."),
    ("by-zone.md", "Zone", "zones", True,
     "Generated from `catalog/index.yaml`. Axis: `zones`."),
    ("by-system.md", "System", "system", False,
     "Generated from `catalog/index.yaml`. Axis: `system` (cross-cutting 1.x systems\n"
     "such as guildleve, behest, battle-regimen, grand-company)."),
    ("by-progression.md", "Progression", "progression_track", False,
     "Generated from `catalog/index.yaml`. Axis: `progression_track` (class quest, job\n"
     "quest, grand-company rank)."),
    ("by-city-state.md", "City-State", "city_state", False,
     "Generated from `catalog/index.yaml`. Axis: `city_state` (Limsa Lominsa,\n"
     "Gridania, Ul'dah)."),
]


def load_index() -> dict:
    return yaml.safe_load((CATALOG / "index.yaml").read_text(encoding="utf-8")) or {}


def _values(entry: dict, field: str, is_list: bool) -> list[str]:
    raw = entry.get(field)
    if is_list:
        return [v for v in (raw or []) if isinstance(v, str) and v.strip()]
    if isinstance(raw, str) and raw.strip():
        return [raw]
    return []


def _group(entries: list[dict], field: str, is_list: bool) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for entry in entries:
        entry_id = entry.get("id", "")
        for value in _values(entry, field, is_list):
            groups.setdefault(value, []).append(entry_id)
    return groups


def render(title: str, field: str, is_list: bool, note: str,
           studies: list[dict], scenarios: list[dict]) -> str:
    study_groups = _group(studies, field, is_list)
    scenario_groups = _group(scenarios, field, is_list)
    values = sorted(set(study_groups) | set(scenario_groups))

    out = [f"# Captures By {title}", "", note, ""]
    if not values:
        out += [f"No captures carry a `{field}` yet.", ""]
        return "\n".join(out)
    for value in values:
        study_ids = sorted(study_groups.get(value, []))
        scenario_ids = sorted(scenario_groups.get(value, []))
        out += [f"## {value} ({len(study_ids) + len(scenario_ids)})", ""]
        if study_ids:
            out += [f"### Studies ({len(study_ids)})", ""]
            out += [f"- `{sid}`" for sid in study_ids]
            out.append("")
        if scenario_ids:
            out += [f"### Scenarios ({len(scenario_ids)})", ""]
            out += [f"- `{sid}`" for sid in scenario_ids]
            out.append("")
    return "\n".join(out)


def build_all(index: dict) -> dict[str, str]:
    studies = index.get("studies") or []
    scenarios = index.get("scenarios") or []
    return {
        filename: render(title, field, is_list, note, studies, scenarios)
        for filename, title, field, is_list, note in AXES
    }


def run(check: bool = False) -> int:
    rendered = build_all(load_index())
    stale: list[str] = []
    for filename, text in rendered.items():
        path = CATALOG / filename
        current = path.read_bytes() if path.exists() else None
        if current != text.encode("utf-8"):
            stale.append(filename)
            if not check:
                path.write_text(text, encoding="utf-8", newline="\n")

    if check:
        if stale:
            print("STALE: " + ", ".join(sorted(stale)))
            return 1
        print("All axis files are up to date.")
        return 0

    print(("Rewrote: " + ", ".join(sorted(stale))) if stale else "No changes; all axis files already current.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate catalog/by-*.md from index.yaml.")
    parser.add_argument("--check", action="store_true",
                        help="report whether any file is stale; do not write (exit 1 if stale)")
    args = parser.parse_args()
    return run(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
