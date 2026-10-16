#!/usr/bin/env python3
"""Join retained battle-result rows to actor property-stream state.

Each battle-result row is joined, per capture and actor, to the actor's
nearest-preceding 0x0137 property record for class, level, hpMax, hp, mp,
mpMax and tp. Every joined value carries a tier. The study then evaluates its
recorded combat anchors (hit outcomes, damage bands, TP steps, engage order,
Cure values, actor identities, and mob level/hpMax pairs) against the join.

The default inputs are this repository's retained study tables. Engage order
also reads the restricted pcap corpus; --public-shape reuses the committed
engage-order.csv instead and regenerates every other product.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import statistics
import struct
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR.parent))

from name_gam_hashes import murmur_hash2  # type: ignore  # noqa: E402

STUDY_ID = "battle-result-actor-join"
DEFAULT_OUT = REPO_ROOT / "studies" / STUDY_ID / "derived"
DEFAULT_BATTLE_ROWS = (
    REPO_ROOT
    / "studies"
    / "battle-result-backfit"
    / "derived"
    / "battle-result-rows.csv"
)
DEFAULT_PROPERTY_RECORDS = (
    REPO_ROOT
    / "studies"
    / "property-stream-hash-catalog"
    / "derived"
    / "property-records.csv"
)
PCAP_MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"
PCAP_OBJECTS = Path(
    os.environ.get(
        "XIVL_PCAP_OBJECTS_DIR", REPO_ROOT / "sources" / "pcap-1.23b" / "objects"
    )
)
EXPECTED_BATTLE_ROWS = 622
EXPECTED_PROPERTY_RECORDS = 9307

# Field names resolve by exact MurmurHash2 in
# xivl-client-structs:manifests/gam_hash_names.json; the hashes are recomputed
# here so the join needs no sibling checkout.
FIELD_SPECS = (
    ("class", "charaWork.parameterSave.state_mainSkill[0]", "0x7532ce24"),
    ("level", "charaWork.parameterSave.state_mainSkillLevel", "0x96063588"),
    ("hpMax", "charaWork.parameterSave.hpMax[0]", "0x7bcdfb69"),
    ("hp", "charaWork.parameterSave.hp[0]", "0x4232bcaa"),
    ("mp", "charaWork.parameterSave.mp", "0x13f89710"),
    ("mpMax", "charaWork.parameterSave.mpMax", "0x3c95d5c5"),
    ("tp", "charaWork.parameterTemp.tp", "0x0b99c876"),
)
HATE_TYPE_SPEC = ("hateType", "npcWork.hateType", "0x8e9c05be")
HASH_NAME_SOURCE = {
    "citation": "xivl-client-structs:manifests/gam_hash_names.json",
    "sha256": "4c6626aaec0569e8e857ae4d25ddd186614d8843c50b91904c4ac617283d2ca3",
    "resolved_names": 263,
}
FIELDS = tuple(spec[0] for spec in FIELD_SPECS)
# Slow-changing fields may take a capture-static value; hp, mp and tp may not.
STATIC_FIELDS = ("class", "level", "hpMax", "mpMax")

# Retained player character ids sit below 2**30 and spawned actors above it.
# This is a corpus observation used for selection, not a decoded id-space rule.
PLAYER_ID_LIMIT = 1 << 30

# Command names and tp_cost come from
# xivl-client-data:derived/command_battle_params.csv (name_en, tp_cost).
COMMAND_NAMES = {
    22104: "Attack",
    23003: "Attack",
    23005: "Attack",
    23061: "Rage of the Deep",
    23079: "Hoofkick",
    23091: "Head Butt",
    23092: "Alpine Fury",
    23167: "Head Butt",
    23226: "Trap Jaws",
    27150: "Fast Blade",
    27151: "Flat Blade",
    27152: "Savage Blade",
    27156: "Shield Bash",
    27158: "Phalanx",
    27190: "Heavy Swing",
    27191: "Skull Sunder",
    27193: "Brutal Swing",
    27198: "Fracture",
    27346: "Cure",
}
PLAYER_AUTO = 22104
MOB_AUTOS = (23003, 23005)
MOB_MOVES = (23061, 23079, 23091, 23092, 23167, 23226)  # tp_cost 1000
CURE = 27346

OUTCOME_CLASSES = (
    "normal_damage",
    "critical_damage",
    "block_damage",
    "parry_damage",
    "miss",
)
HIT_CLASSES = OUTCOME_CLASSES[:4]
# Rows the battle-result backfit could not classify do not break a TP window.
UNCLASSED = ("non_fit", "unknown")

TP_WINDOW_FRAMES = 14
ROBUST_RATIO_DROP = Fraction(1, 20)
ABOUT_TOLERANCE = Fraction(1, 100)
ENGAGE_WINDOW_FRAMES = 32
ENGAGE_RUN_GAP_FRAMES = 2
ENGAGE_OPCODES = {0x0187: "0x0187", 0x0195: "0x0195"}
ENGAGE_HATE_VALUES = (2, 3)

PBL = "party_battle_leve.pcapng"
WQU2 = "war_quest_update2.pcapng"
CAA = "combat_autoattack.pcapng"
CSK = "combat_skills.pcapng"
CLASS3_ACTOR = 43722707
CLASS4_ACTOR = 43723073

JOINED_FIELDS = (
    "row_index",
    "capture",
    "lane_index",
    "frame_index",
    "subevent_index",
    "opcode",
    "source_actor_id",
    "target_actor_id",
    "command_id",
    "message_class",
    "numeric_value",
) + tuple(
    f"{role}_{field}{suffix}"
    for role in ("src", "tgt")
    for field in FIELDS
    for suffix in ("", "_tier", "_record")
)
TP_FIELDS = (
    "capture",
    "lane_index",
    "actor_id",
    "actor_kind",
    "record_index",
    "frame_index",
    "subevent_index",
    "tp",
    "previous_tp",
    "delta",
    "window_rows",
    "clean_kind",
    "row_index",
    "command_id",
    "message_class",
    "numeric_value",
    "row_frame_gap",
    "k_low",
    "k_high",
    "robust_kept",
)
ENGAGE_FIELDS = (
    "engagement",
    "capture",
    "lane_index",
    "frame_index",
    "subevent_index",
    "event",
    "actor_id",
    "destination_actor_id",
    "hate_type",
    "record_index",
)
ANCHOR_FIELDS = (
    "anchor_id",
    "group",
    "anchor",
    "selection",
    "n",
    "counts",
    "band_low",
    "band_high",
    "k_low",
    "k_high",
    "computed",
    "tier_mix",
    "verdict",
)
MOB_TABLE_FIELDS = (
    "level",
    "hpMax",
    "classes",
    "capture",
    "actor_id",
    "level_record_index",
    "hpMax_record_index",
)

# Comparison values supplied by a consumer project, which attributes them to
# the 1.19-1.22 era. This repository holds no source for them; they are kept
# beside the corpus values as an observation of a different version.
EARLIER_VERSION_MOB_HP = {8: "141", 9: "157", 11: "233", 17: "406"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_field_hashes() -> None:
    for _, name, expected in FIELD_SPECS + (HATE_TYPE_SPEC,):
        actual = f"0x{murmur_hash2(name):08x}"
        if actual != expected:
            raise ValueError(f"{name} hashes to {actual}, expected {expected}")


def verify_hash_names(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    resolved = {entry["idHex"]: entry["names"] for entry in data["resolved"]}
    for _, name, expected in FIELD_SPECS + (HATE_TYPE_SPEC,):
        if name not in resolved.get(expected, []):
            raise ValueError(f"{path}: {expected} does not resolve to {name}")
    return sha256_file(path)


def fmt_fraction(value: Fraction | None) -> str:
    return "" if value is None else f"{float(value):.6f}"


def fmt4(value: Fraction) -> str:
    return f"{float(value):.4f}"


# ---------------------------------------------------------------------------
# Input loading


def load_battle_rows(path: Path) -> list[dict]:
    with path.open(encoding="ascii", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != EXPECTED_BATTLE_ROWS:
        raise ValueError(
            f"expected {EXPECTED_BATTLE_ROWS} battle rows, got {len(rows)}"
        )
    out = []
    for row in rows:
        parsed = dict(row)
        for key in (
            "row_index",
            "lane_index",
            "frame_index",
            "subevent_index",
            "source_actor_id",
            "target_actor_id",
            "command_id",
            "numeric_value",
        ):
            parsed[key] = int(row[key])
        parsed["key"] = (parsed["frame_index"], parsed["subevent_index"])
        out.append(parsed)
    return out


def load_property_records(path: Path) -> list[dict]:
    with path.open(encoding="ascii", newline="") as handle:
        records = list(csv.DictReader(handle))
    if len(records) != EXPECTED_PROPERTY_RECORDS:
        raise ValueError(
            f"expected {EXPECTED_PROPERTY_RECORDS} property records, got {len(records)}"
        )
    by_hash = {spec[2]: spec[0] for spec in FIELD_SPECS + (HATE_TYPE_SPEC,)}
    out = []
    for record in records:
        field = by_hash.get(record["property_hash"])
        if field is None:
            continue
        out.append(
            {
                "field": field,
                "record_index": int(record["record_index"]),
                "capture": record["capture"],
                "lane_index": int(record["lane_index"]),
                "frame_index": int(record["frame_index"]),
                "subevent_index": int(record["subevent_index"]),
                "actor": int(record["source_actor_id"]),
                "value": int(record["value_u_le"]),
                "key": (int(record["frame_index"]), int(record["subevent_index"])),
            }
        )
    return out


def is_player(actor_id: int) -> bool:
    return 0 < actor_id < PLAYER_ID_LIMIT


# ---------------------------------------------------------------------------
# Join


class Join:
    def __init__(self, rows: list[dict], records: list[dict]):
        self.rows = rows
        self.timeline: dict[tuple, list[tuple]] = defaultdict(list)
        self.hate: list[dict] = []
        for record in records:
            if record["field"] == "hateType":
                self.hate.append(record)
                continue
            key = (
                record["capture"],
                record["lane_index"],
                record["actor"],
                record["field"],
            )
            self.timeline[key].append(
                (record["key"], record["record_index"], record["value"])
            )
        for series in self.timeline.values():
            series.sort()
        self.bridges = self._build_bridges()
        self.joined = [self._join_row(row) for row in rows]

    def series(self, capture: str, lane: int, actor: int, field: str) -> list[tuple]:
        return self.timeline.get((capture, lane, actor, field), [])

    def _static(self, capture: str, lane: int, actor: int, field: str):
        series = self.series(capture, lane, actor, field)
        values = {value for _, _, value in series}
        if len(values) == 1:
            return series[0]
        return None

    def _build_bridges(self) -> dict[tuple, dict]:
        """Bridge an actor's identity tuple across captures by stat ceilings.

        A capture with no class or level record for an actor takes the single
        complete (class, level, hpMax, mpMax) tuple seen for the same actor id
        in another capture whose hpMax and mpMax equal the actor's in-capture
        hp and mp maxima.
        """
        tuples: dict[int, dict[tuple, list[str]]] = defaultdict(
            lambda: defaultdict(list)
        )
        actors_by_capture: dict[tuple, set] = defaultdict(set)
        for capture, lane, actor, _field in self.timeline:
            actors_by_capture[(capture, lane)].add(actor)
        for (capture, lane), actors in actors_by_capture.items():
            for actor in actors:
                found = []
                for field in STATIC_FIELDS:
                    static = self._static(capture, lane, actor, field)
                    if static is None:
                        break
                    found.append(static[2])
                else:
                    tuples[actor][tuple(found)].append(capture)
        bridges = {}
        for (capture, lane), actors in sorted(actors_by_capture.items()):
            for actor in sorted(actors):
                if any(
                    self.series(capture, lane, actor, f) for f in ("class", "level")
                ):
                    continue
                hp = [v for _, _, v in self.series(capture, lane, actor, "hp")]
                mp = [v for _, _, v in self.series(capture, lane, actor, "mp")]
                if not hp or not mp:
                    continue
                matches = {
                    candidate: sorted(set(sources))
                    for candidate, sources in tuples[actor].items()
                    if capture not in sources
                    and candidate[2] == max(hp)
                    and candidate[3] == max(mp)
                }
                if len(matches) == 1:
                    ((candidate, sources),) = matches.items()
                    bridges[(capture, lane, actor)] = {
                        "values": dict(zip(STATIC_FIELDS, candidate)),
                        "source_captures": sources,
                        "hp_max_observed": max(hp),
                        "mp_max_observed": max(mp),
                    }
        return bridges

    def lookup(self, capture: str, lane: int, actor: int, field: str, key: tuple):
        """Return (value, tier, record_index) for one actor field at a row key."""
        if actor == 0:
            return None, "none", None
        series = self.series(capture, lane, actor, field)
        previous = None
        for entry in series:
            if entry[0] < key:
                previous = entry
            else:
                break
        if previous is not None:
            return previous[2], "T0", previous[1]
        if field in STATIC_FIELDS:
            static = self._static(capture, lane, actor, field)
            if static is not None:
                return static[2], "T1", static[1]
            bridge = self.bridges.get((capture, lane, actor))
            if bridge is not None and not series:
                return bridge["values"][field], "T2", None
        return None, "none", None

    def _join_row(self, row: dict) -> dict:
        joined = {}
        for role, actor_key in (("src", "source_actor_id"), ("tgt", "target_actor_id")):
            for field in FIELDS:
                joined[(role, field)] = self.lookup(
                    row["capture"], row["lane_index"], row[actor_key], field, row["key"]
                )
        return joined


def render_joined(join: Join) -> list[dict]:
    out = []
    for row, joined in zip(join.rows, join.joined):
        rendered = {
            name: row[name]
            for name in JOINED_FIELDS
            if not name.startswith(("src_", "tgt_"))
        }
        for role in ("src", "tgt"):
            for field in FIELDS:
                value, tier, record = joined[(role, field)]
                rendered[f"{role}_{field}"] = "" if value is None else value
                rendered[f"{role}_{field}_tier"] = tier
                rendered[f"{role}_{field}_record"] = "" if record is None else record
        out.append(rendered)
    return out


# ---------------------------------------------------------------------------
# TP series


def tp_events(join: Join) -> list[dict]:
    """Classify each consecutive tp-record window per actor."""
    rows_by_actor: dict[tuple, list[dict]] = defaultdict(list)
    for row in join.rows:
        for actor in {row["source_actor_id"], row["target_actor_id"]}:
            rows_by_actor[(row["capture"], row["lane_index"], actor)].append(row)
    events = []
    tp_keys = sorted(k for k in join.timeline if k[3] == "tp")
    for capture, lane, actor, _ in tp_keys:
        series = join.series(capture, lane, actor, "tp")
        actor_rows = sorted(
            rows_by_actor.get((capture, lane, actor), []),
            key=lambda r: (r["key"], r["row_index"]),
        )
        position = 0
        previous = None
        for key, record_index, value in series:
            window = []
            while position < len(actor_rows) and actor_rows[position]["key"] < key:
                if previous is not None:
                    window.append(actor_rows[position])
                position += 1
            event = {
                "capture": capture,
                "lane_index": lane,
                "actor_id": actor,
                "actor_kind": "player" if is_player(actor) else "spawned",
                "record_index": record_index,
                "frame_index": key[0],
                "subevent_index": key[1],
                "tp": value,
                "previous_tp": "" if previous is None else previous,
                "delta": "" if previous is None else value - previous,
                "window_rows": len(window) if previous is not None else "",
                "clean_kind": "",
                "row": None,
                "row_frame_gap": "",
            }
            if previous is not None and window:
                _classify_window(event, actor, window, key)
            events.append(event)
            previous = value
    return events


def _classify_window(event: dict, actor: int, window: list[dict], key: tuple) -> None:
    hits = [
        r
        for r in window
        if r["target_actor_id"] == actor
        and r["message_class"] in HIT_CLASSES
        and r["numeric_value"] > 0
    ]
    if len(hits) == 1:
        hit = hits[0]
        others = [
            r
            for r in window
            if r["key"] != hit["key"] and r["message_class"] not in UNCLASSED
        ]
        same_key_own = [
            r
            for r in window
            if r["key"] == hit["key"] and r is not hit and r["source_actor_id"] == actor
        ]
        gap = key[0] - hit["frame_index"]
        if (
            not others
            and not same_key_own
            and gap <= TP_WINDOW_FRAMES
            and event["delta"] > 0
        ):
            event.update(clean_kind="taken", row=hit, row_frame_gap=gap)
            return
    own = [
        r
        for r in window
        if r["source_actor_id"] == actor
        and r["command_id"] != 0
        and r["message_class"] not in UNCLASSED + ("hp_recovery",)
    ]
    struck = [
        r
        for r in window
        if r["target_actor_id"] == actor
        and r["source_actor_id"] != actor
        and r["message_class"] in HIT_CLASSES
    ]
    if len(own) == 1 and not struck:
        row = own[0]
        gap = key[0] - row["frame_index"]
        others = [
            r
            for r in window
            if r["key"] != row["key"] and r["message_class"] not in UNCLASSED
        ]
        if not others and gap <= TP_WINDOW_FRAMES:
            if row["command_id"] in MOB_AUTOS:
                kind = "dealt-swing"
            elif row["command_id"] in MOB_MOVES:
                kind = "dealt-move"
            else:
                kind = "dealt-other"
            event.update(
                clean_kind=kind,
                row=row,
                row_frame_gap=gap,
                window_start_gap=key[0] - window[0]["frame_index"],
            )


def k_interval(events: list[dict]):
    """Intersect (delta-1)/dmg < k <= delta/dmg after the robust ratio drop."""
    if not events:
        return None, None, [], []
    ratios = [Fraction(e["delta"], e["row"]["numeric_value"]) for e in events]
    median = Fraction(statistics.median(ratios))
    kept, dropped = [], []
    for event, ratio in zip(events, ratios):
        (dropped if abs(ratio - median) > ROBUST_RATIO_DROP else kept).append(event)
    low, high = Fraction(0), None
    for event in kept:
        dmg = event["row"]["numeric_value"]
        low = max(low, Fraction(event["delta"] - 1, dmg))
        bound = Fraction(event["delta"], dmg)
        high = bound if high is None else min(high, bound)
    return low, high, kept, dropped


def taken_intervals(events: list[dict]) -> dict[tuple, tuple]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for event in events:
        if event["clean_kind"] == "taken":
            grouped[(event["capture"], event["lane_index"], event["actor_id"])].append(
                event
            )
    return {key: k_interval(value) for key, value in grouped.items()}


def render_tp(events: list[dict], intervals: dict[tuple, tuple]) -> list[dict]:
    out = []
    for event in events:
        row = event["row"]
        key = (event["capture"], event["lane_index"], event["actor_id"])
        rendered = {name: event.get(name, "") for name in TP_FIELDS}
        rendered.update(
            row_index="" if row is None else row["row_index"],
            command_id="" if row is None else row["command_id"],
            message_class="" if row is None else row["message_class"],
            numeric_value="" if row is None else row["numeric_value"],
            k_low="",
            k_high="",
            robust_kept="",
        )
        if event["clean_kind"] == "taken":
            dmg = row["numeric_value"]
            rendered["k_low"] = fmt_fraction(Fraction(event["delta"] - 1, dmg))
            rendered["k_high"] = fmt_fraction(Fraction(event["delta"], dmg))
            kept = intervals[key][2]
            rendered["robust_kept"] = "yes" if any(e is event for e in kept) else "no"
        out.append(rendered)
    return out


# ---------------------------------------------------------------------------
# Engage order


def engage_captures(join: Join) -> list[str]:
    return sorted({r["capture"] for r in join.hate if r["value"] in ENGAGE_HATE_VALUES})


def walk_engage_opcodes(capture_path: Path) -> list[dict]:
    from extract_observations import (  # type: ignore
        INNER_HEADER_LEN,
        SUB_EVENT_CLASS_ACTOR_WRAPPED,
        SUB_EVENT_HEADER_LEN,
    )
    from extract_streams import (  # type: ignore
        maybe_inflate,
        parse_outer_frames,
        reconstruct_lanes,
    )

    events = []
    for lane_index, lane in enumerate(reconstruct_lanes(capture_path)):
        blob = lane["streams"].get("s2c", b"")
        for frame_index, frame in enumerate(parse_outer_frames(blob)):
            body = maybe_inflate(frame["body"])
            if body is None:
                body = frame["body"]
            offset = 0
            subevent_index = 0
            while offset + SUB_EVENT_HEADER_LEN <= len(body):
                size, event_type = struct.unpack_from("<HH", body, offset)
                if size < SUB_EVENT_HEADER_LEN or offset + size > len(body):
                    break
                if event_type == SUB_EVENT_CLASS_ACTOR_WRAPPED:
                    sub_body = body[offset + SUB_EVENT_HEADER_LEN : offset + size]
                    if len(sub_body) >= INNER_HEADER_LEN:
                        opcode = struct.unpack_from("<H", sub_body, 2)[0]
                        if opcode in ENGAGE_OPCODES:
                            events.append(
                                {
                                    "lane_index": lane_index,
                                    "frame_index": frame_index,
                                    "subevent_index": subevent_index,
                                    "event": ENGAGE_OPCODES[opcode],
                                    "actor_id": struct.unpack_from(
                                        "<I", body, offset + 4
                                    )[0],
                                    "destination_actor_id": struct.unpack_from(
                                        "<I", body, offset + 8
                                    )[0],
                                }
                            )
                offset += size
                subevent_index += 1
    return events


def build_engage_rows(join: Join, pcap_dir: Path) -> list[dict]:
    rows: list[dict] = []
    engagement = 0
    for capture in engage_captures(join):
        wire = walk_engage_opcodes(pcap_dir / capture)
        hate = [
            {
                "lane_index": r["lane_index"],
                "frame_index": r["frame_index"],
                "subevent_index": r["subevent_index"],
                "event": f"hateType={r['value']}",
                "actor_id": r["actor"],
                "destination_actor_id": "",
                "hate_type": r["value"],
                "record_index": r["record_index"],
            }
            for r in join.hate
            if r["capture"] == capture
        ]
        stream = sorted(
            wire + hate,
            key=lambda e: (e["lane_index"], e["frame_index"], e["subevent_index"]),
        )
        runs: list[list[dict]] = []
        for event in stream:
            if event["event"] != "0x0187":
                continue
            if (
                runs
                and runs[-1][-1]["lane_index"] == event["lane_index"]
                and event["frame_index"] - runs[-1][-1]["frame_index"]
                <= ENGAGE_RUN_GAP_FRAMES
            ):
                runs[-1].append(event)
            else:
                runs.append([event])
        for run in runs:
            start = run[0]
            limit = start["frame_index"] + ENGAGE_WINDOW_FRAMES
            starts = [
                e
                for e in stream
                if e["lane_index"] == start["lane_index"]
                and e.get("hate_type") in ENGAGE_HATE_VALUES
                and (e["frame_index"], e["subevent_index"])
                > (start["frame_index"], start["subevent_index"])
                and e["frame_index"] <= limit
            ]
            if not starts:
                continue
            end = starts[-1]
            engagement += 1
            for event in stream:
                position = (
                    event["lane_index"],
                    event["frame_index"],
                    event["subevent_index"],
                )
                if (
                    (start["lane_index"], start["frame_index"], start["subevent_index"])
                    <= position
                    <= (end["lane_index"], end["frame_index"], end["subevent_index"])
                ):
                    rows.append(
                        {
                            "engagement": engagement,
                            "capture": capture,
                            "lane_index": event["lane_index"],
                            "frame_index": event["frame_index"],
                            "subevent_index": event["subevent_index"],
                            "event": event["event"],
                            "actor_id": event["actor_id"],
                            "destination_actor_id": event["destination_actor_id"],
                            "hate_type": event.get("hate_type", ""),
                            "record_index": event.get("record_index", ""),
                        }
                    )
    rendered = [{k: str(v) for k, v in row.items()} for row in rows]
    return rendered


def read_engage_rows(path: Path) -> list[dict]:
    with path.open(encoding="ascii", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != ENGAGE_FIELDS:
            raise ValueError(f"{path}: engage-order header changed")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: no engage rows")
    return rows


def engagements(engage_rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in engage_rows:
        grouped[row["engagement"]].append(row)
    out = []
    for engagement_id in sorted(grouped, key=int):
        events = grouped[engagement_id]
        tokens: list[list] = []
        for event in events:
            if tokens and tokens[-1][0] == event["event"]:
                tokens[-1][1] += 1
            else:
                tokens.append([event["event"], 1])
        out.append(
            {
                "engagement": int(engagement_id),
                "capture": events[0]["capture"],
                "start_frame": int(events[0]["frame_index"]),
                "end_frame": int(events[-1]["frame_index"]),
                "pattern": " > ".join(
                    f"{token} x{count}" if count > 1 else token
                    for token, count in tokens
                ),
                "kinds": [token for token, _ in tokens],
                "count_0187": sum(e["event"] == "0x0187" for e in events),
                "frames_0187": sorted(
                    {int(e["frame_index"]) for e in events if e["event"] == "0x0187"}
                ),
                "frames_0195": sorted(
                    {int(e["frame_index"]) for e in events if e["event"] == "0x0195"}
                ),
                "frames_hate": sorted(
                    (int(e["frame_index"]), int(e["hate_type"]))
                    for e in events
                    if e["hate_type"]
                ),
            }
        )
    return out


# ---------------------------------------------------------------------------
# Anchors


class Anchors:
    def __init__(
        self, join: Join, events: list[dict], intervals: dict, engage_rows: list[dict]
    ):
        self.join = join
        self.events = events
        self.intervals = intervals
        self.engagements = engagements(engage_rows)
        self.rows: list[dict] = []

    # Helpers -----------------------------------------------------------------

    def value(self, index: int, role: str, field: str):
        return self.join.joined[index][(role, field)]

    def select(self, predicate) -> list[int]:
        return [i for i, row in enumerate(self.join.rows) if predicate(i, row)]

    def level_is(self, index: int, role: str, level: int) -> bool:
        return self.value(index, role, "level")[0] == level

    def tier_mix(self, lookups) -> str:
        counts = Counter(tier for tier in lookups)
        return ";".join(f"{tier}={counts[tier]}" for tier in sorted(counts))

    def row_tiers(self, indices, roles=("src", "tgt"), fields=("level",)) -> str:
        return self.tier_mix(
            self.value(i, role, field)[1]
            for i in indices
            for role in roles
            for field in fields
        )

    def add(self, anchor_id, group, anchor, selection, verdict, computed, **extra):
        row = {name: "" for name in ANCHOR_FIELDS}
        row.update(
            anchor_id=anchor_id,
            group=group,
            anchor=anchor,
            selection=selection,
            computed=computed,
            verdict=verdict,
        )
        row.update({k: v for k, v in extra.items() if k in ANCHOR_FIELDS})
        self.rows.append(row)

    def outcome_counts(self, indices) -> Counter:
        return Counter(self.join.rows[i]["message_class"] for i in indices)

    @staticmethod
    def counts_text(counts: Counter) -> str:
        return ";".join(
            f"{name}={counts[name]}"
            for name in OUTCOME_CLASSES + ("hp_recovery",)
            if counts[name]
        )

    # Populations -------------------------------------------------------------

    def pbl_outcomes(
        self,
        source=None,
        target=None,
        commands=None,
        source_level=None,
        target_level=None,
    ):
        def predicate(i, row):
            if row["capture"] != PBL or row["message_class"] not in OUTCOME_CLASSES:
                return False
            if source is not None and row["source_actor_id"] != source:
                return False
            if target is not None and row["target_actor_id"] != target:
                return False
            if commands is not None and row["command_id"] not in commands:
                return False
            if source_level is not None and not self.level_is(i, "src", source_level):
                return False
            if target_level is not None and not self.level_is(i, "tgt", target_level):
                return False
            return True

        return self.select(predicate)

    # Anchor groups -------------------------------------------------------------

    def rate_anchor(
        self,
        anchor_id,
        anchor,
        selection,
        indices,
        outcome,
        expected_hits,
        expected_n,
        extra="",
    ):
        counts = self.outcome_counts(indices)
        hits = sum(counts[name] for name in outcome)
        n = len(indices)
        verdict = (
            "REPRODUCED" if (hits, n) == (expected_hits, expected_n) else "CONFLICT"
        )
        computed = f"{hits}/{n} ({100 * hits / n:.1f} percent){extra}" if n else "0/0"
        self.add(
            anchor_id,
            "hit-outcomes",
            anchor,
            selection,
            verdict,
            computed,
            n=n,
            counts=self.counts_text(counts),
            tier_mix=self.row_tiers(indices),
        )

    def hit_outcomes(self) -> None:
        gla_v30 = self.pbl_outcomes(
            CLASS3_ACTOR, commands=(PLAYER_AUTO,), target_level=30
        )
        mrd_v30 = self.pbl_outcomes(
            CLASS4_ACTOR, commands=(PLAYER_AUTO,), target_level=30
        )
        mob_on_gla = self.pbl_outcomes(
            target=CLASS3_ACTOR, commands=MOB_AUTOS, source_level=30
        )
        mob_on_mrd = self.pbl_outcomes(
            target=CLASS4_ACTOR, commands=MOB_AUTOS, source_level=30
        )
        self.rate_anchor(
            "A01",
            "Miss 4/50 (8.0 percent)",
            "party_battle_leve; source 43722707 command 22104; target level 30",
            gla_v30,
            ("miss",),
            4,
            50,
        )
        self.rate_anchor(
            "A02",
            "Miss 4/37 (10.8 percent)",
            "party_battle_leve; source 43723073 command 22104; target level 30",
            mrd_v30,
            ("miss",),
            4,
            37,
        )
        self.rate_anchor(
            "A03",
            "Miss 3/44 (6.8 percent)",
            "party_battle_leve; commands 23003/23005; source level 30; target 43722707",
            mob_on_gla,
            ("miss",),
            3,
            44,
        )
        zero_blocks = sum(
            1
            for i in mob_on_gla
            if self.join.rows[i]["message_class"] == "block_damage"
            and self.join.rows[i]["numeric_value"] == 0
        )
        blocks = self.outcome_counts(mob_on_gla)["block_damage"]
        self.add(
            "A04",
            "hit-outcomes",
            "Block 13/44 (29.5 percent), four zero-valued",
            "party_battle_leve; commands 23003/23005; source level 30; target 43722707",
            "REPRODUCED"
            if (blocks, len(mob_on_gla), zero_blocks) == (13, 44, 4)
            else "CONFLICT",
            f"{blocks}/{len(mob_on_gla)} ({100 * blocks / len(mob_on_gla):.1f} percent); zero-valued {zero_blocks}",
            n=len(mob_on_gla),
            counts=self.counts_text(self.outcome_counts(mob_on_gla)),
            tier_mix=self.row_tiers(mob_on_gla),
        )
        self.rate_anchor(
            "A05",
            "Parry 2/13 (15.4 percent)",
            "party_battle_leve; commands 23003/23005; source level 30; target 43723073",
            mob_on_mrd,
            ("parry_damage",),
            2,
            13,
        )
        on_class2 = self.select(
            lambda i, r: (
                r["capture"] == WQU2
                and r["target_actor_id"] == CLASS3_ACTOR
                and r["command_id"] in MOB_AUTOS
                and r["message_class"] in OUTCOME_CLASSES
            )
        )
        self.rate_anchor(
            "A06",
            "Parry 2/14 (14.3 percent)",
            "war_quest_update2; commands 23003/23005; target 43722707 (class 2, level 50)",
            on_class2,
            ("parry_damage",),
            2,
            14,
        )
        gla_swings = self.pbl_outcomes(CLASS3_ACTOR, target_level=30)
        counts = self.outcome_counts(gla_swings)
        defended = counts["parry_damage"] + counts["block_damage"]
        self.add(
            "A07",
            "hit-outcomes",
            "Mob parry or block: 0 across 81 swings by 43722707",
            "party_battle_leve; source 43722707, all commands; target level 30",
            "REPRODUCED" if (defended, len(gla_swings)) == (0, 81) else "CONFLICT",
            f"{defended}/{len(gla_swings)} parried or blocked",
            n=len(gla_swings),
            counts=self.counts_text(counts),
            tier_mix=self.row_tiers(gla_swings),
        )
        player_to_mob = self.select(
            lambda i, r: (
                r["message_class"] in OUTCOME_CLASSES
                and is_player(r["source_actor_id"])
                and not is_player(r["target_actor_id"])
            )
        )
        counts = self.outcome_counts(player_to_mob)
        defended = counts["parry_damage"] + counts["block_damage"]
        by_capture = Counter(self.join.rows[i]["capture"] for i in player_to_mob)
        self.add(
            "A08",
            "hit-outcomes",
            "Mob parry or block: 0 across all 201 player-to-mob rows",
            "all captures; player source, spawned-actor target, outcome classes",
            "REPRODUCED" if (defended, len(player_to_mob)) == (0, 201) else "CONFLICT",
            f"{defended}/{len(player_to_mob)} parried or blocked; "
            + "; ".join(
                f"{c.removesuffix('.pcapng')} {n}"
                for c, n in sorted(by_capture.items())
            ),
            n=len(player_to_mob),
            counts=self.counts_text(counts),
            tier_mix=self.row_tiers(player_to_mob),
        )

    def band_anchor(
        self, anchor_id, anchor, selection, indices, normal, dense=None, crits=None
    ):
        def values(cls):
            return sorted(
                self.join.rows[i]["numeric_value"]
                for i in indices
                if self.join.rows[i]["message_class"] == cls
            )

        normals, criticals = values("normal_damage"), values("critical_damage")
        observed = (min(normals), max(normals)) if normals else (None, None)
        ok = observed == normal
        parts = [f"normal {observed[0]}-{observed[1]} (n={len(normals)})"]
        if dense is not None:
            inside = sum(dense[0] <= v <= dense[1] for v in normals)
            parts.append(f"inside {dense[0]}-{dense[1]}: {inside}/{len(normals)}")
            ok = ok and normal[0] <= dense[0] <= dense[1] <= normal[1]
        if crits is not None:
            parts.append("crits " + ",".join(str(v) for v in criticals))
            if isinstance(crits, tuple):
                ok = (
                    ok and bool(criticals) and (min(criticals), max(criticals)) == crits
                )
            else:
                ok = ok and sorted(criticals) == sorted(crits)
        self.add(
            anchor_id,
            "damage-bands",
            anchor,
            selection,
            "REPRODUCED" if ok else "CONFLICT",
            "; ".join(parts),
            n=len(indices),
            counts=self.counts_text(self.outcome_counts(indices)),
            band_low=observed[0],
            band_high=observed[1],
            tier_mix=self.row_tiers(indices),
        )

    def damage_bands(self) -> None:
        def gla(cmd):
            return self.pbl_outcomes(CLASS3_ACTOR, commands=(cmd,), target_level=30)

        def mrd(cmd):
            return self.pbl_outcomes(CLASS4_ACTOR, commands=(cmd,), target_level=30)

        self.band_anchor(
            "A09",
            "GLA auto: normal 18-23 (dense 18-22), crits 25 and 22",
            "party_battle_leve; source 43722707 command 22104; target level 30",
            gla(PLAYER_AUTO),
            (18, 23),
            (18, 22),
            [22, 25],
        )
        self.band_anchor(
            "A10",
            "MRD auto: normal 42-53 (dense 44-51), crit 57",
            "party_battle_leve; source 43723073 command 22104; target level 30",
            mrd(PLAYER_AUTO),
            (42, 53),
            (44, 51),
            [57],
        )
        self.band_anchor(
            "A11",
            "Lv30 mob autos on the GLA: normal 32-79 (dense 56-63), crits 85-94",
            "party_battle_leve; commands 23003/23005; source level 30; target 43722707",
            self.pbl_outcomes(target=CLASS3_ACTOR, commands=MOB_AUTOS, source_level=30),
            (32, 79),
            (56, 63),
            (85, 94),
        )
        for anchor_id, actor, command, band in (
            ("A12", CLASS3_ACTOR, 27150, (56, 65)),
            ("A13", CLASS3_ACTOR, 27152, (64, 66)),
            ("A14", CLASS3_ACTOR, 27156, (49, 55)),
            ("A15", CLASS3_ACTOR, 27158, (48, 57)),
            ("A16", CLASS4_ACTOR, 27190, (77, 106)),
            ("A17", CLASS4_ACTOR, 27191, (87, 102)),
            ("A18", CLASS4_ACTOR, 27193, (81, 83)),
            ("A19", CLASS4_ACTOR, 27198, (68, 85)),
        ):
            name = COMMAND_NAMES[command]
            indices = (gla if actor == CLASS3_ACTOR else mrd)(command)
            self.band_anchor(
                anchor_id,
                f"{name} {band[0]}-{band[1]}",
                f"party_battle_leve; source {actor} command {command}; target level 30",
                indices,
                band,
            )

    def tp_anchors(self) -> None:
        spawned = [e for e in self.events if e["actor_kind"] == "spawned"]
        swings = [
            e
            for e in spawned
            if e["clean_kind"] == "dealt-swing"
            and e["row"]["message_class"] in HIT_CLASSES
        ]
        plus300 = [e for e in swings if e["delta"] == 300]
        capped = [e for e in swings if e["delta"] != 300 and e["tp"] == 3000]
        other = len(swings) - len(plus300) - len(capped)
        # The anchor's count measured the 14-frame gap from the window's first
        # row; this study measures it from the swing row and reports both.
        narrow = [e for e in swings if e["window_start_gap"] <= TP_WINDOW_FRAMES]
        narrow300 = [e for e in narrow if e["delta"] == 300]
        added = [e for e in swings if e not in narrow]
        self.add(
            "A20",
            "tp",
            "Mob TP +300 on 38 of 39 isolated landed swings, one capped at 3000",
            "spawned actors; one own 23003/23005 landed row per tp window; next tp record within 14 frames of the row",
            "REPRODUCED"
            if (len(narrow300), len(narrow), len(capped), other) == (38, 39, 1, 0)
            else "CONFLICT",
            f"+300 on {len(plus300)}/{len(swings)}; capped at 3000: {len(capped)}"
            + "".join(f" ({e['previous_tp']}->{e['tp']})" for e in capped)
            + (f"; other steps {other}" if other else "")
            + f"; gap from the window's first row: +300 on {len(narrow300)}/{len(narrow)}"
            + (
                "; additional windows "
                + ",".join(
                    f"{e['capture'].removesuffix('.pcapng')} row {e['row']['row_index']}"
                    for e in added
                )
                if added
                else ""
            ),
            n=len(swings),
            counts=";".join(
                f"{k}={v}"
                for k, v in sorted(Counter(e["delta"] for e in swings).items())
            ),
            tier_mix="T0=" + str(len(swings)),
        )
        moves = [e for e in spawned if e["clean_kind"] == "dealt-move"]
        minus = [e for e in moves if e["delta"] == -1000]
        self.add(
            "A21",
            "tp",
            "Mob TP -1000 on 5 of 5 isolated moves",
            "spawned actors; one own tp_cost-1000 move row per tp window; next tp record within 14 frames",
            "REPRODUCED" if (len(minus), len(moves)) == (5, 5) else "CONFLICT",
            f"-1000 on {len(minus)}/{len(moves)}; commands "
            + ",".join(str(e["row"]["command_id"]) for e in moves),
            n=len(moves),
            counts=";".join(
                f"{k}={v}"
                for k, v in sorted(Counter(e["delta"] for e in moves).items())
            ),
            tier_mix="T0=" + str(len(moves)),
        )
        for anchor_id, capture, actor, label, expected, level_note in (
            ("A22", PBL, CLASS4_ACTOR, "Lv26", ("0.8235", "0.8305"), None),
            ("A23", PBL, CLASS3_ACTOR, "Lv27", ("0.7759", "0.7765"), None),
            ("A24", WQU2, CLASS4_ACTOR, "Lv30", ("0.6360", "0.6381"), "T3"),
            ("A25", WQU2, CLASS3_ACTOR, "Lv50", ("0.1744", "0.1818"), None),
        ):
            low, high, kept, dropped = self.intervals.get(
                (capture, 0, actor), (None, None, [], [])
            )
            level = self.actor_level(capture, actor)
            if level[0] is None:
                level = (None, level_note or "none")
            level_text = (
                f"level {level[0]} ({level[1]})"
                if level[0] is not None
                else f"level unresolved ({level[1]})"
            )
            computed = (
                f"({fmt4(low)}, {fmt4(high)}] over {len(kept)} clean hits"
                + (
                    "; dropped "
                    + ",".join(
                        f"{e['row']['numeric_value']}->{e['delta']}" for e in dropped
                    )
                    if dropped
                    else ""
                )
                + f"; {level_text}"
                if low is not None and high is not None
                else ("all clean hits dropped" if dropped else "no clean hits")
            )
            ok = (
                low is not None
                and high is not None
                and low < high
                and (fmt4(low), fmt4(high)) == expected
            )
            self.add(
                anchor_id,
                "tp",
                f"Player TP-taken k {label} ({expected[0]}, {expected[1]}]"
                + (" with level at T3" if level_note else ""),
                f"{capture.removesuffix('.pcapng')}; actor {actor}; tp-taken clean windows",
                "REPRODUCED" if ok else "CONFLICT",
                computed,
                n=len(kept) + len(dropped),
                k_low=fmt_fraction(low),
                k_high=fmt_fraction(high),
                tier_mix=f"tp T0={len(kept) + len(dropped)};level {level[1]}=1",
            )
        for anchor_id, actors, about in (
            ("A26", ((PBL, 1158679893), (PBL, 1158679890)), "3.13"),
            ("A27", ((PBL, 1158679894), (PBL, 1158679895)), "1.91"),
            ("A28", ((PBL, 1158679897), (PBL, 1158679898)), "1.71"),
            ("A29", ((PBL, 1158679843),), "2.49"),
            ("A30", ((CAA, 1154495952), (CSK, 1154495957)), "3.71"),
        ):
            target = Fraction(about)
            parts, ok, n, lows, highs, levels = [], True, 0, [], [], []
            for capture, actor in actors:
                low, high, kept, dropped = self.intervals.get(
                    (capture, 0, actor), (None, None, [], [])
                )
                n += len(kept) + len(dropped)
                level = self.actor_level(capture, actor)
                levels.append(level[1])
                if low is None or high is None or not low < high:
                    ok = False
                    parts.append(f"{actor} empty")
                    continue
                ok = (
                    ok
                    and low < target + ABOUT_TOLERANCE
                    and high >= target - ABOUT_TOLERANCE
                )
                lows.append(low)
                highs.append(high)
                parts.append(
                    f"{actor} ({fmt4(low)}, {fmt4(high)}] n={len(kept)}"
                    + (f" dropped {len(dropped)}" if dropped else "")
                    + (f" level {level[0]}" if level[0] is not None else "")
                )
            self.add(
                anchor_id,
                "tp",
                "Mob k about " + about + ": " + ", ".join(str(a) for _, a in actors),
                "tp-taken clean windows; robust ratio drop 0.05; about means within 0.01",
                "REPRODUCED" if ok else "CONFLICT",
                "; ".join(parts),
                n=n,
                k_low=fmt_fraction(min(lows)) if lows else "",
                k_high=fmt_fraction(max(highs)) if highs else "",
                tier_mix=f"tp T0={n};level " + ",".join(levels),
            )

    def actor_level(self, capture: str, actor: int):
        value, tier, _ = self.join.lookup(capture, 0, actor, "level", (10**9, 0))
        return value, tier

    def engage_anchors(self) -> None:
        def first(capture):
            return next(e for e in self.engagements if e["capture"] == capture)

        for anchor_id, capture, frames in (
            ("A31", CAA, ([19], [26, 27], [(30, 3)])),
            ("A32", CSK, None),
        ):
            engagement = first(capture)
            ok = (
                engagement["kinds"] == ["0x0187", "0x0195", "hateType=3"]
                and engagement["count_0187"] == 2
            )
            if frames is not None:
                ok = (
                    ok
                    and (
                        engagement["frames_0187"],
                        engagement["frames_0195"],
                        engagement["frames_hate"],
                    )
                    == frames
                )
            self.add(
                anchor_id,
                "engage-order",
                f"Order 0x0187 twice, then 0x0195, then hateType 3 in {capture.removesuffix('.pcapng')}"
                + (" (frames 19, 26-27, 30)" if frames else ""),
                f"{capture.removesuffix('.pcapng')}; first 0x0187 run followed by hateType 2 or 3 within {ENGAGE_WINDOW_FRAMES} frames",
                "REPRODUCED" if ok else "CONFLICT",
                f"{engagement['pattern']}; 0x0187 frames {engagement['frames_0187']}, 0x0195 frames {engagement['frames_0195']}, hateType {engagement['frames_hate']}",
                n=1,
                tier_mix="wire="
                + str(engagement["count_0187"] + len(engagement["frames_0195"]))
                + ";T0="
                + str(len(engagement["frames_hate"])),
            )
        pbl = [e for e in self.engagements if e["capture"] == PBL]
        starts = [e["start_frame"] for e in pbl]
        with_two = [e for e in pbl if any(value == 2 for _, value in e["frames_hate"])]
        expected = [373, 1364, 2090, 2291]
        ok = all(frame in starts for frame in expected) and [
            e["start_frame"] for e in with_two
        ] == [2090]
        extra = [frame for frame in starts if frame not in expected]
        self.add(
            "A33",
            "engage-order",
            "party_battle_leve engagements at frames 373, 1364, 2090 and 2291, intermediate hateType 2 at 2090",
            f"party_battle_leve; every 0x0187 run followed by hateType 2 or 3 within {ENGAGE_WINDOW_FRAMES} frames",
            "REPRODUCED" if ok else "CONFLICT",
            "starts "
            + ",".join(str(f) for f in starts)
            + "; hateType 2 in engagement at "
            + ",".join(
                f"{e['start_frame']} (frame {[f for f, v in e['frames_hate'] if v == 2][0]})"
                for e in with_two
            )
            + (
                f"; additional engagement not in the anchor at {','.join(str(f) for f in extra)}"
                if extra
                else ""
            ),
            n=len(pbl),
            tier_mix="wire+T0",
        )

    def identity_anchors(self) -> None:
        cures = self.select(
            lambda i, r: r["command_id"] == CURE and r["message_class"] == "hp_recovery"
        )
        observed = sorted(
            (
                self.join.rows[i]["numeric_value"],
                self.join.rows[i]["target_actor_id"],
                self.join.rows[i]["source_actor_id"],
            )
            for i in cures
        )
        expected = sorted(
            [
                (151, CLASS3_ACTOR, CLASS3_ACTOR),
                (152, CLASS3_ACTOR, CLASS3_ACTOR),
                (166, CLASS4_ACTOR, CLASS3_ACTOR),
            ]
        )
        caster_levels = {
            (self.value(i, "src", "class")[0], self.value(i, "src", "level")[0])
            for i in cures
        }
        self.add(
            "A34",
            "cure-identities",
            "Cure 151 and 152 on self and 166 on 43723073, cast by the Lv27 actor 43722707",
            "all captures; command 27346 rows classed hp_recovery",
            "REPRODUCED"
            if observed == expected and caster_levels == {(3, 27)}
            else "CONFLICT",
            "; ".join(f"{v} on {t} by {s}" for v, t, s in observed)
            + f"; caster class/level {sorted(caster_levels)}"
            + "; captures "
            + ",".join(
                sorted(
                    {
                        self.join.rows[i]["capture"].removesuffix(".pcapng")
                        for i in cures
                    }
                )
            ),
            n=len(cures),
            tier_mix=self.row_tiers(cures, roles=("src",), fields=("class", "level")),
        )
        self.identity_row(
            "A35",
            PBL,
            CLASS3_ACTOR,
            "43722707 in party_battle_leve: class 3, Lv27, hpMax 750, mpMax 405 (frame 3453, T1)",
            {"class": 3, "level": 27, "hpMax": 750, "mpMax": 405},
            frame=3453,
        )
        self.identity_row(
            "A36",
            WQU2,
            CLASS3_ACTOR,
            "43722707 in war_quest_update2: class 2, Lv50, hpMax 2634, mpMax 1914",
            {"class": 2, "level": 50, "hpMax": 2634, "mpMax": 1914},
        )
        bridge = self.join.bridges.get((PBL, 0, CLASS4_ACTOR))
        if bridge:
            values = bridge["values"]
            ok = (
                values["class"],
                values["level"],
                bridge["hp_max_observed"],
                bridge["mp_max_observed"],
            ) == (4, 26, 758, 249)
            computed = (
                f"class {values['class']}, level {values['level']}, hpMax {values['hpMax']}, mpMax {values['mpMax']} "
                f"bridged from {','.join(c.removesuffix('.pcapng') for c in bridge['source_captures'])}; "
                f"in-capture hp max {bridge['hp_max_observed']}, mp max {bridge['mp_max_observed']}"
            )
        else:
            ok, computed = False, "no unique bridge"
        uses = self.select(
            lambda i, r: (
                r["capture"] == PBL
                and CLASS4_ACTOR in (r["source_actor_id"], r["target_actor_id"])
            )
        )
        self.add(
            "A37",
            "cure-identities",
            "43723073 in party_battle_leve: class 4, Lv26, hp 758, mp 249 by T2 bridge",
            "party_battle_leve; no class or level record; stat-ceiling bridge by actor id",
            "REPRODUCED" if ok else "CONFLICT",
            computed,
            n=len(uses),
            tier_mix=self.tier_mix(
                self.value(i, role, "level")[1]
                for i in uses
                for role, key in (
                    ("src", "source_actor_id"),
                    ("tgt", "target_actor_id"),
                )
                if self.join.rows[i][key] == CLASS4_ACTOR
            ),
        )
        for anchor_id, ids, expected_level, expected_hp in (
            ("A38", range(1158679889, 1158679894), 30, 550),
            ("A39", range(1158679894, 1158679899), 30, 770),
            ("A40", range(1158679843, 1158679844), 25, 679),
        ):
            parts, matches, contrary, outside = [], [], [], []
            for actor in ids:
                level = self.static_value(PBL, actor, "level")
                hp_max = self.static_value(PBL, actor, "hpMax")
                if (level, hp_max) == (expected_level, expected_hp):
                    matches.append(actor)
                elif level == expected_level:
                    contrary.append(f"{actor} hpMax {hp_max}")
                else:
                    outside.append(
                        f"{actor} no level or hpMax record"
                        if level is None and hp_max is None
                        else f"{actor} level {level} hpMax {hp_max}"
                    )
            # The anchor names Lv-N mobs in an id range; ids at another level or
            # without records are reported but do not contradict it.
            ok = bool(matches) and not contrary
            parts.append(
                f"level {expected_level} hpMax {expected_hp}: {','.join(str(a) for a in matches)}"
            )
            if contrary:
                parts.append(
                    f"level {expected_level} with other hpMax: " + "; ".join(contrary)
                )
            if outside:
                parts.append("outside the set: " + "; ".join(outside))
            first_id, last_id = ids[0], ids[-1]
            label = (
                f"mobs {first_id}-{str(last_id)[-2:]}"
                if len(ids) > 1
                else f"mob {first_id}"
            )
            self.add(
                anchor_id,
                "cure-identities",
                f"Lv{expected_level} {label}: hpMax {expected_hp}",
                "party_battle_leve; single distinct level and hpMax value per actor",
                "REPRODUCED" if ok else "CONFLICT",
                "; ".join(parts),
                n=len(matches),
                tier_mix=f"T1={2 * len(matches)}",
            )

    def static_value(self, capture: str, actor: int, field: str):
        static = self.join._static(capture, 0, actor, field)
        return None if static is None else static[2]

    def identity_row(self, anchor_id, capture, actor, anchor, expected, frame=None):
        observed, frames = {}, set()
        for field in expected:
            static = self.join._static(capture, 0, actor, field)
            observed[field] = None if static is None else static[2]
            if static is not None:
                frames.add(static[0][0])
        ok = observed == expected and (frame is None or frames == {frame})
        uses = self.select(
            lambda i, r: (
                r["capture"] == capture
                and actor in (r["source_actor_id"], r["target_actor_id"])
            )
        )
        tiers = [
            self.value(i, role, field)[1]
            for i in uses
            for role, key in (("src", "source_actor_id"), ("tgt", "target_actor_id"))
            if self.join.rows[i][key] == actor
            for field in expected
        ]
        self.add(
            anchor_id,
            "cure-identities",
            anchor,
            f"{capture.removesuffix('.pcapng')}; single record per field for actor {actor}",
            "REPRODUCED" if ok else "CONFLICT",
            ", ".join(f"{k} {v}" for k, v in observed.items())
            + f"; record frames {sorted(frames)}",
            n=len(uses),
            tier_mix=self.tier_mix(tiers),
        )

    def mob_table_anchors(self, table: list[dict]) -> None:
        by_level: dict[int, list[dict]] = defaultdict(list)
        for row in table:
            by_level[row["level"]].append(row)
        self.add(
            "A41",
            "mob-level-hp",
            "Table of every spawned actor with one level and one hpMax value",
            "all captures; spawned actors with a single distinct level and hpMax value",
            "REPRODUCED" if table else "UNRESOLVABLE",
            f"{len(table)} actor rows across {len(by_level)} levels; derived/mob-level-hp.csv",
            n=len(table),
            tier_mix=f"T1={2 * len(table)}",
        )
        for anchor_id, level, stated in (
            ("A42", 8, "169"),
            ("A43", 9, "189"),
            ("A44", 11, "194"),
            ("A45", 17, "288-338"),
        ):
            rows = by_level.get(level, [])
            values = Counter(row["hpMax"] for row in rows)
            observed = (
                (
                    f"{min(values)}-{max(values)}"
                    if len(values) > 1
                    else str(next(iter(values)))
                )
                if values
                else "absent"
            )
            self.add(
                anchor_id,
                "mob-level-hp",
                f"Lv{level} mob hpMax: corpus {stated} "
                f"vs earlier-version {EARLIER_VERSION_MOB_HP[level]}",
                f"spawned actors at level {level}",
                "CONFLICT"
                if values and set(values) != {int(EARLIER_VERSION_MOB_HP[level])}
                else "REPRODUCED",
                f"1.23b corpus {observed} ("
                + ", ".join(f"{hp} x{count}" for hp, count in sorted(values.items()))
                + f"); earlier-version value {EARLIER_VERSION_MOB_HP[level]}; both recorded"
                + (
                    ""
                    if observed == stated
                    else "; corpus differs from the anchor's value"
                ),
                n=len(rows),
                band_low=min(values) if values else "",
                band_high=max(values) if values else "",
                tier_mix=f"T1={2 * len(rows)}",
            )

    def unresolvable(self, subject_check: dict) -> None:
        low, high, kept, _ = self.intervals.get(
            (WQU2, 0, CLASS4_ACTOR), (None, None, [], [])
        )
        self.add(
            "U01",
            "unresolvable",
            "Lv30 recorder level for 43723073 in war_quest_update2",
            "war_quest_update2; no class or level record; no stat-ceiling bridge",
            "UNRESOLVABLE",
            "no level record and no unique bridge; the anchor's Lv30 stays T3",
            tier_mix="T3=1",
        )
        self.add(
            "U02",
            "unresolvable",
            "Name of class id 2",
            "war_quest_update2 actor 43722707",
            "UNRESOLVABLE",
            "class id 2 recorded; no packet field names it",
            tier_mix="T1=1",
        )
        mobs = [a for a in range(1163947556, 1163947560)]
        parts = []
        for actor in mobs:
            low, high, kept, _ = self.intervals.get(
                (WQU2, 0, actor), (None, None, [], [])
            )
            level = self.static_value(WQU2, actor, "level")
            hp_max = self.static_value(WQU2, actor, "hpMax")
            identity = (
                "no level or hpMax record"
                if level is None and hp_max is None
                else f"level {level} hpMax {hp_max}"
            )
            parts.append(
                f"{actor} k ({fmt4(low)}, {fmt4(high)}] n={len(kept)}, {identity}"
                if low is not None
                else f"{actor} no clean hits, {identity}"
            )
        self.add(
            "U03",
            "unresolvable",
            "Mobs 1163947556-59 (k about 0.469): level and hpMax",
            "war_quest_update2; tp-taken clean windows",
            "UNRESOLVABLE",
            "; ".join(parts),
            tier_mix="tp T0;level T3",
        )
        self.add(
            "U04",
            "unresolvable",
            "0x0137 subject is source_actor_id (64 percent of 234 hp-delta checks)",
            "damage rows with an hp record of the target before and within 14 frames after",
            "UNRESOLVABLE",
            f"hp delta equals damage on {subject_check['matches']}/{subject_check['checks']} "
            f"({100 * subject_check['matches'] / subject_check['checks']:.0f} percent); supported, not proven",
            n=subject_check["checks"],
            tier_mix=f"T0={subject_check['checks']}",
        )
        self.add(
            "U05",
            "unresolvable",
            "Recorder 43723073 identity in combat_autoattack, combat_skills and war_quest_update2",
            "no class or level record and no unique stat-ceiling bridge",
            "UNRESOLVABLE",
            "; ".join(
                f"{c.removesuffix('.pcapng')}: hp max {max([v for _, _, v in self.join.series(c, 0, CLASS4_ACTOR, 'hp')] or [0])}, "
                f"bridge {'yes' if (c, 0, CLASS4_ACTOR) in self.join.bridges else 'no'}"
                for c in (CAA, CSK, WQU2)
            ),
            tier_mix="T3=3",
        )


def subject_check(join: Join) -> dict:
    """Count damage rows whose target's next hp record drops by the damage."""
    checks = matches = 0
    for row in join.rows:
        if (
            row["message_class"] not in ("normal_damage", "critical_damage")
            or row["numeric_value"] <= 0
        ):
            continue
        series = join.series(
            row["capture"], row["lane_index"], row["target_actor_id"], "hp"
        )
        before = [v for key, _, v in series if key <= row["key"]]
        after = [(key, v) for key, _, v in series if key > row["key"]]
        if (
            not before
            or not after
            or after[0][0][0] - row["frame_index"] > TP_WINDOW_FRAMES
        ):
            continue
        checks += 1
        matches += before[-1] - after[0][1] == row["numeric_value"]
    return {"checks": checks, "matches": matches}


def mob_table(join: Join) -> list[dict]:
    table = []
    keys = sorted(
        {
            (capture, lane, actor)
            for capture, lane, actor, field in join.timeline
            if field == "level" and not is_player(actor)
        }
    )
    for capture, lane, actor in keys:
        level = join._static(capture, lane, actor, "level")
        hp_max = join._static(capture, lane, actor, "hpMax")
        if level is None or hp_max is None:
            continue
        classes = sorted({v for _, _, v in join.series(capture, lane, actor, "class")})
        table.append(
            {
                "level": level[2],
                "hpMax": hp_max[2],
                "classes": "/".join(str(c) for c in classes),
                "capture": capture,
                "actor_id": actor,
                "level_record_index": level[1],
                "hpMax_record_index": hp_max[1],
            }
        )
    table.sort(key=lambda r: (r["level"], r["hpMax"], r["capture"], r["actor_id"]))
    return table


def extra_observations(anchors: Anchors) -> list[str]:
    mob_on_gla = anchors.pbl_outcomes(
        target=CLASS3_ACTOR, commands=MOB_AUTOS, source_level=30
    )
    crits = anchors.outcome_counts(mob_on_gla)["critical_damage"]
    class2 = anchors.select(
        lambda i, r: (
            r["capture"] == WQU2
            and r["source_actor_id"] == CLASS3_ACTOR
            and r["command_id"] == PLAYER_AUTO
            and r["message_class"] in OUTCOME_CLASSES
        )
    )
    class2_crits = anchors.outcome_counts(class2)["critical_damage"]
    two = [
        e
        for e in anchors.engagements
        if e["capture"] == PBL and any(v == 2 for _, v in e["frames_hate"])
    ]
    return [
        f"Lv30 mobs crit the 43722707 actor on {crits} of {len(mob_on_gla)} autos in party_battle_leve.",
        f"The class-2 Lv50 actor 43722707 crits on {class2_crits} of {len(class2)} autos in war_quest_update2.",
        "hateType 2 appears as an intermediate state in the party_battle_leve engagement at frame "
        + ", ".join(str(e["start_frame"]) for e in two)
        + " (hateType 2 at frame "
        + ", ".join(str([f for f, v in e["frames_hate"] if v == 2][0]) for e in two)
        + ").",
    ]


# ---------------------------------------------------------------------------
# Rendering


def csv_bytes(fields, rows) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output, fieldnames=fields, lineterminator="\n", extrasaction="ignore"
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("ascii")


def json_bytes(obj) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def md_cell(text) -> str:
    return str(text).replace("|", "/")


def evidence_map(
    anchors: Anchors,
    table: list[dict],
    subject: dict,
    observations: list[str],
    accounting: dict,
) -> bytes:
    rows = anchors.rows
    verdicts = Counter(row["verdict"] for row in rows)
    lines = [
        "# Battle-result actor join evidence map",
        "",
        "Generated by `tools/extractors/extract_battle_result_actor_join.py`.",
        "`derived/anchor-summary.csv` holds one row per anchor with its counts,",
        "bands, k interval, tier mix and verdict.",
        "",
        "## Join",
        "",
        "Every row of `studies/battle-result-backfit/derived/battle-result-rows.csv`",
        f"({accounting['inputs']['battle_rows']['rows']} rows) is joined to",
        "`studies/property-stream-hash-catalog/derived/property-records.csv`",
        f"({accounting['inputs']['property_records']['records']} records) for both the",
        "source and the target actor. Each value carries one tier:",
        "",
        "| Tier | Meaning |",
        "|---|---|",
        "| T0 | The actor's own nearest-preceding record in the same capture and lane. |",
        "| T1 | No preceding record; the actor has a single distinct value for a slow field (class, level, hpMax, mpMax) in the capture. |",
        "| T2 | No record for the field in the capture; a unique (class, level, hpMax, mpMax) tuple for the same actor id in another capture whose hpMax and mpMax equal the actor's in-capture hp and mp maxima. |",
        "| T3 | Inferred; no record ties the value to the actor. Used only where an anchor states a value the join cannot supply (A24, U01, U05). |",
        "| none | No record, static value or bridge; the joined value is empty. |",
        "",
        "A tier mix counts the joined value lookups behind an anchor's selection:",
        "the level of both actors for outcome and band anchors, the stated fields",
        "for identity anchors.",
        "",
        "The join takes `source_actor_id` as the subject of a `0x0137` record. That",
        f"is supported, not proven: across {subject['checks']} damage rows whose target has an",
        "hp record before the row and another within 14 frames after it, the hp",
        f"drop equals the damage on {subject['matches']} ({100 * subject['matches'] / subject['checks']:.0f} percent). The",
        "`studies/player-hp-calibration` study likewise records that header",
        "equality does not identify the subject.",
        "",
        'Level selections such as "target level 30" use the joined level value at',
        "the row. Command names come from",
        "`xivl-client-data:derived/command_battle_params.csv`; actor labels GLA and",
        "MRD in anchor text are the anchors' own shorthand for the class-3 actor",
        "43722707 and the class-4 actor 43723073. Class ids are not mapped to class",
        "names here.",
        "",
        "## Methods",
        "",
        "- TP windows: each consecutive pair of an actor's tp records bounds the",
        "  battle rows that involve the actor. A taken window holds exactly one",
        "  landed hit on the actor, no other classified row at another key, no",
        "  same-packet row by the actor, a positive tp step, and its next tp",
        "  record within 14 frames of the hit. A dealt window holds exactly one own",
        "  command row (excluding `hp_recovery`), no landed hit on the actor, no",
        "  other classified row, and its next tp record within 14 frames of that",
        "  row. Rows the backfit classed `non_fit` or `unknown` do not break a",
        "  window.",
        "- k intervals: with delta = ceil(k * damage), each taken window bounds k to",
        "  ((delta - 1) / damage, delta / damage]. Windows whose ratio lies more than",
        "  0.05 from the actor's median ratio are dropped, then the bounds are",
        '  intersected. "About" a value means the interval reaches within 0.01 of it.',
        f"- Engage order: a run of `0x0187` subevents (each within {ENGAGE_RUN_GAP_FRAMES} frames of the",
        "  previous) starts an engagement when a hateType 2 or 3 record follows",
        f"  within {ENGAGE_WINDOW_FRAMES} frames of the run's first frame. The engagement spans to",
        "  the last such record. `0x0187` also occurs in login and travel captures;",
        "  only captures with a hateType 2 or 3 record are walked. Frame indices are",
        "  the reconstructed s2c outer-frame indices used by the CSV inputs.",
        "",
        "## Anchors",
        "",
        f"Verdicts: {', '.join(f'{name} {verdicts[name]}' for name in ('REPRODUCED', 'CONFLICT', 'UNRESOLVABLE'))}.",
        "",
        "| Id | Anchor | Computed | Tier mix | Verdict |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['anchor_id']} | {md_cell(row['anchor'])} | {md_cell(row['computed'])} | {md_cell(row['tier_mix'])} | {row['verdict']} |"
        )
    lines += [
        "",
        "## Conflicts",
        "",
        "The Lv8, Lv9, Lv11 and Lv17 rows (A42-A45) compare the 1.23b corpus with",
        "comparison values that a consumer project attributes to the 1.19-1.22",
        "era. This repository holds no source for those values. Both sets are",
        "recorded as observations of different versions; the study does not pick",
        "between them. The corpus values also show more than one hpMax at a single",
        "level for several levels (see the table below), so level alone does not",
        "fix mob hpMax in 1.23b.",
    ]
    lines += [
        "",
        "A34 reproduces the three Cure values, but not their attribution. Rows 174",
        "and 396 carry `source_actor_id` and `target_actor_id` 43722707 (151 and",
        "152). Row 176 carries value 166 with `source_actor_id` 43723073 and",
        "`target_actor_id` 43722707, the reverse of the anchor's caster and",
        "target. The battle-result backfit already records that row 176 has a",
        "different source. The packet fields are kept as decoded; this study does",
        "not reinterpret them.",
    ]
    lines += [
        "",
        "## Notes on reproduced anchors",
        "",
        "- A20 reproduces 38 of 39 when the 14-frame gap is measured from the",
        "  window's first row, as the anchor counted. Measured from the swing row,",
        "  as this study does, one more window qualifies (listed in A20) and also",
        "  steps +300, giving 39 of 40. Either way every isolated landed swing",
        "  steps +300 except the one capped at 3000.",
        "- A33 finds a fifth party_battle_leve engagement at frame 2870, which the",
        "  anchor does not list. The four listed engagements match.",
        "- A38 and A39 read their id ranges as the Lv30 mobs within them.",
        "  1158679891 has no level or hpMax record, and 1158679896 is a Lv26 actor",
        "  with hpMax 724; neither contradicts the anchor. Every Lv30 actor in the",
        "  ranges has the stated hpMax.",
        "- A06 and A08 include source or target actors with no level record; their",
        "  selections do not depend on those levels.",
    ]
    lines += [
        "",
        "## Unresolvable",
        "",
        "- U01: 43723073 has hp records but no class, level or mp record in",
        "  war_quest_update2, and its hp maximum matches no tuple from another",
        "  capture, so the Lv30 used by A24 stays T3. The k interval itself is",
        "  computed from T0 tp records.",
        "- U02: class id 2 is a recorded value; no packet field names it. Only the",
        "  `class_job` column of `xivl-client-data:derived/command_battle_params.csv`",
        "  bears on it.",
        "- U03: the war_quest_update2 mobs have tp-taken intervals but no level or",
        "  hpMax record.",
        "- U04: the subject assumption above.",
        "- U05: 43723073 has hp records but no identity tuple or matching ceiling in",
        "  combat_autoattack, combat_skills and war_quest_update2.",
        "",
        "Gear is not on the wire in these rows, so damage is reported as bands",
        "only. The Lv26 level of 43723073 in party_battle_leve is T2 (A37).",
        "",
        "## Mob level and hpMax",
        "",
        "`derived/mob-level-hp.csv` lists every spawned actor with a single distinct",
        "level and hpMax value in a capture. Summary by level:",
        "",
        "| Level | hpMax (actors) | Earlier-version value |",
        "|---:|---|---|",
    ]
    by_level: dict[int, Counter] = defaultdict(Counter)
    for row in table:
        by_level[row["level"]][row["hpMax"]] += 1
    for level in sorted(by_level):
        lines.append(
            f"| {level} | "
            + ", ".join(
                f"{hp} ({count})" for hp, count in sorted(by_level[level].items())
            )
            + f" | {EARLIER_VERSION_MOB_HP.get(level, '')} |"
        )
    lines += [
        "",
        "## Observations no earlier study cites",
        "",
    ] + [f"- {text}" for text in observations]
    lines += [
        "",
        "## Evidence gaps",
        "",
        "- Gear and attribute values are not joined; damage stays banded.",
        "- Class ids 2, 3 and 4 are not mapped to class names.",
        "- The subject of a `0x0137` record is supported, not proven.",
        "",
    ]
    return "\n".join(lines).encode("ascii")


def build(
    battle_rows: Path, property_records: Path, engage_source: Path, public_shape: bool
) -> dict[str, bytes]:
    """Build every product; public_shape reads engage_source as engage-order.csv."""
    verify_field_hashes()
    rows = load_battle_rows(battle_rows)
    records = load_property_records(property_records)
    join = Join(rows, records)
    events = tp_events(join)
    intervals = taken_intervals(events)
    if public_shape:
        engage_rows = read_engage_rows(engage_source)
    else:
        engage_rows = build_engage_rows(join, engage_source)
    anchors = Anchors(join, events, intervals, engage_rows)
    subject = subject_check(join)
    table = mob_table(join)
    anchors.hit_outcomes()
    anchors.damage_bands()
    anchors.tp_anchors()
    anchors.engage_anchors()
    anchors.identity_anchors()
    anchors.mob_table_anchors(table)
    anchors.unresolvable(subject)
    observations = extra_observations(anchors)

    manifest = yaml.safe_load(PCAP_MANIFEST.read_text(encoding="utf-8")) or {}
    members = {
        m["file"]: m
        for m in manifest.get("members", [])
        if isinstance(m, dict) and "file" in m
    }
    walked = engage_captures(join)
    tier_counts = {
        field: dict(
            sorted(
                Counter(
                    j[(role, field)][1] for j in join.joined for role in ("src", "tgt")
                ).items()
            )
        )
        for field in FIELDS
    }
    accounting = {
        "study": STUDY_ID,
        "inputs": {
            "battle_rows": {
                "path": "studies/battle-result-backfit/derived/battle-result-rows.csv",
                "sha256": sha256_file(battle_rows),
                "rows": len(rows),
            },
            "property_records": {
                "path": "studies/property-stream-hash-catalog/derived/property-records.csv",
                "sha256": sha256_file(property_records),
                "records": EXPECTED_PROPERTY_RECORDS,
                "joined_field_records": len(records),
            },
            "hash_names": HASH_NAME_SOURCE,
            "engage_captures": [
                {
                    "file": name,
                    "source": "sources/pcap-1.23b/manifest.yaml",
                    "sha256": members.get(name, {}).get("sha256", ""),
                }
                for name in walked
            ],
        },
        "hard_asserts": {
            "battle_rows": EXPECTED_BATTLE_ROWS,
            "property_records": EXPECTED_PROPERTY_RECORDS,
        },
        "fields": [
            {"column": column, "property": name, "hash": prop_hash}
            for column, name, prop_hash in FIELD_SPECS + (HATE_TYPE_SPEC,)
        ],
        "parameters": {
            "tp_window_frames": TP_WINDOW_FRAMES,
            "robust_ratio_drop": "0.05",
            "about_tolerance": "0.01",
            "engage_window_frames": ENGAGE_WINDOW_FRAMES,
            "engage_run_gap_frames": ENGAGE_RUN_GAP_FRAMES,
            "player_id_limit": PLAYER_ID_LIMIT,
        },
        "join_tier_counts": tier_counts,
        "bridges": [
            {
                "capture": capture,
                "lane_index": lane,
                "actor_id": actor,
                **bridge,
            }
            for (capture, lane, actor), bridge in sorted(join.bridges.items())
        ],
        "subject_check": subject,
        "tp_windows": dict(
            sorted(Counter(e["clean_kind"] or "unclean" for e in events).items())
        ),
        "engagements": len(anchors.engagements),
        "mob_level_hp_rows": len(table),
        "verdicts": dict(sorted(Counter(r["verdict"] for r in anchors.rows).items())),
        "boundaries": [
            "source_actor_id is taken as the 0x0137 subject; supported, not proven.",
            "Class ids are recorded values, not class names.",
            "Damage is banded; gear and attributes are not joined.",
        ],
    }
    outputs = {
        "joined-rows.csv": csv_bytes(JOINED_FIELDS, render_joined(join)),
        "anchor-summary.csv": csv_bytes(ANCHOR_FIELDS, anchors.rows),
        "tp-series.csv": csv_bytes(TP_FIELDS, render_tp(events, intervals)),
        "mob-level-hp.csv": csv_bytes(MOB_TABLE_FIELDS, table),
        "accounting.json": json_bytes(accounting),
        "evidence-map.md": evidence_map(
            anchors, table, subject, observations, accounting
        ),
    }
    if not public_shape:
        outputs["engage-order.csv"] = csv_bytes(ENGAGE_FIELDS, engage_rows)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--battle-rows", type=Path, default=DEFAULT_BATTLE_ROWS)
    parser.add_argument(
        "--property-records", type=Path, default=DEFAULT_PROPERTY_RECORDS
    )
    parser.add_argument(
        "--hash-names",
        type=Path,
        help="optional xivl-client-structs gam_hash_names.json to verify field names",
    )
    parser.add_argument("--pcap-dir", type=Path, default=PCAP_OBJECTS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--public-shape",
        action="store_true",
        help="reuse the committed engage-order.csv instead of the restricted pcaps",
    )
    args = parser.parse_args()
    if args.hash_names is not None:
        digest = verify_hash_names(args.hash_names)
        note = (
            ""
            if digest == HASH_NAME_SOURCE["sha256"]
            else " (digest differs from the pinned source)"
        )
        print(
            f"battle-result actor join: field names verified against {args.hash_names}{note}"
        )
    engage_source = (
        args.out_dir / "engage-order.csv" if args.public_shape else args.pcap_dir
    )
    if not args.public_shape and not any(args.pcap_dir.glob("*.pcapng")):
        raise SystemExit(f"no pcap objects in {args.pcap_dir}; use --public-shape")
    outputs = build(
        args.battle_rows, args.property_records, engage_source, args.public_shape
    )
    if args.check:
        stale = [
            name
            for name, data in outputs.items()
            if not (args.out_dir / name).is_file()
            or (args.out_dir / name).read_bytes() != data
        ]
        if stale:
            print(
                f"battle-result actor join: stale or missing {', '.join(stale)}",
                file=sys.stderr,
            )
            return 1
        print(f"battle-result actor join: {len(outputs)} products verified")
        return 0
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (args.out_dir / name).write_bytes(data)
    print(f"battle-result actor join: {len(outputs)} products written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
