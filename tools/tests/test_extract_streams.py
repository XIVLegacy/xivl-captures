import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "extractors"))

import extract_streams  # noqa: E402


def connection(port: int, *streams: bytes) -> dict:
    directions = ("c2s", "s2c")
    return {
        "server_endpoint": ("203.0.113.10", port),
        "streams": dict(zip(directions, streams)),
    }


class GameLaneAdmissionTests(unittest.TestCase):
    def test_accepts_clear_game_connection(self):
        candidate = connection(54992, b"\x01\x00", b"\x01\x01")
        self.assertTrue(extract_streams._is_game_connection(candidate))

    def test_rejects_lobby_connection(self):
        candidate = connection(54994, b"\x01\x00", b"\x01\x00")
        self.assertFalse(extract_streams._is_game_connection(candidate))

    def test_rejects_tls_on_game_port(self):
        candidate = connection(54992, b"\x16\x03\x01", b"\x01\x01")
        self.assertFalse(extract_streams._is_game_connection(candidate))

    def test_reconstruct_lanes_filters_before_consumers(self):
        game = connection(54992, b"\x01\x00", b"\x01\x01")
        lobby = connection(54994, b"\x01\x00", b"\x01\x00")
        tls = connection(54992, b"\x16\x03\x01", b"\x01\x01")
        with patch.object(
            extract_streams,
            "reconstruct_connections",
            return_value=[lobby, game, tls],
        ):
            self.assertEqual(extract_streams.reconstruct_lanes(Path("unused")), [game])


if __name__ == "__main__":
    unittest.main()
