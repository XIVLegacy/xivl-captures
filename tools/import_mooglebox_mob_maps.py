#!/usr/bin/env python3
"""Import the preserved Mooglebox regional mob-map HTML snapshots.

The source pages embed one OpenLayers marker per mob camp. This importer
extracts the marker order and popup fields without depending on a browser or
third-party HTML parser. It intentionally retains slash-separated labels as
candidate lists: the source assigns one map slot to several possible mobs and
does not identify which candidate occupied the slot.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = REPO_ROOT / "sources" / "mooglebox-regional-mob-maps" / "objects"
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "studies"
    / "mooglebox-regional-mob-maps"
    / "derived"
    / "marker-records.csv"
)

REGIONS = (
    {
        "region": "Coerthas",
        "filename": "coerthas.html",
        "count": 39,
    },
    {
        "region": "Black Shroud",
        "filename": "blackshroud.html",
        "count": 74,
    },
    {
        "region": "La Noscea",
        "filename": "la-noscea.html",
        "count": 63,
    },
    {
        "region": "Thanalan",
        "filename": "thanalan.html",
        "count": 78,
    },
)

ORIGINAL_URLS = {
    "coerthas.html": "http://www.mooglebox.com/coerthas/index.php",
    "blackshroud.html": "http://www.mooglebox.com/blackshroud/index.php",
    "la-noscea.html": "http://www.mooglebox.com/la-noscea/index.php",
    "thanalan.html": "http://www.mooglebox.com/thanalan/index.php",
}

SNAPSHOT_URLS = {
    "coerthas.html": (
        "https://web.archive.org/web/20120602044520/"
        "http://mooglebox.com/coerthas/index.php"
    ),
    "blackshroud.html": (
        "https://web.archive.org/web/20120605230901/"
        "http://mooglebox.com/blackshroud/index.php"
    ),
    "la-noscea.html": (
        "https://web.archive.org/web/20120702115825/"
        "http://www.mooglebox.com/la-noscea/index.php"
    ),
    "thanalan.html": (
        "https://web.archive.org/web/20120605034042/"
        "http://mooglebox.com/thanalan/index.php"
    ),
}

EXPECTED_SOURCE_SHA256 = {
    "blackshroud.html": "84bca3963ae4009e074505bd81d8e42a530ab385134ba58064228c86e63baa35",
    "coerthas.html": "4cc3876f74d17009eda2ed76435bb5e1b84ed1cbd899bc1a766ba41db63932d7",
    "la-noscea.html": "2336eefc06008562b3885db2e2f18c90a8845825740d5c8b36c2429acf6fe589",
    "thanalan.html": "d7ad7fe8432fdf63c23dbdb53641b4f131e610d772d608d430691e3488524d88",
}

CSV_COLUMNS = (
    "region",
    "marker_order",
    "label_raw",
    "parsed_candidates",
    "level_text",
    "level_min",
    "level_max",
    "amount_text",
    "amount_min",
    "amount_max",
    "amount_approximation",
    "map_x",
    "map_y",
    "coordinates",
    "coordinate_x",
    "coordinate_y",
    "coordinate_note",
    "aggression_marker",
    "snapshot_url",
    "original_url",
    "shared_slot_verdict",
)

MARKER_RE = re.compile(
    r"coords\s*=\s*new\s+OpenLayers\.LonLat\(\s*"
    r"(?P<map_x>[-+]?\d+(?:\.\d+)?)\s*,\s*"
    r"(?P<map_y>[-+]?\d+(?:\.\d+)?)\s*\).*?"
    r"popupContentHTML\s*=\s*'(?P<payload>(?:\\.|[^'])*)';",
    re.DOTALL,
)
LABEL_RE = re.compile(r"<th\b[^>]*>(?P<label>.*?)</th>", re.DOTALL)
LEVEL_RE = re.compile(r"<p>\s*Level:\s*(?P<value>.*?)\s*</p>", re.DOTALL)
AMOUNT_RE = re.compile(r"<p>\s*Amount:\s*(?P<value>.*?)\s*</p>", re.DOTALL)
COORDINATES_RE = re.compile(r"<p>\s*Coords:\s*(?P<value>.*?)\s*</p>", re.DOTALL)
AGGRESSION_RE = re.compile(r"images/maps/(?P<value>[01])\.png")
RANGE_RE = re.compile(r"^(?P<low>\d+)(?:-(?P<high>\d+))?$")
COORDINATE_VALUE_RE = re.compile(
    r"^(?P<x>[-+]?\d+(?:\.\d+)?)\s*,\s*"
    r"(?P<y>[-+]?\d+(?:\.\d+)?)(?:\s+(?P<note>.*))?$"
)
TAG_RE = re.compile(r"<[^>]+>")


class ImportError(RuntimeError):
    """Raised when a pinned source cannot be parsed deterministically."""


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def decode_javascript_text(value: str) -> str:
    """Decode the small escaped subset used inside popup JavaScript strings."""

    value = html.unescape(value)
    return re.sub(r"\\([\\'\"])", r"\1", value)


def popup_field(payload: str, pattern: re.Pattern[str], name: str) -> str:
    match = pattern.search(payload)
    if not match:
        raise ImportError(f"marker popup is missing {name}")
    return decode_javascript_text(match.group("value"))


def parse_bound(value: str, field: str) -> tuple[str, str]:
    value = value.strip()
    if not value:
        return "", ""
    match = RANGE_RE.fullmatch(value)
    if not match:
        raise ImportError(f"unsupported {field} value {value!r}")
    low = match.group("low")
    high = match.group("high") or low
    return low, high


def parse_coordinates(value: str) -> tuple[str, str, str, str]:
    visible = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    visible = TAG_RE.sub("", visible).strip()
    match = COORDINATE_VALUE_RE.fullmatch(visible)
    if not match:
        raise ImportError(f"unsupported coordinates value {value!r}")
    return (
        visible,
        match.group("x"),
        match.group("y"),
        (match.group("note") or "").strip(),
    )


def parse_marker(
    region: str,
    marker_order: int,
    match: re.Match[str],
    filename: str,
) -> dict[str, str]:
    payload = html.unescape(match.group("payload"))
    label_match = LABEL_RE.search(payload)
    if not label_match:
        raise ImportError(f"{filename} marker {marker_order} is missing label")
    label = decode_javascript_text(label_match.group("label")).strip()
    if not label:
        raise ImportError(f"{filename} marker {marker_order} has an empty label")

    candidates = [candidate.strip() for candidate in label.split("/")]
    if any(not candidate for candidate in candidates):
        raise ImportError(f"{filename} marker {marker_order} has an empty candidate")

    level_text = popup_field(payload, LEVEL_RE, "level").strip()
    level_min, level_max = parse_bound(level_text, "level")
    amount_text = popup_field(payload, AMOUNT_RE, "amount").strip()
    amount_approximation = "unresolved"
    amount_value = amount_text
    if amount_value.startswith("~"):
        amount_approximation = "approximate"
        amount_value = amount_value[1:].strip()
    elif amount_value:
        amount_approximation = "exact"
    amount_min, amount_max = parse_bound(amount_value, "amount")

    coordinates_raw = popup_field(payload, COORDINATES_RE, "coordinates")
    coordinates, coordinate_x, coordinate_y, coordinate_note = parse_coordinates(
        coordinates_raw
    )
    aggression_match = AGGRESSION_RE.search(payload)
    if not aggression_match:
        raise ImportError(
            f"{filename} marker {marker_order} is missing aggression marker"
        )

    return {
        "region": region,
        "marker_order": str(marker_order),
        "label_raw": label,
        "parsed_candidates": json.dumps(
            candidates, ensure_ascii=False, separators=(",", ":")
        ),
        "level_text": level_text,
        "level_min": level_min,
        "level_max": level_max,
        "amount_text": amount_text,
        "amount_min": amount_min,
        "amount_max": amount_max,
        "amount_approximation": amount_approximation,
        "map_x": match.group("map_x").strip(),
        "map_y": match.group("map_y").strip(),
        "coordinates": coordinates,
        "coordinate_x": coordinate_x,
        "coordinate_y": coordinate_y,
        "coordinate_note": coordinate_note,
        "aggression_marker": aggression_match.group("value"),
        "snapshot_url": SNAPSHOT_URLS[filename],
        "original_url": ORIGINAL_URLS[filename],
        "shared_slot_verdict": (
            "unresolved_shared_slot" if len(candidates) > 1 else "single_label"
        ),
    }


def parse_html(raw: bytes, region: str, filename: str) -> list[dict[str, str]]:
    text = raw.decode("utf-8")
    matches = list(MARKER_RE.finditer(text))
    rows = [
        parse_marker(region, marker_order, match, filename)
        for marker_order, match in enumerate(matches, start=1)
    ]
    expected = next(item["count"] for item in REGIONS if item["region"] == region)
    if len(rows) != expected:
        raise ImportError(f"{filename} parsed {len(rows)} markers; expected {expected}")
    return rows


def load_rows(source_dir: Path, verify_hashes: bool = True) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for config in REGIONS:
        path = source_dir / config["filename"]
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise ImportError(f"cannot read {path}: {exc}") from exc
        if verify_hashes:
            actual = sha256_bytes(raw)
            expected = EXPECTED_SOURCE_SHA256[config["filename"]]
            if actual != expected:
                raise ImportError(
                    f"{config['filename']} SHA-256 mismatch: expected {expected}, got {actual}"
                )
        rows.extend(parse_html(raw, config["region"], config["filename"]))
    return rows


def render_csv(rows: list[dict[str, str]]) -> bytes:
    from io import StringIO

    stream = StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=CSV_COLUMNS, lineterminator="\n", extrasaction="raise"
    )
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def write_or_check(output: Path, expected: bytes, check: bool) -> int:
    if check:
        try:
            actual = output.read_bytes()
        except OSError as exc:
            print(f"STALE: {output}: {exc}")
            return 1
        if actual != expected:
            print(f"STALE: {output}")
            return 1
        print(f"OK: {output}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(expected)
    print(f"WROTE: {output}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="directory containing the four preserved HTML objects",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="marker CSV path",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify deterministic output without writing",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        rows = load_rows(args.source_dir)
        output = render_csv(rows)
        return write_or_check(args.output, output, args.check)
    except (ImportError, UnicodeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
