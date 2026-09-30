import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "extractors" / "extract_equipment_property_correlation.py"
SPEC = importlib.util.spec_from_file_location(
    "extract_equipment_property_correlation", SCRIPT
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _property_row(
    record_index,
    *,
    capture="synthetic.pcapng",
    lane_index=0,
    source_actor_id=1,
    destination_actor_id=1,
    target_marker="",
    property_hash="0x00000001",
    value_hex="00",
    frame_index=0,
    subevent_index=0,
    packet_index=0,
    record_in_packet=0,
    stream_offset=1,
):
    return {
        "record_index": str(record_index),
        "capture": capture,
        "lane_index": str(lane_index),
        "source_actor_id": str(source_actor_id),
        "destination_actor_id": str(destination_actor_id),
        "target_marker": target_marker,
        "property_hash": property_hash,
        "value_hex": value_hex,
        "value_u_le": str(int.from_bytes(bytes.fromhex(value_hex), "little")),
        "frame_index": str(frame_index),
        "subevent_index": str(subevent_index),
        "packet_index": str(packet_index),
        "record_in_packet": str(record_in_packet),
        "stream_offset": str(stream_offset),
    }


def _replay(rows, **kwargs):
    defaults = {
        "event_id": "equipment-event-synthetic",
        "capture": "synthetic.pcapng",
        "lane_index": 0,
        "source_actor_id": 1,
        "destination_actor_id": 1,
        "source_actor": "actor-01",
        "destination_actor": "actor-01",
        "equipment_slot": 0,
        "catalog_item_id": "0x00000001",
        "begin_frame": 10,
        "begin_subevent": 1,
        "end_frame": 10,
        "end_subevent": 3,
    }
    defaults.update(kwargs)
    return MODULE._replay_property_rows(rows, **defaults)


class EquipmentPropertyReplaySyntheticTests(unittest.TestCase):
    def test_wire_order_repeated_writes_and_carrier_bound_exclusion(self):
        rows = [
            _property_row(4, frame_index=11, value_hex="01", stream_offset=20),
            _property_row(5, frame_index=11, value_hex="02", stream_offset=10),
            _property_row(
                3,
                frame_index=10,
                subevent_index=2,
                value_hex="ff",
                stream_offset=1,
            ),
            _property_row(
                2, frame_index=9, subevent_index=1, value_hex="01", stream_offset=20
            ),
            _property_row(
                1, frame_index=9, subevent_index=1, value_hex="02", stream_offset=10
            ),
            _property_row(6, frame_index=13, value_hex="03", stream_offset=1),
        ]
        replay = _replay(rows)
        self.assertEqual(
            [row["comparison_status"] for row in replay], ["CHANGED", "UNCHANGED"]
        )
        self.assertEqual([row["after_record_index"] for row in replay], ["5", "4"])
        self.assertEqual(replay[0]["before_record_index"], "2")
        self.assertEqual(replay[0]["within_carrier_write_count"], 1)
        self.assertEqual(replay[0]["after_write_count"], 2)
        self.assertTrue(all(row["after_record_index"] != "6" for row in replay))

    def test_partition_and_target_marker_context_isolation(self):
        rows = [
            _property_row(1, frame_index=9, value_hex="01", target_marker="a"),
            _property_row(2, frame_index=11, value_hex="02", target_marker="a"),
            _property_row(3, frame_index=11, value_hex="03", target_marker="b"),
            _property_row(4, frame_index=11, value_hex="04", lane_index=1),
            _property_row(5, frame_index=11, value_hex="05", source_actor_id=2),
            _property_row(6, frame_index=11, value_hex="06", capture="other.pcapng"),
        ]
        replay = _replay(rows)
        self.assertEqual(
            [row["comparison_status"] for row in replay],
            ["CHANGED", "UNKNOWN-INITIAL"],
        )
        self.assertEqual(
            {row["property_context"] for row in replay}, {"context-01", "context-02"}
        )
        self.assertTrue(all("a" not in row["property_context"] for row in replay))

    def test_unknown_initial_value_is_explicit(self):
        replay = _replay(
            [
                _property_row(
                    8,
                    frame_index=12,
                    property_hash="0x00000002",
                    value_hex="09",
                )
            ]
        )
        self.assertEqual(len(replay), 1)
        self.assertEqual(replay[0]["comparison_status"], "UNKNOWN-INITIAL")
        self.assertEqual(replay[0]["before_record_index"], "")

    def test_no_post_frame_is_explicit(self):
        replay = _replay(
            [
                _property_row(
                    9,
                    frame_index=9,
                    property_hash="0x00000003",
                    value_hex="09",
                )
            ]
        )
        self.assertEqual(replay[0]["comparison_status"], "NO-POST-FRAME")
        self.assertEqual(replay[0]["post_frame_cutoff"], "")


@unittest.skipUnless(
    MODULE.default_corpus_paths(),
    "restricted corpus absent",
)
class EquipmentTransitionCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (
            cls.accounting,
            cls.matrix,
            cls.deltas,
            cls.summary,
            cls.replay,
        ) = MODULE.extract_with_replay()

    def test_full_corpus_and_balanced_framing(self):
        self.assertEqual(len(self.accounting), 54)
        self.assertEqual(self.summary["set_scopes"], 158)
        self.assertEqual(self.summary["framed_events"], 142)
        self.assertTrue(
            all(
                row["set_begin_count"] == row["set_end_count"]
                for row in self.accounting
            )
        )

    def test_every_item_and_link_cardinality_is_censused(self):
        totals = {
            opcode: sum(
                int(row[f"opcode_0x{opcode:04x}_count"]) for row in self.accounting
            )
            for opcode in range(0x0148, 0x0152)
        }
        self.assertEqual(
            totals,
            {
                0x0148: 54,
                0x0149: 43,
                0x014A: 12,
                0x014B: 77,
                0x014C: 0,
                0x014D: 6,
                0x014E: 25,
                0x014F: 0,
                0x0150: 0,
                0x0151: 0,
            },
        )
        self.assertEqual(
            (self.summary["item_records"], self.summary["link_records"]), (2982, 146)
        )

    def test_exact_helm_transition_preserves_wire_only_property(self):
        exact = [
            row for row in self.matrix if row["classification"] == "EXACT-TRANSITION"
        ]
        self.assertEqual(len(exact), 1)
        self.assertEqual(
            (
                exact[0]["capture"],
                exact[0]["equipment_slot"],
                exact[0]["catalog_item_id"],
            ),
            ("change_helm.pcapng", 8, "0x007A3F58"),
        )
        changed = [
            row
            for row in self.deltas
            if row["comparison_status"] == "changed"
            and row["carrier_scope"] == "single-slot"
        ]
        self.assertEqual(len(changed), 1)
        self.assertEqual(
            (
                changed[0]["property_hash"],
                changed[0]["before_value_u_le"],
                changed[0]["after_value_u_le"],
            ),
            ("0x8cae90db", "141", "161"),
        )

    def test_old_helm_link_is_closed_by_exact_snapshots(self):
        old_helm = [
            row
            for row in self.matrix
            if row["equipment_slot"] == 8 and row["catalog_item_id"] == "0x007A3D64"
        ]
        self.assertEqual(len(old_helm), 6)
        self.assertEqual(
            {row["classification"] for row in old_helm}, {"AGGREGATE-SNAPSHOT"}
        )
        self.assertTrue(
            all(str(row["join_status"]).startswith("exact-") for row in old_helm)
        )

    def test_open_candidates_and_soul_fail_closed(self):
        candidates = [
            row for row in self.matrix if row["classification"] == "BOUNDED-CANDIDATE"
        ]
        self.assertEqual(
            [
                (row["capture"], row["equipment_slot"], row["catalog_item_id"])
                for row in candidates
            ],
            [
                ("change_bodyarmor.pcapng", 10, "0x007A88D7"),
                ("change_to_botanist.pcapng", 0, "0x006B1DE2"),
                ("change_to_botanist.pcapng", 1, "0x006B1E4C"),
                ("gear_changeweapon.pcapng", 0, "0x003D7E3D"),
                ("switch_to_weaver.pcapng", 0, "0x005C77E6"),
            ],
        )
        soul = [
            row for row in self.matrix if row["capture"] == "gear_changesoul.pcapng"
        ]
        self.assertEqual(len(soul), 1)
        self.assertEqual(soul[0]["join_status"], "property-only-no-inventory-frame")
        after_only = {
            (row["capture"], row["property_hash"]): row["after_value_u_le"]
            for row in self.deltas
            if row["comparison_status"] == "after-only"
        }
        self.assertEqual(after_only[("change_bodyarmor.pcapng", "0x8cae90db")], "147")
        self.assertEqual(after_only[("gear_changeweapon.pcapng", "0x8cae90db")], "169")

    def test_repetition_retransmission_and_excluded_nearby_traffic(self):
        self.assertEqual(self.summary["repeated_aggregate_events"], 10)
        self.assertEqual(self.summary["retransmitted_segments"], 1759)
        self.assertEqual(self.summary["excluded_nearby_packets"], 5625)
        self.assertTrue(
            all(
                row["link_opcode"] not in {"0x018F", "0x0190", "0x0191"}
                for row in self.matrix
            )
        )

    def test_public_actor_tokens_do_not_expose_numeric_ids(self):
        actors = {
            row[field]
            for row in self.matrix
            for field in ("source_actor", "destination_actor")
            if row[field]
        }
        self.assertTrue(actors)
        self.assertTrue(all(str(actor).startswith("actor-") for actor in actors))

    def test_bounded_replay_covers_only_named_candidates(self):
        self.assertEqual(
            {row["event_id"] for row in self.replay}, MODULE.REPLAY_EVENT_IDS
        )
        self.assertTrue(
            all(
                row["comparison_status"] not in {"CHANGED", "UNCHANGED"}
                for row in self.replay
            )
        )
        self.assertTrue(
            all(row["within_carrier_write_count"] == 0 for row in self.replay)
        )
        expected_post_frames = {
            "equipment-event-002": 20,
            "equipment-event-005": 23,
            "equipment-event-006": 36,
            "equipment-event-027": 16,
            "equipment-event-111": 26,
        }
        for event_id, frame_index in expected_post_frames.items():
            self.assertEqual(
                {
                    row["post_frame_cutoff"]
                    for row in self.replay
                    if row["event_id"] == event_id
                },
                {frame_index},
            )
        expected_before = {
            ("equipment-event-002", "0x0ad1ce80"): "33",
            ("equipment-event-005", "0x0ad1ce80"): "49",
            ("equipment-event-006", "0x416571ac"): "52",
            ("equipment-event-027", "0x0ad1ce80"): "587",
            ("equipment-event-111", "0x0ad1ce80"): "8140",
        }
        for key, record_index in expected_before.items():
            matching = [
                row
                for row in self.replay
                if (row["event_id"], row["property_hash"]) == key
            ]
            self.assertEqual(len(matching), 1)
            self.assertEqual(matching[0]["before_record_index"], record_index)
        self.assertEqual(
            next(
                row["after_record_index"]
                for row in self.replay
                if row["event_id"] == "equipment-event-002"
                and row["property_hash"] == "0x8cae90db"
            ),
            "37",
        )


if __name__ == "__main__":
    unittest.main()
