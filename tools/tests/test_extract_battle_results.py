from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "extractors"))
from extract_battle_results import decode_packet  # noqa: E402


class BattleResultDecodeTests(unittest.TestCase):
    def test_x01_offsets(self):
        app = bytearray(56)
        struct.pack_into("<II", app, 0, 0x11111111, 0x22222222)
        struct.pack_into("<HHHH", app, 0x20, 1, 3, 27346, 5)
        struct.pack_into("<IHHI", app, 0x28, 0x33333333, 157, 30320, 44)
        app[0x34:0x36] = bytes((6, 7))
        header, rows = decode_packet(bytes(app), 0x0139)
        self.assertEqual(header["command_id"], 27346)
        self.assertEqual(rows, [{
            "target_actor_id": 0x33333333, "numeric_value": 157,
            "world_master_text_id": 30320, "effect_id": 44,
            "text_param": 6, "row_ordinal_or_filter": 7,
        }])

    def test_x10_transposes_sparse_arrays(self):
        app = bytearray(184)
        struct.pack_into("<H", app, 0x20, 2)
        for i, value in enumerate((101, 102)):
            struct.pack_into("<I", app, 0x28 + i * 4, value)
            struct.pack_into("<H", app, 0x50 + i * 2, 201 + i)
            struct.pack_into("<H", app, 0x64 + i * 2, 30301 + i)
            struct.pack_into("<I", app, 0x78 + i * 4, 301 + i)
            app[0xA0 + i] = 4 + i
            app[0xAA + i] = 6 + i
        _header, rows = decode_packet(bytes(app), 0x013A)
        self.assertEqual([row["target_actor_id"] for row in rows], [101, 102])
        self.assertEqual([row["numeric_value"] for row in rows], [201, 202])
        self.assertEqual([row["world_master_text_id"] for row in rows], [30301, 30302])

    def test_row_count_bound(self):
        app = bytearray(56)
        struct.pack_into("<H", app, 0x20, 2)
        with self.assertRaisesRegex(ValueError, "exceeds 1"):
            decode_packet(bytes(app), 0x0139)

    def test_x18_static_offsets(self):
        app = bytearray(296)
        struct.pack_into("<H", app, 0x20, 1)
        struct.pack_into("<I", app, 0x28, 401)
        struct.pack_into("<H", app, 0x70, 402)
        struct.pack_into("<H", app, 0x94, 30301)
        struct.pack_into("<I", app, 0xB8, 403)
        app[0x100] = 4
        app[0x112] = 5
        _header, rows = decode_packet(bytes(app), 0x013B)
        self.assertEqual(rows[0], {
            "target_actor_id": 401, "numeric_value": 402,
            "world_master_text_id": 30301, "effect_id": 403,
            "text_param": 4, "row_ordinal_or_filter": 5,
        })


if __name__ == "__main__":
    unittest.main()
