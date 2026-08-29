#!/usr/bin/env python3
"""Join gear item and equipment-link carriers to 0x0137 property records."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import struct
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from extract_content_samples import parse_inventory_items  # type: ignore  # noqa: E402
from extract_observations import (  # type: ignore  # noqa: E402
    INNER_HEADER_LEN,
    SUB_EVENT_CLASS_ACTOR_WRAPPED,
    SUB_EVENT_HEADER_LEN,
)
from extract_streams import maybe_inflate, parse_outer_frames, reconstruct_lanes  # type: ignore  # noqa: E402

CAPTURE_ROOT = REPO_ROOT / "sources" / "pcap-1.23b" / "objects"
PROPERTY_RECORDS = (
    REPO_ROOT / "studies" / "property-stream-hash-catalog" / "derived" / "property-records.csv"
)
OUT = REPO_ROOT / "studies" / "equipment-property-correlation" / "derived"

ITEM_COUNTS = {0x0148: 1, 0x0149: 8}
GEAR_STREAM_OPCODES = {0x018F, 0x0190, 0x0191}
GENERAL_PARAMETER_18_HASH = "0x8cae90db"

CAPTURE_SPECS = (
    {
        "capture": "change_bodyarmor.pcapng",
        "sha256": "55ee6035d24e80b97c9354a0800b86a52d0a99e1200cf6875a5b56009215021a",
        "verdict": "AFTER-ONLY",
        "catalog_item_id": "0x007A88D7",
        "equipment_slot": 10,
        "item_slot": 140,
        "property_hash": GENERAL_PARAMETER_18_HASH,
        "property_label": "generalParameter[18]",
        "after_record_index": 36,
        "after_frame_index": 20,
        "after_value": 147,
        "projection_range": "33-37",
        "projection_count": 5,
    },
    {
        "capture": "change_helm.pcapng",
        "sha256": "af1e465076c3acf6188f24f084622b22beccc932bb96effd517b2d9a44606e08",
        "verdict": "CORRELATED",
        "catalog_item_id": "0x007A3F58",
        "equipment_slot": 8,
        "item_slot": 113,
        "property_hash": GENERAL_PARAMETER_18_HASH,
        "property_label": "generalParameter[18]",
        "before_record_index": 43,
        "before_frame_index": 16,
        "before_value": 141,
        "after_record_index": 44,
        "after_frame_index": 30,
        "after_value": 161,
        "projection_range": "44",
        "projection_count": 1,
        "old_item_id": "0x007A3D64",
        "old_item_slot": 131,
    },
    {
        "capture": "gear_changesoul.pcapng",
        "sha256": "62af2cde3a4683fba3e09cc3dfed8001d74303b120381de577b05df492926780",
        "verdict": "NO-GO",
    },
    {
        "capture": "gear_changeweapon.pcapng",
        "sha256": "3eec2c2993feeb2b8c47c1e1f553335638a7262ec13b561e2d52d768f0798080",
        "verdict": "AFTER-ONLY",
        "catalog_item_id": "0x003D7E3D",
        "equipment_slot": 0,
        "item_slot": 79,
        "property_hash": GENERAL_PARAMETER_18_HASH,
        "property_label": "generalParameter[18]",
        "after_record_index": 593,
        "after_frame_index": 16,
        "after_value": 169,
        "projection_range": "575-649",
        "projection_count": 75,
    },
)

FIELDS = (
    "capture", "sha256", "verdict", "lane_index", "property_hash", "property_label",
    "before_record_index", "before_frame_index", "before_value",
    "after_record_index", "after_frame_index", "after_value",
    "property_projection_record_range", "property_projection_record_count",
    "item_opcode", "item_frame_index", "item_subevent_index",
    "item_record_index", "catalog_item_id", "item_slot",
    "link_frame_index", "link_subevent_index", "equipment_slot",
    "linked_item_slot", "old_item_id", "old_item_slot",
    "old_slot_link_status", "gear_stream_0x018f_0x0191",
)


def _scan_capture(path: Path) -> dict[str, list | set]:
    items: list[dict] = []
    links: list[dict] = []
    opcodes: set[int] = set()
    for lane_index, lane in enumerate(reconstruct_lanes(path)):
        for direction in ("c2s", "s2c"):
            for frame_index, frame in enumerate(parse_outer_frames(lane["streams"].get(direction, b""))):
                inflated = maybe_inflate(frame["body"])
                body = inflated if inflated is not None else frame["body"]
                offset = 0
                subevent_index = 0
                while offset + SUB_EVENT_HEADER_LEN <= len(body):
                    size, event_type = struct.unpack_from("<HH", body, offset)
                    if not size or size < SUB_EVENT_HEADER_LEN or offset + size > len(body):
                        break
                    if event_type == SUB_EVENT_CLASS_ACTOR_WRAPPED:
                        sub = body[offset + SUB_EVENT_HEADER_LEN:offset + size]
                        if len(sub) >= INNER_HEADER_LEN:
                            opcode = struct.unpack_from("<H", sub, 2)[0]
                            opcodes.add(opcode)
                            if direction == "s2c" and opcode in ITEM_COUNTS:
                                for item_index, item in enumerate(
                                    parse_inventory_items(sub, ITEM_COUNTS[opcode])
                                ):
                                    items.append({
                                        **item,
                                        "opcode": opcode,
                                        "lane_index": lane_index,
                                        "frame_index": frame_index,
                                        "subevent_index": subevent_index,
                                        "item_record_index": item_index,
                                    })
                            elif direction == "s2c" and opcode == 0x014D:
                                application = sub[INNER_HEADER_LEN:]
                                if len(application) != 16:
                                    raise ValueError(f"{path.name}: unexpected 0x014D application size")
                                equipment_slot, item_slot = struct.unpack_from("<HH", application, 8)
                                links.append({
                                    "lane_index": lane_index,
                                    "frame_index": frame_index,
                                    "subevent_index": subevent_index,
                                    "equipment_slot": equipment_slot,
                                    "item_slot": item_slot,
                                })
                    offset += size
                    subevent_index += 1
    return {"items": items, "links": links, "opcodes": opcodes}


def _load_property_rows(path: Path = PROPERTY_RECORDS) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    with path.open(encoding="ascii", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"record_index", "capture", "lane_index", "frame_index", "property_hash", "value_u_le"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError("property-record input is missing required columns")
        for row in reader:
            grouped.setdefault(row["capture"], []).append(row)
    return grouped


def _one(rows: list[dict], **values: object) -> dict:
    matches = [row for row in rows if all(row.get(key) == value for key, value in values.items())]
    if len(matches) != 1:
        raise ValueError(f"expected one matching carrier for {values}, found {len(matches)}")
    return matches[0]


def extract_rows(
    capture_root: Path = CAPTURE_ROOT,
    property_path: Path = PROPERTY_RECORDS,
) -> list[dict[str, object]]:
    properties = _load_property_rows(property_path)
    output: list[dict[str, object]] = []
    for spec in CAPTURE_SPECS:
        capture = str(spec["capture"])
        path = capture_root / capture
        if hashlib.sha256(path.read_bytes()).hexdigest() != spec["sha256"]:
            raise ValueError(f"{capture}: source hash changed")
        scanned = _scan_capture(path)
        items = scanned["items"]
        links = scanned["links"]
        opcodes = scanned["opcodes"]
        if opcodes & GEAR_STREAM_OPCODES:
            raise ValueError(f"{capture}: unexpected 0x018F-0x0191 gear stream")

        row: dict[str, object] = {field: "" for field in FIELDS}
        row.update({
            "capture": capture,
            "sha256": spec["sha256"],
            "verdict": spec["verdict"],
            "gear_stream_0x018f_0x0191": "absent",
        })
        if spec["verdict"] == "NO-GO":
            if items or links or not properties.get(capture):
                raise ValueError(f"{capture}: NO-GO carrier boundary changed")
            row["old_slot_link_status"] = "not-applicable"
            output.append(row)
            continue

        link = _one(links, equipment_slot=spec["equipment_slot"], item_slot=spec["item_slot"])
        item = _one(items, itemId=int(str(spec["catalog_item_id"]), 16), slot=spec["item_slot"])
        if item["lane_index"] != link["lane_index"]:
            raise ValueError(f"{capture}: item and equipment link moved to different lanes")
        if (item["frame_index"], item["subevent_index"]) >= (
            link["frame_index"], link["subevent_index"]
        ):
            raise ValueError(f"{capture}: equipment link no longer follows its item record")
        later_properties = [
            prop for prop in properties.get(capture, [])
            if int(prop["lane_index"]) == link["lane_index"]
            and int(prop["frame_index"]) > link["frame_index"]
        ]
        first_property_frame = min(int(prop["frame_index"]) for prop in later_properties)
        projection = [
            prop for prop in later_properties
            if int(prop["frame_index"]) == first_property_frame
        ]
        observed_range = (
            str(projection[0]["record_index"])
            if len(projection) == 1
            else f"{projection[0]['record_index']}-{projection[-1]['record_index']}"
        )
        if observed_range != spec["projection_range"] or len(projection) != spec["projection_count"]:
            raise ValueError(f"{capture}: first post-link property projection changed")
        if spec["verdict"] == "AFTER-ONLY":
            post_hashes = {prop["property_hash"] for prop in projection}
            comparable_before = [
                prop for prop in properties[capture]
                if int(prop["lane_index"]) == link["lane_index"]
                and int(prop["frame_index"]) < link["frame_index"]
                and prop["property_hash"] in post_hashes
            ]
            if comparable_before:
                raise ValueError(f"{capture}: comparable before properties now exist")
            after = _one(
                properties[capture],
                property_hash=spec["property_hash"],
                record_index=str(spec["after_record_index"]),
            )
            observed_after = (int(after["frame_index"]), int(after["value_u_le"]))
            if observed_after != (spec["after_frame_index"], spec["after_value"]):
                raise ValueError(f"{capture}: after-only property value changed")
            row.update({
                "property_hash": spec["property_hash"],
                "property_label": spec["property_label"],
                "after_record_index": after["record_index"],
                "after_frame_index": after["frame_index"],
                "after_value": after["value_u_le"],
            })
        row.update({
            "lane_index": link["lane_index"],
            "property_projection_record_range": observed_range,
            "property_projection_record_count": len(projection),
            "item_opcode": f"0x{item['opcode']:04X}",
            "item_frame_index": item["frame_index"],
            "item_subevent_index": item["subevent_index"],
            "item_record_index": item["item_record_index"],
            "catalog_item_id": spec["catalog_item_id"],
            "item_slot": item["slot"],
            "link_frame_index": link["frame_index"],
            "link_subevent_index": link["subevent_index"],
            "equipment_slot": link["equipment_slot"],
            "linked_item_slot": link["item_slot"],
            "old_item_id": spec.get("old_item_id", ""),
            "old_item_slot": spec.get("old_item_slot", ""),
        })

        if spec["verdict"] == "CORRELATED":
            before = _one(
                properties[capture],
                property_hash=spec["property_hash"],
                record_index=str(spec["before_record_index"]),
            )
            after = _one(
                properties[capture],
                property_hash=spec["property_hash"],
                record_index=str(spec["after_record_index"]),
            )
            observed = (
                int(before["frame_index"]), int(before["value_u_le"]),
                int(after["frame_index"]), int(after["value_u_le"]),
            )
            expected = (
                spec["before_frame_index"], spec["before_value"],
                spec["after_frame_index"], spec["after_value"],
            )
            if observed != expected:
                raise ValueError(f"{capture}: property change reconciliation changed")
            old = _one(items, itemId=int(str(spec["old_item_id"]), 16), slot=spec["old_item_slot"])
            if any(
                candidate["equipment_slot"] == spec["equipment_slot"]
                and candidate["frame_index"] < link["frame_index"]
                for candidate in links
            ):
                raise ValueError(f"{capture}: old slot link is no longer missing")
            if old["frame_index"] >= int(before["frame_index"]):
                raise ValueError(f"{capture}: old item no longer precedes the before property")
            row.update({
                "property_hash": spec["property_hash"],
                "property_label": spec["property_label"],
                "before_record_index": before["record_index"],
                "before_frame_index": before["frame_index"],
                "before_value": before["value_u_le"],
                "after_record_index": after["record_index"],
                "after_frame_index": after["frame_index"],
                "after_value": after["value_u_le"],
                "old_slot_link_status": "missing",
            })
        output.append(row)
    return output


def csv_bytes(rows: list[dict[str, object]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("ascii")


def evidence_map_bytes(rows: list[dict[str, object]]) -> bytes:
    by_capture = {str(row["capture"]): row for row in rows}
    helm = by_capture["change_helm.pcapng"]
    lines = [
        "# Equipment property correlation evidence map",
        "",
        "## Deterministic matrix",
        "",
        "`matrix.csv` is exhaustive for the four named gear captures. Packet locators",
        "for item records and links are s2c and use reconstructed lane, outer frame,",
        "and subevent indices. Property locators use the canonical record indices from",
        "the 0x0137 property-stream study.",
        "",
        "| Capture | Verdict | Item record | 0x014D link | Property evidence |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        if row["verdict"] == "NO-GO":
            item = "absent"
            link = "absent"
            prop = "unjoined; no item/link carrier"
        else:
            item = (
                f"{row['item_opcode']} lane {row['lane_index']} frame {row['item_frame_index']} subevent "
                f"{row['item_subevent_index']}; {row['catalog_item_id']} item slot {row['item_slot']}"
            )
            link = (
                f"lane {row['lane_index']} frame {row['link_frame_index']} subevent "
                f"{row['link_subevent_index']}; "
                f"equipment slot {row['equipment_slot']} -> item slot {row['linked_item_slot']}"
            )
            if row["verdict"] == "CORRELATED":
                prop = (
                    f"{row['property_label']} {row['before_value']} -> {row['after_value']}; "
                    f"records {row['before_record_index']} and {row['after_record_index']}"
                )
            else:
                prop = (
                    f"{row['property_label']} after {row['after_value']} at record "
                    f"{row['after_record_index']}; before value missing; projection records "
                    f"{row['property_projection_record_range']}"
                )
        lines.append(f"| `{row['capture']}` | {row['verdict']} | {item} | {link} | {prop} |")
    lines.extend([
        "",
        "## Promoted facts",
        "",
        f"The helm capture changes `{helm['property_label']}` from {helm['before_value']} "
        f"to {helm['after_value']}. The new catalog item `{helm['catalog_item_id']}` is "
        f"linked from equipment slot {helm['equipment_slot']} to item slot {helm['item_slot']}.",
        "The old catalog item is present at item slot 131, but no earlier explicit",
        "equipment-slot-8 link exists in the capture.",
        "",
        "Body and weapon each have an item/link join followed by a property projection,",
        "but neither capture supplies comparable before values. Soul has 0x0137 property",
        "traffic but no 0x0148/0x0149 item record and no 0x014D link, so it is NO-GO.",
        "",
        "## Claim boundary",
        "",
        "`generalParameter[18]` is an exact indexed field label only. This study does",
        "not assign gameplay meaning to that index or to any other generalParameter",
        "index. It does not turn after-only body or weapon projections into changes.",
        "The actual four captures contain no 0x018F, 0x0190, or 0x0191 stream.",
        "",
        "## Unresolved fields",
        "",
        "The body and weapon before-side property values remain missing. The helm old",
        "item's explicit equipment-slot-8 link remains missing. Soul cannot be joined",
        "to an item or equipment link within the retained capture.",
        "",
    ])
    return "\n".join(lines).encode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows = extract_rows()
    outputs = {
        "matrix.csv": csv_bytes(rows),
        "evidence-map.md": evidence_map_bytes(rows),
    }
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
        print("stale equipment-property artifacts:\n  " + "\n  ".join(stale))
        return 1
    print(("verified" if args.check else "wrote") + f" {len(outputs)} equipment-property artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
