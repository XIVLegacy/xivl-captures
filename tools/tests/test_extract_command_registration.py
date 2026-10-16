"""Guard byte separation, bounded identifiers and retained census accounting."""

import csv
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/extractors"))
import extract_command_registration as extractor  # noqa: E402


def application(name, byte0, byte1):
    return bytes((byte0, byte1)) + name.encode("ascii").ljust(32, b"\0") + bytes(6)


class RegistrationTests(unittest.TestCase):
    def test_request_has_zero_first_byte_and_nonzero_second_byte(self):
        row = extractor.decode_application(application("commandRequest", 0, 1))
        self.assertEqual((row["byte0"], row["byte1"]), (0, 1))
        with self.assertRaisesRegex(ValueError, "byte/name"):
            extractor.decode_application(application("commandRequest", 1, 0))

    def test_forced_and_request_keep_distinct_byte_pairs(self):
        forced = extractor.decode_application(application("commandForced", 11, 0))
        request = extractor.decode_application(application("commandRequest", 0, 1))
        self.assertNotEqual(forced["application_sha256"], request["application_sha256"])
        self.assertEqual(
            forced["reserved_tail_sha256"], request["reserved_tail_sha256"]
        )

    def test_unbounded_name_or_nonzero_reserved_tail_fails(self):
        with self.assertRaisesRegex(ValueError, "name"):
            extractor.decode_application(bytes(2) + b"x" * 32 + bytes(6))
        data = bytearray(application("commandRequest", 0, 1))
        data[-1] = 1
        with self.assertRaisesRegex(ValueError, "reserved tail"):
            extractor.decode_application(data)

    def test_public_census_rejects_removed_batch_and_actor_disagreement(self):
        out = ROOT / "studies/command-registration/derived"
        outputs = {
            name: (out / name).read_bytes()
            for name in ("occurrences.csv", "accounting.json")
        }
        manifest = (ROOT / "sources/pcap-1.23b/manifest.yaml").read_bytes()
        extractor.validate_products(outputs, manifest)
        rows = list(
            csv.DictReader(io.StringIO(outputs["occurrences.csv"].decode("ascii")))
        )
        output = io.StringIO(newline="")
        writer = csv.DictWriter(
            output, fieldnames=extractor.FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows[8:])
        changed = {**outputs, "occurrences.csv": output.getvalue().encode("ascii")}
        with self.assertRaisesRegex(ValueError, "identity"):
            extractor.validate_products(changed, manifest)
        accounting = json.loads(outputs["accounting.json"])
        accounting["actor_references"][0]["c2s_0008_body0_actor_counts"] = {
            "0x00000001": 1
        }
        changed = {**outputs, "accounting.json": json.dumps(accounting).encode("ascii")}
        with self.assertRaisesRegex(ValueError, "actor-reference"):
            extractor.validate_products(changed, manifest)

    def test_public_census_rejects_changed_provenance(self):
        out = ROOT / "studies/command-registration/derived"
        outputs = {
            name: (out / name).read_bytes()
            for name in ("occurrences.csv", "accounting.json")
        }
        manifest = (ROOT / "sources/pcap-1.23b/manifest.yaml").read_bytes()
        for field, value in (
            ("source_id", "incorrect-source"),
            ("source_manifest_sha256", "0" * 64),
        ):
            with self.subTest(field=field):
                accounting = json.loads(outputs["accounting.json"])
                accounting[field] = value
                changed = {
                    **outputs,
                    "accounting.json": json.dumps(accounting).encode("ascii"),
                }
                with self.assertRaisesRegex(ValueError, "source or study identity"):
                    extractor.validate_products(changed, manifest)


if __name__ == "__main__":
    unittest.main()
