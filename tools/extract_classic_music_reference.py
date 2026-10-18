"""Reproduce the music crosswalk from the exact retained Music HTML."""

from __future__ import annotations

import argparse
import csv
import hashlib
from html.parser import HTMLParser
import io
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources/classic-music-reference/manifest.yaml"
OUTPUT = ROOT / "studies/classic-music-reference/derived/music-crosswalk.csv"
FIELDS = (
    "music_id",
    "source_line",
    "source_name",
    "source_usage",
    "title_confidence",
    "usage_confidence",
    "wiki_version_scope",
    "numeric_id_evidence",
    "computed_resource_key",
    "resource_availability",
)


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.table = None
        self.row = None
        self.cell = None
        self.row_line = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.table = []
        elif self.table is not None:
            if tag == "tr":
                self.row = []
                self.row_line = self.getpos()[0]
            elif tag in ("td", "th"):
                self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append("".join(self.cell).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.table.append((self.row_line, self.row))
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def confidence(name: str, usage: str) -> tuple[str, str, str]:
    title = "secondary-named"
    if not name:
        title = "unresolved-placeholder"
    elif name == "???":
        title = "unresolved-unknown"
    elif "?" in name:
        title = "secondary-tentative"
    elif name == "Opening Movie music":
        title = "descriptive-only"

    context = "secondary"
    if not usage:
        context = "unspecified"
    elif usage == "Placeholder" or usage.startswith(("//", "Removed in")):
        context = "secondary-note-only"
    elif "Needs more info" in usage:
        context = "secondary-incomplete"

    version = "unspecified"
    if "Removed in post-launch versions." in usage:
        version = "removed-post-launch-claim"
    elif "before patch 1.18" in usage:
        version = "pre-1.18-claim"
    elif "from patch 1.18 onward" in usage:
        version = "1.18-onward-claim"
    elif "from patch 1.19 onward" in usage:
        version = "1.19-onward-claim"
    return title, context, version


def extract(path: Path) -> list[dict]:
    manifest = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    member = manifest["provenance"]["inspected_html"]
    raw = path.read_bytes()
    if (
        len(raw) != member["size_bytes"]
        or hashlib.sha256(raw).hexdigest() != member["sha256"]
    ):
        raise ValueError("HTML size/SHA-256 does not match the retained source")
    text = raw.decode("utf-8")
    revision = str(manifest["provenance"]["revision_id"])
    for field in ("wgCurRevisionId", "wgRevisionId"):
        if re.findall(r'"' + field + r'":(\d+)', text) != [revision]:
            raise ValueError("HTML revision does not match the source manifest")
    parser = TableParser()
    parser.feed(text)
    parser.close()
    tables = [
        t for t in parser.tables if t and t[0][1] == ["Music ID", "Name", "Usage"]
    ]
    if len(tables) != 1:
        raise ValueError("Expected one Music ID / Name / Usage table")
    rows = []
    for line, cells in tables[0][1:]:
        if len(cells) != 3:
            raise ValueError("Expected three cells per music row")
        id_text, name, usage = cells
        music_id = int(id_text)
        title, context, version = confidence(name, usage)
        numeric = "wiki-only"
        # Selected intersections: the study evidence map, Retail numeric intersections.
        if music_id in (7, 25, 61):
            numeric = "shipped-lua-reference"
        elif music_id in (13, 57, 83):
            numeric = "retail-packet-request"
        rows.append(
            dict(
                zip(
                    FIELDS,
                    (
                        music_id,
                        line,
                        name,
                        usage,
                        title,
                        context,
                        version,
                        numeric,
                        f"0x{0x07FE0000 + music_id:08X}",
                        "not-checked",
                    ),
                )
            )
        )
    if [row["music_id"] for row in rows] != list(range(1, 110)):
        raise ValueError("Expected IDs 1 through 109 exactly once in source order")
    return rows


def render(rows: list[dict]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--html", type=Path, required=True, help="exact retained music.html"
    )
    parser.add_argument("--check", action="store_true", help="compare without writing")
    args = parser.parse_args()
    try:
        expected = render(extract(args.html))
        if args.check:
            if not OUTPUT.exists() or OUTPUT.read_bytes() != expected:
                raise ValueError("music-crosswalk.csv is missing or stale")
        else:
            OUTPUT.write_bytes(expected)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: retained HTML identity/revision and 109-row music crosswalk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
