import unittest

from tools.extractors.extract_local_guildleve_dialogue import (
    delegate_prefix_string,
)


class DelegatePrefixCensusTest(unittest.TestCase):
    def test_command_and_event_use_distinct_string_positions(self):
        command = bytes.fromhex("06 01020304 02") + b"confirmLeve\0"
        event = bytes.fromhex("06 01020304 06 05060708 02") + b"processPgEvent\0"
        self.assertEqual(
            delegate_prefix_string("delegateCommand", command.ljust(64, b"\0")),
            "confirmLeve",
        )
        self.assertEqual(
            delegate_prefix_string("delegateEvent", event.ljust(64, b"\0")),
            "processPgEvent",
        )
        with self.assertRaisesRegex(ValueError, "actor"):
            delegate_prefix_string("delegateEvent", command.ljust(64, b"\0"))
        with self.assertRaisesRegex(ValueError, "string"):
            delegate_prefix_string("delegateCommand", event.ljust(64, b"\0"))

    def test_later_tag_does_not_remove_a_valid_prefix(self):
        # Model the later tag 3 in return_to_inn.pcapng main s2c frame 6/subevent 1.
        parameters = (
            bytes.fromhex("06 01020304 02") + b"eventConfirm\0\x03\x0f"
        ).ljust(64, b"\0")
        self.assertEqual(
            delegate_prefix_string("delegateCommand", parameters), "eventConfirm"
        )

    def test_incomplete_or_unsupported_prefix_fails(self):
        valid = (bytes.fromhex("06 01020304 02") + b"init\0").ljust(64, b"\0")
        for parameters in (valid[:-1], valid + b"\0"):
            with self.subTest(size=len(parameters)):
                with self.assertRaisesRegex(ValueError, "exactly 64"):
                    delegate_prefix_string("delegateCommand", parameters)
        malformed = [
            (bytes.fromhex("00 01020304 02") + b"init\0").ljust(64, b"\0"),
            (bytes.fromhex("06 01020304 05") + b"init\0").ljust(64, b"\0"),
            bytes.fromhex("06 01020304 02") + b"x" * 58,
            (bytes.fromhex("06 01020304 02 ff 00")).ljust(64, b"\0"),
        ]
        for parameters in malformed:
            with self.subTest(prefix=parameters[:6].hex()):
                with self.assertRaises(ValueError):
                    delegate_prefix_string("delegateCommand", parameters)
        with self.assertRaisesRegex(ValueError, "unsupported delegate"):
            delegate_prefix_string("other", valid)


if __name__ == "__main__":
    unittest.main()
