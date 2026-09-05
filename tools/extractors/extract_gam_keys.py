"""Extract hashed property entries and target markers from s2c opcode 0x0137."""

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

DEFAULT_OUT = Path(__file__).parent.parent.parent / "derived" / "gam_keys.json"

OPCODE_SET_ACTOR_PROPERTY = 0x0137
# Wire fact: the property block follows the 8-byte inner header and 8-byte actor-id/zero preamble.
PROPERTY_BLOCK_OFFSET = 16


def target_marker_length(lead: int) -> int | None:
    """Return the directly observed ASCII target length for a marker lead."""
    if 0x60 <= lead <= 0x9F:
        return lead - 0x60 if lead < 0x82 else lead - 0x82
    if lead == 0xA0:
        return 30
    if 0xA4 <= lead <= 0xE3:
        return lead - 0xA4
    return None


def parse_property_block(buf: bytes) -> tuple[list[dict], list[str], int]:
    """Parse the length-prefixed property and target-marker stream."""
    entries: list[dict] = []
    targets: list[str] = []
    if not buf:
        return entries, targets, 0
    declared_total = buf[0]
    end = min(len(buf), 1 + declared_total)
    i = 1
    safety = 0
    while i < end and safety < 512:
        safety += 1
        b = buf[i]
        if b == 0:
            break
        target_marker = target_marker_length(b)
        if target_marker is not None and i + 1 + target_marker <= end:
            possible = buf[i + 1 : i + 1 + target_marker]
            if all(32 <= x < 127 for x in possible):
                targets.append(possible.decode("ascii"))
                i += 1 + target_marker
                continue
        size = b
        if i + 5 + size > end:
            break
        prop_id = struct.unpack_from("<I", buf, i + 1)[0]
        value = buf[i + 5 : i + 5 + size]
        kind_label = {1: "byte", 2: "short", 4: "int", 8: "long"}.get(size, f"buf{size}")
        entries.append(
            {
                "id": prop_id,
                "idHex": f"0x{prop_id:08x}",
                "size": size,
                "kind": kind_label,
                "valueHex": value.hex(),
            }
        )
        i += 5 + size
    return entries, targets, declared_total


def walk_capture_gam(path: Path) -> list[dict]:
    """Return parsed GAM entries for one capture."""
    streams = reconstruct(path)
    out: list[dict] = []
    for direction, blob in streams.items():
        if direction != "s2c":
            continue
        for f in parse_outer_frames(blob):
            body = f["body"]
            if len(body) >= 2 and body[0] == 0x78 and body[1] == 0x9C:
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
                        if inner_opcode == OPCODE_SET_ACTOR_PROPERTY:
                            block = sub_body[PROPERTY_BLOCK_OFFSET:]
                            entries, targets, _ = parse_property_block(block)
                            out.append(
                                {
                                    "capture": path.name,
                                    "entries": entries,
                                    "targets": targets,
                                }
                            )
                offset += size
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    paths = default_corpus_paths()

    id_stats: dict[int, dict] = {}
    target_counts: Counter = Counter()
    target_captures: dict[str, set] = {}
    packet_count = 0
    captures_with_data = 0

    for p in paths:
        if not p.is_file():
            continue
        per_cap = walk_capture_gam(p)
        if per_cap:
            captures_with_data += 1
        for record in per_cap:
            packet_count += 1
            for ent in record["entries"]:
                pid = ent["id"]
                stats = id_stats.setdefault(
                    pid,
                    {
                        "count": 0,
                        "idHex": ent["idHex"],
                        "sizes": Counter(),
                        "captures": set(),
                        "sampleValues": [],
                    },
                )
                stats["count"] += 1
                stats["sizes"][ent["size"]] += 1
                stats["captures"].add(record["capture"])
                if len(stats["sampleValues"]) < 5:
                    stats["sampleValues"].append(ent["valueHex"])
            for t in record["targets"]:
                target_counts[t] += 1
                target_captures.setdefault(t, set()).add(record["capture"])

    ids_out = []
    for pid, s in id_stats.items():
        ids_out.append(
            {
                "id": pid,
                "idHex": s["idHex"],
                "count": s["count"],
                "sizes": dict(s["sizes"]),
                "captures": len(s["captures"]),
                "sampleValues": s["sampleValues"],
            }
        )
    ids_out.sort(key=lambda x: -x["count"])

    targets_out = []
    for t, c in target_counts.items():
        targets_out.append(
            {
                "target": t,
                "count": c,
                "captures": len(target_captures.get(t, [])),
            }
        )
    targets_out.sort(key=lambda x: -x["count"])

    out_struct = {
        "packetCount": packet_count,
        "capturesWithSetActorProperty": captures_with_data,
        "distinctIds": len(id_stats),
        "distinctTargets": len(target_counts),
        "ids": ids_out,
        "targets": targets_out,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, out_struct)
    print(f"wrote {out_path}")
    print(f"  packets parsed: {packet_count}")
    print(f"  distinct property ids: {len(id_stats)}")
    print(f"  distinct target strings: {len(target_counts)}")
    print()
    print("Top 10 property ids by frequency:")
    for entry in ids_out[:10]:
        sizes = ",".join(f"{s}B" for s in sorted(entry["sizes"].keys()))
        print(
            f"  {entry['idHex']}  count={entry['count']:>4}  sizes={sizes:<10}  "
            f"in {entry['captures']:>2} captures"
        )
    print()
    print("Top 10 target strings:")
    for entry in targets_out[:10]:
        print(f"  {entry['target']:<40}  count={entry['count']:>4}  in {entry['captures']:>2} captures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
