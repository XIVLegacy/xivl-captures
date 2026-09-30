import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import build_scenario_views  # noqa: E402


class GameObservationJoinTests(unittest.TestCase):
    def test_lobby_witness_does_not_label_game_observation(self):
        observations = {
            "inner_opcodes": {
                "c2s": {},
                "s2c": {
                    "0x000c": {
                        "observedIn": ["login.pcapng"],
                        "subEventSizes": [40],
                    },
                    "0x000f": {
                        "observedIn": ["login.pcapng"],
                        "subEventSizes": [56],
                    },
                },
            }
        }
        entries = []
        for opcode in ("0x000c", "0x000f"):
            for service in ("map", "lobby"):
                entries.append(
                    {
                        "service": service,
                        "direction": "clientbound",
                        "opcodeHex": opcode,
                        "name": f"{service}-{opcode}",
                        "retail_class_name": None,
                        "observedIn": ["login.pcapng"],
                    }
                )
        with (
            patch.object(
                build_scenario_views,
                "OBSERVATIONS_JSON",
                Mock(read_text=Mock(return_value=json.dumps(observations))),
            ),
            patch.object(
                build_scenario_views,
                "OPCODE_NAMES_JSON",
                Mock(read_text=Mock(return_value=json.dumps({"entries": entries}))),
            ),
        ):
            joined = build_scenario_views.load_inversion()
        self.assertEqual(
            joined,
            {
                "login.pcapng": [
                    {
                        "hex": opcode,
                        "name": f"map-{opcode}",
                        "retail_class_name": None,
                        "service": "map",
                        "direction": "clientbound",
                        "lengths": [length],
                    }
                    for opcode, length in (("0x000c", 40), ("0x000f", 56))
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
