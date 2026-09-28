import unittest

from tools.extractors import extract_monster_actor_class_paths as paths


def target(actor_id, catalog_path=""):
    return {
        "pool_id": actor_id,
        "pool_name": f"pool_{actor_id}",
        "source": "test",
        "actor_class_id": actor_id,
        "display_name_id": actor_id + 1000000,
        "base_model_id": 7,
        "decoded_graphic_pair_row_count": 1,
        "population_catalog_path": catalog_path,
        "population_configured_path": "",
    }


class MonsterActorClassPathTest(unittest.TestCase):
    def test_mapping_verdicts_separate_catalog_and_instance_evidence(self):
        targets = [
            target(1, "/catalog"),
            target(2, "/catalog"),
            target(3),
            target(4, "/catalog"),
            target(5, "/Chara/Npc/Monster/Match/MatchStandard"),
            target(6),
        ]
        occurrences = [
            {
                "actor_class_id": 1,
                "decoded_graphic_pair_row_count": 1,
                "observed_instance_class_path": "/Chara/Npc/Monster/New/NewStandard",
            },
            {
                "actor_class_id": 4,
                "decoded_graphic_pair_row_count": 1,
                "observed_instance_class_path": "/Chara/Npc/Monster/One/OneStandard",
            },
            {
                "actor_class_id": 4,
                "decoded_graphic_pair_row_count": 1,
                "observed_instance_class_path": "/Chara/Npc/Monster/Two/TwoStandard",
            },
            {
                "actor_class_id": 5,
                "decoded_graphic_pair_row_count": 1,
                "observed_instance_class_path": "/Chara/Npc/Monster/Match/MatchStandard",
            },
            {
                "actor_class_id": 6,
                "decoded_graphic_pair_row_count": 1,
                "observed_instance_class_path": "/Chara/Npc/Monster/Only/OnlyStandard",
            },
        ]
        mappings = paths._build_mappings(targets, occurrences)
        self.assertEqual(
            [row["verdict"] for row in mappings],
            [
                "population_catalog_instance_path_mismatch",
                "population_catalog_no_instance_observation",
                "unresolved",
                "population_catalog_multiple_instance_paths",
                "population_catalog_instance_path_match",
                "observed_instance_path_only",
            ],
        )
        self.assertEqual(mappings[0]["population_catalog_path"], "/catalog")
        self.assertEqual(
            mappings[0]["retained_instance_class_paths"],
            "/Chara/Npc/Monster/New/NewStandard",
        )
        self.assertEqual(mappings[0]["retained_lifetime_count"], 1)

    def test_shared_identity_pair_cannot_promote(self):
        shared = target(4)
        shared["decoded_graphic_pair_row_count"] = 2
        occurrences = [
            {
                "actor_class_id": 4,
                "decoded_graphic_pair_row_count": 2,
                "observed_instance_class_path": "/Chara/Npc/Monster/Maybe/MaybeStandard",
            }
        ]
        mapping = paths._build_mappings([shared], occurrences)[0]
        self.assertEqual(mapping["verdict"], "unresolved")
        self.assertEqual(mapping["retained_lifetime_count"], 0)


if __name__ == "__main__":
    unittest.main()
