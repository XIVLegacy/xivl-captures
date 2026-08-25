#!/usr/bin/env python3
"""Reproduce the sanitized decrypted lobby record census."""

from __future__ import annotations

import argparse
from collections import defaultdict
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
OUTPUT = REPO_ROOT / "studies/lobby-handshake-triage/derived/lobby-record-census.json"
SOURCE_SHA256 = "28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62"
FORMAT = "xivl-lobby-record-census-v1"
OUTER_HEADER_LENGTH = 16
SUBRECORD_HEADER_LENGTH = 16
BLOCK_SIZE = 8
TRANSFORMED_LENGTH_MASK = 0xFFE0
CLIENT_NUMBER_STREAM_OFFSET = 0x84
TICKET_FIELD_STREAM_OFFSET = 0x44
TICKET_FIELD_LENGTH = 32
TRANSFORMED_PAYLOAD_TYPES = {3, 10}
PRE_KEY_PLAINTEXT_TYPES = {7, 9}
ZERO_EXTENT_TYPES = {8}
REDACTED_CLASSES = [
    "session tokens",
    "character and session names",
    "network addresses and ports",
    "cryptographic keys and key inputs",
    "opaque payload values and plaintext hashes",
]
HEX_SECRET_RE = re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{32,}(?![0-9a-f])")
IPV4_RE = re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)")

SHARED_IDS = {
    ("c2s", 648, ((632, 9, 0, None),)): "c2s-0009",
    ("c2s", 192, ((176, 3, 160, 5),)): "c2s-0003-0005",
    ("c2s", 40, ((24, 8, 0, None),)): "c2s-0008",
    ("s2c", 40, ((24, 7, 0, None),)): "s2c-0007",
    ("s2c", 672, ((656, 10, 640, None),)): "s2c-000a",
    ("s2c", 640, ((624, 3, 608, 12),)): "s2c-0003-000c",
}
EXPECTED_SHARED_POST_ACKNOWLEDGEMENT = [
    {"direction": "c2s", "clearType": 3, "innerOpcode": 5},
    {"direction": "c2s", "clearType": 8},
    {"direction": "s2c", "clearType": 3, "innerOpcode": 12},
]


def _read_u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _normalized_key(client_number: int, ticket_field: bytes) -> bytes:
    if len(ticket_field) != TICKET_FIELD_LENGTH:
        raise ValueError("initial ticket field length changed")
    material = struct.pack("<III", 0x12345678, client_number, 1000)
    material += ticket_field
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


def _decrypt(payload: bytes, client_number: int, ticket_field: bytes) -> bytes:
    try:
        from Crypto.Cipher import Blowfish
    except ImportError as exc:
        raise RuntimeError(
            "PyCryptodome is required to reproduce the restricted fixture; "
            "install tools/requirements.txt"
        ) from exc

    cipher = Blowfish.new(_normalized_key(client_number, ticket_field), Blowfish.MODE_ECB)
    output = bytearray()
    for offset in range(0, len(payload), BLOCK_SIZE):
        block = payload[offset : offset + BLOCK_SIZE]
        output.extend(_swap_words(cipher.decrypt(_swap_words(block))))
    return bytes(output)


def _comparison_spans(left: bytes, right: bytes) -> list[dict]:
    if len(left) != len(right) or not left:
        raise ValueError("comparison records must have the same nonzero length")
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
        for offset in range(32, len(record), BLOCK_SIZE):
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


def _frame_signature(direction: str, frame: dict) -> tuple:
    return (
        direction,
        frame["outerLength"],
        tuple(
            (
                record["declaredLength"],
                record["clearType"],
                record["encryptedExtent"]["length"],
                record.get("innerOpcode"),
            )
            for record in frame["subrecords"]
        ),
    )


def _parse_direction(
    stream: bytes,
    direction: str,
    client_number: int,
    ticket_field: bytes,
) -> tuple[dict, list[bytes]]:
    offset = 0
    frames = []
    acknowledgement_records = []
    while offset < len(stream):
        if offset + OUTER_HEADER_LENGTH > len(stream):
            raise ValueError("lobby stream ends inside an outer header")
        outer_length = _read_u16(stream, offset + 4)
        subrecord_count = _read_u16(stream, offset + 6)
        if outer_length < OUTER_HEADER_LENGTH or offset + outer_length > len(stream):
            raise ValueError("lobby stream ends inside an outer frame")
        raw_frame = stream[offset : offset + outer_length]
        frame = {
            "frameIndex": len(frames),
            "streamOffset": offset,
            "outerLength": outer_length,
            "subrecordCount": subrecord_count,
            "subrecords": [],
        }
        cursor = OUTER_HEADER_LENGTH
        for subrecord_index in range(subrecord_count):
            if cursor + SUBRECORD_HEADER_LENGTH > outer_length:
                raise ValueError("lobby frame ends inside a subrecord header")
            declared_length = _read_u16(raw_frame, cursor)
            clear_type = _read_u16(raw_frame, cursor + 2)
            if declared_length < SUBRECORD_HEADER_LENGTH or cursor + declared_length > outer_length:
                raise ValueError("lobby frame ends inside a subrecord")
            payload = raw_frame[cursor + SUBRECORD_HEADER_LENGTH : cursor + declared_length]
            encrypted_length = 0
            plaintext = payload
            if clear_type in TRANSFORMED_PAYLOAD_TYPES:
                encrypted_length = len(payload) & TRANSFORMED_LENGTH_MASK
                plaintext = _decrypt(payload[:encrypted_length], client_number, ticket_field) + payload[encrypted_length:]
            elif clear_type not in PRE_KEY_PLAINTEXT_TYPES | ZERO_EXTENT_TYPES:
                raise ValueError(f"unclassified clear lobby type {clear_type}")
            record = {
                "subrecordIndex": subrecord_index,
                "frameOffset": cursor,
                "streamOffset": offset + cursor,
                "declaredLength": declared_length,
                "clearType": clear_type,
                "encryptedExtent": {
                    "offset": SUBRECORD_HEADER_LENGTH,
                    "length": encrypted_length,
                },
            }
            if clear_type == 3:
                if len(plaintext) < 16:
                    raise ValueError("type-0x0003 payload lacks its inner header")
                record["innerOpcode"] = _read_u16(plaintext, 2)
            frame["subrecords"].append(record)
            if clear_type == 10:
                acknowledgement_records.append(raw_frame[cursor : cursor + 16] + plaintext)
            cursor += declared_length
        if cursor != outer_length:
            raise ValueError("subrecords do not cover their outer frame")
        frames.append(frame)
        offset += outer_length
    return {
        "direction": direction,
        "streamLength": len(stream),
        "completeFrameLength": offset,
        "frames": frames,
    }, acknowledgement_records


def _shared_shapes(sessions: list[dict]) -> list[dict]:
    occurrences = defaultdict(list)
    for session in sessions:
        for direction in session["directions"]:
            for frame in direction["frames"]:
                occurrences[_frame_signature(direction["direction"], frame)].append({
                    "sessionId": session["id"],
                    "frameIndex": frame["frameIndex"],
                    "streamOffset": frame["streamOffset"],
                })
    shared = []
    for signature, found in occurrences.items():
        if len({item["sessionId"] for item in found}) != len(sessions):
            continue
        if signature not in SHARED_IDS:
            raise ValueError("shared lobby frame shape lacks a stable numeric id")
        direction, outer_length, records = signature
        shared.append({
            "id": SHARED_IDS[signature],
            "direction": direction,
            "outerLength": outer_length,
            "subrecords": [
                {
                    "declaredLength": declared,
                    "clearType": clear_type,
                    "encryptedLength": encrypted,
                    **({"innerOpcode": inner} if inner is not None else {}),
                }
                for declared, clear_type, encrypted, inner in records
            ],
            "occurrences": found,
        })
    return sorted(shared, key=lambda item: item["id"])


def build_fixture(source: Path = SOURCE) -> dict:
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("login.pcapng identity mismatch")

    connections = [
        connection
        for connection in reconstruct_connections(source)
        if connection["server_endpoint"][1] == 54994
    ]
    if len(connections) != 2:
        raise ValueError(f"expected two retained lobby connections, found {len(connections)}")

    sessions = []
    acknowledgement_records = []
    for session_index, connection in enumerate(connections, 1):
        c2s = connection["streams"].get("c2s", b"")
        if len(c2s) < CLIENT_NUMBER_STREAM_OFFSET + 4:
            raise ValueError("initial client lobby record is too short")
        client_number = struct.unpack_from("<I", c2s, CLIENT_NUMBER_STREAM_OFFSET)[0]
        ticket_field = c2s[
            TICKET_FIELD_STREAM_OFFSET : TICKET_FIELD_STREAM_OFFSET + TICKET_FIELD_LENGTH
        ]
        directions = []
        session_acknowledgements = []
        for direction in ("c2s", "s2c"):
            stream = connection["streams"].get(direction)
            if stream is None:
                raise ValueError(f"retained lobby connection lacks {direction}")
            parsed, acknowledgements = _parse_direction(stream, direction, client_number, ticket_field)
            directions.append(parsed)
            session_acknowledgements.extend(acknowledgements)
        initial = directions[0]["frames"][0]["subrecords"]
        if len(initial) != 1 or initial[0]["clearType"] != 9:
            raise ValueError("client-number locator is not inside the initial type-0x0009 record")
        if len(session_acknowledgements) != 1:
            raise ValueError("retained session lacks one acknowledgement")
        acknowledgement_frame = directions[1]["frames"][1]
        raw_header = connection["streams"]["s2c"][
            acknowledgement_frame["streamOffset"] : acknowledgement_frame["streamOffset"] + 16
        ]
        acknowledgement_records.append(raw_header + session_acknowledgements[0])
        sessions.append({"id": f"session-{session_index}", "directions": directions})

    fixture = {
        "format": FORMAT,
        "source": {
            "id": "pcap-1.23b",
            "artifact": "login.pcapng",
            "sha256": SOURCE_SHA256,
            "retainedSessionCount": 2,
        },
        "crypto": {
            "blockSize": BLOCK_SIZE,
            "transformedLengthMask": TRANSFORMED_LENGTH_MASK,
            "subrecordPayloadOffset": SUBRECORD_HEADER_LENGTH,
            "transformedPayloadClearTypes": sorted(TRANSFORMED_PAYLOAD_TYPES),
            "preKeyPlaintextClearTypes": sorted(PRE_KEY_PLAINTEXT_TYPES),
            "observedZeroExtentClearTypes": sorted(ZERO_EXTENT_TYPES),
        },
        "inventory": {
            "completeFrameCount": sum(
                len(direction["frames"])
                for session in sessions
                for direction in session["directions"]
            ),
            "subrecordCount": sum(
                frame["subrecordCount"]
                for session in sessions
                for direction in session["directions"]
                for frame in direction["frames"]
            ),
        },
        "sessions": sessions,
        "crossSession": {
            "sharedFrameShapes": _shared_shapes(sessions),
            "sharedPostAcknowledgementSubrecords": EXPECTED_SHARED_POST_ACKNOWLEDGEMENT,
            "acknowledgementComparison": {
                "byteComparisonSpans": _comparison_spans(*acknowledgement_records),
                "repeatedAlignedValueGroups": _repeat_groups(acknowledgement_records),
            },
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
        if HEX_SECRET_RE.search(text) and text != SOURCE_SHA256:
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


def _expected_session_shapes() -> list:
    return [
        [
            ("c2s", 880, [(0, 648, [(16, 632, 9, 0, None)]), (648, 192, [(16, 176, 3, 160, 5)]), (840, 40, [(16, 24, 8, 0, None)])]),
            ("s2c", 1352, [(0, 40, [(16, 24, 7, 0, None)]), (40, 672, [(16, 656, 10, 640, None)]), (712, 640, [(16, 624, 3, 608, 12)])]),
        ],
        [
            ("c2s", 1016, [(0, 648, [(16, 632, 9, 0, None)]), (648, 40, [(16, 24, 8, 0, None)]), (688, 192, [(16, 176, 3, 160, 5)]), (880, 64, [(16, 48, 3, 32, 3)]), (944, 72, [(16, 56, 3, 32, 4)])]),
            ("s2c", 4624, [(0, 40, [(16, 24, 7, 0, None)]), (40, 672, [(16, 656, 10, 640, None)]), (712, 640, [(16, 624, 3, 608, 12)]), (1352, 3072, [(16, 528, 3, 512, 21), (544, 528, 3, 512, 21), (1072, 528, 3, 512, 22), (1600, 496, 3, 480, 23), (2096, 976, 3, 960, 13)]), (4424, 200, [(16, 184, 3, 160, 15)])]),
        ],
    ]


def _session_shapes(fixture: dict) -> list:
    shapes = []
    for session in fixture.get("sessions", []):
        directions = []
        for direction in session.get("directions", []):
            frames = []
            for frame in direction.get("frames", []):
                records = [
                    (
                        record.get("frameOffset"),
                        record.get("declaredLength"),
                        record.get("clearType"),
                        record.get("encryptedExtent", {}).get("length"),
                        record.get("innerOpcode"),
                    )
                    for record in frame.get("subrecords", [])
                ]
                frames.append((frame.get("streamOffset"), frame.get("outerLength"), records))
            directions.append((direction.get("direction"), direction.get("streamLength"), frames))
        shapes.append(directions)
    return shapes


def validate_fixture(fixture: dict) -> None:
    if fixture.get("format") != FORMAT:
        raise ValueError("unexpected fixture format")
    source = fixture.get("source", {})
    if source != {
        "id": "pcap-1.23b",
        "artifact": "login.pcapng",
        "sha256": SOURCE_SHA256,
        "retainedSessionCount": 2,
    }:
        raise ValueError("source boundary changed")
    if fixture.get("crypto") != {
        "blockSize": 8,
        "transformedLengthMask": 65504,
        "subrecordPayloadOffset": 16,
        "transformedPayloadClearTypes": [3, 10],
        "preKeyPlaintextClearTypes": [7, 9],
        "observedZeroExtentClearTypes": [8],
    }:
        raise ValueError("crypto boundary changed")
    if fixture.get("inventory") != {"completeFrameCount": 16, "subrecordCount": 20}:
        raise ValueError("inventory count changed")
    if _session_shapes(fixture) != _expected_session_shapes():
        raise ValueError("lobby frame or subrecord census changed")

    for session_index, session in enumerate(fixture["sessions"], 1):
        if session.get("id") != f"session-{session_index}":
            raise ValueError("session id changed")
        for direction in session["directions"]:
            cursor = 0
            for frame_index, frame in enumerate(direction["frames"]):
                if frame.get("frameIndex") != frame_index or frame.get("streamOffset") != cursor:
                    raise ValueError("frames are not in exact stream order")
                if frame.get("subrecordCount") != len(frame.get("subrecords", [])):
                    raise ValueError("subrecord count changed")
                frame_cursor = OUTER_HEADER_LENGTH
                for record_index, record in enumerate(frame["subrecords"]):
                    if record.get("subrecordIndex") != record_index or record.get("frameOffset") != frame_cursor:
                        raise ValueError("subrecords are not in exact frame order")
                    if record.get("streamOffset") != frame["streamOffset"] + frame_cursor:
                        raise ValueError("subrecord stream offset changed")
                    extent = record.get("encryptedExtent", {})
                    if extent.get("offset") != SUBRECORD_HEADER_LENGTH or extent.get("length", -1) % 32:
                        raise ValueError("encrypted extent changed")
                    frame_cursor += record["declaredLength"]
                if frame_cursor != frame["outerLength"]:
                    raise ValueError("subrecords do not cover their outer frame")
                cursor += frame["outerLength"]
            if cursor != direction.get("streamLength") or cursor != direction.get("completeFrameLength"):
                raise ValueError("complete frame coverage changed")

    cross_session = fixture.get("crossSession", {})
    shared = cross_session.get("sharedFrameShapes", [])
    if [item.get("id") for item in shared] != sorted(SHARED_IDS.values()):
        raise ValueError("cross-session frame correspondence changed")
    for item in shared:
        if len(item.get("occurrences", [])) != 2 or {
            occurrence.get("sessionId") for occurrence in item["occurrences"]
        } != {"session-1", "session-2"}:
            raise ValueError("shared frame shape does not cover both sessions")
    if cross_session.get("sharedPostAcknowledgementSubrecords") != EXPECTED_SHARED_POST_ACKNOWLEDGEMENT:
        raise ValueError("shared post-acknowledgement census changed")

    comparison = cross_session.get("acknowledgementComparison", {})
    spans = comparison.get("byteComparisonSpans", [])
    if not spans or spans[0] != {"kind": "invariant", "offset": 0, "length": 32}:
        raise ValueError("acknowledgement clear invariant span changed")
    cursor = 0
    for span in spans:
        if span.get("kind") not in {"invariant", "dynamic"} or span.get("offset") != cursor or span.get("length", 0) <= 0:
            raise ValueError("acknowledgement spans are not a contiguous partition")
        cursor += span["length"]
    if cursor != 672 or not any(span["kind"] == "dynamic" for span in spans):
        raise ValueError("acknowledgement spans do not cover the record")
    groups = comparison.get("repeatedAlignedValueGroups", [])
    if not groups:
        raise ValueError("acknowledgement repeated-value structure is missing")
    for group in groups:
        offsets = group.get("offsets", [])
        if group.get("unitLength") != BLOCK_SIZE or len(offsets) < 2:
            raise ValueError("invalid repeated-value group")
        if offsets != sorted(offsets) or any(offset < 32 or offset % BLOCK_SIZE for offset in offsets):
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

    if OUTPUT.exists():
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        validate_fixture(committed)
    elif args.check or args.public_shape:
        print("lobby record census: committed fixture missing", file=sys.stderr)
        return 1
    if args.public_shape:
        print("lobby record census: public fixture valid; restricted reproduction skipped")
        return 0

    reproduced = build_fixture()
    rendered = json.dumps(reproduced, indent=2, sort_keys=True) + "\n"
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            print("lobby record census: regenerated bytes differ", file=sys.stderr)
            return 1
        print("lobby record census: restricted fixture reproduced")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8", newline="\n")
    print("lobby record census: wrote sanitized fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
