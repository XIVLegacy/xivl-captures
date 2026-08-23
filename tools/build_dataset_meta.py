#!/usr/bin/env python3
"""Generate deterministic metadata sidecars from provenance and hashes.

Run after product regeneration because sidecars hash their outputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

import yaml

from _json_io import REPO_ROOT, DATA_DIR

PIPELINES_DIR = REPO_ROOT / "pipelines"
SOURCE_MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"

PROMOTED_DATASETS = {"opcode_names"}
FROZEN_DATASETS = {"spawn_location_validation"}

# Fixed historical provenance is not derivable from the file, so keep it with the frozen artifact definition.
FROZEN_NOTES = {
    "spawn_location_validation": (
        "Frozen historical artifact from a one-time spawn-location divergence "
        "study. This repo retains its result as packet-capture evidence."
    ),
}

# Non-generated evidence classes are assigned explicitly.
NON_GENERATED_EVIDENCE_CLASS = {
    "opcode_names": "packet-capture",
    "spawn_location_validation": "packet-capture",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corpus_content_sha256() -> str:
    """Hash sorted member digests as the corpus-content identity."""
    manifest = yaml.safe_load(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    hashes = sorted(m["sha256"] for m in manifest["members"])
    return hashlib.sha256("\n".join(hashes).encode("ascii")).hexdigest()


def load_pipelines() -> dict[str, dict]:
    """Return {output_dataset_id: pipeline_dict} across all pipelines/*.yaml."""
    by_output: dict[str, dict] = {}
    for path in sorted(PIPELINES_DIR.glob("*.yaml")):
        pipeline = yaml.safe_load(path.read_text(encoding="utf-8"))
        for output in pipeline["outputs"]:
            out_id = output["dataset"]
            by_output[out_id] = {
                "generator": output["generator"],
                "inputs": output["inputs"],
                "outputs": [out_id],
            }
    return by_output


def build_generated_meta(name: str, pipeline: dict, corpus_hash: str) -> dict:
    inputs = []
    for inp in pipeline["inputs"]:
        if "source" in inp:
            inputs.append({"source": inp["source"], "content_sha256": corpus_hash})
        else:
            dataset_id = inp["dataset"]
            dataset_path = DATA_DIR / f"{dataset_id}.json"
            inputs.append({"dataset": dataset_id, "sha256": sha256_file(dataset_path)})

    return {
        "dataset": name,
        "kind": "generated",
        "evidence_class": "packet-capture",
        "schema_version": 1,
        "output": {
            "file": f"derived/{name}.json",
            "sha256": sha256_file(DATA_DIR / f"{name}.json"),
        },
        "generator": {
            "tool": pipeline["generator"]["tool"],
            "version": pipeline["generator"]["version"],
        },
        "inputs": inputs,
    }


def build_promoted_meta(name: str) -> dict:
    doc = json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))
    citation = doc["source"]

    return {
        "dataset": name,
        "kind": "promoted",
        "evidence_class": NON_GENERATED_EVIDENCE_CLASS[name],
        "schema_version": 1,
        "output": {
            "file": f"derived/{name}.json",
            "sha256": sha256_file(DATA_DIR / f"{name}.json"),
        },
        "provenance": {"citation": citation},
    }


def build_frozen_meta(name: str) -> dict:
    return {
        "dataset": name,
        "kind": "frozen",
        "evidence_class": NON_GENERATED_EVIDENCE_CLASS[name],
        "schema_version": 1,
        "output": {
            "file": f"derived/{name}.json",
            "sha256": sha256_file(DATA_DIR / f"{name}.json"),
        },
        "provenance": {"note": FROZEN_NOTES[name]},
    }


def dump_yaml(obj: dict) -> str:
    return yaml.dump(obj, default_flow_style=False, sort_keys=False, allow_unicode=True)


def write_sidecar(path: Path, obj: dict) -> None:
    text = dump_yaml(obj)
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(text)


def build_all_meta() -> dict[str, dict]:
    corpus_hash = corpus_content_sha256()
    pipelines_by_output = load_pipelines()

    out: dict[str, dict] = {}
    for json_path in sorted(DATA_DIR.glob("*.json")):
        name = json_path.stem
        if name in PROMOTED_DATASETS:
            out[name] = build_promoted_meta(name)
        elif name in FROZEN_DATASETS:
            out[name] = build_frozen_meta(name)
        elif name in pipelines_by_output:
            out[name] = build_generated_meta(name, pipelines_by_output[name], corpus_hash)
        else:
            print(
                f"error: derived/{json_path.name} has no pipeline output entry and is not "
                "marked promoted/frozen in tools/build_dataset_meta.py. Add a "
                "pipelines/*.yaml entry (or a PROMOTED_DATASETS/FROZEN_DATASETS "
                "entry) before this product can get a sidecar.",
                file=sys.stderr,
            )
            sys.exit(2)
    return out


def do_write() -> int:
    all_meta = build_all_meta()
    for name, meta in all_meta.items():
        write_sidecar(DATA_DIR / f"{name}.meta.yaml", meta)
    print(f"wrote {len(all_meta)} sidecars under derived/*.meta.yaml")
    return 0


def do_check() -> int:
    all_meta = build_all_meta()
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, meta in all_meta.items():
            committed = DATA_DIR / f"{name}.meta.yaml"
            if not committed.exists():
                failures.append(f"derived/{name}.meta.yaml missing")
                continue
            tmp_path = Path(tmp) / f"{name}.meta.yaml"
            write_sidecar(tmp_path, meta)
            if tmp_path.read_bytes() != committed.read_bytes():
                failures.append(f"derived/{name}.meta.yaml is stale (regenerated bytes differ)")

    known = set(all_meta.keys())
    for sidecar in sorted(DATA_DIR.glob("*.meta.yaml")):
        name = sidecar.name[: -len(".meta.yaml")]
        if name not in known:
            failures.append(f"derived/{sidecar.name} has no matching derived/{name}.json")

    if failures:
        print("FAIL: dataset metadata drift detected:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS: {len(all_meta)} sidecars are up to date.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="regenerate to temp and byte-compare; exit 1 on drift")
    args = ap.parse_args()
    return do_check() if args.check else do_write()


if __name__ == "__main__":
    sys.exit(main())
