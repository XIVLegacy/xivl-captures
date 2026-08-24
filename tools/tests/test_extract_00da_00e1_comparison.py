import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "extractors"))

import extract_00da_00e1_comparison as comparison  # noqa: E402


def event(index: int, opcode: int | None, lane: int = 0, direction: str = "s2c") -> dict:
    return {
        "capture": "capture.pcapng",
        "lane_index": lane,
        "lane": "main" if lane == 0 else "chat",
        "direction": direction,
        "direction_event_index": index,
        "frame_index": index,
        "subevent_index": 0,
        "subevent_offset": 0,
        "subevent_type": 3,
        "opcode_value": opcode,
        "transport_source_actor_id": 1,
        "transport_target_actor_id": 2,
        "capture_time_us": index * 100,
        "outer_value": index * 10,
    }


class ComparisonTests(unittest.TestCase):
    def test_completion_uses_first_full_frame_witness(self):
        spans = [
            {"start": 100, "end": 140, "packet_index": 7, "capture_time_us": 700},
            {"start": 140, "end": 180, "packet_index": 9, "capture_time_us": 900},
            {"start": 100, "end": 180, "packet_index": 12, "capture_time_us": 1200},
        ]
        self.assertEqual(comparison._frame_completion(120, 40, spans)["packet_index"], 9)

    def test_completion_rejects_missing_frame_bytes(self):
        spans = [{"start": 100, "end": 139, "packet_index": 7, "capture_time_us": 700}]
        with self.assertRaisesRegex(ValueError, "do not complete frame"):
            comparison._frame_completion(100, 40, spans)

    def test_neighbors_do_not_cross_connection_or_direction(self):
        previous = event(0, 0x0001)
        anchor = event(1, 0x00DA)
        following = event(2, 0x0130)
        mixed = [
            event(0, 0xDEAD, lane=1), previous,
            event(0, 0xBEEF, direction="c2s"), anchor, following,
        ]
        rows = comparison._neighbors(mixed, [anchor])
        self.assertEqual([row["neighbor_opcode"] for row in rows], ["0x0001", "0x0130"])

    def test_word_vectors_are_little_endian_and_bounded(self):
        self.assertEqual(comparison._word_vector(bytes.fromhex("01000200"), 2), "0x0001 0x0002")
        self.assertEqual(comparison._word_vector(b"\x01\x02\x03", 2), "")


if __name__ == "__main__":
    unittest.main()
