"""Guard tagged work streams and the bestiary absence boundary."""

import struct
import unittest

from tools.build_species_drop_coverage import table_fields_present
from tools.extractors.extract_group_combat_contracts import parse_work


class GroupWorkTests(unittest.TestCase):
    def test_variable_records_and_terminal_target(self):
        stream = bytes([1]) + struct.pack("<I", 123) + bytes([7, 0x88]) + b"/_init"
        app = struct.pack("<Q", 99) + bytes([len(stream)]) + stream
        records, markers = parse_work(app.ljust(144, b"\0"))
        self.assertEqual(
            records, [{"offset": 9, "property_id": 123, "width": 1, "value": 7}]
        )
        self.assertEqual(markers, [{"offset": 15, "tag": 0x88, "target": "/_init"}])

    def test_rejects_partial_property(self):
        app = (bytes(8) + bytes([5, 8]) + bytes(4)).ljust(144, b"\0")
        with self.assertRaisesRegex(ValueError, "truncated group-work property"):
            parse_work(app)

    def test_rejects_nonzero_unused_capacity(self):
        app = bytearray(144)
        app[-1] = 1
        with self.assertRaisesRegex(ValueError, "unused capacity"):
            parse_work(bytes(app))


class BestiaryFieldTests(unittest.TestCase):
    def test_dropkick_skill_is_not_an_item_table(self):
        self.assertEqual(
            table_fields_present("| ドロップキック | 近接単体 |"), (False, False)
        )

    def test_item_and_level_rows_are_detected(self):
        self.assertEqual(
            table_fields_present("| アイテム | item |\n| レベル | 5-7 |"), (True, True)
        )


if __name__ == "__main__":
    unittest.main()
