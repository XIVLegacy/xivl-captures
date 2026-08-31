import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "extractors" / "extract_equipment_property_correlation.py"
SPEC = importlib.util.spec_from_file_location("extract_equipment_property_correlation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


@unittest.skipUnless(
    (ROOT / "sources" / "pcap-1.23b" / "objects").is_dir(),
    "restricted corpus absent",
)
class EquipmentTransitionCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accounting, cls.matrix, cls.deltas, cls.summary = MODULE.extract()

    def test_full_corpus_and_balanced_framing(self):
        self.assertEqual(len(self.accounting), 54)
        self.assertEqual(self.summary["set_scopes"], 158)
        self.assertEqual(self.summary["framed_events"], 142)
        self.assertTrue(all(row["set_begin_count"] == row["set_end_count"]
                            for row in self.accounting))

    def test_every_item_and_link_cardinality_is_censused(self):
        totals = {
            opcode: sum(int(row[f"opcode_0x{opcode:04x}_count"]) for row in self.accounting)
            for opcode in range(0x0148, 0x0152)
        }
        self.assertEqual(totals, {
            0x0148: 54, 0x0149: 43, 0x014A: 12, 0x014B: 77, 0x014C: 0,
            0x014D: 6, 0x014E: 25, 0x014F: 0, 0x0150: 0, 0x0151: 0,
        })
        self.assertEqual((self.summary["item_records"], self.summary["link_records"]),
                         (2982, 146))

    def test_exact_helm_transition_preserves_wire_only_property(self):
        exact = [row for row in self.matrix if row["classification"] == "EXACT-TRANSITION"]
        self.assertEqual(len(exact), 1)
        self.assertEqual((exact[0]["capture"], exact[0]["equipment_slot"],
                          exact[0]["catalog_item_id"]),
                         ("change_helm.pcapng", 8, "0x007A3F58"))
        changed = [row for row in self.deltas
                   if row["comparison_status"] == "changed"
                   and row["carrier_scope"] == "single-slot"]
        self.assertEqual(len(changed), 1)
        self.assertEqual((changed[0]["property_hash"],
                          changed[0]["before_value_u_le"],
                          changed[0]["after_value_u_le"]),
                         ("0x8cae90db", "141", "161"))

    def test_old_helm_link_is_closed_by_exact_snapshots(self):
        old_helm = [row for row in self.matrix
                    if row["equipment_slot"] == 8
                    and row["catalog_item_id"] == "0x007A3D64"]
        self.assertEqual(len(old_helm), 6)
        self.assertEqual({row["classification"] for row in old_helm}, {"AGGREGATE-SNAPSHOT"})
        self.assertTrue(all(str(row["join_status"]).startswith("exact-") for row in old_helm))

    def test_open_candidates_and_soul_fail_closed(self):
        candidates = [row for row in self.matrix if row["classification"] == "BOUNDED-CANDIDATE"]
        self.assertEqual(
            [(row["capture"], row["equipment_slot"], row["catalog_item_id"])
             for row in candidates],
            [
                ("change_bodyarmor.pcapng", 10, "0x007A88D7"),
                ("change_to_botanist.pcapng", 0, "0x006B1DE2"),
                ("change_to_botanist.pcapng", 1, "0x006B1E4C"),
                ("gear_changeweapon.pcapng", 0, "0x003D7E3D"),
                ("switch_to_weaver.pcapng", 0, "0x005C77E6"),
            ],
        )
        soul = [row for row in self.matrix if row["capture"] == "gear_changesoul.pcapng"]
        self.assertEqual(len(soul), 1)
        self.assertEqual(soul[0]["join_status"], "property-only-no-inventory-frame")
        after_only = {(row["capture"], row["property_hash"]): row["after_value_u_le"]
                      for row in self.deltas if row["comparison_status"] == "after-only"}
        self.assertEqual(after_only[("change_bodyarmor.pcapng", "0x8cae90db")], "147")
        self.assertEqual(after_only[("gear_changeweapon.pcapng", "0x8cae90db")], "169")

    def test_repetition_retransmission_and_excluded_nearby_traffic(self):
        self.assertEqual(self.summary["repeated_aggregate_events"], 10)
        self.assertEqual(self.summary["retransmitted_segments"], 1759)
        self.assertEqual(self.summary["excluded_nearby_packets"], 5625)
        self.assertTrue(all(row["link_opcode"] not in {"0x018F", "0x0190", "0x0191"}
                            for row in self.matrix))

    def test_public_actor_tokens_do_not_expose_numeric_ids(self):
        actors = {row[field] for row in self.matrix for field in ("source_actor", "destination_actor")
                  if row[field]}
        self.assertTrue(actors)
        self.assertTrue(all(str(actor).startswith("actor-") for actor in actors))


if __name__ == "__main__":
    unittest.main()
