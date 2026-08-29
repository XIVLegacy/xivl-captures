import csv
import importlib.util
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "extractors" / "extract_player_hp_calibration.py"
SPEC = importlib.util.spec_from_file_location("extract_player_hp_calibration", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PlayerHpCalibrationTests(unittest.TestCase):
    def test_exact_hash_correlation_and_repeated_leads(self):
        self.assertEqual(
            [(label, prop_hash) for label, prop_hash, _, _ in MODULE.PROPERTY_SPECS],
            [
                ("state_mainSkill[0]", "0x7532ce24"),
                ("state_mainSkillLevel", "0x96063588"),
                ("generalParameter[5]", "0x416571ac"),
                ("hpMax[0]", "0x7bcdfb69"),
            ],
        )
        rows = MODULE.extract_rows()
        self.assertEqual(len(rows), 12)
        self.assertEqual(Counter(row["repeated_lead"] for row in rows), {"lead-1": 6, "lead-2": 6})
        self.assertEqual(
            {
                (row["state_mainSkill_0"], row["state_mainSkillLevel"],
                 row["generalParameter_5"], row["hpMax_0"])
                for row in rows
            },
            {(4, 26, 102, 758), (3, 31, 110, 1016)},
        )

    def test_changed_correlation_fails_closed(self):
        with MODULE.INPUT.open(encoding="ascii", newline="") as handle:
            rows = list(csv.DictReader(handle))
            fieldnames = handle.seek(0) or next(csv.reader(handle))
        target = next(
            row for row in rows
            if row["capture"] == "login.pcapng"
            and row["frame_index"] == "17"
            and row["property_hash"] == "0x416571ac"
        )
        target["value_u_le"] = "103"
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "property-records.csv"
            with path.open("w", encoding="ascii", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "lead reconciliation changed"):
                MODULE.extract_rows(path)


if __name__ == "__main__":
    unittest.main()
