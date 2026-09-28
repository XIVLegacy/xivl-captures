"""Publish retail GAM hashes without external name assertions.

Writes an unresolved, packet-only dataset.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

from _json_io import write_json

# Bump when matching logic changes generated output.
GENERATOR_VERSION = "3"

GAM_KEYS_IN = Path(__file__).parent.parent / "derived" / "gam_keys.json"
DEFAULT_OUT = Path(__file__).parent.parent / "derived" / "gam_hash_names.json"


def murmur_hash2(key: str, seed: int = 0) -> int:
    """Apply the GAM property-name MurmurHash2 variant."""
    data = key.encode("ascii")
    n = len(key)
    m = 0xFFFFFFFF & 0x5BD1E995
    r = 24
    h = (seed ^ n) & 0xFFFFFFFF
    data_index = n - 4
    remaining = n
    mask32 = 0xFFFFFFFF

    while remaining >= 4:
        h = (h * m) & mask32
        k = struct.unpack_from("<I", data, data_index)[0]
        k = (
            ((k >> 24) & 0xFF)
            | ((k << 8) & 0xFF0000)
            | ((k >> 8) & 0xFF00)
            | ((k << 24) & 0xFF000000)
        ) & mask32
        k = (k * m) & mask32
        k ^= (k >> r) & mask32
        k = (k * m) & mask32
        h ^= k
        h &= mask32
        data_index -= 4
        remaining -= 4

    # This variant indexes the original buffer with the remaining length.
    if remaining == 3:
        h ^= (data[0] << 16) & mask32
        h ^= (data[remaining - 2] << 8) & mask32
        h ^= data[remaining - 1]
        h = (h * m) & mask32
    elif remaining == 2:
        h ^= (data[remaining - 2] << 8) & mask32
        h ^= data[remaining - 1]
        h = (h * m) & mask32
    elif remaining == 1:
        h ^= data[remaining - 1]
        h = (h * m) & mask32

    h ^= (h >> 13) & mask32
    h = (h * m) & mask32
    h ^= (h >> 15) & mask32
    return h & mask32


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=str(GAM_KEYS_IN))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    sanity = murmur_hash2("charaWork.parameterSave.hp[0]")
    print(f"murmur('charaWork.parameterSave.hp[0]') = 0x{sanity:08x}")

    gam = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    retail_ids = {entry["id"]: entry for entry in gam["ids"]}

    # Preserve widths so consumers need not rejoin gam_keys.json.
    unresolved: list[dict] = []
    for h, entry in retail_ids.items():
        unresolved.append(
            {
                "idHex": entry["idHex"],
                "count": entry["count"],
                "captures": entry["captures"],
                "sizes": entry.get("sizes", {}),
                "sampleValues": entry.get("sampleValues", [])[:2],
            }
        )

    unresolved.sort(key=lambda x: -x["count"])

    out_struct = {
        "candidatesTried": 0,
        "retailHashes": len(retail_ids),
        "resolved": [],
        "unresolved": unresolved,
        "needsReverify": True,
        "reverifyMethod": "verification against the retail 1.23b client in a live session or direct corpus re-derivation",
        "reverifyReason": "Property-name assertions have not been confirmed by live validation or direct corpus re-derivation.",
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, out_struct)

    print(f"wrote {out_path}")
    print("  candidates tried: 0")
    print(f"  retail hashes: {len(retail_ids)}")
    print("  resolved: 0  (0.0%)")
    print(f"  unresolved: {len(unresolved)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
