import importlib.util
import json
import math
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "extractors" / "extract_c2s_00ca_position_report.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location(
    "extract_c2s_00ca_position_report", SCRIPT
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

STUDY = ROOT / "studies" / "c2s-00ca-position-report"
ACCOUNTING = STUDY / "derived" / "accounting.json"

# Published tables. A change to the study products has to change these too.
PUBLISHED = {
    "move_around_gridania.pcapng": {
        "records": 600,
        "move_state_counts": {"0": 24, "2": 576},
        "position_changing_total": 574,
        "position_changing_by_move_state": {"0": 1, "2": 573},
        "rotation_steps_ge_1": {"n": 279, "resultant_length": 0.993},
        "run": {"reports": 576, "duration_seconds": 104, "path_length": 502.1},
    },
    "moving_around_gridania.pcapng": {
        "records": 2402,
        "move_state_counts": {"0": 24, "2": 2378},
        "position_changing_total": 2375,
        "position_changing_by_move_state": {"0": 1, "2": 2374},
        "rotation_steps_ge_1": {"n": 1177, "resultant_length": 0.9928},
        "run": {"reports": 2378, "duration_seconds": 423, "path_length": 2081.9},
    },
}
PUBLISHED_COMBINED = {"n": 1456, "resultant_length": 0.9929, "mean_offset_rad": -0.0023}


def body(ts=100, x=0.0, y=0.0, z=0.0, rot=0.0, move_state=2, reserved=b"\0" * 6):
    data = bytearray(MODULE.BODY_LEN)
    struct.pack_into("<Q", data, MODULE.TS_PREFIX_OFFSET, ts)
    struct.pack_into("<Q", data, MODULE.TS_OFFSET, ts)
    struct.pack_into("<4f", data, MODULE.POS_OFFSET, x, y, z, rot)
    struct.pack_into("<H", data, MODULE.MOVE_STATE_OFFSET, move_state)
    data[MODULE.RESERVED_OFFSET : MODULE.BODY_LEN] = reserved
    return bytes(data)


def synthetic_run(seconds=30, per_second=5, speed=5.0, heading=0.5):
    """Straight walk at a constant speed with the rotation set to the heading."""
    dx, dz = math.sin(heading), math.cos(heading)
    step = speed / per_second
    reports = [MODULE.decode_report(body(ts=50, move_state=0))]
    for i in range(seconds * per_second):
        reports.append(
            MODULE.decode_report(
                body(
                    ts=100 + i // per_second,
                    x=dx * step * (i + 1),
                    z=dz * step * (i + 1),
                    rot=heading,
                )
            )
        )
    last = reports[-1]
    reports.append(
        MODULE.decode_report(body(ts=200, x=last["x"], z=last["z"], move_state=0))
    )
    return reports


class DecodeTests(unittest.TestCase):
    def test_decodes_fields_at_published_offsets(self):
        report = MODULE.decode_report(
            body(ts=7, x=1.5, y=2.5, z=-3.5, rot=0.25, move_state=2, reserved=b"abcdef")
        )
        self.assertEqual(report["ts"], 7)
        self.assertEqual(report["ts_prefix"], 7)
        self.assertEqual((report["x"], report["y"], report["z"]), (1.5, 2.5, -3.5))
        self.assertEqual((report["rot"], report["move_state"]), (0.25, 2))
        self.assertEqual(report["reserved"], b"abcdef")

    def test_rejects_wrong_body_length(self):
        with self.assertRaises(ValueError):
            MODULE.decode_report(bytes(MODULE.BODY_LEN - 1))


class AnalysisTests(unittest.TestCase):
    def test_straight_walk_recovers_speed_and_heading(self):
        result = MODULE.analyze_reports(synthetic_run())
        self.assertEqual(result["move_state_counts"], {"0": 2, "2": 150})
        self.assertEqual(result["position_changing_by_move_state"]["2"], 150)
        self.assertEqual(result["position_changing_by_move_state"].get("0", 0), 0)
        self.assertAlmostEqual(result["run"]["mean_speed"], 149 / 29, delta=0.01)
        self.assertEqual(result["run"]["second_bucket_speed"]["median"], 5.0)
        self.assertEqual(result["rotation"]["all_steps"]["resultant_length"], 1.0)
        self.assertAlmostEqual(
            result["rotation"]["all_steps"]["mean_offset_rad"], 0.0, places=3
        )

    def test_rotation_offset_follows_dx_dz_convention(self):
        reports = synthetic_run(heading=0.5)
        # A rotation that is the heading mirrored in x must not read as aligned.
        for report in reports:
            report["rot"] = -0.5
        stats = MODULE.analyze_reports(reports)["rotation"]["all_steps"]
        self.assertAlmostEqual(stats["mean_offset_rad"], -1.0, places=3)

    def test_offsets_wrap_across_pi(self):
        self.assertAlmostEqual(MODULE.wrap(math.pi + 0.1), -math.pi + 0.1)
        self.assertAlmostEqual(MODULE.wrap(-math.pi - 0.1), math.pi - 0.1)

    def test_percentile_is_nearest_rank(self):
        values = [float(i) for i in range(1, 101)]
        self.assertEqual(MODULE.percentile(values, 0.05), 5.0)
        self.assertEqual(MODULE.percentile(values, 0.95), 95.0)


class PublishedProductTests(unittest.TestCase):
    def setUp(self):
        self.accounting = json.loads(ACCOUNTING.read_text(encoding="ascii"))

    def test_published_tables_match_expected_figures(self):
        self.assertEqual(set(self.accounting["captures"]), set(PUBLISHED))
        for name, expected in PUBLISHED.items():
            cap = self.accounting["captures"][name]
            for key in (
                "records",
                "move_state_counts",
                "position_changing_total",
                "position_changing_by_move_state",
            ):
                self.assertEqual(cap[key], expected[key], f"{name} {key}")
            rot = cap["rotation"]["steps_ge_1"]
            for key, value in expected["rotation_steps_ge_1"].items():
                self.assertEqual(rot[key], value, f"{name} rotation {key}")
            for key, value in expected["run"].items():
                self.assertEqual(cap["run"][key], value, f"{name} run {key}")
        combined = self.accounting["combined_rotation_steps_ge_1"]
        self.assertEqual(combined, PUBLISHED_COMBINED)

    def test_move_state_values_are_exhaustive(self):
        for cap in self.accounting["captures"].values():
            self.assertEqual(set(cap["move_state_counts"]), {"0", "2"})
            self.assertEqual(sum(cap["move_state_counts"].values()), cap["records"])
            self.assertTrue(cap["run"]["all_reports_move_state_2"])

    def test_verdicts_regenerate_from_accounting(self):
        expected = MODULE.render_verdicts(self.accounting).encode("ascii")
        self.assertEqual((STUDY / "derived" / "verdicts.md").read_bytes(), expected)

    def test_readme_cites_the_published_statistics(self):
        readme = (STUDY / "README.md").read_text(encoding="ascii")
        combined = self.accounting["combined_rotation_steps_ge_1"]
        long_run = self.accounting["captures"]["moving_around_gridania.pcapng"]["run"]
        for token in (
            str(combined["n"]),
            str(combined["resultant_length"]),
            str(combined["mean_offset_rad"]),
            str(long_run["path_length"]),
            str(long_run["duration_seconds"]),
            f"{long_run['mean_speed']:.2f}",
        ):
            self.assertIn(token, readme)

    def test_public_shape_validates(self):
        self.assertEqual(MODULE.validate_public_shape(), 0)


class CaptureReplayTests(unittest.TestCase):
    def test_rederives_published_accounting_from_captures(self):
        missing = [n for n in MODULE.CAPTURES if not (MODULE.OBJECTS / n).is_file()]
        if missing:
            self.skipTest(
                "restricted Gridania captures are absent: " + ", ".join(missing)
            )
        rebuilt = MODULE.render_products(MODULE.build_accounting())
        for name, data in rebuilt.items():
            self.assertEqual(
                (STUDY / "derived" / name).read_bytes(), data, f"{name} drifted"
            )


if __name__ == "__main__":
    unittest.main()
