#!/usr/bin/env python3
"""Extract the bounded regional guildleve publisher contract from one capture."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from extract_00da_00e1_comparison import _decode_capture  # type: ignore  # noqa: E402
from extract_property_stream_catalog import parse_records  # type: ignore  # noqa: E402

CAPTURE = REPO_ROOT / "sources" / "pcap-1.23b" / "objects" / "party_battle_leve.pcapng"
CAPTURE_SHA256 = "6327e5e1f5cbd51a9baaa9bcbacf53ca51c50a98fe4b66ae3e6bdecd9198089f"
OUT = REPO_ROOT / "studies" / "regional-guildleve-publisher-contract" / "derived"
PLAYER_ACTOR_ID = 0x029B2941
START_OWNER_ACTOR_ID = 0x4510000C
REWARD_OWNER_ACTOR_ID = 0x45100D5B
DIRECTOR_ACTOR_ID = 0x45100D44
GUILDLEVE_ID = 12487

FIELDS = [
    "sequence", "stage", "capture_packet_index", "capture_timestamp_utc",
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
        records, declared, terminated = parse_records(app)
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


def build_outputs(path: Path = CAPTURE) -> dict[str, bytes]:
    if sha256_file(path) != CAPTURE_SHA256:
        raise ValueError("party_battle_leve.pcapng identity mismatch")
    events, totals, lane_counts = _decode_capture(path)
    rows = []
    for stage, direction, frame_index, subevent_index, opcode in LOCATORS:
        event = _select(events, direction, frame_index, subevent_index, opcode)
        app = event["sub_body"][16:]
        rows.append({
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
