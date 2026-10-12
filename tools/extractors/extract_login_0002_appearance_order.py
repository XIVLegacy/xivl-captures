#!/usr/bin/env python3
"""Extract numeric same-source order around login s2c inner 0x0002."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from extract_login_018a_timeline import _frame_packet  # noqa: E402
from extract_observations import parse_sub_events  # noqa: E402
from extract_streams import (  # noqa: E402
    _is_game_connection,
    maybe_inflate,
    parse_outer_frames,
    read_packets,
    reconstruct_connections,
    reconstruct_lanes,
)

REPO_ROOT = SCRIPT_DIR.parents[1]
STUDY = "login-0002-appearance-order"
CAPTURE_SHA256 = "28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62"
CAPTURE_SIZE = 856236
SELECTED_OPCODES = (0x0002, 0x00CA, 0x00CC, 0x00D6, 0x00D7)
CSV_FIELDS = [
    "connection_index",
    "lane",
    "direction",
    "direction_event_index",
    "frame_index",
    "frame_stream_offset",
    "subevent_index",
    "subevent_offset",
    "capture_packet_index",
    "frame_start_capture_packet_index",
    "opcode",
    "src_actor",
    "dst_actor",
    "subevent_size",
    "subevent_sha256",
]


def _packet_spans(path: Path, connection: dict, direction: str) -> list[dict]:
    """Locate TCP data using IP-declared lengths, excluding captured padding."""
    server, client = connection["server_endpoint"], connection["client_endpoint"]
    expected = (server, client) if direction == "s2c" else (client, server)
    matched = []
    for packet_index, packet in enumerate(read_packets(path)):
        if not packet.haslayer("IP") or not packet.haslayer("TCP"):
            continue
        ip, tcp = packet["IP"], packet["TCP"]
        if ((ip.src, tcp.sport), (ip.dst, tcp.dport)) != expected:
            continue
        payload_size = int(ip.len) - 4 * int(ip.ihl) - 4 * int(tcp.dataofs)
        if payload_size < 0 or len(bytes(tcp.payload)) < payload_size:
            raise ValueError("invalid or truncated IP-declared TCP payload")
        # Scapy can attach Ethernet Padding to TCP.payload on a payload-free ACK.
        if payload_size == 0:
            continue
        matched.append(
            (
                int(tcp.seq),
                payload_size,
                packet_index,
                int(Decimal(str(packet.time)) * 1_000_000),
            )
        )
    if not matched:
        raise ValueError(f"no TCP payload packets for {connection['lane']} {direction}")
    initial_sequence = min(row[0] for row in matched)
    return [
        {
            "start": sequence - initial_sequence,
            "end": sequence - initial_sequence + size,
            "packet_index": packet_index,
            "capture_time_us": capture_time_us,
        }
        for sequence, size, packet_index, capture_time_us in matched
    ]


def collect_events(path: Path) -> tuple[list[dict], list[dict], list[dict]]:
    """Use canonical game admission; retain independent connection directions."""
    connections = reconstruct_lanes(path)
    events, framing = [], []
    for connection_index, connection in enumerate(connections):
        for direction in ("c2s", "s2c"):
            blob = connection["streams"].get(direction, b"")
            spans = _packet_spans(path, connection, direction) if blob else []
            frames = parse_outer_frames(blob)
            if sum(frame["size"] for frame in frames) != len(blob):
                raise ValueError("unaccounted reconstructed outer-frame bytes")
            # Reconstruction trims to complete frames; check against captured span ends.
            captured_end = max((span["end"] for span in spans), default=0)
            if captured_end != len(blob):
                raise ValueError(
                    "captured TCP direction has an incomplete trailing frame"
                )
            covered_end = 0
            for span in sorted(spans, key=lambda row: row["start"]):
                if span["start"] > covered_end:
                    raise ValueError("captured TCP direction has a sequence gap")
                covered_end = max(covered_end, span["end"])
            event_index = 0
            for frame_index, frame in enumerate(frames):
                inflated = maybe_inflate(frame["body"])
                if (frame["marker"][1] == 1) != (inflated is not None):
                    raise ValueError("outer compression flag/body mismatch")
                body = inflated if inflated is not None else frame["body"]
                witness = _frame_packet(frame["offset"], frame["size"], spans)
                subevents = parse_sub_events(body)
                if any(event.get("truncated") for event in subevents):
                    raise ValueError("truncated sub-event")
                consumed = sum(event["size"] for event in subevents)
                if any(body[consumed:]):
                    raise ValueError("nonzero undecoded sub-event tail")
                for subevent_index, event in enumerate(subevents):
                    opcode = event.get("inner_opcode")
                    if event["type"] != 3 or opcode is None:
                        continue
                    start, size = event["offset"], event["size"]
                    events.append(
                        {
                            "connection_index": connection_index,
                            "lane": connection["lane"],
                            "direction": direction,
                            "direction_event_index": event_index,
                            "frame_index": frame_index,
                            "frame_stream_offset": frame["offset"],
                            "subevent_index": subevent_index,
                            "subevent_offset": start,
                            "capture_packet_index": witness["packet_index"] + 1,
                            "frame_start_capture_packet_index": witness[
                                "start_packet_index"
                            ]
                            + 1,
                            "opcode": opcode,
                            "src_actor": event["src_actor"],
                            "dst_actor": event["dst_actor"],
                            "subevent_size": size,
                            "subevent_sha256": hashlib.sha256(
                                body[start : start + size]
                            ).hexdigest(),
                        }
                    )
                    event_index += 1
            framing.append(
                {
                    "connection_index": connection_index,
                    "lane": connection["lane"],
                    "direction": direction,
                    "stream_bytes": len(blob),
                    "frames": len(frames),
                    "wrapped_inner_events": event_index,
                    "trailing_bytes": captured_end - len(blob),
                    "captured_payload_segments": len(spans),
                    "unique_reconstructed_starts": len(
                        {span["start"] for span in spans}
                    ),
                    "compressed_frames": sum(
                        frame["marker"][1] == 1 for frame in frames
                    ),
                }
            )
    return connections, events, framing


def select_source_events(events: list[dict]) -> tuple[dict, list[dict]]:
    """Join on wrapped source, connection and direction; order by stream position."""
    anchors = [
        event
        for event in events
        if event["direction"] == "s2c" and event["opcode"] == 2
    ]
    if len(anchors) != 1 or anchors[0]["lane"] != "main":
        raise ValueError("expected one admitted main s2c inner 0x0002")
    anchor = anchors[0]
    selected = [
        event
        for event in events
        if event["connection_index"] == anchor["connection_index"]
        and event["direction"] == "s2c"
        and event["src_actor"] == anchor["src_actor"]
        and event["opcode"] in SELECTED_OPCODES
    ]
    selected.sort(key=lambda row: (row["frame_stream_offset"], row["subevent_offset"]))
    return anchor, selected


def build_outputs(path: Path) -> dict[str, bytes]:
    data = path.read_bytes()
    if len(data) != CAPTURE_SIZE or hashlib.sha256(data).hexdigest() != CAPTURE_SHA256:
        raise ValueError("login.pcapng identity mismatch")
    connections, events, framing = collect_events(path)
    anchor, selected = select_source_events(events)
    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for event in selected:
        row = dict(event)
        for key in ("opcode", "src_actor", "dst_actor"):
            row[key] = f"0x{row[key]:0{4 if key == 'opcode' else 8}X}"
        writer.writerow(row)
    raw = reconstruct_connections(path)
    accounting = {
        "schema_version": 1,
        "study": STUDY,
        "input": {
            "source": "pcap-1.23b",
            "capture": "login.pcapng",
            "capture_sha256": CAPTURE_SHA256,
            "size_bytes": CAPTURE_SIZE,
            "manifest_locator": "sources/pcap-1.23b/manifest.yaml:135-137",
        },
        "admission": {
            "raw_frame_shaped_connections": len(raw),
            "admitted_connections": len(connections),
            "rejected_connections": sum(not _is_game_connection(conn) for conn in raw),
            "raw_server_port_counts": dict(
                sorted(Counter(str(conn["server_endpoint"][1]) for conn in raw).items())
            ),
        },
        "framing": framing,
        "anchor": anchor,
        "selected_source_counts": {
            f"0x{opcode:04X}": sum(event["opcode"] == opcode for event in selected)
            for opcode in SELECTED_OPCODES
        },
        "all_admitted_s2c_counts": {
            f"0x{opcode:04X}": sum(
                event["direction"] == "s2c" and event["opcode"] == opcode
                for event in events
            )
            for opcode in SELECTED_OPCODES
        },
        "order": [f"0x{event['opcode']:04X}" for event in selected],
        "index_convention": "Connection, frame, sub-event and direction-event indexes are zero-based; capture packet indexes are one-based. Stream offsets are wire bytes; sub-event offsets are in the decoded frame body.",
        "boundary": "One reconstructed s2c direction on one admitted TCP connection; no capture-wide or cross-direction order, dispatch timing, appearance admission or rendering is established. Wrapped source equality is numeric; native case-2 interpretation belongs to the consumer.",
    }
    return {
        "events.csv": csv_buffer.getvalue().encode("ascii"),
        "accounting.json": (json.dumps(accounting, indent=2) + "\n").encode("ascii"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    capture = (
        Path(
            os.environ.get(
                "XIVL_PCAP_OBJECTS_DIR", str(args.repo / "sources/pcap-1.23b/objects")
            )
        )
        / "login.pcapng"
    )
    out = args.out_dir or args.repo / "studies" / STUDY / "derived"
    outputs = build_outputs(capture)
    if args.check:
        stale = [
            name
            for name, content in outputs.items()
            if not (out / name).is_file() or (out / name).read_bytes() != content
        ]
        if stale:
            raise ValueError("stale study products: " + ", ".join(stale))
    else:
        out.mkdir(parents=True, exist_ok=True)
        for name, content in outputs.items():
            (out / name).write_bytes(content)
    print(
        f"{STUDY}: {'verified' if args.check else 'generated'} {len(outputs)} products"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
