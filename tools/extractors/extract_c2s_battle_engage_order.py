#!/usr/bin/env python3
"""Build the sanitized c2s battle engage and disengage order study.

Products carry shape classes, counts, packet locators, field-value classes,
and millisecond deltas between completing capture packets. Actor ids,
absolute timestamps, and raw payloads stay out of the products.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import zlib
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools" / "extractors"
OBJECTS = Path(
    os.environ.get(
        "XIVL_PCAP_OBJECTS_DIR", REPO_ROOT / "sources" / "pcap-1.23b" / "objects"
    )
)
MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"
STUDY_ID = "c2s-battle-engage-order"
OUT = REPO_ROOT / "studies" / STUDY_ID / "derived"

sys.path.insert(0, str(TOOLS))

GENERATOR_VERSION = "2"
MEMBER_COUNT = 54

OP_POSITION = 0x00CA
OP_LOCK = 0x00CC
OP_SET = 0x00CD
OP_START = 0x012D
OP_END_EVENT = 0x0131
OP_STATE = 0x0134
OP_ECHO_D2 = 0x00D2
OP_ECHO_D3 = 0x00D3
RESULT_OPCODES = (0x0139, 0x013A, 0x013B, 0x013C)

# Application offsets count from the first byte after the 16-byte game-message header.
START_APP_LEN = 184
START_OWNER = 4
START_CRC = 12
START_SELECTOR = 0x10
START_NAME = 0x11
START_NAME_LEN = 0x20
START_WINDOW = 0x31
START_WINDOW_LEN = 128
END_EVENT_NAME = 9
RESULT_COMMAND = 0x24
RESULT_FIRST_TARGET = 0x28
TARGET_APP_LEN = 8

CLEAR_ACTOR = 0xC0000000
PENDING_VALUE = 0xE0000000
STATIC_COMMAND_HIGH = 0xA0F0
MODE_COMMANDS = {21001: "Active Mode", 21002: "Passive Mode"}
ATTACK_COMMAND = 22104
TALK_NAME = "talkDefault"
FORCED_NAME = "commandForced"

TAIL_NIL = 0x05
TAIL_INT = 0x00
TAIL_ACTOR = 0x06
TAIL_END = 0x0F


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def event_name(app: bytes, offset: int) -> str:
    return (
        app[offset : offset + START_NAME_LEN]
        .split(b"\0", 1)[0]
        .decode("ascii", "replace")
    )


def typed_tail(window: bytes) -> list[tuple[str, int | None]]:
    """Decode the witnessed nil/int/actor-reference/terminator tag shapes."""
    values: list[tuple[str, int | None]] = []
    offset = 0
    while offset < len(window):
        tag = window[offset]
        offset += 1
        if tag == TAIL_END:
            return values
        if tag == TAIL_NIL:
            values.append(("nil", None))
        elif tag in (TAIL_INT, TAIL_ACTOR):
            if offset + 4 > len(window):
                raise ValueError("typed tail has a truncated value")
            value = int.from_bytes(window[offset : offset + 4], "big")
            values.append(("int" if tag == TAIL_INT else "actor", value))
            offset += 4
        else:
            raise ValueError(f"unsupported typed-tail tag 0x{tag:02x}")
    raise ValueError("typed tail has no terminator")


def tail_shape(values: list[tuple[str, int | None]], lock_target: int | None) -> str:
    """Render a tail without actor ids: actor references become a relation class."""
    parts = []
    for kind, value in values:
        if kind == "nil":
            parts.append("nil")
        elif kind == "int":
            parts.append(f"int {value}")
        else:
            parts.append("actor=lock target" if value == lock_target else "actor=other")
    return ",".join(parts)


def classify_lock(actor: int, second: int) -> str:
    if actor == CLEAR_ACTOR:
        return "clear"
    return "actor, zero" if second == 0 else "actor, nonzero"


def classify_set(actor: int, second: int, self_actor: int) -> str:
    if actor == CLEAR_ACTOR:
        return "clear, 0xe0000000" if second == PENDING_VALUE else "clear, other"
    who = "self" if actor == self_actor else "actor"
    if second == PENDING_VALUE:
        return f"{who}, 0xe0000000"
    if second == actor:
        return f"{who}, same actor"
    return f"{who}, other"


def record_class(rec: dict | None, self_actor: int) -> str:
    """Name a c2s record by opcode and shape, with no actor id."""
    if rec is None:
        return "frame end"
    op = rec["op"]
    if op == OP_LOCK:
        return "0x00cc " + classify_lock(rec["actor"], rec["second"])
    if op == OP_SET:
        return "0x00cd " + classify_set(rec["actor"], rec["second"], self_actor)
    if op == OP_START:
        return f"0x012d {rec['name']}"
    return f"0x{op:04x}"


def mode_label(mode: int | None) -> str:
    return "none" if mode is None else str(mode)


def ms(later: dict, earlier: dict) -> int:
    return round((later["time_us"] - earlier["time_us"]) / 1000)


def distribution(values: list[int]) -> dict:
    if not values:
        return {"n": 0}
    ordered = sorted(values)
    mid = len(ordered) // 2
    median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2
    if median == int(median):
        median = int(median)
    return {"n": len(ordered), "min": ordered[0], "median": median, "max": ordered[-1]}


def counted(counter: Counter) -> dict[str, int]:
    return {str(k): v for k, v in sorted(counter.items(), key=lambda kv: str(kv[0]))}


def rows_from(counter: Counter, fields: tuple[str, ...]) -> list[dict]:
    return [
        {**dict(zip(fields, key)), "count": count}
        for key, count in sorted(
            counter.items(), key=lambda kv: [str(v) for v in kv[0]]
        )
    ]


def slim(event: dict) -> dict:
    """Keep the ordering keys and the application bytes of one wrapped record."""
    sub_body = event.get("sub_body", b"")
    return {
        "lane": event["lane_index"],
        "direction": event["direction"],
        "frame": event["frame_index"],
        "sub": event["subevent_index"],
        "packet": event["capture_packet_index"],
        "time_us": event["capture_time_us"],
        "src": event["transport_source_actor_id"],
        "op": event["opcode_value"],
        "app": sub_body[16:],
    }


def annotate(rec: dict) -> None:
    """Decode the c2s fields this study joins on, refusing unexpected shapes."""
    if rec["direction"] != "c2s":
        return
    app = rec["app"]
    if rec["op"] in (OP_LOCK, OP_SET):
        if len(app) != TARGET_APP_LEN:
            raise ValueError(f"unexpected 0x{rec['op']:04x} length {len(app)}")
        rec["actor"], rec["second"] = struct.unpack_from("<II", app, 0)
    elif rec["op"] == OP_START:
        if len(app) != START_APP_LEN:
            raise ValueError(f"unexpected 0x012d length {len(app)}")
        rec["owner"] = u32(app, START_OWNER)
        rec["trigger"] = u32(app, 0)
        rec["crc"] = u32(app, START_CRC)
        rec["selector"] = app[START_SELECTOR]
        rec["name"] = event_name(app, START_NAME)
        rec["window"] = app[START_WINDOW : START_WINDOW + START_WINDOW_LEN]
        owner_high, owner_low = rec["owner"] >> 16, rec["owner"] & 0xFFFF
        rec["mode"] = (
            owner_low
            if owner_high == STATIC_COMMAND_HIGH and owner_low in MODE_COMMANDS
            else None
        )


def first_after(timeline: list[dict], start: int, predicate, stop: int | None = None):
    end = len(timeline) if stop is None else stop
    for index in range(start + 1, end):
        if predicate(timeline[index]):
            return index
    return None


def analyze_capture(records: list[dict]) -> dict:
    """Join one capture's c2s target and mode records to the server records."""
    for rec in records:
        annotate(rec)
    timeline = sorted(
        records,
        key=lambda r: (r["packet"], r["lane"], r["direction"], r["frame"], r["sub"]),
    )
    for position, rec in enumerate(timeline):
        rec["pos"] = position
    c2s = sorted(
        (r for r in records if r["direction"] == "c2s"),
        key=lambda r: (r["lane"], r["frame"], r["sub"]),
    )
    actor_ids = {r["src"] for r in records}
    for rec in c2s:
        if rec["op"] in (OP_LOCK, OP_SET):
            actor_ids.add(rec["actor"])
    out = {
        "starts": [],
        "modes": [],
        "locks": [],
        "engages": [],
        "clears": [],
        "talks": [],
        "decides": [],
        "lock_seconds": Counter(),
        "set_classes": Counter(),
    }
    mode = None
    last_actor_lock = None
    for i, rec in enumerate(c2s):
        nxt = c2s[i + 1] if i + 1 < len(c2s) else None
        same_frame_next = (
            nxt
            if nxt and (nxt["lane"], nxt["frame"]) == (rec["lane"], rec["frame"])
            else None
        )
        prv = c2s[i - 1] if i else None
        same_frame_prev = (
            prv
            if prv and (prv["lane"], prv["frame"]) == (rec["lane"], rec["frame"])
            else None
        )
        self_actor = rec["src"]
        op = rec["op"]
        if op == OP_START:
            out["starts"].append(rec)
            if rec["mode"] is not None:
                mode = rec["mode"]
                out["modes"].append(
                    {
                        "rec": rec,
                        "lock_target": last_actor_lock and last_actor_lock["actor"],
                    }
                )
            if rec["name"] == TALK_NAME:
                out["talks"].append(
                    {
                        "selector": rec["selector"],
                        "prev": record_class(same_frame_prev, self_actor),
                        "prev_actor_is_owner": bool(
                            same_frame_prev
                            and same_frame_prev["op"] in (OP_LOCK, OP_SET)
                            and same_frame_prev["actor"] == rec["owner"]
                        ),
                        "next": record_class(same_frame_next, self_actor),
                        "next_actor_is_owner": bool(
                            same_frame_next
                            and same_frame_next["op"] in (OP_LOCK, OP_SET)
                            and same_frame_next["actor"] == rec["owner"]
                        ),
                    }
                )
        elif op == OP_SET:
            out["set_classes"][
                classify_set(rec["actor"], rec["second"], self_actor)
            ] += 1
            if rec["second"] == rec["actor"] and rec["actor"] != CLEAR_ACTOR:
                after_lock = bool(
                    same_frame_prev
                    and same_frame_prev["op"] == OP_LOCK
                    and same_frame_prev["actor"] == rec["actor"]
                )
                out["decides"].append(
                    {
                        "preceded_by_same_frame_lock": after_lock,
                        "self": rec["actor"] == self_actor,
                        "mode": mode,
                        "next": record_class(same_frame_next, self_actor),
                    }
                )
        elif op == OP_LOCK:
            shape = classify_lock(rec["actor"], rec["second"])
            second = rec["second"]
            if shape == "actor, zero":
                value = "0x00000000"
            elif second in actor_ids:
                value = "actor id"
            else:
                value = f"0x{second:08x}"
            out["lock_seconds"][(shape, value)] += 1
            out["locks"].append(
                {
                    "shape": shape,
                    "mode": mode,
                    "next": record_class(same_frame_next, self_actor),
                }
            )
            if shape == "actor, nonzero":
                out["engages"].append(
                    engage_row(rec, c2s, i, timeline, self_actor, mode)
                )
            elif shape == "clear":
                out["clears"].append(
                    clear_row(
                        rec,
                        c2s,
                        i,
                        timeline,
                        last_actor_lock,
                        same_frame_next,
                        self_actor,
                    )
                )
            if shape != "clear":
                last_actor_lock = rec
    for entry in out["modes"]:
        entry.update(mode_reply(entry["rec"], timeline, c2s))
    return out


def frame_shape(c2s: list[dict], rec: dict, self_actor: int) -> str:
    return " + ".join(
        record_class(r, self_actor)
        for r in c2s
        if (r["lane"], r["frame"]) == (rec["lane"], rec["frame"])
        and r["op"] != OP_POSITION
    )


def engage_row(
    lock: dict,
    c2s: list[dict],
    index: int,
    timeline: list[dict],
    self_actor: int,
    mode: int | None,
) -> dict:
    actor = lock["actor"]
    select = None
    for back in range(index - 1, -1, -1):
        rec = c2s[back]
        if rec["op"] == OP_LOCK:
            break
        if (
            rec["op"] == OP_SET
            and rec["actor"] == actor
            and rec["second"] == PENDING_VALUE
        ):
            select = rec
            break
    # The window runs to the next actor lock. A clear inside it does not end it,
    # since the server can still send results onto the actor after a clear.
    clear = None
    next_lock = None
    for rec in c2s[index + 1 :]:
        if rec["op"] != OP_LOCK:
            continue
        if rec["actor"] != CLEAR_ACTOR:
            next_lock = rec
            break
        if clear is None:
            clear = rec
    stop = next_lock["pos"] if next_lock else None

    def is_swing(r: dict) -> bool:
        return (
            r["direction"] == "s2c"
            and r["op"] in RESULT_OPCODES
            and len(r["app"]) > RESULT_FIRST_TARGET + 3
            and u32(r["app"], 0) == self_actor
            and struct.unpack_from("<H", r["app"], RESULT_COMMAND)[0] == ATTACK_COMMAND
            and u32(r["app"], RESULT_FIRST_TARGET) == actor
        )

    swing = first_after(timeline, lock["pos"], is_swing, stop)
    post_clear = []
    if clear is not None:
        end = len(timeline) if stop is None else stop
        post_clear = [
            timeline[k] for k in range(clear["pos"] + 1, end) if is_swing(timeline[k])
        ]
    echo = first_after(
        timeline,
        lock["pos"],
        lambda r: (
            r["direction"] == "s2c"
            and r["op"] == OP_ECHO_D2
            and len(r["app"]) >= 4
            and u32(r["app"], 0) == actor
        ),
        stop,
    )
    row = {
        "c2s_frame": lock["frame"],
        "packet": lock["packet"],
        "mode": mode,
        "frame_shape": frame_shape(c2s, lock, self_actor),
        "select": None,
        "first_d2_ms": None if echo is None else ms(timeline[echo], lock),
        "d2_after_clear": bool(
            echo is not None and clear is not None and echo > clear["pos"]
        ),
        "clear_ms": None if clear is None else ms(clear, lock),
        "first_attack_ms": None,
        "attack_after_clear": False,
        "attacks_after_clear": len(post_clear),
        "clear_to_attack_ms": [ms(hit, clear) for hit in post_clear],
        "c2s_before_attack": {},
    }
    if select is not None:
        select_echo = first_after(
            timeline,
            select["pos"],
            lambda r: (
                r["direction"] == "s2c"
                and r["op"] == OP_ECHO_D3
                and len(r["app"]) >= 4
                and u32(r["app"], 0) == actor
            ),
        )
        row["select"] = {
            "c2s_frame": select["frame"],
            "packet": select["packet"],
            "frame_gap": lock["frame"] - select["frame"],
            "ms_to_lock": ms(lock, select),
            "frame_shape": frame_shape(c2s, select, self_actor),
            "d3_before_lock": select_echo is not None
            and timeline[select_echo]["pos"] < lock["pos"],
        }
    if swing is not None:
        hit = timeline[swing]
        row["first_attack_ms"] = ms(hit, lock)
        row["first_attack_opcode"] = f"0x{hit['op']:04x}"
        row["attack_after_clear"] = clear is not None and swing > clear["pos"]
        between = Counter(
            record_class(r, self_actor)
            for r in timeline[lock["pos"] + 1 : swing]
            if r["direction"] == "c2s"
            and (r["lane"], r["frame"]) != (lock["lane"], lock["frame"])
        )
        row["c2s_before_attack"] = counted(between)
    return row


def clear_row(
    lock: dict,
    c2s: list[dict],
    index: int,
    timeline: list[dict],
    last_actor_lock: dict | None,
    same_frame_next: dict | None,
    self_actor: int,
) -> dict:
    after = (
        "none"
        if last_actor_lock is None
        else classify_lock(last_actor_lock["actor"], last_actor_lock["second"])
    )
    following_mode = None
    for rec in c2s[index + 1 :]:
        if rec["op"] == OP_LOCK and rec["actor"] != CLEAR_ACTOR:
            break
        if rec["op"] == OP_START and rec["mode"] is not None:
            following_mode = rec
            break
    echoes = []
    for opcode in (OP_ECHO_D2, OP_ECHO_D3):
        found = first_after(
            timeline,
            lock["pos"],
            lambda r, opcode=opcode: (
                r["direction"] == "s2c"
                and r["op"] == opcode
                and len(r["app"]) >= 4
                and u32(r["app"], 0) == CLEAR_ACTOR
            ),
        )
        echoes.append(None if found is None else timeline[found])
    d2, d3 = echoes
    if d2 is not None and d3 is not None:
        same = (d2["lane"], d2["frame"]) == (d3["lane"], d3["frame"])
        echo = (
            "0x00d2 then 0x00d3, one frame"
            if same and d2["sub"] < d3["sub"]
            else "other"
        )
    else:
        echo = "missing"
    return {
        "after": after,
        "next": record_class(same_frame_next, self_actor),
        "next_mode": "none" if following_mode is None else str(following_mode["mode"]),
        "mode_ms": None if following_mode is None else ms(following_mode, lock),
        "echo": echo,
    }


def mode_reply(request: dict, timeline: list[dict], c2s: list[dict]) -> dict:
    """Find the first commandForced EndEvent the server sends the requester."""
    requester = request["src"]
    prior = "none"
    for r in timeline[: request["pos"]]:
        if r["direction"] == "s2c" and r["op"] == OP_STATE and r["src"] == requester:
            prior = f"{r['app'][0]:02x}"
    end = first_after(
        timeline,
        request["pos"],
        lambda r: (
            r["direction"] == "s2c"
            and r["op"] == OP_END_EVENT
            and r["src"] == requester
            and event_name(r["app"], END_EVENT_NAME) == FORCED_NAME
        ),
    )
    if end is None:
        return {"reply": "missing", "prior_state": prior}
    end_rec = timeline[end]
    frame = [
        r
        for r in timeline
        if r["direction"] == "s2c"
        and (r["lane"], r["frame"]) == (end_rec["lane"], end_rec["frame"])
        and r["src"] == requester
    ]
    frame.sort(key=lambda r: r["sub"])
    parts = []
    for r in frame:
        if r["op"] == OP_STATE:
            parts.append(f"0x0134 {r['app'][0]:02x} {r['app'][1]:02x}")
        elif r["op"] in RESULT_OPCODES:
            command = struct.unpack_from("<H", r["app"], RESULT_COMMAND)[0]
            relation = "request" if command == request["mode"] else "other"
            parts.append(f"0x{r['op']:04x} command={relation}")
        elif r["op"] == OP_END_EVENT:
            parts.append(f"0x0131 {event_name(r['app'], END_EVENT_NAME)}")
        else:
            parts.append(f"0x{r['op']:04x}")
    target_before_reply = sum(
        1
        for r in c2s
        if r["op"] in (OP_LOCK, OP_SET) and request["pos"] < r["pos"] < end_rec["pos"]
    )
    return {
        "reply": " + ".join(parts),
        "prior_state": prior,
        "reply_ms": ms(end_rec, request),
        "targets_before_reply": target_before_reply,
    }


def load_manifest_members() -> list[dict]:
    import yaml

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    return list(manifest.get("members", []))


def decode_records(path: Path) -> tuple[list[dict], Counter]:
    from extract_00da_00e1_comparison import _decode_capture  # type: ignore
    from extract_streams import clear_packet_cache  # type: ignore

    events, totals, _lanes = _decode_capture(path)
    clear_packet_cache()
    return [slim(e) for e in events if e["opcode_value"] is not None], totals


def build_accounting() -> dict:
    members = load_manifest_members()
    if len(members) != MEMBER_COUNT:
        raise ValueError(f"expected {MEMBER_COUNT} source members, got {len(members)}")
    captures = {}
    decode = Counter()
    starts = Counter()
    modes = Counter()
    replies = Counter()
    reply_ms = []
    targets_before_reply = 0
    locks = Counter()
    lock_seconds = Counter()
    set_classes = Counter()
    engages = []
    clears = Counter()
    clear_mode_ms = []
    talks = Counter()
    decides = Counter()
    for member in sorted(members, key=lambda m: m["file"]):
        name = member["file"]
        path = OBJECTS / name
        if path.stat().st_size != int(member["size_bytes"]):
            raise ValueError(f"{name}: size differs from the source manifest")
        if sha256(path) != member["sha256"]:
            raise ValueError(f"{name}: SHA-256 differs from the source manifest")
        records, totals = decode_records(path)
        for key in (
            "c2s_subevent_truncations",
            "c2s_compressed_frame_inflate_failures",
        ):
            if totals.get(key):
                raise ValueError(f"{name}: {key} is nonzero")
        decode["c2s_frames"] += totals.get("c2s_frames", 0)
        decode["c2s_subevents"] += totals.get("c2s_subevents", 0)
        result = analyze_capture(records)
        for rec in result["starts"]:
            starts["messages"] += 1
            starts["owner_low16_is_attack_command"] += (
                rec["owner"] & 0xFFFF
            ) == ATTACK_COMMAND
            starts["crc32_matches_parameter_window"] += (
                zlib.crc32(rec["window"]) == rec["crc"]
            )
        per = Counter()
        for entry in result["modes"]:
            rec = entry["rec"]
            shape = tail_shape(typed_tail(rec["window"]), entry["lock_target"])
            modes[
                (
                    rec["mode"],
                    rec["name"],
                    rec["selector"],
                    rec["trigger"] == rec["src"],
                    shape,
                    f"0x{rec['crc']:08x}",
                )
            ] += 1
            replies[(rec["mode"], entry["prior_state"], shape, entry["reply"])] += 1
            if "reply_ms" in entry:
                reply_ms.append(entry["reply_ms"])
                targets_before_reply += entry["targets_before_reply"]
            per[f"mode {rec['mode']}"] += 1
        for row in result["locks"]:
            locks[(row["shape"], mode_label(row["mode"]), row["next"])] += 1
            per[f"0x00cc {row['shape']}"] += 1
        lock_seconds.update(result["lock_seconds"])
        set_classes.update(result["set_classes"])
        for cls, count in result["set_classes"].items():
            per[f"0x00cd {cls}"] += count
        for row in result["engages"]:
            engages.append({"capture": name, **row, "mode": mode_label(row["mode"])})
        for row in result["clears"]:
            clears[(row["after"], row["next"], row["next_mode"], row["echo"])] += 1
            if row["mode_ms"] is not None and row["after"] == "actor, nonzero":
                clear_mode_ms.append(row["mode_ms"])
        for row in result["talks"]:
            talks[
                (
                    row["selector"],
                    row["prev"],
                    row["prev_actor_is_owner"],
                    row["next"],
                    row["next_actor_is_owner"],
                )
            ] += 1
        for row in result["decides"]:
            decides[
                (
                    row["preceded_by_same_frame_lock"],
                    row["self"],
                    mode_label(row["mode"]),
                    row["next"],
                )
            ] += 1
        if per:
            captures[name] = {
                "sha256": member["sha256"],
                "size_bytes": int(member["size_bytes"]),
                "counts": counted(per),
            }
    return {
        "study": STUDY_ID,
        "generator_version": GENERATOR_VERSION,
        "evidence_class": "packet-capture",
        "direction": "c2s",
        "decode": counted(decode),
        "captures": captures,
        "event_start_crc": counted(starts),
        "mode_requests": rows_from(
            modes,
            (
                "command",
                "event_name",
                "selector",
                "trigger_is_sender",
                "typed_tail",
                "crc32",
            ),
        ),
        "mode_replies": rows_from(
            replies, ("command", "prior_state", "typed_tail", "reply_frame")
        ),
        "mode_reply_ms": distribution(reply_ms),
        "target_records_before_mode_reply": targets_before_reply,
        "locks": rows_from(locks, ("shape", "mode", "same_frame_next")),
        "lock_second_dword": rows_from(lock_seconds, ("shape", "value")),
        "set_classes": counted(set_classes),
        "engages": engages,
        "engage_summary": engage_summary(engages),
        "clears": rows_from(
            clears, ("after_lock", "same_frame_next", "next_mode", "echo")
        ),
        "clear_to_mode_ms": distribution(clear_mode_ms),
        "talk_starts": rows_from(
            talks,
            (
                "selector",
                "same_frame_prev",
                "prev_is_owner",
                "same_frame_next",
                "next_is_owner",
            ),
        ),
        "same_actor_sets": rows_from(
            decides, ("after_same_frame_lock", "self", "mode", "same_frame_next")
        ),
    }


def engage_summary(engages: list[dict]) -> dict:
    selects = [e["select"] for e in engages if e["select"]]
    return {
        "locks": len(engages),
        "with_select": len(selects),
        "select_same_frame": sum(1 for s in selects if s["frame_gap"] == 0),
        "select_frame_gap": counted(Counter(s["frame_gap"] for s in selects)),
        "select_to_lock_ms_earlier_frame": distribution(
            [s["ms_to_lock"] for s in selects if s["frame_gap"] > 0]
        ),
        "select_frame_shapes": counted(Counter(s["frame_shape"] for s in selects)),
        "d3_before_lock": sum(1 for s in selects if s["d3_before_lock"]),
        "lock_frame_shapes": counted(Counter(e["frame_shape"] for e in engages)),
        "with_d2": sum(1 for e in engages if e["first_d2_ms"] is not None),
        "d2_after_clear": sum(1 for e in engages if e["d2_after_clear"]),
        "with_clear": sum(1 for e in engages if e["clear_ms"] is not None),
        "lock_to_d2_ms": distribution(
            [e["first_d2_ms"] for e in engages if e["first_d2_ms"] is not None]
        ),
        "with_attack": sum(1 for e in engages if e["first_attack_ms"] is not None),
        "first_attack_after_clear": sum(1 for e in engages if e["attack_after_clear"]),
        "with_attack_after_clear": sum(1 for e in engages if e["attacks_after_clear"]),
        "attacks_after_clear": sum(e["attacks_after_clear"] for e in engages),
        "clear_to_attack_ms": distribution(
            [v for e in engages for v in e["clear_to_attack_ms"]]
        ),
        "lock_to_attack_ms": distribution(
            [e["first_attack_ms"] for e in engages if e["first_attack_ms"] is not None]
        ),
        "first_attack_opcode": counted(
            Counter(
                e["first_attack_opcode"] for e in engages if "first_attack_opcode" in e
            )
        ),
        "c2s_before_attack": counted(
            sum(
                (
                    Counter(e["c2s_before_attack"])
                    for e in engages
                    if not e["attack_after_clear"]
                ),
                Counter(),
            )
        ),
        "modes": counted(Counter(e["mode"] for e in engages)),
    }


def cell(value) -> str:
    return "-" if value is None else str(value)


def dist_cells(d: dict) -> str:
    if not d.get("n"):
        return "0 | - | - | -"
    return f"{d['n']} | {d['min']} | {d['median']} | {d['max']}"


def render_verdicts(acc: dict) -> str:
    es = acc["engage_summary"]
    lines = [
        "# Client Battle Engage and Disengage Order",
        "",
        "Every figure below is aggregated from the client-to-server `0x00cc`,",
        "`0x00cd`, and `0x012d` records in the retail captures and joined to the",
        "server records that complete in later capture packets. The products hold",
        "shape classes, counts, packet locators, field-value classes, and",
        "millisecond deltas. They hold no actor ids, absolute timestamps, or raw",
        "payloads.",
        "",
        "## Record shapes",
        "",
        "Offsets count from the first application byte after the 16-byte",
        "game-message header.",
        "",
        "| Record | Offset | Size | Field |",
        "|---|---:|---:|---|",
        "| c2s `0x00cc`, `0x00cd` | 0x00 | 4 | actor, or `0xc0000000` |",
        "| c2s `0x00cc`, `0x00cd` | 0x04 | 4 | second dword |",
        "| c2s `0x012d` | 0x04 | 4 | owner actor |",
        "| c2s `0x012d` | 0x0c | 4 | parameter CRC |",
        "| c2s `0x012d` | 0x11 | 32 | event name |",
        "| c2s `0x012d` | 0x31 | 128 | typed parameter window |",
        "| s2c `0x0139`-`0x013c` | 0x00 | 4 | source actor |",
        "| s2c `0x0139`-`0x013c` | 0x24 | 2 | command id |",
        "| s2c `0x0139`-`0x013c` | 0x28 | 4 | first target actor |",
        "| s2c `0x00d2`, `0x00d3` | 0x00 | 4 | actor, or `0xc0000000` |",
        "",
        "A `0x00cc` shape is `clear` when its actor field is `0xc0000000`.",
        "Otherwise it is `actor, zero` or `actor, nonzero` by its second dword.",
        "A `0x00cd` shape names the actor field as `self` when it equals the",
        "wrapper source, `actor` otherwise, and the second dword as",
        "`0xe0000000`, `same actor`, or `other`.",
        "",
        "## Capture set",
        "",
        "Captures with at least one counted record.",
        "",
        "| Capture | SHA-256 | Counted records |",
        "|---|---|---|",
    ]
    for name, cap in acc["captures"].items():
        counts = ", ".join(f"{k} x{v}" for k, v in cap["counts"].items())
        lines.append(f"| `{name}` | `{cap['sha256']}` | {counts} |")
    crc = acc["event_start_crc"]
    lines += [
        "",
        "## EventStart census",
        "",
        "| Quantity | Messages |",
        "|---|---:|",
        f"| c2s `0x012d` messages | {crc['messages']} |",
        "| CRC field equals zlib CRC-32 of the 128-byte parameter window "
        f"| {crc['crc32_matches_parameter_window']} |",
        "| owner low 16 bits equal attack command 22104 "
        f"| {crc['owner_low16_is_attack_command']} |",
        "",
        "## Mode requests",
        "",
        "c2s `0x012d` messages whose owner is static command 21001 or 21002.",
        "Typed tags are `0x05` nil, `0x00` int, `0x06` actor reference, and",
        "`0x0f` end. An actor reference is named by its relation to the most",
        "recent actor `0x00cc`.",
        "",
        "| Command | Event name | Selector | Trigger is sender | Typed tail | CRC | Messages |",
        "|---:|---|---:|---|---|---|---:|",
    ]
    for row in acc["mode_requests"]:
        lines.append(
            f"| {row['command']} | `{row['event_name']}` | {row['selector']} "
            f"| {row['trigger_is_sender']} | {row['typed_tail']} | `{row['crc32']}` "
            f"| {row['count']} |"
        )
    lines += [
        "",
        "The reply frame is the s2c frame holding the first `commandForced`",
        "`0x0131` from the requester after the request. It lists that frame's",
        "requester records in subevent order. Prior state is the first byte of",
        "the last s2c `0x0134` from the requester before the request.",
        "",
        "| Command | Prior state | Typed tail | Reply frame | Requests |",
        "|---:|---|---|---|---:|",
    ]
    for row in acc["mode_replies"]:
        lines.append(
            f"| {row['command']} | {row['prior_state']} | {row['typed_tail']} "
            f"| {row['reply_frame']} | {row['count']} |"
        )
    lines += [
        "",
        "| Quantity | n | min | median | max |",
        "|---|---:|---:|---:|---:|",
        f"| Request to reply, ms | {dist_cells(acc['mode_reply_ms'])} |",
        "",
        "c2s `0x00cc` or `0x00cd` records completing between a request and its",
        f"reply: {acc['target_records_before_mode_reply']}.",
        "",
        "## Lock records",
        "",
        "Mode is the most recent mode request in client stream order, or `none`.",
        "The next record is the following c2s record in the same frame.",
        "",
        "| Shape | Mode | Same-frame next record | Records |",
        "|---|---|---|---:|",
    ]
    for row in acc["locks"]:
        lines.append(
            f"| {row['shape']} | {row['mode']} | {row['same_frame_next']} | {row['count']} |"
        )
    lines += [
        "",
        "Second dword values. A value equal to an actor id seen in the same",
        "capture would print as `actor id`.",
        "",
        "| Shape | Value | Records |",
        "|---|---|---:|",
    ]
    for row in acc["lock_second_dword"]:
        lines.append(f"| {row['shape']} | `{row['value']}` | {row['count']} |")
    lines += [
        "",
        "## Set records",
        "",
        "| Shape | Records |",
        "|---|---:|",
    ]
    for shape, count in acc["set_classes"].items():
        lines.append(f"| {shape} | {count} |")
    lines += [
        "",
        "## Engage order",
        "",
        "One row per `actor, nonzero` lock. The select is the nearest earlier",
        "c2s `0x00cd` with the same actor and `0xe0000000`, searched back to the",
        "previous `0x00cc` of any shape. Frame shapes omit `0x00ca`. The search",
        "window for the server records runs from the lock to the next `actor,",
        "zero` or `actor, nonzero` lock. A clear inside the window does not end",
        "it. Clear is the first clear lock in the window. Attack is the first s2c",
        "result from the sender with command 22104 and the lock actor as first",
        "target. A trailing `*` marks a record that completes after the clear.",
        "Deltas are milliseconds between completing capture packets.",
        "",
        "| Capture | Select frame / packet | Lock frame / packet | Frame gap "
        "| Select to lock | Lock to `0x00d2` | Lock to clear | Lock to attack "
        "| Lock frame shape |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for e in acc["engages"]:
        s = e["select"]
        sel = "-" if s is None else f"{s['c2s_frame']} / {s['packet']}"
        gap = "-" if s is None else s["frame_gap"]
        to_lock = "-" if s is None else s["ms_to_lock"]
        d2 = cell(e["first_d2_ms"]) + ("*" if e["d2_after_clear"] else "")
        hit = cell(e["first_attack_ms"]) + ("*" if e["attack_after_clear"] else "")
        lines.append(
            f"| `{e['capture']}` | {sel} | {e['c2s_frame']} / {e['packet']} | {gap} "
            f"| {to_lock} | {d2} | {cell(e['clear_ms'])} | {hit} "
            f"| {e['frame_shape']} |"
        )
    lines += [
        "",
        "| Quantity | Value |",
        "|---|---:|",
        f"| `actor, nonzero` locks | {es['locks']} |",
        f"| with a select | {es['with_select']} |",
        f"| select in the lock frame | {es['select_same_frame']} |",
        f"| `0x00d3` for the actor completes before the lock | {es['d3_before_lock']} |",
        f"| with a clear before the next actor lock | {es['with_clear']} |",
        f"| with a later `0x00d2` for the actor | {es['with_d2']} |",
        f"| first `0x00d2` completes after the clear | {es['d2_after_clear']} |",
        f"| with a later attack result | {es['with_attack']} |",
        f"| first attack result completes after the clear "
        f"| {es['first_attack_after_clear']} |",
        f"| with an attack result after the clear | {es['with_attack_after_clear']} |",
        f"| attack results after the clear | {es['attacks_after_clear']} |",
        *[
            f"| first attack result on `{opcode}` | {count} |"
            for opcode, count in es["first_attack_opcode"].items()
        ],
        "",
        "| Interval, ms | n | min | median | max |",
        "|---|---:|---:|---:|---:|",
        f"| select to lock, select in an earlier frame | "
        f"{dist_cells(es['select_to_lock_ms_earlier_frame'])} |",
        f"| lock to first `0x00d2` | {dist_cells(es['lock_to_d2_ms'])} |",
        f"| lock to first attack | {dist_cells(es['lock_to_attack_ms'])} |",
        f"| clear to each attack result after it | "
        f"{dist_cells(es['clear_to_attack_ms'])} |",
        "",
        "| Select frame shape | Selects |",
        "|---|---:|",
    ]
    for shape, count in es["select_frame_shapes"].items():
        lines.append(f"| {shape} | {count} |")
    lines += ["", "| Lock frame shape | Locks |", "|---|---:|"]
    for shape, count in es["lock_frame_shapes"].items():
        lines.append(f"| {shape} | {count} |")
    lines += [
        "",
        "c2s records completing after the lock frame and before the first attack,",
        "for locks whose first attack completes before any clear.",
        "",
        "| Record | Records |",
        "|---|---:|",
    ]
    for record, count in es["c2s_before_attack"].items():
        lines.append(f"| {record} | {count} |")
    lines += [
        "",
        "## Clear records",
        "",
        "One row group per `clear` lock. After lock is the shape of the most",
        "recent actor lock. Next mode is the first mode request before the next",
        "actor lock. Echo names the first s2c `0x00d2` and `0x00d3` for",
        "`0xc0000000` after the clear.",
        "",
        "| After lock | Same-frame next record | Next mode | Echo | Records |",
        "|---|---|---|---|---:|",
    ]
    for row in acc["clears"]:
        lines.append(
            f"| {row['after_lock']} | {row['same_frame_next']} | {row['next_mode']} "
            f"| {row['echo']} | {row['count']} |"
        )
    lines += [
        "",
        "| Interval, ms | n | min | median | max |",
        "|---|---:|---:|---:|---:|",
        "| clear after `actor, nonzero` to next mode request | "
        f"{dist_cells(acc['clear_to_mode_ms'])} |",
        "",
        "## Talk starts",
        "",
        "Same-frame neighbors of each `talkDefault` c2s `0x012d`. Owner columns",
        "say whether the neighbor's actor field equals the EventStart owner.",
        "",
        "| Selector | Previous record | Previous is owner | Next record | Next is owner "
        "| Messages |",
        "|---:|---|---|---|---|---:|",
    ]
    for row in acc["talk_starts"]:
        lines.append(
            f"| {row['selector']} | {row['same_frame_prev']} | {row['prev_is_owner']} "
            f"| {row['same_frame_next']} | {row['next_is_owner']} | {row['count']} |"
        )
    lines += [
        "",
        "## Same-actor set records",
        "",
        "Every c2s `0x00cd` whose second dword equals its actor field.",
        "",
        "| After same-frame lock | Self | Mode | Same-frame next record | Records |",
        "|---|---|---|---|---:|",
    ]
    for row in acc["same_actor_sets"]:
        lines.append(
            f"| {row['after_same_frame_lock']} | {row['self']} | {row['mode']} "
            f"| {row['same_frame_next']} | {row['count']} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_products(acc: dict) -> dict[str, bytes]:
    return {
        "accounting.json": (json.dumps(acc, indent=2, sort_keys=True) + "\n").encode(
            "ascii"
        ),
        "verdicts.md": render_verdicts(acc).encode("ascii"),
    }


def build_outputs() -> dict[str, bytes]:
    return render_products(build_accounting())


def validate_public_shape() -> int:
    try:
        acc_path, md_path = OUT / "accounting.json", OUT / "verdicts.md"
        acc = json.loads(acc_path.read_text(encoding="ascii"))
        if acc.get("study") != STUDY_ID:
            raise ValueError("study id changed")
        if acc_path.read_bytes() != render_products(acc)["accounting.json"]:
            raise ValueError("accounting.json is not canonically formatted")
        if md_path.read_bytes() != render_verdicts(acc).encode("ascii"):
            raise ValueError("verdicts.md differs from accounting.json")
        members = {m["file"]: m for m in load_manifest_members()}
        for name, cap in acc["captures"].items():
            if cap["sha256"] != members[name]["sha256"]:
                raise ValueError(f"{name}: source hash differs from manifest")
        lock_total = sum(r["count"] for r in acc["locks"])
        if sum(r["count"] for r in acc["lock_second_dword"]) != lock_total:
            raise ValueError("lock second-dword counts do not sum")
        listed = sum(
            v
            for cap in acc["captures"].values()
            for k, v in cap["counts"].items()
            if k.startswith("0x00cc ")
        )
        if listed != lock_total:
            raise ValueError("capture lock counts do not sum")
        nonzero = sum(
            r["count"] for r in acc["locks"] if r["shape"] == "actor, nonzero"
        )
        if nonzero != len(acc["engages"]) or nonzero != acc["engage_summary"]["locks"]:
            raise ValueError("engage rows differ from the nonzero lock count")
        clear = sum(r["count"] for r in acc["locks"] if r["shape"] == "clear")
        if clear != sum(r["count"] for r in acc["clears"]):
            raise ValueError("clear rows differ from the clear lock count")
        if sum(r["count"] for r in acc["mode_requests"]) != sum(
            r["count"] for r in acc["mode_replies"]
        ):
            raise ValueError("mode request and reply counts differ")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"c2s battle engage order: public shape invalid: {exc}", file=sys.stderr)
        return 1
    print("verified c2s battle engage order public shape")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare, write nothing")
    parser.add_argument(
        "--public-shape",
        action="store_true",
        help="validate committed products without capture inputs",
    )
    args = parser.parse_args()
    if args.public_shape:
        return validate_public_shape()
    products = build_outputs()
    stale = []
    for name, expected in products.items():
        target = OUT / name
        if args.check:
            if not target.is_file() or target.read_bytes() != expected:
                stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)
    if stale:
        print("stale c2s battle engage products: " + ", ".join(stale), file=sys.stderr)
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {len(products)} c2s battle engage order products")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
