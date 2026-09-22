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
        "identity_pair_catalog_count": 1,
        "catalog_class_path": catalog_path,
        "configured_class_path": "",
    }


class MonsterActorClassPathTest(unittest.TestCase):
    def test_mapping_verdicts_preserve_evidence_tiers(self):
        targets = [
            target(1, "/old"),
            target(2, "/catalog"),
            target(3),
        ]
        occurrences = [
            {
                "actor_class_id": 1,
                "identity_pair_catalog_count": 1,
                "observed_class_path": "/Chara/Npc/Monster/New/NewStandard",
            }
        ]
        mappings = paths._build_mappings(targets, occurrences)
        self.assertEqual(
            [row["verdict"] for row in mappings],
            ["catalog_with_runtime_override", "catalog_only", "unresolved"],
        )
        self.assertEqual(
            mappings[0]["adoption_path"],
            "/old",
        )

    def test_shared_identity_pair_cannot_promote(self):
        shared = target(4)
        shared["identity_pair_catalog_count"] = 2
        occurrences = [
            {
                "actor_class_id": 4,
                "identity_pair_catalog_count": 2,
                "observed_class_path": "/Chara/Npc/Monster/Maybe/MaybeStandard",
            }
        ]
        mapping = paths._build_mappings([shared], occurrences)[0]
        self.assertEqual(mapping["verdict"], "unresolved")
        self.assertEqual(mapping["retail_observation_count"], 0)


if __name__ == "__main__":
    unittest.main()
