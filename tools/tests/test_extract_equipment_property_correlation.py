import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "extractors" / "extract_equipment_property_correlation.py"
SPEC = importlib.util.spec_from_file_location("extract_equipment_property_correlation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class EquipmentPropertyCorrelationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = MODULE.extract_rows()
        cls.by_capture = {row["capture"]: row for row in cls.rows}

    def test_exact_capture_matrix(self):
        self.assertEqual(
            [(row["capture"], row["verdict"]) for row in self.rows],
            [
                ("change_bodyarmor.pcapng", "AFTER-ONLY"),
                ("change_helm.pcapng", "CORRELATED"),
                ("gear_changesoul.pcapng", "NO-GO"),
                ("gear_changeweapon.pcapng", "AFTER-ONLY"),
            ],
        )

    def test_item_and_link_joins(self):
        expected = {
            "change_bodyarmor.pcapng": ("0x007A88D7", 10, 140),
            "change_helm.pcapng": ("0x007A3F58", 8, 113),
            "gear_changeweapon.pcapng": ("0x003D7E3D", 0, 79),
        }
        for capture, values in expected.items():
            row = self.by_capture[capture]
            self.assertEqual(
                (row["catalog_item_id"], row["equipment_slot"], row["linked_item_slot"]),
                values,
            )

    def test_helm_change_preserves_index_without_semantics(self):
        helm = self.by_capture["change_helm.pcapng"]
        self.assertEqual(
            (helm["property_label"], helm["property_hash"], helm["before_value"], helm["after_value"]),
            ("generalParameter[18]", "0x8cae90db", "141", "161"),
        )
        self.assertEqual(helm["old_slot_link_status"], "missing")

    def test_missing_evidence_fails_closed(self):
        self.assertEqual(
            self.by_capture["change_bodyarmor.pcapng"]["property_projection_record_count"], 5
        )
        self.assertEqual(
            self.by_capture["gear_changeweapon.pcapng"]["property_projection_record_count"], 75
        )
        self.assertEqual(self.by_capture["change_bodyarmor.pcapng"]["after_value"], "147")
        self.assertEqual(self.by_capture["gear_changeweapon.pcapng"]["after_value"], "169")
        soul = self.by_capture["gear_changesoul.pcapng"]
        self.assertEqual(soul["catalog_item_id"], "")
        self.assertEqual(soul["old_slot_link_status"], "not-applicable")

    def test_actual_gear_captures_have_no_018f_0191_stream(self):
        self.assertEqual(
            {row["gear_stream_0x018f_0x0191"] for row in self.rows},
            {"absent"},
        )


if __name__ == "__main__":
    unittest.main()
