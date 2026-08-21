"""Validate the 1.23b outer-frame compression invariant.

Marker byte 1 must identify whether the body inflates as zlib. Raw chat-lane
server frames are valid. Trailing capture bytes are reported but do not fail.

Usage:
    python tools/validate_framing.py <capture1.pcapng> [<capture2.pcapng> ...]

With no arguments, validates a default set of priority captures.
"""
from __future__ import annotations

import sys
import os
import warnings
import zlib
from pathlib import Path

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent / "extractors"))
from extract_streams import reconstruct, parse_outer_frames  # type: ignore


PRIORITY_CAPTURES = [
    "chat_say.pcapng",
    "chat_shout.pcapng",
    "inventory.pcapng",
    "idle_in_party.pcapng",
    "gridania_to_coerthas.pcapng",
]
DEFAULT_CAP_DIR = Path(os.environ.get(
    "XIVL_PCAP_OBJECTS_DIR",
    str(Path(__file__).resolve().parent.parent / "sources" / "pcap-1.23b" / "objects"),
))


def check(path: Path) -> dict:
    streams = reconstruct(path)
    out: dict = {"capture": path.name}
    for direction in ("c2s", "s2c"):
        blob = streams.get(direction)
        if not blob:
            out[direction] = {"status": "no stream"}
            continue
        frames = parse_outer_frames(blob)
        accounted = sum(f["size"] for f in frames)
        compressed_ok = compressed_raw = flag_mismatch = 0
        for f in frames:
            flag = f["marker"][1]
            body = f["body"]
            is_zlib = len(body) >= 2 and body[0] == 0x78 and body[1] == 0x9C
            inflates = False
            if is_zlib:
                try:
                    zlib.decompress(body)
                    inflates = True
                except zlib.error:
                    inflates = False
            if flag == 0x01:
                if inflates:
                    compressed_ok += 1
                else:
                    flag_mismatch += 1
            else:
                if inflates:
                    flag_mismatch += 1
                else:
                    compressed_raw += 1
        out[direction] = {
            "stream_bytes": len(blob),
            "frames": len(frames),
            "trailing_bytes": len(blob) - accounted,
            "compressed_ok": compressed_ok,
            "raw_bodies": compressed_raw,
            "flag_mismatch": flag_mismatch,
        }
    return out


def main() -> int:
    if len(sys.argv) > 1:
        paths = [Path(a) for a in sys.argv[1:]]
    else:
        paths = [DEFAULT_CAP_DIR / n for n in PRIORITY_CAPTURES]

    all_clean = True
    for p in paths:
        if not p.is_file():
            print(f"=== {p.name}: not found at {p} ===")
            all_clean = False
            continue
        r = check(p)
        print(f"=== {r['capture']} ===")
        for direction in ("c2s", "s2c"):
            v = r.get(direction)
            print(f"  {direction}: {v}")
            # Truncation is observable. Only a flag/body mismatch fails.
            if isinstance(v, dict) and v.get("flag_mismatch", 0) > 0:
                all_clean = False
        print()
    return 0 if all_clean else 1


if __name__ == "__main__":
    sys.exit(main())
