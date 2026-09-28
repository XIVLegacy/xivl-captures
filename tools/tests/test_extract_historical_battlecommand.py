from __future__ import annotations

import importlib.util
import sys
import unittest
from xml.etree import ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "tools" / "extract_historical_battlecommand.py"
SPEC = importlib.util.spec_from_file_location(
    "extract_historical_battlecommand", MODULE_PATH
)
assert SPEC and SPEC.loader
extractor = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = extractor
SPEC.loader.exec_module(extractor)


class HistoricalBattleCommandTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = extractor.build_document(extractor.DEFAULT_SOURCE)
        cls.records = {
            record["normalized"]["command_id"]: record
            for record in cls.document["records"]
        }

    def test_extracts_complete_command_sheet(self) -> None:
        summary = self.document["summary"]
        self.assertEqual(summary["command_records"], 1237)
        self.assertEqual(summary["unique_command_ids"], 1237)
        self.assertEqual(summary["command_sheet_formula_cells"], 30648)
        self.assertEqual(summary["cached_formula_error_cells"], 20)
        self.assertEqual(summary["unfinished_weapon_skill_rows"], 230)
        self.assertEqual(summary["unfinished_weapon_skill_unique_ids"], 224)
        self.assertEqual(summary["commands_without_unfinished_weapon_skill_row"], 1013)

    def test_preserves_raw_normalized_and_formula_layers(self) -> None:
        backflip = self.records[23058]
        self.assertEqual(backflip["raw"]["full_battle_animation_hex"], "13002000")
        self.assertEqual(backflip["normalized"]["full_battle_animation"], 318775296)
        self.assertEqual(
            backflip["cached_formulas"]["full_battle_animation"],
            "of:=BITOR(BITLSHIFT([.I84];24);BITOR(BITLSHIFT([.J84];12);[.K84]))",
        )

    def test_keeps_analyst_table_separate(self) -> None:
        backflip_rows = self.records[23058]["unfinished_weapon_skill_rows"]
        self.assertEqual(len(backflip_rows), 1)
        self.assertEqual(backflip_rows[0]["normalized"]["aoe_type"], 2)
        self.assertEqual(self.records[23456]["unfinished_weapon_skill_rows"], [])

    def test_flags_non_numeric_workbook_values(self) -> None:
        ambiguous = self.records[23370]
        self.assertEqual(ambiguous["raw"]["animation_type"], "?")
        self.assertIsNone(ambiguous["normalized"]["animation_type"])
        self.assertIn("animation_type", ambiguous["normalization_issues"])

    def test_renders_ascii_deterministically(self) -> None:
        first = extractor.render_document(self.document)
        second = extractor.render_document(
            extractor.build_document(extractor.DEFAULT_SOURCE)
        )
        self.assertEqual(first, second)
        first.decode("ascii")

    def test_preserves_rows_after_repeated_blank_gap(self) -> None:
        root = ET.fromstring(
            f'''<office:document-content
                xmlns:office="{extractor.NS["office"]}"
                xmlns:table="{extractor.NS["table"]}"
                xmlns:text="{extractor.NS["text"]}">
              <office:body><office:spreadsheet><table:table table:name="Gap">
                <table:table-row><table:table-cell office:value-type="string"><text:p>head</text:p></table:table-cell></table:table-row>
                <table:table-row table:number-rows-repeated="3"><table:table-cell/></table:table-row>
                <table:table-row><table:table-cell office:value-type="string"><text:p>tail</text:p></table:table-cell></table:table-row>
              </table:table></office:spreadsheet></office:body>
            </office:document-content>'''
        )
        tables, _ = extractor.read_tables(root)
        self.assertEqual([row_number for row_number, _ in tables["Gap"]], [1, 5])


if __name__ == "__main__":
    unittest.main()
