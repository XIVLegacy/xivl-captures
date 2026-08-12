#!/usr/bin/env python3
"""Regenerate catalog/index.yaml and catalog/aliases.yaml.

The index projects source and study manifests, pcap scenarios, and derived
sidecars into four id-sorted sections. The aliases file maps legacy ids and
path prefixes to current homes. Edit the constants and canonical inputs here,
not the generated YAML.

Usage:
    python tools/build_catalog_index.py            # rewrite both files
    python tools/build_catalog_index.py --check     # diff-only, exit 1 if stale
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from build_scenario_views import BASE_TAGS, load_inversion, member_stats, scenario_search_hints
from restricted_paths import EXCLUDED_DERIVED_IDS

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = REPO_ROOT / "sources"
STUDIES_DIR = REPO_ROOT / "studies"
DATA_DIR = REPO_ROOT / "derived"
PCAP_MANIFEST = SOURCES_DIR / "pcap-1.23b" / "manifest.yaml"
INDEX = REPO_ROOT / "catalog" / "index.yaml"
ALIASES = REPO_ROOT / "catalog" / "aliases.yaml"

FACET_KEYS = ("system", "city_state", "progression_track", "zones")

# Stable aliases whose current id differs from the historical key.
RENAMED_IDS = {
    "primal-battle-ifrit-bowl-of-embers-video-breakdown": "primal-battle-ifrit-bowl-of-embers",
}

# Frozen compatibility ids omit departed sets rather than emit dangling aliases.
PRE_RESHAPE_STUDY_IDS = (
    "bluegartr-stat-tests",
    "elemen-battle-actions",
    "elemen-battlecraft-leve-objectives",
    "elemen-bestiary",
    "elemen-consumable-effects",
    "elemen-craft-gather-actions",
    "elemen-history-removed",
    "elemen-instanced-content-entry-rules",
    "elemen-level-exp",
    "elemen-playguide",
    "elemen-quest-rewards-walkthroughs",
    "elemen-shop-inventory",
    "elemen-site-archive",
    "elemen-zone-guide",
    "gamerescape-tables",
    "kanican-tables",
    "lodestone-beginners",
    "lodestone-dev-patch",
    "lodestone-lore",
    "lodestone-manual",
    "primal-battle-ifrit-bowl-of-embers-video-breakdown",
)

PRE_RESHAPE_SCENARIO_IDS = (
    "action-mechanic-combat-and-actions",
    "aetheryte-mechanic-teleport-flows",
    "battlecraft-leve-accept-and-complete",
    "character-mechanic-attributes-and-class",
    "chat-mechanic-say-shout-and-npc-talk",
    "chocobo-mechanic-mount-unmount",
    "cutscene-mechanic-book",
    "emote-mechanic-dance-and-kneel",
    "gathering-node-wood-and-harvest",
    "inventory-mechanic-bags-and-gear",
    "job-quest-war-updates",
    "movement-mechanic-gridania-locomotion",
    "session-mechanic-login-and-idle",
    "shop-vendor-buy-sell-repair",
    "side-quest-accept-and-journal",
    "social-mechanic-party-and-friends",
    "zone-mechanic-cross-zone-travel",
    "zone-mechanic-inn-room",
    "zone-mechanic-map-ui",
)

HEADER = (
    "# Generated registry; taxonomy: catalog/integrating-new-captures.md.\n"
    "# Inputs: source/study manifests, pcap scenarios, and derived/*.meta.yaml.\n"
    "# Edit canonical inputs and run tools/build_catalog_index.py; do not hand-edit.\n"
)

ALIASES_HEADER = (
    "# Generated legacy id and path compatibility map.\n"
    "# Edit tools/build_catalog_index.py; do not hand-edit.\n"
)


class _NoAlias(yaml.SafeDumper):
    """Never emit YAML anchors/aliases for shared list objects."""

    def ignore_aliases(self, data):  # noqa: D401 - simple override
        return True


def _dump(obj) -> str:
    return yaml.dump(
        obj, Dumper=_NoAlias, sort_keys=False, default_flow_style=False,
        allow_unicode=True, width=100,
    )


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def build_sources() -> list[dict]:
    entries = []
    for manifest_path in sorted(SOURCES_DIR.glob("*/manifest.yaml")):
        source_id = manifest_path.parent.name
        m = load_yaml(manifest_path)
        storage = m.get("storage") or {}
        entry: dict = {"id": m.get("id", source_id)}
        if m.get("title") is not None:
            entry["title"] = m["title"]
        if m.get("evidence_class") is not None:
            entry["evidence_class"] = m["evidence_class"]
        if m.get("distribution") is not None:
            entry["distribution"] = m["distribution"]
        if storage.get("original_state") is not None:
            entry["original_state"] = storage["original_state"]
        if storage.get("storage_id") is not None:
            entry["storage_id"] = storage["storage_id"]
        entry["member_count"] = len(m.get("members") or [])
        entries.append(entry)
    entries.sort(key=lambda e: e["id"])
    return entries


def build_studies() -> list[dict]:
    entries = []
    for manifest_path in sorted(STUDIES_DIR.glob("*/manifest.yaml")):
        study_id = manifest_path.parent.name
        m = load_yaml(manifest_path)
        entry: dict = {"id": m.get("id", study_id)}
        for key in ("title", "status", "evidence_class", "content_kind"):
            if m.get(key) is not None:
                entry[key] = m[key]
        for key in FACET_KEYS:
            if m.get(key) is not None:
                entry[key] = m[key]
        for key in ("tags", "search_hints"):
            if m.get(key) is not None:
                entry[key] = m[key]
        entry["primary_paths"] = [
            f"studies/{study_id}/{p}" for p in m.get("primary_paths") or []
        ]
        if m.get("source_refs") is not None:
            entry["source_refs"] = m["source_refs"]
        entries.append(entry)
    entries.sort(key=lambda e: e["id"])
    return entries


def build_scenarios() -> list[dict]:
    if not PCAP_MANIFEST.exists():
        return []
    corpus = load_yaml(PCAP_MANIFEST)
    inv = load_inversion()
    entries = []
    for s in corpus.get("scenarios") or []:
        entry: dict = {"id": s["id"], "title": s["title"], "content_kind": s["content_kind"]}
        for key in FACET_KEYS:
            if s.get(key) is not None:
                entry[key] = s[key]
        tags = list(s.get("tags") or [])
        for tag in BASE_TAGS:
            if tag not in tags:
                tags.append(tag)
        entry["tags"] = tags
        members = list(s.get("members") or [])
        entry["members"] = members
        stats = member_stats(members, inv)
        entry["search_hints"] = scenario_search_hints(members, stats)
        entries.append(entry)
    entries.sort(key=lambda e: e["id"])
    return entries


def build_derived() -> list[dict]:
    entries = []
    for sidecar in sorted(DATA_DIR.glob("*.meta.yaml")):
        d = load_yaml(sidecar)
        name = sidecar.name[: -len(".meta.yaml")]
        if name in EXCLUDED_DERIVED_IDS:
            continue
        entry: dict = {"id": d.get("dataset", name)}
        if d.get("kind") is not None:
            entry["kind"] = d["kind"]
        if d.get("evidence_class") is not None:
            entry["evidence_class"] = d["evidence_class"]
        output = d.get("output") or {}
        if output.get("file") is not None:
            entry["output_file"] = output["file"]
        entries.append(entry)
    entries.sort(key=lambda e: e["id"])
    return entries


def build_index() -> dict:
    return {
        "sources": build_sources(),
        "studies": build_studies(),
        "scenarios": build_scenarios(),
        "derived": build_derived(),
    }


def render_index(sections: dict) -> str:
    return HEADER + _dump(sections)


def build_aliases() -> dict:
    ids: dict[str, dict] = {}

    for old_id in PRE_RESHAPE_STUDY_IDS:
        new_id = RENAMED_IDS.get(old_id, old_id)
        study_manifest = STUDIES_DIR / new_id / "manifest.yaml"
        source_manifest = SOURCES_DIR / new_id / "manifest.yaml"
        if not (study_manifest.exists() and source_manifest.exists()):
            continue
        ids[old_id] = {
            "study": f"studies/{new_id}/",
            "source": f"sources/{new_id}/",
        }

    for scenario_id in PRE_RESHAPE_SCENARIO_IDS:
        ids[scenario_id] = {"scenario": f"catalog/scenarios/{scenario_id}/"}

    path_prefixes = {
        "captures/": "sources/pcap-1.23b/objects/",
        "data/": "derived/",
        "datasets/": "derived/",
        "sets/<id>/": "per-kind home; resolve <id> against the `ids:` map above "
                      "(study/source for a split-set id, scenario for a scenario id)",
    }

    return {"ids": dict(sorted(ids.items())), "path_prefixes": path_prefixes}


def render_aliases(aliases: dict) -> str:
    return ALIASES_HEADER + _dump(aliases)


def run(check: bool = False) -> int:
    sections = build_index()
    index_text = render_index(sections)
    aliases = build_aliases()
    aliases_text = render_aliases(aliases)

    index_current = INDEX.read_bytes() if INDEX.exists() else None
    aliases_current = ALIASES.read_bytes() if ALIASES.exists() else None
    index_stale = index_current != index_text.encode("utf-8")
    aliases_stale = aliases_current != aliases_text.encode("utf-8")

    if check:
        stale = []
        if index_stale:
            stale.append("catalog/index.yaml")
        if aliases_stale:
            stale.append("catalog/aliases.yaml")
        if stale:
            print("STALE: " + ", ".join(stale))
            return 1
        n = sum(len(v) for v in sections.values())
        print(f"Up to date: catalog/index.yaml ({n} entries across 4 sections), "
              f"catalog/aliases.yaml ({len(aliases['ids'])} id entries).")
        return 0

    wrote = []
    if index_stale:
        INDEX.write_text(index_text, encoding="utf-8", newline="\n")
        wrote.append("catalog/index.yaml")
    if aliases_stale:
        ALIASES.write_text(aliases_text, encoding="utf-8", newline="\n")
        wrote.append("catalog/aliases.yaml")
    if wrote:
        print("Wrote: " + ", ".join(wrote))
    else:
        print("No changes.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate catalog/index.yaml and catalog/aliases.yaml.")
    parser.add_argument("--check", action="store_true",
                        help="report whether either file is stale; do not write (exit 1 if stale)")
    args = parser.parse_args()
    return run(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
