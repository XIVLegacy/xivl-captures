#!/usr/bin/env python3
"""Validate and publish the pinned Navmut world-population observations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "navmut-world-population-observations"
RAW_FILENAME = "observations.jsonl"
DEFAULT_INPUT = REPO_ROOT / "sources" / SOURCE_ID / "objects" / RAW_FILENAME
EXPECTED_SHA256 = "8bf6fb2a872e417f3cc94851d84fbf5bc7b76faca0d9164e493affdaeff40214"
EXPECTED_SIZE = 262971
EXPECTED_COUNT = 650
EXPECTED_ZONES = {128: 237, 159: 168, 190: 245}
EXPECTED_TYPES = {"monster": 590, "mmonster": 1, "npc": 18, "misc": 41}
CATEGORY_BY_TYPE = {
    "monster": "ambient",
    "mmonster": "encounter",
    "npc": "npc",
    "misc": "misc",
}
CATEGORY_ORDER = {"ambient": 0, "npc": 1, "encounter": 2, "misc": 3}
ENCOUNTER_NOTE_RE = re.compile(
    r"\b(?:quest|gc|boss|content)\b|\bgrand[\s_-]+company\b", re.IGNORECASE
)
OBSERVATION_KEYS = {
    "created_at",
    "map_bounds",
    "notes",
    "observation_id",
    "position",
    "profile_id",
    "rotation",
    "schema_version",
    "subject_name",
    "subject_type",
    "zone",
}
SUBJECT_TYPES = set(CATEGORY_BY_TYPE)
SUBJECT_TYPES.add("Misc")
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
PROFILE_RE = re.compile(r"^profile-[0-9a-f]{16}$")

# This is the only exact client zone binding present for the pinned zones.
# The other two numeric ids remain visible and deliberately unresolved.
CANONICAL_ZONE_NAMES = {
    128: "Lower La Noscea",
    159: "The Thousand Maws of Toto-Rak",
    190: "Mor Dhona",
}
CLIENT_ZONE_NAMES = {159: "fst0Dungeon03"}


class IntakeError(ValueError):
    """An input, identity, or generated-product contract failed."""


def category_for_type(subject_type: str) -> str:
    return CATEGORY_BY_TYPE[subject_type.lower()]


def category_for_record(record: dict[str, Any]) -> str:
    subject_type = record["subject_type"].lower()
    if subject_type in {"npc", "misc"}:
        return subject_type
    if subject_type == "mmonster":
        return "encounter"
    if subject_type == "monster" and (
        record["zone"] == 159 or ENCOUNTER_NOTE_RE.search(record["notes"])
    ):
        return "encounter"
    return "ambient"


def category_basis_for_record(record: dict[str, Any]) -> str:
    subject_type = record["subject_type"].lower()
    if subject_type == "npc":
        return "raw subject_type=npc"
    if subject_type == "misc":
        return "raw subject_type=misc"
    if subject_type == "mmonster":
        return "raw subject_type=mmonster encounter candidate"
    if record["zone"] == 159:
        return "The Thousand Maws of Toto-Rak monster encounter candidate"
    if ENCOUNTER_NOTE_RE.search(record["notes"]):
        return "explicit quest/Grand Company/GC/boss/content note encounter candidate"
    return "remaining overworld monster ambient candidate"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _reject_duplicate_fields(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IntakeError(f"duplicate JSON field {key!r}")
        result[key] = value
    return result


def _number(value: Any, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise IntakeError(f"{label} must be a number")
    if not math.isfinite(float(value)):
        raise IntakeError(f"{label} must be finite")


def validate_record(record: Any, line_number: int) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise IntakeError(f"line {line_number}: record must be an object")
    if set(record) != OBSERVATION_KEYS:
        missing = sorted(OBSERVATION_KEYS - set(record))
        extra = sorted(set(record) - OBSERVATION_KEYS)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("unexpected " + ", ".join(extra))
        raise IntakeError(f"line {line_number}: " + "; ".join(details))

    created_at = record["created_at"]
    if not isinstance(created_at, str) or not created_at.endswith("Z"):
        raise IntakeError(f"line {line_number}: created_at must be a UTC string")
    try:
        datetime.fromisoformat(created_at[:-1] + "+00:00")
    except ValueError as exc:
        raise IntakeError(f"line {line_number}: invalid created_at") from exc

    for field, length in (("map_bounds", 4), ("position", 3)):
        value = record[field]
        if not isinstance(value, list) or len(value) != length:
            raise IntakeError(f"line {line_number}: {field} must have {length} values")
        for index, item in enumerate(value):
            _number(item, f"line {line_number}: {field}[{index}]")

    notes = record["notes"]
    if not isinstance(notes, str):
        raise IntakeError(f"line {line_number}: notes must be a string")
    observation_id = record["observation_id"]
    if not isinstance(observation_id, str) or not UUID_RE.fullmatch(observation_id):
        raise IntakeError(f"line {line_number}: observation_id is not a UUID")
    profile_id = record["profile_id"]
    if not isinstance(profile_id, str) or not PROFILE_RE.fullmatch(profile_id):
        raise IntakeError(f"line {line_number}: profile_id is not a profile id")
    _number(record["rotation"], f"line {line_number}: rotation")
    if record["schema_version"] != 2:
        raise IntakeError(f"line {line_number}: schema_version must be 2")
    for field in ("subject_name", "subject_type"):
        if not isinstance(record[field], str):
            raise IntakeError(f"line {line_number}: {field} must be a string")
    if record["subject_type"] not in SUBJECT_TYPES:
        raise IntakeError(f"line {line_number}: unknown subject_type")
    zone = record["zone"]
    if isinstance(zone, bool) or not isinstance(zone, int) or zone < 0:
        raise IntakeError(f"line {line_number}: zone must be a non-negative integer")
    return record


def read_records(
    input_path: Path, *, enforce_pin: bool = True
) -> tuple[bytes, list[dict[str, Any]]]:
    try:
        raw = input_path.read_bytes()
    except OSError as exc:
        raise IntakeError(f"cannot read input: {input_path}") from exc
    digest = sha256_bytes(raw)
    if enforce_pin and (len(raw) != EXPECTED_SIZE or digest != EXPECTED_SHA256):
        raise IntakeError(f"input identity mismatch: size={len(raw)} sha256={digest}")
    if not raw.endswith(b"\n") or b"\r" in raw:
        raise IntakeError("input must be LF-delimited JSONL with a trailing newline")

    records: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for line_number, line in enumerate(raw.splitlines(), start=1):
        try:
            record = json.loads(line, object_pairs_hook=_reject_duplicate_fields)
        except (UnicodeDecodeError, json.JSONDecodeError, IntakeError) as exc:
            raise IntakeError(f"line {line_number}: invalid JSONL ({exc})") from exc
        record = validate_record(record, line_number)
        observation_id = record["observation_id"]
        canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
        if observation_id in seen:
            if seen[observation_id] != canonical:
                raise IntakeError(f"observation_id content conflict: {observation_id}")
            raise IntakeError(f"duplicate observation_id: {observation_id}")
        seen[observation_id] = canonical
        records.append(record)

    if enforce_pin:
        if len(records) != EXPECTED_COUNT:
            raise IntakeError(f"expected {EXPECTED_COUNT} records, got {len(records)}")
        zones = Counter(row["zone"] for row in records)
        types = Counter(row["subject_type"].lower() for row in records)
        if dict(zones) != EXPECTED_ZONES:
            raise IntakeError(f"zone distribution mismatch: {dict(zones)}")
        if dict(types) != EXPECTED_TYPES:
            raise IntakeError(f"subject_type distribution mismatch: {dict(types)}")
    return raw, records


def ordered_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda row: (
            row["zone"],
            CATEGORY_ORDER[category_for_record(row)],
            row["created_at"],
            row["observation_id"],
        ),
    )


def zone_name(zone: int) -> str:
    return CLIENT_ZONE_NAMES.get(zone, "unresolved")


def csv_rows(records: Iterable[dict[str, Any]]) -> list[list[Any]]:
    fields = [
        "source_ordinal",
        "observation_id",
        "created_at",
        "zone",
        "canonical_zone_name",
        "client_zone_name",
        "zone_identity_status",
        "category",
        "category_basis",
        "subject_type",
        "subject_name",
        "subject_identity_status",
        "profile_id",
        "map_bounds",
        "position",
        "rotation",
        "notes",
        "placement_claim_status",
    ]
    rows = list(records)
    by_id = {row["observation_id"]: index for index, row in enumerate(rows, 1)}
    output = [fields]
    for row in ordered_records(rows):
        output.append(
            [
                by_id[row["observation_id"]],
                row["observation_id"],
                row["created_at"],
                row["zone"],
                CANONICAL_ZONE_NAMES.get(row["zone"], "unresolved"),
                zone_name(row["zone"]),
                "resolved" if row["zone"] in CLIENT_ZONE_NAMES else "unresolved",
                category_for_record(row),
                category_basis_for_record(row),
                row["subject_type"],
                row["subject_name"],
                "unresolved",
                row["profile_id"],
                json.dumps(row["map_bounds"], separators=(",", ":")),
                json.dumps(row["position"], separators=(",", ":")),
                row["rotation"],
                row["notes"],
                "observation-only; home/slot/respawn unresolved",
            ]
        )
    return output


def render_csv(records: list[dict[str, Any]]) -> str:
    stream = StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerows(csv_rows(records))
    return stream.getvalue()


def markdown_value(value: Any) -> str:
    text = str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")
    return text


def render_review(records: list[dict[str, Any]]) -> str:
    grouped: dict[int, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in ordered_records(records):
        grouped[row["zone"]][category_for_record(row)].append(row)
    raw_misc_count = sum(row["subject_type"] == "misc" for row in records)
    raw_misc_title_count = sum(row["subject_type"] == "Misc" for row in records)

    lines = [
        "# Navmut World Population Observations",
        "",
        "This review surface preserves one row for each of the 650 pinned Navmut "
        "observations. Rows are ordered by numeric zone, review category, UTC "
        "timestamp, and observation UUID.",
        "",
        "The category is a provisional review partition. NPC and misc records "
        "remain in their source categories; Toto-Rak monsters and monsters with "
        "explicit quest, Grand Company, GC, boss, or content notes are encounter "
        "candidates; only remaining overworld monsters are ambient candidates. "
        "The raw spelling and UUID are retained. Subject identities are unresolved "
        "because no hydrated client actor table was available for this intake.",
        "Raw misc spellings are misc="
        f"{raw_misc_count}, Misc={raw_misc_title_count}; the case-folded misc count is "
        f"{raw_misc_count + raw_misc_title_count}.",
        "",
        "Positions, map bounds, and rotations are observations only. This study "
        "does not promote home, slot, or respawn claims.",
        "",
        "## Zone coverage",
        "",
        "| zone | canonical zone name | client zone name | identity status | records |",
        "|---:|---|---|---|---:|",
    ]
    for zone in sorted(grouped):
        total = sum(len(rows) for rows in grouped[zone].values())
        status = "resolved" if zone in CLIENT_ZONE_NAMES else "unresolved"
        lines.append(
            f"| {zone} | {CANONICAL_ZONE_NAMES.get(zone, 'unresolved')} | {zone_name(zone)} | "
            f"{status} | {total} |"
        )

    lines.extend(["", "## Records by zone and category", ""])
    for zone in sorted(grouped):
        status = "resolved" if zone in CLIENT_ZONE_NAMES else "unresolved"
        lines.extend(
            [
                f"### Zone {zone} ({CANONICAL_ZONE_NAMES.get(zone, 'unresolved')}; "
                f"client binding {status}; {zone_name(zone)})",
                "",
            ]
        )
        for category in sorted(grouped[zone], key=CATEGORY_ORDER.__getitem__):
            rows = grouped[zone][category]
            lines.extend(
                [
                    f"#### {category} ({len(rows)})",
                    "",
                    "| observation_id | created_at | subject_type | subject_name | profile_id | position | rotation | notes | category basis | identity | placement |",
                    "|---|---|---|---|---|---|---:|---|---|---|---|",
                ]
            )
            for row in rows:
                position = json.dumps(row["position"], separators=(",", ":"))
                values = [
                    row["observation_id"],
                    row["created_at"],
                    row["subject_type"],
                    row["subject_name"],
                    row["profile_id"],
                    position,
                    row["rotation"],
                    row["notes"],
                    category_basis_for_record(row),
                    "unresolved",
                    "observation-only",
                ]
                lines.append(
                    "| " + " | ".join(markdown_value(v) for v in values) + " |"
                )
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_evidence_map(records: list[dict[str, Any]], raw: bytes) -> str:
    zones = Counter(row["zone"] for row in records)
    types = Counter(row["subject_type"].lower() for row in records)
    raw_types = Counter(row["subject_type"] for row in records)
    categories = Counter(category_for_record(row) for row in records)
    lines = [
        "# Navmut World Population Observations",
        "",
        "## Confirmed",
        "",
        f"- The immutable source member sources/{SOURCE_ID}/objects/{RAW_FILENAME} "
        f"is {len(raw)} bytes with SHA-256 {sha256_bytes(raw)}.",
        f"- The source contains {len(records)} unique schema-v2 observations.",
        "- Zone counts are "
        + ", ".join(f"{zone}={zones[zone]}" for zone in sorted(zones))
        + ".",
        "- Case-folded subject-type counts are "
        + ", ".join(f"{kind}={types[kind]}" for kind in sorted(types))
        + ".",
        "- Raw misc spellings are misc="
        f"{raw_types['misc']}, Misc={raw_types['Misc']}; case-folded misc="
        f"{raw_types['misc'] + raw_types['Misc']}.",
        "- Canonical zone facets are "
        + ", ".join(
            f"{zone}={CANONICAL_ZONE_NAMES[zone]}"
            for zone in sorted(CANONICAL_ZONE_NAMES)
        )
        + ".",
        "- Review categories are a provisional deterministic partition: "
        + ", ".join(
            f"{category}={categories[category]}" for category in sorted(categories)
        )
        + ".",
        "- Monster classification promotes only Toto-Rak monsters and explicit "
        "quest/Grand Company/GC/boss/content note markers to encounter candidates; "
        "remaining overworld monsters are ambient candidates. NPC and misc records "
        "remain in their source categories.",
        "- Zone 159 resolves to client internal name fst0Dungeon03 from "
        "xivl-client-data:manifests/zone_internal_names.json.",
        "",
        "## Unverifiable",
        "",
        "- Subject names remain raw Navmut labels. No client actor identity is "
        "promoted without a supported static-data join.",
        "- Zones 128 and 190 remain numeric-only because no exact client zone "
        "binding for these ids is present in the reviewed client manifest.",
        "- Position, map bounds, and rotation are not interpreted as a home point, "
        "spawn slot, respawn point, or respawn rule.",
        "",
        "## Derived review products",
        "",
        f"- studies/{SOURCE_ID}/derived/observations.csv carries one row per "
        "observation with category and identity-status columns.",
        f"- studies/{SOURCE_ID}/derived/review-by-zone.md carries the same 650 "
        "records grouped by zone and category.",
        "",
        "## Gaps",
        "",
        "- Client actor ids, canonical display names, population slots, and home "
        "locations require a supported join or a separate retail observation; none "
        "is asserted here.",
        "- Promotion gap: video URL is missing.",
        "- Promotion gap: video title is missing.",
        "- Promotion gap: video time ranges are missing.",
        "- Promotion gap: source patch is missing.",
        "- Promotion gap: respawn timing is missing.",
        "- Promotion gap: confidence is missing; no per-record confidence grade is "
        "asserted.",
        "- Promotion gap: respawn behavior remains unresolved and is not asserted.",
    ]
    return "\n".join(lines) + "\n"


def render_source_manifest(raw: bytes) -> str:
    return f"""id: {SOURCE_ID}
title: Navmut World Population Observations
evidence_class: historical-research
distribution: public
provenance:
  contributor: gavint130
  source: Navmut world-population observer
  filename: {RAW_FILENAME}
  schema_version: 2
  observed_at: 2026-09-16/17
  note: Directly recorded world-population observations; raw labels and UUIDs are retained.
storage:
  original_state: in-repo
  storage_id: repo
  path: objects/
members:
- file: {RAW_FILENAME}
  sha256: {sha256_bytes(raw)}
  size_bytes: {len(raw)}
notes: >-
  This source preserves the pinned Navmut JSONL bytes. It records observations,
  not canonical population definitions or home, slot, or respawn rules.
"""


def render_study_manifest() -> str:
    return f"""id: {SOURCE_ID}
title: Navmut World Population Observations
evidence_class: historical-research
status: indexed
content_kind: zone-mechanic
zones:
- Lower La Noscea
- The Thousand Maws of Toto-Rak
- Mor Dhona
tags:
- navmut
- world-population
- spawn-observation
- ambient
- npc
- encounter
- misc
- unresolved-identities
- provisional
search_hints:
- Navmut world population
- zone 128
- zone 159
- zone 190
- fst0Dungeon03
- ambient NPC encounter misc observations
notes: >-
  Indexed, provisional observations attributed to gavint130. The derived review
  surface keeps all records and raw spellings while leaving unsupported
  identities and placement semantics unresolved. Promotion gaps are missing
  video URL, video title, video time ranges, source patch, respawn timing, and
  confidence grading.
promotion_gaps:
- video URL is missing
- video title is missing
- video time ranges are missing
- source patch is missing
- respawn timing is missing
- confidence grading is missing
source_refs:
- source: {SOURCE_ID}
primary_paths:
- derived/evidence-map.md
- derived/observations.csv
- derived/review-by-zone.md
canonical_evidence:
- derived/observations.csv
- derived/review-by-zone.md
- derived/evidence-map.md
"""


def write_if_changed(path: Path, content: bytes, *, check: bool) -> None:
    existing = path.read_bytes() if path.exists() else None
    if existing == content:
        return
    if check:
        raise IntakeError(f"stale or missing generated file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(content)
    try:
        temporary.replace(path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def install_raw(source_dir: Path, raw: bytes, *, check: bool) -> None:
    path = source_dir / "objects" / RAW_FILENAME
    if path.exists():
        if path.read_bytes() != raw:
            raise IntakeError(f"source member content conflict: {path}")
        return
    if check:
        raise IntakeError(f"missing immutable source member: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def run(args: argparse.Namespace) -> None:
    raw, records = read_records(args.input, enforce_pin=True)
    source_dir = args.source_dir
    study_dir = args.study_dir
    install_raw(source_dir, raw, check=args.check)
    write_if_changed(
        source_dir / "manifest.yaml",
        render_source_manifest(raw).encode("utf-8"),
        check=args.check,
    )
    write_if_changed(
        study_dir / "manifest.yaml",
        render_study_manifest().encode("utf-8"),
        check=args.check,
    )
    write_if_changed(
        study_dir / "derived" / "observations.csv",
        render_csv(records).encode("utf-8"),
        check=args.check,
    )
    write_if_changed(
        study_dir / "derived" / "review-by-zone.md",
        render_review(records).encode("utf-8"),
        check=args.check,
    )
    write_if_changed(
        study_dir / "derived" / "evidence-map.md",
        render_evidence_map(records, raw).encode("utf-8"),
        check=args.check,
    )
    print(
        f"PASS: {len(records)} observations, {len(set(row['zone'] for row in records))} zones, "
        f"sha256 {sha256_bytes(raw)}"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="input JSONL; defaults to the tracked in-repo source member",
    )
    parser.add_argument(
        "--source-dir", type=Path, default=REPO_ROOT / "sources" / SOURCE_ID
    )
    parser.add_argument(
        "--study-dir", type=Path, default=REPO_ROOT / "studies" / SOURCE_ID
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        run(parse_args(argv))
    except (IntakeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
