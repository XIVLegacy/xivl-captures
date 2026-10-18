import importlib.util
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "extractors" / "extract_c2s_012d_event_start.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("extract_c2s_012d_event_start", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

STUDY = ROOT / "studies" / "c2s-012d-event-start"
ACCOUNTING = STUDY / "derived" / "accounting.json"

# Published tables. A change to the study products has to change these too.
PUBLISHED_CORPUS_SELECTORS = {
    "caution": {"2": 3},
    "commandContent": {"0": 4},
    "commandDefault": {"0": 44},
    "commandForced": {"0": 28},
    "commandJudgeMode": {"0": 5},
    "commandRequest": {"0": 19},
    "exit": {"2": 3},
    "noticeEvent": {"5": 1, "101": 1},
    "regionChange": {"2": 1},
    "talkDefault": {"1": 16, "101": 1},
}
PUBLISHED_SAMPLE_TALK = {"1": 14}
PUBLISHED_SAMPLE_PUSH = 5
PUBLISHED_SAMPLE_COMMAND = 41
PUBLISHED_TARGETS = {
    "selector 1": {
        "messages": 16,
        "lock_since_previous_start": 16,
        "lock_immediately_before": 16,
        "lock_actor_equals_owner": 16,
        "set_since_previous_start": 13,
        "set_actor_equals_owner": 13,
        "set_before_lock": 13,
    },
    "selector 101": {
        "messages": 1,
        "lock_since_previous_start": 0,
        "set_since_previous_start": 1,
    },
}
PUBLISHED_CAPTURES = 39
PUBLISHED_MESSAGES = 126


def start_message(name="talkDefault", selector=1, owner=7, zone=150, low=0):
    data = bytearray(MODULE.START_LEN)
    struct.pack_into("<I", data, MODULE.OWNER_OFFSET, owner)
    struct.pack_into("<I", data, MODULE.SERVER_CODES_OFFSET, (zone << 22) | low)
    data[MODULE.SELECTOR_OFFSET] = selector
    raw = name.encode("ascii")
    data[MODULE.NAME_OFFSET : MODULE.NAME_OFFSET + len(raw)] = raw
    return bytes(data)


def target_message(actor, other=0):
    data = bytearray(MODULE.TARGET_LEN)
    struct.pack_into("<II", data, MODULE.TARGET_ACTOR_OFFSET, actor, other)
    return bytes(data)


class DecodeTests(unittest.TestCase):
    def test_decodes_fields_at_published_offsets(self):
        start = MODULE.decode_start(start_message("exit", 2, owner=9, zone=155, low=3))
        self.assertEqual(
            (start["name"], start["selector"], start["owner"]), ("exit", 2, 9)
        )
        self.assertEqual(MODULE.split_codes(start["server_codes"]), (155, 3))

    def test_rejects_wrong_length_and_non_identifier_name(self):
        with self.assertRaises(ValueError):
            MODULE.decode_start(bytes(MODULE.START_LEN - 1))
        with self.assertRaises(ValueError):
            MODULE.decode_start(start_message("bad name"))
        with self.assertRaises(ValueError):
            MODULE.decode_target(bytes(MODULE.TARGET_LEN + 1))


class JoinTests(unittest.TestCase):
    def test_target_window_resets_at_each_start(self):
        sequence = [
            (MODULE.OPCODE_SET, target_message(7, MODULE.CLEAR_SENTINEL)),
            (0x00CA, b""),
            (MODULE.OPCODE_LOCK, target_message(7)),
            (MODULE.OPCODE_START, start_message(owner=7)),
            (MODULE.OPCODE_START, start_message(selector=101, owner=7)),
        ]
        first, second = MODULE.find_starts(sequence)
        self.assertEqual(first["lock_gap"], 1)
        self.assertTrue(first["set_before_lock"])
        self.assertIsNone(second["lock"])
        self.assertIsNone(second["set"])

    def test_target_summary_classes_second_dwords(self):
        sequence = [
            (MODULE.OPCODE_SET, target_message(7, MODULE.CLEAR_SENTINEL)),
            (MODULE.OPCODE_LOCK, target_message(7, 5)),
            (MODULE.OPCODE_START, start_message(owner=7)),
        ]
        summary = MODULE.target_summary(MODULE.find_starts(sequence))["selector 1"]
        self.assertEqual(summary["lock_second_dword"], {"other": 1})
        self.assertEqual(summary["set_second_dword"], {"0xe0000000": 1})
        self.assertEqual(summary["lock_actor_equals_owner"], 1)

    def test_summary_counts_name_selector_and_low_bits(self):
        starts = [
            dict(MODULE.decode_start(start_message(low=0))),
            dict(MODULE.decode_start(start_message(name="exit", selector=2, low=60))),
        ]
        summary = MODULE.summarize(starts)
        self.assertEqual(summary["server_codes_low22_nonzero"], 1)
        self.assertEqual(summary["selector_by_event_name"]["exit"], {"2": 1})

    def test_sampler_reproduction_caps_per_capture_and_overall(self):
        starts = [{"n": i} for i in range(10)]
        picked = MODULE.published_sample_picks([("a", starts), ("b", starts)])
        self.assertEqual(len(picked), 2 * MODULE.SAMPLE_CAPTURE_CAP)


class PublishedProductTests(unittest.TestCase):
    def setUp(self):
        self.accounting = json.loads(ACCOUNTING.read_text(encoding="ascii"))

    def test_published_corpus_tables_match_expected_figures(self):
        corpus = self.accounting["corpus"]
        self.assertEqual(corpus["messages"], PUBLISHED_MESSAGES)
        self.assertEqual(len(self.accounting["captures"]), PUBLISHED_CAPTURES)
        self.assertEqual(corpus["selector_by_event_name"], PUBLISHED_CORPUS_SELECTORS)
        self.assertEqual(corpus["server_codes_low22_nonzero"], 9)

    def test_published_sample_tables_match_expected_figures(self):
        samples = self.accounting["published_samples"]
        by_name = samples["selector_by_event_name"]
        self.assertEqual(samples["messages"], 60)
        self.assertEqual(by_name["talkDefault"], PUBLISHED_SAMPLE_TALK)
        push = sum(by_name[n]["2"] for n in ("caution", "exit", "regionChange"))
        command = sum(c["0"] for n, c in by_name.items() if n.startswith("command"))
        self.assertEqual(push, PUBLISHED_SAMPLE_PUSH)
        self.assertEqual(command, PUBLISHED_SAMPLE_COMMAND)
        self.assertEqual(samples["server_codes_low22_nonzero"], 0)

    def test_sample_joins_follow_published_sample_order(self):
        joins = self.accounting["published_samples"]["sample_joins"]
        self.assertEqual([row["index"] for row in joins], list(range(60)))
        talk = [row for row in joins if row["event_name"] == "talkDefault"]
        self.assertEqual(len(talk), 14)
        self.assertEqual({row["selector"] for row in talk}, {1})
        self.assertEqual({row["low22"] for row in joins}, {0})

    def test_sample_join_drift_is_rejected(self):
        samples = json.loads(json.dumps(self.accounting["published_samples"]))
        MODULE.check_sample_joins(samples)
        samples["sample_joins"][0]["selector"] ^= 1
        with self.assertRaises(ValueError):
            MODULE.check_sample_joins(samples)

    def test_published_target_counts_match_expected_figures(self):
        for label, expected in PUBLISHED_TARGETS.items():
            actual = self.accounting["targets"][label]
            for key, value in expected.items():
                self.assertEqual(actual[key], value, f"{label} {key}")

    def test_joins_sum_to_message_counts(self):
        for key in ("corpus", "published_samples"):
            summary = self.accounting[key]
            self.assertEqual(
                sum(row["count"] for row in summary["joins"]), summary["messages"]
            )

    def test_verdicts_regenerate_from_accounting(self):
        expected = MODULE.render_verdicts(self.accounting).encode("ascii")
        self.assertEqual((STUDY / "derived" / "verdicts.md").read_bytes(), expected)

    def test_readme_cites_the_published_figures(self):
        readme = (STUDY / "README.md").read_text(encoding="ascii")
        for token in (
            "126 messages in 39 captures",
            "16 of 17",
            "7 of 7",
            "100 of 100",
        ):
            self.assertIn(token, readme)
        for token in ("14 of 14", "5 of 5", "41 of 41", "117 of the 126"):
            self.assertIn(token, readme)

    def test_public_shape_validates(self):
        self.assertEqual(MODULE.validate_public_shape(), 0)


class CaptureReplayTests(unittest.TestCase):
    def test_rederives_published_accounting_from_captures(self):
        members = MODULE.load_manifest_members()
        missing = [n for n in members if not (MODULE.OBJECTS / n).is_file()]
        if missing:
            self.skipTest(f"restricted captures are absent: {len(missing)} files")
        rebuilt = MODULE.render_products(MODULE.build_accounting())
        for name, data in rebuilt.items():
            self.assertEqual(
                (STUDY / "derived" / name).read_bytes(), data, f"{name} drifted"
            )


if __name__ == "__main__":
    unittest.main()
