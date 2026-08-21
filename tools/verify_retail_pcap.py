#!/usr/bin/env python3
"""Verify the fixed PCAP retail-input contract and emit a safe attestation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_retail_pcap_archive as archive_tool  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE = REPO / "archives" / "pcap-1.23b" / "pcap-1.23b-objects.zip"
DEFAULT_INPUTS = REPO / "config" / "retail_inputs.json"
DEFAULT_CHECK = REPO / "config" / "retail_pcap_check.json"
DEFAULT_SOURCE = REPO / "sources" / "pcap-1.23b" / "manifest.yaml"
DEFAULT_SCHEMA = REPO / "schemas" / "retail-evidence-attestation.schema.json"

CHECK_ID = "pcap-1.23b-products-v1"
INPUT_ID = "pcap-corpus-1.23b"
INPUT_SHA256 = archive_tool.EXPECTED_ARCHIVE_SHA256
PRIVATE_REPOSITORY = "XIVLegacy/xivl-retail-client-inputs"
PRIVATE_COMMIT = "abfddb3e8434af4ae36d55269088e489cc8050e5"
PRIVATE_PATH = "captures/pcap-1.23b/pcap-1.23b-objects.zip"
ATTESTATION_FILENAME = "retail-evidence-attestation.json"
SCHEMA_VERSION = 1
TOOL_VERSIONS = {"python": "3.12", "verifier": "1.0"}
COMMIT_LENGTH = 40


class VerificationError(Exception):
    """Malformed input that is safe to report without its contents."""


def _read_json(path: Path) -> Any:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise VerificationError("JSON duplicate field")
            result[key] = value
        return result

    try:
        return json.loads(path.read_text(encoding="ascii"), object_pairs_hook=reject_duplicates)
    except (OSError, UnicodeError, ValueError) as exc:
        raise VerificationError("JSON input unreadable") from exc


def _expected_input() -> dict[str, Any]:
    return {
        "id": INPUT_ID,
        "filename": "pcap-1.23b-objects.zip",
        "size": archive_tool.EXPECTED_ARCHIVE_SIZE,
        "sha256": INPUT_SHA256,
        "source": {
            "repository": PRIVATE_REPOSITORY,
            "commit": PRIVATE_COMMIT,
            "path": PRIVATE_PATH,
        },
        "archive": {
            "member_count": archive_tool.EXPECTED_MEMBER_COUNT,
            "uncompressed_size": archive_tool.EXPECTED_UNCOMPRESSED_SIZE,
            "suffix": ".pcapng",
        },
        "allowed_checks": [CHECK_ID],
    }


def _expected_check() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "check": {"id": CHECK_ID, "version": 1},
        "input_id": INPUT_ID,
        "expected": {
            "member_count": archive_tool.EXPECTED_MEMBER_COUNT,
            "uncompressed_size": archive_tool.EXPECTED_UNCOMPRESSED_SIZE,
            "product_count": 27,
        },
    }


def _source_errors(path: Path) -> list[str]:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeError, yaml.YAMLError):
        return ["source manifest unreadable"]
    storage = document.get("storage")
    archive = storage.get("master_archive") if isinstance(storage, dict) else None
    if (
        document.get("id") != "pcap-1.23b"
        or document.get("distribution") != "restricted"
        or not isinstance(storage, dict)
        or storage.get("original_state") != "private-repository"
        or storage.get("storage_id") != PRIVATE_REPOSITORY
        or storage.get("path") != PRIVATE_PATH
        or storage.get("repository") != PRIVATE_REPOSITORY
        or storage.get("commit") != PRIVATE_COMMIT
        or not isinstance(archive, dict)
        or archive.get("file") != "pcap-1.23b-objects.zip"
        or archive.get("size_bytes") != archive_tool.EXPECTED_ARCHIVE_SIZE
        or archive.get("sha256") != INPUT_SHA256
        or len(document.get("members") or []) != archive_tool.EXPECTED_MEMBER_COUNT
    ):
        return ["source storage contract drifted"]
    try:
        archive_tool.expected_members(path)
    except archive_tool.ArchiveValidationError:
        return ["source member contract drifted"]
    return []


def contract_errors(
    inputs_path: Path = DEFAULT_INPUTS,
    check_path: Path = DEFAULT_CHECK,
    source_path: Path = DEFAULT_SOURCE,
) -> list[str]:
    errors: list[str] = []
    try:
        inputs = _read_json(inputs_path)
        expected_inputs = {"schema_version": 1, "inputs": [_expected_input()]}
        if inputs != expected_inputs:
            errors.append("retail input grant drifted")
        check = _read_json(check_path)
        if check != _expected_check():
            errors.append("PCAP check contract drifted")
    except VerificationError:
        errors.append("retail contract unreadable")
    errors.extend(_source_errors(source_path))
    return errors


def verify_archive(
    archive_path: Path,
    *,
    inputs_path: Path = DEFAULT_INPUTS,
    check_path: Path = DEFAULT_CHECK,
    source_path: Path = DEFAULT_SOURCE,
) -> list[str]:
    errors = contract_errors(inputs_path, check_path, source_path)
    try:
        shape = archive_tool.inspect_archive(archive_path, manifest_path=source_path)
    except archive_tool.ArchiveValidationError:
        return errors + ["private archive validation failed"]
    if shape["member_count"] != archive_tool.EXPECTED_MEMBER_COUNT:
        errors.append("private archive member count drifted")
    if shape["uncompressed_size"] != archive_tool.EXPECTED_UNCOMPRESSED_SIZE:
        errors.append("private archive size drifted")
    try:
        import jsonschema

        archive_schema = _read_json(REPO / "schemas" / "retail_pcap_archive.schema.json")
        if any(jsonschema.Draft202012Validator(archive_schema).iter_errors(shape)):
            errors.append("private archive shape schema rejected")
    except (ImportError, VerificationError, ValueError):
        errors.append("private archive shape schema unavailable")
    return errors


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise VerificationError("public commit unavailable") from exc
    commit = result.stdout.strip()
    if (
        len(commit) != COMMIT_LENGTH
        or any(c not in "0123456789abcdef" for c in commit)
        or commit == "0" * COMMIT_LENGTH
    ):
        raise VerificationError("public commit is not a full SHA")
    return commit


def build_attestation(status: str, public_commit: str | None = None) -> dict[str, Any]:
    if status not in {"pass", "fail"}:
        raise ValueError("attestation status invalid")
    commit = public_commit if public_commit is not None else _git_commit()
    if (
        len(commit) != COMMIT_LENGTH
        or any(c not in "0123456789abcdef" for c in commit)
        or commit == "0" * COMMIT_LENGTH
    ):
        raise ValueError("public commit invalid")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "publicRepositoryCommit": commit,
        "approvedInputSha256": INPUT_SHA256,
        "toolVersions": dict(TOOL_VERSIONS),
        "check": {"id": CHECK_ID, "version": 1},
        "result": {"status": status},
    }


def _schema_errors(document: Any) -> bool:
    try:
        import jsonschema

        schema = _read_json(DEFAULT_SCHEMA)
        return any(jsonschema.Draft202012Validator(schema).iter_errors(document))
    except (ImportError, VerificationError, ValueError):
        return True


def retained_output_errors(directory: Path) -> list[str]:
    if not directory.is_dir() or directory.is_symlink():
        return ["retained output root invalid"]
    try:
        entries = list(directory.iterdir())
        if len(entries) != 1 or entries[0].name != ATTESTATION_FILENAME:
            return ["retained output allowlist differs"]
        path = entries[0]
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 4096:
            return ["retained attestation file invalid"]
        raw = path.read_bytes()
        if b"\r" in raw:
            return ["retained attestation line ending invalid"]
        raw.decode("ascii")
        document = json.loads(raw.decode("ascii"))
        canonical = (
            json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("ascii")
        if raw != canonical:
            return ["retained attestation serialization invalid"]
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
        return ["retained attestation unreadable"]
    return ["retained attestation schema rejected"] if _schema_errors(document) else []


def dispatch_errors(event_name: str, ref: str, sha: str, head: str | None) -> list[str]:
    if event_name != "workflow_dispatch":
        return ["dispatch event unauthorized"]
    if ref != "refs/heads/main":
        return ["dispatch ref unauthorized"]
    if not sha or len(sha) != COMMIT_LENGTH or not head or len(head) != COMMIT_LENGTH:
        return ["dispatch revision unauthorized"]
    if sha != head:
        return ["dispatch revision mismatch"]
    return []


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=None)
    parser.add_argument("--check-contract", action="store_true")
    parser.add_argument("--check-dispatch", action="store_true")
    parser.add_argument("--failure-attestation", action="store_true")
    parser.add_argument("--validate-retained-output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.check_dispatch:
        try:
            head = _git_commit()
        except VerificationError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        errors = dispatch_errors(
            os.environ.get("GITHUB_EVENT_NAME", ""),
            os.environ.get("GITHUB_REF", ""),
            os.environ.get("GITHUB_SHA", ""),
            head,
        )
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1 if errors else 0
    if args.validate_retained_output is not None:
        errors = retained_output_errors(args.validate_retained_output)
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1 if errors else 0
    if args.failure_attestation:
        try:
            attestation = build_attestation("fail")
        except (VerificationError, ValueError):
            print("ERROR: attestation could not be built", file=sys.stderr)
            return 1
        if _schema_errors(attestation):
            print("ERROR: attestation schema rejected", file=sys.stderr)
            return 1
        sys.stdout.buffer.write(
            (json.dumps(attestation, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
        )
        return 0
    if args.archive is not None:
        errors = verify_archive(args.archive)
    else:
        errors = contract_errors()
    if args.archive is None and not args.check_contract:
        errors.append("private archive is required")
    try:
        attestation = build_attestation("pass" if not errors else "fail")
    except (VerificationError, ValueError):
        print("ERROR: attestation could not be built", file=sys.stderr)
        return 1
    if _schema_errors(attestation):
        errors.append("attestation schema rejected")
        attestation["result"] = {"status": "fail"}
    sys.stdout.buffer.write(
        (json.dumps(attestation, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    )
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
