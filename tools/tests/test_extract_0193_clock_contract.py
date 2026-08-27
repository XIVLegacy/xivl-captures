import json
import struct
import sys
import unittest
from pathlib import Path

import jsonschema
from scapy.layers.inet import IP, TCP
from scapy.packet import Raw
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "extractors"))

import extract_0193_clock_contract as clock  # noqa: E402


def sub_body(header_clock=100, reserved=0, subopcode=0x12, value=30):
    data = bytearray(clock.INNER_HEADER_LEN + clock.PACKET_HEADER_TAIL_SIZE + clock.APPLICATION_SIZE)
    struct.pack_into("<II", data, clock.INNER_HEADER_LEN, header_clock, reserved)
    struct.pack_into(
        "<II", data, clock.INNER_HEADER_LEN + clock.PACKET_HEADER_TAIL_SIZE,
        subopcode, value,
    )
    return bytes(data)


class Map0193ClockContractTests(unittest.TestCase):
    def test_decodes_modular_sum(self):
        decoded, reason = clock.decode_application(
            clock.EXPECTED_SUBEVENT_SIZE, sub_body(0xFFFFFFFE, value=3)
        )
        self.assertEqual(reason, "")
        self.assertEqual(decoded["subopcode"], 0x12)
        self.assertEqual(decoded["derived_modular_sum"], 1)
        self.assertFalse(decoded["special_sentinel"])

    def test_marks_sentinel_without_claiming_an_observed_case(self):
        decoded, reason = clock.decode_application(
            clock.EXPECTED_SUBEVENT_SIZE, sub_body(value=clock.SENTINEL)
        )
        self.assertEqual(reason, "")
        self.assertTrue(decoded["special_sentinel"])

    def test_rejects_mutated_shape_and_reserved_word(self):
        decoded, reason = clock.decode_application(1, sub_body())
        self.assertIsNone(decoded)
        self.assertEqual(reason, "unexpected_subevent_size")
        decoded, reason = clock.decode_application(
            clock.EXPECTED_SUBEVENT_SIZE, sub_body(reserved=1)
        )
        self.assertIsNone(decoded)
        self.assertEqual(reason, "nonzero_packet_header_reserved")

    def test_frame_completion_ignores_late_retransmission(self):
        spans = [
            {"start": 0, "end": 4, "packet_index": 1, "capture_time_us": 100},
            {"start": 0, "end": 4, "packet_index": 3, "capture_time_us": 300},
            {"start": 4, "end": 8, "packet_index": 2, "capture_time_us": 200},
        ]
        completion = clock._frame_completion(0, 8, spans)
        self.assertEqual(completion["packet_index"], 2)
        self.assertEqual(completion["capture_time_us"], 200)

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
        with patch.object(clock, "read_packets", return_value=packets):
            self.assertEqual(clock._segment_accounting(Path("unused"), connection, "s2c"), (4, 0))

    def test_compound_targets_keep_subevent_order(self):
        first = {
            "capture": "capture.pcapng", "lane_index": 0, "direction": "s2c",
            "frame_index": 4, "subopcode": 0x12, "application_value": 900,
        }
        second = {
            "capture": "capture.pcapng", "lane_index": 0, "direction": "s2c",
            "frame_index": 4, "subopcode": 0x14, "application_value": 2,
        }
        clock._annotate_targets([first, second])
        self.assertEqual(first["same_frame_target_ordinal"], 1)
        self.assertEqual(second["same_frame_target_ordinal"], 2)
        self.assertEqual(first["same_frame_target_count"], 2)

    def test_accounting_schema_rejects_mutation(self):
        schema = json.loads(
            (ROOT / "schemas" / "map-0193-clock-contract.schema.json").read_text(encoding="utf-8")
        )
        accounting = json.loads(
            (ROOT / "studies" / clock.STUDY_ID / "derived" / "accounting.json").read_text(encoding="ascii")
        )
        jsonschema.validate(accounting, schema)
        accounting["clock_correlations"]["same_session_server_utc_pairs"] = 1
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(accounting, schema)

    def test_public_columns_exclude_sensitive_raw_surfaces(self):
        fields = clock.OCCURRENCE_FIELDS + clock.NEIGHBOR_FIELDS
        forbidden = (
            "payload", "endpoint", "actor", "player", "token", "session",
            "capture_timestamp", "absolute_capture_time",
        )
        for field in fields:
            self.assertFalse(any(term in field for term in forbidden), field)

    def test_public_csv_rejects_security_mutations(self):
        with self.assertRaisesRegex(ValueError, "IPv4-like"):
            clock.validate_public_csv(b"field\n203.0.113.10\n")
        with self.assertRaisesRegex(ValueError, "32-bit"):
            clock.validate_public_csv(b"field\n0x1234abcd\n")
        with self.assertRaisesRegex(ValueError, "credential"):
            clock.validate_public_csv(b"field\nticket\n")


if __name__ == "__main__":
    unittest.main()
