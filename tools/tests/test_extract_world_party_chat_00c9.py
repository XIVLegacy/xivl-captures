from __future__ import annotations

import base64
import copy
import csv
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
EXTRACTORS = ROOT / "tools" / "extractors"
sys.path.insert(0, str(EXTRACTORS))

import extract_world_party_chat_00c9 as study  # type: ignore  # noqa: E402


class WorldPartyChatSyntheticTests(unittest.TestCase):
    def test_synthetic_fixtures_decode(self):
        document = study._normalized_fixtures()
        self.assertEqual(document["format"], "xivl-world-party-chat-00c9-synthetic-v1")
        for fixture in document["fixtures"]:
            raw = base64.b64decode(fixture["subevent"])
            decoded = study.decode_subevent(fixture["direction"], raw)
            self.assertEqual(decoded["opcode"], 0x00C9)
            self.assertEqual(decoded["selector"], 10)
            self.assertEqual(len(raw), fixture["subevent_size"])
            if fixture["direction"] == "c2s":
                self.assertEqual(decoded["source_actor"], decoded["destination_actor"])
                self.assertNotEqual(decoded["counter"], 0)
            else:
                self.assertNotEqual(decoded["source_actor"], decoded["destination_actor"])
                self.assertEqual(decoded["counter"], 0)

    def test_decoder_rejects_selector_mutation(self):
        raw = bytearray(study._synthetic_subevent("s2c"))
        raw[24] = 11
        with self.assertRaisesRegex(ValueError, "unexpected_invariant"):
            study.decode_subevent("s2c", bytes(raw))

    def test_decoder_rejects_missing_message_terminator(self):
        raw = bytearray(study._synthetic_subevent("c2s"))
        raw[36:548] = b"x" * 512
        with self.assertRaisesRegex(ValueError, "invalid_message_missing_nul"):
            study.decode_subevent("c2s", bytes(raw))

    def test_decoder_rejects_wrong_direction_size(self):
        with self.assertRaisesRegex(ValueError, "unexpected_subevent_size"):
            study.decode_subevent("s2c", study._synthetic_subevent("c2s"))

    def test_field_matrix_covers_each_subevent_without_gaps(self):
        for direction, expected_size in (("c2s", 552), ("s2c", 584)):
            rows = [row for row in study._field_matrix() if row["direction"] == direction and row["offset_basis"] == "subevent"]
            spans = sorted((int(row["offset"]), int(row["offset"]) + int(row["width"])) for row in rows)
            cursor = 0
            for start, end in spans:
                self.assertEqual(start, cursor)
                cursor = end
            self.assertEqual(cursor, expected_size)

        contexts = {
            row["direction"]: row["observed_status"]
            for row in study._field_matrix()
            if row["field"] == "unknown_context_u32"
        }
        self.assertEqual(contexts, {"c2s": "invariant-per-corpus", "s2c": "dynamic"})

    def test_public_validator_bites_sensitive_labels(self):
        with self.assertRaisesRegex(ValueError, "forbidden sensitive label"):
            study.validate_public_bytes(b"private chat")


class WorldPartyChatSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schemas" / "world-party-chat-00c9-contract.schema.json").read_text(encoding="ascii"))
        cls.accounting = json.loads((ROOT / "studies" / study.STUDY_ID / "derived" / "accounting.json").read_text(encoding="ascii"))

    def test_accounting_schema(self):
        jsonschema.Draft202012Validator(self.schema).validate(self.accounting)

    def test_schema_rejects_direction_count_mutation(self):
        mutated = copy.deepcopy(self.accounting)
        mutated["directions"]["c2s"]["events"] = 10
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(self.schema).validate(mutated)

    def test_schema_rejects_counter_mutation(self):
        mutated = copy.deepcopy(self.accounting)
        mutated["directions"]["c2s"]["zero_counters"] = 11
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(self.schema).validate(mutated)

    def test_schema_rejects_message_overlap_mutation(self):
        mutated = copy.deepcopy(self.accounting)
        mutated["cross_capture_context"]["message_values_shared_across_directions"] = 0
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(self.schema).validate(mutated)


@unittest.skipUnless(study.default_corpus_paths(), "restricted corpus absent")
class WorldPartyChatRestrictedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = study.default_corpus_paths()
        cls.records, cls.totals, cls.per_capture = study.collect_records(cls.paths)
        cls.outputs = study.build_outputs(cls.paths)

    def test_complete_locator_coverage(self):
        study.validate_locator_coverage(self.records)

    def test_locator_mutation_bites(self):
        mutated = copy.deepcopy(self.records)
        mutated[0]["global_frame_index"] += 1
        with self.assertRaisesRegex(ValueError, "locator coverage"):
            study.validate_locator_coverage(mutated)

    def test_counter_mutation_bites(self):
        mutated = copy.deepcopy(self.records)
        next(record for record in mutated if record["direction"] == "c2s")["counter"] = 0
        with self.assertRaisesRegex(ValueError, "counter contract"):
            study.validate_observed_contract(mutated)

    def test_message_overlap_mutation_bites(self):
        mutated = copy.deepcopy(self.records)
        c2s_values = {
            record["message"]["bytes"] for record in mutated if record["direction"] == "c2s"
        }
        shared = next(
            record
            for record in mutated
            if record["direction"] == "s2c" and record["message"]["bytes"] in c2s_values
        )
        shared["message"]["bytes"] = b"synthetic-no-overlap-marker"
        with self.assertRaisesRegex(ValueError, "message overlap"):
            study.validate_observed_contract(mutated)

    def test_per_capture_context_mutation_bites(self):
        mutated = copy.deepcopy(self.records)
        alternate = next(
            record["context"]
            for record in mutated
            if record["capture"] == "war_quest_update2.pcapng" and record["direction"] == "s2c"
        )
        next(
            record
            for record in mutated
            if record["capture"] == "party_battle_leve.pcapng" and record["direction"] == "s2c"
        )["context"] = alternate
        self.assertEqual(
            len({record["context"] for record in mutated if record["direction"] == "s2c"}),
            2,
        )
        with self.assertRaisesRegex(ValueError, "per-capture context relation"):
            study.validate_observed_contract(mutated)

    def test_sender_name_class_mutation_bites(self):
        mutated = copy.deepcopy(self.records)
        target = next(record for record in mutated if record["direction"] == "s2c")
        target["name"]["bytes"] = b"x" * target["name"]["length"]
        with self.assertRaisesRegex(ValueError, "sender-name equality class"):
            study.validate_observed_contract(mutated)

    def test_outputs_match_and_do_not_leak_restricted_values(self):
        for name, rendered in self.outputs.items():
            self.assertEqual(rendered, (study.OUT / name).read_bytes())
        public = b"\n".join(self.outputs.values()).lower()
        for record in self.records:
            for value in (record["source_actor"], record["destination_actor"], record["counter"], record["context"]):
                if value:
                    self.assertNotIn(str(value).encode("ascii"), public)
                    self.assertNotIn(f"{value:08x}".encode("ascii"), public)
            if record["name"] is not None:
                self.assertNotIn(record["name"]["bytes"].lower(), public)
            if any(record["tail"]):
                self.assertNotIn(record["tail"], public)

    def test_all_message_lengths_are_value_independent(self):
        mutated = copy.deepcopy(self.records)
        values = []
        for record in mutated:
            value = record["message"]["bytes"]
            if value not in values:
                values.append(value)
        sentinels = {
            value: bytes((0x80 | (index >> 6), 0x80 | (index & 0x3f)))
            + bytes([0xfe]) * (len(value) - 2)
            for index, value in enumerate(values, 1)
        }
        for record in mutated:
            record["message"]["bytes"] = sentinels[record["message"]["bytes"]]
        with patch.object(
            study,
            "collect_records",
            return_value=(mutated, self.totals, self.per_capture),
        ):
            outputs = study.build_outputs(self.paths)
        public = b"\n".join(outputs.values())
        for sentinel in sentinels.values():
            self.assertNotIn(sentinel, public)

    def test_occurrence_rows_are_tokenized(self):
        rows = list(csv.DictReader(io.StringIO(self.outputs["occurrences.csv"].decode("ascii"))))
        self.assertEqual(len(rows), 37)
        self.assertIn("wrapper_counter_token", rows[0])
        self.assertNotIn("wrapper_counter", rows[0])


if __name__ == "__main__":
    unittest.main()
