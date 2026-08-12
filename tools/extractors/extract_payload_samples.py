"""Sample capped wrapped-actor payloads by direction and opcode.

Samples include the inner header. Name-shaped and text ASCII is zero-filled
before emission so offsets and lengths remain stable.
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
import warnings
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _json_io import write_json  # noqa: E402

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from extract_streams import reconstruct, parse_outer_frames  # type: ignore
from extract_observations import (  # type: ignore
    SUB_EVENT_CLASS_ACTOR_WRAPPED,
    SUB_EVENT_HEADER_LEN,
    INNER_HEADER_LEN,
    default_corpus_paths,
)

# Bump when extraction changes output; record the version in pipelines/*.yaml and derived/*.meta.yaml.
GENERATOR_VERSION = "1"

DEFAULT_OUT = Path(__file__).parent.parent.parent / "derived" / "payload_samples.json"
# Sampling caps keep high-frequency opcodes from crowding out cross-capture variance evidence.
MAX_SAMPLES_PER_CAPTURE = 4
MAX_SAMPLES_PER_KEY = 60

_PRINTABLE_RUN_RE = re.compile(rb"[\x20-\x7e]+")
_LETTER_RUN_RE = re.compile(rb"[A-Za-z]{4,}")
# Privacy guard: name-shaped pairs catch short 1.x names such as "Aoi Alt" below the letter-run threshold.
_NAME_PAIR_RE = re.compile(rb"[A-Z][a-z]+[ '\-][A-Z][a-z]+")


def scrub_text_bytes(data: bytes) -> bytes:
    """Zero out printable-ASCII runs holding text or a name-shaped pair.

    The tracked digestion must carry no player names or chat text. A run is
    nulled if it contains 4+ consecutive letters or a capitalized word pair.
    Zero-filling in place (not stripping) preserves offsets and lengths for
    layout analysis.
    """

    def _scrub_run(m: re.Match) -> bytes:
        run = m.group(0)
        if _LETTER_RUN_RE.search(run) or _NAME_PAIR_RE.search(run):
            return b"\x00" * len(run)
        return run

    return _PRINTABLE_RUN_RE.sub(_scrub_run, data)


def walk_capture_payloads(path: Path) -> list[dict]:
    """Return one record per wrapped-actor sub-event."""
    streams = reconstruct(path)
    records: list[dict] = []
    for direction, blob in streams.items():
        if not blob:
            continue
        for f in parse_outer_frames(blob):
            body = f["body"]
            if direction == "s2c" and len(body) >= 2 and body[0] == 0x78 and body[1] == 0x9C:
                try:
                    body = zlib.decompress(body)
                except zlib.error:
                    continue
            offset = 0
            while offset + SUB_EVENT_HEADER_LEN <= len(body):
                size, ev_type = struct.unpack_from("<HH", body, offset)
                if size == 0 or size < SUB_EVENT_HEADER_LEN or offset + size > len(body):
                    break
                if ev_type == SUB_EVENT_CLASS_ACTOR_WRAPPED:
                    sub_body = body[offset + SUB_EVENT_HEADER_LEN : offset + size]
                    if len(sub_body) >= INNER_HEADER_LEN:
                        _is, inner_opcode = struct.unpack_from("<HH", sub_body, 0)
                        records.append(
                            {
                                "direction": direction,
                                "opcode": inner_opcode,
                                "sub_size": size,
                                "capture": path.name,
                                # Preserve raw spawn bytes here. Scrub only when emitting samples.
                                "bytes": sub_body.hex(),
                            }
                        )
                offset += size
    return records


def main() -> int:
    ap = argparse.ArgumentParser(description="Sample raw payload bytes per opcode.")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path.")
    ap.add_argument("--max-samples", type=int, default=MAX_SAMPLES_PER_KEY)
    args = ap.parse_args()

    paths = default_corpus_paths()

    samples: dict[tuple[str, int], list[dict]] = {}
    capture_count = 0
    for p in paths:
        if not p.is_file():
            continue
        capture_count += 1
        per_capture_counts: dict[tuple[str, int], int] = {}
        for r in walk_capture_payloads(p):
            key = (r["direction"], r["opcode"])
            existing = samples.setdefault(key, [])
            if len(existing) >= args.max_samples:
                continue
            if per_capture_counts.get(key, 0) >= MAX_SAMPLES_PER_CAPTURE:
                continue
            existing.append(
                {
                    "capture": r["capture"],
                    "sub_size": r["sub_size"],
                    "bytes": scrub_text_bytes(bytes.fromhex(r["bytes"])).hex(),
                }
            )
            per_capture_counts[key] = per_capture_counts.get(key, 0) + 1

    out_struct = {
        "captureCount": capture_count,
        "maxSamplesPerKey": args.max_samples,
        "samples": {
            "c2s": {},
            "s2c": {},
        },
    }
    for (direction, opcode), recs in samples.items():
        out_struct["samples"][direction][f"0x{opcode:04x}"] = {
            "opcode": opcode,
            "sampleCount": len(recs),
            "samples": recs,
        }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, out_struct)
    print(f"wrote {out_path}")
    print(f"  captures: {capture_count}")
    print(f"  total samples kept: {sum(len(v) for v in samples.values())}")
    print(f"  distinct (direction, opcode) keys: {len(samples)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
