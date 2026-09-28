"""Guard precision and non-observation boundaries in the supplied-table intake."""

import csv
import unittest

from tools import import_monster_population as importer


class PopulationIntakeTests(unittest.TestCase):
    def test_comments_are_not_observations(self):
        text = "-- INSERT INTO `t` (`x`) VALUES (9);\nINSERT INTO `t` (`x`) VALUES (-0.030);"
        tokens = list(importer.statements(text))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(list(importer.literal_rows(tokens[0]))[0][0], {"x": "-0.030"})

    def test_quoted_delimiters_and_original_precision(self):
        text = "INSERT INTO `t` (`name`,`x`,`y`) VALUES ('Dodore''s; minion, one',1.230, NULL);"
        row = list(importer.literal_rows(next(importer.statements(text))))[0][0]
        self.assertEqual(
            row, {"name": "Dodore's; minion, one", "x": "1.230", "y": None}
        )

    def test_column_mismatch_fails(self):
        with self.assertRaises(ValueError):
            list(
                importer.literal_rows(
                    next(importer.statements("INSERT INTO `t` (`x`,`y`) VALUES (1);"))
                )
            )

    def test_expression_is_not_a_literal_measurement(self):
        with self.assertRaises(ValueError):
            list(
                importer.literal_rows(
                    next(importer.statements("INSERT INTO `t` (`x`) VALUES (1+2);"))
                )
            )

    def test_public_evidence_invariants(self):
        importer.validate_public(importer.ROOT / "studies" / importer.STUDY / "derived")

    def test_authored_distribution_is_not_a_sighting(self):
        path = importer.ROOT / "studies" / importer.STUDY / "derived/observations.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        for section in ("Coerthas Western Highlands", "Etc1", "Copperbell Mines"):
            selected = [r for r in rows if r["source_section"].startswith(section)]
            self.assertTrue(selected)
            self.assertEqual(
                {r["position_verdict"] for r in selected}, {"authored-habitat"}
            )


if __name__ == "__main__":
    unittest.main()
