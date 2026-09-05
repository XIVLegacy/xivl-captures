"""Join opcode 0x0137 property hashes to their active target markers."""

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
from extract_gam_keys import (  # type: ignore
    OPCODE_SET_ACTOR_PROPERTY,
    PROPERTY_BLOCK_OFFSET,
    target_marker_length,
)

# Bump when extraction changes output; record the version in pipelines/*.yaml and derived/*.meta.yaml.
GENERATOR_VERSION = "4"

DEFAULT_OUT = Path(__file__).parent.parent.parent / "derived" / "property_targets.json"


def parse_property_block_with_targets(buf: bytes) -> list[tuple[str | None, int, int, bytes]]:
    """Return property records with the active target, or ``None`` before a marker."""
    out: list[tuple[str | None, int, int, bytes]] = []
    if not buf:
        return out
    declared_total = buf[0]
    end = min(len(buf), 1 + declared_total)
    i = 1
    safety = 0
    current_target: str | None = None
    while i < end and safety < 512:
        safety += 1
        b = buf[i]
        if b == 0:
            break
        target_marker = target_marker_length(b)
        if target_marker is not None and i + 1 + target_marker <= end:
            possible = buf[i + 1 : i + 1 + target_marker]
            if all(32 <= x < 127 for x in possible):
                current_target = possible.decode("ascii")
                i += 1 + target_marker
                continue
        size = b
        if i + 5 + size > end:
            break
        prop_id = struct.unpack_from("<I", buf, i + 1)[0]
        value = bytes(buf[i + 5 : i + 5 + size])
        out.append((current_target, prop_id, size, value))
        i += 5 + size
    return out


def walk_capture(path: Path) -> list[dict]:
    streams = reconstruct(path)
    records: list[dict] = []
    blob = streams.get("s2c")
    if not blob:
        return records
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
                        for target, prop_id, prop_size, value in parse_property_block_with_targets(block):
                            records.append(
                                {
                                    "capture": path.name,
                                    "target": target,
                                    "id": prop_id,
                                    "size": prop_size,
                                    "value": value.hex(),
                                }
                            )
            offset += size
    return records


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    paths = default_corpus_paths()

    all_records: list[dict] = []
    for p in paths:
        if not p.is_file():
            continue
        all_records.extend(walk_capture(p))

    pair_stats: dict[tuple[str | None, int], dict] = {}
    target_stats: dict[str | None, dict] = {}
    untargeted_ids: set[int] = set()

    for rec in all_records:
        t = rec["target"]
        pid = rec["id"]
        sz = rec["size"]
        key = (t, pid)
        ps = pair_stats.setdefault(
            key,
            {
                "count": 0,
                "sizes": Counter(),
                "captures": set(),
                "sampleValues": [],
            },
        )
        ps["count"] += 1
        ps["sizes"][sz] += 1
        ps["captures"].add(rec["capture"])
        if len(ps["sampleValues"]) < 4:
            ps["sampleValues"].append(rec["value"])

        ts = target_stats.setdefault(
            t,
            {"recordCount": 0, "distinctIds": set(), "captures": set()},
        )
        ts["recordCount"] += 1
        ts["distinctIds"].add(pid)
        ts["captures"].add(rec["capture"])

        if t is None:
            untargeted_ids.add(pid)

    targets_out: list[dict] = []
    for t, ts in target_stats.items():
        ids_under = []
        for (tk, pid), ps in pair_stats.items():
            if tk != t:
                continue
            ids_under.append(
                {
                    "id": pid,
                    "idHex": f"0x{pid:08x}",
                    "count": ps["count"],
                    "sizes": dict(ps["sizes"]),
                    "captures": sorted(ps["captures"]),
                    "resolvedNames": [],
                    "sampleValues": ps["sampleValues"],
                }
            )
        ids_under.sort(key=lambda r: -r["count"])
        targets_out.append(
            {
                "target": t,
                "recordCount": ts["recordCount"],
                "distinctIds": len(ts["distinctIds"]),
                "captures": sorted(ts["captures"]),
                "ids": ids_under,
                "resolvedIdCount": 0,
                "unresolvedIdCount": len(ids_under),
            }
        )
    targets_out.sort(key=lambda x: (x["target"] is None, -x["recordCount"]))

    out_struct = {
        "totalRecords": len(all_records),
        "distinctTargets": len(target_stats),
        "distinctPropertyIds": len({pid for _, pid in pair_stats.keys()}),
        "targets": targets_out,
        "nameTableEntries": 0,
        "needsReverify": True,
        "reverifyMethod": "verification against the retail 1.23b client in a live session or direct corpus re-derivation",
        "reverifyReason": "Property-name assertions have not been confirmed by live validation or direct corpus re-derivation.",
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, out_struct)
    print(f"wrote {out_path}")
    print(f"  total records: {len(all_records)}")
    print(f"  distinct targets: {len(target_stats)}")
    print(f"  distinct (target, id) pairs: {len(pair_stats)}")
    print("  resolved-name table entries: 0")
    print()
    print("Top 10 targets by record count:")
    for t in targets_out[:10]:
        tname = t["target"] if t["target"] is not None else "(no target / implicit)"
        print(
            f"  {tname:<40}  records={t['recordCount']:>4}  "
            f"ids={t['distinctIds']:>3}  resolved=0/{t['unresolvedIdCount']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
