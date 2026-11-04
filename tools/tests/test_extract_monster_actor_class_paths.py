import unittest
from pathlib import Path
from unittest.mock import patch

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
    def test_lifetimes_use_wrapper_source_instead_of_header_clock(self):
        def record(opcode, source, value=0, clock=9):
            raw = bytearray(20)
            raw[8:12] = clock.to_bytes(4, "little")
            raw[16:20] = value.to_bytes(4, "little")
            if opcode == 0x00CC:
                raw.extend(b"Example\0/Chara/Npc/Monster/Example\0")
            return {
                "direction": "s2c",
                "opcode": opcode,
                "source_actor_id": source,
                "bytes": raw.hex(),
            }

        records = [
            record(0x00CC, 0x1234),
            record(0x00CC, 0x5678),
            record(0x00D6, 0x1234, 7, clock=10),
            record(0x013D, 0x1234, 1000001, clock=10),
            record(0x00D6, 0x5678, 7, clock=11),
            record(0x013D, 0x5678, 1000002, clock=11),
        ]
        with (
            patch.object(paths, "default_corpus_paths", return_value=[Path("test")]),
            patch.object(Path, "is_file", return_value=True),
            patch.object(paths, "walk_capture_payloads", return_value=records),
        ):
            occurrences, accounting = paths._scan([target(1), target(2)])
        self.assertEqual(
            [(row["source_actor_id"], row["actor_class_id"]) for row in occurrences],
            [("0x00001234", 1), ("0x00005678", 2)],
        )
        self.assertEqual(accounting["completed_lifetime_count"], 2)

    def test_payload_walker_preserves_wrapper_source(self):
        raw = bytearray(36)
        raw[0:2] = (36).to_bytes(2, "little")
        raw[2:4] = (3).to_bytes(2, "little")
        raw[4:8] = (0x1234).to_bytes(4, "little")
        raw[8:12] = (0x5678).to_bytes(4, "little")
        raw[18:20] = (0x00CC).to_bytes(2, "little")
        raw[24:28] = (9).to_bytes(4, "little")
        with patch.dict(
            paths.walk_capture_payloads.__globals__,
            reconstruct=lambda path: {"s2c": b"synthetic"},
            parse_outer_frames=lambda blob: [{"body": bytes(raw)}],
        ):
            records = paths.walk_capture_payloads(Path("test"))
        self.assertEqual(records[0]["source_actor_id"], 0x1234)
        self.assertEqual(bytes.fromhex(records[0]["bytes"])[8:12], b"\x09\0\0\0")

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
