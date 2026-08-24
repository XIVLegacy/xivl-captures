import unittest

from tools.extractors.extract_guildleve_journal_command import csv_bytes, find_all


class GuildleveJournalCommandTest(unittest.TestCase):
    def test_find_all_reports_overlapping_offsets(self):
        self.assertEqual(find_all(b"aaaa", b"aa"), [0, 1, 2])

    def test_empty_match_csv_retains_locator_schema(self):
        rendered = csv_bytes([]).decode("ascii")
        self.assertTrue(rendered.startswith("capture,lane_index,lane,"))
        self.assertEqual(rendered.count("\n"), 1)


if __name__ == "__main__":
    unittest.main()
