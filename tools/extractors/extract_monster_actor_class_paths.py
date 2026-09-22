#!/usr/bin/env python3
"""Join retained spawn lifetimes to configured monster actor classes."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_observations import default_corpus_paths  # type: ignore  # noqa: E402
from extract_payload_samples import walk_capture_payloads  # type: ignore  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
STUDY = REPO_ROOT / "studies" / "monster-actor-class-paths"
INPUT = STUDY / "inputs" / "target_actor_classes.csv"
DERIVED = STUDY / "derived"
FAMILY_CROSSCHECK = (
    REPO_ROOT
    / "studies"
    / "gamerescape-tables"
    / "derived"
    / "mob-client-crosscheck.csv"
)

OP_INSTANTIATE = 0x00CC
OP_APPEARANCE = 0x00D6
OP_NAME = 0x013D

INPUT_FIELDS = (
    "pool_id",
    "pool_name",
    "source",
    "actor_class_id",
    "display_name_id",
    "base_model_id",
    "identity_pair_catalog_count",
    "catalog_class_path",
    "configured_class_path",
)
OCCURRENCE_FIELDS = (
    "capture",
    "instantiate_record_index",
    "appearance_record_index",
    "name_record_index",
    "network_actor_id",
    "actor_class_id",
    "pool_name",
    "display_name_id",
    "base_model_id",
    "identity_pair_catalog_count",
    "instance_name",
    "base_class",
    "observed_class_path",
)
MAPPING_FIELDS = (
    "pool_id",
    "pool_name",
    "source",
    "actor_class_id",
    "display_name_id",
    "base_model_id",
    "identity_pair_catalog_count",
    "catalog_class_path",
    "configured_class_path",
    "retail_observation_count",
    "retail_class_paths",
    "verdict",
    "adoption_path",
)
TAXONOMY_FIELDS = (
    "actor_class_id",
    "pool_name",
    "era_family",
    "decoded_race_name",
    "catalog_class_path",
    "configured_class_path",
    "runtime_class_paths",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ascii_strings(raw: bytes) -> list[str]:
    return [match.decode("latin1") for match in re.findall(rb"[\x20-\x7e]{3,}", raw)]


def _render_csv(fields: tuple[str, ...], rows: list[dict]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return out.getvalue().encode("utf-8")


def _read_targets(path: Path = INPUT) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != INPUT_FIELDS:
            raise ValueError("target actor-class input header is not canonical")
        rows = []
        for row in reader:
            parsed = dict(row)
            for field in (
                "pool_id",
                "actor_class_id",
                "display_name_id",
                "base_model_id",
                "identity_pair_catalog_count",
            ):
                parsed[field] = int(parsed[field])
            rows.append(parsed)
    if len(rows) != 52:
        raise ValueError(f"expected 52 target rows, found {len(rows)}")
    actor_ids = [row["actor_class_id"] for row in rows]
    if len(set(actor_ids)) != len(actor_ids):
        raise ValueError("target actor-class IDs are not unique")
    return rows


def _scan(targets: list[dict]) -> tuple[list[dict], dict]:
    by_pair: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for target in targets:
        by_pair[(target["display_name_id"], target["base_model_id"])].append(target)

    occurrences: list[dict] = []
    capture_count = 0
    decoded_records = 0
    instantiate_records = 0
    completed_lifetimes = 0

    for capture in default_corpus_paths():
        if not capture.is_file():
            continue
        capture_count += 1
        active: dict[int, dict] = {}
        for record_index, record in enumerate(walk_capture_payloads(capture)):
            decoded_records += 1
            if record["direction"] != "s2c":
                continue
            raw = bytes.fromhex(record["bytes"])
            if len(raw) < 20:
                continue
            actor_id = int.from_bytes(raw[8:12], "little")
            opcode = record["opcode"]
            if opcode == OP_INSTANTIATE:
                instantiate_records += 1
                strings = _ascii_strings(raw)
                class_path = next(
                    (value for value in strings if value.startswith("/Chara/")), ""
                )
                path_index = strings.index(class_path) if class_path else -1
                active[actor_id] = {
                    "instantiate_record_index": record_index,
                    "appearance_record_index": None,
                    "name_record_index": None,
                    "display_name_id": None,
                    "base_model_id": None,
                    "instance_name": strings[0].lstrip("&%3=(+*)/-#$ !\"'0123456789")
                    if strings
                    else "",
                    "base_class": strings[path_index - 1] if path_index > 0 else "",
                    "observed_class_path": class_path,
                    "completed": False,
                }
                continue
            if opcode not in (OP_APPEARANCE, OP_NAME) or actor_id not in active:
                continue
            state = active[actor_id]
            value = int.from_bytes(raw[16:20], "little")
            if opcode == OP_APPEARANCE:
                state["base_model_id"] = value
                state["appearance_record_index"] = record_index
            else:
                state["display_name_id"] = value
                state["name_record_index"] = record_index
            if state["completed"] or None in (
                state["display_name_id"],
                state["base_model_id"],
            ):
                continue
            state["completed"] = True
            completed_lifetimes += 1
            pair = (state["display_name_id"], state["base_model_id"])
            for target in by_pair.get(pair, []):
                occurrences.append(
                    {
                        "capture": capture.name,
                        "instantiate_record_index": state["instantiate_record_index"],
                        "appearance_record_index": state["appearance_record_index"],
                        "name_record_index": state["name_record_index"],
                        "network_actor_id": f"0x{actor_id:08x}",
                        "actor_class_id": target["actor_class_id"],
                        "pool_name": target["pool_name"],
                        "display_name_id": state["display_name_id"],
                        "base_model_id": state["base_model_id"],
                        "identity_pair_catalog_count": target[
                            "identity_pair_catalog_count"
                        ],
                        "instance_name": state["instance_name"],
                        "base_class": state["base_class"],
                        "observed_class_path": state["observed_class_path"],
                    }
                )

    occurrences.sort(
        key=lambda row: (
            row["capture"],
            row["instantiate_record_index"],
            row["actor_class_id"],
        )
    )
    return occurrences, {
        "capture_count": capture_count,
        "decoded_record_count": decoded_records,
        "instantiate_record_count": instantiate_records,
        "completed_lifetime_count": completed_lifetimes,
    }


def _build_mappings(targets: list[dict], occurrences: list[dict]) -> list[dict]:
    by_id: dict[int, list[dict]] = defaultdict(list)
    for occurrence in occurrences:
        by_id[occurrence["actor_class_id"]].append(occurrence)

    mappings = []
    for target in sorted(targets, key=lambda row: row["pool_id"]):
        actor_occurrences = by_id.get(target["actor_class_id"], [])
        exact = [
            row
            for row in actor_occurrences
            if row["identity_pair_catalog_count"] == 1
            and row["observed_class_path"].startswith("/Chara/Npc/Monster/")
        ]
        retail_paths = sorted({row["observed_class_path"] for row in exact})
        catalog_path = target["catalog_class_path"]
        if catalog_path:
            adoption_path = catalog_path
            if len(retail_paths) > 1:
                verdict = "catalog_with_runtime_variants"
            elif retail_paths and retail_paths[0] != catalog_path:
                verdict = "catalog_with_runtime_override"
            elif retail_paths:
                verdict = "catalog_runtime_supported"
            else:
                verdict = "catalog_only"
        elif retail_paths:
            verdict = "runtime_instance_only"
            adoption_path = ""
        else:
            verdict = "unresolved"
            adoption_path = ""
        mappings.append(
            {
                **{field: target[field] for field in INPUT_FIELDS},
                "retail_observation_count": len(exact),
                "retail_class_paths": "|".join(retail_paths),
                "verdict": verdict,
                "adoption_path": adoption_path,
            }
        )
    return mappings


def _build_taxonomy(mappings: list[dict]) -> list[dict]:
    with FAMILY_CROSSCHECK.open(newline="", encoding="utf-8-sig") as handle:
        by_name = {
            row["mob_name"].strip().lower(): row
            for row in csv.DictReader(handle)
            if row["mob_name"].strip()
        }
    rows = []
    for mapping in mappings:
        mob = by_name.get(mapping["pool_name"].replace("_", " ").lower(), {})
        rows.append(
            {
                "actor_class_id": mapping["actor_class_id"],
                "pool_name": mapping["pool_name"],
                "era_family": mob.get("ge_family", ""),
                "decoded_race_name": mob.get("client_race_name", ""),
                "catalog_class_path": mapping["catalog_class_path"],
                "configured_class_path": mapping["configured_class_path"],
                "runtime_class_paths": mapping["retail_class_paths"],
            }
        )
    return rows


def _verdicts(mappings: list[dict], occurrences: list[dict], accounting: dict) -> bytes:
    priority = {row["actor_class_id"]: row for row in mappings}
    catalog = [row for row in mappings if row["verdict"].startswith("catalog")]
    unresolved = [row for row in mappings if row["verdict"] == "unresolved"]
    lines = [
        "# Monster actor-class path verdicts",
        "",
        "## Adoption boundary",
        "",
        "The decoded actorclass catalog is the ID-to-class-path authority. Retained",
        "`0x00CC` paths describe individual runtime instances and do not replace that",
        "static mapping. Configured family/job paths are candidates, not mappings.",
        "",
        "| Actor class | Pool | Verdict | Path | Evidence |",
        "|---:|---|---|---|---|",
    ]
    for row in catalog:
        lines.append(
            f"| {row['actor_class_id']} | {row['pool_name']} | "
            f"{row['verdict']} | `{row['adoption_path']}` | "
            f"{row['retail_observation_count']} retained lifetimes |"
        )
    lines.extend(
        [
            "",
            "Puroboros is cataloged as `/Chara/Npc/Monster/Bomb/BombNormalStandard`.",
            "Its era family and decoded race are both Bomb. Two retained Puroboros",
            "lifetimes were instantiated through `CactusLesserStandard`; this is a",
            "runtime-class override observation, not an actorclass remapping.",
            "",
            "## Priority Kobold results",
            "",
        ]
    )
    for actor_id in (2106637, 2106628):
        row = priority[actor_id]
        lines.append(
            f"- {actor_id} `{row['pool_name']}`: UNRESOLVED. The decoded identity pair "
            f"({row['display_name_id']}, {row['base_model_id']}) is shared by "
            f"{row['identity_pair_catalog_count']} actor-class rows and has no retained "
            "class-path lifetime. The configured Goblin path is only a family/job "
            "calibration."
        )
    lines.extend(
        [
            "",
            "The client-script registry proves that `GoblinBommerGlaStandard` exists,",
            "but its schema has no actor-class ID. The retained Goblin instantiate row",
            "therefore does not identify either Kobold class. The era family and decoded",
            "race both identify these rows as Kobold. The configured Goblin path remains",
            "an implementation calibration, not a taxonomy or mapping claim.",
            "",
            "## Other decoded catalog rows",
            "",
            "| Actor class | Pool | Catalog path |",
            "|---:|---|---|",
        ]
    )
    for row in [item for item in catalog if item["actor_class_id"] != 2101608]:
        lines.append(
            f"| {row['actor_class_id']} | {row['pool_name']} | "
            f"`{row['catalog_class_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Unresolved rows",
            "",
            f"The remaining {len(unresolved)} rows are unresolved. Their configured paths",
            "remain calibration candidates only; blank candidates stay blank. Exact rows",
            "and candidates are retained in `mappings.csv`.",
            "",
            "## Coverage and method",
            "",
            f"The extractor scanned {accounting['capture_count']} retained captures,",
            f"{accounting['decoded_record_count']} decoded records,",
            f"{accounting['instantiate_record_count']} instantiate records, and",
            f"{accounting['completed_lifetime_count']} lifetimes carrying both appearance",
            "and display-name identity. It resets identity state on each `0x00CC`",
            "instantiate, then joins `0x00D6` application `u32 +0x00` (graphic base)",
            "and `0x013D` application `u32 +0x00` (display-name ID) for the same network",
            "actor lifetime. A globally unique decoded pair identifies the actor-class",
            "row associated with that lifetime. It does not make the lifetime's",
            "instance class path the static actorclass path.",
            "",
            "The two positive rows are in `war_quest_update2.pcapng` at decoded record",
            "indexes 1999/2007 and 2035/2043 (instantiate/name; appearance is recorded in",
            "`occurrences.csv`), both on network actor `0x50e15b06`.",
            "",
            "## Evidence boundary",
            "",
            "Class-file or registry existence is not an actor-ID association. A matching",
            "family name, graphic base alone, display name alone, network actor ID, or",
            "per-instance class path cannot replace a decoded actorclass mapping.",
            "Network actor IDs are reused across lifetimes.",
            "Missing retained coverage is an irreducible historical limitation; this",
            "study does not request a new capture or runtime probe.",
            "",
        ]
    )
    return ("\n".join(lines)).encode("ascii")


def build() -> dict[str, bytes]:
    targets = _read_targets()
    occurrences, scan = _scan(targets)
    mappings = _build_mappings(targets, occurrences)
    taxonomy = _build_taxonomy(mappings)
    counts = Counter(row["verdict"] for row in mappings)
    accounting = {
        "version": "1.23b",
        "target_count": len(targets),
        **scan,
        "matched_occurrence_count": len(occurrences),
        "verdict_counts": dict(sorted(counts.items())),
        "input": {
            "path": "inputs/target_actor_classes.csv",
            "sha256": _sha256(INPUT),
            "family_crosscheck_path": "studies/gamerescape-tables/derived/mob-client-crosscheck.csv",
            "family_crosscheck_sha256": _sha256(FAMILY_CROSSCHECK),
            "bahamut_revision": "453691c2ad619234beb448aaefc3b234294c2539",
            "bahamut_monster_pools_sha256": "24ec4b0a8f8688118d96aab81dcd7f7e0efb9f25b00b20a40ea41dbb4ad5c1f0",
            "bahamut_actorclass_sha256": "8ed0cc0dd6783f008797ff2e0d6f05578489d5801831b2c0513b38473f344a25",
            "bahamut_actorclass_graphic_sha256": "4da32970742e571555bec8f4708cb083040b5b071b11bb37785e7496d388f383",
            "client_data_revision": "bd3515848fe5564bab9eb901558ab918c427a709",
            "actorclass_csv_sha256": "3ac9f8d1812d49101f367e2a41356be96b5d64b1fc5ca29949195f50ebe1d984",
            "actorclass_graphic_csv_sha256": "7da8241400530885e0a28ded04a03acf2771b0580a79c1f49f46ee0861010611",
            "set_actor_appearance_source_sha256": "2edd15504afb2025665f9fafc98b925f331318756a9eb154f6e7fca9302623ef",
            "set_actor_name_source_sha256": "23ee664cefd9c57c99a18de567e0d439b2eb4db8bf4bdaf3c26beee339e33e81",
        },
    }
    return {
        "accounting.json": (
            json.dumps(accounting, indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8"),
        "occurrences.csv": _render_csv(OCCURRENCE_FIELDS, occurrences),
        "mappings.csv": _render_csv(MAPPING_FIELDS, mappings),
        "taxonomy.csv": _render_csv(TAXONOMY_FIELDS, taxonomy),
        "verdicts.md": _verdicts(mappings, occurrences, accounting),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    products = build()
    problems = []
    for name, expected in products.items():
        path = DERIVED / name
        if args.check:
            if not path.is_file() or path.read_bytes() != expected:
                problems.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(expected)
    if problems:
        print("stale monster actor-class path products: " + ", ".join(problems))
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {len(products)} monster actor-class path products")
    return 0


if __name__ == "__main__":
    sys.exit(main())
