#!/usr/bin/env python3
"""Regenerate or verify every generated catalog surface in dependency order."""

from __future__ import annotations

import argparse
import sys

import build_catalog_axes
import build_catalog_index
import build_scenario_views


def _run_phase(phase, check: bool) -> int:
    """Convert a phase's CLI-style exit into a status so later phases still run."""
    try:
        return phase(check=check)
    except SystemExit as exc:
        return int(exc.code or 0)


def run(check: bool = False) -> int:
    """Run scenario views, registry/aliases, then axes without short-circuiting."""
    statuses = [
        _run_phase(build_scenario_views.run, check),
        _run_phase(build_catalog_index.run, check),
        _run_phase(build_catalog_axes.run, check),
    ]
    return 1 if any(statuses) else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate scenario views, the catalog registry, aliases, and axes."
    )
    parser.add_argument(
        "--check", action="store_true",
        help="report stale catalog outputs without writing",
    )
    args = parser.parse_args()
    return run(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
