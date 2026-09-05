"""Extract first observed NPC and object spawn identities and positions.

Join s2c opcodes 0x00ca, 0x00cc, and 0x00ce by the actor id at offset 8.
Position floats are at offsets 24, 28, 32, and 36. Zone tags remain verbatim.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import struct
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _json_io import write_json  # noqa: E402

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from extract_payload_samples import walk_capture_payloads  # type: ignore
from extract_observations import default_corpus_paths  # type: ignore

# Bump when extraction changes output; record the version in pipelines/*.yaml and derived/*.meta.yaml.
GENERATOR_VERSION = "2"

DEFAULT_OUT = Path(__file__).parent.parent.parent / "derived" / "spawn_observations.json"
DEFAULT_CSV_OUT = DEFAULT_OUT.with_suffix(".csv")

# This is the public row contract. Keep it explicit so CSV column order does
# not depend on dictionary insertion order or a future JSON-only field.
RECORD_FIELDS = (
    "capture",
    "actorId",
    "instanceName",
    "baseClass",
    "classPath",
    "zoneTag",
    "x",
    "y",
    "z",
    "rotation",
    "hadInstantiate",
    "hadAddActor",
)
CSV_FIELDS = RECORD_FIELDS
_FLOAT_DIGITS = {"x": 3, "y": 3, "z": 3, "rotation": 4}
_BOOLEAN_FIELDS = {"hadInstantiate", "hadAddActor"}

OP_ADD, OP_INST, OP_POS = 202, 204, 206  # 0x00ca / 0x00cc / 0x00ce
# Wire fact: instance-name zone tags look like `_fst0Twn01a_` or `_wil0Fld03_`.
ZONE_RE = re.compile(r"_((?:fst|roc|sea|wil|ocn|lak|prv|ori|non)\d[A-Za-z]+\d+[a-z]?)_")
# Wire quirk: the wire prepends sync/length glyphs before the printable name.
_NAME_LSTRIP = "&%3=(+*)/-#$ !\"'0123456789"


def _ascii_strings(b: bytes, minlen: int = 3) -> list[str]:
    return [m.decode("latin1") for m in re.findall(rb"[\x20-\x7e]{%d,}" % minlen, b)]


def walk_capture_spawns(path: Path) -> list[dict]:
    """One record per (actorId) with a position, for a single capture."""
    pos: dict[int, tuple[float, float, float, float]] = {}
    inst: dict[int, tuple[str, str, str, str]] = {}
    add: set[int] = set()
    for r in walk_capture_payloads(path):
        if r["direction"] != "s2c":
            continue
        b = bytes.fromhex(r["bytes"])
        if len(b) < 12:
            continue
        aid = int.from_bytes(b[8:12], "little")
        op = r["opcode"]
        if op == OP_ADD:
            add.add(aid)
        elif op == OP_INST:
            ss = _ascii_strings(b)
            name = ss[0].lstrip(_NAME_LSTRIP) if ss else ""
            base = ss[1] if len(ss) > 1 else ""
            cpath = next((s for s in ss if s.startswith("/Chara")), "")
            zt = ""
            if ss:
                m = ZONE_RE.search(ss[0])
                if m:
                    zt = m.group(1)
            inst[aid] = (name, base, cpath, zt)
        elif op == OP_POS and len(b) >= 40:
            if aid not in pos:  # Keep the first observed placement for each actor.
                pos[aid] = struct.unpack_from("<ffff", b, 24)

    records = []
    for aid, (x, y, z, rot) in pos.items():
        name, base, cpath, zt = inst.get(aid, ("", "", "", ""))
        records.append(
            {
                "capture": path.name,
                "actorId": f"0x{aid:08x}",
                "instanceName": name,
                "baseClass": base,
                "classPath": cpath,
                "zoneTag": zt,
                "x": round(x, 3),
                "y": round(y, 3),
                "z": round(z, 3),
                "rotation": round(rot, 4),
                "hadInstantiate": aid in inst,
                "hadAddActor": aid in add,
            }
        )
    return records


def _csv_value(field: str, value: object) -> str:
    """Render one record value using a stable, locale-independent spelling."""
    if field in _BOOLEAN_FIELDS:
        if not isinstance(value, bool):
            raise ValueError(f"{field} must be boolean")
        return "true" if value else "false"
    if field in _FLOAT_DIGITS:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field} must be numeric")
        return f"{float(value):.{_FLOAT_DIGITS[field]}f}"
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value


def render_csv(records: list[dict]) -> bytes:
    """Render sorted spawn records as UTF-8 CSV with LF endings."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=RECORD_FIELDS,
        extrasaction="raise",
        lineterminator="\n",
    )
    writer.writeheader()
    for record in records:
        if not isinstance(record, dict) or set(record) != set(RECORD_FIELDS):
            raise ValueError("record fields differ from the stable CSV fields")
        writer.writerow({field: _csv_value(field, record[field]) for field in RECORD_FIELDS})
    return output.getvalue().encode("utf-8")


def write_csv(path: Path, records: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_csv(records))


def validate_csv(json_path: Path, csv_path: Path) -> list[str]:
    """Validate a retained CSV against the JSON record order and values."""
    errors: list[str] = []
    try:
        document = json.loads(Path(json_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"invalid spawn_observations JSON: {exc}"]
    records = document.get("records") if isinstance(document, dict) else None
    if not isinstance(records, list):
        return ["spawn_observations JSON has no records list"]
    try:
        raw = Path(csv_path).read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"invalid spawn_observations CSV: {exc}"]
    if "\r" in text:
        errors.append("spawn_observations CSV contains CR line endings")
    try:
        rows = list(csv.reader(io.StringIO(text, newline="")))
    except csv.Error as exc:
        return [f"invalid spawn_observations CSV: {exc}"]
    if not rows:
        return ["spawn_observations CSV is empty"]
    if rows[0] != list(RECORD_FIELDS):
        errors.append("spawn_observations CSV header differs from the stable record fields")
    data_rows = rows[1:]
    if len(data_rows) != len(records):
        errors.append(
            f"spawn_observations CSV has {len(data_rows)} records; JSON has {len(records)}"
        )
    try:
        canonical = render_csv(records)
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"spawn_observations JSON records are invalid: {exc}")
    else:
        if raw != canonical:
            errors.append("spawn_observations CSV bytes are not canonical")
    for index, record in enumerate(records[:len(data_rows)]):
        row = data_rows[index]
        if len(row) != len(RECORD_FIELDS):
            errors.append(
                f"spawn_observations CSV row {index + 2} has {len(row)} fields; "
                f"expected {len(RECORD_FIELDS)}"
            )
            continue
        try:
            expected = [_csv_value(field, record[field]) for field in RECORD_FIELDS]
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"spawn_observations JSON record {index} is invalid: {exc}")
            continue
        if row != expected:
            errors.append(f"spawn_observations CSV row {index + 2} differs from JSON")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract observed spawn positions from the pcap corpus.")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path.")
    ap.add_argument("--csv-out", default=None, help="Output CSV path (defaults beside --out).")
    args = ap.parse_args()

    records: list[dict] = []
    capture_count = 0
    for p in default_corpus_paths():
        if not p.is_file():
            continue
        capture_count += 1
        records.extend(walk_capture_spawns(p))

    records.sort(key=lambda r: (r["capture"], r["actorId"]))
    positioned = len(records)
    identified = sum(1 for r in records if r["hadInstantiate"])
    zone_tagged = sum(1 for r in records if r["zoneTag"])

    out = {
        "version": "1.23b",
        "source": "s2c 0x00ca/0x00cc/0x00ce joined by actorId; first placement per actor",
        "captureCount": capture_count,
        "positionedSpawns": positioned,
        "withInstantiate": identified,
        "withZoneTag": zone_tagged,
        "records": records,
    }
    out_path = Path(args.out)
    csv_path = Path(args.csv_out) if args.csv_out else out_path.with_suffix(".csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, out)
    write_csv(csv_path, records)
    print(f"wrote {out_path}")
    print(f"wrote {csv_path}")
    print(f"  captures: {capture_count}")
    print(f"  positioned spawns: {positioned}  (identified {identified}, zone-tagged {zone_tagged})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
