from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze_battle_result_distributions import (  # noqa: E402
    build_distributions,
    build_matches,
    build_recovery_clusters,
)


def row(index, message_class, value, scenario="s", command=1, source=2,
        target=3, message_id=30301):
    return {
        "row_index": index,
        "scenario_id": scenario,
        "command_id": command,
        "source_actor_id": source,
        "target_actor_id": target,
        "message_class": message_class,
        "numeric_value": value,
        "world_master_text_id": message_id,
    }


class DistributionTests(unittest.TestCase):
    def test_matched_sets_are_scenario_stratified(self):
        rows = [
            row(0, "normal_damage", 10),
            row(1, "normal_damage", 12),
            row(2, "critical_damage", 20),
            row(3, "critical_damage", 30, scenario="other"),
        ]
        matches = [m for m in build_matches(rows) if m["comparison"] == "critical_vs_normal"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["one_to_one_pair_capacity"], 1)
        self.assertEqual(matches[0]["candidate_pair_count"], 2)
        self.assertEqual(matches[0]["normal_row_indices"], "0;1")
        self.assertEqual(matches[0]["outcome_row_indices"], "2")

    def test_repetition_counts_duplicate_excess(self):
        rows = [row(0, "normal_damage", 10), row(1, "normal_damage", 10),
                row(2, "normal_damage", 12)]
        overall = next(
            item for item in build_distributions(rows)
            if item["dimension"] == "overall" and item["message_class"] == "normal_damage"
        )
        self.assertEqual(overall["unique_value_count"], 2)
        self.assertEqual(overall["duplicate_excess_count"], 1)
        self.assertEqual(overall["value_counts"], "10:2;12:1")

    def test_recovery_clusters_keep_message_identity(self):
        rows = [
            row(0, "hp_recovery", 151, message_id=30320),
            row(1, "hp_recovery", 166, message_id=30320),
            row(2, "hp_recovery", 136, message_id=33008),
        ]
        clusters = build_recovery_clusters(rows)
        self.assertEqual(len(clusters), 2)
        self.assertEqual([cluster["world_master_text_id"] for cluster in clusters], [30320, 33008])
        self.assertEqual([cluster["within_cluster_pair_count"] for cluster in clusters], [1, 0])


if __name__ == "__main__":
    unittest.main()
