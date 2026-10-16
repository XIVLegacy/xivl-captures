import csv
import importlib.util
import io
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "extractors" / "extract_battle_result_actor_join.py"
SPEC = importlib.util.spec_from_file_location(
    "extract_battle_result_actor_join", SCRIPT
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)
ENGAGE = MODULE.DEFAULT_OUT / "engage-order.csv"


class BattleResultActorJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = MODULE.build(
            MODULE.DEFAULT_BATTLE_ROWS, MODULE.DEFAULT_PROPERTY_RECORDS, ENGAGE, True
        )

    def anchors(self):
        text = self.outputs["anchor-summary.csv"].decode("ascii")
        return {row["anchor_id"]: row for row in csv.DictReader(io.StringIO(text))}

    def test_field_hashes_match_property_names(self):
        MODULE.verify_field_hashes()
        self.assertEqual(
            {spec[0]: spec[2] for spec in MODULE.FIELD_SPECS}["hpMax"], "0x7bcdfb69"
        )

    def test_anchor_verdicts(self):
        anchors = self.anchors()
        conflicts = {"A34", "A42", "A43", "A44", "A45"}
        for anchor_id, row in anchors.items():
            if anchor_id.startswith("U"):
                expected = "UNRESOLVABLE"
            elif anchor_id in conflicts:
                expected = "CONFLICT"
            else:
                expected = "REPRODUCED"
            self.assertEqual(row["verdict"], expected, anchor_id)
        self.assertEqual(anchors["A01"]["computed"], "4/50 (8.0 percent)")
        self.assertIn("(0.7759, 0.7765]", anchors["A23"]["computed"])
        self.assertIn("166 on 43722707 by 43723073", anchors["A34"]["computed"])
        self.assertIn("T2", anchors["A37"]["tier_mix"])

    def test_joined_rows_cover_every_battle_row(self):
        text = self.outputs["joined-rows.csv"].decode("ascii")
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(len(rows), MODULE.EXPECTED_BATTLE_ROWS)
        bridged = [
            row
            for row in rows
            if row["capture"] == MODULE.PBL
            and row["source_actor_id"] == str(MODULE.CLASS4_ACTOR)
        ]
        self.assertTrue(bridged)
        self.assertEqual({row["src_level"] for row in bridged}, {"26"})
        self.assertEqual({row["src_level_tier"] for row in bridged}, {"T2"})

    def test_k_interval_drops_outlier_then_intersects(self):
        def event(damage, delta):
            return {"delta": delta, "row": {"numeric_value": damage}}

        low, high, kept, dropped = MODULE.k_interval(
            [event(56, 44), event(61, 48), event(38, 30), event(57, 25)]
        )
        self.assertEqual(len(kept), 3)
        self.assertEqual(len(dropped), 1)
        self.assertEqual(low, Fraction(47, 61))
        self.assertEqual(high, Fraction(44, 56))

    def test_changed_row_count_fails_closed(self):
        with MODULE.DEFAULT_BATTLE_ROWS.open(encoding="ascii", newline="") as handle:
            lines = handle.readlines()
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "battle-result-rows.csv"
            path.write_text("".join(lines[:-1]), encoding="ascii", newline="")
            with self.assertRaisesRegex(ValueError, "expected 622 battle rows"):
                MODULE.build(path, MODULE.DEFAULT_PROPERTY_RECORDS, ENGAGE, True)


if __name__ == "__main__":
    unittest.main()
