#!/usr/bin/env python3
"""Generate or verify every canonical pcap-derived JSON product in one process."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
EXTRACTORS_DIR = TOOLS_DIR / "extractors"
REPO_ROOT = TOOLS_DIR.parent
DATA_DIR = REPO_ROOT / "derived"

sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(EXTRACTORS_DIR))

import analyze_payload_layouts  # noqa: E402
import extract_content_samples  # noqa: E402
import extract_gam_keys  # noqa: E402
import extract_observations  # noqa: E402
import extract_payload_samples  # noqa: E402
import extract_property_targets  # noqa: E402
import extract_request_response_pairs  # noqa: E402
import extract_sequences  # noqa: E402
import extract_spawn_observations  # noqa: E402
import extract_streams  # noqa: E402
import extract_timing  # noqa: E402
import name_gam_hashes  # noqa: E402

PIPELINE_VERSION = "1"
EXPECTED_CORPUS_SIZE = 54

PRODUCTS = (
    "observations",
    "lane_observations",
    "sequences",
    "timing",
    "payload_samples",
    "content_samples",
    "property_targets",
    "request_response_pairs",
    "gam_keys",
    "spawn_observations",
    "gam_hash_names",
    "payload_layouts",
)

DEPENDENCIES = {
    "gam_hash_names": {"gam_keys"},
    "payload_layouts": {"payload_samples"},
}

GROUPS = (
    ("observations", {"observations", "lane_observations"}),
    ("sequences", {"sequences"}),
    ("timing", {"timing"}),
    ("payload_samples", {"payload_samples"}),
    ("content_samples", {"content_samples"}),
    ("property_targets", {"property_targets"}),
    ("request_response_pairs", {"request_response_pairs"}),
    ("gam_keys", {"gam_keys"}),
    ("spawn_observations", {"spawn_observations"}),
    ("gam_hash_names", {"gam_hash_names"}),
    ("payload_layouts", {"payload_layouts"}),
)

LAST_READ_COUNTS: dict[Path, int] = {}


def _invoke_main(main, argv: list[str]) -> int:
    previous = sys.argv
    sys.argv = [getattr(main, "__module__", "generator"), *argv]
    try:
        try:
            return int(main() or 0)
        except SystemExit as exc:
            return int(exc.code or 0)
    finally:
        sys.argv = previous


def _dependency_closure(selected: set[str]) -> set[str]:
    needed = set(selected)
    pending = list(selected)
    while pending:
        product = pending.pop()
        for dependency in DEPENDENCIES.get(product, set()):
            if dependency not in needed:
                needed.add(dependency)
                pending.append(dependency)
    return needed


def _run_group(group: str, stage: Path) -> int:
    out = lambda name: str(stage / f"{name}.json")
    commands = {
        "observations": (
            extract_observations.main,
            ["--out", out("observations"), "--lane-out", out("lane_observations")],
        ),
        "sequences": (extract_sequences.main, ["--out", out(group)]),
        "timing": (extract_timing.main, ["--out", out(group)]),
        "payload_samples": (extract_payload_samples.main, ["--out", out(group)]),
        "content_samples": (extract_content_samples.main, ["--out", out(group)]),
        "property_targets": (extract_property_targets.main, ["--out", out(group)]),
        "request_response_pairs": (extract_request_response_pairs.main, ["--out", out(group)]),
        "gam_keys": (extract_gam_keys.main, ["--out", out(group)]),
        "spawn_observations": (extract_spawn_observations.main, ["--out", out(group)]),
        "gam_hash_names": (
            name_gam_hashes.main,
            ["--in", out("gam_keys"), "--out", out(group)],
        ),
        "payload_layouts": (
            analyze_payload_layouts.main,
            ["--in", out("payload_samples"), "--out", out(group)],
        ),
    }
    main, argv = commands[group]
    return _invoke_main(main, argv)


def _validate_reads() -> list[str]:
    expected = {path.resolve() for path in extract_observations.default_corpus_paths()}
    counts = extract_streams.packet_read_counts()
    errors = []
    if set(counts) != expected:
        missing = sorted(path.name for path in expected - set(counts))
        extra = sorted(path.name for path in set(counts) - expected)
        if missing:
            errors.append("pcaps not read: " + ", ".join(missing))
        if extra:
            errors.append("unexpected pcaps read: " + ", ".join(extra))
    repeated = sorted(path.name for path, count in counts.items() if count != 1)
    if repeated:
        errors.append("pcaps not read exactly once: " + ", ".join(repeated))
    if len(expected) != EXPECTED_CORPUS_SIZE:
        errors.append(
            f"expected corpus selection has {len(expected)} pcaps, "
            f"expected {EXPECTED_CORPUS_SIZE}"
        )
    return errors


def _public_check(selected: set[str], output_dir: Path) -> int:
    errors = []
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        for product in selected:
            target = output_dir / f"{product}.json"
            if not target.is_file():
                errors.append(f"missing retained product: {target}")
                continue
            try:
                json.loads(target.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                errors.append(f"invalid retained product {target}: {exc}")

        for group in ("gam_hash_names", "payload_layouts"):
            if group not in selected:
                continue
            if group == "gam_hash_names":
                status = _invoke_main(
                    name_gam_hashes.main,
                    [
                        "--in", str(output_dir / "gam_keys.json"),
                        "--out", str(stage / "gam_hash_names.json"),
                    ],
                )
            else:
                status = _invoke_main(
                    analyze_payload_layouts.main,
                    [
                        "--in", str(output_dir / "payload_samples.json"),
                        "--out", str(stage / "payload_layouts.json"),
                    ],
                )
            if status:
                errors.append(f"{group} public-shape reducer failed with status {status}")
                continue
            if (stage / f"{group}.json").read_bytes() != (
                output_dir / f"{group}.json"
            ).read_bytes():
                errors.append(f"derived/{group}.json regenerated bytes differ")

    print("pcap reads: 0 unique, 0 total (public shape)")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


def execute(
    selected: set[str],
    *,
    check: bool,
    output_dir: Path,
) -> int:
    """Generate selected products."""
    global LAST_READ_COUNTS

    corpus_paths = extract_observations.default_corpus_paths()
    if not corpus_paths:
        if not check:
            print("ERROR: corpus is absent; write mode is unavailable", file=sys.stderr)
            return 2
        return _public_check(selected, output_dir)

    needed = _dependency_closure(selected)
    extract_streams.reset_packet_cache()
    errors = []
    try:
        with tempfile.TemporaryDirectory() as tmp:
            stage = Path(tmp)
            for group, outputs in GROUPS:
                if not outputs & needed:
                    continue
                try:
                    status = int(_run_group(group, stage))
                except Exception as exc:  # Atomic publication requires reducer isolation.
                    errors.append(f"{group} reducer raised: {exc}")
                    break
                if status:
                    errors.append(f"{group} reducer failed with status {status}")
                    break

            LAST_READ_COUNTS = extract_streams.packet_read_counts()
            errors.extend(_validate_reads())

            for product in selected:
                staged = stage / f"{product}.json"
                if not staged.is_file():
                    errors.append(f"{product} reducer produced no staged output")

            if not errors and check:
                for product in selected:
                    staged = stage / f"{product}.json"
                    committed = output_dir / f"{product}.json"
                    if not committed.is_file():
                        errors.append(f"committed product missing: {committed}")
                    elif staged.read_bytes() != committed.read_bytes():
                        errors.append(f"derived/{product}.json regenerated bytes differ")

            if not errors and not check:
                output_dir.mkdir(parents=True, exist_ok=True)
                publish: list[tuple[Path, Path]] = []
                for product in selected:
                    staged = stage / f"{product}.json"
                    target = output_dir / f"{product}.json"
                    pending = output_dir / f".{product}.json.pending"
                    shutil.copyfile(staged, pending)
                    publish.append((pending, target))
                for pending, target in publish:
                    os.replace(pending, target)
    finally:
        LAST_READ_COUNTS = extract_streams.packet_read_counts()
        extract_streams.clear_packet_cache()

    total_reads = sum(LAST_READ_COUNTS.values())
    print(f"pcap reads: {len(LAST_READ_COUNTS)} unique, {total_reads} total")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true",
        help="regenerate to temporary files and byte-compare without writing",
    )
    parser.add_argument(
        "--product", action="append", choices=PRODUCTS,
        help="select one product; repeat for more (default: all products)",
    )
    args = parser.parse_args()
    selected = set(args.product or PRODUCTS)
    return execute(selected, check=args.check, output_dir=DATA_DIR)


if __name__ == "__main__":
    sys.exit(main())
