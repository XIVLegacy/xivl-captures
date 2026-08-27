import json
import math
import struct
import sys
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_party_marker_fields as census  # noqa: E402


class PartyMarkerFieldCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = json.loads(
            (census.OUT / "field-census.json").read_text(encoding="ascii")
        )
        cls.schema = json.loads(
            (ROOT / "schemas" / "party-marker-field-census.schema.json").read_text(
                encoding="ascii"
            )
        )

    def test_accounting_matches_public_schema(self):
        jsonschema.Draft202012Validator(self.schema).validate(self.product)

    def test_schema_rejects_sensitive_nested_field(self):
        mutated = json.loads(json.dumps(self.product))
        mutated["sanitized_timing"]["timestamp"] = 1
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(self.schema).validate(mutated)

    def test_integer_profile_preserves_signed_and_unsigned_views(self):
        profile = census._integer_profile([0, 0x7F, 0x80, 0xFF], 1, 0)
        self.assertEqual(profile["all_ones_sentinel_count"], 1)
        self.assertEqual(profile["signed_sign_distribution"], {
            "negative": 2, "zero": 1, "positive": 1,
        })
        self.assertEqual(profile["unsigned_value_distribution"], {
            "0": 1, "127": 1, "128": 1, "255": 1,
        })

    def test_float_profile_counts_nonfinite_mutations(self):
        rows = []
        for value in (0.0, -0.0, math.inf, -math.inf, math.nan):
            row = bytearray(40)
            struct.pack_into("<f", row, 0x14, value)
            rows.append(bytes(row))
        profile = census._float_profile(rows, 0x14)
        self.assertEqual(profile["finite"], 2)
        self.assertEqual(profile["positive_infinity"], 1)
        self.assertEqual(profile["negative_infinity"], 1)
        self.assertEqual(profile["nan"], 1)
        self.assertEqual(profile["positive_zero"], 1)
        self.assertEqual(profile["negative_zero"], 1)

    def test_profiles_cover_every_aligned_record_view(self):
        profiles = self.product["integer_profiles"]
        self.assertEqual(CounterByWidth(profiles), {1: 40, 2: 20, 4: 10})
        self.assertEqual([row["offset"] for row in self.product["float_profiles"]], [
            "+0x14", "+0x18", "+0x1c", "+0x20",
        ])

    def test_inactive_rows_and_tail_are_zero(self):
        shape = self.product["count_and_tail"]
        self.assertEqual(shape["inactive_physical_rows"], 8703)
        self.assertEqual(shape["inactive_nonzero_rows"], 0)
        self.assertEqual(shape["nonzero_tail_samples"], 0)

    def test_public_product_rejects_endpoint_and_raw_id_mutations(self):
        with self.assertRaisesRegex(ValueError, "IPv4-like"):
            census.validate_public_product(b"203.0.113.10")
        with self.assertRaisesRegex(ValueError, "32-bit"):
            census.validate_public_product(b"0x1234abcd")
        with self.assertRaisesRegex(ValueError, "credential-like"):
            census.validate_public_product(b"authorization token")


def CounterByWidth(profiles):
    result = {}
    for profile in profiles:
        width = profile["width"]
        result[width] = result.get(width, 0) + 1
    return result


if __name__ == "__main__":
    unittest.main()
