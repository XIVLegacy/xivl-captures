import json
import math
import struct
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import jsonschema
from scapy.layers.inet import IP, TCP
from scapy.packet import Raw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "extractors"))

import extract_party_marker_chronology as marker  # noqa: E402


def application(count=1):
    data = bytearray(marker.APPLICATION_SIZE)
    struct.pack_into("<III", data, 0, 1, 2, 3)
    struct.pack_into("<I", data, marker.RECORD_OFFSET + 0x00, 4)
    struct.pack_into("<I", data, marker.RECORD_OFFSET + 0x08, 5)
    struct.pack_into("<I", data, marker.RECORD_OFFSET + 0x0C, 6)
    struct.pack_into("<ffff", data, marker.RECORD_OFFSET + 0x14, 1.25, 2.5, -3.75, 4.5)
    data[marker.COUNT_OFFSET] = count
    return data


def sub_body(data):
    return bytes(marker.INNER_HEADER_LEN + marker.GAME_PREAMBLE_SIZE) + bytes(data)


class PartyMarkerChronologyTests(unittest.TestCase):
    def test_decodes_only_client_read_record_fields(self):
        decoded, reason = marker.decode_application(marker.EXPECTED_SUBEVENT_SIZE, sub_body(application()))
        self.assertEqual(reason, "")
        self.assertEqual(decoded["header"], (1, 2, 3))
        self.assertEqual(decoded["count"], 1)
        self.assertEqual(decoded["records"][0][:3], (4, 5, 6))
        self.assertEqual(decoded["records"][0][3:], (1.25, 2.5, -3.75, 4.5))

    def test_rejects_mutated_size(self):
        decoded, reason = marker.decode_application(1, sub_body(application()))
        self.assertIsNone(decoded)
        self.assertEqual(reason, "unexpected_subevent_size")

    def test_rejects_count_beyond_reserved_rows(self):
        decoded, reason = marker.decode_application(
            marker.EXPECTED_SUBEVENT_SIZE, sub_body(application(marker.RECORD_CAPACITY + 1))
        )
        self.assertIsNone(decoded)
        self.assertEqual(reason, "count_exceeds_reserved_capacity")

    def test_rejects_nonzero_reserved_tail(self):
        data = application()
        data[-1] = 1
        decoded, reason = marker.decode_application(marker.EXPECTED_SUBEVENT_SIZE, sub_body(data))
        self.assertIsNone(decoded)
        self.assertEqual(reason, "nonzero_reserved_tail")

    def test_rejects_nonfinite_float(self):
        data = application()
        struct.pack_into("<f", data, marker.RECORD_OFFSET + 0x14, math.inf)
        decoded, reason = marker.decode_application(marker.EXPECTED_SUBEVENT_SIZE, sub_body(data))
        self.assertIsNone(decoded)
        self.assertEqual(reason, "nonfinite_record_float")

    def test_snapshot_shapes_are_chronology_only(self):
        first = {"lane_index": 0, "lane": "main", "header": (1, 2, 3), "records": ((4, 5, 6, 1.0, 2.0, 3.0, 4.0),), "count": 1, "snapshot_key": b"first"}
        repeated = dict(first)
        changed = {**first, "records": ((4, 5, 6, 2.0, 2.0, 3.0, 4.0),), "snapshot_key": b"changed"}
        increased = {**changed, "count": 2, "snapshot_key": b"increased"}
        decreased = {**changed, "count": 1, "snapshot_key": b"decreased"}
        marker._snapshot_shapes([first, repeated, changed, increased, decreased])
        self.assertEqual(first["chronology_shape"], "first-observed-nonempty")
        self.assertEqual(repeated["chronology_shape"], "repeated-nonempty")
        self.assertEqual(changed["chronology_shape"], "changed-same-count-nonempty")
        self.assertEqual(increased["chronology_shape"], "increased-count-nonempty")
        self.assertEqual(decreased["chronology_shape"], "decreased-count-nonempty")

    def test_correlation_sets_include_requested_opcodes(self):
        self.assertIn(0x018B, marker.CATEGORIES["group_layout_018b"])
        self.assertIn(0x0193, marker.CATEGORIES["setup_0193"])
        self.assertIn(0x00CA, marker.CATEGORIES["actor_lifecycle"])
        self.assertIn(0x0005, marker.CATEGORIES["zone_transition"])

    def test_retransmission_overlap_is_counted_once(self):
        packets = [
            IP(src="203.0.113.10", dst="203.0.113.20") /
            TCP(sport=54992, dport=50000, seq=100) / Raw(b"abcd"),
            IP(src="203.0.113.10", dst="203.0.113.20") /
            TCP(sport=54992, dport=50000, seq=100) / Raw(b"abcd"),
            IP(src="203.0.113.10", dst="203.0.113.20") /
            TCP(sport=54992, dport=50000, seq=104) / Raw(b"efgh"),
        ]
        connection = {
            "server_endpoint": ("203.0.113.10", 54992),
            "client_endpoint": ("203.0.113.20", 50000),
            "streams": {"s2c": b"abcdefgh"},
        }
        with patch.object(marker, "read_packets", return_value=packets):
            self.assertEqual(marker._segment_accounting(Path("unused"), connection, "s2c"), (4, 0))

    def test_accounting_schema_rejects_unknown_fields(self):
        schema = json.loads(
            (ROOT / "schemas" / "party-marker-chronology.schema.json").read_text(encoding="utf-8")
        )
        accounting = json.loads(
            (ROOT / "studies" / marker.STUDY_ID / "derived" / "accounting.json").read_text(encoding="ascii")
        )
        jsonschema.validate(accounting, schema)
        accounting["unexpected"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(accounting, schema)

    def test_public_columns_exclude_sensitive_raw_surfaces(self):
        fields = marker.OCCURRENCE_FIELDS + marker.RECORD_FIELDS + marker.NEIGHBOR_FIELDS
        forbidden = ("payload", "endpoint", "timestamp", "raw_actor", "player_name")
        for field in fields:
            self.assertFalse(any(token in field for token in forbidden), field)

    def test_public_csv_rejects_endpoint_and_raw_id_mutations(self):
        with self.assertRaisesRegex(ValueError, "IPv4-like"):
            marker.validate_public_csv(b"field\n203.0.113.10\n")
        with self.assertRaisesRegex(ValueError, "32-bit"):
            marker.validate_public_csv(b"field\n0x1234abcd\n")


if __name__ == "__main__":
    unittest.main()
