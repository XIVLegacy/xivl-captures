from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze_battle_result_fits import (  # noqa: E402
    aggregate_ratio,
    build_ratio_rows,
    build_recovery_rows,
)


def match(comparison, normals, outcomes):
    return {
        "comparison": comparison,
        "scenario_id": "s",
        "command_id": "1",
        "source_actor_id": "2",
        "target_actor_id": "3",
        "normal_values": ";".join(str(value) for value in normals),
        "outcome_values": ";".join(str(value) for value in outcomes),
        "normal_row_indices": "0",
        "outcome_row_indices": "1",
        "normal_csv_lines": "2",
        "outcome_csv_lines": "3",
    }


def row(index, command, message, value):
    return {
        "row_index": str(index),
        "scenario_id": "s",
        "command_id": str(command),
        "source_actor_id": "2",
        "target_actor_id": "3",
        "world_master_text_id": str(message),
        "message_class": "hp_recovery",
        "numeric_value": str(value),
    }


class FitTests(unittest.TestCase):
    def test_block_ratio_excludes_zero_outcomes(self):
        fits = build_ratio_rows([match("block_vs_normal", [50, 70], [0, 30])])
        self.assertEqual(fits[0]["positive_outcome_count"], 1)
        self.assertEqual(fits[0]["excluded_zero_outcome_count"], 1)
        self.assertEqual(fits[0]["outcome_to_normal_ratio"], "0.500000")

    def test_aggregate_uses_contributing_rows(self):
        fits = build_ratio_rows([
            match("critical_vs_normal", [10], [20]),
            match("critical_vs_normal", [20, 30], [40]),
        ])
        summary = aggregate_ratio(fits, "critical_vs_normal")
        self.assertEqual(summary["normal_rows_in_ratio"], 3)
        self.assertEqual(summary["outcome_rows_in_ratio"], 2)
        self.assertEqual(summary["aggregate_mean_ratio"], "1.500000")

    def test_recovery_identity_controls_base_ratio(self):
        observations = build_recovery_rows([
            row(0, 27346, 30320, 151),
            row(1, 23003, 33008, 136),
        ])
        self.assertEqual(observations[0]["observed_to_base_ratio"], "0.151000")
        self.assertEqual(observations[1]["base_magnitude"], "")
        self.assertEqual(observations[1]["observed_to_base_ratio"], "")


if __name__ == "__main__":
    unittest.main()
