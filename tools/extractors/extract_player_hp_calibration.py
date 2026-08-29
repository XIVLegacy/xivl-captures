#!/usr/bin/env python3
"""Extract repeated same-frame player HP calibration leads."""

from __future__ import annotations

import argparse
import csv
import io
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT = REPO_ROOT / "studies" / "property-stream-hash-catalog" / "derived" / "property-records.csv"
OUT = REPO_ROOT / "studies" / "player-hp-calibration" / "derived" / "anchors.csv"
HEADER_ACTOR_ID = 43723073

# These labels identify exact property hashes only. They do not assign broader
# gameplay semantics to the values or to the wrapped subevent actor fields.
PROPERTY_SPECS = (
    ("state_mainSkill[0]", "0x7532ce24", 1, "state_mainSkill_0"),
    ("state_mainSkillLevel", "0x96063588", 2, "state_mainSkillLevel"),
    ("generalParameter[5]", "0x416571ac", 2, "generalParameter_5"),
    ("hpMax[0]", "0x7bcdfb69", 2, "hpMax_0"),
)
EXPECTED_LEADS = (
    ("lead-1", (4, 26, 102, 758), 6),
    ("lead-2", (3, 31, 110, 1016), 6),
)
FIELDS = (
    "occurrence_index", "repeated_lead", "lead_occurrence", "capture",
    "lane_index", "frame_index", "wrapped_source_actor_id",
    "wrapped_destination_actor_id", "packet_indices", "subevent_indices",
    "state_mainSkill_0", "state_mainSkillLevel", "generalParameter_5", "hpMax_0",
    "state_mainSkill_0_record_index", "state_mainSkillLevel_record_index",
    "generalParameter_5_record_index", "hpMax_0_record_index",
)


def extract_rows(input_path: Path = INPUT) -> list[dict[str, object]]:
    by_frame: defaultdict[tuple[str, int, int], list[dict[str, str]]] = defaultdict(list)
    target_hashes = {spec[1] for spec in PROPERTY_SPECS}
    with input_path.open(encoding="ascii", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "record_index", "capture", "lane_index", "frame_index", "subevent_index",
            "packet_index", "source_actor_id", "destination_actor_id", "property_hash",
            "value_width", "value_u_le",
        }
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError("property-record input is missing required columns")
        for row in reader:
            if (
                int(row["source_actor_id"]) == HEADER_ACTOR_ID
                and int(row["destination_actor_id"]) == HEADER_ACTOR_ID
                and row["property_hash"] in target_hashes
            ):
                key = (row["capture"], int(row["lane_index"]), int(row["frame_index"]))
                by_frame[key].append(row)

    candidates: list[tuple[tuple[str, int, int], dict[str, dict[str, str]]]] = []
    for key, rows in by_frame.items():
        hashes = Counter(row["property_hash"] for row in rows)
        if set(hashes) != target_hashes:
            continue
        if any(hashes[prop_hash] != 1 for prop_hash in target_hashes):
            raise ValueError(f"duplicate target property in complete frame {key}")
        candidates.append((key, {row["property_hash"]: row for row in rows}))

    candidates.sort(key=lambda item: item[0])
    expected = {values: count for _, values, count in EXPECTED_LEADS}
    observed = Counter(
        tuple(int(rows[prop_hash]["value_u_le"]) for _, prop_hash, _, _ in PROPERTY_SPECS)
        for _, rows in candidates
    )
    if observed != expected:
        raise ValueError(f"player HP lead reconciliation changed: {dict(observed)}")

    lead_by_values = {values: label for label, values, _ in EXPECTED_LEADS}
    lead_counts: Counter[str] = Counter()
    output: list[dict[str, object]] = []
    for occurrence_index, (key, rows) in enumerate(candidates, 1):
        values = tuple(int(rows[prop_hash]["value_u_le"]) for _, prop_hash, _, _ in PROPERTY_SPECS)
        lead = lead_by_values[values]
        lead_counts[lead] += 1
        for label, prop_hash, width, _ in PROPERTY_SPECS:
            actual_width = int(rows[prop_hash]["value_width"])
            if actual_width != width:
                raise ValueError(f"{label} changed width from {width} to {actual_width} in frame {key}")
        capture, lane_index, frame_index = key
        selected_rows = list(rows.values())
        rendered: dict[str, object] = {
            "occurrence_index": occurrence_index,
            "repeated_lead": lead,
            "lead_occurrence": lead_counts[lead],
            "capture": capture,
            "lane_index": lane_index,
            "frame_index": frame_index,
            "wrapped_source_actor_id": HEADER_ACTOR_ID,
            "wrapped_destination_actor_id": HEADER_ACTOR_ID,
            "packet_indices": " ".join(str(value) for value in sorted({int(row["packet_index"]) for row in selected_rows})),
            "subevent_indices": " ".join(str(value) for value in sorted({int(row["subevent_index"]) for row in selected_rows})),
        }
        for _, prop_hash, _, column in PROPERTY_SPECS:
            rendered[column] = int(rows[prop_hash]["value_u_le"])
            rendered[f"{column}_record_index"] = int(rows[prop_hash]["record_index"])
        output.append(rendered)
    return output


def csv_bytes(rows: list[dict[str, object]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--input", type=Path, default=INPUT)
    args = parser.parse_args()
    rendered = csv_bytes(extract_rows(args.input))
    if args.check:
        if not OUT.is_file() or OUT.read_bytes() != rendered:
            raise SystemExit(f"stale or missing: {OUT}")
        print("player HP calibration: anchors.csv verified")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(rendered)
    print("player HP calibration: anchors.csv written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
