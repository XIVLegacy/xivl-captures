#!/usr/bin/env python3
"""Audit retained regular bestiary pages for species drop evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
STUDY = REPO / "studies/elemen-bestiary"
OUT = STUDY / "derived"
DROP_FIELDS = (
    "species_jp",
    "client_family_id",
    "mob_name_jp",
    "mob_name_en_client",
    "level_band",
    "item_jp",
    "item_en_client",
    "item_client_id",
    "drop_group",
    "rarity_mark",
    "crystal_or_shard_note",
    "evidence_class",
    "source_locator",
)
COVERAGE_FIELDS = (
    "species_jp",
    "species_en_site",
    "client_generic_name",
    "client_generic_id",
    "client_variant_count",
    "genus_jp",
    "source_page",
    "retained_page",
    "source_sha256",
    "crystal_priority_note",
    "item_table_present",
    "level_band_present",
    "evidence_class",
    "verdict",
)


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_bytes(fields, data) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(data)
    return out.getvalue().encode("utf-8")


def table_fields_present(text: str) -> tuple[bool, bool]:
    labels = [
        line.split("|")[1].strip() for line in text.splitlines() if line.startswith("|")
    ]
    return (
        any(label in {"アイテム", "ドロップ", "戦利品"} for label in labels),
        any(label in {"レベル", "Lv", "Lv."} for label in labels),
    )


def build_outputs(public_shape: bool = False) -> dict[str, bytes]:
    manifest = yaml.safe_load(
        (REPO / "sources/elemen-bestiary/manifest.yaml").read_text("utf-8")
    )
    members = {m["file"]: m for m in manifest["members"]}
    taxonomy = {r["genus_jp"]: r for r in rows(OUT / "bestiary-taxonomy.csv")}
    inventory = {
        r["source_page"]: r
        for r in rows(OUT / "file-inventory.csv")
        if r["kind"] == "bestiary"
    }
    if len(inventory) != 65:
        raise ValueError("regular bestiary page coverage changed")
    evidence = {}
    for source_page, record in inventory.items():
        page = REPO / record["page_file"]
        member_key = page.relative_to(
            REPO / "sources/elemen-bestiary/objects"
        ).as_posix()
        member = members[member_key]
        if public_shape:
            evidence[source_page] = (record["page_file"], member["sha256"])
            continue
        data = page.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if (len(data), digest) != (member["size_bytes"], member["sha256"]):
            raise ValueError("bestiary source identity mismatch")
        text = data.decode("utf-8")
        # These are the preserved NM table labels, not an English-name heuristic.
        item_present, level_present = table_fields_present(text)
        if item_present or level_present:
            raise ValueError(
                "regular page now carries drop/level evidence; extend the extractor"
            )
        evidence[source_page] = (record["page_file"], digest)
    coverage = []
    for species in rows(OUT / "species-client-map.csv"):
        genus = taxonomy[species["genus_jp"]]
        source_page = genus["source"]
        retained, digest = evidence[source_page]
        coverage.append(
            {
                **{
                    k: species[k]
                    for k in (
                        "species_jp",
                        "species_en_site",
                        "client_generic_name",
                        "client_generic_id",
                        "client_variant_count",
                        "genus_jp",
                    )
                },
                "source_page": source_page,
                "retained_page": retained,
                "source_sha256": digest,
                "crystal_priority_note": genus["crystal_drop_priority_by_element"],
                "item_table_present": "no",
                "level_band_present": "no",
                "evidence_class": "site table",
                "verdict": "no retained ordinary-item drop list",
            }
        )
    inputs = (
        "bestiary-taxonomy.csv",
        "species-client-map.csv",
        "file-inventory.csv",
        "mob-drops.csv",
    )
    accounting = {
        "schema_version": 1,
        "evidence_class": "web-tables",
        "regular_pages": len(evidence),
        "species": len(coverage),
        "species_drop_rows": 0,
        "nm_drop_rows_unchanged": len(rows(OUT / "mob-drops.csv")),
        "inputs": {
            name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
            for name in inputs
        },
        "source_pages": [
            {"source_page": page, "retained_page": retained, "sha256": digest}
            for page, (retained, digest) in sorted(evidence.items())
        ],
        "boundary": "The retained regular-page transcriptions contain taxonomy, species, crystal priority, inferred elemental attributes, and special moves. They establish no ordinary-item drop rows, mob level bands, item ids, drop groups, rarity marks, or rates. Crystal priority is a site table observation, not an item-id mapping or drop probability. No inference rows are emitted.",
    }
    return {
        "species-drops.csv": csv_bytes(DROP_FIELDS, []),
        "species-drop-coverage.csv": csv_bytes(COVERAGE_FIELDS, coverage),
        "species-drop-accounting.json": (
            json.dumps(accounting, indent=2) + "\n"
        ).encode("ascii"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--public-shape", action="store_true")
    args = parser.parse_args()
    for name, content in build_outputs(args.public_shape).items():
        path = OUT / name
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                raise ValueError(f"stale species product: {name}")
        else:
            path.write_bytes(content)
    print(
        f"species drop coverage: {'verified' if args.check else 'generated'} 3 products"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
