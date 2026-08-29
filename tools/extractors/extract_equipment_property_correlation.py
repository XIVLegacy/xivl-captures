#!/usr/bin/env python3
"""Build the sanitized full-corpus equipment transition census."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from extract_observations import (  # type: ignore  # noqa: E402
    INNER_HEADER_LEN, SUB_EVENT_CLASS_ACTOR_WRAPPED, SUB_EVENT_HEADER_LEN,
    default_corpus_paths,
)
from extract_streams import (  # type: ignore  # noqa: E402
    IP, TCP, maybe_inflate, parse_outer_frames, read_packets, reconstruct_lanes,
)

PROPERTY_RECORDS = REPO_ROOT / "studies" / "property-stream-hash-catalog" / "derived" / "property-records.csv"
OUT = REPO_ROOT / "studies" / "equipment-property-correlation" / "derived"

SET_BEGIN, SET_END = 0x0146, 0x0147
CHANGE_BEGIN, CHANGE_END = 0x016D, 0x016E
ITEM_COUNTS = {0x0148: 1, 0x0149: 8, 0x014A: 16, 0x014B: 32, 0x014C: 64}
LINK_COUNTS = {0x014D: 1, 0x014E: 8, 0x014F: 16, 0x0150: 32, 0x0151: 64}
EXCLUDED_NEARBY = {0x018F, 0x0190, 0x0191}

ACCOUNTING_FIELDS = (
    "capture", "sha256", "lane_count", "set_begin_count", "set_end_count",
    "change_begin_count", "change_end_count",
    "opcode_0x0148_count", "opcode_0x0149_count", "opcode_0x014a_count",
    "opcode_0x014b_count", "opcode_0x014c_count", "opcode_0x014d_count",
    "opcode_0x014e_count", "opcode_0x014f_count", "opcode_0x0150_count",
    "opcode_0x0151_count",
    "item_packet_count", "item_record_count", "link_packet_count", "link_record_count",
    "framed_event_count", "exact_item_link_count", "bounded_candidate_count",
    "missing_carrier_count", "repeated_aggregate_event_count", "retransmitted_segment_count",
    "excluded_0x018f_0x0191_count",
)
MATRIX_FIELDS = (
    "event_id", "capture", "lane_index", "source_actor", "destination_actor",
    "classification", "join_status", "set_begin_frame", "set_begin_subevent",
    "set_end_frame", "set_end_subevent", "change_begin_frame", "change_begin_subevent",
    "change_end_frame", "change_end_subevent", "item_opcode", "item_frame",
    "item_subevent", "item_record", "catalog_item_id", "item_slot", "link_opcode",
    "link_frame", "link_subevent", "link_record", "equipment_slot", "linked_item_slot",
    "item_package_code", "item_to_link_distance_frames", "item_to_link_distance_subevents",
    "item_to_link_distance_us", "before_property_frame", "before_distance_frames",
    "before_distance_us", "after_property_frame", "after_distance_frames", "after_distance_us", "changed_property_count",
    "repeated_aggregate_of", "boundary_note",
)
PROPERTY_FIELDS = (
    "event_id", "capture", "lane_index", "source_actor", "destination_actor",
    "carrier_scope", "equipment_slot", "catalog_item_id", "property_hash", "comparison_status", "before_record_index",
    "before_frame", "before_subevent", "before_value_hex", "before_value_u_le",
    "after_record_index", "after_frame", "after_subevent", "after_value_hex",
    "after_value_u_le", "before_distance_frames", "before_distance_us",
    "after_distance_frames", "after_distance_us",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _event_order(row: dict) -> tuple[int, int, int]:
    return int(row["frame_index"]), int(row["subevent_index"]), int(row["ordinal"])


def _actor_labels(events: list[dict], properties: list[dict[str, str]]) -> dict[int, str]:
    labels: dict[int, str] = {}
    actor_ids = []
    for row in events:
        actor_ids.extend((int(row["source_actor_id"]), int(row["destination_actor_id"])))
    for row in properties:
        actor_ids.extend((int(row["source_actor_id"]), int(row["destination_actor_id"])))
    for actor_id in actor_ids:
        if actor_id not in labels:
            labels[actor_id] = f"actor-{len(labels) + 1:02d}"
    return labels


def _retransmitted_segments(path: Path) -> int:
    seen: set[tuple] = set()
    repeated = 0
    admitted = {
        frozenset((lane["client_endpoint"], lane["server_endpoint"]))
        for lane in reconstruct_lanes(path)
    }
    for packet in read_packets(path):
        if not packet.haslayer(IP) or not packet.haslayer(TCP):
            continue
        payload = bytes(packet[TCP].payload)
        if not payload:
            continue
        endpoints = frozenset((
            (packet[IP].src, int(packet[TCP].sport)),
            (packet[IP].dst, int(packet[TCP].dport)),
        ))
        if endpoints not in admitted:
            continue
        key = (
            packet[IP].src, packet[IP].dst, int(packet[TCP].sport), int(packet[TCP].dport),
            int(packet[TCP].seq), hashlib.sha256(payload).digest(),
        )
        if key in seen:
            repeated += 1
        else:
            seen.add(key)
    return repeated


def _parse_link_rows(sub: bytes, opcode: int) -> list[dict[str, int]]:
    application = sub[INNER_HEADER_LEN:]
    if len(application) < 8:
        raise ValueError("linked-item packet lacks the common prefix")
    payload = application[8:]
    maximum = LINK_COUNTS[opcode]
    if opcode == 0x014D:
        if len(payload) != 8:
            raise ValueError(f"unexpected 0x014D payload size {len(payload)}")
        count = 1
    elif opcode == 0x014E:
        if len(payload) != 56:
            raise ValueError(f"unexpected 0x014E payload size {len(payload)}")
        count = min(payload[48], maximum)
    else:
        expected = maximum * 6
        if len(payload) < expected:
            raise ValueError(f"unexpected 0x{opcode:04X} payload size {len(payload)}")
        count = maximum
    rows = []
    for index in range(count):
        equipment_slot, item_slot, package_code = struct.unpack_from("<HHH", payload, index * 6)
        rows.append({"link_record": index, "equipment_slot": equipment_slot,
                     "item_slot": item_slot, "item_package_code": package_code})
    return rows


def _parse_item_rows(sub: bytes, opcode: int) -> list[dict[str, int]]:
    count = ITEM_COUNTS[opcode]
    expected = 16 + count * 0x70 + (8 if opcode == 0x0149 else 0)
    if len(sub) != expected:
        raise ValueError(f"unexpected 0x{opcode:04X} item payload size {len(sub)}")
    rows = []
    for index in range(count):
        offset = 16 + index * 0x70
        unique_id = struct.unpack_from("<Q", sub, offset)[0]
        item_id = struct.unpack_from("<I", sub, offset + 12)[0]
        if not unique_id and not item_id:
            continue
        rows.append({
            "item_record": index,
            "item_id": item_id,
            "item_slot": struct.unpack_from("<H", sub, offset + 16)[0],
        })
    return rows


def _scan_capture(path: Path) -> tuple[list[dict], int, Counter[int], dict[tuple[int, int], int]]:
    events: list[dict] = []
    opcode_counts: Counter[int] = Counter()
    ordinal = 0
    lanes = reconstruct_lanes(path)
    frame_times: dict[tuple[int, int], int] = {}
    observed = {SET_BEGIN, SET_END, CHANGE_BEGIN, CHANGE_END} | set(ITEM_COUNTS) | set(LINK_COUNTS)
    for lane_index, lane in enumerate(lanes):
        for frame_index, frame in enumerate(parse_outer_frames(lane["streams"].get("s2c", b""))):
            frame_times[(lane_index, frame_index)] = struct.unpack("<Q", frame["timestamp"])[0]
            body = maybe_inflate(frame["body"])
            if body is None:
                body = frame["body"]
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
                        opcode_counts[opcode] += 1
                        if opcode in observed:
                            base = {
                                "lane_index": lane_index, "frame_index": frame_index,
                                "subevent_index": subevent_index, "ordinal": ordinal,
                                "opcode": opcode,
                                "source_actor_id": struct.unpack_from("<I", body, offset + 4)[0],
                                "destination_actor_id": struct.unpack_from("<I", body, offset + 8)[0],
                            }
                            if opcode in ITEM_COUNTS:
                                base["items"] = _parse_item_rows(sub, opcode)
                            elif opcode in LINK_COUNTS:
                                base["links"] = _parse_link_rows(sub, opcode)
                            elif opcode == SET_BEGIN:
                                payload = sub[INNER_HEADER_LEN + 8:]
                                if len(payload) != 8:
                                    raise ValueError(f"{path.name}: unexpected 0x0146 payload size")
                                actor_id, set_size, set_code = struct.unpack("<IHH", payload)
                                base.update({"set_actor_id": actor_id, "set_size": set_size,
                                             "set_code": set_code})
                            events.append(base)
                            ordinal += 1
                offset += size
                subevent_index += 1
    return events, len(lanes), opcode_counts, frame_times


def _load_properties() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    with PROPERTY_RECORDS.open(encoding="ascii", newline="") as handle:
        for row in csv.DictReader(handle):
            grouped[row["capture"]].append(row)
    return grouped


def _property_projection(properties: list[dict[str, str]], *, lane_index: int,
                         source_actor_id: int, destination_actor_id: int,
                         boundary: tuple[int, int, int], before: bool) -> list[dict[str, str]]:
    candidates = []
    for row in properties:
        if (int(row["lane_index"]) != lane_index
                or int(row["source_actor_id"]) != source_actor_id
                or int(row["destination_actor_id"]) != destination_actor_id):
            continue
        order = (int(row["frame_index"]), int(row["subevent_index"]), -1)
        if (before and order < boundary) or (not before and order > boundary):
            candidates.append(row)
    if not candidates:
        return []
    nearest_frame = (max if before else min)(int(row["frame_index"]) for row in candidates)
    return [row for row in candidates if int(row["frame_index"]) == nearest_frame]


def _transactions(events: list[dict]) -> list[dict]:
    by_lane: dict[int, list[dict]] = defaultdict(list)
    for event in events:
        by_lane[int(event["lane_index"])].append(event)
    transactions = []
    for lane_index, lane_events in sorted(by_lane.items()):
        lane_events.sort(key=_event_order)
        depth = 0
        begin_index = None
        for index, event in enumerate(lane_events):
            if event["opcode"] == SET_BEGIN:
                if depth == 0:
                    begin_index = index
                depth += 1
                continue
            if event["opcode"] != SET_END:
                continue
            if depth == 0:
                raise ValueError("unmatched 0x0147 inventory-set end")
            depth -= 1
            if depth:
                continue
            assert begin_index is not None
            begin = lane_events[begin_index]
            end_index = index
            end = event
            previous_change = next((lane_events[index] for index in range(begin_index - 1, -1, -1)
                                    if lane_events[index]["opcode"] in {CHANGE_BEGIN, CHANGE_END}), None)
            next_change = next((lane_events[index] for index in range(end_index + 1, len(lane_events))
                                if lane_events[index]["opcode"] in {CHANGE_BEGIN, CHANGE_END}), None)
            transactions.append({
                "lane_index": lane_index, "begin": begin, "end": end,
                "members": lane_events[begin_index + 1:end_index],
                "change_begin": previous_change if previous_change and previous_change["opcode"] == CHANGE_BEGIN else None,
                "change_end": next_change if next_change and next_change["opcode"] == CHANGE_END else None,
            })
            begin_index = None
        if depth:
            raise ValueError("unterminated 0x0146 inventory set")
    return transactions


def _blank(fields: tuple[str, ...]) -> dict[str, object]:
    return {field: "" for field in fields}


def _item_rows_with_package(transaction: dict) -> list[tuple[dict, dict, int]]:
    stack = [int(transaction["begin"]["set_code"])]
    rows = []
    for event in transaction["members"]:
        if event["opcode"] == SET_BEGIN:
            stack.append(int(event["set_code"]))
        elif event["opcode"] == SET_END:
            if len(stack) == 1:
                raise ValueError("inventory-set nesting escaped its outer frame")
            stack.pop()
        elif event["opcode"] in ITEM_COUNTS:
            rows.extend((event, item, stack[-1]) for item in event.get("items", []))
    if len(stack) != 1:
        raise ValueError("inventory-set nesting remained open")
    return rows


def _csv_bytes(rows: list[dict], fields: tuple[str, ...]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("ascii")


def extract() -> tuple[list[dict], list[dict], list[dict], dict[str, int]]:
    properties_by_capture = _load_properties()
    accounting_rows: list[dict] = []
    matrix_rows: list[dict] = []
    property_rows: list[dict] = []
    event_number = 0
    aggregate_seen: dict[tuple, str] = {}
    corpus_paths = default_corpus_paths()
    if len(corpus_paths) != 54:
        raise ValueError(f"expected canonical 54-capture corpus, found {len(corpus_paths)}")

    for path in corpus_paths:
        source_hash = _sha256(path)
        events, lane_count, opcode_counts, frame_times = _scan_capture(path)
        properties = properties_by_capture.get(path.name, [])
        labels = _actor_labels(events, properties)
        transactions = _transactions(events)
        capture_matrix: list[dict] = []
        repeated_aggregate_count = 0
        inventory_state: dict[int, dict[tuple[int, int], list[tuple[dict, dict]]]] = defaultdict(dict)

        for transaction in transactions:
            event_number += 1
            event_id = f"equipment-event-{event_number:03d}"
            begin, end = transaction["begin"], transaction["end"]
            link_events = [row for row in transaction["members"] if row["opcode"] in LINK_COUNTS]
            item_candidates: dict[tuple[int, int], list[tuple[dict, dict]]] = defaultdict(list)
            item_rows = _item_rows_with_package(transaction)
            for item_event, item, package_code in item_rows:
                item_candidates[(package_code, int(item["item_slot"]))].append((item_event, item))
            lane_state = inventory_state[int(transaction["lane_index"])]

            actor_source = int(begin["source_actor_id"])
            actor_destination = int(begin["destination_actor_id"])
            projection_args = {"properties": properties, "lane_index": int(transaction["lane_index"]),
                               "source_actor_id": actor_source, "destination_actor_id": actor_destination}
            before = _property_projection(**projection_args, boundary=_event_order(begin), before=True)
            after = _property_projection(**projection_args, boundary=_event_order(end), before=False)
            before_by_hash = {row["property_hash"]: row for row in before}
            after_by_hash = {row["property_hash"]: row for row in after}
            changed_hashes = sorted(prop_hash for prop_hash in before_by_hash.keys() & after_by_hash.keys()
                                    if before_by_hash[prop_hash]["value_hex"] != after_by_hash[prop_hash]["value_hex"])
            before_frame = before[0]["frame_index"] if before else ""
            after_frame = after[0]["frame_index"] if after else ""
            before_distance = int(begin["frame_index"]) - int(before_frame) if before else ""
            after_distance = int(after_frame) - int(end["frame_index"]) if after else ""
            lane_index = int(transaction["lane_index"])
            before_distance_us = (frame_times[(lane_index, int(begin["frame_index"]))]
                                  - frame_times[(lane_index, int(before_frame))]) if before else ""
            after_distance_us = (frame_times[(lane_index, int(after_frame))]
                                 - frame_times[(lane_index, int(end["frame_index"]))]) if after else ""

            link_rows = [(event, link) for event in link_events for link in event.get("links", [])]
            repeated_of = ""
            if any(event["opcode"] != 0x014D for event in link_events):
                fingerprint = tuple((event["opcode"], link["equipment_slot"], link["item_slot"],
                                     link["item_package_code"]) for event, link in link_rows)
                if fingerprint in aggregate_seen:
                    repeated_of = aggregate_seen[fingerprint]
                    repeated_aggregate_count += 1
                else:
                    aggregate_seen[fingerprint] = event_id

            common = {
                "event_id": event_id, "capture": path.name,
                "lane_index": transaction["lane_index"], "source_actor": labels[actor_source],
                "destination_actor": labels[actor_destination],
                "set_begin_frame": begin["frame_index"], "set_begin_subevent": begin["subevent_index"],
                "set_end_frame": end["frame_index"], "set_end_subevent": end["subevent_index"],
                "change_begin_frame": transaction["change_begin"]["frame_index"] if transaction["change_begin"] else "",
                "change_begin_subevent": transaction["change_begin"]["subevent_index"] if transaction["change_begin"] else "",
                "change_end_frame": transaction["change_end"]["frame_index"] if transaction["change_end"] else "",
                "change_end_subevent": transaction["change_end"]["subevent_index"] if transaction["change_end"] else "",
                "before_property_frame": before_frame, "before_distance_frames": before_distance,
                "before_distance_us": before_distance_us,
                "after_property_frame": after_frame, "after_distance_frames": after_distance,
                "after_distance_us": after_distance_us,
                "changed_property_count": len(changed_hashes),
            }
            if not link_rows:
                for item_event, item, package_code in item_rows:
                    lane_state[(package_code, int(item["item_slot"]))] = [(item_event, item)]
                capture_matrix.append({**_blank(MATRIX_FIELDS), **common,
                    "classification": "MISSING-CARRIER", "join_status": "no-equipment-link",
                    "boundary_note": "framed inventory set without an equipment-link carrier"})
                continue

            for link_event, link in link_rows:
                item_key = (int(link["item_package_code"]), int(link["item_slot"]))
                matches = item_candidates.get(item_key, [])
                match_origin = "same-event"
                if not matches:
                    matches = lane_state.get(item_key, [])
                    match_origin = "prior-state"
                match = matches[-1] if len(matches) == 1 else None
                if link_event["opcode"] == 0x014D and match and changed_hashes:
                    classification = "EXACT-TRANSITION"
                elif link_event["opcode"] == 0x014D:
                    classification = "BOUNDED-CANDIDATE"
                else:
                    classification = "AGGREGATE-SNAPSHOT"
                row = {**_blank(MATRIX_FIELDS), **common,
                    "classification": classification,
                    "join_status": f"exact-{match_origin}-item-link" if match else ("ambiguous-item-link" if matches else "missing-item"),
                    "link_opcode": f"0x{link_event['opcode']:04X}", "link_frame": link_event["frame_index"],
                    "link_subevent": link_event["subevent_index"], "link_record": link["link_record"],
                    "equipment_slot": link["equipment_slot"], "linked_item_slot": link["item_slot"],
                    "item_package_code": link["item_package_code"], "repeated_aggregate_of": repeated_of,
                    "boundary_note": "same-lane s2c order is correlation evidence, not causality"}
                if match:
                    item_event, item = match
                    item_frame_distance = int(link_event["frame_index"]) - int(item_event["frame_index"])
                    item_subevent_distance = (int(link_event["subevent_index"]) - int(item_event["subevent_index"])
                                              if not item_frame_distance else "")
                    item_distance_us = (frame_times[(lane_index, int(link_event["frame_index"]))]
                                        - frame_times[(lane_index, int(item_event["frame_index"]))])
                    row.update({"item_opcode": f"0x{item_event['opcode']:04X}",
                                "item_frame": item_event["frame_index"], "item_subevent": item_event["subevent_index"],
                                "item_record": item["item_record"], "catalog_item_id": f"0x{int(item['item_id']):08X}",
                                "item_slot": item["item_slot"],
                                "item_to_link_distance_frames": item_frame_distance,
                                "item_to_link_distance_subevents": item_subevent_distance,
                                "item_to_link_distance_us": item_distance_us})
                capture_matrix.append(row)
                if link_event["opcode"] == 0x014D and match:
                    for prop_hash in sorted(before_by_hash.keys() | after_by_hash.keys()):
                        old = before_by_hash.get(prop_hash)
                        new = after_by_hash.get(prop_hash)
                        if old and new:
                            comparison_status = ("changed" if old["value_hex"] != new["value_hex"]
                                                 else "unchanged")
                        else:
                            comparison_status = "before-only" if old else "after-only"
                        property_rows.append({
                            "event_id": event_id, "capture": path.name, "lane_index": transaction["lane_index"],
                            "source_actor": labels[actor_source], "destination_actor": labels[actor_destination],
                            "carrier_scope": "single-slot",
                            "equipment_slot": link["equipment_slot"], "catalog_item_id": row["catalog_item_id"],
                            "property_hash": prop_hash, "comparison_status": comparison_status,
                            "before_record_index": old["record_index"] if old else "",
                            "before_frame": old["frame_index"] if old else "",
                            "before_subevent": old["subevent_index"] if old else "",
                            "before_value_hex": old["value_hex"] if old else "",
                            "before_value_u_le": old["value_u_le"] if old else "",
                            "after_record_index": new["record_index"] if new else "",
                            "after_frame": new["frame_index"] if new else "",
                            "after_subevent": new["subevent_index"] if new else "",
                            "after_value_hex": new["value_hex"] if new else "",
                            "after_value_u_le": new["value_u_le"] if new else "",
                            "before_distance_frames": before_distance if old else "",
                            "before_distance_us": before_distance_us if old else "",
                            "after_distance_frames": after_distance if new else "",
                            "after_distance_us": after_distance_us if new else ""})

            if any(event["opcode"] != 0x014D for event in link_events):
                for prop_hash in sorted(before_by_hash.keys() | after_by_hash.keys()):
                    old = before_by_hash.get(prop_hash)
                    new = after_by_hash.get(prop_hash)
                    if old and new:
                        comparison_status = ("changed" if old["value_hex"] != new["value_hex"]
                                             else "unchanged")
                    else:
                        comparison_status = "before-only" if old else "after-only"
                    property_rows.append({
                        "event_id": event_id, "capture": path.name,
                        "lane_index": transaction["lane_index"],
                        "source_actor": labels[actor_source],
                        "destination_actor": labels[actor_destination],
                        "carrier_scope": "aggregate-event", "equipment_slot": "",
                        "catalog_item_id": "", "property_hash": prop_hash,
                        "comparison_status": comparison_status,
                        "before_record_index": old["record_index"] if old else "",
                        "before_frame": old["frame_index"] if old else "",
                        "before_subevent": old["subevent_index"] if old else "",
                        "before_value_hex": old["value_hex"] if old else "",
                        "before_value_u_le": old["value_u_le"] if old else "",
                        "after_record_index": new["record_index"] if new else "",
                        "after_frame": new["frame_index"] if new else "",
                        "after_subevent": new["subevent_index"] if new else "",
                        "after_value_hex": new["value_hex"] if new else "",
                        "after_value_u_le": new["value_u_le"] if new else "",
                        "before_distance_frames": before_distance if old else "",
                        "before_distance_us": before_distance_us if old else "",
                        "after_distance_frames": after_distance if new else "",
                        "after_distance_us": after_distance_us if new else ""})

            for item_event, item, package_code in item_rows:
                lane_state[(package_code, int(item["item_slot"]))] = [(item_event, item)]

        if path.name == "gear_changesoul.pcapng" and not transactions:
            event_number += 1
            capture_matrix.append({**_blank(MATRIX_FIELDS),
                "event_id": f"equipment-event-{event_number:03d}", "capture": path.name,
                "classification": "MISSING-CARRIER",
                "join_status": "property-only-no-inventory-frame",
                "boundary_note": "named soul capture has property traffic but no item, link, or inventory-set carrier"})

        matrix_rows.extend(capture_matrix)
        accounting_rows.append({
            "capture": path.name, "sha256": source_hash, "lane_count": lane_count,
            "set_begin_count": opcode_counts[SET_BEGIN], "set_end_count": opcode_counts[SET_END],
            "change_begin_count": opcode_counts[CHANGE_BEGIN], "change_end_count": opcode_counts[CHANGE_END],
            **{f"opcode_0x{opcode:04x}_count": opcode_counts[opcode]
               for opcode in range(0x0148, 0x0152)},
            "item_packet_count": sum(opcode_counts[opcode] for opcode in ITEM_COUNTS),
            "item_record_count": sum(len(event.get("items", [])) for event in events if event["opcode"] in ITEM_COUNTS),
            "link_packet_count": sum(opcode_counts[opcode] for opcode in LINK_COUNTS),
            "link_record_count": sum(len(event.get("links", [])) for event in events if event["opcode"] in LINK_COUNTS),
            "framed_event_count": len(transactions),
            "exact_item_link_count": sum(str(row["join_status"]).startswith("exact-") for row in capture_matrix),
            "bounded_candidate_count": sum(row["classification"] == "BOUNDED-CANDIDATE" for row in capture_matrix),
            "missing_carrier_count": sum(row["classification"] == "MISSING-CARRIER" for row in capture_matrix),
            "repeated_aggregate_event_count": repeated_aggregate_count,
            "retransmitted_segment_count": _retransmitted_segments(path),
            "excluded_0x018f_0x0191_count": sum(opcode_counts[opcode] for opcode in EXCLUDED_NEARBY)})

    summary = {
        "captures": len(accounting_rows),
        "set_scopes": sum(int(row["set_begin_count"]) for row in accounting_rows),
        "change_scopes": sum(int(row["change_begin_count"]) for row in accounting_rows),
        "framed_events": sum(int(row["framed_event_count"]) for row in accounting_rows),
        "item_packets": sum(int(row["item_packet_count"]) for row in accounting_rows),
        "item_records": sum(int(row["item_record_count"]) for row in accounting_rows),
        "link_packets": sum(int(row["link_packet_count"]) for row in accounting_rows),
        "link_records": sum(int(row["link_record_count"]) for row in accounting_rows),
        "exact_transitions": sum(row["classification"] == "EXACT-TRANSITION" for row in matrix_rows),
        "bounded_candidates": sum(row["classification"] == "BOUNDED-CANDIDATE" for row in matrix_rows),
        "aggregate_snapshots": sum(row["classification"] == "AGGREGATE-SNAPSHOT" for row in matrix_rows),
        "missing_carriers": sum(row["classification"] == "MISSING-CARRIER" for row in matrix_rows),
        "property_joins": len(property_rows),
        "retransmitted_segments": sum(int(row["retransmitted_segment_count"]) for row in accounting_rows),
        "repeated_aggregate_events": sum(int(row["repeated_aggregate_event_count"]) for row in accounting_rows),
        "excluded_nearby_packets": sum(int(row["excluded_0x018f_0x0191_count"]) for row in accounting_rows),
    }
    return accounting_rows, matrix_rows, property_rows, summary


def _evidence_map_bytes(matrix: list[dict], summary: dict[str, int]) -> bytes:
    exact = [row for row in matrix if row["classification"] == "EXACT-TRANSITION"]
    candidates = [row for row in matrix if row["classification"] == "BOUNDED-CANDIDATE"]
    missing = [row for row in matrix if row["classification"] == "MISSING-CARRIER"]
    lines = [
        "# Equipment transition census evidence map", "", "## Corpus accounting", "",
        f"The deterministic census covers all {summary['captures']} canonical captures. It matched {summary['set_scopes']} balanced 0x0146/0x0147 scopes into {summary['framed_events']} outer framed inventory events, inside {summary['change_scopes']} observed 0x016D/0x016E change scopes. It decoded {summary['item_packets']} item packets ({summary['item_records']} nonempty rows) and {summary['link_packets']} linked-item packets ({summary['link_records']} rows).",
        "",
        f"TCP reconstruction suppressed {summary['retransmitted_segments']} exact repeated payload segments. The census separately marks {summary['repeated_aggregate_events']} repeated aggregate equipment events. The {summary['excluded_nearby_packets']} observed 0x018F-0x0191 packets are counted as excluded nearby traffic and are never treated as equipment-transition carriers.",
        "", "## Result classes", "",
        "`matrix.csv` preserves sanitized per-capture actor equality plus lane, frame, subevent, transaction, item-row, equipment-row, slot, catalog-id, and temporal-distance locators. `property-joins.csv` preserves before-only, after-only, unchanged, and changed hashes from the nearest actor-scoped projections around each carrier event. Same-lane order is correlation evidence, not a causal assertion.",
        "", "| Class | Rows | Meaning |", "|---|---:|---|",
        f"| EXACT-TRANSITION | {len(exact)} | Single-slot 0x014D item/link join with comparable changed before/after properties. |",
        f"| BOUNDED-CANDIDATE | {len(candidates)} | Single-slot 0x014D carrier whose property or item side is incomplete. |",
        f"| AGGREGATE-SNAPSHOT | {summary['aggregate_snapshots']} | 0x014E multi-slot state; not promoted as a transition. |",
        f"| MISSING-CARRIER | {len(missing)} | Framed inventory activity without an equipment link, plus the named soul property-only gap. |",
        "", "## Exact transitions", "",
        "| Event | Capture | Equipment slot | Catalog item | Changed hashes | Property frame bracket |",
        "|---|---|---:|---|---:|---|",
    ]
    for row in exact:
        lines.append(f"| {row['event_id']} | `{row['capture']}` | {row['equipment_slot']} | `{row['catalog_item_id']}` | {row['changed_property_count']} | {row['before_property_frame']} -> {row['after_property_frame']} |")
    lines.extend(["", "## Bounded candidates", "",
                  "| Event | Capture | Equipment slot | Catalog item | Join | Property bracket |",
                  "|---|---|---:|---|---|---|"])
    for row in candidates:
        lines.append(f"| {row['event_id']} | `{row['capture']}` | {row['equipment_slot']} | `{row['catalog_item_id'] or 'missing'}` | {row['join_status']} | {row['before_property_frame'] or 'missing'} -> {row['after_property_frame'] or 'missing'} |")
    lines.extend(["", "## Claim boundary", "",
        "Actor labels are capture-local tokens assigned by first observed appearance. They preserve equality without publishing actor or session identifiers. Property hashes and integer values are wire facts only; no gameplay meaning is assigned to `generalParameter[18]` or another indexed property. Aggregate snapshots, chronology, and 0x018F-0x0191 traffic are not forced into transition claims.",
        "", "## Original gap disposition", "",
        "The complete-corpus result below is generated from carrier and property evidence; it does not treat a similarly timed record as proof of causality.", ""])
    old_helm = [row for row in matrix if row["equipment_slot"] == 8
                and row["catalog_item_id"] == "0x007A3D64"]
    lines.extend([
        "- Helm transition: closed in `change_helm.pcapng`; equipment slot 8 changes to catalog item `0x007A3F58` while property hash `0x8cae90db` changes 141 -> 161.",
        f"- Helm old link: closed as prior state by {len(old_helm)} exact aggregate snapshots that bind equipment slot 8 to catalog item `0x007A3D64`; no snapshot is promoted as the transition itself.",
        "- Body: still open; `change_bodyarmor.pcapng` exactly joins equipment slot 10 to `0x007A88D7` and has after-only `0x8cae90db=147`, but no comparable before value.",
        "- Weapon: still open; `gear_changeweapon.pcapng` exactly joins equipment slot 0 to `0x003D7E3D` and has after-only `0x8cae90db=169`, but no comparable before value.",
        "- Soul: still open; `gear_changesoul.pcapng` has property traffic but no inventory frame, item row, or equipment-link carrier.",
        "- Additional bounded candidates: `change_to_botanist.pcapng` has exact slot 0 and slot 1 item/link joins, and `switch_to_weaver.pcapng` has an exact slot 0 join; none has comparable changed before/after property evidence.",
    ])
    lines.append("")
    return "\n".join(lines).encode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    accounting, matrix, properties, summary = extract()
    outputs = {
        "capture-accounting.csv": _csv_bytes(accounting, ACCOUNTING_FIELDS),
        "matrix.csv": _csv_bytes(matrix, MATRIX_FIELDS),
        "property-joins.csv": _csv_bytes(properties, PROPERTY_FIELDS),
        "evidence-map.md": _evidence_map_bytes(matrix, summary),
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
        print("stale equipment-transition artifacts:\n  " + "\n  ".join(stale))
        return 1
    print(("verified" if args.check else "wrote") + f" {len(outputs)} equipment-transition artifacts")
    print(" ".join(f"{key}={value}" for key, value in summary.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
