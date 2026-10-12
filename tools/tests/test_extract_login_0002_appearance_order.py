"""Guard connection, source and reconstructed-order attribution."""

from __future__ import annotations

import sys
import unittest
from ipaddress import IPv4Address
from pathlib import Path
from unittest.mock import patch

from scapy.all import Ether, IP, Padding, Raw, TCP

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "extractors"))
from extract_login_0002_appearance_order import select_source_events  # noqa: E402
import extract_login_0002_appearance_order as extractor  # noqa: E402


def event(
    opcode,
    offset,
    *,
    connection=0,
    direction="s2c",
    source=10,
    destination=10,
    subevent_offset=0,
    lane="main",
    packet=1,
):
    return {
        "opcode": opcode,
        "frame_stream_offset": offset,
        "subevent_offset": subevent_offset,
        "connection_index": connection,
        "direction": direction,
        "src_actor": source,
        "dst_actor": destination,
        "lane": lane,
        "capture_packet_index": packet,
    }


class AppearanceOrderTests(unittest.TestCase):
    def test_connection_and_direction_do_not_merge(self):
        anchor = event(2, 10)
        own = event(0xD6, 20)
        foreign_connection = event(0xCC, 11, connection=1)
        opposite_direction = event(0xCC, 12, direction="c2s")
        opposite_anchor = event(2, 0, direction="c2s")
        _, selected = select_source_events(
            [foreign_connection, opposite_direction, opposite_anchor, own, anchor]
        )
        self.assertEqual(selected, [anchor, own])

    def test_destination_equality_cannot_replace_source_equality(self):
        anchor = event(2, 10)
        wrong_source = event(0xCC, 11, source=20, destination=10)
        correct_source = event(0xD6, 12, source=10, destination=20)
        _, selected = select_source_events([anchor, wrong_source, correct_source])
        self.assertEqual(selected, [anchor, correct_source])

    def test_frame_then_body_order_survives_reversed_packet_witnesses(self):
        anchor = event(2, 10, packet=100)
        ca = event(0xCA, 20, subevent_offset=0, packet=90)
        appearance = event(0xD6, 20, subevent_offset=856, packet=90)
        bind = event(0xCC, 30, packet=1)
        _, selected = select_source_events([bind, appearance, ca, anchor])
        self.assertEqual(selected, [anchor, ca, appearance, bind])

    def test_other_opcode_is_not_an_appearance_or_binding_event(self):
        anchor = event(2, 10)
        noise = event(0x134, 11)
        _, selected = select_source_events([anchor, noise])
        self.assertEqual(selected, [anchor])

    def test_ambiguous_s2c_anchors_fail(self):
        with self.assertRaisesRegex(ValueError, "one admitted main"):
            select_source_events([event(2, 10), event(2, 20, connection=1)])

    def test_chat_anchor_fails(self):
        with self.assertRaisesRegex(ValueError, "one admitted main"):
            select_source_events([event(2, 10, lane="chat")])

    def test_no_s2c_anchor_fails(self):
        with self.assertRaisesRegex(ValueError, "one admitted main"):
            select_source_events([event(2, 10, direction="c2s")])

    def test_padded_ack_cannot_witness_frame_start(self):
        ack = tcp_packet(100, b"", padding_size=6)
        data = tcp_packet(100, b"x" * 53)
        self.assertEqual(len(bytes(ack["TCP"].payload)), 6)
        with patch.object(extractor, "read_packets", return_value=[ack, data]):
            spans = extractor._packet_spans(
                Path("unused.pcapng"), connection(data), "s2c"
            )
        self.assertEqual(len(spans), 1)
        self.assertEqual((spans[0]["start"], spans[0]["end"]), (0, 53))
        witness = extractor._frame_packet(0, 53, spans)
        self.assertEqual(witness["start_packet_index"], 1)
        self.assertEqual(witness["packet_index"], 1)

    def test_padding_after_data_cannot_complete_frame(self):
        first = tcp_packet(100, b"abc", padding_size=6)
        last = tcp_packet(103, b"de")
        self.assertEqual(len(bytes(first["TCP"].payload)), 9)
        with patch.object(extractor, "read_packets", return_value=[first, last]):
            spans = extractor._packet_spans(
                Path("unused.pcapng"), connection(first), "s2c"
            )
        self.assertEqual(
            [(span["start"], span["end"]) for span in spans], [(0, 3), (3, 5)]
        )
        witness = extractor._frame_packet(0, 5, spans)
        self.assertEqual(witness["start_packet_index"], 0)
        self.assertEqual(witness["packet_index"], 1)


def tcp_packet(sequence, payload, padding_size=0):
    packet = (
        Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:02")
        / IP(
            src=str(IPv4Address(0xC0000201)),
            dst=str(IPv4Address(0xC0000202)),
            ihl=5,
            len=40 + len(payload),
        )
        / TCP(sport=54992, dport=60000, seq=sequence, dataofs=5, flags="A")
    )
    if payload:
        packet /= Raw(payload)
    if padding_size:
        packet /= Padding(b"\0" * padding_size)
    return Ether(bytes(packet))


def connection(packet):
    return {
        "lane": "main",
        "server_endpoint": (packet["IP"].src, 54992),
        "client_endpoint": (packet["IP"].dst, 60000),
    }


if __name__ == "__main__":
    unittest.main()
