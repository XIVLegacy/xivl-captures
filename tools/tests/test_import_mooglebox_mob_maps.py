from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools import import_mooglebox_mob_maps as intake


EXPECTED_SIZES = {
    "blackshroud.html": 97572,
    "coerthas.html": 75419,
    "la-noscea.html": 90026,
    "thanalan.html": 98901,
}


class MoogleboxMobMapTests(unittest.TestCase):
    def test_pinned_source_hashes_and_sizes(self) -> None:
        for filename, expected_hash in intake.EXPECTED_SOURCE_SHA256.items():
            path = intake.DEFAULT_SOURCE_DIR / filename
            raw = path.read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), expected_hash)
            self.assertEqual(path.stat().st_size, EXPECTED_SIZES[filename])

    def test_audited_marker_counts(self) -> None:
        rows = intake.load_rows(intake.DEFAULT_SOURCE_DIR)
        counts = {region["region"]: 0 for region in intake.REGIONS}
        for row in rows:
            counts[row["region"]] += 1
        self.assertEqual(
            counts,
            {
                "Coerthas": 39,
                "Black Shroud": 74,
                "La Noscea": 63,
                "Thanalan": 78,
            },
        )

    def test_known_amaljaa_shared_slot_tuple(self) -> None:
        rows = intake.load_rows(intake.DEFAULT_SOURCE_DIR)
        row = next(
            row
            for row in rows
            if row["region"] == "Thanalan" and row["marker_order"] == "11"
        )
        self.assertEqual(row["label_raw"], "Amalj'aa Lancer/Divinator/Bowyer/Drubber")
        self.assertEqual(
            json.loads(row["parsed_candidates"]),
            ["Amalj'aa Lancer", "Divinator", "Bowyer", "Drubber"],
        )
        self.assertEqual(row["level_text"], "47-49")
        self.assertEqual((row["level_min"], row["level_max"]), ("47", "49"))
        self.assertEqual(row["amount_text"], "8")
        self.assertEqual((row["amount_min"], row["amount_max"]), ("8", "8"))
        self.assertEqual(row["amount_approximation"], "exact")
        self.assertEqual((row["map_x"], row["map_y"]), ("2075", "-1675"))
        self.assertEqual(row["coordinates"], "41,33")
        self.assertEqual((row["coordinate_x"], row["coordinate_y"]), ("41", "33"))
        self.assertEqual(row["aggression_marker"], "1")
        self.assertEqual(row["shared_slot_verdict"], "unresolved_shared_slot")

    def test_owner_supplied_amaljaa_tuple(self) -> None:
        rows = intake.load_rows(intake.DEFAULT_SOURCE_DIR)
        row = next(
            row
            for row in rows
            if row["region"] == "Thanalan" and row["marker_order"] == "52"
        )
        self.assertEqual(row["label_raw"], "Amalj'aa Scout/Harpooner/Ranger/Seer")
        self.assertEqual(row["level_text"], "20-21")
        self.assertEqual(row["amount_text"], "8-10")
        self.assertEqual(row["coordinates"], "14.5,21")
        self.assertEqual(row["shared_slot_verdict"], "unresolved_shared_slot")

    def test_rendered_csv_is_byte_deterministic(self) -> None:
        rows = intake.load_rows(intake.DEFAULT_SOURCE_DIR)
        first = intake.render_csv(rows)
        second = intake.render_csv(rows)
        self.assertEqual(first, second)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "marker-records.csv"
            output.write_bytes(first)
            with output.open(newline="", encoding="utf-8") as handle:
                records = list(csv.DictReader(handle))
            self.assertEqual(len(records), 254)
            self.assertEqual(records[0]["region"], "Coerthas")
            self.assertEqual(records[-1]["region"], "Thanalan")


if __name__ == "__main__":
    unittest.main()
