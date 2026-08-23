"""Reconstruct and inspect clear port-54992 game lanes in a 1.23b capture.

TLS and non-game server ports remain available only through the raw connection
reconstructor and never enter canonical reducers.
"""

from __future__ import annotations

from collections import Counter
import struct
import warnings
import zlib
from pathlib import Path

warnings.filterwarnings("ignore")
from scapy.all import rdpcap, IP, TCP  # noqa: E402


FFXIV_SERVER_PORTS = {54992, 54993, 54994}  # Observed 1.23b server ports; other pairs use the lower-port heuristic.
GAME_SERVER_PORT = 54992
TLS_RECORD_SIGNATURE = b"\x16\x03"

_PACKET_CACHE: dict[Path, object] = {}
_PACKET_READ_COUNTS: Counter[Path] = Counter()


def reset_packet_cache() -> None:
    """Drop cached packets and counters before a unified generation run."""
    _PACKET_CACHE.clear()
    _PACKET_READ_COUNTS.clear()


def clear_packet_cache() -> None:
    """Release packet memory without discarding the completed read counters."""
    _PACKET_CACHE.clear()


def packet_read_counts() -> dict[Path, int]:
    """Return the number of physical pcap reads by resolved path."""
    return dict(_PACKET_READ_COUNTS)


def read_packets(pcap_path: Path):
    """Read one pcap at most once in this process and return its Scapy packets."""
    key = Path(pcap_path).resolve()
    if key not in _PACKET_CACHE:
        _PACKET_CACHE[key] = rdpcap(str(key))
        _PACKET_READ_COUNTS[key] += 1
    return _PACKET_CACHE[key]


def _reconstruct_direction(items: list[tuple[int, bytes, int]]):
    """Place segments by sequence offset so retransmits do not duplicate bytes."""
    if not items:
        return b"", []
    items = sorted(items, key=lambda x: x[0])
    initial_seq = items[0][0]
    max_end = max(seq + len(payload) - initial_seq for seq, payload, _ in items)
    buf = bytearray(max_end)
    offmap: list[tuple[int, int]] = []
    for seq, payload, idx in items:
        offset = seq - initial_seq
        buf[offset : offset + len(payload)] = payload
        offmap.append((offset, idx))
    offmap.sort()
    return bytes(buf), offmap


def _server_endpoint(ep_a: tuple[str, int], ep_b: tuple[str, int]) -> tuple[str, int]:
    """Prefer known ports because client ephemeral ports may be lower; otherwise choose lower."""
    port_a, port_b = ep_a[1], ep_b[1]
    if port_a in FFXIV_SERVER_PORTS and port_b not in FFXIV_SERVER_PORTS:
        return ep_a
    if port_b in FFXIV_SERVER_PORTS and port_a not in FFXIV_SERVER_PORTS:
        return ep_b
    return ep_a if port_a < port_b else ep_b


def reconstruct_connections(pcap_path: Path) -> list[dict]:
    """Return every frame-shaped TCP connection before protocol admission."""
    pcap = read_packets(pcap_path)

    conns: dict[tuple, list[tuple[tuple, tuple, int, bytes, int]]] = {}
    for idx, p in enumerate(pcap):
        if not p.haslayer(IP) or not p.haslayer(TCP):
            continue
        payload = bytes(p[TCP].payload)
        if not payload:
            continue
        ep_src = (p[IP].src, p[TCP].sport)
        ep_dst = (p[IP].dst, p[TCP].dport)
        conn_key = tuple(sorted((ep_src, ep_dst)))
        conns.setdefault(conn_key, []).append((ep_src, ep_dst, p[TCP].seq, payload, idx))

    lanes = []
    for conn_key in sorted(conns):
        ep_a, ep_b = conn_key
        server_ep = _server_endpoint(ep_a, ep_b)
        streams = {}
        indexes = {}
        for direction in ("c2s", "s2c"):
            want_server_src = direction == "s2c"
            items = [
                (seq, payload, idx)
                for ep_src, _ep_dst, seq, payload, idx in conns[conn_key]
                if (ep_src == server_ep) == want_server_src
            ]
            blob, offmap = _reconstruct_direction(items)
            clean = frame_clean_length(blob)
            if clean:
                streams[direction] = blob[:clean]
                indexes[direction] = [(offset, idx) for offset, idx in offmap if offset < clean]

        if not streams:
            continue
        s2c_frames = parse_outer_frames(streams.get("s2c", b""))
        if any(frame["marker"][1] == 0x01 for frame in s2c_frames):
            lane = "main"
        elif s2c_frames:
            lane = "chat"
        else:
            lane = "unknown"
        client_ep = ep_b if server_ep == ep_a else ep_a
        lanes.append({
            "lane": lane,
            "client_endpoint": client_ep,
            "server_endpoint": server_ep,
            "streams": streams,
            "index": indexes,
        })
    return lanes


def _is_game_connection(connection: dict) -> bool:
    """Accept clear port-54992 game traffic and reject lobby or TLS streams."""
    if connection["server_endpoint"][1] != GAME_SERVER_PORT:
        return False
    return not any(
        blob.startswith(TLS_RECORD_SIGNATURE)
        for blob in connection["streams"].values()
    )


def reconstruct_lanes(pcap_path: Path) -> list[dict]:
    """Return classified lanes from clear port-54992 game connections only."""
    return [
        connection
        for connection in reconstruct_connections(pcap_path)
        if _is_game_connection(connection)
    ]


def reconstruct_with_index(pcap_path: Path):
    """Merge frame-clean game lanes by direction and retain packet-offset indexes."""
    lanes = reconstruct_lanes(pcap_path)
    if not lanes:
        return {}, {}

    merged: dict[str, list[bytes]] = {"c2s": [], "s2c": []}
    merged_index: dict[str, list[tuple[int, int]]] = {"c2s": [], "s2c": []}
    base: dict[str, int] = {"c2s": 0, "s2c": 0}

    # Deterministic connection order keeps merged offsets reproducible.
    for connection in lanes:
        for direction in ("c2s", "s2c"):
            blob = connection["streams"].get(direction)
            if blob is None:
                continue
            merged[direction].append(blob)
            for offset, idx in connection["index"][direction]:
                merged_index[direction].append((base[direction] + offset, idx))
            base[direction] += len(blob)

    streams: dict[str, bytes] = {}
    index: dict[str, list[tuple[int, int]]] = {}
    for direction in ("c2s", "s2c"):
        if merged[direction]:
            streams[direction] = b"".join(merged[direction])
            index[direction] = merged_index[direction]

    return streams, index


def reconstruct(pcap_path: Path) -> dict[str, bytes]:
    """Return {direction: bytes} where direction is c2s or s2c."""
    streams, _index = reconstruct_with_index(pcap_path)
    return streams


# Outer frame model: see docs/pcap-decoding.md "Outer frames" for the field offsets and marker byte values.
OUTER_HEADER_LEN = 16


def parse_outer_frames(blob: bytes) -> list[dict]:
    """Return outer frames as dicts with offset, header fields, raw body."""
    frames = []
    offset = 0
    while offset + OUTER_HEADER_LEN <= len(blob):
        marker = blob[offset : offset + 4]
        size, outer_type = struct.unpack_from("<HH", blob, offset + 4)
        timestamp = blob[offset + 8 : offset + 16]
        if size < OUTER_HEADER_LEN or offset + size > len(blob):
            # Safety: a truncated frame stops parsing cleanly.
            break
        body = blob[offset + OUTER_HEADER_LEN : offset + size]
        frames.append(
            {
                "offset": offset,
                "marker": marker,
                "size": size,
                "type": outer_type,
                "timestamp": timestamp,
                "body": body,
            }
        )
        offset += size
    return frames


def frame_clean_length(blob: bytes) -> int:
    """Return the bytes covered by complete outer frames."""
    offset = 0
    n = len(blob)
    while offset + OUTER_HEADER_LEN <= n:
        size = struct.unpack_from("<H", blob, offset + 4)[0]
        if size < OUTER_HEADER_LEN or offset + size > n:
            break
        offset += size
    return offset


def maybe_inflate(body: bytes) -> bytes | None:
    """Return inflated bytes if body starts with zlib magic 78 9c, else None."""
    if len(body) < 2 or body[0] != 0x78 or body[1] != 0x9C:
        return None
    try:
        return zlib.decompress(body)
    except zlib.error:
        return None
