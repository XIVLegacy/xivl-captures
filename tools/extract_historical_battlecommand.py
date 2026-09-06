#!/usr/bin/env python3
"""Extract provisional command research from BattleCommand.ods.

The extractor reads cached ODS cell values. It does not evaluate formulas or
promote analyst labels to retail facts.
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from xml.etree import ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    REPO_ROOT
    / "sources"
    / "historical-battlecommand-workbook"
    / "objects"
    / "BattleCommand.ods"
)
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "studies"
    / "historical-battlecommand-workbook"
    / "derived"
    / "commands.json"
)

NS = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}
TABLE_NAME = f"{{{NS['table']}}}name"
TABLE_DISPLAY = f"{{{NS['table']}}}display"
COL_REPEAT = f"{{{NS['table']}}}number-columns-repeated"
ROW_REPEAT = f"{{{NS['table']}}}number-rows-repeated"
FORMULA = f"{{{NS['table']}}}formula"
VALUE_TYPE = f"{{{NS['office']}}}value-type"
VALUE_ATTRS = {
    "boolean": f"{{{NS['office']}}}boolean-value",
    "currency": f"{{{NS['office']}}}value",
    "date": f"{{{NS['office']}}}date-value",
    "float": f"{{{NS['office']}}}value",
    "percentage": f"{{{NS['office']}}}value",
    "string": f"{{{NS['office']}}}string-value",
    "time": f"{{{NS['office']}}}time-value",
}
MAX_COLUMNS = 159  # A through FC, the workbook's last documented column.


def column_index(name: str) -> int:
    value = 0
    for char in name:
        value = value * 26 + ord(char) - ord("A") + 1
    return value - 1


def as_text(value: str) -> str | None:
    return value if value != "" else None


def as_int(value: str) -> int | None:
    if value == "":
        return None
    try:
        number = float(value)
    except ValueError as exc:
        raise ValueError(f"expected integer, got {value!r}") from exc
    if not number.is_integer():
        raise ValueError(f"expected integer, got {value!r}")
    return int(number)


def as_float(value: str) -> float | None:
    if value == "":
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"expected number, got {value!r}") from exc


def as_bool(value: str) -> bool | None:
    if value == "":
        return None
    lowered = value.lower()
    if lowered not in {"true", "false"}:
        raise ValueError(f"expected boolean, got {value!r}")
    return lowered == "true"


@dataclass(frozen=True)
class Field:
    name: str
    column: str
    layer: str
    normalize: Callable[[str], object]
    boundary: str


FIELDS = (
    Field("command_id", "B", "workbook-field", as_int, "numeric command identifier"),
    Field("command_id_hex", "E", "cached-formula", as_text, "cached hexadecimal rendering of B"),
    Field("name", "D", "workbook-field", as_text, "unlabeled source column; retain as workbook name"),
    Field("command_user", "F", "analyst-label", as_text, "secondary taxonomy"),
    Field("genus_id", "G", "workbook-field", as_int, "numeric value; genus meaning follows the workbook header"),
    Field("command_notes", "H", "analyst-note", as_text, "lead only"),
    Field("animation_type", "I", "workbook-field", as_int, "header records an unresolved capture conflict"),
    Field("model_animation", "J", "workbook-field", as_int, "numeric animation component"),
    Field("effect_animation", "K", "workbook-field", as_int, "numeric animation component"),
    Field("full_battle_animation", "L", "cached-formula", as_int, "cached composition of I, J, and K"),
    Field("full_battle_animation_hex", "M", "cached-formula", as_text, "cached hexadecimal rendering of L"),
    Field("command_type_code", "W", "workbook-field", as_int, "raw workbook taxonomy code"),
    Field("max_range", "AZ", "workbook-field", as_float, "label also permits radius or line length"),
    Field("best_range", "BA", "workbook-field", as_float, "numeric range field"),
    Field("minimum_range", "BB", "workbook-field", as_float, "numeric range field"),
    Field("fallback_radius", "BC", "workbook-field", as_float, "numeric range field"),
    Field("cast_time", "BL", "workbook-field", as_float, "unit is not stated by the workbook"),
    Field("recast_time", "BO", "workbook-field", as_float, "unit is not stated by the workbook"),
    Field("magic_potency", "BT", "workbook-field", as_int, "raw workbook label; retail consumers may use a narrower name"),
    Field("damage_attribute", "CL", "workbook-field", as_int, "numeric damage attribute"),
    Field("damage_attribute_weight", "CM", "workbook-field", as_float, "numeric workbook percentage field"),
    Field("damage_element", "CN", "workbook-field", as_int, "numeric damage element"),
    Field("damage_element_weight", "CO", "workbook-field", as_float, "numeric workbook percentage field"),
    Field("target_self", "CZ", "workbook-field", as_bool, "raw target flag"),
    Field("target_ally", "DA", "workbook-field", as_bool, "raw target flag"),
    Field("target_enemy", "DB", "workbook-field", as_bool, "raw target flag"),
    Field("range_width", "DO", "analyst-custom", as_float, "provisional geometry"),
    Field("battle_command_type", "DP", "analyst-custom", as_int, "provisional taxonomy"),
    Field("hit_count", "DQ", "analyst-custom", as_int, "provisional hit count"),
    Field("rotation_pi", "DR", "analyst-custom", as_float, "provisional geometry"),
    Field("rotation_note", "DS", "analyst-note", as_text, "lead only"),
    Field("rotation_radians", "DT", "cached-formula", as_float, "cached DR multiplied by pi"),
    Field("cone_angle_pi", "DV", "analyst-custom", as_float, "provisional geometry"),
    Field("cone_note", "DW", "analyst-note", as_text, "lead only"),
    Field("cone_angle_radians", "DX", "cached-formula", as_float, "cached DV multiplied by pi"),
    Field("main_target_mask", "DY", "formula-or-override", as_int, "semantics unresolved"),
    Field("valid_target_mask", "DZ", "formula-or-override", as_int, "semantics unresolved"),
    Field("aoe_type", "EB", "formula-or-override", as_int, "provisional geometry taxonomy"),
    Field("aoe_target", "EC", "cached-formula", as_int, "provisional target taxonomy"),
    Field("height", "ED", "analyst-custom", as_float, "provisional geometry"),
    Field("text_id", "EE", "analyst-custom", as_int, "mapping not independently corroborated"),
    Field("cast_type", "EG", "formula-or-override", as_int, "header explicitly records uncertain meanings"),
    Field("knockback_id", "EI", "analyst-custom", as_int, "mapping not independently corroborated"),
    Field("interpreted_command_type_code", "EK", "formula-or-override", as_int, "depends on analyst taxonomy and unfinished weapon-skill list"),
    Field("interpreted_command_type", "EM", "cached-formula", as_text, "depends on analyst taxonomy and unfinished weapon-skill list"),
    Field("resistable", "EO", "formula-or-override", as_int, "derived from analyst command taxonomy"),
)

WEAPON_SKILL_FIELDS = (
    Field("hits_self", "C", "unfinished-analyst-table", as_bool, "lead only"),
    Field("hits_allies", "D", "unfinished-analyst-table", as_bool, "lead only"),
    Field("hits_enemies", "E", "unfinished-analyst-table", as_bool, "lead only"),
    Field("aoe_type", "F", "unfinished-analyst-table", as_int, "1 circle, 2 cone, 4 line per header"),
    Field("aoe_location", "G", "unfinished-analyst-table", as_int, "1 target, 2 self per header"),
    Field("unused", "H", "unfinished-analyst-table", as_int, "uninterpreted"),
    Field("resistable_code", "I", "unfinished-analyst-table", as_int, "header is uncertain"),
    Field("deals_damage", "J", "unfinished-analyst-table", as_int, "provisional damage flag"),
)


def cell_text(cell: ET.Element) -> str:
    return "\n".join(
        "".join(paragraph.itertext())
        for paragraph in cell.findall(".//text:p", NS)
    )


def read_cell(cell: ET.Element) -> dict[str, str]:
    result = {"display": cell_text(cell)}
    value_type = cell.get(VALUE_TYPE)
    if value_type:
        result["value_type"] = value_type
        stored = cell.get(VALUE_ATTRS.get(value_type, ""))
        if stored is not None:
            result["stored_value"] = stored
    formula = cell.get(FORMULA)
    if formula:
        result["formula"] = formula
    return result


def read_row(row: ET.Element) -> list[dict[str, str]]:
    cells: list[dict[str, str]] = []
    accepted = {
        f"{{{NS['table']}}}table-cell",
        f"{{{NS['table']}}}covered-table-cell",
    }
    for cell in row:
        if cell.tag not in accepted:
            continue
        value = read_cell(cell)
        repeat = int(cell.get(COL_REPEAT, "1"))
        remaining = MAX_COLUMNS - len(cells)
        if remaining <= 0:
            break
        cells.extend([value] * min(repeat, remaining))
    return cells


def read_tables(
    root: ET.Element,
) -> tuple[dict[str, list[tuple[int, list[dict[str, str]]]]], dict[str, bool]]:
    tables: dict[str, list[tuple[int, list[dict[str, str]]]]] = {}
    visibility: dict[str, bool] = {}
    for table in root.findall(".//table:table", NS):
        name = table.get(TABLE_NAME)
        if not name:
            continue
        rows: list[tuple[int, list[dict[str, str]]]] = []
        physical_row = 1
        for row in table.findall(".//table:table-row", NS):
            values = read_row(row)
            repeat = int(row.get(ROW_REPEAT, "1"))
            if not any(cell.get("display") for cell in values) and repeat > 1:
                physical_row += repeat
                continue
            rows.extend((physical_row + offset, values) for offset in range(repeat))
            physical_row += repeat
        tables[name] = rows
        visibility[name] = table.get(TABLE_DISPLAY, "true") != "false"
    return tables, visibility


def get_cell(row: list[dict[str, str]], column: str) -> dict[str, str]:
    index = column_index(column)
    return row[index] if index < len(row) else {"display": ""}


def normalize_fields(
    row: list[dict[str, str]], fields: tuple[Field, ...]
) -> tuple[dict, dict, dict, dict]:
    raw: dict[str, str | None] = {}
    normalized: dict[str, object] = {}
    formulas: dict[str, str] = {}
    issues: dict[str, str] = {}
    for field in fields:
        cell = get_cell(row, field.column)
        displayed = cell.get("display", "")
        raw[field.name] = displayed if displayed != "" else None
        try:
            normalized[field.name] = field.normalize(displayed)
        except ValueError as exc:
            normalized[field.name] = None
            issues[field.name] = str(exc)
        if cell.get("formula"):
            formulas[field.name] = cell["formula"]
    return raw, normalized, formulas, issues


def workbook_metadata(meta_root: ET.Element) -> dict[str, object]:
    def find_text(path: str) -> str | None:
        element = meta_root.find(path, NS)
        return element.text if element is not None else None

    statistics = meta_root.find(".//meta:document-statistic", NS)
    stats = {}
    if statistics is not None:
        prefix = f"{{{NS['meta']}}}"
        stats = {
            key.removeprefix(prefix): int(value)
            for key, value in statistics.attrib.items()
        }
    return {
        "saved_at": find_text(".//dc:date"),
        "generator": find_text(".//meta:generator"),
        "editing_duration": find_text(".//meta:editing-duration"),
        "editing_cycles": as_int(find_text(".//meta:editing-cycles") or ""),
        "document_statistics": stats,
    }


def formula_cell_count(table: ET.Element) -> int:
    total = 0
    for row in table.findall(".//table:table-row", NS):
        row_repeat = int(row.get(ROW_REPEAT, "1"))
        for cell in row.findall("table:table-cell", NS):
            if cell.get(FORMULA):
                total += row_repeat * int(cell.get(COL_REPEAT, "1"))
    return total


def build_document(source: Path) -> dict[str, object]:
    with zipfile.ZipFile(source) as archive:
        content_root = ET.fromstring(archive.read("content.xml"))
        meta_root = ET.fromstring(archive.read("meta.xml"))

    tables, visibility = read_tables(content_root)
    if "Command" not in tables or "Sheet2" not in tables:
        raise ValueError("expected Command and Sheet2 sheets")
    command_rows = tables["Command"]
    weapon_rows = tables["Sheet2"]
    command_table = next(
        table
        for table in content_root.findall(".//table:table", NS)
        if table.get(TABLE_NAME) == "Command"
    )
    if len(command_rows) < 4 or get_cell(command_rows[0][1], "B")["display"] != "Id":
        raise ValueError("Command sheet header layout changed")
    if len(weapon_rows) < 4 or get_cell(weapon_rows[0][1], "B")["display"] != "WS id":
        raise ValueError("Sheet2 header layout changed")

    weapon_by_id: dict[int, list[dict[str, object]]] = defaultdict(list)
    for source_row, row in weapon_rows[3:]:
        identifier = as_int(get_cell(row, "B").get("display", ""))
        if identifier is None:
            continue
        raw, normalized, _, issues = normalize_fields(row, WEAPON_SKILL_FIELDS)
        weapon_by_id[identifier].append(
            {
                "source_row": source_row,
                "raw": raw,
                "normalized": normalized,
                "normalization_issues": issues,
            }
        )

    records = []
    coverage = Counter()
    formula_count = 0
    normalization_issue_counts = Counter()
    command_ids = set()
    for source_row, row in command_rows[3:]:
        identifier = as_int(get_cell(row, "B").get("display", ""))
        if identifier is None:
            continue
        if identifier in command_ids:
            raise ValueError(f"duplicate command id {identifier}")
        command_ids.add(identifier)
        raw, normalized, formulas, issues = normalize_fields(row, FIELDS)
        for name, value in raw.items():
            if value is not None:
                coverage[name] += 1
        formula_count += sum(
            1 for cell in row if cell.get("formula")
        )
        normalization_issue_counts.update(issues.keys())
        record = {
            "source_row": source_row,
            "raw": raw,
            "normalized": normalized,
            "cached_formulas": formulas,
            "normalization_issues": issues,
            "unfinished_weapon_skill_rows": weapon_by_id.get(identifier, []),
        }
        records.append(record)

    weapon_counts = Counter(
        as_int(get_cell(row, "B").get("display", ""))
        for _, row in weapon_rows[3:]
        if get_cell(row, "B").get("display", "") != ""
    )
    duplicates = {
        str(identifier): count
        for identifier, count in sorted(weapon_counts.items())
        if identifier is not None and count > 1
    }
    field_map = [
        {
            "name": field.name,
            "sheet": "Command",
            "column": field.column,
            "header": get_cell(command_rows[0][1], field.column).get("display", ""),
            "layer": field.layer,
            "normalization": field.normalize.__name__,
            "boundary": field.boundary,
        }
        for field in FIELDS
    ]
    field_map.extend(
        {
            "name": f"unfinished_weapon_skill.{field.name}",
            "sheet": "Sheet2",
            "column": field.column,
            "header": get_cell(weapon_rows[0][1], field.column).get("display", ""),
            "layer": field.layer,
            "normalization": field.normalize.__name__,
            "boundary": field.boundary,
        }
        for field in WEAPON_SKILL_FIELDS
    )
    return {
        "schema_version": 1,
        "evidence": {
            "class": "historical-research",
            "strength": "provisional-secondary",
            "boundary": (
                "Workbook fields may fill unresolved fields but do not override retail "
                "captures, client data, client scripts, or retail video. Analyst notes "
                "and the unfinished weapon-skill table are leads."
            ),
        },
        "source": {
            "source_id": "historical-battlecommand-workbook",
            "member": "BattleCommand.ods",
            "sheet_visibility": visibility,
            "embedded_metadata": workbook_metadata(meta_root),
        },
        "field_map": field_map,
        "summary": {
            "command_records": len(records),
            "unique_command_ids": len(command_ids),
            "command_sheet_formula_cells": formula_cell_count(command_table),
            "mapped_command_record_formula_cells": formula_count,
            "cached_formula_error_cells": sum(
                1
                for _, row in command_rows
                for cell in row
                if cell.get("display") == "#VALUE!"
            ),
            "unfinished_weapon_skill_rows": sum(weapon_counts.values()),
            "unfinished_weapon_skill_unique_ids": len(weapon_counts),
            "commands_without_unfinished_weapon_skill_row": (
                len(command_ids) - len(weapon_counts)
            ),
            "unfinished_weapon_skill_duplicate_ids": duplicates,
            "field_nonempty_counts": dict(sorted(coverage.items())),
            "normalization_issue_counts": dict(sorted(normalization_issue_counts.items())),
            "unresolved_fields": [
                "animation_type_capture_disagreement",
                "cast_and_recast_units",
                "target_mask_semantics",
                "timing_semantics_beyond_raw_values",
                "status_effect_semantics_from_analyst_notes",
                "damage_semantics_from_unfinished_analyst_table",
                "analyst_command_taxonomy",
                "formula_cache_freshness",
                "auxiliary_command_region_ER_to_JB_rows_1061_to_1063",
            ],
        },
        "records": records,
    }


def render_document(document: dict[str, object]) -> bytes:
    return (json.dumps(document, ensure_ascii=True, indent=2) + "\n").encode("ascii")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rendered = render_document(build_document(args.source))
    if args.check:
        if not args.out.exists() or args.out.read_bytes() != rendered:
            print(f"stale: {display_path(args.out)}", file=sys.stderr)
            return 1
        print(f"up to date: {display_path(args.out)}")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(rendered)
    print(f"wrote {display_path(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
