import importlib.util
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "extractors" / "extract_property_stream_catalog.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("extract_property_stream_catalog", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PropertyStreamCatalogTests(unittest.TestCase):
    def test_property_and_target_marker(self):
        marker = bytes([0x60 + 4]) + b"work"
        record = bytes([2]) + struct.pack("<I", 0x12345678) + b"\x34\x12"
        block = bytes([len(marker + record)]) + marker + record + bytes(120)
        rows, declared, terminated, consumed = MODULE.parse_records(block)
        self.assertEqual(declared, len(marker + record))
        self.assertFalse(terminated)
        self.assertEqual(consumed, 1 + declared)
        self.assertEqual(rows[0]["target_marker"], "work")
        self.assertEqual(rows[0]["property_hash"], "0x12345678")
        self.assertEqual(rows[0]["value_u_le"], 0x1234)

    def test_zero_terminator(self):
        rows, declared, terminated, consumed = MODULE.parse_records(bytes([1, 0]))
        self.assertEqual((rows, declared, terminated, consumed), ([], 1, True, 1))

    def test_a0_target_marker_continues_parsing(self):
        target = b"charaWork/commandDetailForSelf"
        self.assertEqual(len(target), 30)
        record = bytes([1]) + struct.pack("<I", 0x12345678) + b"\x01"
        stream = bytes([0xA0]) + target + record
        rows, declared, terminated, consumed = MODULE.parse_records(bytes([len(stream)]) + stream)
        self.assertEqual(declared, len(stream))
        self.assertFalse(terminated)
        self.assertEqual(consumed, 1 + declared)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["target_marker"], target.decode("ascii"))
        self.assertEqual(rows[0]["property_hash"], "0x12345678")

    def test_incomplete_tail_is_not_promoted(self):
        rows, declared, terminated, consumed = MODULE.parse_records(bytes([3, 4, 1, 2]))
        self.assertEqual(rows, [])
        self.assertEqual(declared, 3)
        self.assertFalse(terminated)
        self.assertEqual(consumed, 1)


if __name__ == "__main__":
    unittest.main()
