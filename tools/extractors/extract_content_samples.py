"""Extract inventory records and event-start identities from packet bodies.

Inventory opcodes 0x0148-0x014a use 112-byte items. C2s 0x012d carries event
actor ids and an ASCII event name.
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
GENERATOR_VERSION = "1"

DEFAULT_OUT = Path(__file__).parent.parent.parent / "derived" / "content_samples.json"

OPCODE_INVENTORY_LIST_X16 = 0x014A
OPCODE_INVENTORY_LIST_X08 = 0x0149
OPCODE_INVENTORY_LIST_X01 = 0x0148
OPCODE_EVENT_START = 0x012D

# Wire fact: after the 8-byte inner header, an 8-byte actor-id/zero-pad preamble puts item data at offset 16.
INVENTORY_PREAMBLE = 16
ITEM_LEN = 0x70


def parse_inventory_items(sub_body: bytes, expected_count: int) -> list[dict]:
    items: list[dict] = []
    base = INVENTORY_PREAMBLE
    for i in range(expected_count):
        offset = base + i * ITEM_LEN
        if offset + ITEM_LEN > len(sub_body):
            break
        unique_id = struct.unpack_from("<Q", sub_body, offset + 0)[0]
        quantity = struct.unpack_from("<i", sub_body, offset + 8)[0]
        item_id = struct.unpack_from("<I", sub_body, offset + 12)[0]
        slot = struct.unpack_from("<H", sub_body, offset + 16)[0]
        # Fields occupy 18-19, a1/a2/a3 end at 32, then tags follow and quality is at 41.
        if item_id == 0 and unique_id == 0:
            continue
        items.append(
            {
                "uniqueId": unique_id,
                "uniqueIdHex": f"0x{unique_id:016x}",
                "quantity": quantity,
                "itemId": item_id,
                "itemIdHex": f"0x{item_id:08x}",
                "slot": slot,
            }
        )
    return items


def parse_event_start(sub_body: bytes) -> dict:
    """Decode the c2s 0x012d event-start payload as:
    triggerActorID (u32), ownerActorID (u32), serverCodes (u32),
    unknown (u32), eventName (ascii null-padded to 0x20 bytes), luaParams.

    The c2s wire body after the 8-byte inner header has an 8-byte preamble.
    """
    if len(sub_body) < INVENTORY_PREAMBLE + 0x30:
        return {}
    p = INVENTORY_PREAMBLE
    trigger = struct.unpack_from("<I", sub_body, p)[0]
    owner = struct.unpack_from("<I", sub_body, p + 4)[0]
    server_codes = struct.unpack_from("<I", sub_body, p + 8)[0]
    unknown = struct.unpack_from("<I", sub_body, p + 12)[0]
    # Wire fact: the event name starts at offset +17 after the +16 type flag and ends at the first null.
    name_bytes = sub_body[p + 17 : p + 17 + 0x20]
    name = name_bytes.split(b"\x00", 1)[0].decode("ascii", errors="replace")
    return {
        "triggerActorId": trigger,
        "triggerActorIdHex": f"0x{trigger:08x}",
        "ownerActorId": owner,
        "ownerActorIdHex": f"0x{owner:08x}",
        "serverCodes": server_codes,
        "unknown": unknown,
        "eventName": name,
    }


def walk_capture_content(path: Path) -> dict:
    streams = reconstruct(path)
    items: list[dict] = []
    event_starts: list[dict] = []

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
                        if direction == "s2c" and inner_opcode in (
                            OPCODE_INVENTORY_LIST_X01,
                            OPCODE_INVENTORY_LIST_X08,
                            OPCODE_INVENTORY_LIST_X16,
                        ):
                            count_map = {
                                OPCODE_INVENTORY_LIST_X01: 1,
                                OPCODE_INVENTORY_LIST_X08: 8,
                                OPCODE_INVENTORY_LIST_X16: 16,
                            }
                            items.extend(
                                {**it, "capture": path.name, "opcodeHex": f"0x{inner_opcode:04x}"}
                                for it in parse_inventory_items(sub_body, count_map[inner_opcode])
                            )
                        elif direction == "c2s" and inner_opcode == OPCODE_EVENT_START:
                            parsed = parse_event_start(sub_body)
                            if parsed:
                                event_starts.append({**parsed, "capture": path.name})
                offset += size
    return {"items": items, "event_starts": event_starts}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    paths = default_corpus_paths()

    all_items: list[dict] = []
    all_events: list[dict] = []

    for p in paths:
        if not p.is_file():
            continue
        rec = walk_capture_content(p)
        all_items.extend(rec["items"])
        all_events.extend(rec["event_starts"])

    item_count_by_id: Counter = Counter()
    item_captures: dict[int, set] = {}
    item_sample_quantity: dict[int, int] = {}
    for it in all_items:
        iid = it["itemId"]
        item_count_by_id[iid] += 1
        item_captures.setdefault(iid, set()).add(it["capture"])
        if iid not in item_sample_quantity:
            item_sample_quantity[iid] = it["quantity"]

    items_summary = [
        {
            "itemId": iid,
            "itemIdHex": f"0x{iid:08x}",
            "totalOccurrences": item_count_by_id[iid],
            "capturesSeen": len(item_captures[iid]),
            "sampleQuantity": item_sample_quantity[iid],
        }
        for iid in sorted(item_count_by_id, key=lambda i: -item_count_by_id[i])
    ]

    event_count_by_name: Counter = Counter()
    event_captures: dict[str, set] = {}
    for e in all_events:
        name = e["eventName"] or "(empty)"
        event_count_by_name[name] += 1
        event_captures.setdefault(name, set()).add(e["capture"])

    events_summary = [
        {
            "eventName": name,
            "count": cnt,
            "capturesSeen": len(event_captures.get(name, [])),
        }
        for name, cnt in event_count_by_name.most_common()
    ]

    out_struct = {
        "captureCount": len(paths),
        "inventory": {
            "totalItemsObserved": len(all_items),
            "distinctItemIds": len(item_count_by_id),
            "items": items_summary,
        },
        "eventStarts": {
            "totalStarts": len(all_events),
            "distinctEvents": len(event_count_by_name),
            "events": events_summary,
        },
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, out_struct)
    print(f"wrote {out_path}")
    print(f"  inventory items: {len(all_items)} observations, {len(item_count_by_id)} distinct itemIds")
    print(f"  event starts: {len(all_events)} observations, {len(event_count_by_name)} distinct names")
    print()
    print("Top 10 items by frequency:")
    for entry in items_summary[:10]:
        print(
            f"  {entry['itemIdHex']}  count={entry['totalOccurrences']:>3}  "
            f"qty={entry['sampleQuantity']:>5}  in {entry['capturesSeen']:>2} captures"
        )
    print()
    print("Top 10 event names:")
    for entry in events_summary[:10]:
        print(f"  {entry['eventName']:<28}  count={entry['count']:>3}  in {entry['capturesSeen']:>2} captures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
