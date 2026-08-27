#!/usr/bin/env python3
"""Validate schemas, references, hashes, boundaries, and generated shape."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import yaml

try:
    import jsonschema
except ImportError:
    print(
        "error: the 'jsonschema' package is not installed. Install repo "
        "dependencies first:\n    python -m pip install -r tools/requirements.txt",
        file=sys.stderr,
    )
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"
CONFIG_DIR = REPO_ROOT / "config"
SOURCES_DIR = REPO_ROOT / "sources"
STUDIES_DIR = REPO_ROOT / "studies"
DATA_DIR = REPO_ROOT / "derived"
PIPELINES_DIR = REPO_ROOT / "pipelines"
CATALOG_DIR = REPO_ROOT / "catalog"
PCAP_MANIFEST = SOURCES_DIR / "pcap-1.23b" / "manifest.yaml"
CORPUS_ABSENT = os.environ.get("XIVL_CORPUS_ABSENT") == "1"


def pcap_objects_dir(default: Path) -> Path:
    """Resolve private corpus bytes outside the public checkout when requested."""
    override = os.environ.get("XIVL_PCAP_OBJECTS_DIR")
    return Path(override) if override else default

ID_CEILING = 48
PATH_CEILING = 180


def load_json_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


def load_evidence_classes() -> set[str]:
    doc = yaml.safe_load((SCHEMAS_DIR / "evidence-classes.yaml").read_text(encoding="utf-8"))
    return {c["id"] for c in doc["classes"]}


def check_lobby_record_census(results: list) -> None:
    path = STUDIES_DIR / "lobby-handshake-triage" / "derived" / "lobby-record-census.json"
    schema = load_json_schema("lobby-record-census.schema.json")
    try:
        document = json.loads(path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, ValueError) as exc:
        results.append(("schema: sanitized decrypted lobby record census", False, str(exc)))
        return
    validate_doc(document, schema, "schema: sanitized decrypted lobby record census", results)


def check_id_ceiling(value: str, context: str, results: list) -> None:
    ok = isinstance(value, str) and 1 <= len(value) <= ID_CEILING
    results.append((context, ok, "" if ok else f"id {value!r} exceeds the {ID_CEILING}-char ceiling"))


def validate_doc(doc, schema, label: str, results: list) -> None:
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    if errors:
        for e in errors:
            path = "/".join(str(p) for p in e.path) or "<root>"
            results.append((f"{label} [{path}]", False, e.message))
    else:
        results.append((label, True, ""))


def check_sources(results: list, evidence_classes: set[str]) -> dict[str, dict]:
    schema = load_json_schema("source.schema.json")
    manifests: dict[str, dict] = {}
    if not SOURCES_DIR.is_dir():
        return manifests
    timing: list[tuple[str, int, float]] = []
    for source_dir in sorted(p for p in SOURCES_DIR.iterdir() if p.is_dir()):
        manifest_path = source_dir / "manifest.yaml"
        label = f"schema: sources/{source_dir.name}/manifest.yaml"
        if not manifest_path.exists():
            results.append((label, False, "manifest.yaml missing"))
            continue
        doc = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        validate_doc(doc, schema, label, results)
        manifests[doc.get("id", source_dir.name)] = doc

        if "evidence_class" in doc:
            ok = doc["evidence_class"] in evidence_classes
            results.append((
                f"evidence_class: sources/{source_dir.name}/manifest.yaml",
                ok,
                "" if ok else f"evidence_class {doc['evidence_class']!r} not in schemas/evidence-classes.yaml",
            ))

        if "id" in doc:
            check_id_ceiling(doc["id"], f"id ceiling: sources/{source_dir.name} id", results)
        for scenario in doc.get("scenarios", []):
            if "id" in scenario:
                check_id_ceiling(
                    scenario["id"],
                    f"id ceiling: sources/{source_dir.name} scenario {scenario['id']!r}",
                    results,
                )

        check_source_boundary(source_dir, doc, results)
        check_source_objects(source_dir, doc, results, timing)

        for product in doc.get("products") or []:
            product_file = product.get("file") if isinstance(product, dict) else None
            if not product_file:
                continue
            ok = (REPO_ROOT / product_file).exists()
            results.append((
                f"product resolves: sources/{source_dir.name} product {product_file!r}",
                ok,
                "" if ok else f"{product_file} does not exist",
            ))

    total_files = sum(n for _, n, _ in timing)
    total_seconds = sum(t for _, _, t in timing)
    print(f"objects hash-verify timing: {total_files} files across {len(timing)} "
          f"sources in {total_seconds:.2f}s", file=sys.stderr)
    return manifests


def check_retail_contracts(results: list) -> None:
    """Validate the credential-free shape of the optional PCAP lane."""
    contracts = (
        (CONFIG_DIR / "retail_inputs.json", SCHEMAS_DIR / "retail_inputs.schema.json"),
        (CONFIG_DIR / "retail_pcap_check.json", SCHEMAS_DIR / "retail_pcap_check.schema.json"),
    )
    for document_path, schema_path in contracts:
        label = f"schema: {document_path.relative_to(REPO_ROOT).as_posix()}"
        try:
            document = json.loads(document_path.read_text(encoding="ascii"))
            schema = json.loads(schema_path.read_text(encoding="ascii"))
        except (OSError, UnicodeError, ValueError) as exc:
            results.append((label, False, f"retail contract unreadable ({exc.__class__.__name__})"))
            continue
        validate_doc(document, schema, label, results)

    attestation_path = CONFIG_DIR / "retail_evidence" / "pcap-1.23b-products.json"
    if attestation_path.exists():
        label = "schema: config/retail_evidence/pcap-1.23b-products.json"
        try:
            document = json.loads(attestation_path.read_text(encoding="ascii"))
            schema = load_json_schema("retail-evidence-attestation.schema.json")
        except (OSError, UnicodeError, ValueError) as exc:
            results.append((label, False, f"attestation unreadable ({exc.__class__.__name__})"))
        else:
            validate_doc(document, schema, label, results)


def check_source_boundary(source_dir: Path, doc: dict, results: list) -> None:
    """Keep source files under objects and forbid objects for local-only or cold-stored sources."""
    label_stray = f"boundary: sources/{source_dir.name} no stray files beside manifest.yaml"
    strays = sorted(
        str(p.relative_to(source_dir)).replace("\\", "/")
        for p in source_dir.iterdir()
        if p.name != "manifest.yaml" and p.name != "objects"
    )
    if strays:
        results.append((label_stray, False, f"stray path(s) outside objects/: {', '.join(strays)}"))
    else:
        results.append((label_stray, True, ""))

    objects_dir = pcap_objects_dir(source_dir / "objects") if source_dir.name == "pcap-1.23b" else source_dir / "objects"
    distribution = doc.get("distribution")
    if distribution == "local-only":
        label = f"boundary: sources/{source_dir.name} local-only implies no objects/"
        members = doc.get("members") or []
        problems = []
        if members:
            problems.append("members is non-empty")
        if objects_dir.is_dir():
            problems.append("objects/ exists")
        if problems:
            results.append((label, False, "; ".join(problems)))
        else:
            results.append((label, True, ""))

    original_state = (doc.get("storage") or {}).get("original_state")
    if original_state == "cold-stored":
        label = f"boundary: sources/{source_dir.name} cold-stored implies no objects/"
        ok = not objects_dir.is_dir()
        results.append((label, ok, "" if ok else "objects/ exists alongside cold-stored storage"))

    label_consistency = (
        f"boundary: sources/{source_dir.name} distribution local-only "
        "<=> storage.original_state local-only"
    )
    dist_local = distribution == "local-only"
    state_local = original_state == "local-only"
    ok = dist_local == state_local
    results.append((
        label_consistency, ok,
        "" if ok else f"distribution={distribution!r}, storage.original_state={original_state!r}",
    ))


def check_source_objects(source_dir: Path, doc: dict, results: list, timing: list) -> None:
    """Hash exact object membership or validate an allowed object-free state."""
    objects_dir = pcap_objects_dir(source_dir / "objects") if source_dir.name == "pcap-1.23b" else source_dir / "objects"
    label = f"objects hash-verify: sources/{source_dir.name}"
    members = doc.get("members") or []

    if not objects_dir.is_dir():
        if CORPUS_ABSENT:
            results.append((
                label, True,
                f"public shape: {len(members)} source object(s) intentionally absent",
            ))
            return
        original_state = (doc.get("storage") or {}).get("original_state")
        if original_state == "cold-stored":
            results.append((
                label, True,
                f"cold-stored: {len(members)} member(s) documented, not hash-verified here",
            ))
            return
        if original_state == "local-only":
            ok = not members
            results.append((label, ok, "" if ok else "local-only source must not carry members"))
            return
        results.append((label, False, "objects/ directory missing"))
        return

    manifest_files = {m["file"]: m for m in members}
    # Member paths are relative to objects/ and may include subdirectories.
    disk_files = {
        str(p.relative_to(objects_dir)).replace("\\", "/")
        for p in objects_dir.rglob("*") if p.is_file()
    }

    missing = sorted(set(manifest_files) - disk_files)
    extra = sorted(disk_files - set(manifest_files))
    mismatched = []
    size_mismatched = []
    start = time.monotonic()
    for name, entry in manifest_files.items():
        path = objects_dir / name
        if not path.is_file():
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != entry["sha256"]:
            mismatched.append(f"{name} (expected {entry['sha256']}, got {actual})")
        actual_size = path.stat().st_size
        if actual_size != entry["size_bytes"]:
            size_mismatched.append(
                f"{name} (expected {entry['size_bytes']}, got {actual_size})"
            )
    timing.append((source_dir.name, len(manifest_files), time.monotonic() - start))

    if missing or extra or mismatched or size_mismatched:
        notes = []
        if missing:
            notes.append(f"missing: {', '.join(missing)}")
        if extra:
            notes.append(f"extra: {', '.join(extra)}")
        if mismatched:
            notes.append(f"sha256 mismatch: {', '.join(mismatched)}")
        if size_mismatched:
            notes.append(f"size_bytes mismatch: {', '.join(size_mismatched)}")
        results.append((label, False, "; ".join(notes)))
    else:
        results.append((label, True, f"{len(members)} members verified"))


def check_dataset_meta(results: list, evidence_classes: set[str]) -> set[str]:
    schema = load_json_schema("dataset-meta.schema.json")
    sidecar_names: set[str] = set()
    for sidecar in sorted(DATA_DIR.glob("*.meta.yaml")):
        name = sidecar.name[: -len(".meta.yaml")]
        sidecar_names.add(name)
        label = f"schema: derived/{sidecar.name}"
        doc = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
        validate_doc(doc, schema, label, results)

        if "evidence_class" in doc:
            ok = doc["evidence_class"] in evidence_classes
            results.append((
                f"evidence_class: derived/{sidecar.name}",
                ok,
                "" if ok else f"evidence_class {doc['evidence_class']!r} not in schemas/evidence-classes.yaml",
            ))
        if "dataset" in doc:
            check_id_ceiling(doc["dataset"], f"id ceiling: derived/{sidecar.name} dataset id", results)
            ok = doc["dataset"] == name
            results.append((
                f"dataset id matches filename: derived/{sidecar.name}",
                ok,
                "" if ok else f"dataset field {doc['dataset']!r} != filename stem {name!r}",
            ))
    return sidecar_names


def check_data_sidecar_pairing(results: list, sidecar_names: set[str]) -> None:
    json_names = {p.stem for p in DATA_DIR.glob("*.json")}
    missing_sidecars = sorted(json_names - sidecar_names)
    orphan_sidecars = sorted(sidecar_names - json_names)
    ok = not missing_sidecars and not orphan_sidecars
    note_parts = []
    if missing_sidecars:
        note_parts.append(f"derived/*.json missing a sidecar: {', '.join(missing_sidecars)}")
    if orphan_sidecars:
        note_parts.append(f"sidecar with no derived/*.json: {', '.join(orphan_sidecars)}")
    results.append(("derived/*.json <-> derived/*.meta.yaml pairing", ok, "; ".join(note_parts)))


def literal_version(tool_path: Path, constant: str) -> str | None:
    """Read a tool's literal version constant without importing it."""
    try:
        tree = ast.parse(tool_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == constant
            for target in node.targets
        ):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            return None
        return value if isinstance(value, str) else None
    return None


def check_pipelines(results: list) -> None:
    schema = load_json_schema("pipeline.schema.json")
    if not PIPELINES_DIR.is_dir():
        results.append(("pipelines/ directory", False, "pipelines/ directory missing"))
        return
    for path in sorted(PIPELINES_DIR.glob("*.yaml")):
        label = f"schema: pipelines/{path.name}"
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        validate_doc(doc, schema, label, results)

        if "id" in doc:
            check_id_ceiling(doc["id"], f"id ceiling: pipelines/{path.name} id", results)

        runner = doc.get("runner") or {}
        runner_tool = runner.get("tool")
        if runner_tool:
            runner_path = REPO_ROOT / runner_tool
            runner_ok = runner_path.is_file()
            results.append((
                f"runner.tool resolves: pipelines/{path.name} tool {runner_tool!r}",
                runner_ok,
                "" if runner_ok else f"{runner_tool} does not exist",
            ))
            if runner_ok:
                code_version = literal_version(runner_path, "PIPELINE_VERSION")
                declared_version = runner.get("version")
                version_ok = code_version is not None and code_version == declared_version
                results.append((
                    f"runner.version matches tool: pipelines/{path.name}",
                    version_ok,
                    "" if version_ok else (
                        f"pipeline declares {declared_version!r}, tool declares {code_version!r}"
                    ),
                ))

        seen_outputs: set[str] = set()
        for output in doc.get("outputs", []):
            out_id = output.get("dataset")
            if not out_id:
                continue
            duplicate = out_id in seen_outputs
            seen_outputs.add(out_id)
            results.append((
                f"pipeline output unique: pipelines/{path.name} output {out_id!r}",
                not duplicate,
                "" if not duplicate else "duplicate output id",
            ))
            check_id_ceiling(out_id, f"id ceiling: pipelines/{path.name} output {out_id!r}", results)
            output_ok = (DATA_DIR / f"{out_id}.json").exists()
            results.append((
                f"pipeline output resolves: pipelines/{path.name} output {out_id!r}",
                output_ok,
                "" if output_ok else f"derived/{out_id}.json does not exist",
            ))

            generator = output.get("generator") or {}
            tool = generator.get("tool")
            if tool:
                tool_path = REPO_ROOT / tool
                tool_ok = tool_path.is_file()
                results.append((
                    f"generator.tool resolves: {out_id} tool {tool!r}",
                    tool_ok,
                    "" if tool_ok else f"{tool} does not exist",
                ))
                if tool_ok:
                    code_version = literal_version(tool_path, "GENERATOR_VERSION")
                    declared_version = generator.get("version")
                    version_ok = code_version is not None and code_version == declared_version
                    results.append((
                        f"generator.version matches tool: {out_id}",
                        version_ok,
                        "" if version_ok else (
                            f"pipeline declares {declared_version!r}, "
                            f"tool declares {code_version!r}"
                        ),
                    ))

            for inp in output.get("inputs", []):
                if "source" in inp:
                    input_id = inp["source"]
                    check_id_ceiling(
                        input_id, f"id ceiling: {out_id} input {input_id!r}", results
                    )
                    input_ok = (SOURCES_DIR / input_id).is_dir()
                    results.append((
                        f"pipeline input resolves: {out_id} source {input_id!r}",
                        input_ok,
                        "" if input_ok else f"sources/{input_id}/ does not exist",
                    ))
                elif "dataset" in inp:
                    input_id = inp["dataset"]
                    check_id_ceiling(
                        input_id, f"id ceiling: {out_id} input {input_id!r}", results
                    )
                    input_ok = (DATA_DIR / f"{input_id}.json").exists()
                    results.append((
                        f"pipeline input resolves: {out_id} dataset {input_id!r}",
                        input_ok,
                        "" if input_ok else f"derived/{input_id}.json does not exist",
                    ))


def check_studies(results: list, evidence_classes: set[str]) -> None:
    if not STUDIES_DIR.is_dir():
        return
    schema = load_json_schema("study.schema.json")
    for study_dir in sorted(p for p in STUDIES_DIR.iterdir() if p.is_dir()):
        manifest_path = study_dir / "manifest.yaml"
        label = f"schema: studies/{study_dir.name}/manifest.yaml"
        if not manifest_path.exists():
            results.append((label, False, "manifest.yaml missing"))
            continue
        doc = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        validate_doc(doc, schema, label, results)

        if "evidence_class" in doc:
            ok = doc["evidence_class"] in evidence_classes
            results.append((
                f"evidence_class: studies/{study_dir.name}/manifest.yaml",
                ok,
                "" if ok else f"evidence_class {doc['evidence_class']!r} not in schemas/evidence-classes.yaml",
            ))
        if "id" in doc:
            check_id_ceiling(doc["id"], f"id ceiling: studies/{study_dir.name} id", results)


def check_party_marker_chronology(results: list) -> None:
    schema = load_json_schema("party-marker-chronology.schema.json")
    path = STUDIES_DIR / "party-marker-018d-chronology" / "derived" / "accounting.json"
    label = "schema: party-marker-018d-chronology accounting"
    if not path.is_file():
        results.append((label, False, "accounting.json missing"))
        return
    validate_doc(json.loads(path.read_text(encoding="ascii")), schema, label, results)


def check_catalog_generated(results: list) -> None:
    """Reject catalog files outside the declared generated and authored shape."""
    label = "catalog: only generated/allowed files present"
    if not CATALOG_DIR.is_dir():
        results.append((label, False, "catalog/ directory missing"))
        return

    allowed_top = {
        "README.md", "index.yaml", "aliases.yaml", "by-content-kind.md",
        "by-zone.md", "by-system.md", "by-progression.md",
        "by-city-state.md", "integrating-new-captures.md",
        "video-breakdown-handoff.md",
    }
    allowed_scenario_files = {"README.md", "evidence-map.md", "file-inventory.csv"}

    scenario_ids: set[str] = set()
    if PCAP_MANIFEST.exists():
        corpus = yaml.safe_load(PCAP_MANIFEST.read_text(encoding="utf-8")) or {}
        scenario_ids = {s["id"] for s in (corpus.get("scenarios") or [])}

    bad: list[str] = []
    for path in CATALOG_DIR.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(CATALOG_DIR).as_posix()
        parts = rel.split("/")
        if len(parts) == 1:
            if parts[0] not in allowed_top:
                bad.append(f"catalog/{rel}")
            continue
        if len(parts) == 3 and parts[0] == "scenarios" and parts[1] in scenario_ids \
                and parts[2] in allowed_scenario_files:
            continue
        bad.append(f"catalog/{rel}")

    ok = not bad
    note = "" if ok else "unexpected path(s) under catalog/: " + ", ".join(sorted(bad))
    results.append((label, ok, note))


def check_path_lengths(results: list) -> None:
    """Every git-tracked file's repo-relative path respects PATH_CEILING."""
    try:
        proc = subprocess.run(
            ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        results.append(("path ceiling: git ls-files", False, f"could not enumerate tracked files: {exc}"))
        return
    too_long = [line for line in proc.stdout.splitlines() if line and len(line) > PATH_CEILING]
    ok = not too_long
    note = "" if ok else f"{len(too_long)} path(s) exceed {PATH_CEILING} chars: " + ", ".join(too_long[:5])
    results.append((f"path ceiling: every tracked file <= {PATH_CEILING} chars", ok, note))


def report(results: list) -> int:
    failed = [r for r in results if not r[1]]
    print()
    print("=== validate_schemas.py summary ===")
    for label, ok, note in results:
        status = "PASS" if ok else "FAIL"
        suffix = f" - {note}" if note else ""
        print(f"[{status}] {label}{suffix}")
    print()
    if failed:
        print(f"FAIL: {len(failed)}/{len(results)} checks failed.")
        return 1
    print(f"PASS: all {len(results)} checks passed.")
    return 0


def main() -> int:
    results: list[tuple[str, bool, str]] = []
    evidence_classes = load_evidence_classes()

    check_retail_contracts(results)
    check_sources(results, evidence_classes)
    sidecar_names = check_dataset_meta(results, evidence_classes)
    check_data_sidecar_pairing(results, sidecar_names)
    check_pipelines(results)
    check_studies(results, evidence_classes)
    check_party_marker_chronology(results)
    check_lobby_record_census(results)
    check_catalog_generated(results)
    check_path_lengths(results)

    return report(results)


if __name__ == "__main__":
    sys.exit(main())
