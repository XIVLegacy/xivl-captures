from __future__ import annotations

import copy
import json
import unittest

import jsonschema

from tools.extractors.extract_lobby_record_census import OUTPUT, REPO_ROOT, validate_fixture


class LobbyRecordCensusTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_committed_fixture_is_valid(self):
        validate_fixture(self.fixture)

    def test_rejects_shifted_stream_offset(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["sessions"][1]["directions"][1]["frames"][3]["subrecords"][2]["streamOffset"] += 1
        with self.assertRaisesRegex(ValueError, "stream offset changed"):
            validate_fixture(mutated)

    def test_rejects_removed_subrecord(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["sessions"][1]["directions"][1]["frames"][3]["subrecords"].pop()
        with self.assertRaisesRegex(ValueError, "census changed"):
            validate_fixture(mutated)

    def test_rejects_changed_inner_opcode(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["sessions"][1]["directions"][1]["frames"][4]["subrecords"][0]["innerOpcode"] += 1
        with self.assertRaisesRegex(ValueError, "census changed"):
            validate_fixture(mutated)

    def test_rejects_shifted_encrypted_extent(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["sessions"][0]["directions"][1]["frames"][1]["subrecords"][0]["encryptedExtent"]["offset"] += 8
        with self.assertRaisesRegex(ValueError, "encrypted extent changed"):
            validate_fixture(mutated)

    def test_rejects_changed_shared_correspondence(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["crossSession"]["sharedFrameShapes"][0]["occurrences"][1]["sessionId"] = "session-1"
        with self.assertRaisesRegex(ValueError, "does not cover both sessions"):
            validate_fixture(mutated)

    def test_rejects_sensitive_address(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["redactedClasses"][0] = ".".join(("192", "0", "2", "1"))
        with self.assertRaisesRegex(ValueError, "IPv4 address"):
            validate_fixture(mutated)

    def test_rejects_token_like_hex(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["redactedClasses"][0] = "a" * 64
        with self.assertRaisesRegex(ValueError, "token-like"):
            validate_fixture(mutated)

    def test_rejects_c0_control(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["redactedClasses"][0] = "bad\x01value"
        with self.assertRaisesRegex(ValueError, "C0"):
            validate_fixture(mutated)

    def test_rejects_non_ascii(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["redactedClasses"][0] = "bad\N{EM DASH}value"
        with self.assertRaisesRegex(ValueError, "non-ASCII"):
            validate_fixture(mutated)

    def test_schema_rejects_injected_plaintext(self):
        mutated = copy.deepcopy(self.fixture)
        record = mutated["sessions"][0]["directions"][0]["frames"][0]["subrecords"][0]
        record["plaintext"] = "private"
        schema = json.loads(
            (REPO_ROOT / "schemas/lobby-record-census.schema.json").read_text(encoding="utf-8")
        )
        errors = list(jsonschema.Draft202012Validator(schema).iter_errors(mutated))
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
