#!/usr/bin/env python3
"""Distill the pinned restricted population tables without executing source SQL."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sqlite3
from collections import Counter
from decimal import Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STUDY = "monster-population-reported-observations"
BASE = "server_battlenpc_spawn_locations"
PROFILE = "server_battlenpc_mob_types"
CONDITION = "server_battlenpc_spawn_conditions"
TOKEN = re.compile(
    r"--[^\n]*|/\*[\s\S]*?\*/|'(?:''|\\.|[^'\\])*'|`[^`]*`|"
    r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|[A-Za-z_@][\w@]*|\S"
)


def value(token):
    if token.upper() == "NULL":
        return None
    if token.startswith("'"):
        return token[1:-1].replace("''", "'").replace("\\'", "'").replace("\\\\", "\\")
    if not re.fullmatch(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", token):
        raise ValueError(f"Not a literal: {token}")
    return token


def statements(text):
    tokens = []
    for match in TOKEN.finditer(text):
        token = match.group()
        if token.startswith(("--", "/*")):
            continue
        if token == ";":
            if tokens:
                yield tokens
            tokens = []
        else:
            tokens.append((token, match.start()))
    if tokens:
        raise ValueError("Unterminated SQL statement")


def literal_rows(tokens):
    words = [t[0] for t in tokens]
    end = words.index(")", 4)
    columns = [w.strip("`") for w in words[4:end] if w != ","]
    if words[end + 1] == "VALUES":
        i = end + 2
        while i < len(words):
            if words[i] == ",":
                i += 1
                continue
            if words[i] != "(":
                raise ValueError("Unexpected INSERT suffix")
            finish = words.index(")", i)
            cells = [value(w) for w in words[i + 1 : finish] if w != ","]
            if len(cells) != len(columns):
                raise ValueError("Column/value mismatch")
            yield dict(zip(columns, cells)), tokens[i][1]
            i = finish + 1
    elif words[end + 1] == "SELECT":
        # This pinned input uses one counter expression followed by literals.
        counter = words[end + 2].startswith("@")
        start = words.index(",", end + 2) + 1 if counter else end + 2
        finish = words.index("WHERE", start)
        cells = ([None] if counter else []) + [
            value(w) for w in words[start:finish] if w != ","
        ]
        if len(cells) != len(columns):
            raise ValueError("Unexpected conditional INSERT")
        yield dict(zip(columns, cells)), tokens[end + 2][1]
    else:
        raise ValueError("Unsupported INSERT")


def schema(text, table):
    body = re.search(
        r"CREATE TABLE IF NOT EXISTS `" + table + r"` \(([\s\S]*?)\n\)", text
    )[1]
    defaults = {}
    for line in body.splitlines():
        match = re.match(r"\s*`([^`]+)` (.*)", line)
        if match:
            default = re.search(r"DEFAULT ('(?:''|[^'])*'|NULL|\d+)", match[2])
            defaults[match[1]] = value(default[1]) if default else None
    return defaults


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(objects):
    texts = {p.name: p.read_text(encoding="utf-8-sig") for p in objects.glob("*.sql")}
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    defaults = {}
    for table, key in ((PROFILE, "bnpcId"), (BASE, "id"), (CONDITION, "id")):
        defaults[table] = schema(texts[table + ".sql"], table)
        definitions = [
            f"`{col}` TEXT" + (" PRIMARY KEY" if col == key else "")
            for col in defaults[table]
        ]
        db.execute(f"CREATE TABLE `{table}` ({','.join(definitions)})")
    history = {}
    aliases = []
    gaps = []
    corrections = []
    profile_changes = []
    inserts = Counter()
    files = [
        PROFILE + ".sql",
        BASE + ".sql",
        "server_battlenpc_stale_spawn_cleanup.sql",
        CONDITION + ".sql",
    ]
    for filename in files:
        text = texts[filename]
        for tokens in statements(text):
            words = [t[0] for t in tokens]
            op = words[0]
            if op not in ("INSERT", "REPLACE", "UPDATE", "DELETE"):
                continue
            table = words[2 if op in ("INSERT", "REPLACE", "DELETE") else 1].strip("`")
            if table not in defaults:
                continue
            line = text.count("\n", 0, tokens[0][1]) + 1
            locator = f"{filename}:{line}"
            if op in ("INSERT", "REPLACE"):
                for supplied, offset in literal_rows(tokens):
                    if set(supplied) - set(defaults[table]):
                        raise ValueError(
                            "INSERT names a column absent from CREATE TABLE"
                        )
                    row = defaults[table] | supplied
                    row_line = text.count("\n", 0, offset) + 1
                    if table == BASE and row["id"] is None:
                        row["id"] = str(-row_line)
                    key = (
                        row["id"]
                        if table == BASE
                        else row["bnpcId"]
                        if table == PROFILE
                        else str(inserts[table] + 1)
                    )
                    if table == CONDITION:
                        row["id"] = key
                    if "SELECT" in words:
                        if table == PROFILE:
                            if db.execute(
                                f"SELECT 1 FROM `{PROFILE}` WHERE bnpcId=?", (key,)
                            ).fetchone():
                                continue
                        elif table != BASE:
                            raise ValueError("Unexpected conditional table")
                    if "SELECT" in words and table == BASE:
                        if not db.execute(
                            f"SELECT 1 FROM `{PROFILE}` WHERE bnpcId=?",
                            (row["bnpcId"],),
                        ).fetchone():
                            raise ValueError("Conditional profile missing")
                        previous = db.execute(
                            f"SELECT * FROM `{BASE}` WHERE uniqueId=?",
                            (row["uniqueId"],),
                        ).fetchone()
                        if previous:
                            aliases.append(
                                {
                                    "observation_id": key,
                                    "source_locator": f"{filename}:{row_line}",
                                    "literal_fields": supplied,
                                }
                            )
                            continue
                    columns = list(row)
                    db.execute(
                        f"{op} INTO `{table}` ({','.join('`' + c + '`' for c in columns)}) VALUES ({','.join('?' for _ in row)})",
                        list(row.values()),
                    )
                    history[(table, key)] = {
                        "source_member": filename,
                        "source_line": row_line,
                        "supplied_fields": supplied,
                    }
                    inserts[table] += 1
            elif op == "UPDATE" and "JOIN" in words:
                gaps.append(
                    {
                        "source_locator": locator,
                        "field": "isNotorious",
                        "verdict": "unresolved external class join; not applied",
                    }
                )
            else:
                # SQLite sees only selected DML in an isolated in-memory table.
                # Quote numeric tokens to preserve decimal spelling in assignments.
                sql = " ".join(
                    "'" + w + "'" if re.fullmatch(r"-?\d+(?:\.\d+)?", w) else w
                    for w in words
                )
                if table == BASE and op == "UPDATE":
                    before = {
                        r["id"]: dict(r) for r in db.execute(f"SELECT * FROM `{BASE}`")
                    }
                    db.execute(sql)
                    for result in db.execute(f"SELECT * FROM `{BASE}`"):
                        key = result["id"]
                        for field in ("posX", "posY", "posZ", "rot"):
                            if before[key][field] != result[field]:
                                corrections.append(
                                    {
                                        "observation_id": result["uniqueId"],
                                        "field": field,
                                        "before": before[key][field],
                                        "after": result[field],
                                        "source_locator": locator,
                                        "verdict": "authored correction; not a retail measurement",
                                    }
                                )
                else:
                    if table == PROFILE and op == "UPDATE":
                        before = {
                            r["bnpcId"]: dict(r)
                            for r in db.execute(f"SELECT * FROM `{PROFILE}`")
                        }
                    db.execute(sql)
                    if table == PROFILE and op == "UPDATE":
                        for result in db.execute(f"SELECT * FROM `{PROFILE}`"):
                            for field in defaults[PROFILE]:
                                key = result["bnpcId"]
                                if before[key][field] != result[field]:
                                    profile_changes.append(
                                        {
                                            "profile_id": key,
                                            "field": field,
                                            "before": before[key][field],
                                            "after": result[field],
                                            "source_locator": locator,
                                        }
                                    )
    tables = {
        table: [dict(r) for r in db.execute(f"SELECT * FROM `{table}`")]
        for table in defaults
    }
    return tables, history, aliases, gaps, corrections, profile_changes, texts


def csv_bytes(rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def json_bytes(data):
    return (json.dumps(data, indent=2, ensure_ascii=True) + "\n").encode()


def build(objects):
    manifest = yaml.safe_load((ROOT / "sources" / STUDY / "manifest.yaml").read_text())
    for member in manifest["members"]:
        path = objects / member["file"]
        if (
            path.stat().st_size != member["size_bytes"]
            or digest(path) != member["sha256"]
        ):
            raise ValueError(f"Source identity mismatch: {path.name}")
    tables, history, aliases, gaps, corrections, profile_changes, texts = replay(
        objects
    )
    placements = sorted(
        tables[BASE], key=lambda r: history[(BASE, r["id"])]["source_line"]
    )
    referenced = {r["bnpcId"] for r in placements}
    profiles = {r["bnpcId"]: r for r in tables[PROFILE] if r["bnpcId"] in referenced}
    if referenced - profiles.keys():
        raise ValueError("Unresolved supplied profile reference")
    rows = []
    source_lines = texts[BASE + ".sql"].splitlines()
    source_digest = digest(objects / (BASE + ".sql"))
    sections = {}
    authored_sections = set()
    section = ""
    for number, source_line in enumerate(source_lines, 1):
        if source_line.startswith("-- BEGIN "):
            section = source_line[9:]
            header = source_lines[number : number + 5]
            if any(s.startswith("--") and "authored" in s.lower() for s in header):
                authored_sections.add(section)
        sections[number] = section
        if source_line.startswith("-- END "):
            section = ""
    for raw in placements:
        key = raw["id"]
        origin = history[(BASE, key)]
        profile = profiles[raw["bnpcId"]]
        line = origin["source_line"]
        preceding = source_lines[max(0, line - 9) : line - 1]
        note = next(
            (
                s[3:]
                for s in reversed(preceding)
                if re.match(r"-- .+ zone \d+ capture line \d+", s)
            ),
            "",
        )
        capture_line = re.search(r"capture line (\d+)", note)
        generated = any("generated close to" in s for s in preceding)
        authored = sections[line] in authored_sections
        density = "density boost" in sections[line]
        verdict = (
            "generated-companion-offset"
            if generated
            else "authored-habitat"
            if authored
            else "density-expansion-unverified"
            if density
            else "reported-unverified"
        )
        rows.append(
            {
                "observation_id": f"placement-{line:06d}",
                "reported_unique_id": raw["uniqueId"],
                "reported_row_id": origin["supplied_fields"]["id"],
                "source_member": origin["source_member"],
                "source_line": line,
                "source_sha256": source_digest,
                "reported_capture_line": capture_line[1] if capture_line else "",
                "reported_note": note,
                "zone": raw["zoneId"],
                "zone_identity_status": "supplied-numeric; client-join-unresolved",
                "subject_name": raw["mobName"],
                "profile_id": raw["bnpcId"],
                "reported_actor_id": profile["actorId"],
                "subject_identity_status": "supplied-profile-join; client-join-unresolved",
                "min_level": profile["min_lvl"],
                "max_level": profile["max_lvl"],
                "x": origin["supplied_fields"]["posX"],
                "y": origin["supplied_fields"]["posY"],
                "z": origin["supplied_fields"]["posZ"],
                "rotation": raw["rot"],
                "position_verdict": verdict,
                "source_section": sections[line],
                "defaulted_fields": ";".join(
                    k for k in raw if k not in origin["supplied_fields"]
                ),
                "reported_roams": raw["roams"],
                "reported_roam_delay": raw["roamDelay"],
                "reported_private_area": raw["privateArea"],
                "reported_private_area_level": raw["privateAreaLevel"],
                "reported_candidate_group": raw["spawnGroup"],
                "reported_link_group": raw["linkGroup"],
                "evidence_class": "historical-research",
                "retail_corroboration": "unresolved",
                "placement_claim_status": "reported-record-only; home/slot/respawn unresolved",
            }
        )
    profile_rows = []
    for key in sorted(profiles, key=int):
        raw = profiles[key]
        origin = history[(PROFILE, key)]
        profile_rows.append(
            {
                "profile_id": key,
                "source_member": origin["source_member"],
                "source_line": origin["source_line"],
                **{k: raw[k] for k in raw if k != "bnpcId"},
                "defaulted_fields": ";".join(
                    k for k in raw if k not in origin["supplied_fields"]
                ),
                "verdict": "supplied-values; not retail measurements",
            }
        )
    conditions = []
    targets = []
    for raw in tables[CONDITION]:
        origin = history[(CONDITION, raw["id"])]
        conditions.append(
            {
                "condition_id": raw["id"],
                "source_line": origin["source_line"],
                **{k: v for k, v in raw.items() if k != "id"},
                "verdict": "reported-condition; retail-unverified",
            }
        )
        field = {
            "uniqueId": "uniqueId",
            "bnpcId": "bnpcId",
            "spawnGroup": "spawnGroup",
        }[raw["targetType"]]
        for row in placements:
            if row[field] == raw["targetKey"]:
                targets.append(
                    {
                        "condition_id": raw["id"],
                        "observation_id": f"placement-{history[(BASE, row['id'])]['source_line']:06d}",
                        "verdict": "supplied-key-match; not a retail rule",
                    }
                )
    nm = []
    for tokens in statements(texts["server_battlenpc_nm_spawn_locations.sql"]):
        words = [t[0] for t in tokens]
        if words[:3] == ["INSERT", "INTO", "`" + BASE + "`"]:
            for raw, offset in literal_rows(tokens):
                candidates = [r for r in placements if r["uniqueId"] == raw["uniqueId"]]
                if len(candidates) != 1:
                    raise ValueError("NM alias must resolve exactly once")
                differing = [k for k in raw if k != "id" and raw[k] != candidates[0][k]]
                nm.append(
                    {
                        "observation_id": f"placement-{history[(BASE, candidates[0]['id'])]['source_line']:06d}",
                        "reported_unique_id": raw["uniqueId"],
                        "source_member": "server_battlenpc_nm_spawn_locations.sql",
                        "source_line": texts[
                            "server_battlenpc_nm_spawn_locations.sql"
                        ].count("\n", 0, offset)
                        + 1,
                        "differing_literal_fields": ";".join(differing),
                        "verdict": "alias; not an additional placement",
                    }
                )
    counts = {
        "placements": len(rows),
        "referenced_profiles": len(profiles),
        "nm_aliases": len(nm),
        "candidate_group_memberships": sum(bool(r["spawnGroup"]) for r in placements),
        "link_group_memberships": sum(bool(r["linkGroup"]) for r in placements),
        "conditions": len(conditions),
        "condition_targets": len(targets),
        "hp_overrides": sum(int(r["hpMax"]) > 0 for r in profiles.values()),
        "mp_overrides": sum(int(r["mpMax"]) > 0 for r in profiles.values()),
        "attack_40": sum(r["att"] == "40" for r in profiles.values()),
    }
    expected = dict(zip(counts, (7049, 599, 84, 63, 27, 12, 16, 31, 26, 599)))
    duplicate_labels = {
        k: v for k, v in Counter(r["reported_unique_id"] for r in rows).items() if v > 1
    }
    comparisons, comparison_inputs = compare(rows)
    unidentified = []
    for line, text in enumerate(source_lines, 1):
        match = re.fullmatch(
            r"--   line (\d+): unknown at ([^,]+), ([^,]+), ([^ ]+) zone (\d+)", text
        )
        if match:
            unidentified.append(
                {
                    "observation_id": f"unidentified-{line:06d}",
                    "source_member": BASE + ".sql",
                    "source_line": line,
                    "reported_capture_line": match[1],
                    "subject_name": "unknown",
                    "x": match[2],
                    "y": match[3],
                    "z": match[4],
                    "zone": match[5],
                    "verdict": "reported-unidentified; excluded from active placement rowset; retail-unverified",
                }
            )
    accounting = {
        "counts": counts,
        "expected": expected,
        "discrepancies": {
            k: {"actual": v, "expected": expected[k]}
            for k, v in counts.items()
            if v != expected[k]
        },
        "zones": dict(sorted(Counter(r["zone"] for r in rows).items())),
        "position_verdicts": dict(Counter(r["position_verdict"] for r in rows)),
        "retail_corroborated_rows": 0,
        "unapplied_source_join": gaps,
        "suppressed_conditional_aliases": len(aliases),
        "duplicate_reported_unique_ids": duplicate_labels,
        "comparison_inputs": comparison_inputs,
        "comparison_matches": dict(Counter(r["comparison"] for r in comparisons)),
        "unidentified_comment_records": len(unidentified),
    }
    for correction in corrections:
        correction["reported_unique_id"] = correction.pop("observation_id")
        matched = [
            r["observation_id"]
            for r in rows
            if r["reported_unique_id"] == correction["reported_unique_id"]
        ]
        if len(matched) != 1:
            raise ValueError("Ambiguous corrected row")
        correction["observation_id"] = matched[0]
    return {
        "observations.csv": csv_bytes(rows),
        "profiles.csv": csv_bytes(profile_rows),
        "conditions.csv": csv_bytes(conditions),
        "condition-targets.csv": csv_bytes(targets),
        "nm-aliases.csv": csv_bytes(nm),
        "source-corrections.json": json_bytes(corrections),
        "profile-changes.json": json_bytes(
            [c for c in profile_changes if c["profile_id"] in referenced]
        ),
        "comparisons.json": json_bytes(comparisons),
        "unidentified-records.json": json_bytes(unidentified),
        "accounting.json": json_bytes(accounting),
    }


def compare(rows):
    nav_path = (
        ROOT / "studies/navmut-world-population-observations/derived/observations.csv"
    )
    packet_path = ROOT / "derived/spawn_observations.csv"
    inputs = {
        str(p.relative_to(ROOT)).replace("\\", "/"): digest(p)
        for p in (nav_path, packet_path)
    }
    nav_index = {}
    packet_index = {}
    with nav_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            position = json.loads(
                row["position"], parse_float=Decimal, parse_int=Decimal
            )
            key = (row["zone"], *(v.quantize(Decimal(".001")) for v in position))
            nav_index.setdefault(key, []).append(row["observation_id"])
    with packet_path.open(encoding="utf-8", newline="") as handle:
        for line, row in enumerate(csv.DictReader(handle), 2):
            if all(row[k] for k in ("x", "y", "z")):
                key = tuple(Decimal(row[k]) for k in ("x", "y", "z"))
                packet_index.setdefault(key, []).append(
                    {
                        "csv_line": line,
                        "capture": row["capture"],
                        "actorId": row["actorId"],
                        "zoneTag": row["zoneTag"],
                    }
                )
    matches = []
    for row in rows:
        point = tuple(Decimal(row[k]) for k in ("x", "y", "z"))
        nav = nav_index.get(
            (row["zone"], *(v.quantize(Decimal(".001")) for v in point)), []
        )
        packet = packet_index.get(point, [])
        if nav:
            matches.append(
                {
                    "observation_id": row["observation_id"],
                    "comparison": "navmut-zone-position-rounded-0.001",
                    "matched_locators": nav,
                    "verdict": "numeric agreement only; independence and subject join unresolved",
                }
            )
        if packet:
            matches.append(
                {
                    "observation_id": row["observation_id"],
                    "comparison": "packet-position-exact-displayed-decimals",
                    "matched_locators": packet,
                    "verdict": "coordinate agreement only; zone and subject join unresolved; sighting is not a home",
                }
            )
    return matches, inputs


def validate_public(output):
    def read(name):
        with (output / name).open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    rows = read("observations.csv")
    profiles = read("profiles.csv")
    keys = {r["observation_id"] for r in rows}
    profile_keys = {r["profile_id"] for r in profiles}
    accounting = json.loads((output / "accounting.json").read_text())
    if len(keys) != len(rows) or len(profile_keys) != len(profiles):
        raise ValueError("Duplicate stable key")
    manifest = yaml.safe_load((ROOT / "sources" / STUDY / "manifest.yaml").read_text())
    members = {m["file"]: m["sha256"] for m in manifest["members"]}
    for row in rows:
        if row["observation_id"] != f"placement-{int(row['source_line']):06d}":
            raise ValueError("Row key lost source locator")
        if (
            row["profile_id"] not in profile_keys
            or row["source_sha256"] != members[row["source_member"]]
        ):
            raise ValueError("Unresolved row provenance")
        if (
            row["evidence_class"] != "historical-research"
            or row["retail_corroboration"] != "unresolved"
        ):
            raise ValueError("Unsupported evidence promotion")
        for field in ("x", "y", "z", "rotation"):
            if not Decimal(row[field]).is_finite():
                raise ValueError("Non-finite source coordinate")
    for name in ("nm-aliases.csv", "condition-targets.csv"):
        for row in read(name):
            if row["observation_id"] not in keys:
                raise ValueError("Dangling observation reference")
    condition_ids = {r["condition_id"] for r in read("conditions.csv")}
    if any(
        r["condition_id"] not in condition_ids for r in read("condition-targets.csv")
    ):
        raise ValueError("Dangling condition reference")
    counts = {
        "placements": len(rows),
        "referenced_profiles": len(profiles),
        "nm_aliases": len(read("nm-aliases.csv")),
        "candidate_group_memberships": sum(
            bool(r["reported_candidate_group"]) for r in rows
        ),
        "link_group_memberships": sum(bool(r["reported_link_group"]) for r in rows),
        "conditions": len(condition_ids),
        "condition_targets": len(read("condition-targets.csv")),
        "hp_overrides": sum(int(r["hpMax"]) > 0 for r in profiles),
        "mp_overrides": sum(int(r["mpMax"]) > 0 for r in profiles),
        "attack_40": sum(r["att"] == "40" for r in profiles),
    }
    if counts != accounting["counts"]:
        raise ValueError("Public count reconciliation differs")
    comparisons, inputs = compare(rows)
    if inputs != accounting["comparison_inputs"] or comparisons != json.loads(
        (output / "comparisons.json").read_text()
    ):
        raise ValueError("Comparison inputs or results changed")
    if any(field in rows[0] for field in ("hpMax", "mpMax", "att", "fallback_hp")):
        raise ValueError("Stat/model values entered placement observations")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--objects", type=Path, default=ROOT / "sources" / STUDY / "objects"
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--public-shape",
        action="store_true",
        help="check public invariants without restricted source regeneration",
    )
    args = parser.parse_args()
    output = ROOT / "studies" / STUDY / "derived"
    if args.public_shape:
        validate_public(output)
        print(f"{STUDY}: public invariants checked; restricted bytes not reproduced")
        return
    products = build(args.objects)
    for name, data in products.items():
        path = output / name
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                raise ValueError(f"Stale product: {name}")
        else:
            output.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    validate_public(output)
    print(
        f"{STUDY}: {len(products)} deterministic products {'checked' if args.check else 'written'}"
    )


if __name__ == "__main__":
    main()
