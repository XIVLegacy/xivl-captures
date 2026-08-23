#!/usr/bin/env python3
"""Validate and extract the fixed private PCAP archive safely.

Validation reads every member before any destination file is created.  The
archive and destination are expected to be private scratch paths; this tool
never prints member names or packet bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"
EXPECTED_ARCHIVE_SIZE = 2622720
EXPECTED_ARCHIVE_SHA256 = "20a78b9f40ff2393037c9a160c957783cf590b4f01797493d22fcd2039e9cbff"
EXPECTED_MEMBER_COUNT = 54
EXPECTED_UNCOMPRESSED_SIZE = 7242352
MAX_COMPRESSION_RATIO = 1000
CHUNK_SIZE = 1024 * 1024


class ArchiveValidationError(Exception):
    """A fixed-label archive validation failure safe for CI logs."""


def _fail(label: str) -> None:
    raise ArchiveValidationError(label)


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ArchiveValidationError("manifest unreadable") from exc
    if not isinstance(document, dict):
        _fail("manifest shape invalid")
    return document


def expected_members(manifest_path: Path = DEFAULT_SOURCE_MANIFEST) -> dict[str, tuple[int, str]]:
    document = _read_yaml(manifest_path)
    members = document.get("members")
    if not isinstance(members, list) or len(members) != EXPECTED_MEMBER_COUNT:
        _fail("public member manifest count invalid")
    result: dict[str, tuple[int, str]] = {}
    for member in members:
        if not isinstance(member, dict):
            _fail("public member manifest shape invalid")
        name = member.get("file")
        size = member.get("size_bytes")
        digest = member.get("sha256")
        if (
            not isinstance(name, str)
            or not isinstance(size, int)
            or isinstance(size, bool)
            or not isinstance(digest, str)
            or len(digest) != 64
            or name in result
        ):
            _fail("public member manifest entry invalid")
        result[name] = (size, digest)
    return result


def _archive_identity(path: Path) -> None:
    try:
        stat_result = path.lstat()
        if not stat.S_ISREG(stat_result.st_mode) or stat.S_ISLNK(stat_result.st_mode):
            _fail("archive is not a regular file")
        if stat_result.st_size != EXPECTED_ARCHIVE_SIZE:
            _fail("archive size mismatch")
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
                digest.update(chunk)
    except (OSError, ValueError) as exc:
        raise ArchiveValidationError("archive unreadable") from exc
    if digest.hexdigest() != EXPECTED_ARCHIVE_SHA256:
        _fail("archive hash mismatch")


def _safe_member_name(name: str, expected: dict[str, tuple[int, str]]) -> None:
    if not name or "\x00" in name or "\\" in name:
        _fail("archive member path invalid")
    try:
        name.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ArchiveValidationError("archive member path invalid") from exc
    path = PurePosixPath(name)
    if path.is_absolute() or ":" in path.parts[0] or ".." in path.parts:
        _fail("archive member path invalid")
    if path.as_posix() != name or len(path.parts) != 1:
        _fail("archive member path invalid")
    if not name.endswith(".pcapng") or name not in expected:
        _fail("archive member allowlist mismatch")


def _regular_member(info: zipfile.ZipInfo) -> None:
    if info.filename.endswith("/"):
        _fail("archive directory member rejected")
    if info.flag_bits & 0x1:
        _fail("encrypted archive member rejected")
    mode = (info.external_attr >> 16) & 0xFFFF
    if info.create_system == 3 and mode and not stat.S_ISREG(mode):
        _fail("linked archive member rejected")
    if info.external_attr & 0x10:
        _fail("archive directory member rejected")
    if info.compress_size == 0 and info.file_size:
        _fail("archive compression ratio invalid")
    if info.compress_size and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
        _fail("archive compression ratio invalid")


def inspect_archive(
    archive_path: Path,
    *,
    manifest_path: Path = DEFAULT_SOURCE_MANIFEST,
) -> dict[str, Any]:
    """Validate the full archive and return only public shape metadata."""
    _archive_identity(archive_path)
    expected = expected_members(manifest_path)
    seen: set[str] = set()
    actual: list[dict[str, Any]] = []
    total_size = 0
    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            infos = archive.infolist()
            if len(infos) != EXPECTED_MEMBER_COUNT:
                _fail("archive member count mismatch")
            for info in infos:
                _safe_member_name(info.filename, expected)
                if info.filename in seen:
                    _fail("duplicate archive member rejected")
                seen.add(info.filename)
                _regular_member(info)
                expected_size, expected_hash = expected[info.filename]
                if info.file_size != expected_size:
                    _fail("archive member size mismatch")
                total_size += info.file_size
                digest = hashlib.sha256()
                read_size = 0
                magic = b""
                try:
                    with archive.open(info, "r") as handle:
                        while True:
                            chunk = handle.read(CHUNK_SIZE)
                            if not chunk:
                                break
                            if len(magic) < 4:
                                magic += chunk[: 4 - len(magic)]
                            read_size += len(chunk)
                            digest.update(chunk)
                except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                    raise ArchiveValidationError("archive member unreadable") from exc
                if read_size != expected_size or digest.hexdigest() != expected_hash:
                    _fail("archive member identity mismatch")
                if magic != b"\x0a\x0d\x0d\x0a":
                    _fail("non-PCAP archive member rejected")
                actual.append({
                    "file": info.filename,
                    "size_bytes": read_size,
                    "sha256": digest.hexdigest(),
                })
    except ArchiveValidationError:
        raise
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise ArchiveValidationError("archive unreadable") from exc
    if seen != set(expected):
        _fail("archive member set mismatch")
    if total_size != EXPECTED_UNCOMPRESSED_SIZE:
        _fail("archive uncompressed size mismatch")
    actual.sort(key=lambda item: item["file"])
    return {
        "member_count": len(actual),
        "uncompressed_size": total_size,
        "members": actual,
    }


def _destination_is_safe(path: Path) -> None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_dir() or any(path.iterdir()):
            _fail("destination is not an empty private directory")
    else:
        try:
            path.mkdir(parents=True, mode=0o700)
        except OSError as exc:
            raise ArchiveValidationError("destination could not be created") from exc


def extract_archive(
    archive_path: Path,
    destination: Path,
    *,
    manifest_path: Path = DEFAULT_SOURCE_MANIFEST,
) -> dict[str, Any]:
    """Validate completely, then extract regular allowlisted members."""
    shape = inspect_archive(archive_path, manifest_path=manifest_path)
    # Recheck the immutable identity at the phase boundary before opening any
    # output, so a replaced archive cannot bypass the complete validation pass.
    _archive_identity(archive_path)
    created = not destination.exists()
    try:
        _destination_is_safe(destination)
        with zipfile.ZipFile(archive_path, "r") as archive:
            for info in archive.infolist():
                target = destination / info.filename
                with archive.open(info, "r") as source, target.open("xb") as sink:
                    shutil.copyfileobj(source, sink, CHUNK_SIZE)
                try:
                    os.chmod(target, 0o600)
                except OSError:
                    pass
    except ArchiveValidationError:
        if created:
            shutil.rmtree(destination, ignore_errors=True)
        raise
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        if created:
            shutil.rmtree(destination, ignore_errors=True)
        raise ArchiveValidationError("archive extraction failed") from exc
    return shape


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    args = parser.parse_args(argv)
    try:
        shape = extract_archive(args.archive, args.destination, manifest_path=args.manifest)
    except ArchiveValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: archive validated ({shape['member_count']} members, {shape['uncompressed_size']} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
