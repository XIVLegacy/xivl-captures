#!/usr/bin/env python3
"""Reproduce the three retained local Guildleve processPgEvent calls."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from extract_00da_00e1_comparison import (  # noqa: E402
    GAME_MESSAGE_PREAMBLE_LEN,
    INNER_HEADER_LEN,
    _decode_capture,
)

STUDY = "local-guildleve-dialogue"
CAPTURE = "local_leve_complete.pcapng"
CAPTURE_SIZE = 358296
CAPTURE_SHA256 = "4f0793f354140478725bf2c30642a3458a854460f47fb11a7af635c8881d95cd"
PARAMETER_OFFSET = 0x49
PARAMETER_SIZE = 64
EXPECTED_CALLS = [
    (14, 38, 365, 0x151A9000),
    (25, 79, 366, 0x04136000),
    (497, 1734, 368, 0x04140000),
]
EXPECTED_TOTALS = {
    "lanes": 2,
    "c2s_discarded_trailing_stream_bytes": 0,
    "c2s_admitted_unparsed_stream_bytes": 0,
    "c2s_frames": 504,
    "c2s_subevents": 1075,
    "c2s_wrapped_subevents": 1070,
    "s2c_discarded_trailing_stream_bytes": 0,
    "s2c_admitted_unparsed_stream_bytes": 0,
    "s2c_frames": 525,
    "s2c_subevents": 2292,
    "s2c_wrapped_subevents": 2287,
}


def decode_parameters(blob: bytes) -> tuple[list[dict], int]:
    """Decode only the tag forms present in this bounded parameter block."""
    if len(blob) != PARAMETER_SIZE:
        raise ValueError("expected exactly 64 parameter bytes")
    values = []
    offset = 0
    while offset < len(blob):
        tag_offset = offset
        tag = blob[offset]
        offset += 1
        item = {"tag_offset": tag_offset, "tag": tag}
        if tag == 15:
            if any(blob[offset:]):
                raise ValueError("nonzero parameter padding after END")
            return values, tag_offset
        if tag in (0, 6):
            if offset + 4 > len(blob):
                raise ValueError("truncated four-byte parameter")
            value = int.from_bytes(blob[offset : offset + 4], "big")
            item.update(
                type="actor" if tag == 6 else "integer",
                value_offset=offset,
                value=value,
                value_hex=f"0x{value:08X}",
            )
            offset += 4
        elif tag == 2:
            end = blob.find(b"\0", offset)
            if end < 0:
                raise ValueError("unterminated string parameter")
            item.update(
                type="string",
                value_offset=offset,
                value=blob[offset:end].decode("ascii"),
            )
            offset = end + 1
        elif tag == 5:
            item.update(type="nil", value=None)
        else:
            raise ValueError(f"unsupported parameter tag {tag} at {tag_offset}")
        values.append(item)
    raise ValueError("parameter END is absent")


def build_outputs(path: Path) -> dict[str, bytes]:
    data = path.read_bytes()
    if len(data) != CAPTURE_SIZE or hashlib.sha256(data).hexdigest() != CAPTURE_SHA256:
        raise ValueError(f"{CAPTURE} identity mismatch")
    events, totals, lanes = _decode_capture(path)
    if dict(totals) != EXPECTED_TOTALS or lanes != {"chat": 1, "main": 1}:
        raise ValueError("unexpected capture framing or lane accounting")
    calls = []
    function_counts = Counter()
    for event in events:
        application = event.get("sub_body", b"")[
            INNER_HEADER_LEN + GAME_MESSAGE_PREAMBLE_LEN :
        ]
        if event["opcode_value"] == 0x0130:
            function = (
                application[0x29:PARAMETER_OFFSET].split(b"\0", 1)[0].decode("ascii")
            )
            function_counts[function] += 1
        if b"processPgEvent" not in application:
            continue
        if (
            event["opcode_value"] != 0x0130
            or event["lane_index"] != 0
            or event["lane"] != "main"
            or event["direction"] != "s2c"
            or event["subevent_index"] != 0
            or function != "delegateEvent"
            or len(application) != 144
            or int.from_bytes(application[4:8], "little") != 0x44B00005
        ):
            raise ValueError("unexpected processPgEvent envelope")
        parameters = application[PARAMETER_OFFSET : PARAMETER_OFFSET + PARAMETER_SIZE]
        values, end_offset = decode_parameters(parameters)
        observed = [(value["type"], value["value"]) for value in values]
        if observed[:3] != [
            ("actor", 0x029B2941),
            ("actor", 0xA0F1D58A),
            ("string", "processPgEvent"),
        ]:
            raise ValueError("unexpected delegate actors or method")
        if [value["type"] for value in values] != [
            "actor",
            "actor",
            "string",
            "integer",
            "integer",
            "nil",
            "nil",
        ] or end_offset != 38:
            raise ValueError("unexpected typed argument shape")
        if values[3]["tag_offset"] != 26 or values[3]["value_offset"] != 27:
            raise ValueError("unexpected first integer offset")
        location = {key: value for key, value in event.items() if key != "sub_body"}
        location["opcode"] = f"0x{location.pop('opcode_value'):04X}"
        calls.append(
            {
                "location": location,
                "function": function,
                "owner_actor_id_hex": f"0x{int.from_bytes(application[4:8], 'little'):08X}",
                "owner_actor_application_offset": 4,
                "application_prefix_hex": application[:0x29].hex(),
                "application_size": len(application),
                "application_sha256": hashlib.sha256(application).hexdigest(),
                "parameter_application_offset": PARAMETER_OFFSET,
                "parameter_size": PARAMETER_SIZE,
                "parameters_hex": parameters.hex(),
                "parameters_sha256": hashlib.sha256(parameters).hexdigest(),
                "decoded_parameters": values,
                "end_tag_offset": end_offset,
                "zero_padding_size": PARAMETER_SIZE - end_offset - 1,
                "application_tail_hex": application[
                    PARAMETER_OFFSET + PARAMETER_SIZE :
                ].hex(),
            }
        )
    observed_calls = [
        (
            row["location"]["frame_index"],
            row["location"]["capture_packet_index"],
            row["decoded_parameters"][3]["value"],
            row["decoded_parameters"][4]["value"],
        )
        for row in calls
    ]
    if observed_calls != EXPECTED_CALLS:
        raise ValueError("three expected call observations differ")
    accounting = {
        "schema_version": 1,
        "study": STUDY,
        "input": {
            "source": "pcap-1.23b",
            "capture": CAPTURE,
            "sha256": CAPTURE_SHA256,
            "size_bytes": CAPTURE_SIZE,
            "manifest": "sources/pcap-1.23b/manifest.yaml",
        },
        "framing": dict(totals),
        "lanes": lanes,
        "all_admitted_0x0130_function_counts": dict(sorted(function_counts.items())),
        "selected_calls": len(calls),
        "selection": "Every admitted application payload containing the ASCII processPgEvent literal, required to be a main s2c 0x0130 delegateEvent call.",
        "index_convention": "Lane, frame, subevent and direction-event indexes are zero-based; capture packet indexes are one-based. Frame stream offsets are wire bytes; subevent offsets are decoded-frame-body bytes. Parameter offsets are relative to the 64-byte block.",
        "packet_locator": "The earliest captured packet that completes the outer frame in reconstructed TCP sequence space.",
        "boundary": "One retained capture; connection-local stream order only. The second integer's meaning and any client-data source-column selection are unestablished.",
    }
    return {
        name: (json.dumps(value, indent=2) + "\n").encode("ascii")
        for name, value in {"calls.json": calls, "accounting.json": accounting}.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    capture = (
        Path(
            os.environ.get(
                "XIVL_PCAP_OBJECTS_DIR", str(args.repo / "sources/pcap-1.23b/objects")
            )
        )
        / CAPTURE
    )
    out = args.out_dir or args.repo / "studies" / STUDY / "derived"
    outputs = build_outputs(capture)
    if args.check:
        stale = [
            name
            for name, content in outputs.items()
            if not (out / name).is_file() or (out / name).read_bytes() != content
        ]
        if stale:
            raise ValueError("stale study products: " + ", ".join(stale))
    else:
        out.mkdir(parents=True, exist_ok=True)
        for name, content in outputs.items():
            (out / name).write_bytes(content)
    print(
        f"{STUDY}: {'verified' if args.check else 'generated'} {len(outputs)} products"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
