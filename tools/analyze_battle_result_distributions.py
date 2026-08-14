#!/usr/bin/env python3
"""Build Stage 2 distributions and outcome-matched comparison sets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STUDY_DIR = REPO_ROOT / "studies" / "battle-result-backfit"
DEFAULT_ROWS = STUDY_DIR / "derived" / "battle-result-rows.csv"
DEFAULT_OUT = STUDY_DIR / "derived"

INT_FIELDS = {
    "row_index", "command_id", "source_actor_id", "target_actor_id",
    "numeric_value", "world_master_text_id",
}
DIMENSIONS = (
    ("overall", lambda row: "all"),
    ("scenario", lambda row: row["scenario_id"]),
    ("command", lambda row: str(row["command_id"])),
    ("source_actor", lambda row: str(row["source_actor_id"])),
    ("target_actor", lambda row: str(row["target_actor_id"])),
)
COMPARISONS = (
    ("critical_vs_normal", "critical_damage"),
    ("block_vs_normal", "block_damage"),
    ("parry_vs_normal", "parry_damage"),
    ("miss_vs_normal", "miss"),
)

DISTRIBUTION_FIELDS = (
    "dimension", "key", "message_class", "row_count", "min_value",
    "max_value", "unique_value_count", "duplicate_excess_count",
    "value_counts", "source_row_indices", "source_csv_lines",
)
MATCH_FIELDS = (
    "comparison", "scenario_id", "command_id", "source_actor_id",
    "target_actor_id", "normal_count", "outcome_count",
    "one_to_one_pair_capacity", "candidate_pair_count", "normal_values", "outcome_values",
    "normal_row_indices", "outcome_row_indices", "normal_csv_lines",
    "outcome_csv_lines",
)
RECOVERY_FIELDS = (
    "scenario_id", "command_id", "source_actor_id", "target_actor_id",
    "world_master_text_id", "row_count", "min_value", "max_value",
    "unique_value_count", "duplicate_excess_count", "value_counts",
    "within_cluster_pair_count",
    "source_row_indices", "source_csv_lines",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="ascii", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for field in INT_FIELDS:
            row[field] = int(row[field])
    expected = list(range(len(rows)))
    observed = [row["row_index"] for row in rows]
    if observed != expected:
        raise ValueError("row_index is not contiguous from zero")
    return rows


def compact_counts(values: list[int]) -> str:
    return ";".join(f"{value}:{count}" for value, count in sorted(Counter(values).items()))


def compact_values(rows: list[dict]) -> str:
    return ";".join(str(row["numeric_value"]) for row in sorted(rows, key=lambda r: r["row_index"]))


def compact_rows(rows: list[dict], csv_lines: bool = False) -> str:
    offset = 2 if csv_lines else 0
    return ";".join(str(row["row_index"] + offset) for row in sorted(rows, key=lambda r: r["row_index"]))


def value_summary(rows: list[dict]) -> dict:
    values = [row["numeric_value"] for row in rows]
    counts = Counter(values)
    return {
        "row_count": len(rows),
        "min_value": min(values),
        "max_value": max(values),
        "unique_value_count": len(counts),
        "duplicate_excess_count": sum(count - 1 for count in counts.values()),
        "value_counts": compact_counts(values),
        "source_row_indices": compact_rows(rows),
        "source_csv_lines": compact_rows(rows, csv_lines=True),
    }


def build_distributions(rows: list[dict]) -> list[dict]:
    output: list[dict] = []
    for dimension, key_fn in DIMENSIONS:
        groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for row in rows:
            groups[(key_fn(row), row["message_class"])].append(row)
        for (key, message_class), group in sorted(groups.items()):
            output.append({
                "dimension": dimension,
                "key": key,
                "message_class": message_class,
                **value_summary(group),
            })
    return output


def identity_key(row: dict) -> tuple[str, int, int, int]:
    return (
        row["scenario_id"], row["command_id"],
        row["source_actor_id"], row["target_actor_id"],
    )


def build_matches(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, int, int, int], list[dict]] = defaultdict(list)
    for row in rows:
        groups[identity_key(row)].append(row)
    output: list[dict] = []
    for comparison, outcome_class in COMPARISONS:
        for key, group in sorted(groups.items()):
            normal = [row for row in group if row["message_class"] == "normal_damage"]
            outcome = [row for row in group if row["message_class"] == outcome_class]
            if not normal or not outcome:
                continue
            scenario, command, source, target = key
            output.append({
                "comparison": comparison,
                "scenario_id": scenario,
                "command_id": command,
                "source_actor_id": source,
                "target_actor_id": target,
                "normal_count": len(normal),
                "outcome_count": len(outcome),
                "one_to_one_pair_capacity": min(len(normal), len(outcome)),
                "candidate_pair_count": len(normal) * len(outcome),
                "normal_values": compact_values(normal),
                "outcome_values": compact_values(outcome),
                "normal_row_indices": compact_rows(normal),
                "outcome_row_indices": compact_rows(outcome),
                "normal_csv_lines": compact_rows(normal, csv_lines=True),
                "outcome_csv_lines": compact_rows(outcome, csv_lines=True),
            })
    return output


def build_recovery_clusters(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, int, int, int, int], list[dict]] = defaultdict(list)
    for row in rows:
        if row["message_class"] != "hp_recovery":
            continue
        key = identity_key(row) + (row["world_master_text_id"],)
        groups[key].append(row)
    output: list[dict] = []
    for key, group in sorted(groups.items()):
        scenario, command, source, target, message_id = key
        output.append({
            "scenario_id": scenario,
            "command_id": command,
            "source_actor_id": source,
            "target_actor_id": target,
            "world_master_text_id": message_id,
            **value_summary(group),
            "within_cluster_pair_count": len(group) * (len(group) - 1) // 2,
        })
    return output


def render_csv(rows: list[dict], fields: tuple[str, ...]) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("ascii")


def build_accounting(source: Path, rows: list[dict], distributions: list[dict],
                     matches: list[dict], recoveries: list[dict]) -> dict:
    class_counts = Counter(row["message_class"] for row in rows)
    match_accounting = {}
    for comparison, outcome_class in COMPARISONS:
        selected = [row for row in matches if row["comparison"] == comparison]
        matched_outcome_rows = sum(row["outcome_count"] for row in selected)
        match_accounting[comparison] = {
            "available_outcome_rows": class_counts[outcome_class],
            "matched_sets": len(selected),
            "matched_outcome_rows": matched_outcome_rows,
            "unmatched_outcome_rows": class_counts[outcome_class] - matched_outcome_rows,
            "matched_normal_rows": sum(row["normal_count"] for row in selected),
            "one_to_one_pair_capacity": sum(
                row["one_to_one_pair_capacity"] for row in selected),
            "candidate_pair_count": sum(row["candidate_pair_count"] for row in selected),
        }
    return {
        "schema_version": 1,
        "input": {
            "path": "studies/battle-result-backfit/derived/battle-result-rows.csv",
            "sha256": sha256_file(source),
            "row_count": len(rows),
        },
        "matching_contract": {
            "key": ["scenario_id", "command_id", "source_actor_id", "target_actor_id"],
            "baseline": "normal_damage",
            "candidate_pair_count": "Cartesian normal/outcome row combinations within a matched set; not temporal pairs.",
            "effect_fields": "Retained as observations and excluded from matching because their semantics remain unresolved.",
        },
        "class_counts": dict(sorted(class_counts.items())),
        "dimension_row_counts": dict(sorted(Counter(row["dimension"] for row in distributions).items())),
        "matched_comparisons": match_accounting,
        "recovery_cluster_count": len(recoveries),
        "recovery_within_cluster_pair_count": sum(
            row["within_cluster_pair_count"] for row in recoveries
        ),
    }


def build_outputs(source: Path) -> dict[str, bytes]:
    rows = load_rows(source)
    distributions = build_distributions(rows)
    matches = build_matches(rows)
    recoveries = build_recovery_clusters(rows)
    accounting = build_accounting(source, rows, distributions, matches, recoveries)
    if len(rows) != 622:
        raise ValueError(f"expected 622 Stage 1 rows, found {len(rows)}")
    return {
        "distribution-summary.csv": render_csv(distributions, DISTRIBUTION_FIELDS),
        "matched-comparison-sets.csv": render_csv(matches, MATCH_FIELDS),
        "hp-recovery-clusters.csv": render_csv(recoveries, RECOVERY_FIELDS),
        "distribution-accounting.json": (
            json.dumps(accounting, indent=2, sort_keys=True) + "\n"
        ).encode("ascii"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs(args.rows.resolve())
    stale = []
    for name, content in outputs.items():
        target = args.out_dir / name
        if args.check:
            if not target.is_file() or target.read_bytes() != content:
                stale.append(str(target))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    if stale:
        print("stale battle-result distribution outputs:")
        for path in stale:
            print(f"  {path}")
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {len(outputs)} battle-result distribution artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
