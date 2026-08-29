import json
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

import extract_0190_transaction_census as census  # noqa: E402


def target_body(opcode, *, key1=0, key2=0, vector=None, tail=None):
    application_size = 0x68 if opcode == census.RECORD else 8
    body = bytearray(census.INNER_HEADER_LEN + census.PACKET_HEADER_TAIL_SIZE + application_size)
    struct.pack_into("<H", body, 2, opcode)
    if opcode == census.RECORD:
        values = [key1, key2] + list(vector or range(census.VECTOR_WORDS))
        struct.pack_into("<18I", body, census.INNER_HEADER_LEN + census.PACKET_HEADER_TAIL_SIZE, *values)
        if tail is not None:
            body[-census.TAIL_SIZE:] = tail
    return bytes(body)


def event(opcode, position, **extra):
    row = {
        "opcode": opcode,
        "capture": "capture.pcapng",
        "lane_index": 0,
        "lane": "main",
        "frame_index": position,
        "subevent_index": 0,
    }
    row.update(extra)
    return row


class Map0190TransactionCensusTests(unittest.TestCase):
    @staticmethod
    def accounting():
        return json.loads(
            (ROOT / "studies" / census.STUDY_ID / "derived" / "accounting.json").read_text(
                encoding="ascii"
            )
        )

    def test_decodes_established_record_layout(self):
        tail = bytes(range(census.TAIL_SIZE))
        decoded, reason = census.decode_application(
            census.RECORD,
            census.EXPECTED_SIZES[census.RECORD],
            target_body(census.RECORD, key1=7, key2=9, tail=tail),
        )
        self.assertEqual(reason, "")
        self.assertEqual(decoded["key1"], 7)
        self.assertEqual(decoded["key2"], 9)
        self.assertEqual(decoded["vector"], tuple(range(census.VECTOR_WORDS)))
        self.assertEqual(decoded["tail"], tail)

    def test_rejects_mutated_shapes(self):
        decoded, reason = census.decode_application(census.RECORD, 1, target_body(census.RECORD))
        self.assertIsNone(decoded)
        self.assertEqual(reason, "unexpected_subevent_size")
        decoded, reason = census.decode_application(
            census.RECORD,
            census.EXPECTED_SIZES[census.RECORD],
            target_body(census.RECORD)[:-1],
        )
        self.assertIsNone(decoded)
        self.assertEqual(reason, "unexpected_application_shape")

    def test_segments_only_ordered_same_lane_spans(self):
        timeline = [
            event(census.RECORD, 0),
            event(census.BEGIN, 1, zero_application=True),
            event(0x0137, 2),
            event(census.RECORD, 3, application=b"a", key1=1, key2=0, vector=(0,) * 16, tail=bytes(32)),
            event(census.END, 4, zero_application=True),
            event(census.END, 5, zero_application=True),
        ]
        spans, issues = census.segment_transactions(timeline)
        self.assertEqual(len(spans), 1)
        self.assertEqual(len(spans[0]["records"]), 1)
        self.assertEqual(issues["orphan_record"], 1)
        self.assertEqual(issues["orphan_end"], 1)

    def test_nested_begin_closes_prior_candidate_as_malformed(self):
        timeline = [
            event(census.BEGIN, 0, zero_application=True),
            event(census.RECORD, 1),
            event(census.BEGIN, 2, zero_application=True),
            event(census.END, 3, zero_application=True),
        ]
        spans, issues = census.segment_transactions(timeline)
        self.assertEqual(len(spans), 1)
        self.assertEqual(len(spans[0]["records"]), 0)
        self.assertEqual(issues["nested_begin"], 1)
        self.assertEqual(issues["unterminated_span"], 1)

    def test_scope_overlap_detects_enclosing_change_frame(self):
        timeline = [
            event(0x016D, 0),
            event(census.BEGIN, 1),
            event(census.END, 2),
            event(0x016E, 3),
        ]
        self.assertTrue(census._scope_overlap(timeline, 1, 2, 0x016D, 0x016E))
        self.assertFalse(census._scope_overlap(timeline, 1, 2, 0x0146, 0x0147))

    def test_retransmitted_segments_are_separate_from_decoded_events(self):
        packets = [
            IP(src="203.0.113.10", dst="203.0.113.20") /
            TCP(sport=54992, dport=50000, seq=100) / Raw(b"abcd"),
            IP(src="203.0.113.10", dst="203.0.113.20") /
            TCP(sport=54992, dport=50000, seq=100) / Raw(b"abcd"),
        ]
        lanes = [{
            "server_endpoint": ("203.0.113.10", 54992),
            "client_endpoint": ("203.0.113.20", 50000),
        }]
        with patch.object(census, "reconstruct_lanes", return_value=lanes), patch.object(
            census, "read_packets", return_value=packets
        ):
            self.assertEqual(census._retransmitted_segments(Path("unused")), 1)

    def test_accounting_schema_rejects_count_mutation(self):
        schema = json.loads(
            (ROOT / "schemas" / "map-0190-transaction-census.schema.json").read_text(encoding="ascii")
        )
        accounting = self.accounting()
        jsonschema.validate(accounting, schema)
        accounting["corpus"]["target_s2c_0x0190"] -= 1
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(accounting, schema)

    def test_accounting_reconciles_events_vectors_and_changes(self):
        accounting = self.accounting()
        corpus = accounting["corpus"]
        self.assertEqual(corpus["source_manifest"], "sources/pcap-1.23b/manifest.yaml")
        layout = accounting["application_layouts"]["0x0190"]
        self.assertEqual(layout["key_dword_offsets"], [0, 4])
        self.assertEqual(
            (layout["record_dword_offset_first"], layout["record_dword_offset_last"]),
            (8, 0x44),
        )
        self.assertEqual(
            (layout["unread_tail_offset"], layout["unread_tail_size_bytes"]),
            (0x48, 32),
        )
        span_histogram = accounting["span_distributions"]["records_per_span"]
        self.assertEqual(
            sum(int(records) * count for records, count in span_histogram.items()),
            corpus["records_in_complete_spans"],
        )
        self.assertEqual(
            corpus["target_s2c_0x018f"] + corpus["target_s2c_0x0190"] + corpus["target_s2c_0x0191"],
            5625,
        )
        vectors = accounting["vectors"]
        self.assertEqual(sum(vectors["value_bands"].values()), 16 * vectors["record_vectors"])
        self.assertEqual(
            sum(int(words) * count for words, count in vectors["nonzero_word_count_histogram"].items()),
            sum(vectors["position_nonzero_counts"].values()),
        )
        self.assertEqual(
            vectors["equal_vector_comparisons"] + vectors["changed_vector_comparisons"],
            vectors["same_capture_lane_key_pair_comparisons"],
        )
        self.assertEqual(
            sum(vectors["changed_position_counts"].values()),
            sum(int(words) * count for words, count in vectors["changed_word_count_histogram"].items()),
        )

    def test_public_products_reject_raw_security_surfaces(self):
        with self.assertRaisesRegex(ValueError, "IPv4-like"):
            census.validate_public_bytes(b"203.0.113.10")
        with self.assertRaisesRegex(ValueError, "32-bit"):
            census.validate_public_bytes(b"0x1234abcd")
        with self.assertRaisesRegex(ValueError, "credential"):
            census.validate_public_bytes(b"session_id")

    def test_public_span_columns_exclude_raw_record_surfaces(self):
        forbidden = (
            "application", "payload", "key", "vector", "tail", "actor",
            "endpoint", "session", "timestamp", "address", "token",
        )
        for field in census.SPAN_FIELDS:
            self.assertFalse(any(term in field for term in forbidden), field)

    def test_rendered_products_pass_public_sanitizer(self):
        derived = ROOT / "studies" / census.STUDY_ID / "derived"
        for name in ("accounting.json", "spans.csv", "verdicts.md"):
            census.validate_public_bytes((derived / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
