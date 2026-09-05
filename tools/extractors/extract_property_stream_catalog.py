#!/usr/bin/env python3
"""Decode every retained typed actor-property stream record."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from extract_battle_results import load_scenarios  # type: ignore  # noqa: E402
from extract_gam_keys import parse_property_block, target_marker_length  # type: ignore  # noqa: E402
from extract_observations import INNER_HEADER_LEN, SUB_EVENT_CLASS_ACTOR_WRAPPED, SUB_EVENT_HEADER_LEN, default_corpus_paths  # type: ignore  # noqa: E402
from extract_streams import maybe_inflate, parse_outer_frames, reconstruct_lanes  # type: ignore  # noqa: E402

OPCODE = 0x0137
APP_OFFSET = INNER_HEADER_LEN + 8
OUT = REPO_ROOT / "studies" / "property-stream-hash-catalog" / "derived"
FIELDS = ["record_index", "capture", "scenario_id", "lane_index", "frame_index",
          "subevent_index", "packet_index", "record_in_packet", "stream_offset",
          "source_actor_id", "destination_actor_id", "target_marker", "property_hash", "value_width",
          "value_hex", "value_u_le", "value_f32"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_records(block: bytes) -> tuple[list[dict], int, bool, int]:
    rows: list[dict] = []
    if not block:
        return rows, 0, False, 0
    declared = block[0]
    end = min(len(block), 1 + declared)
    pos = 1
    target: str | None = None
    terminated = False
    while pos < end:
        lead = block[pos]
        if lead == 0:
            terminated = True
            break
        marker_len = target_marker_length(lead)
        if marker_len is not None and pos + 1 + marker_len <= end:
            candidate = block[pos + 1:pos + 1 + marker_len]
            if all(32 <= byte < 127 for byte in candidate):
                target = candidate.decode("ascii")
                pos += 1 + marker_len
                continue
        width = lead
        if pos + 5 + width > end:
            # Match the retained canonical parser: an incomplete tail ends the
            # usable record sequence without inventing a partial property.
            break
        prop_hash = struct.unpack_from("<I", block, pos + 1)[0]
        value = block[pos + 5:pos + 5 + width]
        row = {"stream_offset": pos, "target_marker": target or "",
               "property_hash": f"0x{prop_hash:08x}", "value_width": width,
               "value_hex": value.hex(), "value_u_le": int.from_bytes(value, "little"),
               "value_f32": ""}
        if width == 4:
            row["value_f32"] = format(struct.unpack("<f", value)[0], ".9g")
        rows.append(row)
        pos += 5 + width
    return rows, declared, terminated, pos


def scan() -> tuple[list[dict], dict]:
    scenarios = load_scenarios()
    rows: list[dict] = []
    packet_count = 0
    packet_by_capture: Counter[str] = Counter()
    declared_totals: Counter[int] = Counter()
    terminated_packets = 0
    fully_consumed_packets = 0
    residual_padding_bytes = 0
    nonzero_padding_packets = 0
    for capture in default_corpus_paths():
        packet_index = 0
        for lane_index, lane in enumerate(reconstruct_lanes(capture)):
            blob = lane["streams"].get("s2c", b"")
            for frame_index, frame in enumerate(parse_outer_frames(blob)):
                body = maybe_inflate(frame["body"])
                if body is None:
                    body = frame["body"]
                off = 0
                sub_index = 0
                while off + SUB_EVENT_HEADER_LEN <= len(body):
                    size, event_type = struct.unpack_from("<HH", body, off)
                    if not size or size < SUB_EVENT_HEADER_LEN or off + size > len(body):
                        break
                    if event_type == SUB_EVENT_CLASS_ACTOR_WRAPPED:
                        sub = body[off + SUB_EVENT_HEADER_LEN:off + size]
                        if len(sub) >= APP_OFFSET and struct.unpack_from("<H", sub, 2)[0] == OPCODE:
                            if size != 168 or len(sub[APP_OFFSET:]) != 136:
                                raise ValueError(f"{capture.name}: unexpected 0x0137 shape {size}/{len(sub[APP_OFFSET:])}")
                            block = sub[APP_OFFSET:]
                            parsed, declared, terminated, consumed = parse_records(block)
                            # Reconcile with the retained canonical parser before promoting detailed rows.
                            canonical, _, canonical_declared = parse_property_block(sub[APP_OFFSET:])
                            if canonical_declared != declared or len(canonical) != len(parsed):
                                raise ValueError(f"{capture.name}: parser reconciliation failed")
                            for expected, actual in zip(canonical, parsed):
                                if (expected["idHex"] != actual["property_hash"] or
                                        expected["size"] != actual["value_width"] or
                                        expected["valueHex"] != actual["value_hex"]):
                                    raise ValueError(f"{capture.name}: property row reconciliation failed")
                            packet_count += 1
                            packet_by_capture[capture.name] += 1
                            declared_totals[declared] += 1
                            terminated_packets += int(terminated)
                            fully_consumed_packets += int(consumed == 1 + declared)
                            padding = block[1 + declared:]
                            residual_padding_bytes += len(padding)
                            nonzero_padding_packets += int(any(padding))
                            source_actor = struct.unpack_from("<I", body, off + 4)[0]
                            destination_actor = struct.unpack_from("<I", body, off + 8)[0]
                            for record_in_packet, row in enumerate(parsed):
                                rows.append({"record_index": len(rows), "capture": capture.name,
                                             "scenario_id": scenarios.get(capture.name, "unassigned"),
                                             "lane_index": lane_index, "frame_index": frame_index,
                                             "subevent_index": sub_index, "packet_index": packet_index,
                                             "record_in_packet": record_in_packet,
                                             "source_actor_id": source_actor,
                                             "destination_actor_id": destination_actor, **row})
                            packet_index += 1
                    off += size
                    sub_index += 1
    by_hash: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_hash[row["property_hash"]].append(row)
    profiles = []
    for prop_hash, group in by_hash.items():
        widths = Counter(r["value_width"] for r in group)
        values = Counter(r["value_hex"] for r in group)
        profiles.append({"property_hash": prop_hash, "occurrences": len(group),
                         "captures": len({r["capture"] for r in group}),
                         "scenarios": len({r["scenario_id"] for r in group}),
                         "source_actors": len({r["source_actor_id"] for r in group}),
                         "destination_actors": len({r["destination_actor_id"] for r in group}),
                         "widths": {str(k): v for k, v in sorted(widths.items())},
                         "distinct_values": len(values),
                         "value_u_le_min": min(r["value_u_le"] for r in group),
                         "value_u_le_max": max(r["value_u_le"] for r in group),
                         "top_values": [{"value_hex": value, "count": count}
                                        for value, count in values.most_common(8)]})
    profiles.sort(key=lambda row: (-row["occurrences"], row["property_hash"]))
    accounting = {"schema_version": 1, "carrier_opcodes": ["0x0137"],
                  "packet_count": packet_count, "record_count": len(rows),
                  "distinct_hashes": len(by_hash), "captures": len(packet_by_capture),
                  "scenarios": len({r["scenario_id"] for r in rows}),
                  "width_distribution": {str(k): v for k, v in sorted(Counter(r["value_width"] for r in rows).items())},
                  "declared_total_distribution": {str(k): v for k, v in sorted(declared_totals.items())},
                  "zero_terminated_packets": terminated_packets,
                  "fully_consumed_declared_packets": fully_consumed_packets,
                  "residual_padding_bytes": residual_padding_bytes,
                  "nonzero_padding_packets": nonzero_padding_packets,
                  "packets_by_capture": dict(sorted(packet_by_capture.items())),
                  "hash_profiles": profiles,
                  "inputs": {"captures": [{"name": path.name, "sha256": sha256(path)} for path in default_corpus_paths()]},
                  "boundaries": ["value_u_le and value_f32 are parallel packet interpretations, not promoted property semantics.",
                                 "source_actor_id and destination_actor_id are wrapped subevent header fields; the packet-only study does not rename either as the property subject.",
                                 "target_marker is independent stream context."]}
    if (packet_count, len(rows), len(by_hash), len(packet_by_capture)) != (2014, 9307, 263, 37):
        raise ValueError(f"corpus reconciliation changed: {packet_count}/{len(rows)}/{len(by_hash)}/{len(packet_by_capture)}")
    if (
        fully_consumed_packets != packet_count
        or residual_padding_bytes != 164365
        or nonzero_padding_packets != 0
        or min(declared_totals) != 7
        or max(declared_totals) != 128
    ):
        raise ValueError("property-stream payload layout reconciliation changed")
    return rows, accounting


def csv_bytes(rows: list[dict]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows, accounting = scan()
    outputs = {"property-records.csv": csv_bytes(rows),
               "accounting.json": (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii")}
    stale = []
    for name, data in outputs.items():
        path = OUT / name
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                stale.append(str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    if stale:
        print("stale property-stream artifacts:\n  " + "\n  ".join(stale))
        return 1
    print(("verified" if args.check else "wrote") + f" {len(outputs)} property-stream artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
