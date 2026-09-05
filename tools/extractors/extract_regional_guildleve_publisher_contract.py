#!/usr/bin/env python3
"""Extract the bounded regional guildleve publisher contract from one capture."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from extract_00da_00e1_comparison import _decode_capture  # type: ignore  # noqa: E402
from extract_property_stream_catalog import parse_records  # type: ignore  # noqa: E402

OBJECTS_DIR = Path(os.environ.get(
    "XIVL_PCAP_OBJECTS_DIR",
    str(REPO_ROOT / "sources" / "pcap-1.23b" / "objects"),
))
CAPTURE = OBJECTS_DIR / "party_battle_leve.pcapng"
CAPTURE_SHA256 = "6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f"
OUT = REPO_ROOT / "studies" / "regional-guildleve-publisher-contract" / "derived"
PLAYER_ACTOR_ID = 0x029B2941
START_OWNER_ACTOR_ID = 0x4510000C
REWARD_OWNER_ACTOR_ID = 0x45100D5B
DIRECTOR_ACTOR_ID = 0x45100D44
GUILDLEVE_ID = 12487

FIELDS = [
    "capture", "sequence", "stage", "capture_packet_index", "capture_timestamp_utc",
    "lane_index", "lane", "direction", "frame_index", "frame_stream_offset",
    "subevent_index", "subevent_offset", "subevent_size", "opcode",
    "transport_source_actor_id_hex", "transport_target_actor_id_hex",
    "event_name", "function_name", "attributable_fields", "application_sha256",
]

LOCATORS = [
    ("activation-interaction", "c2s", 6, 2, 0x012D),
    ("aetheryte-selection", "s2c", 7, 0, 0x0130),
    ("aetheryte-selection-response", "c2s", 13, 1, 0x012E),
    ("journal-selection", "s2c", 17, 0, 0x0130),
    ("journal-selection-response", "c2s", 21, 1, 0x012E),
    ("journal-detail", "s2c", 28, 0, 0x0130),
    ("journal-detail-response", "c2s", 27, 1, 0x012E),
    ("difficulty-selection", "s2c", 35, 1, 0x0130),
    ("difficulty-response", "c2s", 34, 1, 0x012E),
    ("activation-confirmation", "s2c", 40, 2, 0x0130),
    ("activation-response", "c2s", 42, 2, 0x012E),
    ("content-group-start", "s2c", 78, 0, 0x017C),
    ("content-members-start", "s2c", 78, 2, 0x0183),
    ("director-finish-update", "s2c", 3374, 0, 0x0137),
    ("reward-interaction", "c2s", 1763, 1, 0x012D),
    ("reward-presentation", "s2c", 3420, 0, 0x0130),
    ("reward-response", "c2s", 1769, 1, 0x012E),
    ("reward-warp-presentation", "s2c", 3429, 2, 0x0130),
    ("reward-warp-response", "c2s", 1777, 1, 0x012E),
    ("content-group-retirement-7", "s2c", 3448, 2, 0x0143),
    ("content-group-retirement-4", "s2c", 3448, 3, 0x0143),
    ("event-retirement", "s2c", 3451, 0, 0x0131),
    ("final-unanswered-interaction", "c2s", 1785, 3, 0x012D),
]

EXPECTED_FUNCTIONS = {
    7: "eventAetheryteChildSelect",
    17: "eventGLSelect",
    28: "eventGLSelectDetail",
    35: "eventGLDifficulty",
    40: "eventGLStart",
    3420: "eventGuildleveReward",
    3429: "eventTalkGuildleveWarp",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _event_name(app: bytes) -> str:
    return app[17:49].split(b"\0", 1)[0].decode("ascii")


def _function_name(app: bytes) -> str:
    return app[0x29:0x49].split(b"\0", 1)[0].decode("ascii")


def _hex32(value: int) -> str:
    return f"0x{value:08x}"


def _select(events: list[dict], direction: str, frame_index: int,
            subevent_index: int, opcode: int) -> dict:
    matches = [
        event for event in events
        if event["direction"] == direction
        and event["frame_index"] == frame_index
        and event["subevent_index"] == subevent_index
        and event.get("opcode_value") == opcode
    ]
    if len(matches) != 1:
        raise ValueError(
            f"locator {direction}/{frame_index}/{subevent_index}/0x{opcode:04x} "
            f"matched {len(matches)} rows"
        )
    return matches[0]


def order_rows(rows: list[dict]) -> None:
    rows.sort(key=lambda row: (
        row["capture_packet_index"], row["frame_stream_offset"],
        row["subevent_offset"], row["direction"],
    ))


def _fields(stage: str, event: dict, app: bytes) -> str:
    if event["opcode_value"] == 0x012D:
        trigger = int.from_bytes(app[0:4], "little")
        owner = int.from_bytes(app[4:8], "little")
        name = _event_name(app)
        if trigger != PLAYER_ACTOR_ID or name != "talkDefault":
            raise ValueError(f"unexpected EventStart identity at {stage}")
        expected_owner = START_OWNER_ACTOR_ID if stage == "activation-interaction" else REWARD_OWNER_ACTOR_ID
        if owner != expected_owner:
            raise ValueError(f"unexpected EventStart owner at {stage}")
        return f"trigger_actor_id={_hex32(trigger)};owner_actor_id={_hex32(owner)}"
    if event["opcode_value"] == 0x0130:
        function = _function_name(app)
        if function != EXPECTED_FUNCTIONS[event["frame_index"]]:
            raise ValueError(f"unexpected RunEvent function at frame {event['frame_index']}")
        if function in {"eventGLSelectDetail", "eventGLDifficulty", "eventGLStart", "eventGuildleveReward"}:
            value = int.from_bytes(app[0x4C:0x4E], "big")
            if value != GUILDLEVE_ID:
                raise ValueError(f"unexpected guildleve ID prefix at {function}: {value}")
            return f"guildleve_id={value}"
        return ""
    if event["opcode_value"] == 0x017C:
        group_type = int.from_bytes(app[0x30:0x34], "little")
        if group_type != 30001:
            raise ValueError(f"unexpected content group type {group_type}")
        return f"group_type={group_type}"
    if event["opcode_value"] == 0x0183:
        count = app[0x70]
        actors = [int.from_bytes(app[0x10 + slot * 0x0C:0x14 + slot * 0x0C], "little") for slot in range(count)]
        expected = [DIRECTOR_ACTOR_ID, PLAYER_ACTOR_ID, 0x029B27D3, REWARD_OWNER_ACTOR_ID - 0x16]
        if actors != expected:
            raise ValueError(f"unexpected initial content members {actors}")
        return f"member_count={count};member_actor_ids={';'.join(_hex32(actor) for actor in actors)}"
    if event["opcode_value"] == 0x0137:
        records, declared, terminated, _consumed = parse_records(app)
        wanted = {row["property_hash"]: row for row in records}
        signal = wanted.get("0xafedf257")
        start_time = wanted.get("0xd2c67973")
        if len(records) != 5 or declared != 104 or terminated or signal is None or start_time is None:
            raise ValueError("director finish property block shape changed")
        if signal["value_hex"] != "ff" or start_time["value_hex"] != "00000000":
            raise ValueError("director finish property values changed")
        if event["transport_source_actor_id"] != DIRECTOR_ACTOR_ID:
            raise ValueError("director finish source actor changed")
        return "property_0xafedf257=ff;property_0xd2c67973=00000000"
    if event["opcode_value"] == 0x0143:
        control = int.from_bytes(app[0:4], "little")
        group_id = int.from_bytes(app[8:16], "little")
        expected_control = 7 if stage.endswith("-7") else 4
        if control != expected_control or group_id != 0x2880000000000822:
            raise ValueError("content-group retirement tuple changed")
        return f"control={control};group_id=0x{group_id:016x}"
    if event["opcode_value"] == 0x0131:
        selector = int.from_bytes(app[4:8], "little")
        if selector != 5:
            raise ValueError(f"unexpected EndEvent selector {selector}")
        return f"selector={selector}"
    return ""


def _build_party_outputs(path: Path = CAPTURE) -> dict[str, bytes]:
    if sha256_file(path) != CAPTURE_SHA256:
        raise ValueError("party_battle_leve.pcapng identity mismatch")
    events, totals, lane_counts = _decode_capture(path)
    rows = []
    for stage, direction, frame_index, subevent_index, opcode in LOCATORS:
        event = _select(events, direction, frame_index, subevent_index, opcode)
        app = event["sub_body"][16:]
        rows.append({
            "capture": path.name,
            "stage": stage,
            "capture_packet_index": event["capture_packet_index"],
            "capture_timestamp_utc": event["capture_timestamp_utc"],
            "lane_index": event["lane_index"],
            "lane": event["lane"],
            "direction": direction,
            "frame_index": frame_index,
            "frame_stream_offset": event["frame_stream_offset"],
            "subevent_index": subevent_index,
            "subevent_offset": event["subevent_offset"],
            "subevent_size": event["subevent_size"],
            "opcode": f"0x{opcode:04x}",
            "transport_source_actor_id_hex": _hex32(event["transport_source_actor_id"]),
            "transport_target_actor_id_hex": _hex32(event["transport_target_actor_id"]),
            "event_name": _event_name(app) if opcode == 0x012D else "",
            "function_name": _function_name(app) if opcode == 0x0130 else "",
            "attributable_fields": _fields(stage, event, app),
            "application_sha256": sha256_bytes(app),
        })
    order_rows(rows)
    for sequence, row in enumerate(rows, 1):
        row["sequence"] = sequence

    run_functions = {
        _function_name(event["sub_body"][16:])
        for event in events
        if event["direction"] == "s2c" and event.get("opcode_value") == 0x0130
    }
    publisher_functions = sorted(run_functions & {"eventTalkCard", "eventTalkDetail"})
    if publisher_functions:
        raise ValueError(f"publisher acceptance functions appeared: {publisher_functions}")

    accounting = {
        "schema_version": 1,
        "study": "regional-guildleve-publisher-contract",
        "input": {
            "capture": path.name,
            "capture_sha256": CAPTURE_SHA256,
            "capture_size_bytes": path.stat().st_size,
        },
        "decode": {
            "lane_counts": lane_counts,
            "c2s_frames": totals["c2s_frames"],
            "s2c_frames": totals["s2c_frames"],
            "c2s_wrapped_subevents": totals["c2s_wrapped_subevents"],
            "s2c_wrapped_subevents": totals["s2c_wrapped_subevents"],
        },
        "timeline_rows": len(rows),
        "observed_run_event_functions": sorted(run_functions),
        "publisher_acceptance_functions": publisher_functions,
        "identities": {
            "guildleve_id": GUILDLEVE_ID,
            "player_actor_id": _hex32(PLAYER_ACTOR_ID),
            "activation_owner_actor_id": _hex32(START_OWNER_ACTOR_ID),
            "director_actor_id": _hex32(DIRECTOR_ACTOR_ID),
            "reward_owner_actor_id": _hex32(REWARD_OWNER_ACTOR_ID),
        },
        "boundaries": [
            "Capture packet indexes order the earliest packet that completes each reconstructed outer frame; they are capture-arrival witnesses, not server causality.",
            "The opening event functions are aetheryte activation of an already retained guildleve, not publisher acceptance.",
            "Reward presentation does not establish reward grant, publisher identity, hand-in authorization, persistence, or journal mutation.",
            "No packet field in the selected timeline identifies insertion, removal, or retention of journal row 12487.",
        ],
    }

    verdicts = """# Regional Guildleve Publisher Contract Verdicts

The sole input is `party_battle_leve.pcapng`, SHA-256
`6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f`.
`timeline.csv` orders the earliest captured packet that completes each selected
outer frame; same-frame rows retain subevent order.

| Question | Verdict | Evidence boundary |
|---|---|---|
| Publisher acceptance | INSUFFICIENT | The opening calls `eventAetheryteChildSelect`, `eventGLSelect`, `eventGLSelectDetail`, `eventGLDifficulty`, and `eventGLStart`. No `eventTalkCard` or `eventTalkDetail` publisher-acceptance call occurs. Guildleve 12487 is already retained when selection begins, so no offered list or acceptance response is captured. |
| Director start | SUPPORTED | `eventGLStart` carries guildleve ID 12487 before the first type-30001 content-group snapshot. The compact member list contains director actor `0x45100D44`, player `0x029B2941`, peer `0x029B27D3`, and content actor `0x45100D45`. This is one observed activation, not a universal creation recipe. |
| Completion | SUPPORTED | The director-targeted `0x0137` row at s2c frame 3374 carries property `0xAFEDF257=FF` and `0xD2C67973=00000000`. Tracked client evidence interprets these as signed signal -1 and startTime zero, sufficient for generic Guildleve UI `finish`; the packet does not settle success policy or rewards. |
| Publisher hand-in | INSUFFICIENT | The post-completion `talkDefault` owner is dynamic actor `0x45100D5B`. The server invokes `eventGuildleveReward` and `eventTalkGuildleveWarp`, but no tracked packet or static row identifies that actor as a regional publisher or exposes an authoritative hand-in operation. |
| Reward | SUPPORTED | `eventGuildleveReward` carries guildleve ID 12487 and precedes the client response and warp presentation. This supports reward presentation only, not grant, selection, authorization, or persistence. |
| Journal mutation | INSUFFICIENT | Selection proves row 12487 was already retained before activation. No selected row identifies its insertion, accepted-state write, removal, or retention after reward. The final `talkDefault` is unanswered before capture end. |

## Bounded negative

This held specimen does not contain the publisher offer/confirmation functions
needed to reconstruct acceptance, does not identify the reward actor as a
publisher, and ends before the final interaction receives a response. It cannot
establish offered-card identity, acceptance mutation, authoritative hand-in,
reward grant, or journal-row removal/retention.

## Packet, script, static, and inference boundary

- Packet facts are limited to the numeric rows and byte-attributable fields in
  `timeline.csv`.
- Client-script behavior supplies the meanings of `eventGL*`,
  `eventGuildleveReward`, signed finish signal, and presentation flow. It does
  not become packet evidence for server mutation.
- The tracked client lifecycle report records row 12487 as
  "Necrologos: Celeritous Impetus"; the pinned data repository inventories the
  source tables but does not distribute their decoded rows.
- The statement that the opening uses an already retained journal row is a
  packet-plus-script inference: `eventGLSelect` selects a retained ID, and the
  following calls carry 12487. No packet writes that row.
"""

    csv_out = io.StringIO(newline="")
    writer = csv.DictWriter(csv_out, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return {
        "timeline.csv": csv_out.getvalue().encode("ascii"),
        "accounting.json": (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii"),
        "verdicts.md": verdicts.encode("ascii"),
    }


ACCEPTANCE_SPECS = {
    "accept_leve.pcapng": {
        "sha256": "42b87e6c095db130def1de5bc382e428b4f4c12c8069c4682d6fa4bc7681967a",
        "owner": 0x44D8000A,
        "window": (49, 261),
        "locators": [
            ("regional-event-start", "c2s", 11, 2, 0x012D),
            ("regional-type", "s2c", 11, 0, 0x0130),
            ("regional-type-response", "c2s", 19, 1, 0x012E),
            ("regional-pack", "s2c", 16, 0, 0x0130),
            ("regional-pack-response", "c2s", 33, 1, 0x012E),
            ("regional-card-1", "s2c", 27, 1, 0x0130),
            ("regional-card-1-response", "c2s", 40, 1, 0x012E),
            ("regional-detail-12483", "s2c", 32, 1, 0x0130),
            ("regional-detail-12483-response", "c2s", 47, 2, 0x012E),
            ("regional-after-offer", "s2c", 37, 1, 0x0130),
            ("regional-journal-slot-3", "s2c", 38, 0, 0x0137),
            ("regional-after-offer-response", "c2s", 52, 1, 0x012E),
            ("regional-card-2", "s2c", 42, 1, 0x0130),
            ("regional-card-2-response", "c2s", 58, 1, 0x012E),
            ("regional-detail-12482", "s2c", 48, 0, 0x0130),
            ("regional-detail-12482-response", "c2s", 64, 1, 0x012E),
            ("regional-card-empty", "s2c", 52, 3, 0x0130),
            ("regional-card-empty-response", "c2s", 66, 1, 0x012E),
            ("regional-journal-slot-4", "s2c", 53, 0, 0x0137),
            ("regional-pack-close", "s2c", 54, 1, 0x0130),
            ("regional-pack-close-response", "c2s", 73, 1, 0x012E),
            ("regional-type-close", "s2c", 61, 0, 0x0130),
            ("regional-type-close-response", "c2s", 79, 1, 0x012E),
            ("regional-event-end", "s2c", 65, 1, 0x0131),
        ],
        "functions": {
            11: "eventTalkType", 16: "eventTalkPack", 27: "eventTalkCard",
            32: "eventTalkDetail", 37: "eventTalkAfterOffer",
            42: "eventTalkCard", 48: "eventTalkDetail", 52: "eventTalkCard",
            54: "eventTalkPack", 61: "eventTalkType",
        },
        "counts": {
            "c2s:0x0001": 24, "c2s:0x00ca": 142, "c2s:0x00cc": 1,
            "c2s:0x00cd": 1, "c2s:0x012d": 1, "c2s:0x012e": 10,
            "s2c:0x0001": 24, "s2c:0x00cf": 120, "s2c:0x00d2": 1,
            "s2c:0x0130": 10, "s2c:0x0131": 1, "s2c:0x0137": 2,
            "s2c:0x0161": 4, "s2c:0x0167": 4, "s2c:0x018d": 5,
        },
    },
    "accept_local_leve.pcapng": {
        "sha256": "3b4b071d88742a5d3c94a1e29ca6a4074cb6b9a9a60207118302fe22f932bd7c",
        "owner": 0x44D80009,
        "window": (34, 218),
        "locators": [
            ("local-event-start", "c2s", 6, 2, 0x012D),
            ("local-welcome", "s2c", 5, 0, 0x0130),
            ("local-welcome-response", "c2s", 10, 1, 0x012E),
            ("local-pack", "s2c", 9, 0, 0x0130),
            ("local-pack-response", "c2s", 18, 1, 0x012E),
            ("local-rank", "s2c", 15, 0, 0x0130),
            ("local-rank-response", "c2s", 24, 2, 0x012E),
            ("local-quest", "s2c", 20, 0, 0x0130),
            ("local-quest-response", "c2s", 38, 2, 0x012E),
            ("local-decide", "s2c", 30, 1, 0x0130),
            ("local-journal-slot-8", "s2c", 31, 0, 0x0137),
            ("local-decide-response", "c2s", 43, 1, 0x012E),
            ("local-quest-close", "s2c", 34, 1, 0x0130),
            ("local-quest-close-response", "c2s", 54, 1, 0x012E),
            ("local-rank-close", "s2c", 42, 0, 0x0130),
            ("local-rank-close-response", "c2s", 59, 1, 0x012E),
            ("local-pack-close", "s2c", 46, 0, 0x0130),
            ("local-pack-close-response", "c2s", 64, 1, 0x012E),
            ("local-finish", "s2c", 50, 0, 0x0130),
            ("local-finish-response", "c2s", 66, 1, 0x012E),
            ("local-event-end", "s2c", 54, 0, 0x0131),
        ],
        "functions": {
            5: "talkOfferWelcome", 9: "askOfferPack", 15: "askOfferRank",
            20: "askOfferQuest", 30: "talkOfferDecide", 34: "askOfferQuest",
            42: "askOfferRank", 46: "askOfferPack", 50: "finishTalkTurn",
        },
        "counts": {
            "c2s:0x0001": 22, "c2s:0x00ca": 126, "c2s:0x00cc": 1,
            "c2s:0x00cd": 1, "c2s:0x012d": 1, "c2s:0x012e": 9,
            "s2c:0x0001": 22, "s2c:0x00cf": 110, "s2c:0x00d2": 1,
            "s2c:0x00d9": 3, "s2c:0x0130": 9, "s2c:0x0131": 1,
            "s2c:0x0137": 1, "s2c:0x0167": 2, "s2c:0x018d": 5,
        },
    },
}

PROPERTY_NAMES = {
    "0x19030954": "work.guildleveId[3]",
    "0xb4f4e4ca": "work.guildleveId[4]",
    "0x3e8a7bb7": "playerWork.questGuildleve[0]",
    "0x4f5efe11": "work.guildleveId[8]",
}


def decode_lua_values(data: bytes) -> tuple[list[str], int | None]:
    values = []
    offset = 0
    while offset < len(data):
        tag = data[offset]
        offset += 1
        if tag == 0x0F:
            return values, None
        if tag in {0x00, 0x06}:
            if offset + 4 > len(data):
                raise ValueError("truncated Lua integer/reference")
            value = int.from_bytes(data[offset:offset + 4], "big")
            offset += 4
            values.append(("int:" if tag == 0x00 else "actor:") + str(value))
        elif tag == 0x03:
            values.append("bool:true")
        elif tag == 0x04:
            values.append("bool:false")
        elif tag == 0x05:
            values.append("nil")
        else:
            return values, tag
    raise ValueError("Lua value list has no terminator")


def _lua_summary(data: bytes) -> str:
    values, unsupported = decode_lua_values(data)
    parts = ["lua_values=" + ",".join(values)]
    if unsupported is not None:
        parts.append(f"unsupported_tag=0x{unsupported:02x}")
    return ";".join(parts)


def _acceptance_fields(stage: str, event: dict, app: bytes, spec: dict) -> str:
    opcode = event["opcode_value"]
    if opcode == 0x012D:
        owner = int.from_bytes(app[4:8], "little")
        if owner != spec["owner"] or _event_name(app) != "talkDefault":
            raise ValueError(f"unexpected acceptance EventStart at {stage}")
        return f"owner_actor_id={_hex32(owner)}"
    if opcode == 0x0130:
        owner = int.from_bytes(app[4:8], "little")
        if owner != spec["owner"]:
            raise ValueError(f"unexpected RunEvent owner at {stage}")
        function = _function_name(app)
        if function != spec["functions"][event["frame_index"]]:
            raise ValueError(f"unexpected acceptance function at {stage}")
        return f"owner_actor_id={_hex32(owner)};" + _lua_summary(app[0x49:])
    if opcode == 0x012E:
        if app[16] != 1:
            raise ValueError(f"unexpected EventUpdate result count at {stage}")
        return _lua_summary(app[17:])
    if opcode == 0x0137:
        records, _declared, terminated, _consumed = parse_records(app)
        if terminated:
            raise ValueError(f"truncated property records at {stage}")
        fields = []
        for record in records:
            name = PROPERTY_NAMES.get(record["property_hash"], "unresolved")
            fields.append(
                f"{record['property_hash']}:{name}:{record['value_width']}:"
                f"{record['value_hex']}:{record['value_u_le']}"
            )
        return "property_records=" + ",".join(fields)
    if opcode == 0x0131:
        name = app[9:41].split(b"\0", 1)[0].decode("ascii")
        if name != "talkDefault":
            raise ValueError(f"unexpected EndEvent name at {stage}")
        return "event_name=talkDefault"
    return ""


def _window_counts(events: list[dict], start: int, end: int) -> dict[str, int]:
    counts = Counter()
    for event in events:
        if event["lane"] != "main" or not start <= event["capture_packet_index"] <= end:
            continue
        opcode = event.get("opcode_value")
        key = f"{event['direction']}:" + ("none" if opcode is None else f"0x{opcode:04x}")
        counts[key] += 1
    return dict(sorted(counts.items()))


def _build_acceptance_capture(name: str, spec: dict) -> tuple[list[dict], dict]:
    path = OBJECTS_DIR / name
    if sha256_file(path) != spec["sha256"]:
        raise ValueError(f"{name} identity mismatch")
    events, totals, lane_counts = _decode_capture(path)
    rows = []
    for stage, direction, frame_index, subevent_index, opcode in spec["locators"]:
        event = _select(events, direction, frame_index, subevent_index, opcode)
        app = event["sub_body"][16:]
        rows.append({
            "capture": name,
            "stage": stage,
            "capture_packet_index": event["capture_packet_index"],
            "capture_timestamp_utc": event["capture_timestamp_utc"],
            "lane_index": event["lane_index"],
            "lane": event["lane"],
            "direction": direction,
            "frame_index": frame_index,
            "frame_stream_offset": event["frame_stream_offset"],
            "subevent_index": subevent_index,
            "subevent_offset": event["subevent_offset"],
            "subevent_size": event["subevent_size"],
            "opcode": f"0x{opcode:04x}",
            "transport_source_actor_id_hex": _hex32(event["transport_source_actor_id"]),
            "transport_target_actor_id_hex": _hex32(event["transport_target_actor_id"]),
            "event_name": _event_name(app) if opcode == 0x012D else "",
            "function_name": _function_name(app) if opcode == 0x0130 else "",
            "attributable_fields": _acceptance_fields(stage, event, app, spec),
            "application_sha256": sha256_bytes(app),
        })
    order_rows(rows)
    for sequence, row in enumerate(rows, 1):
        row["sequence"] = sequence

    start, end = spec["window"]
    counts = _window_counts(events, start, end)
    if counts != spec["counts"]:
        raise ValueError(f"{name} transaction accounting changed: {counts}")
    return rows, {
        "capture": name,
        "capture_sha256": spec["sha256"],
        "capture_size_bytes": path.stat().st_size,
        "decode": {
            "lane_counts": lane_counts,
            "c2s_frames": totals["c2s_frames"],
            "s2c_frames": totals["s2c_frames"],
            "c2s_wrapped_subevents": totals["c2s_wrapped_subevents"],
            "s2c_wrapped_subevents": totals["s2c_wrapped_subevents"],
            "c2s_admitted_unparsed_stream_bytes": totals["c2s_admitted_unparsed_stream_bytes"],
            "s2c_admitted_unparsed_stream_bytes": totals["s2c_admitted_unparsed_stream_bytes"],
        },
        "transaction_window": {
            "first_capture_packet_index": start,
            "last_capture_packet_index": end,
            "main_lane_subevents": sum(counts.values()),
            "opcode_counts": counts,
            "selected_timeline_rows": len(rows),
        },
    }


def build_outputs(path: Path = CAPTURE) -> dict[str, bytes]:
    party_outputs = _build_party_outputs(path)
    party_rows = list(csv.DictReader(io.StringIO(party_outputs["timeline.csv"].decode("ascii"))))
    party_accounting = json.loads(party_outputs["accounting.json"])
    all_rows = []
    acceptance_accounting = []
    for name, spec in ACCEPTANCE_SPECS.items():
        rows, accounting = _build_acceptance_capture(name, spec)
        all_rows.extend(rows)
        acceptance_accounting.append(accounting)
    all_rows.extend(party_rows)

    accounting = {
        "schema_version": 2,
        "study": "regional-guildleve-publisher-contract",
        "acceptance_captures": acceptance_accounting,
        "party_activation_comparison": party_accounting,
        "capture_roles": {
            "accept_leve.pcapng": "regional publisher acceptance",
            "accept_local_leve.pcapng": "local publisher acceptance comparison",
            "party_battle_leve.pcapng": "already-retained regional activation and completion comparison",
        },
        "packet_exclusions": {
            "0x0001": "keepalive",
            "0x00ca/0x00cf": "movement",
            "0x00cc/0x00cd": "targeting around interaction start",
            "0x00d2/0x00d9": "unbound presentation sidecars",
            "0x0161/0x0167": "opaque adjacent state records with no acceptance field attribution",
            "0x018d": "map-marker traffic with no acceptance field attribution",
            "non-main regional lane": "two chat-lane records with no inner game opcode",
        },
        "boundaries": [
            "Capture packet indexes order frame-completion witnesses and do not independently establish causality.",
            "The regional detail true results are client confirmation intent; the matching synchronized journal-slot writes are the first server acknowledgement visible in the capture.",
            "Synchronized journal insertion does not prove durable persistence, allowance consumption, publisher-state mutation, reward policy, or hand-in.",
            "The local capture shares the event envelope but uses a different function family and journal-slot representation.",
        ],
    }

    verdicts = """# Regional Guildleve Publisher Contract Verdicts

The acceptance inputs are `accept_leve.pcapng`, SHA-256
`42b87e6c095db130def1de5bc382e428b4f4c12c8069c4682d6fa4bc7681967a`,
and the independent local comparison `accept_local_leve.pcapng`, SHA-256
`3b4b071d88742a5d3c94a1e29ca6a4074cb6b9a9a60207118302fe22f932bd7c`.
The retained-row activation/completion comparison remains
`party_battle_leve.pcapng`, SHA-256
`6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f`.

| Question | Verdict | Evidence boundary |
|---|---|---|
| Regional publisher actor | SUPPORTED | EventStart and all ten regional RunEvent callbacks carry owner actor `0x44D8000A`. The callback family binds the interaction to the retail `PopulaceGuildlevePublisher` client class; no static actor-row identity is inferred. |
| Offered Guildleve identity | SUPPORTED | The first `eventTalkCard` offers 12483 in card 1 and 12482 in card 4. After card 1 is selected, the detail callback carries 12483; after card 4 is selected, the detail callback carries 12482. |
| Acceptance intent | SUPPORTED | The client returns card indexes 1 and 4, then returns boolean true from each matching `eventTalkDetail`. Retail Lua defines that true only as successful confirmation UI, not server mutation. |
| Acceptance acknowledgement | SUPPORTED | In the same bounded EventStart-EndEvent window, server `0x0137` writes 12483 to synchronized `work.guildleveId[3]` and 12482 to `work.guildleveId[4]`. These are the first captured client-visible accepted-row acknowledgements. |
| Client journal insertion | SUPPORTED | The two nonzero synchronized slot writes place the accepted IDs in the client's retained journal state. |
| Durable persistence | INSUFFICIENT | No reconnect or relog specimen proves that either accepted row survives the captured session. |
| Allowance check or decrement | INSUFFICIENT | No selected callback argument, synchronized property, or adjacent packet is identified as an allowance amount, check, or decrement. A paired allowance-bearing before/after state is required. |
| Publisher-state mutation | INSUFFICIENT | No packet in the bounded window writes an identified field on owner actor `0x44D8000A`. A named publisher property before/after transition is required. |
| Director creation or activation | INSUFFICIENT | The acceptance window has no `eventGLStart`, content-group start, director member, or identified director actor. A subsequent structurally linked activation specimen is required. |
| Regional/local shared contract | REFUTED | Both use EventStart, RunEvent, EventUpdate, synchronized journal work, and EndEvent, but local uses `talkOfferWelcome`/`askOffer*`/`talkOfferDecide`, owner `0x44D80009`, and `work.guildleveId[8]=202`; regional uses `eventTalk*`, owner `0x44D8000A`, and slots 3/4. Only the outer envelope is shared. |
| Bounded Bahamut publisher acceptance | SUPPORTED WITH BOUNDARIES | The capture supports offer cards, selected-card returns, detail confirmation, subsequent offer-list closure, and synchronized insertion of the selected IDs. Offer eligibility, allowance policy, durable persistence, and later activation remain separate requirements. |
| Hand-in, reward grant, or journal removal | INSUFFICIENT | The acceptance captures end after offer closure and contain no identified hand-in, attributable grant, or nonzero-to-zero accepted-slot transition. The party comparison supports reward presentation only. |

## Regional acceptance sequence

Owner `0x44D8000A` starts `talkDefault`. The server presents type and pack
selection, then cards containing 12483 and 12482. Card result 1 plus a true
detail result for 12483 appears before `work.guildleveId[3]=12483` in capture
order. The next card list retains only 12482; card result 4 plus a true detail
result appears before an empty card list and `work.guildleveId[4]=12482`.
Pack/type closure and EndEvent complete the bounded transaction.

## Local comparison

Owner `0x44D80009` uses `talkOfferWelcome`, `askOfferPack`, `askOfferRank`,
`askOfferQuest`, `talkOfferDecide`, and `finishTalkTurn`. The quest selector
offers 120222 and 120202 and returns index 2. The capture then records
synchronized `work.guildleveId[8]=202` plus a separate
`playerWork.questGuildleve[0]` record whose value semantics remain unpromoted.
This supports a local accepted row while proving that the regional callback
and slot contract is not shared.

## Packet, script, static, and inference boundary

- Packet facts are the actor IDs, function strings, typed Lua values, property
  records, hashes, and ordering in `timeline.csv`.
- Retail client scripts establish card-index and detail-confirmation UI
  behavior. They do not establish authoritative persistence or allowance
  policy.
- Property names are exact backward-MurmurHash2 resolutions promoted from the
  pinned `xivl-client-structs` revision. They identify synchronized client
  fields, not the server's durable storage model.
- `accounting.json` reconciles every main-lane packet in each bounded window;
  excluded opcode families remain numeric sidecars unless another study
  supplies their semantics.
"""

    csv_out = io.StringIO(newline="")
    writer = csv.DictWriter(csv_out, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(all_rows)
    return {
        "timeline.csv": csv_out.getvalue().encode("ascii"),
        "accounting.json": (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii"),
        "verdicts.md": verdicts.encode("ascii"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    stale = []
    for name, data in outputs.items():
        target = OUT / name
        if args.check:
            if not target.is_file() or target.read_bytes() != data:
                stale.append(str(target))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    if stale:
        print("stale regional guildleve publisher artifacts:\n  " + "\n  ".join(stale))
        return 1
    print(("verified" if args.check else "wrote") + " 3 regional guildleve publisher artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
