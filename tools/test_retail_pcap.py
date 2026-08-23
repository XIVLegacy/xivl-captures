#!/usr/bin/env python3
"""Mutation and security tests for the restricted PCAP retail lane."""

from __future__ import annotations

import ast
import copy
import json
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import extract_retail_pcap_archive as extractor
import verify_retail_pcap as verifier

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE = ROOT / "archives" / "pcap-1.23b" / "pcap-1.23b-objects.zip"
WORKFLOW = ROOT / ".github" / "workflows" / "retail-checks.yml"
PASSED = 0
FAILED: list[str] = []


def check(label: str, condition: bool) -> None:
    global PASSED
    if condition:
        PASSED += 1
    else:
        FAILED.append(label)


def expect_archive_error(label: str, callback) -> None:
    try:
        callback()
    except extractor.ArchiveValidationError:
        check(label, True)
    except Exception:
        check(label, False)
    else:
        check(label, False)


def write_json(path: Path, value: object) -> None:
    path.write_bytes(
        (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    )


def archive_shape_tests(archive: Path) -> None:
    shape = extractor.inspect_archive(archive)
    check("canonical archive shape passes", shape["member_count"] == 54 and shape["uncompressed_size"] == 7242352)
    try:
        first = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "verify_retail_pcap.py"), "--archive", str(archive)],
            cwd=ROOT, capture_output=True, check=False, timeout=120,
        )
        second = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "verify_retail_pcap.py"), "--archive", str(archive)],
            cwd=ROOT, capture_output=True, check=False, timeout=120,
        )
    except subprocess.TimeoutExpired:
        check("retail verifier subprocess timeout fails closed", False)
        return
    check(
        "repeated sanitized attestations are byte-identical",
        first.returncode == second.returncode == 0 and first.stdout == second.stdout,
    )
    with tempfile.TemporaryDirectory(prefix="retail-pcap-test-") as raw:
        root = Path(raw)
        destination = root / "corpus"
        extracted = extractor.extract_archive(archive, destination)
        check("canonical archive extracts", extracted == shape)
        members = sorted(destination.glob("*.pcapng"))
        check("extraction has exactly 54 members", len(members) == 54)
        check("extraction has no nested members", not any(path.parent != destination for path in members))

        changed = root / "changed.zip"
        data = bytearray(archive.read_bytes())
        data[-1] ^= 1
        changed.write_bytes(data)
        expect_archive_error("changed archive bytes fail", lambda: extractor.inspect_archive(changed))


def path_and_member_tests() -> None:
    expected = {"safe.pcapng": (4, "0" * 64)}
    for value, label in (
        ("", "empty path"),
        ("/safe.pcapng", "absolute path"),
        ("../safe.pcapng", "parent traversal"),
        ("safe\\name.pcapng", "backslash path"),
        ("safe.txt", "non-PCAP suffix"),
        ("nested/safe.pcapng", "nested path"),
    ):
        expect_archive_error(label + " fails", lambda value=value: extractor._safe_member_name(value, expected))

    directory = zipfile.ZipInfo("safe.pcapng/")
    expect_archive_error("directory member fails", lambda: extractor._regular_member(directory))
    encrypted = zipfile.ZipInfo("safe.pcapng")
    encrypted.flag_bits |= 0x1
    expect_archive_error("encrypted member fails", lambda: extractor._regular_member(encrypted))
    linked = zipfile.ZipInfo("safe.pcapng")
    linked.create_system = 3
    linked.external_attr = stat.S_IFLNK << 16
    expect_archive_error("linked member fails", lambda: extractor._regular_member(linked))
    bomb = zipfile.ZipInfo("safe.pcapng")
    bomb.file_size = 1001
    bomb.compress_size = 1
    expect_archive_error("compression bomb fails", lambda: extractor._regular_member(bomb))


def contract_and_output_tests() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    check(
        "private tree selects the approved blob and directory paths",
        "assert set(expected_blobs) | expected_trees <= set(by_path)" in workflow
        and '"ffxivgame.exe"' not in workflow
        and '"client-data/' not in workflow
        and '"client-scripts/' not in workflow,
    )
    check(
        "private tree requires blob and directory modes",
        'assert entry.get("mode") == "100644"' in workflow
        and 'assert entry.get("mode") == "040000"' in workflow,
    )
    check(
        "hosted dependencies use an exact hash lock without cache",
        'python-version: "3.12.14"' in workflow
        and "--require-hashes --only-binary=:all:" in workflow
        and "cache:" not in workflow,
    )
    python_commands = [
        line for line in workflow.splitlines()
        if "python" in line
        and "python-version" not in line
        and "setup-python" not in line
    ]
    check(
        "every hosted Python command is bounded",
        bool(python_commands) and all("timeout " in line for line in python_commands),
    )
    check(
        "hosted refresh failure prints only its sanitized summary",
        "awk '/^=== refresh.py summary ===/ { emit = 1 } emit'" in workflow
        and 'cat "${private_root}/refresh.log"' not in workflow,
    )
    check(
        "hosted refresh keeps unrelated private corpora absent",
        "export XIVL_CORPUS_ABSENT=1" in workflow,
    )
    timeout_files = (
        "refresh.py",
        "test_retail_pcap.py",
        "verify_retail_pcap.py",
        "validate_digestion.py",
        "validate_schemas.py",
    )
    unbounded: list[str] = []
    for name in timeout_files:
        tree = ast.parse((ROOT / "tools" / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            owner = node.func.value
            if (
                node.func.attr == "run"
                and isinstance(owner, ast.Name)
                and owner.id == "subprocess"
                and not any(keyword.arg == "timeout" for keyword in node.keywords)
            ):
                unbounded.append(f"{name}:{node.lineno}")
    check("credentialed subprocess calls are bounded", not unbounded)
    check("public contract passes", not verifier.contract_errors())
    with tempfile.TemporaryDirectory(prefix="retail-pcap-contract-") as raw:
        root = Path(raw)
        inputs = json.loads(verifier.DEFAULT_INPUTS.read_text(encoding="ascii"))
        inputs["inputs"][0]["sha256"] = "0" * 64
        mutated_inputs = root / "inputs.json"
        write_json(mutated_inputs, inputs)
        check(
            "input hash mutation fails",
            bool(verifier.contract_errors(mutated_inputs, verifier.DEFAULT_CHECK, verifier.DEFAULT_SOURCE)),
        )
        check_doc = json.loads(verifier.DEFAULT_CHECK.read_text(encoding="ascii"))
        check_doc["expected"]["member_count"] += 1
        mutated_check = root / "check.json"
        write_json(mutated_check, check_doc)
        check(
            "check member mutation fails",
            bool(verifier.contract_errors(verifier.DEFAULT_INPUTS, mutated_check, verifier.DEFAULT_SOURCE)),
        )
        check_doc = json.loads(verifier.DEFAULT_CHECK.read_text(encoding="ascii"))
        check_doc["expected"]["product_count"] += 1
        mutated_check.write_bytes(
            (json.dumps(check_doc, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
        )
        check(
            "stale product expectation fails",
            bool(verifier.contract_errors(verifier.DEFAULT_INPUTS, mutated_check, verifier.DEFAULT_SOURCE)),
        )

        attestation = verifier.build_attestation("pass", "1" * 40)
        check("passing attestation schema passes", not verifier._schema_errors(attestation))
        extra = copy.deepcopy(attestation)
        extra["payload"] = "forbidden"
        check("attestation additional field fails", verifier._schema_errors(extra))
        wrong = copy.deepcopy(attestation)
        wrong["approvedInputSha256"] = "0" * 64
        check("attestation input hash mutation fails", verifier._schema_errors(wrong))
        zero_commit = copy.deepcopy(attestation)
        zero_commit["publicRepositoryCommit"] = "0" * 40
        check("attestation all-zero commit fails", verifier._schema_errors(zero_commit))

        safe = root / "safe"
        safe.mkdir()
        write_json(safe / verifier.ATTESTATION_FILENAME, attestation)
        check("single retained attestation passes", not verifier.retained_output_errors(safe))
        (safe / "extra.log").write_text("forbidden\n", encoding="ascii")
        check("extra retained file fails", bool(verifier.retained_output_errors(safe)))
        (safe / "extra.log").unlink()
        (safe / verifier.ATTESTATION_FILENAME).write_bytes(b"{}\r\n")
        check("CRLF retained attestation fails", bool(verifier.retained_output_errors(safe)))

    for event, ref, sha, head, label in (
        ("push", "refs/heads/main", "1" * 40, "1" * 40, "event"),
        ("workflow_dispatch", "refs/heads/feature", "1" * 40, "1" * 40, "branch"),
        ("workflow_dispatch", "refs/heads/main", "1" * 40, "2" * 40, "revision"),
    ):
        check("dispatch " + label + " fails", bool(verifier.dispatch_errors(event, ref, sha, head)))


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    contracts_only = "--contracts-only" in args
    args = [arg for arg in args if arg != "--contracts-only"]
    archive_arg = next((Path(args[i + 1]) for i, arg in enumerate(args[:-1]) if arg == "--archive"), None)
    if any(arg not in {"--archive", str(archive_arg) if archive_arg else ""} for arg in args):
        print("FAIL: unsupported test argument")
        return 1
    path_and_member_tests()
    contract_and_output_tests()
    if not contracts_only:
        archive = archive_arg or (DEFAULT_ARCHIVE if DEFAULT_ARCHIVE.is_file() else None)
        if archive is not None:
            archive_shape_tests(archive)
    if FAILED:
        print("FAIL: " + "; ".join(FAILED))
        return 1
    print(f"PASS: {PASSED} retail PCAP security and mutation checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
