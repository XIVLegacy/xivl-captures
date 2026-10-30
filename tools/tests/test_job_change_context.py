import importlib.util
import copy
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "extractors" / "extract_job_change_context.py"
SPEC = importlib.util.spec_from_file_location("extract_job_change_context", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

PRODUCT = (
    ROOT / "studies" / "c2s-012d-event-start" / "derived" / "job-change-context.json"
)


class SelectorTests(unittest.TestCase):
    def test_packed_predicate_keeps_middle_bits(self):
        self.assertTrue(MODULE.packed_selector(0x04000030))
        self.assertTrue(MODULE.packed_selector(0x04001030))
        self.assertTrue(MODULE.packed_selector(0x040FF030))
        self.assertFalse(MODULE.packed_selector(0x04000029))


class TailTests(unittest.TestCase):
    def test_witness_tail_is_integer_eight_nils_and_terminator(self):
        data = bytes([0, 0, 0, 0, 1, *([5] * 8), 0x0F])
        self.assertEqual(
            MODULE.typed_tail(data),
            [
                {"tail_offset": 0, "type": "int", "value": 1},
                *[{"tail_offset": offset, "type": "nil"} for offset in range(5, 13)],
                {"tail_offset": 13, "type": "terminator"},
            ],
        )

    def test_handle_bearing_tail_is_out_of_scope(self):
        with self.assertRaisesRegex(ValueError, "unsupported 12017"):
            MODULE.typed_tail(bytes([0x07]))


class ActorEqualityTests(unittest.TestCase):
    def test_matching_pairs_do_not_imply_all_four_equal(self):
        pair = {"_source_actor": 1, "_destination_actor": 2}
        self.assertFalse(MODULE.all_actor_fields_equal(pair, pair))
        equal = {"_source_actor": 1, "_destination_actor": 1}
        self.assertTrue(MODULE.all_actor_fields_equal(equal, equal))


class ProductTests(unittest.TestCase):
    def test_request_job_witness_mutations_are_rejected(self):
        product = json.loads(PRODUCT.read_text(encoding="ascii"))
        MODULE.validate_request_job_context(product)
        mutations = (
            ("request", "retained request identity changed"),
            ("job", "retained job anchor changed"),
            ("pair", "retained request/job relation changed"),
            ("summary", "summaries disagree"),
        )
        for kind, reason in mutations:
            changed = copy.deepcopy(product)
            if kind == "request":
                changed["requests"][0]["event_name"] = "wrongEvent"
            elif kind == "job":
                anchor = next(
                    row for row in changed["job_contexts"] if row["candidate_neighbors"]
                )
                anchor["job_byte"] = 0
            elif kind == "pair":
                changed["request_job_pairs"][0]["all_four_actor_fields_equal"] = False
            else:
                changed["summary"]["request_job_pair_count"] = 2
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, reason):
                MODULE.validate_request_job_context(changed)

    def test_public_shape_and_sanitization(self):
        self.assertEqual(MODULE.validate_public_shape(), 0)
        product = json.loads(PRODUCT.read_text(encoding="ascii"))
        text = json.dumps(product, sort_keys=True)
        for forbidden in ("actor_id", "endpoint", "payload_hex", "_source_actor"):
            self.assertNotIn(forbidden, text)
        self.assertEqual(len(product["requests"]), 1)
        self.assertEqual(product["requests"][0]["application_04_low16"], 12017)
        self.assertEqual(product["summary"]["request_job_pairs_all_four_equal"], 1)
        self.assertEqual(product["selector_search"]["truncated_subevents"], 0)


if __name__ == "__main__":
    unittest.main()
