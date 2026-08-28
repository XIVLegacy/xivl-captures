import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "extractors"))

import extract_status_wire_census as census  # noqa: E402


class StatusWireCensusTests(unittest.TestCase):
    def test_native_translation_boundary(self):
        self.assertEqual(census.decode_wire_id(0x8000), 232768)
        self.assertEqual(census.decode_wire_id(0x8001), 215537)
        self.assertEqual(census.decode_wire_id(0), 0)

    def test_projections_overlap_without_labels(self):
        self.assertEqual(census.unpack_status_word(223263), {
            "chant_kind_1": 6, "chant_kind_2": 8, "object_bits_8_11": 8,
            "object_bits_14_15": 1, "object_bits_12_13": 2,
        })

    def test_crosswalk_preserves_reverse_ambiguity(self):
        row = census._load_crosswalk(census.CROSSWALK)[223263]
        self.assertEqual(row["wire_ids"], (0x5ADF, 0x9E2F))

    def test_retransmission_overlap_is_counted(self):
        class Layer:
            src = "a"; dst = "b"; sport = 1; dport = 2; seq = 100
            payload = b"abcd"
        class Packet:
            def haslayer(self, _): return True
            def __getitem__(self, _): return Layer()
        original = census.read_packets
        census.read_packets = lambda _: [Packet(), Packet()]
        try:
            connection = {"server_endpoint": ("a", 1), "client_endpoint": ("b", 2)}
            self.assertEqual(census._raw_stream_accounting(Path("x"), connection, "s2c"), (4, 4))
        finally:
            census.read_packets = original

    def test_crosswalk_rejects_stale_projection(self):
        import tempfile
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "crosswalk.csv"
            path.write_text(
                "status_row_id,status_name,all_wire_ids_for_row_hex,chant_kind_1,chant_kind_2,object_bits_8_11,object_bits_14_15,object_bits_12_13\n"
                "223263,Resting,0x5ADF 0x9E2F,7,8,8,1,2\n", encoding="ascii")
            with self.assertRaisesRegex(ValueError, "stale chant_kind_1"):
                census._load_crosswalk(path)

    def test_malformed_status_shapes_are_excluded(self):
        valid = bytes(census.INNER_HEADER_LEN + census.GAME_PREAMBLE_SIZE + census.APPLICATION_SIZE)
        self.assertEqual(census.decode_status_ids(71, valid), (None, "unexpected_subevent_size"))
        self.assertEqual(census.decode_status_ids(72, valid[:-1]), (None, "unexpected_application_shape"))
        statuses, reason = census.decode_status_ids(72, valid)
        self.assertEqual(reason, "")
        self.assertEqual(statuses, (0,) * 20)

    def test_accounting_matches_public_schema(self):
        import json
        import jsonschema
        accounting = json.loads((census.OUT / "accounting.json").read_text(encoding="ascii"))
        schema = json.loads((ROOT / "schemas" / "status-wire-census.schema.json").read_text(encoding="ascii"))
        jsonschema.Draft202012Validator(schema).validate(accounting)

    def test_schema_rejects_sensitive_nested_field(self):
        import copy
        import json
        import jsonschema
        accounting = json.loads((census.OUT / "accounting.json").read_text(encoding="ascii"))
        schema = json.loads((ROOT / "schemas" / "status-wire-census.schema.json").read_text(encoding="ascii"))
        mutated = copy.deepcopy(accounting)
        capture = next(value for value in mutated["per_capture_chronology"].values() if value["events"])
        capture["events"][0]["endpoint"] = "forbidden"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schema).validate(mutated)

    def test_incomplete_corpus_membership_fails_closed(self):
        manifest = yaml.safe_load(census.SOURCE_MANIFEST.read_text(encoding="utf-8"))
        paths = [Path(member["file"]) for member in manifest["members"]]
        self.assertEqual(len(paths), 54)
        census.validate_corpus_paths(paths)
        with self.assertRaisesRegex(ValueError, "membership mismatch"):
            census.validate_corpus_paths(paths[:-1])


if __name__ == "__main__":
    unittest.main()
