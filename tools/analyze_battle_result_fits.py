#!/usr/bin/env python3
"""Build Stage 3 descriptive fits from strict battle-result matched sets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STUDY_DIR = REPO_ROOT / "studies" / "battle-result-backfit"
DEFAULT_ROWS = STUDY_DIR / "derived" / "battle-result-rows.csv"
DEFAULT_MATCHES = STUDY_DIR / "derived" / "matched-comparison-sets.csv"
DEFAULT_ACCOUNTING = STUDY_DIR / "derived" / "accounting.json"
DEFAULT_OUT = STUDY_DIR / "derived"

FIT_FIELDS = (
    "comparison", "scenario_id", "command_id", "source_actor_id",
    "target_actor_id", "normal_count", "outcome_count",
    "positive_outcome_count", "excluded_zero_outcome_count", "normal_mean",
    "outcome_mean", "outcome_to_normal_ratio", "normal_values",
    "outcome_values", "normal_row_indices", "outcome_row_indices",
    "normal_csv_lines", "outcome_csv_lines",
)
RECOVERY_FIELDS = (
    "identity", "command_id", "world_master_text_id", "base_magnitude",
    "observed_value", "observed_to_base_ratio", "scenario_id",
    "source_actor_id", "target_actor_id", "row_index", "source_csv_line",
)
RATIO_COMPARISONS = {
    "critical_vs_normal": False,
    "block_vs_normal": True,
    "parry_vs_normal": True,
}
CURE_COMMAND_ID = 27346
CURE_MESSAGE_ID = 30320
AEGIS_MESSAGE_ID = 33008
CURE_BASE_MAGNITUDE = 1000
CURE_INPUT_SHA256 = "9a81350dbd88d61c90a715f1859a1899d3d86c77c6bb52994371b69e1094a444"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_ints(value: str) -> list[int]:
    return [int(item) for item in value.split(";") if item]


def fmt(value: Decimal | None) -> str:
    if value is None:
        return ""
    return format(value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP), "f")


def mean(values: list[int]) -> Decimal:
    return Decimal(sum(values)) / Decimal(len(values))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="ascii", newline="") as handle:
        return list(csv.DictReader(handle))


def build_ratio_rows(matches: list[dict[str, str]]) -> list[dict[str, object]]:
    output = []
    for row in matches:
        comparison = row["comparison"]
        if comparison not in RATIO_COMPARISONS:
            continue
        normals = split_ints(row["normal_values"])
        outcomes = split_ints(row["outcome_values"])
        selected = [value for value in outcomes if value > 0] if RATIO_COMPARISONS[comparison] else outcomes
        normal_mean = mean(normals)
        outcome_mean = mean(selected) if selected else None
        ratio = outcome_mean / normal_mean if outcome_mean is not None else None
        output.append({
            "comparison": comparison,
            "scenario_id": row["scenario_id"],
            "command_id": row["command_id"],
            "source_actor_id": row["source_actor_id"],
            "target_actor_id": row["target_actor_id"],
            "normal_count": len(normals),
            "outcome_count": len(outcomes),
            "positive_outcome_count": len(selected),
            "excluded_zero_outcome_count": len(outcomes) - len(selected),
            "normal_mean": fmt(normal_mean),
            "outcome_mean": fmt(outcome_mean),
            "outcome_to_normal_ratio": fmt(ratio),
            "normal_values": row["normal_values"],
            "outcome_values": row["outcome_values"],
            "normal_row_indices": row["normal_row_indices"],
            "outcome_row_indices": row["outcome_row_indices"],
            "normal_csv_lines": row["normal_csv_lines"],
            "outcome_csv_lines": row["outcome_csv_lines"],
        })
    return output


def build_recovery_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output = []
    for row in rows:
        command = int(row["command_id"])
        message = int(row["world_master_text_id"])
        if row["message_class"] != "hp_recovery":
            continue
        if command == CURE_COMMAND_ID and message == CURE_MESSAGE_ID:
            identity = "cure"
            base: int | str = CURE_BASE_MAGNITUDE
            ratio = fmt(Decimal(int(row["numeric_value"])) / Decimal(CURE_BASE_MAGNITUDE))
        elif message == AEGIS_MESSAGE_ID:
            identity = "aegis_boon"
            base = ""
            ratio = ""
        else:
            continue
        output.append({
            "identity": identity,
            "command_id": command,
            "world_master_text_id": message,
            "base_magnitude": base,
            "observed_value": int(row["numeric_value"]),
            "observed_to_base_ratio": ratio,
            "scenario_id": row["scenario_id"],
            "source_actor_id": int(row["source_actor_id"]),
            "target_actor_id": int(row["target_actor_id"]),
            "row_index": int(row["row_index"]),
            "source_csv_line": int(row["row_index"]) + 2,
        })
    return output


def render_csv(rows: list[dict[str, object]], fields: tuple[str, ...]) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("ascii")


def aggregate_ratio(rows: list[dict[str, object]], comparison: str) -> dict[str, object]:
    selected = [row for row in rows if row["comparison"] == comparison]
    usable = [row for row in selected if row["outcome_to_normal_ratio"]]
    normal_values = [
        value for row in usable for value in split_ints(str(row["normal_values"]))
    ]
    outcome_values = [
        value for row in usable for value in split_ints(str(row["outcome_values"])) if value > 0
    ]
    ratios = [Decimal(str(row["outcome_to_normal_ratio"])) for row in usable]
    aggregate = mean(outcome_values) / mean(normal_values) if outcome_values else None
    return {
        "matched_sets": len(selected),
        "ratio_eligible_sets": len(usable),
        "normal_rows_in_ratio": len(normal_values),
        "outcome_rows_in_ratio": len(outcome_values),
        "excluded_zero_outcome_rows": sum(int(row["excluded_zero_outcome_count"]) for row in selected),
        "aggregate_mean_ratio": fmt(aggregate),
        "per_set_ratio_min": fmt(min(ratios) if ratios else None),
        "per_set_ratio_max": fmt(max(ratios) if ratios else None),
    }


def build_outputs(rows_path: Path, matches_path: Path, accounting_path: Path) -> dict[str, bytes]:
    rows = load_csv(rows_path)
    matches = load_csv(matches_path)
    if len(rows) != 622:
        raise ValueError(f"expected 622 Stage 1 rows, found {len(rows)}")
    accounting = json.loads(accounting_path.read_text(encoding="ascii"))
    command_input = accounting["inputs"]["command_battle_params"]
    if command_input["sha256"] != CURE_INPUT_SHA256:
        raise ValueError("Stage 1 command_battle_params SHA-256 changed")
    ratio_rows = build_ratio_rows(matches)
    recovery_rows = build_recovery_rows(rows)
    miss_sets = [row for row in matches if row["comparison"] == "miss_vs_normal"]
    miss_normal = sum(int(row["normal_count"]) for row in miss_sets)
    miss_outcome = sum(int(row["outcome_count"]) for row in miss_sets)
    cure_rows = [row for row in recovery_rows if row["identity"] == "cure"]
    aegis_rows = [row for row in recovery_rows if row["identity"] == "aegis_boon"]
    if len(cure_rows) != 3 or len(aegis_rows) != 4:
        raise ValueError("Cure or Aegis recovery identity counts changed")
    fit_accounting = {
        "schema_version": 1,
        "inputs": {
            "battle_result_rows": {"path": str(rows_path.relative_to(REPO_ROOT)).replace("\\", "/"), "sha256": sha256_file(rows_path)},
            "matched_comparison_sets": {"path": str(matches_path.relative_to(REPO_ROOT)).replace("\\", "/"), "sha256": sha256_file(matches_path)},
            "command_battle_params": {
                "path": command_input["path"],
                "sha256": command_input["sha256"],
                "validated_row": "27346,Cure",
                "base_magnitude": CURE_BASE_MAGNITUDE,
                "source_csv_line": 1101,
            },
        },
        "ratio_contract": "Ratios compare set-level arithmetic means inside the strict Stage 2 key; they are descriptive packet observations, not fitted coefficients or temporal pairs.",
        "critical": aggregate_ratio(ratio_rows, "critical_vs_normal"),
        "block": aggregate_ratio(ratio_rows, "block_vs_normal"),
        "parry": aggregate_ratio(ratio_rows, "parry_vs_normal"),
        "miss": {
            "matched_sets": len(miss_sets),
            "normal_rows": miss_normal,
            "miss_rows": miss_outcome,
            "descriptive_fraction": fmt(Decimal(miss_outcome) / Decimal(miss_normal + miss_outcome)),
        },
        "cure": {
            "hp_recovery_rows": len(cure_rows),
            "observed_values": sorted(int(row["observed_value"]) for row in cure_rows),
            "base_magnitude": CURE_BASE_MAGNITUDE,
            "stat_controlled_pairs": 0,
        },
        "aegis_boon": {
            "hp_recovery_rows": len(aegis_rows),
            "observed_values": sorted(int(row["observed_value"]) for row in aegis_rows),
            "stat_controlled_pairs": 0,
        },
        "def_vit": {
            "source_rows": len(rows),
            "rows_with_actor_stat_join": 0,
            "stat_controlled_pairs": 0,
        },
        "uncontrolled_corpus": ["gear", "buffs", "level and dLVL", "scenario mixing"],
    }
    return {
        "matched-set-ratios.csv": render_csv(ratio_rows, FIT_FIELDS),
        "recovery-model-observations.csv": render_csv(recovery_rows, RECOVERY_FIELDS),
        "model-fit-accounting.json": (json.dumps(fit_accounting, indent=2, sort_keys=True) + "\n").encode("ascii"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--matches", type=Path, default=DEFAULT_MATCHES)
    parser.add_argument("--accounting", type=Path, default=DEFAULT_ACCOUNTING)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs(args.rows.resolve(), args.matches.resolve(), args.accounting.resolve())
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
        print("stale battle-result fit outputs:")
        for path in stale:
            print(f"  {path}")
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {len(outputs)} battle-result fit artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
