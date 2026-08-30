import unittest

from tools.extractors.extract_regional_guildleve_publisher_contract import order_rows


class RegionalGuildlevePublisherContractTest(unittest.TestCase):
    def test_timeline_preserves_frame_order_within_capture_packet(self):
        rows = [
            {"stage": "event-retirement", "capture_packet_index": 5444,
             "frame_stream_offset": 426300, "subevent_offset": 0, "direction": "s2c"},
            {"stage": "content-group-retirement-4", "capture_packet_index": 5444,
             "frame_stream_offset": 426046, "subevent_offset": 144, "direction": "s2c"},
            {"stage": "content-group-retirement-7", "capture_packet_index": 5444,
             "frame_stream_offset": 426046, "subevent_offset": 80, "direction": "s2c"},
        ]
        order_rows(rows)
        self.assertEqual([row["stage"] for row in rows], [
            "content-group-retirement-7",
            "content-group-retirement-4",
            "event-retirement",
        ])


if __name__ == "__main__":
    unittest.main()
