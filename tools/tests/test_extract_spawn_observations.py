import csv
import io
import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.extractors import extract_spawn_observations as spawn


def _record(opcode, source_actor_id, clock, body=b""):
    payload = bytes(8) + struct.pack("<I", clock) + body
    return {
        "direction": "s2c",
        "opcode": opcode,
        "source_actor_id": source_actor_id,
        "bytes": payload.hex(),
    }


def _position(source_actor_id, clock, x):
    body = bytes(12) + struct.pack("<ffff", x, 2.0, 3.0, 0.5)
    return _record(spawn.OP_POS, source_actor_id, clock, body)


def _instance(source_actor_id, clock, name):
    body = b"\0" + name.encode() + b"\0Base\0/Chara/Npc/Base\0"
    return _record(spawn.OP_INST, source_actor_id, clock, body)


class SpawnObservationsJoinTest(unittest.TestCase):
    def walk(self, records):
        with mock.patch.object(spawn, "walk_capture_payloads", lambda _: records):
            return {row["actorId"]: row for row in spawn.walk_capture_spawns(Path("a"))}

    def test_shared_clock_does_not_merge_source_actors(self):
        rows = self.walk(
            [
                _position(1, 0x50E0E838, 10.0),
                _position(2, 0x50E0E838, 20.0),
                _instance(1, 0x50E0E838, "alpha"),
                _instance(2, 0x50E0E838, "bravo"),
            ]
        )
        self.assertEqual(sorted(rows), ["0x00000001", "0x00000002"])
        self.assertEqual(rows["0x00000001"]["x"], 10.0)
        self.assertEqual(rows["0x00000001"]["instanceName"], "alpha")
        self.assertEqual(rows["0x00000002"]["x"], 20.0)
        self.assertEqual(rows["0x00000002"]["instanceName"], "bravo")

    def test_changing_clock_joins_one_source_actor(self):
        rows = self.walk(
            [
                _record(spawn.OP_ADD, 1, 100),
                _position(1, 101, 10.0),
                _position(1, 102, 99.0),
                _instance(1, 103, "@$alpha"),
                _instance(1, 104, "bravo"),
            ]
        )
        self.assertEqual(list(rows), ["0x00000001"])
        row = rows["0x00000001"]
        self.assertTrue(row["hadAddActor"])
        self.assertTrue(row["hadInstantiate"])
        self.assertEqual(row["x"], 10.0)
        self.assertEqual(row["instanceName"], "alpha")


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
        self.assertEqual(
            rows[1][6:], ["1.200", "-0.000", "3.456", "-1.0000", "false", "true"]
        )

    def test_validate_csv_matches_json_order_and_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            json_path = root / "spawn_observations.json"
            csv_path = root / "spawn_observations.csv"
            json_path.write_text(
                json.dumps({"records": self.records}), encoding="utf-8"
            )
            csv_path.write_bytes(spawn.render_csv(self.records))
            self.assertEqual(spawn.validate_csv(json_path, csv_path), [])

            csv_path.write_bytes(
                spawn.render_csv(self.records).replace(b"a.pcapng", b"b.pcapng")
            )
            self.assertTrue(spawn.validate_csv(json_path, csv_path))


if __name__ == "__main__":
    unittest.main()
