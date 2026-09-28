import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "extractors"))

import extract_login_018a_timeline as timeline  # noqa: E402


def event(opcode: int, lane_index: int, lane: str, direction: str, index: int) -> dict:
    return {
        "opcode": opcode,
        "lane_index": lane_index,
        "lane": lane,
        "direction": direction,
        "direction_event_index": index,
    }


class Login018ATimelineTests(unittest.TestCase):
    def test_window_never_crosses_connection_or_direction(self):
        previous = event(0x0137, 0, "main", "s2c", 10)
        anchor = event(0x018A, 0, "main", "s2c", 11)
        following = event(0x0189, 0, "main", "s2c", 12)
        mixed = [
            event(0xDEAD, 1, "chat", "s2c", 0),
            previous,
            event(0xBEEF, 0, "main", "c2s", 0),
            anchor,
            event(0xCAFE, 1, "chat", "s2c", 1),
            following,
        ]
        selected = timeline.select_anchor(mixed)
        window = timeline.same_lane_window(mixed, selected, before=1, after=1)
        self.assertEqual([row["opcode"] for row in window], [0x0137, 0x018A, 0x0189])

    def test_wrong_lane_anchor_is_rejected(self):
        events = [event(0x018A, 1, "chat", "s2c", 0)]
        with self.assertRaisesRegex(ValueError, "not on the main s2c lane"):
            timeline.select_anchor(events)

    def test_retransmit_cannot_replace_first_frame_witness(self):
        spans = [
            {"start": 100, "end": 200, "packet_index": 9, "capture_time_us": 900},
            {"start": 100, "end": 200, "packet_index": 4, "capture_time_us": 400},
        ]
        witness = timeline._frame_packet(120, 40, spans)
        self.assertEqual(witness["packet_index"], 4)
        self.assertEqual(witness["candidate_packet_indexes"], [4, 9])

    def test_fragmented_frame_uses_completion_witness(self):
        spans = [
            {"start": 100, "end": 140, "packet_index": 4, "capture_time_us": 400},
            {"start": 140, "end": 180, "packet_index": 6, "capture_time_us": 600},
        ]
        witness = timeline._frame_packet(120, 40, spans)
        self.assertEqual(witness["start_packet_index"], 4)
        self.assertEqual(witness["packet_index"], 6)


if __name__ == "__main__":
    unittest.main()
