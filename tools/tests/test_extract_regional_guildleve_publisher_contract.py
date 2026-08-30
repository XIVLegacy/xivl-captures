import unittest

from tools.extractors.extract_regional_guildleve_publisher_contract import (
    PROPERTY_NAMES,
    _acceptance_fields,
    decode_lua_values,
    order_rows,
)


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

    def test_lua_values_decode_known_scalar_tags(self):
        values, unsupported = decode_lua_values(bytes.fromhex(
            "00 000030c3 03 04 05 0f"
        ))
        self.assertEqual(values, [
            "int:12483", "bool:true", "bool:false", "nil",
        ])
        self.assertIsNone(unsupported)

    def test_lua_values_decode_actor_reference(self):
        values, unsupported = decode_lua_values(bytes.fromhex("06 029b2941 0f"))
        self.assertEqual(values, ["actor:43723073"])
        self.assertIsNone(unsupported)

    def test_lua_values_preserve_unsupported_tag_boundary(self):
        values, unsupported = decode_lua_values(bytes.fromhex("03 02"))
        self.assertEqual(values, ["bool:true"])
        self.assertEqual(unsupported, 0x02)

    def test_lua_values_reject_truncated_integer(self):
        with self.assertRaisesRegex(ValueError, "truncated Lua integer"):
            decode_lua_values(bytes.fromhex("00 000030"))

    def test_lua_values_require_terminator(self):
        with self.assertRaisesRegex(ValueError, "no terminator"):
            decode_lua_values(bytes.fromhex("03"))

    def test_promoted_property_hashes_are_fixed(self):
        self.assertEqual(PROPERTY_NAMES, {
            "0x19030954": "work.guildleveId[3]",
            "0xb4f4e4ca": "work.guildleveId[4]",
            "0x3e8a7bb7": "playerWork.questGuildleve[0]",
            "0x4f5efe11": "work.guildleveId[8]",
        })

    def test_run_event_owner_rejects_drift(self):
        app = bytearray(0x4A)
        app[4:8] = (0x44D8000B).to_bytes(4, "little")
        app[0x29:0x36] = b"eventTalkType"
        app[0x49] = 0x0F
        event = {"opcode_value": 0x0130, "frame_index": 11}
        spec = {"owner": 0x44D8000A, "functions": {11: "eventTalkType"}}
        with self.assertRaisesRegex(ValueError, "unexpected RunEvent owner"):
            _acceptance_fields("mutated-owner", event, bytes(app), spec)


if __name__ == "__main__":
    unittest.main()
