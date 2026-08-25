#!/usr/bin/env python3
"""Reproduce the sanitized lobby acknowledgement structure fixture."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import re
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.extractors.extract_streams import reconstruct_connections  # noqa: E402

SOURCE = Path(os.environ.get(
    "XIVL_PCAP_OBJECTS_DIR",
    str(REPO_ROOT / "sources/pcap-1.23b/objects"),
)) / "login.pcapng"
OUTPUT = REPO_ROOT / "studies/lobby-handshake-triage/derived/lobby-acknowledgement-structure.json"
SOURCE_SHA256 = "28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62"
FORMAT = "xivl-lobby-acknowledgement-structure-v1"
OUTER_LENGTH = 0x2A0
ACK_STREAM_OFFSET = 0x28
PAYLOAD_OFFSET = 0x20
BLOCK_SIZE = 8
REDACTED_CLASSES = [
    "session tokens",
    "character names",
    "network addresses and ports",
    "cryptographic keys",
    "opaque payload values",
]
HEX_SECRET_RE = re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{32,}(?![0-9a-f])")
IPV4_RE = re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)")


def _read_u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _normalized_key(client_number: int) -> bytes:
    material = struct.pack("<III", 0x12345678, client_number, 1000)
    material += b"Test Ticket Data" + bytes(16)
    digest = hashlib.md5(material).digest()
    normalized = bytearray()
    for offset in range(0, len(digest), 4):
        word = 0
        for value in digest[offset : offset + 4]:
            signed = value if value < 0x80 else value - 0x100
            word = ((word << 8) | (signed & 0xFFFFFFFF)) & 0xFFFFFFFF
        normalized.extend(word.to_bytes(4, "big"))
    return bytes(normalized)


def _swap_words(block: bytes) -> bytes:
    return block[:4][::-1] + block[4:][::-1]


def _decrypt(payload: bytes, client_number: int) -> bytes:
    try:
        from Crypto.Cipher import Blowfish
    except ImportError as exc:
        raise RuntimeError(
            "PyCryptodome is required to reproduce the restricted fixture; "
            "install tools/requirements.txt"
        ) from exc

    cipher = Blowfish.new(_normalized_key(client_number), Blowfish.MODE_ECB)
    output = bytearray()
    for offset in range(0, len(payload), BLOCK_SIZE):
        block = payload[offset : offset + BLOCK_SIZE]
        output.extend(_swap_words(cipher.decrypt(_swap_words(block))))
    return bytes(output)


def _frames(blob: bytes) -> list[tuple[int, bytes]]:
    frames = []
    offset = 0
    while offset + 16 <= len(blob):
        size = _read_u16(blob, offset + 4)
        if size < 16 or offset + size > len(blob):
            break
        frames.append((offset, blob[offset : offset + size]))
        offset += size
    return frames


def _comparison_spans(left: bytes, right: bytes) -> list[dict]:
    spans = []
    start = 0
    kind = "invariant" if left[0] == right[0] else "dynamic"
    for offset in range(1, len(left) + 1):
        current = None
        if offset < len(left):
            current = "invariant" if left[offset] == right[offset] else "dynamic"
        if current != kind:
            spans.append({"kind": kind, "offset": start, "length": offset - start})
            start = offset
            kind = current
    return spans


def _repeat_groups(records: list[bytes]) -> list[dict]:
    per_record = []
    for record in records:
        values: dict[bytes, list[int]] = {}
        for offset in range(PAYLOAD_OFFSET, len(record), BLOCK_SIZE):
            block = record[offset : offset + BLOCK_SIZE]
            if block != bytes(BLOCK_SIZE):
                values.setdefault(block, []).append(offset)
        per_record.append({tuple(offsets): value for value, offsets in values.items() if len(offsets) > 1})

    common_offsets = sorted(set(per_record[0]) & set(per_record[1]))
    return [
        {
            "offsets": list(offsets),
            "unitLength": BLOCK_SIZE,
            "valueVariesAcrossSessions": per_record[0][offsets] != per_record[1][offsets],
        }
        for offsets in common_offsets
    ]


def build_fixture(source: Path = SOURCE) -> dict:
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("login.pcapng identity mismatch")

    records = []
    session_shapes = []
    for connection in reconstruct_connections(source):
        if connection["server_endpoint"][1] != 54994:
            continue
        c2s = connection["streams"].get("c2s", b"")
        s2c = connection["streams"].get("s2c", b"")
        if len(c2s) < 0x88:
            continue
        client_number = struct.unpack_from("<I", c2s, 0x84)[0]
        candidates = _frames(s2c)
        acknowledgement = next(
            ((offset, frame) for offset, frame in candidates if offset == ACK_STREAM_OFFSET and len(frame) == OUTER_LENGTH),
            None,
        )
        if acknowledgement is None:
            raise ValueError("lobby acknowledgement boundary not found")
        offset, ciphertext = acknowledgement
        plaintext = ciphertext[:PAYLOAD_OFFSET] + _decrypt(ciphertext[PAYLOAD_OFFSET:], client_number)
        records.append(plaintext)
        session_shapes.append(
            {
                "streamOffset": offset,
                "outerLength": len(plaintext),
                "followingStreamOffset": offset + len(plaintext),
            }
        )

    if len(records) != 2:
        raise ValueError(f"expected two retained lobby acknowledgements, found {len(records)}")

    fixture = {
        "format": FORMAT,
        "source": {
            "id": "pcap-1.23b",
            "artifact": "login.pcapng",
            "sha256": SOURCE_SHA256,
            "retainedSessionCount": 2,
        },
        "sessions": session_shapes,
        "record": {
            "outerLength": OUTER_LENGTH,
            "outerHeader": {
                "offset": 0,
                "length": 16,
                "markerHex": records[0][0:4].hex(),
                "sizeFieldOffset": 4,
                "subrecordCountFieldOffset": 6,
                "subrecordCount": _read_u16(records[0], 6),
            },
            "subrecord": {
                "offset": 16,
                "length": _read_u16(records[0], 16),
                "headerLength": 16,
                "typeFieldOffset": 18,
                "type": _read_u16(records[0], 18),
            },
            "encryptedPayload": {
                "offset": PAYLOAD_OFFSET,
                "length": OUTER_LENGTH - PAYLOAD_OFFSET,
                "blockSize": BLOCK_SIZE,
            },
        },
        "crossSession": {
            "byteComparisonSpans": _comparison_spans(records[0], records[1]),
            "repeatedAlignedValueGroups": _repeat_groups(records),
        },
        "redactedClasses": REDACTED_CLASSES,
    }
    validate_fixture(fixture)
    return fixture


def _all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_strings(item)


def _validate_no_sensitive_strings(fixture: dict) -> None:
    for text in _all_strings(fixture):
        if HEX_SECRET_RE.search(text):
            if text != SOURCE_SHA256:
                raise ValueError("fixture contains a token-like hexadecimal string")
        for candidate in IPV4_RE.findall(text):
            try:
                ipaddress.ip_address(candidate)
            except ValueError:
                continue
            raise ValueError("fixture contains an IPv4 address")
        if any(ord(character) < 0x20 and character not in "\t\n\r" for character in text):
            raise ValueError("fixture contains a C0 control character")
        if not text.isascii():
            raise ValueError("fixture contains non-ASCII text")


def validate_fixture(fixture: dict) -> None:
    if fixture.get("format") != FORMAT:
        raise ValueError("unexpected fixture format")
    if fixture.get("source", {}).get("retainedSessionCount") != 2 or len(fixture.get("sessions", [])) != 2:
        raise ValueError("fixture must describe both retained sessions")
    record = fixture.get("record", {})
    outer = record.get("outerHeader", {})
    subrecord = record.get("subrecord", {})
    payload = record.get("encryptedPayload", {})
    if record.get("outerLength") != OUTER_LENGTH:
        raise ValueError("outer acknowledgement length shifted")
    if outer != {
        "offset": 0,
        "length": 16,
        "markerHex": "00000000",
        "sizeFieldOffset": 4,
        "subrecordCountFieldOffset": 6,
        "subrecordCount": 1,
    }:
        raise ValueError("outer acknowledgement header changed")
    if subrecord != {
        "offset": 16,
        "length": 656,
        "headerLength": 16,
        "typeFieldOffset": 18,
        "type": 10,
    }:
        raise ValueError("acknowledgement subrecord boundary or marker changed")
    if payload != {"offset": 32, "length": 640, "blockSize": 8}:
        raise ValueError("encrypted acknowledgement payload boundary shifted")
    for session in fixture["sessions"]:
        if session != {"streamOffset": 40, "outerLength": 672, "followingStreamOffset": 712}:
            raise ValueError("retained session acknowledgement boundary changed")

    spans = fixture.get("crossSession", {}).get("byteComparisonSpans", [])
    if not spans or spans[0] != {"kind": "invariant", "offset": 0, "length": 32}:
        raise ValueError("clear invariant header span changed")
    cursor = 0
    for span in spans:
        if span.get("kind") not in {"invariant", "dynamic"} or span.get("offset") != cursor or span.get("length", 0) <= 0:
            raise ValueError("comparison spans are not an exact contiguous partition")
        cursor += span["length"]
    if cursor != OUTER_LENGTH:
        raise ValueError("comparison spans do not cover the acknowledgement")
    if not any(span["kind"] == "dynamic" for span in spans):
        raise ValueError("comparison spans omit session-varying bytes")

    groups = fixture.get("crossSession", {}).get("repeatedAlignedValueGroups", [])
    if not groups:
        raise ValueError("repeated-value structure is missing")
    for group in groups:
        offsets = group.get("offsets", [])
        if group.get("unitLength") != BLOCK_SIZE or len(offsets) < 2:
            raise ValueError("invalid repeated-value group")
        if offsets != sorted(offsets) or any(offset < PAYLOAD_OFFSET or offset % BLOCK_SIZE for offset in offsets):
            raise ValueError("repeated-value offsets are invalid")
        if not isinstance(group.get("valueVariesAcrossSessions"), bool):
            raise ValueError("repeated-value variance is missing")
    _validate_no_sensitive_strings(fixture)
    if fixture.get("redactedClasses") != REDACTED_CLASSES:
        raise ValueError("redacted class boundary changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the committed fixture")
    parser.add_argument("--public-shape", action="store_true", help="validate without restricted source bytes")
    args = parser.parse_args()

    committed = None
    if OUTPUT.exists():
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        validate_fixture(committed)
    elif args.check or args.public_shape:
        print("lobby acknowledgement structure: committed fixture missing", file=sys.stderr)
        return 1
    if args.public_shape:
        print("lobby acknowledgement structure: public fixture valid; restricted reproduction skipped")
        return 0

    reproduced = build_fixture()
    rendered = json.dumps(reproduced, indent=2, sort_keys=True) + "\n"
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            print("lobby acknowledgement structure: regenerated bytes differ", file=sys.stderr)
            return 1
        print("lobby acknowledgement structure: restricted fixture reproduced")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8", newline="\n")
    print("lobby acknowledgement structure: wrote sanitized fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
