from __future__ import annotations

import copy
import json
import unittest

from tools.extractors.extract_lobby_acknowledgement_schema import OUTPUT, validate_fixture


class LobbyAcknowledgementFixtureTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_committed_fixture_is_valid(self):
        validate_fixture(self.fixture)

    def test_rejects_shifted_payload_boundary(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["record"]["encryptedPayload"]["offset"] += 8
        with self.assertRaisesRegex(ValueError, "boundary shifted"):
            validate_fixture(mutated)

    def test_rejects_changed_invariant_marker(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["record"]["outerHeader"]["markerHex"] = "01000000"
        with self.assertRaisesRegex(ValueError, "header changed"):
            validate_fixture(mutated)

    def test_rejects_sensitive_address(self):
        mutated = copy.deepcopy(self.fixture)
        mutated["redactedClasses"][0] = "192.0.2.1"
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


if __name__ == "__main__":
    unittest.main()
