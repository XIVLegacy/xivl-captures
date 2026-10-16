#!/usr/bin/env python3
"""Census retained processPgEvent calls and reproduce their bounded exchanges."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from extract_00da_00e1_comparison import (  # noqa: E402
    GAME_MESSAGE_PREAMBLE_LEN,
    INNER_HEADER_LEN,
    _decode_capture,
    corpus_digest,
)

from extract_observations import parse_sub_events  # noqa: E402
from extract_streams import (  # noqa: E402
    GAME_SERVER_PORT,
    _server_endpoint,
    clear_packet_cache,
    maybe_inflate,
    parse_outer_frames,
    read_packets,
    reconstruct_lanes,
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


def application_bytes(event: dict) -> bytes:
    return event.get("sub_body", b"")[INNER_HEADER_LEN + GAME_MESSAGE_PREAMBLE_LEN :]


def event_location(event: dict) -> dict:
    location = {key: value for key, value in event.items() if key != "sub_body"}
    location["opcode"] = f"0x{location.pop('opcode_value'):04X}"
    return location


def capture_admission(path: Path) -> dict:
    """Account for payload-bearing TCP connections without publishing endpoints."""
    connection_ports = {}
    for packet in read_packets(path):
        if not packet.haslayer("IP") or not packet.haslayer("TCP"):
            continue
        tcp = packet["TCP"]
        if not bytes(tcp.payload):
            continue
        ip = packet["IP"]
        key = tuple(sorted(((ip.src, tcp.sport), (ip.dst, tcp.dport))))
        connection_ports[key] = _server_endpoint(*key)[1]
    lanes = reconstruct_lanes(path)
    admitted = {
        tuple(sorted((lane["client_endpoint"], lane["server_endpoint"])))
        for lane in lanes
    }
    excluded = Counter(
        (
            "non-game-server-port"
            if port != GAME_SERVER_PORT
            else "no-admitted-game-frames",
            port,
        )
        for key, port in connection_ports.items()
        if key not in admitted
    )
    frame_counts = Counter()
    decoded_body_padding = Counter()
    for lane in lanes:
        for direction, blob in lane["streams"].items():
            for frame in parse_outer_frames(blob):
                inflated = maybe_inflate(frame["body"])
                flag = frame["marker"][1]
                if flag not in (0, 1) or (flag == 1) != (inflated is not None):
                    raise ValueError(f"{path.name}: compression flag/body mismatch")
                body = inflated if inflated is not None else frame["body"]
                parsed = parse_sub_events(body)
                consumed = sum(event.get("size", 0) for event in parsed)
                if any(body[consumed:]):
                    raise ValueError(
                        f"{path.name}: nonzero unparsed decoded-frame bytes"
                    )
                decoded_body_padding[direction] += len(body) - consumed
                frame_counts[
                    f"{direction}_compressed_frames"
                    if flag
                    else f"{direction}_raw_frames"
                ] += 1
    return {
        "payload_bearing_tcp_connections": len(connection_ports),
        "admitted_connections": len(admitted),
        "excluded_connections": [
            {"reason": reason, "server_port": port, "count": count}
            for (reason, port), count in sorted(excluded.items())
        ],
        "compression": dict(sorted(frame_counts.items())),
        "compression_flag_mismatches": 0,
        "decoded_frame_zero_padding_bytes": dict(sorted(decoded_body_padding.items())),
    }


def survey_corpus(
    repo: Path, objects: Path, selected_events, selected_totals, selected_lanes
) -> dict:
    manifest = yaml.safe_load(
        (repo / "sources/pcap-1.23b/manifest.yaml").read_text(encoding="utf-8")
    )
    members = manifest["members"]
    if len(members) != 54 or len({member["file"] for member in members}) != 54:
        raise ValueError("expected 54 distinct manifest members")
    rows = []
    aggregate = Counter()
    occurrences = []
    paths = []
    for member in sorted(members, key=lambda row: row["file"]):
        name = member["file"]
        if Path(name).name != name:
            raise ValueError("source member must be a root-level file")
        path = objects / name
        data = path.read_bytes()
        if (
            len(data) != member["size_bytes"]
            or hashlib.sha256(data).hexdigest() != member["sha256"]
        ):
            raise ValueError(f"{name}: manifest identity mismatch")
        row = {"capture": name, "size_bytes": len(data), "sha256": member["sha256"]}
        if path.suffix.lower() not in (".pcap", ".pcapng"):
            row["status"] = "excluded-non-pcap-member"
            rows.append(row)
            continue
        paths.append(path)
        if name == CAPTURE:
            events, totals, lanes = selected_events, selected_totals, selected_lanes
        else:
            events, totals, lanes = _decode_capture(path)
        for direction in ("c2s", "s2c"):
            for key in (
                "admitted_unparsed_stream_bytes",
                "compressed_frame_inflate_failures",
                "subevent_truncations",
                "wrapped_short_inner_headers",
            ):
                if totals[f"{direction}_{key}"]:
                    raise ValueError(f"{name}: unexpected {direction} {key}")
        function_counts = Counter()
        hits = []
        for event in events:
            app = application_bytes(event)
            if event["opcode_value"] == 0x0130:
                if len(app) < PARAMETER_OFFSET:
                    raise ValueError(f"{name}: short RunEvent application")
                function_counts[
                    app[0x29:PARAMETER_OFFSET].split(b"\0", 1)[0].decode("ascii")
                ] += 1
            if b"processPgEvent" in app:
                hits.append(event_location(event))
        occurrences.extend(hits)
        row.update(
            status="decoded-clear-game-lanes",
            lanes=lanes,
            framing=dict(totals),
            admission=capture_admission(path),
            decoder_failures={
                f"{direction}_{key}": totals[f"{direction}_{key}"]
                for direction in ("c2s", "s2c")
                for key in (
                    "compressed_frame_inflate_failures",
                    "subevent_truncations",
                    "wrapped_short_inner_headers",
                )
            },
            processPgEvent_occurrences=hits,
            all_admitted_0x0130_function_counts=dict(sorted(function_counts.items())),
        )
        aggregate.update(totals)
        rows.append(row)
        clear_packet_cache()
    expected = [
        (CAPTURE, "main", "s2c", frame, packet)
        for frame, packet, _, _ in EXPECTED_CALLS
    ]
    actual = [
        (
            event["capture"],
            event["lane"],
            event["direction"],
            event["frame_index"],
            event["capture_packet_index"],
        )
        for event in occurrences
    ]
    if (
        actual != expected
        or len(paths) != 54
        or aggregate["lanes"] != 84
        or aggregate["s2c_discarded_trailing_stream_bytes"] != 228
        or aggregate["c2s_discarded_trailing_stream_bytes"] != 0
    ):
        raise ValueError("complete corpus reconciliation changed")
    return {
        "manifest": "sources/pcap-1.23b/manifest.yaml",
        "manifest_members": len(members),
        "pcap_members": len(paths),
        "non_pcap_members": len(members) - len(paths),
        "corpus_digest_sha256": corpus_digest(paths),
        "framing": dict(aggregate),
        "selected_occurrences": len(occurrences),
        "members": rows,
        "scope": "Every manifest member is identity-checked; every PCAP member is decoded through canonical clear port-54992 game admission. Non-game TCP connections and non-PCAP members are separate exclusions. Unlisted local files are outside scope. TLS and lobby plaintext are not searched.",
    }


def exchange_row(event: dict) -> dict:
    app = application_bytes(event)
    opcode = event["opcode_value"]
    row = {
        "location": event_location(event),
        "application_size": len(app),
        "application_hex": app.hex(),
        "application_sha256": hashlib.sha256(app).hexdigest(),
    }
    if opcode == 0x012D:
        if (
            app[17:29] != b"talkDefault\0"
            or int.from_bytes(app[4:8], "little") != 0x44B00005
        ):
            raise ValueError("unexpected bounded EventStart")
        row.update(
            event_name="talkDefault",
            owner_actor_id_hex="0x44B00005",
            owner_actor_application_offset=4,
        )
    elif opcode in (0x012E, 0x0130):
        offset = 17 if opcode == 0x012E else PARAMETER_OFFSET
        parameters = app[offset : offset + PARAMETER_SIZE]
        values, end = decode_parameters(parameters)
        row.update(
            parameter_application_offset=offset,
            parameter_size=PARAMETER_SIZE,
            parameters_hex=parameters.hex(),
            decoded_parameters=values,
            end_tag_offset=end,
            application_tail_hex=app[offset + PARAMETER_SIZE :].hex(),
        )
        if opcode == 0x012E:
            row["application_byte_16"] = app[16]
        else:
            row.update(
                function=app[0x29:PARAMETER_OFFSET].split(b"\0", 1)[0].decode("ascii"),
                owner_actor_id_hex=f"0x{int.from_bytes(app[4:8], 'little'):08X}",
                owner_actor_application_offset=4,
            )
    return row


def build_exchanges(events: list[dict]) -> dict:
    # Windows are pinned observations in each direction, not merged sequence offsets.
    windows = [((5, 33), (6, 30)), ((458, 475), (490, 505))]
    result = []
    for c2s_bounds, s2c_bounds in windows:
        directions = {}
        for direction, bounds in (("c2s", c2s_bounds), ("s2c", s2c_bounds)):
            selected = []
            for event in events:
                if (
                    event["lane_index"] != 0
                    or event["direction"] != direction
                    or not bounds[0] <= event["frame_index"] <= bounds[1]
                ):
                    continue
                opcode = event["opcode_value"]
                app = application_bytes(event)
                if direction == "c2s" and opcode in (0x012D, 0x012E):
                    selected.append(exchange_row(event))
                elif (
                    direction == "s2c"
                    and opcode == 0x0130
                    and int.from_bytes(app[4:8], "little") == 0x44B00005
                ):
                    selected.append(exchange_row(event))
                elif (
                    direction == "s2c"
                    and opcode == 0x0131
                    and app[9:21] == b"talkDefault\0"
                ):
                    selected.append(exchange_row(event))
            directions[direction] = selected
        result.append({"owner_actor_id_hex": "0x44B00005", "directions": directions})
    first, second = [window["directions"] for window in result]
    if [
        [row["location"]["capture_packet_index"] for row in window[direction]]
        for window in (first, second)
        for direction in ("c2s", "s2c")
    ] != [
        [16, 28, 35, 43, 75, 86, 90],
        [19, 30, 38, 49, 79, 89, 93],
        [1698, 1722, 1728, 1747, 1752],
        [1701, 1724, 1734, 1751, 1758],
    ]:
        raise ValueError("bounded exchange locators changed")
    comparisons = []
    for label, left, right, prefix_size in (
        ("EventStart", first["c2s"][0], second["c2s"][0], 184),
        ("switchEvent", first["s2c"][0], second["s2c"][0], 144),
        ("welcomeTalk", first["s2c"][1], second["s2c"][1], 144),
        ("integer-result-EventUpdate", first["c2s"][1], second["c2s"][1], 81),
    ):
        a, b = (
            bytes.fromhex(left["application_hex"]),
            bytes.fromhex(right["application_hex"]),
        )
        if a[:prefix_size] != b[:prefix_size] or (
            label == "integer-result-EventUpdate" and a[81:] == b[81:]
        ):
            raise ValueError("bounded exchange payload comparison changed")
        comparisons.append(
            {
                "comparison": label,
                "capture_packet_indexes": [
                    left["location"]["capture_packet_index"],
                    right["location"]["capture_packet_index"],
                ],
                "equal_application_prefix_size": prefix_size,
                "equal_prefix_sha256": hashlib.sha256(a[:prefix_size]).hexdigest(),
                "complete_application_equal": a == b,
                "remaining_application_hex": [
                    a[prefix_size:].hex(),
                    b[prefix_size:].hex(),
                ],
            }
        )
    for window in (first, second):
        if [
            (value["type"], value["value"])
            for value in window["c2s"][1]["decoded_parameters"]
        ] != [("integer", 0), ("integer", 2)]:
            raise ValueError("unexpected EventUpdate integer results")
        if any(
            [(value["type"], value["value"]) for value in row["decoded_parameters"]]
            != [("nil", None)]
            for row in window["c2s"][2:]
        ):
            raise ValueError("unexpected bounded nil result")
    return {
        "schema_version": 1,
        "study": STUDY,
        "capture": CAPTURE,
        "windows": result,
        "comparisons": comparisons,
        "association": "Each direction is in reconstructed lane-0 stream order. The two explicit windows retain every c2s EventStart/EventUpdate and owner-matching s2c RunEvent, plus the talkDefault end. EventUpdate carries no owner field identified here; membership is bounded context, not a proved response/callback pairing.",
        "packet_provenance": "Capture packet indexes identify earliest frame-completion packets. Cross-direction packet comparisons describe captured provenance, not the server's receive or execution order.",
        "producer_boundary": "processPgEvent and its two integers are observed on server-to-client 0x0130. The capture does not expose server code, server state, a source-column selector, or a binding from owner 0x44B00005 to a client-data actor class.",
    }


def build_outputs(path: Path, repo: Path = REPO_ROOT) -> dict[str, bytes]:
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
        "boundary": "The complete manifest-admitted clear-game corpus is censused. Exchange order is per connection direction; packet provenance does not prove server causality. Client-data source-column selection remains unestablished.",
        "consumer_interpretation": {
            "citation": "xivl-client-scripts:docs/passivegl-craft-columns.md#supplied-dialogue-consumer",
            "qualification": "Raw bytecode establishes text-ID and scheduler positional use, not runtime scheduler execution or source-column selection.",
        },
        "corpus": survey_corpus(repo, path.parent, events, totals, lanes),
    }
    return {
        name: (json.dumps(value, indent=2) + "\n").encode("ascii")
        for name, value in {
            "calls.json": calls,
            "accounting.json": accounting,
            "exchanges.json": build_exchanges(events),
        }.items()
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
    outputs = build_outputs(capture, args.repo)
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
