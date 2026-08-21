#!/usr/bin/env python3
"""Generate packet scenario views from repository-owned evidence.

Scenario membership and hashes come from sources/pcap-1.23b/manifest.yaml.
Numeric observations join the promoted opcode-name mapping by opcode and
direction. Each scenario emits README.md, evidence-map.md, and
file-inventory.csv under catalog/scenarios/<id>/.

Usage:
    python tools/build_scenario_views.py
    python tools/build_scenario_views.py --check   # fail if anything is stale
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "derived"
SOURCES_DIR = REPO_ROOT / "sources" / "pcap-1.23b"
CORPUS_MANIFEST = SOURCES_DIR / "manifest.yaml"
# Numeric facts use this repo's canonical decode; opcode names use the promoted mapping's `source` field.
OPCODE_NAMES_JSON = DATA_DIR / "opcode_names.json"
OBSERVATIONS_JSON = DATA_DIR / "observations.json"
CAPTURES_DIR = Path(os.environ.get("XIVL_PCAP_OBJECTS_DIR", str(SOURCES_DIR / "objects")))
SCENARIOS_DIR = REPO_ROOT / "catalog" / "scenarios"

# Logical repo-relative label used in prose and CSV columns; CAPTURES_DIR does the actual resolution.
SIBLING_LABEL = "sources/pcap-1.23b/objects"
CORPUS_ABSENT = os.environ.get("XIVL_CORPUS_ABSENT") == "1"


class _NoAlias(yaml.SafeDumper):
    """Never emit YAML anchors or aliases for shared lists."""

    def ignore_aliases(self, data):  # noqa: D401 - simple override
        return True


def _dump(obj) -> str:
    return yaml.dump(
        obj, Dumper=_NoAlias, sort_keys=False, default_flow_style=False,
        allow_unicode=True, width=100,
    )


# Scenario definitions come from sources/pcap-1.23b/manifest.yaml; members resolve under CAPTURES_DIR and facets are validated.
FACET_KEYS = ("system", "city_state", "progression_track", "zones")


def load_corpus_manifest() -> dict:
    if not CORPUS_MANIFEST.exists():
        print(f"ERROR: corpus manifest not found at {CORPUS_MANIFEST}", file=sys.stderr)
        raise SystemExit(2)
    with CORPUS_MANIFEST.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_scenarios(manifest: dict) -> list[dict]:
    """Require scenarios to partition the manifest and match disk hashes."""
    mpath = CORPUS_MANIFEST
    manifest_members: list[dict] = manifest.get("members") or []
    scenarios: list[dict] = manifest.get("scenarios") or []

    errors: list[str] = []

    declared = {m["file"] for m in manifest_members}
    if len(declared) != len(manifest_members):
        errors.append(f"{mpath}: members list has duplicate file entries")

    scenario_members: list[str] = []
    seen_in_scenarios: dict[str, str] = {}
    for s in scenarios:
        for fn in s["members"]:
            scenario_members.append(fn)
            if fn in seen_in_scenarios:
                errors.append(
                    f"{mpath}: `{fn}` is claimed by both scenario "
                    f"`{seen_in_scenarios[fn]}` and `{s['id']}` (not a partition)"
                )
            else:
                seen_in_scenarios[fn] = s["id"]

    unclaimed = declared - set(scenario_members)
    if unclaimed:
        errors.append(
            f"{mpath}: member(s) not claimed by any scenario: {', '.join(sorted(unclaimed))}"
        )
    unlisted = set(scenario_members) - declared
    if unlisted:
        errors.append(
            f"{mpath}: scenario member(s) not present in the manifest `members` list: "
            f"{', '.join(sorted(unlisted))}"
        )

    for m in manifest_members:
        path = CAPTURES_DIR / m["file"]
        if not path.exists():
            if not CORPUS_ABSENT:
                errors.append(f"{mpath}: member `{m['file']}` has no file at {path}")
            continue
        actual = sha256_file(path)
        if actual != m["sha256"]:
            errors.append(
                f"{mpath}: sha256 mismatch for `{m['file']}` "
                f"(manifest {m['sha256']}, disk {actual})"
            )

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)

    return scenarios


BASE_TAGS = ["packet-capture", "pcap-reference", "patch-1.23b", "opcode-names"]

# Map observations.json inner_opcodes buckets to opcode_names.json direction labels.
DIRECTION_LABEL = {"c2s": "serverbound", "s2c": "clientbound"}


def load_inversion() -> dict:
    """Join numeric observations to mapping claims, grouped by pcap filename.

    A unique opcode-direction mapping applies to every local witness. Multiple
    service claimants require per-pcap attribution; missing claims fail.
    """
    obs = json.loads(OBSERVATIONS_JSON.read_text(encoding="utf-8"))
    mapping = json.loads(OPCODE_NAMES_JSON.read_text(encoding="utf-8"))

    by_key: dict[tuple[str, str], list[dict]] = {}
    for e in mapping["entries"]:
        by_key.setdefault((e["opcodeHex"], e["direction"]), []).append(e)

    inv: dict[str, list[dict]] = {}
    missing_key: set[tuple[str, str]] = set()
    unclaimed: list[tuple[str, str, str]] = []
    for bucket, direction in DIRECTION_LABEL.items():
        for hexv, rec in obs["inner_opcodes"][bucket].items():
            candidates = by_key.get((hexv, direction))
            if not candidates:
                missing_key.add((hexv, direction))
                continue
            local_observed = rec.get("observedIn") or []
            lengths = rec.get("subEventSizes") or []
            if len(candidates) == 1:
                cand = candidates[0]
                for pc in local_observed:
                    inv.setdefault(pc, []).append({
                        "hex": hexv,
                        "name": cand.get("name"),
                        "retail_class_name": cand.get("retail_class_name"),
                        "service": cand.get("service"),
                        "direction": direction,
                        "lengths": lengths,
                    })
                continue
            for pc in local_observed:
                claimants = [c for c in candidates if pc in (c.get("observedIn") or [])]
                if not claimants:
                    unclaimed.append((hexv, direction, pc))
                    continue
                for cand in claimants:
                    inv.setdefault(pc, []).append({
                        "hex": hexv,
                        "name": cand.get("name"),
                        "retail_class_name": cand.get("retail_class_name"),
                        "service": cand.get("service"),
                        "direction": direction,
                        "lengths": lengths,
                    })

    if missing_key or unclaimed:
        if missing_key:
            detail = ", ".join(f"{h} {d}" for h, d in sorted(missing_key))
            print("ERROR: opcode(s) observed locally with no entry in "
                  f"derived/opcode_names.json: {detail}. Re-promote the mapping "
                  "(tools/promote_opcode_names.py) or confirm the source catalog "
                  "covers them before re-running.", file=sys.stderr)
        if unclaimed:
            detail = ", ".join(f"{h} {d} {pc}" for h, d, pc in sorted(unclaimed))
            print("ERROR: opcode(s) with more than one service in "
                  "derived/opcode_names.json where no candidate's observedIn "
                  f"names the pcap: {detail}.", file=sys.stderr)
        raise SystemExit(2)

    return inv


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def member_stats(members: list[str], inv: dict) -> dict:
    """Per-member size/sha/opcode rollup, all from disk + the local join."""
    stats = {}
    manifest_members = {
        item["file"]: item for item in (load_corpus_manifest().get("members") or [])
    }
    for fn in members:
        path = CAPTURES_DIR / fn
        recs = inv.get(fn, [])
        hexes = sorted({r["hex"] for r in recs if r["hex"]},
                       key=lambda h: int(h, 16))
        svc = Counter(r["service"] for r in recs if r["service"])
        manifest_item = manifest_members[fn]
        stats[fn] = {
            "size": path.stat().st_size if path.exists() else manifest_item["size_bytes"],
            "sha256": sha256_file(path) if path.exists() else manifest_item["sha256"],
            "opcode_hexes": hexes,
            "service_mix": dict(svc),
            "records": recs,
        }
    return stats


def union_opcodes(stats: dict) -> list[dict]:
    """Distinct opcodes across a scenario's members: (hex, service, direction,
    name, retail_class_name, lengths-union), sorted by (service, hex)."""
    merged: dict[tuple, dict] = {}
    for fn, st in stats.items():
        for r in st["records"]:
            key = (r["hex"], r["service"], r["direction"])
            slot = merged.setdefault(key, {
                "hex": r["hex"], "service": r["service"], "direction": r["direction"],
                "name": r["name"], "retail_class_name": r["retail_class_name"],
                "lengths": set(),
            })
            slot["lengths"].update(r["lengths"])
    rows = []
    for v in merged.values():
        v["lengths"] = sorted(v["lengths"])
        rows.append(v)
    svc_order = {"lobby": 0, "world": 1, "map": 2, "backend": 3}
    rows.sort(key=lambda v: (svc_order.get(v["service"], 9),
                             int(v["hex"], 16) if v["hex"] else 0,
                             v["direction"] or ""))
    return rows


def scenario_search_hints(members: list[str], stats: dict) -> list[str]:
    """Return member names and receiver classes as scenario search anchors."""
    hints: set[str] = set()
    for fn in members:
        hints.add(fn.rsplit(".", 1)[0].replace("_", " "))
    for st in stats.values():
        for r in st["records"]:
            if r.get("retail_class_name"):
                hints.add(r["retail_class_name"].lower())
    return sorted(hints)


def fmt_int(n: int) -> str:
    return f"{n:,}"


@lru_cache(maxsize=1)
def mapping_source() -> str:
    """Read the promoted mapping's citation from the mapping itself."""
    mapping = json.loads(OPCODE_NAMES_JSON.read_text(encoding="utf-8"))
    return mapping["source"]


def render_readme(s: dict, stats: dict) -> str:
    members = s["members"]
    svc_total = Counter()
    for m in members:
        svc_total.update(stats[m]["service_mix"])
    lines = [f"# {s['title']}", "",
             "## What this scenario contains", "",
             s["blurb"], "",
             "This is a **packet-capture reference scenario**. The raw pcaps live in "
             f"this repo's shared `{SIBLING_LABEL}/` corpus; this view distils the opcode "
             "evidence those captures carry. Evidence tier: packet captures > video breakdown > "
             "wiki; this is packet evidence.", "",
             "## Load first", "",
             "- `evidence-map.md` - the per-capture opcode rollup, names "
             "from `derived/opcode_names.json`, plus caveats and gaps.",
             "- `file-inventory.csv` - one row per member pcap (bytes, "
             "sha256, observed opcodes).", "",
             "## Raw materials", ""]
    for m in members:
        st = stats[m]
        lines.append(f"- `{SIBLING_LABEL}/{m}` ({fmt_int(st['size'])} B, "
                     f"{len(st['opcode_hexes'])} opcodes).")
    lines += ["", "## Key entities/topics", ""]
    for tag in s["tags"]:
        lines.append(f"- {tag}")
    lines += ["", "## Gaps", "",
              "- This scenario carries opcode identity, direction, service, and payload "
              "lengths only - not decoded field semantics (those live in this repo's "
              "`derived/payload_layouts.json`).",
              f"- Service split across members: "
              f"{', '.join(f'{k} {v}' for k, v in sorted(svc_total.items()))}."]
    if s.get("caveat"):
        lines.append(f"- Caveat: {s['caveat']}")
    lines += ["", "## Next agent steps", "",
              "- Use `file-inventory.csv` to pick the member pcap that "
              f"isolates the opcode you need, then open it from `{SIBLING_LABEL}/` "
              "for byte-level work.",
              "- Cross-check any opcode here against its full entry in this "
              "repo's `derived/opcode_names.json` before promoting a claim; that "
              f"mapping was promoted from {mapping_source()} and carries no "
              "freshness promise against the sibling catalog.", ""]
    return "\n".join(lines)


def render_evidence_map(s: dict, stats: dict, opcodes: list[dict]) -> str:
    members = s["members"]
    lines = [f"# {s['title']} - Evidence Map", "",
             f"Reference scenario. Raw captures live in this repo's `{SIBLING_LABEL}/`; this "
             "map distils their opcode evidence by joining this repo's own "
             "`derived/observations.json` (numeric truth) against "
             f"`derived/opcode_names.json` (names, promoted from {mapping_source()}).", "",
             f"## Captures ({len(members)})", ""]
    for m in members:
        st = stats[m]
        mix = ", ".join(f"{k} {v}" for k, v in sorted(st["service_mix"].items()))
        lines.append(f"- `{m}` - {fmt_int(st['size'])} B, "
                     f"{len(st['opcode_hexes'])} distinct opcodes ({mix}).")
    lines += ["", f"## Observed opcodes ({len(opcodes)} distinct)", "",
              "Union across the member captures. `name` is the "
              "derived/opcode_names.json entry name; `retail class` is the "
              "retail_class_name attribution when known.", "",
              "| opcode | service | direction | name | retail class | payload lengths |",
              "|---|---|---|---|---|---|"]
    for o in opcodes:
        retail_class = o["retail_class_name"] or "-"
        name = o["name"] or "-"
        lengths = ", ".join(str(x) for x in o["lengths"]) or "-"
        lines.append(f"| `{o['hex']}` | {o['service']} | {o['direction']} | "
                     f"{name} | {retail_class} | {lengths} |")
    lines += ["", "## Verification", "",
              "- Every opcode above is sourced from this repo's own "
              "`derived/observations.json` (numeric truth) joined against "
              "`derived/opcode_names.json` (names) for the member pcaps - no "
              "hand-asserted opcodes.",
              "- Member sizes and sha256 were taken from this repo's "
              f"`{SIBLING_LABEL}/`; the canonical hashes live in "
              "`sources/pcap-1.23b/manifest.yaml`.", "",
              "## Gaps / caveats", "",
              "- Opcode identity and framing only; decoded payload field semantics "
              "live in this repo's `derived/` (payload_layouts.json and friends)."]
    if s.get("caveat"):
        lines.append(f"- {s['caveat']}")
    lines.append("")
    return "\n".join(lines)


def render_file_inventory(s: dict, stats: dict) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["pcap", "capture_path", "bytes", "sha256",
                     "n_opcodes", "opcodes", "service_mix"])
    for m in s["members"]:
        st = stats[m]
        writer.writerow([
            m,
            f"{SIBLING_LABEL}/{m}",
            st["size"],
            st["sha256"],
            len(st["opcode_hexes"]),
            ";".join(st["opcode_hexes"]),
            ";".join(f"{k}={v}" for k, v in sorted(st["service_mix"].items())),
        ])
    return buf.getvalue()


def build() -> tuple[dict, list[dict]]:
    """Return rendered scenario files and declarations."""
    corpus_manifest = load_corpus_manifest()
    scenarios = load_scenarios(corpus_manifest)
    inv = load_inversion()
    files: dict[Path, str] = {}
    for s in scenarios:
        stats = member_stats(s["members"], inv)
        opcodes = union_opcodes(stats)
        scenario_dir = SCENARIOS_DIR / s["id"]
        files[scenario_dir / "README.md"] = render_readme(s, stats)
        files[scenario_dir / "evidence-map.md"] = render_evidence_map(s, stats, opcodes)
        files[scenario_dir / "file-inventory.csv"] = render_file_inventory(s, stats)
    return files, scenarios


def run(check: bool = False) -> int:
    if not OPCODE_NAMES_JSON.exists():
        print(f"ERROR: promoted opcode-name mapping not found at {OPCODE_NAMES_JSON}. "
              "Re-promote it with tools/promote_opcode_names.py.", file=sys.stderr)
        return 2
    if not OBSERVATIONS_JSON.exists():
        print(f"ERROR: observations.json not found at {OBSERVATIONS_JSON}", file=sys.stderr)
        return 2

    files, scenarios = build()
    scenario_ids = {s["id"] for s in scenarios}
    stale_dirs = sorted(
        p for p in (SCENARIOS_DIR.iterdir() if SCENARIOS_DIR.is_dir() else [])
        if p.is_dir() and p.name not in scenario_ids
    )

    stale = []
    for path, text in files.items():
        current = path.read_bytes() if path.exists() else None
        if current != text.encode("utf-8"):
            stale.append(path)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")

    rel = lambda p: str(p.relative_to(REPO_ROOT)).replace("\\", "/")
    if check:
        problems = []
        if stale:
            problems.append("STALE:\n  " + "\n  ".join(sorted(rel(p) for p in stale)))
        if stale_dirs:
            problems.append(
                "STALE SCENARIO DIR(S) (id no longer in "
                "sources/pcap-1.23b/manifest.yaml):\n  "
                + "\n  ".join(rel(p) for p in stale_dirs)
            )
        if problems:
            print("\n\n".join(problems))
            return 1
        print(f"Up to date: {len(scenarios)} scenarios, {len(files)} files.")
        return 0

    for p in stale_dirs:
        shutil.rmtree(p)
    if stale_dirs:
        print("Deleted stale scenario dir(s): " + ", ".join(rel(p) for p in stale_dirs))
    if stale:
        print(f"Wrote {len(stale)} files across {len(scenarios)} scenarios.")
    else:
        print("No changes.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate pcap-reference scenario views.")
    parser.add_argument("--check", action="store_true",
                        help="report stale files; do not write (exit 1 if stale)")
    args = parser.parse_args()
    return run(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
