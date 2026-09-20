from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import import_navmut_observations as intake


def record(observation_id: str, subject_type: str, zone: int) -> dict:
    return {
        "created_at": "2026-09-17T00:00:00.000000Z",
        "map_bounds": [-1.0, -2.0, 3.0, 4.0],
        "notes": "raw note",
        "observation_id": observation_id,
        "position": [1.0, 2.0, 3.0],
        "profile_id": "profile-29e7368b41e51dd7",
        "rotation": 0.0,
        "schema_version": 2,
        "subject_name": "Raw Name",
        "subject_type": subject_type,
        "zone": zone,
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_bytes(
        b"".join(
            json.dumps(row, separators=(",", ":")).encode("utf-8") + b"\n"
            for row in rows
        )
    )


class NavmutIntakeTests(unittest.TestCase):
    def test_repository_input_is_the_default(self) -> None:
        args = intake.parse_args([])
        self.assertEqual(args.input, intake.DEFAULT_INPUT)
        self.assertEqual(args.supplement, intake.DEFAULT_SUPPLEMENT)

    def test_pinned_supplement_archive_is_valid(self) -> None:
        archive_raw, observations_raw, records = intake.read_supplement_archive(
            intake.DEFAULT_SUPPLEMENT
        )
        self.assertEqual(
            intake.sha256_bytes(archive_raw), intake.EXPECTED_SUPPLEMENT_SHA256
        )
        self.assertEqual(
            intake.sha256_bytes(observations_raw),
            intake.EXPECTED_SUPPLEMENT_MEMBER_SHA256,
        )
        self.assertEqual(len(records), 86)
        self.assertEqual({row["subject_type"] for row in records}, {"npc"})

    def test_schema_record_and_category_partition(self) -> None:
        row = record("b665b9cc-2d78-425c-9cc8-dbf674386c2c", "monster", 128)
        self.assertEqual(intake.validate_record(row, 1), row)
        self.assertEqual(intake.CATEGORY_BY_TYPE["monster"], "ambient")
        self.assertEqual(intake.CATEGORY_BY_TYPE["mmonster"], "encounter")
        self.assertEqual(intake.CATEGORY_BY_TYPE["npc"], "npc")
        self.assertEqual(intake.CATEGORY_BY_TYPE["misc"], "misc")
        self.assertEqual(intake.category_for_type("Misc"), "misc")

    def test_record_classification_keeps_source_categories_and_promotes_candidates(
        self,
    ) -> None:
        overworld = record("b665b9cc-2d78-425c-9cc8-dbf674386c2c", "monster", 128)
        toto_rak = record("ae2ecc91-33a4-407b-8aa9-6bae5cc34dca", "monster", 159)
        quest = record("4d4a7d6b-c2cc-4da7-9955-3b6f982abf2f", "monster", 190)
        quest["notes"] = 'Grand Company quest "united we stand" spawn'
        gc = record("2b9df49b-8586-43dc-9b0b-cfda02c8ff72", "monster", 128)
        gc["notes"] = "GC content spawn"
        mmonster = record("9f5d2c7a-8d25-4c95-9d5d-8f2c7e7d4e01", "mmonster", 128)
        npc = record("e1e4a27f-6a7e-4a1d-8473-2a1c2b5e7f47", "npc", 159)
        npc["notes"] = "boss encounter note, identity remains NPC"
        misc = record("06c2fd49-6f2e-4e3a-8e55-c2ad2f2d5c2a", "Misc", 159)
        misc["notes"] = "content boss note remains misc"

        self.assertEqual(intake.category_for_record(overworld), "ambient")
        self.assertEqual(intake.category_for_record(toto_rak), "encounter")
        self.assertEqual(intake.category_for_record(quest), "encounter")
        self.assertEqual(intake.category_for_record(gc), "encounter")
        self.assertEqual(intake.category_for_record(mmonster), "encounter")
        self.assertEqual(intake.category_for_record(npc), "npc")
        self.assertEqual(intake.category_for_record(misc), "misc")
        self.assertIn("Toto-Rak", intake.category_basis_for_record(toto_rak))
        self.assertIn("Grand Company", intake.category_basis_for_record(quest))

    def test_duplicate_uuid_content_conflict_is_explicit(self) -> None:
        row = record("b665b9cc-2d78-425c-9cc8-dbf674386c2c", "monster", 128)
        changed = dict(row)
        changed["subject_name"] = "Changed"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "observations.jsonl"
            write_jsonl(path, [row, changed])
            with self.assertRaisesRegex(
                intake.IntakeError, "observation_id content conflict"
            ):
                intake.read_records(path, enforce_pin=False)

    def test_same_uuid_duplicate_is_rejected(self) -> None:
        row = record("b665b9cc-2d78-425c-9cc8-dbf674386c2c", "monster", 128)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "observations.jsonl"
            write_jsonl(path, [row, row])
            with self.assertRaisesRegex(intake.IntakeError, "duplicate observation_id"):
                intake.read_records(path, enforce_pin=False)

    def test_additive_merge_is_idempotent_and_conflict_safe(self) -> None:
        row = record("b665b9cc-2d78-425c-9cc8-dbf674386c2c", "monster", 128)
        second = record("ae2ecc91-33a4-407b-8aa9-6bae5cc34dca", "npc", 150)
        self.assertEqual(intake.merge_records([row], [row, second]), [row, second])

        changed = dict(row)
        changed["subject_name"] = "Changed"
        with self.assertRaisesRegex(
            intake.IntakeError, "observation_id content conflict"
        ):
            intake.merge_records([row], [changed])

    def test_raw_install_is_idempotent_and_conflict_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_dir = Path(directory) / "source"
            raw = b"immutable bytes\n"
            intake.install_raw(source_dir, raw, check=False)
            intake.install_raw(source_dir, raw, check=False)
            self.assertEqual(
                (source_dir / "objects" / "observations.jsonl").read_bytes(), raw
            )
            with self.assertRaisesRegex(intake.IntakeError, "content conflict"):
                intake.install_raw(source_dir, b"changed bytes\n", check=False)

    def test_review_products_are_zone_sorted_and_keep_raw_fields(self) -> None:
        rows = [
            record("b665b9cc-2d78-425c-9cc8-dbf674386c2c", "npc", 190),
            record("ae2ecc91-33a4-407b-8aa9-6bae5cc34dca", "misc", 159),
        ]
        review = intake.render_review(rows)
        self.assertLess(review.index("### Zone 159"), review.index("### Zone 190"))
        self.assertIn("ae2ecc91-33a4-407b-8aa9-6bae5cc34dca", review)
        self.assertIn("observation-only", review)
        self.assertIn("fst0Dungeon03", review)
        self.assertIn("canonical zone name", review)
        self.assertIn("Raw misc spellings are misc=1, Misc=0", review)
        for row in rows:
            self.assertEqual(review.count(row["observation_id"]), 1)
        csv_text = intake.render_csv(rows)
        self.assertIn("subject_name", csv_text.splitlines()[0])
        self.assertIn("category_basis", csv_text.splitlines()[0])
        self.assertIn("Raw Name", csv_text)
        self.assertEqual(len(csv_text.splitlines()), 3)


if __name__ == "__main__":
    unittest.main()
