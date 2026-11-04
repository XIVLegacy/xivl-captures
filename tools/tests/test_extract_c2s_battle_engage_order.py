import importlib.util
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "extractors" / "extract_c2s_battle_engage_order.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("extract_c2s_battle_engage_order", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

STUDY = ROOT / "studies" / "c2s-battle-engage-order"
ACCOUNTING = STUDY / "derived" / "accounting.json"

PLAYER = 0x11110001
MONSTER = 0x22220002
NPC = 0x33330003
MODE_TAIL = bytes.fromhex("050500000000010505050505050f")


def target(actor, second):
    return struct.pack("<II", actor, second)


def start(owner, name, selector=0, tail=MODE_TAIL):
    app = bytearray(184)
    struct.pack_into("<II", app, 0, PLAYER, owner)
    app[0x10] = selector
    app[0x11 : 0x11 + len(name)] = name.encode("ascii")
    app[0x31 : 0x31 + len(tail)] = tail
    return bytes(app)


def end_event(name):
    app = bytearray(48)
    struct.pack_into("<I", app, 0, PLAYER)
    app[9 : 9 + len(name)] = name.encode("ascii")
    return bytes(app)


def result(command, first_target):
    app = bytearray(88)
    struct.pack_into("<I", app, 0, PLAYER)
    struct.pack_into("<H", app, 0x24, command)
    struct.pack_into("<I", app, 0x28, first_target)
    return bytes(app)


def rec(direction, frame, sub, packet, ms, op, app):
    return {
        "lane": 0,
        "direction": direction,
        "frame": frame,
        "sub": sub,
        "packet": packet,
        "time_us": ms * 1000,
        "src": PLAYER,
        "op": op,
        "app": app,
    }


def engage_capture():
    """Mode on, select, lock and decide, attack, clear, mode off."""
    return [
        rec("c2s", 0, 0, 1, 0, 0x012D, start(0xA0F05209, "commandForced")),
        rec("s2c", 0, 0, 2, 560, 0x0134, bytes([2, 0xBF]) + bytes(6)),
        rec("s2c", 0, 1, 2, 560, 0x0139, result(21001, PLAYER)),
        rec("s2c", 0, 2, 2, 560, 0x0131, end_event("commandForced")),
        rec("c2s", 1, 0, 3, 1000, 0x00CD, target(MONSTER, 0xE0000000)),
        rec("c2s", 2, 0, 4, 1365, 0x00CC, target(MONSTER, 0x0466E6A4)),
        rec("c2s", 2, 1, 4, 1365, 0x00CD, target(MONSTER, MONSTER)),
        rec("s2c", 1, 0, 5, 1500, 0x00D3, target(MONSTER, 0)),
        rec("s2c", 2, 0, 6, 1900, 0x00D2, target(MONSTER, 0)),
        rec("c2s", 3, 0, 7, 2000, 0x00CA, bytes(48)),
        rec("s2c", 3, 0, 8, 4000, 0x0139, result(22104, MONSTER)),
        rec("c2s", 4, 0, 9, 9000, 0x00CC, target(0xC0000000, 0x58)),
        rec("c2s", 4, 1, 9, 9000, 0x00CD, target(0xC0000000, 0xE0000000)),
        rec("s2c", 4, 0, 10, 9500, 0x00D2, target(0xC0000000, 0)),
        rec("s2c", 4, 1, 10, 9500, 0x00D3, target(0xC0000000, 0)),
        rec("c2s", 5, 0, 11, 11000, 0x012D, start(0xA0F0520A, "commandForced")),
        rec("s2c", 5, 0, 12, 11500, 0x0134, bytes([0, 0xBF]) + bytes(6)),
        rec("s2c", 5, 1, 12, 11500, 0x0139, result(21002, PLAYER)),
        rec("s2c", 5, 2, 12, 11500, 0x0131, end_event("commandForced")),
    ]


class DecodeTests(unittest.TestCase):
    def test_classifies_lock_and_set_shapes(self):
        self.assertEqual(MODULE.classify_lock(0xC0000000, 7), "clear")
        self.assertEqual(MODULE.classify_lock(MONSTER, 0), "actor, zero")
        self.assertEqual(MODULE.classify_lock(MONSTER, 0x40), "actor, nonzero")
        self.assertEqual(
            MODULE.classify_set(MONSTER, 0xE0000000, PLAYER), "actor, 0xe0000000"
        )
        self.assertEqual(
            MODULE.classify_set(PLAYER, PLAYER, PLAYER), "self, same actor"
        )
        self.assertEqual(
            MODULE.classify_set(0xC0000000, 0xE0000000, PLAYER), "clear, 0xe0000000"
        )

    def test_typed_tail_reads_nil_int_actor_and_end_tags(self):
        values = MODULE.typed_tail(
            bytes.fromhex("05050000000001050622220002050505050f")
        )
        self.assertEqual(len(values), 9)
        self.assertEqual(values[2], ("int", 1))
        self.assertEqual(values[4], ("actor", MONSTER))
        self.assertEqual(
            MODULE.tail_shape(values, MONSTER),
            "nil,nil,int 1,nil,actor=lock target,nil,nil,nil,nil",
        )
        self.assertEqual(MODULE.tail_shape(values, None).count("actor=other"), 1)

    def test_typed_tail_rejects_unknown_tag_and_missing_end(self):
        with self.assertRaises(ValueError):
            MODULE.typed_tail(bytes.fromhex("0507"))
        with self.assertRaises(ValueError):
            MODULE.typed_tail(bytes.fromhex("0505"))
        with self.assertRaises(ValueError):
            MODULE.typed_tail(bytes.fromhex("000000"))

    def test_annotate_rejects_wrong_lengths(self):
        with self.assertRaises(ValueError):
            MODULE.annotate(rec("c2s", 0, 0, 1, 0, 0x00CC, bytes(7)))
        with self.assertRaises(ValueError):
            MODULE.annotate(rec("c2s", 0, 0, 1, 0, 0x012D, bytes(183)))


class JoinTests(unittest.TestCase):
    def setUp(self):
        self.result = MODULE.analyze_capture(engage_capture())

    def test_engage_row_joins_select_lock_echo_and_attack(self):
        (row,) = self.result["engages"]
        self.assertEqual(row["mode"], 21001)
        self.assertEqual(row["select"]["frame_gap"], 1)
        self.assertEqual(row["select"]["ms_to_lock"], 365)
        self.assertFalse(row["select"]["d3_before_lock"])
        self.assertEqual(row["first_d2_ms"], 535)
        self.assertEqual(row["first_attack_ms"], 2635)
        self.assertFalse(row["attack_after_clear"])
        self.assertEqual(row["clear_ms"], 7635)
        self.assertEqual(row["attacks_after_clear"], 0)
        self.assertEqual(row["c2s_before_attack"], {"0x00ca": 1})
        self.assertEqual(
            row["frame_shape"], "0x00cc actor, nonzero + 0x00cd actor, same actor"
        )

    def test_clear_row_records_echo_and_next_mode(self):
        (row,) = self.result["clears"]
        self.assertEqual(row["after"], "actor, nonzero")
        self.assertEqual(row["next"], "0x00cd clear, 0xe0000000")
        self.assertEqual(row["next_mode"], "21002")
        self.assertEqual(row["mode_ms"], 2000)
        self.assertEqual(row["echo"], "0x00d2 then 0x00d3, one frame")

    def test_mode_reply_lists_requester_records_in_subevent_order(self):
        first, second = self.result["modes"]
        self.assertEqual(
            first["reply"],
            "0x0134 02 bf + 0x0139 command=request + 0x0131 commandForced",
        )
        self.assertEqual(first["reply_ms"], 560)
        self.assertEqual(first["targets_before_reply"], 0)
        self.assertTrue(second["reply"].startswith("0x0134 00 bf"))

    def test_attack_after_a_clear_is_joined_and_marked(self):
        records = engage_capture()
        records.insert(10, rec("c2s", 3, 1, 7, 2000, 0x00CC, target(0xC0000000, 0)))
        (row,) = MODULE.analyze_capture(records)["engages"]
        self.assertEqual(row["clear_ms"], 635)
        self.assertEqual(row["first_attack_ms"], 2635)
        self.assertTrue(row["attack_after_clear"])
        self.assertFalse(row["d2_after_clear"])
        self.assertEqual(row["attacks_after_clear"], 1)
        self.assertEqual(row["clear_to_attack_ms"], [2000])

    def test_attack_after_next_actor_lock_is_not_joined(self):
        records = engage_capture()
        records.insert(10, rec("c2s", 3, 1, 7, 2000, 0x00CC, target(NPC, 0)))
        engages = MODULE.analyze_capture(records)["engages"]
        self.assertIsNone(engages[0]["first_attack_ms"])
        self.assertIsNone(engages[0]["clear_ms"])

    def test_talk_neighbors_and_lock_value_guard(self):
        records = [
            rec("c2s", 0, 0, 1, 0, 0x00CC, target(NPC, 0)),
            rec("c2s", 0, 1, 1, 0, 0x012D, start(NPC, "talkDefault", 1, b"\x0f")),
            rec("c2s", 0, 2, 1, 0, 0x00CD, target(NPC, 0xE0000000)),
            rec("c2s", 1, 0, 2, 400, 0x00CC, target(MONSTER, NPC)),
        ]
        result = MODULE.analyze_capture(records)
        (talk,) = result["talks"]
        self.assertEqual(talk["prev"], "0x00cc actor, zero")
        self.assertTrue(talk["prev_actor_is_owner"])
        self.assertEqual(talk["next"], "0x00cd actor, 0xe0000000")
        self.assertTrue(talk["next_actor_is_owner"])
        self.assertEqual(result["lock_seconds"][("actor, nonzero", "actor id")], 1)


class PublishedProductTests(unittest.TestCase):
    def setUp(self):
        self.accounting = json.loads(ACCOUNTING.read_text(encoding="ascii"))

    def test_published_lock_counts_match_expected_figures(self):
        by_shape = {}
        for row in self.accounting["locks"]:
            by_shape[row["shape"]] = by_shape.get(row["shape"], 0) + row["count"]
        self.assertEqual(
            by_shape, {"actor, nonzero": 16, "actor, zero": 17, "clear": 33}
        )
        nonzero = [
            r for r in self.accounting["locks"] if r["shape"] == "actor, nonzero"
        ]
        self.assertEqual(
            [(r["mode"], r["same_frame_next"], r["count"]) for r in nonzero],
            [("21001", "0x00cd actor, same actor", 16)],
        )

    def test_published_talk_trailer_and_crc(self):
        talks = {
            (r["selector"], r["same_frame_next"], r["next_is_owner"]): r["count"]
            for r in self.accounting["talk_starts"]
        }
        self.assertEqual(talks[(1, "0x00cd actor, 0xe0000000", True)], 16)
        crc = self.accounting["event_start_crc"]
        self.assertEqual(crc["messages"], 126)
        self.assertEqual(crc["crc32_matches_parameter_window"], 126)
        self.assertEqual(crc["owner_low16_is_attack_command"], 0)

    def test_published_attack_window_counts(self):
        es = self.accounting["engage_summary"]
        self.assertEqual(es["with_attack"], 13)
        self.assertEqual(es["first_attack_after_clear"], 1)
        self.assertEqual(es["with_d2"], 16)
        self.assertEqual(es["d2_after_clear"], 1)

    def test_verdicts_regenerate_from_accounting(self):
        expected = MODULE.render_verdicts(self.accounting).encode("ascii")
        self.assertEqual((STUDY / "derived" / "verdicts.md").read_bytes(), expected)

    def test_public_shape_validates(self):
        self.assertEqual(MODULE.validate_public_shape(), 0)


class CaptureReplayTests(unittest.TestCase):
    def test_rederives_published_accounting_from_captures(self):
        members = MODULE.load_manifest_members()
        missing = [m for m in members if not (MODULE.OBJECTS / m["file"]).is_file()]
        if missing:
            self.skipTest(f"restricted captures are absent: {len(missing)} files")
        rebuilt = MODULE.render_products(MODULE.build_accounting())
        for name, data in rebuilt.items():
            self.assertEqual(
                (STUDY / "derived" / name).read_bytes(), data, f"{name} drifted"
            )


if __name__ == "__main__":
    unittest.main()
