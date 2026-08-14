#!/usr/bin/env python3
"""Decode the complete retained 1.23b battle-result packet family.

The output is a study-local evidence table. It preserves capture-local wire
order and joins worldMaster row identity, but it does not infer actor stats,
command behavior, or damage semantics from numeric fields.
"""

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

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from extract_observations import (  # type: ignore  # noqa: E402
    INNER_HEADER_LEN,
    SUB_EVENT_CLASS_ACTOR_WRAPPED,
    SUB_EVENT_HEADER_LEN,
    default_corpus_paths,
)
from extract_streams import (  # type: ignore  # noqa: E402
    maybe_inflate,
    parse_outer_frames,
    reconstruct_lanes,
)

OPCODES = {0x0139: ("X01", 1, 88), 0x013A: ("X10", 10, 216),
           0x013B: ("X18", 18, 328), 0x013C: ("X00", 0, 72)}
APP_PREFIX_LEN = INNER_HEADER_LEN + 8
STUDY_DIR = REPO_ROOT / "studies" / "battle-result-backfit"
DEFAULT_OUT = STUDY_DIR / "derived"
PCAP_MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"

CSV_FIELDS = [
    "row_index", "capture", "scenario_id", "wire_index", "lane_index",
    "frame_index", "outer_timestamp_or_seq_hex", "subevent_index", "subevent_offset",
    "opcode", "shape",
    "row_index_in_packet", "row_count", "source_actor_id", "target_actor_id",
    "effect_or_animation_id", "command_id", "numeric_value",
    "world_master_text_id", "message_class", "effect_id", "text_param",
    "row_ordinal_or_filter", "header_control_value", "presentation_flags",
]

MESSAGE_CLASSES = {
    30108: ("non_fit", "actor defeats target"),
    30109: ("non_fit", "actor regains consciousness"),
    30112: ("non_fit", "body part incapacitated"),
    30116: ("non_fit", "actor defeats target variant"),
    30126: ("non_fit", "actor readies command"),
    30128: ("non_fit", "actor begins casting command"),
    30209: ("non_fit", "command fails"),
    30301: ("normal_damage", "normal damage"),
    30302: ("critical_damage", "critical damage"),
    30303: ("normal_damage", "normal body-part damage"),
    30304: ("critical_damage", "critical body-part damage"),
    30305: ("block_damage", "blocked damage variant 1"),
    30306: ("block_damage", "blocked damage variant 2"),
    30307: ("block_damage", "blocked damage variant 3"),
    30308: ("parry_damage", "parried damage variant 1"),
    30309: ("parry_damage", "parried damage variant 2"),
    30310: ("evade", "evade"),
    30311: ("miss", "miss"),
    30312: ("non_fit", "obstructed action"),
    30313: ("normal_damage", "alternate damage"),
    30314: ("non_fit", "impervious"),
    30315: ("non_fit", "hit without numeric damage"),
    30316: ("evade", "evade with optional damage"),
    30317: ("evade", "partial evade damage"),
    30318: ("evade", "slight evade damage"),
    30319: ("normal_damage", "alternate normal damage"),
    30320: ("hp_recovery", "HP recovery"),
    30321: ("non_fit", "MP recovery"),
    30322: ("non_fit", "TP recovery"),
    30323: ("normal_damage", "additional-effect damage"),
    30328: ("non_fit", "command applies status"),
    30330: ("non_fit", "status applied"),
    30331: ("non_fit", "status ended"),
    30332: ("non_fit", "HP absorption"),
    30333: ("non_fit", "MP absorption"),
    30334: ("non_fit", "TP absorption"),
    30335: ("non_fit", "command applies status variant"),
    30338: ("non_fit", "status ended variant"),
    33008: ("hp_recovery", "Aegis Boon HP recovery"),
    33909: ("non_fit", "skill level attained"),
    33919: ("non_fit", "EXP chain"),
    33921: ("non_fit", "experience gained"),
    33934: ("non_fit", "experience earned variant 1"),
    33935: ("non_fit", "experience earned variant 2"),
    33936: ("non_fit", "experience earned variant 3"),
    33950: ("non_fit", "experience earned variant 4"),
    33954: ("non_fit", "experience earned variant 5"),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_scenarios() -> dict[str, str]:
    manifest = yaml.safe_load(PCAP_MANIFEST.read_text(encoding="utf-8")) or {}
    result: dict[str, str] = {}
    for scenario in manifest.get("scenarios") or []:
        for member in scenario.get("members") or []:
            if member in result:
                raise ValueError(f"capture belongs to multiple scenarios: {member}")
            result[member] = scenario["id"]
    return result


def load_world_master(path: Path) -> dict[int, str]:
    rows: dict[int, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.reader(handle):
            if row and row[0].isdigit():
                rows[int(row[0])] = row[2] if len(row) > 2 else ""
    return rows


def validate_cure_command(path: Path) -> None:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [row for row in csv.reader(handle) if row and row[0] == "27346"]
    if len(rows) != 1 or len(rows[0]) < 2 or rows[0][1] != "Cure":
        raise ValueError("command_battle_params does not map command 27346 to Cure")


def validate_field_model(path: Path) -> None:
    model = json.loads(path.read_text(encoding="utf-8"))
    variants = {int(v["opcodeHex"], 16): v for v in model["wireVariants"]}
    for opcode, (_shape, capacity, size) in OPCODES.items():
        variant = variants[opcode]
        if variant["rowCapacity"] != capacity or variant["subpacketSize"] != size:
            raise ValueError(f"field model disagrees for 0x{opcode:04X}")
    queue = {field["name"]: field for field in model["queueEntry"]["fields"]}
    expected = {"sourceActorId": 0, "effectOrAnimationId": 4,
                "rowCount": 32, "commandId": 36, "presentationFlags": 38}
    for name, offset in expected.items():
        if queue[name].get("wireOffset") != offset:
            raise ValueError(f"field model wire offset disagrees for {name}")


def classify(message_id: int, known_rows: dict[int, str]) -> tuple[str, str]:
    if message_id in MESSAGE_CLASSES and message_id in known_rows:
        return MESSAGE_CLASSES[message_id]
    if message_id == 0:
        return "unknown", "no worldMaster row"
    if message_id in known_rows:
        return "known_unmapped", "localized row not mapped by this study"
    return "unknown", "worldMaster row absent"


def _u8(app: bytes, offset: int) -> int:
    return app[offset]


def _u16(app: bytes, offset: int) -> int:
    return struct.unpack_from("<H", app, offset)[0]


def _u32(app: bytes, offset: int) -> int:
    return struct.unpack_from("<I", app, offset)[0]


def decode_packet(app: bytes, opcode: int) -> tuple[dict, list[dict]]:
    shape, capacity, _size = OPCODES[opcode]
    if len(app) < 40:
        raise ValueError(f"0x{opcode:04X} application payload is too short")
    header = {
        "shape": shape,
        "source_actor_id": _u32(app, 0),
        "effect_or_animation_id": _u32(app, 4),
        "row_count": _u16(app, 0x20),
        "header_control_value": _u16(app, 0x22),
        "command_id": _u16(app, 0x24),
        "presentation_flags": _u16(app, 0x26),
    }
    count = header["row_count"]
    if count > capacity:
        raise ValueError(f"0x{opcode:04X} row count {count} exceeds {capacity}")
    rows: list[dict] = []
    if opcode == 0x0139:
        for i in range(count):
            rows.append({
                "target_actor_id": _u32(app, 0x28),
                "numeric_value": _u16(app, 0x2C),
                "world_master_text_id": _u16(app, 0x2E),
                "effect_id": _u32(app, 0x30),
                "text_param": _u8(app, 0x34),
                "row_ordinal_or_filter": _u8(app, 0x35),
            })
    elif opcode == 0x013A:
        for i in range(count):
            rows.append({
                "target_actor_id": _u32(app, 0x28 + i * 4),
                "numeric_value": _u16(app, 0x50 + i * 2),
                "world_master_text_id": _u16(app, 0x64 + i * 2),
                "effect_id": _u32(app, 0x78 + i * 4),
                "text_param": _u8(app, 0xA0 + i),
                "row_ordinal_or_filter": _u8(app, 0xAA + i),
            })
    elif opcode == 0x013B:
        for i in range(count):
            rows.append({
                "target_actor_id": _u32(app, 0x28 + i * 4),
                "numeric_value": _u16(app, 0x70 + i * 2),
                "world_master_text_id": _u16(app, 0x94 + i * 2),
                "effect_id": _u32(app, 0xB8 + i * 4),
                "text_param": _u8(app, 0x100 + i),
                "row_ordinal_or_filter": _u8(app, 0x112 + i),
            })
    return header, rows


def extract(captures: list[Path], world_rows: dict[int, str]) -> tuple[list[dict], dict]:
    scenario_by_capture = load_scenarios()
    rows: list[dict] = []
    packets: Counter[str] = Counter()
    packet_rows: Counter[str] = Counter()
    scenario_packets: dict[str, Counter[str]] = defaultdict(Counter)
    scenario_rows: Counter[str] = Counter()
    source_mismatches = 0
    target_count_mismatches = 0

    for capture in captures:
        scenario = scenario_by_capture.get(capture.name, "unassigned")
        wire_index = 0
        for lane_index, lane in enumerate(reconstruct_lanes(capture)):
            blob = lane["streams"].get("s2c", b"")
            for frame_index, frame in enumerate(parse_outer_frames(blob)):
                body = maybe_inflate(frame["body"])
                if body is None:
                    body = frame["body"]
                offset = 0
                subevent_index = 0
                while offset + SUB_EVENT_HEADER_LEN <= len(body):
                    size, event_type = struct.unpack_from("<HH", body, offset)
                    if size == 0:
                        break
                    if size < SUB_EVENT_HEADER_LEN or offset + size > len(body):
                        break
                    if event_type == SUB_EVENT_CLASS_ACTOR_WRAPPED:
                        sub_body = body[offset + SUB_EVENT_HEADER_LEN:offset + size]
                        if len(sub_body) >= INNER_HEADER_LEN:
                            opcode = _u16(sub_body, 2)
                            if opcode in OPCODES:
                                shape, _capacity, expected_size = OPCODES[opcode]
                                if size != expected_size:
                                    raise ValueError(
                                        f"{capture.name}: 0x{opcode:04X} size {size}, expected {expected_size}")
                                app = sub_body[APP_PREFIX_LEN:]
                                header, decoded = decode_packet(app, opcode)
                                src_header = _u32(body, offset + 4)
                                if src_header != header["source_actor_id"]:
                                    source_mismatches += 1
                                nonzero_targets = sum(r["target_actor_id"] != 0 for r in decoded)
                                if nonzero_targets != header["row_count"]:
                                    target_count_mismatches += 1
                                key = f"0x{opcode:04X}"
                                packets[key] += 1
                                packet_rows[key] += len(decoded)
                                scenario_packets[scenario][key] += 1
                                scenario_rows[scenario] += len(decoded)
                                for row_in_packet, decoded_row in enumerate(decoded):
                                    message_class, _label = classify(
                                        decoded_row["world_master_text_id"], world_rows)
                                    rows.append({
                                        "row_index": len(rows),
                                        "capture": capture.name,
                                        "scenario_id": scenario,
                                        "wire_index": wire_index,
                                        "lane_index": lane_index,
                                        "frame_index": frame_index,
                                        "outer_timestamp_or_seq_hex": frame["timestamp"].hex(),
                                        "subevent_index": subevent_index,
                                        "subevent_offset": offset,
                                        "opcode": key,
                                        "shape": shape,
                                        "row_index_in_packet": row_in_packet,
                                        **header,
                                        **decoded_row,
                                        "message_class": message_class,
                                    })
                    wire_index += 1
                    subevent_index += 1
                    offset += size

    accounting = {
        "schema_version": 1,
        "packet_counts": {
            f"0x{opcode:04X}": packets[f"0x{opcode:04X}"] for opcode in OPCODES
        },
        "row_counts": {
            f"0x{opcode:04X}": packet_rows[f"0x{opcode:04X}"] for opcode in OPCODES
        },
        "packet_total": sum(packets.values()),
        "row_total": len(rows),
        "source_actor_mismatches": source_mismatches,
        "row_count_nonzero_target_mismatches": target_count_mismatches,
        "scenario_counts": {
            scenario: {
                "packets": dict(sorted(counts.items())),
                "rows": scenario_rows[scenario],
            }
            for scenario, counts in sorted(scenario_packets.items())
        },
        "message_class_counts": dict(sorted(Counter(r["message_class"] for r in rows).items())),
        "world_master_text_id_counts": {
            str(key): value for key, value in sorted(
                Counter(r["world_master_text_id"] for r in rows).items())
        },
        "cure_command_27346": {
            "row_count": sum(r["command_id"] == 27346 for r in rows),
            "hp_recovery_rows": sum(
                r["command_id"] == 27346 and r["message_class"] == "hp_recovery" for r in rows),
            "hp_recovery_values": sorted(
                r["numeric_value"] for r in rows
                if r["command_id"] == 27346 and r["message_class"] == "hp_recovery"),
        },
    }
    return rows, accounting


def render_csv(rows: list[dict]) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row[key] for key in CSV_FIELDS})
    return handle.getvalue().encode("ascii")


def render_messages(rows: list[dict], world_rows: dict[int, str]) -> bytes:
    counts = Counter(r["world_master_text_id"] for r in rows)
    handle = io.StringIO(newline="")
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(["world_master_text_id", "observed_rows", "message_class", "message_label", "join_status"])
    for message_id, count in sorted(counts.items()):
        message_class, label = classify(message_id, world_rows)
        status = "zero_id" if message_id == 0 else (
            "joined" if message_id in world_rows else "row_absent")
        writer.writerow([message_id, count, message_class, label, status])
    return handle.getvalue().encode("ascii")


def build_outputs(client_data_repo: Path, field_model: Path) -> dict[str, bytes]:
    world_path = client_data_repo / "csv" / "worldMaster.csv"
    command_path = client_data_repo / "derived" / "command_battle_params.csv"
    if not world_path.is_file():
        raise FileNotFoundError(world_path)
    if not command_path.is_file():
        raise FileNotFoundError(command_path)
    validate_field_model(field_model)
    validate_cure_command(command_path)
    captures = default_corpus_paths()
    world_rows = load_world_master(world_path)
    rows, accounting = extract(captures, world_rows)
    accounting["inputs"] = {
        "pcap_manifest": {"path": "sources/pcap-1.23b/manifest.yaml", "sha256": sha256_file(PCAP_MANIFEST)},
        "field_model": {
            "path": "xivl-client-structs:manifests/battle_result_field_semantics.json",
            "sha256": sha256_file(field_model),
        },
        "world_master": {
            "path": "xivl-client-data:csv/worldMaster.csv",
            "sha256": sha256_file(world_path),
        },
        "command_battle_params": {
            "path": "xivl-client-data:derived/command_battle_params.csv",
            "sha256": sha256_file(command_path),
        },
        "captures": [
            {"name": path.name, "sha256": sha256_file(path)} for path in captures
        ],
    }
    expected = {"0x0139": 438, "0x013A": 66, "0x013B": 0, "0x013C": 27}
    observed = {key: accounting["packet_counts"].get(key, 0) for key in expected}
    if observed != expected or accounting["row_total"] != 622:
        raise ValueError(f"corpus accounting changed: packets={observed}, rows={accounting['row_total']}")
    return {
        "battle-result-rows.csv": render_csv(rows),
        "world-master-messages.csv": render_messages(rows, world_rows),
        "accounting.json": (json.dumps(accounting, indent=2, sort_keys=True) + "\n").encode("ascii"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-data-repo", type=Path, required=True)
    parser.add_argument("--field-model", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs(args.client_data_repo.resolve(), args.field_model.resolve())
    stale: list[str] = []
    for name, content in outputs.items():
        target = args.out_dir / name
        if args.check:
            if not target.is_file() or target.read_bytes() != content:
                stale.append(str(target))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    if stale:
        print("stale battle-result outputs:")
        for path in stale:
            print(f"  {path}")
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {len(outputs)} battle-result artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
