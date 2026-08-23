"""Build per-capture opcode motif summaries.

Each reconstructed connection retains stream order, but connection blocks are
concatenated deterministically. Cross-direction chronology is approximate, and
derived/sequences.json collapses consecutive same-key runs.

Run: python tools/extractors/extract_sequences.py
"""

from __future__ import annotations

import argparse
import struct
import sys
import warnings
import zlib
from collections import Counter
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
GENERATOR_VERSION = "2"

DEFAULT_OUT = Path(__file__).parent.parent.parent / "derived" / "sequences.json"

# Motif output contract: require cross-capture recurrence and segregate movement/ping-only background.
MOTIF_LENGTHS = (3, 4, 5, 6)
MIN_CAPTURE_COUNT = 5
# Movement/ping-only motifs are emitted separately.
NOISE_OPCODES = {0x0001, 0x00CA, 0x00CF, 0x00D0}


def walk_capture_sequence(path: Path) -> list[tuple[str, int]]:
    """Return a collapsed sequence with deterministic connection blocks."""
    streams = reconstruct(path)
    seq: list[tuple[str, int, int]] = []
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
                        _is, op = struct.unpack_from("<HH", sub_body, 0)
                        seq.append((f["offset"], direction, op))
                offset += size
    # Stable merge preserves each direction's order but cannot establish cross-direction timing.
    seq.sort(key=lambda entry: (entry[0], entry[1]))
    return [(d, op) for _, d, op in seq]


def collapse_runs(seq: list[tuple[str, int]]) -> list[tuple[str, int, int]]:
    """Collapse consecutive same-key entries into (direction, opcode, run_length)."""
    out: list[tuple[str, int, int]] = []
    for key in seq:
        if out and out[-1][0] == key[0] and out[-1][1] == key[1]:
            out[-1] = (out[-1][0], out[-1][1], out[-1][2] + 1)
        else:
            out.append((key[0], key[1], 1))
    return out


def find_motifs(
    captures: dict[str, list[tuple[str, int]]],
    length: int,
    min_captures: int,
) -> list[dict]:
    """Sliding-window motif counter at a given length."""
    motif_capture_set: dict[tuple, set[str]] = {}
    motif_total_count: Counter = Counter()

    for cap_name, seq in captures.items():
        seen_in_this_cap: set[tuple] = set()
        for i in range(len(seq) - length + 1):
            window = tuple(seq[i : i + length])
            motif_total_count[window] += 1
            seen_in_this_cap.add(window)
        for w in seen_in_this_cap:
            motif_capture_set.setdefault(w, set()).add(cap_name)

    results: list[dict] = []
    for window, caps in motif_capture_set.items():
        if len(caps) < min_captures:
            continue
        results.append(
            {
                "length": length,
                "motif": [{"direction": d, "opcode": op, "opcodeHex": f"0x{op:04x}"} for d, op in window],
                "captureCount": len(caps),
                "totalOccurrences": motif_total_count[window],
                "exampleCaptures": sorted(caps)[:5],
            }
        )
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    paths = default_corpus_paths()

    captures: dict[str, list[tuple[str, int]]] = {}
    for p in paths:
        if not p.is_file():
            continue
        captures[p.name] = walk_capture_sequence(p)

    all_motifs: list[dict] = []
    for L in MOTIF_LENGTHS:
        all_motifs.extend(find_motifs(captures, L, MIN_CAPTURE_COUNT))

    def is_background(m: dict) -> bool:
        return all(x["opcode"] in NOISE_OPCODES for x in m["motif"])

    interesting = [m for m in all_motifs if not is_background(m)]
    background = [m for m in all_motifs if is_background(m)]

    # Determinism: opcode-signature tiebreak prevents hash-seed-dependent truncation.
    def sort_key(m: dict) -> tuple:
        sig = tuple((x["direction"], x["opcode"]) for x in m["motif"])
        return (-m["length"], -m["captureCount"], -m["totalOccurrences"], sig)

    interesting.sort(key=sort_key)
    background.sort(key=sort_key)

    out_struct = {
        "captureCount": len(captures),
        "motifLengths": list(MOTIF_LENGTHS),
        "minCaptureCount": MIN_CAPTURE_COUNT,
        "noiseOpcodes": [f"0x{op:04x}" for op in sorted(NOISE_OPCODES)],
        "perCapture": {
            name: {
                "length": len(seq),
                "collapsed": [
                    {"direction": d, "opcodeHex": f"0x{op:04x}", "runLength": rl}
                    for d, op, rl in collapse_runs(seq)
                ],
            }
            for name, seq in captures.items()
        },
        "interestingMotifs": interesting[:200],
        "backgroundMotifs": background[:50],
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, out_struct)
    print(
        f"wrote {out_path}  ({len(captures)} captures, {len(all_motifs)} motifs, "
        f"{len(interesting)} interesting + {len(background)} background)"
    )

    print()
    print("Top interesting motifs by capture coverage:")
    for m in interesting[:15]:
        chain = " -> ".join(f"{x['direction']} {x['opcodeHex']}" for x in m["motif"])
        print(f"  L={m['length']} in {m['captureCount']:>2}/{len(captures)} captures  {chain}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
