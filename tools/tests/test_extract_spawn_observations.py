import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from tools.extractors import extract_spawn_observations as spawn


class SpawnObservationsCsvTest(unittest.TestCase):
    def setUp(self):
        self.records = [
            {
                "capture": "a.pcapng",
                "actorId": "0x00000001",
                "instanceName": "",
                "baseClass": "",
                "classPath": "",
                "zoneTag": "",
                "x": 1.2,
                "y": -0.0,
                "z": 3.456,
                "rotation": -1.0,
                "hadInstantiate": False,
                "hadAddActor": True,
            }
        ]

    def test_render_has_stable_header_values_and_lf(self):
        rendered = spawn.render_csv(self.records)
        self.assertNotIn(b"\r", rendered)
        rows = list(csv.reader(io.StringIO(rendered.decode("utf-8"), newline="")))
        self.assertEqual(rows[0], list(spawn.RECORD_FIELDS))
        self.assertEqual(rows[1][6:], ["1.200", "-0.000", "3.456", "-1.0000", "false", "true"])

    def test_validate_csv_matches_json_order_and_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            json_path = root / "spawn_observations.json"
            csv_path = root / "spawn_observations.csv"
            json_path.write_text(json.dumps({"records": self.records}), encoding="utf-8")
            csv_path.write_bytes(spawn.render_csv(self.records))
            self.assertEqual(spawn.validate_csv(json_path, csv_path), [])

            csv_path.write_bytes(spawn.render_csv(self.records).replace(b"a.pcapng", b"b.pcapng"))
            self.assertTrue(spawn.validate_csv(json_path, csv_path))


if __name__ == "__main__":
    unittest.main()
