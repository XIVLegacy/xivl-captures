import importlib.util
import struct
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "extractors" / "extract_cast_result_state_order.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("extract_cast_result_state_order", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


ACTOR = "actor-haaaaaaaaaaaa"
OTHER_ACTOR = "actor-hbbbbbbbbbbbb"


def property_event(lane: int, event_index: int, record: int, value: int) -> dict:
    return {
        "capture": "fixture.pcapng",
        "lane_index": lane,
        "lane_event_index": event_index,
        "frame_index": event_index,
        "frame_offset": event_index * 100,
        "inflated_offset": record * 16,
        "subevent_index": 0,
        "subevent_size": 168,
        "inner_size": 20,
        "opcode": "0x0137",
        "lane": "main",
        "direction": "s2c",
        "event_kind": "property_write",
        "record_index_in_packet": record,
        "property": "cast_command_client",
        "property_actor": ACTOR,
        "value_u_le": value,
    }


def result_event(lane: int, event_index: int, source: str, command: int) -> dict:
    return {
        "capture": "fixture.pcapng",
        "lane_index": lane,
        "lane_event_index": event_index,
        "frame_index": event_index,
        "frame_offset": event_index * 100,
        "inflated_offset": 0,
        "subevent_index": 0,
        "subevent_size": 88,
        "inner_size": 20,
        "opcode": "0x0139",
        "lane": "main",
        "direction": "s2c",
        "event_kind": "result_packet",
        "source_actor": source,
        "header": {"command_id": command, "row_count": 1},
        "rows": [{"target_actor": source, "numeric_value": 1}],
    }


class CastResultStateOrderTests(unittest.TestCase):
    def test_actor_tokens_are_capture_scoped(self):
        self.assertEqual(
            MODULE.actor_hash("a.pcapng", 7), MODULE.actor_hash("a.pcapng", 7)
        )
        self.assertNotEqual(
            MODULE.actor_hash("a.pcapng", 7), MODULE.actor_hash("b.pcapng", 7)
        )

    def test_same_packet_nonzero_then_zero_is_a_sequence(self):
        events = [
            property_event(0, 10, 0, 27346),
            property_event(0, 10, 1, 0),
        ]
        sequences = MODULE.build_sequences({"fixture.pcapng": events})
        self.assertEqual(len(sequences), 1)
        self.assertEqual(
            sequences[0]["anchor_nonzero_write"]["record_index_in_packet"], 0
        )
        self.assertEqual(sequences[0]["close_zero_write"]["record_index_in_packet"], 1)

    def test_same_packet_record_order_excludes_preceding_deadline(self):
        deadline = property_event(0, 10, 0, 7)
        deadline["property"] = "cast_end_client"
        events = [
            deadline,
            property_event(0, 10, 1, 27346),
            result_event(0, 11, ACTOR, 27346),
            property_event(0, 12, 2, 0),
        ]
        sequence = MODULE.build_sequences({"fixture.pcapng": events})[0]
        self.assertEqual(sequence["anchor_nonzero_write"]["record_index_in_packet"], 1)
        self.assertEqual(
            [
                (event["lane_event_index"], event.get("record_index_in_packet", -1))
                for event in sequence["strict_intervening_events"]
            ],
            [(11, -1)],
        )
        context = sequence["bounded_context_events"]
        self.assertEqual(context[0]["record_index_in_packet"], 0)

    def test_sequences_stay_within_reconstructed_lane(self):
        events = [
            property_event(0, 1, 1, 27346),
            property_event(1, 1, 1, 27346),
            property_event(0, 2, 0, 0),
            property_event(1, 2, 0, 0),
        ]
        sequences = MODULE.build_sequences({"fixture.pcapng": events})
        self.assertEqual([sequence["lane_index"] for sequence in sequences], [0, 1])
        self.assertTrue(
            all(sequence["capture"] == "fixture.pcapng" for sequence in sequences)
        )

    def test_matching_command_requires_source_equality_and_interval(self):
        events = [
            result_event(0, 2, OTHER_ACTOR, 27346),
            property_event(0, 10, 1, 27346),
            result_event(0, 11, ACTOR, 27346),
            property_event(0, 12, 0, 0),
        ]
        sequence = MODULE.build_sequences({"fixture.pcapng": events})[0]
        joins = sequence["bounded_result_joins"]
        self.assertEqual(len(joins), 2)
        self.assertFalse(joins[0]["matching_command_witness"])
        self.assertTrue(joins[1]["matching_command_witness"])
        self.assertEqual(sequence["bounded_command_match_count"], 1)
        self.assertEqual(sequence["bounded_command_match_actor_equal_count"], 1)

    def test_decoder_shape_guards(self):
        with self.assertRaisesRegex(ValueError, "application length"):
            MODULE.decode_mode(bytes(15))
        self.assertEqual(MODULE.decode_mode(bytes(16))["field7_u16"], 0)
        with self.assertRaisesRegex(ValueError, "rejected"):
            MODULE.decode_status(bytes(40), 71)
        self.assertEqual(MODULE.decode_status(bytes(40), 72)["nonzero_status_ids"], [])

    def test_truncated_subevent_is_counted_and_stops_lane(self):
        body = struct.pack("<HH", 2, 0) + b"\0" * 12
        frame = b"\0" * 4 + struct.pack("<HH", 16 + len(body), 0) + b"\0" * 8 + body
        original_lanes = MODULE.reconstruct_lanes
        MODULE.reconstruct_lanes = lambda _: [
            {"lane": "main", "streams": {"s2c": frame}}
        ]
        try:
            events, _counts, errors, _scenarios = MODULE.scan_capture(
                Path("fixture.pcapng"), {}, {}, {}
            )
        finally:
            MODULE.reconstruct_lanes = original_lanes
        self.assertEqual(events, [])
        self.assertEqual(errors["subevent_truncation"], 1)
        with self.assertRaisesRegex(ValueError, "parse diagnostics"):
            MODULE._reject_diagnostics({"errors": dict(errors)})


if __name__ == "__main__":
    unittest.main()
