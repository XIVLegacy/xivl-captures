#!/usr/bin/env python3
"""Build the sanitized c2s 0x012D EventStart join study from the retail captures.

Output carries counts only: event names, selector values, server-codes fields,
and the 0x00CC and 0x00CD target messages that precede each EventStart. Actor
ids, payload bytes, and timestamps stay out of the products.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools" / "extractors"
OBJECTS = Path(
    os.environ.get(
        "XIVL_PCAP_OBJECTS_DIR", REPO_ROOT / "sources" / "pcap-1.23b" / "objects"
    )
)
MANIFEST = REPO_ROOT / "sources" / "pcap-1.23b" / "manifest.yaml"
SAMPLES = REPO_ROOT / "derived" / "payload_samples.json"
STUDY_ID = "c2s-012d-event-start"
OUT = REPO_ROOT / "studies" / STUDY_ID / "derived"

sys.path.insert(0, str(TOOLS))

GENERATOR_VERSION = "1"
OPCODE_START = 0x012D
OPCODE_LOCK = 0x00CC
OPCODE_SET = 0x00CD
START_LEN = 200
TARGET_LEN = 24
# Offsets count from the first byte of the 16-byte game-message header.
TRIGGER_OFFSET = 0x10
OWNER_OFFSET = 0x14
SERVER_CODES_OFFSET = 0x18
SELECTOR_OFFSET = 0x20
NAME_OFFSET = 0x21
NAME_LEN = 0x20
TARGET_ACTOR_OFFSET = 0x10
TARGET_OTHER_OFFSET = 0x14
ZONE_SHIFT = 22
LOW_MASK = (1 << ZONE_SHIFT) - 1
SAMPLE_KEY_CAP = 60
SAMPLE_CAPTURE_CAP = 4
NAME_RE = re.compile(rb"^[A-Za-z][A-Za-z0-9]*$")
TALK_NAME = "talkDefault"
CLEAR_SENTINEL = 0xE0000000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_start(message: bytes) -> dict:
    """Decode the join fields of one c2s 0x012D game message."""
    if len(message) != START_LEN:
        raise ValueError(f"unexpected 0x012D length {len(message)}")
    raw_name = message[NAME_OFFSET : NAME_OFFSET + NAME_LEN].split(b"\0", 1)[0]
    if not NAME_RE.match(raw_name):
        raise ValueError("event name is not an identifier")
    (server_codes,) = struct.unpack_from("<I", message, SERVER_CODES_OFFSET)
    (owner,) = struct.unpack_from("<I", message, OWNER_OFFSET)
    return {
        "name": raw_name.decode("ascii"),
        "selector": message[SELECTOR_OFFSET],
        "owner": owner,
        "server_codes": server_codes,
    }


def decode_target(message: bytes) -> dict:
    if len(message) != TARGET_LEN:
        raise ValueError(f"unexpected target message length {len(message)}")
    actor, other = struct.unpack_from("<II", message, TARGET_ACTOR_OFFSET)
    return {"actor": actor, "other": other}


def split_codes(server_codes: int) -> tuple[int, int]:
    return server_codes >> ZONE_SHIFT, server_codes & LOW_MASK


def find_starts(messages: list[tuple[int, bytes]]) -> list[dict]:
    """Decode each 0x012D with the target messages since the previous 0x012D."""
    starts = []
    window_begin = 0
    for index, (opcode, body) in enumerate(messages):
        if opcode != OPCODE_START:
            continue
        start = decode_start(body)
        start["body"] = body
        lock = set_target = None
        lock_at = set_at = None
        for back in range(index - 1, window_begin - 1, -1):
            kind, other_body = messages[back]
            if kind == OPCODE_LOCK and lock is None:
                lock, lock_at = decode_target(other_body), back
            elif kind == OPCODE_SET and set_target is None:
                set_target, set_at = decode_target(other_body), back
        start["lock"] = lock
        start["lock_gap"] = None if lock_at is None else index - lock_at
        start["set"] = set_target
        start["set_before_lock"] = (
            set_at is not None and lock_at is not None and set_at < lock_at
        )
        starts.append(start)
        window_begin = index + 1
    return starts


def join_rows(starts: list[dict]) -> list[dict]:
    counts = Counter(
        (s["name"], s["selector"], *split_codes(s["server_codes"])) for s in starts
    )
    return [
        {
            "event_name": name,
            "selector": selector,
            "zone_field": zone,
            "low22": low,
            "count": count,
        }
        for (name, selector, zone, low), count in sorted(counts.items())
    ]


def summarize(starts: list[dict]) -> dict:
    by_name: dict[str, Counter] = {}
    for s in starts:
        by_name.setdefault(s["name"], Counter())[str(s["selector"])] += 1
    low = [split_codes(s["server_codes"])[1] for s in starts]
    return {
        "messages": len(starts),
        "selector_by_event_name": {
            name: dict(sorted(c.items(), key=lambda kv: int(kv[0])))
            for name, c in sorted(by_name.items())
        },
        "server_codes_low22_zero": sum(1 for v in low if v == 0),
        "server_codes_low22_nonzero": sum(1 for v in low if v != 0),
        "zone_field_counts": {
            str(k): v
            for k, v in sorted(
                Counter(split_codes(s["server_codes"])[0] for s in starts).items()
            )
        },
        "joins": join_rows(starts),
    }


def other_class(value: int) -> str:
    """Class the second target dword so no actor id reaches the products."""
    if value == 0:
        return "zero"
    if value == CLEAR_SENTINEL:
        return "0xe0000000"
    return "other"


def target_summary(starts: list[dict]) -> dict:
    """Count the 0x00CC and 0x00CD relations to the owner actor for talk starts."""
    groups: dict[str, list[dict]] = {}
    for s in starts:
        if s["name"] == TALK_NAME:
            groups.setdefault(f"selector {s['selector']}", []).append(s)
    result = {}
    for label, rows in sorted(groups.items(), key=lambda kv: int(kv[0].split()[1])):
        lock_rows = [r for r in rows if r["lock"] is not None]
        set_rows = [r for r in rows if r["set"] is not None]
        result[label] = {
            "messages": len(rows),
            "lock_since_previous_start": len(lock_rows),
            "lock_immediately_before": sum(1 for r in rows if r["lock_gap"] == 1),
            "lock_actor_equals_owner": sum(
                1 for r in lock_rows if r["lock"]["actor"] == r["owner"]
            ),
            "lock_second_dword": dict(
                sorted(
                    Counter(other_class(r["lock"]["other"]) for r in lock_rows).items()
                )
            ),
            "set_since_previous_start": len(set_rows),
            "set_actor_equals_owner": sum(
                1 for r in set_rows if r["set"]["actor"] == r["owner"]
            ),
            "set_second_dword": dict(
                sorted(
                    Counter(other_class(r["set"]["other"]) for r in set_rows).items()
                )
            ),
            "set_before_lock": sum(1 for r in rows if r["set_before_lock"]),
        }
    return result


def sample_joins(picks: list[dict]) -> list[dict]:
    """Join each published payload sample, by its index, to its event name."""
    rows = []
    for index, pick in enumerate(picks):
        zone, low = split_codes(pick["server_codes"])
        rows.append(
            {
                "index": index,
                "capture": pick["capture"],
                "event_name": pick["name"],
                "selector": pick["selector"],
                "zone_field": zone,
                "low22": low,
            }
        )
    return rows


def published_sample_picks(per_capture: list[tuple[str, list[dict]]]) -> list[dict]:
    """Reproduce the sampler of derived/payload_samples.json for c2s 0x012D."""
    picked = []
    for _name, starts in per_capture:
        taken = 0
        for start in starts:
            if len(picked) >= SAMPLE_KEY_CAP:
                return picked
            if taken >= SAMPLE_CAPTURE_CAP:
                break
            picked.append(start)
            taken += 1
    return picked


def walk_messages(path: Path) -> list[tuple[int, bytes, str]]:
    from extract_payload_samples import walk_capture_payloads  # type: ignore

    return [
        (r["opcode"], bytes.fromhex(r["bytes"]), r["capture"])
        for r in walk_capture_payloads(path)
        if r["direction"] == "c2s"
    ]


def load_manifest_members() -> dict:
    import yaml

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    return {m["file"]: m for m in manifest.get("members", [])}


def published_sample_bytes() -> list[tuple[str, bytes]]:
    data = json.loads(SAMPLES.read_text(encoding="utf-8"))
    entry = data["samples"]["c2s"][f"0x{OPCODE_START:04x}"]
    return [(s["capture"], bytes.fromhex(s["bytes"])) for s in entry["samples"]]


def build_accounting() -> dict:
    from extract_payload_samples import scrub_text_bytes  # type: ignore

    members = load_manifest_members()
    per_capture = []
    captures = {}
    for name in sorted(members):
        path = OBJECTS / name
        if sha256(path) != members[name]["sha256"]:
            raise ValueError(f"{name}: SHA-256 differs from the source manifest")
        messages = walk_messages(path)
        pairs = [(op, body) for op, body, _ in messages]
        for op, body in pairs:
            if op in (OPCODE_LOCK, OPCODE_SET):
                decode_target(body)
        starts = find_starts(pairs)
        for start in starts:
            start["capture"] = name
        if starts:
            per_capture.append((name, starts))
            captures[name] = {
                "sha256": members[name]["sha256"],
                "size_bytes": members[name]["size_bytes"],
                "messages": len(starts),
            }
    corpus = [s for _, starts in per_capture for s in starts]
    picks = published_sample_picks(per_capture)
    published = published_sample_bytes()
    if len(picks) != len(published):
        raise ValueError("published sample count differs from the reproduced sampler")
    for pick, (pub_cap, pub) in zip(picks, published):
        if pick["capture"] != pub_cap or scrub_text_bytes(pick["body"]) != pub:
            raise ValueError("published sample differs from the reproduced sampler")
    return {
        "study": STUDY_ID,
        "generator_version": GENERATOR_VERSION,
        "evidence_class": "packet-capture",
        "opcode": "0x012d",
        "direction": "c2s",
        "message_length": START_LEN,
        "captures": captures,
        "corpus": summarize(corpus),
        "targets": target_summary(corpus),
        "published_samples": {**summarize(picks), "sample_joins": sample_joins(picks)},
    }


def render_verdicts(acc: dict) -> str:
    corpus, samples = acc["corpus"], acc["published_samples"]

    def selector_table(summary: dict) -> list[str]:
        values = sorted(
            {int(s) for c in summary["selector_by_event_name"].values() for s in c}
        )
        lines = [
            "| Event name | "
            + " | ".join(f"selector {v}" for v in values)
            + " | Messages |",
            "|---|" + "---:|" * (len(values) + 1),
        ]
        for name, counts in summary["selector_by_event_name"].items():
            cells = " | ".join(str(counts.get(str(v), 0)) for v in values)
            lines.append(f"| `{name}` | {cells} | {sum(counts.values())} |")
        return lines

    def join_table(summary: dict) -> list[str]:
        lines = [
            "| Event name | Selector | Zone field | Low 22 bits | Messages |",
            "|---|---:|---:|---:|---:|",
        ]
        for row in summary["joins"]:
            lines.append(
                f"| `{row['event_name']}` | {row['selector']} | {row['zone_field']} "
                f"| {row['low22']} | {row['count']} |"
            )
        return lines

    lines = [
        "# Client EventStart 0x012D Joins",
        "",
        "Every figure below is aggregated from the sent client-to-server `0x012d`",
        "messages in the retail captures. The products hold counts only. They hold",
        "no actor ids, timestamps, or payload bytes.",
        "",
        "## Record shape",
        "",
        f"Every message is {acc['message_length']} bytes: the 16-byte game-message",
        "header and a 184-byte payload. Offsets below count from the first byte of",
        "the header. The payload offset is the header offset minus 16.",
        "",
        "| Offset | Size | Field |",
        "|---:|---:|---|",
        "| 0x10 | 4 | trigger actor |",
        "| 0x14 | 4 | owner actor |",
        "| 0x18 | 4 | server codes |",
        "| 0x1c | 4 | parameter CRC32 |",
        "| 0x20 | 1 | selector |",
        "| 0x21 | 32 | event name, zero padded |",
        "| 0x41 | 128 | parameter window |",
        "",
        "The selector is the byte at payload offset 0x10. The server codes field is",
        "split into a zone field, its high 10 bits, and the low 22 bits.",
        "",
        "## Capture set",
        "",
        f"{corpus['messages']} messages in {len(acc['captures'])} captures. The published",
        f"payload samples hold {samples['messages']} of them. The sampler keeps at most 4",
        "per capture, in stream order, from the captures in file name order.",
        "",
        "| Capture | SHA-256 | Messages |",
        "|---|---|---:|",
    ]
    for name, cap in acc["captures"].items():
        lines.append(f"| `{name}` | `{cap['sha256']}` | {cap['messages']} |")
    lines += [
        "",
        "## Selector by event name",
        "",
        "All messages.",
        "",
        *selector_table(corpus),
        "",
        "The 60 published payload samples zero-fill every event name of four or more",
        "letters, so the name join below comes from the captures and is checked",
        "against the samples byte for byte after the same zero-fill.",
        "",
        "Published samples only.",
        "",
        *selector_table(samples),
        "",
        "## Server codes",
        "",
        "| Quantity | All messages | Published samples |",
        "|---|---:|---:|",
        f"| Low 22 bits zero | {corpus['server_codes_low22_zero']} "
        f"| {samples['server_codes_low22_zero']} |",
        f"| Low 22 bits nonzero | {corpus['server_codes_low22_nonzero']} "
        f"| {samples['server_codes_low22_nonzero']} |",
        "",
        "Zone field values, with message counts.",
        "",
        "| Zone field | All messages | Published samples |",
        "|---:|---:|---:|",
    ]
    zones = sorted(
        set(corpus["zone_field_counts"]) | set(samples["zone_field_counts"]), key=int
    )
    for z in zones:
        lines.append(
            f"| {z} | {corpus['zone_field_counts'].get(z, 0)} "
            f"| {samples['zone_field_counts'].get(z, 0)} |"
        )
    lines += [
        "",
        "## Joins",
        "",
        "Event name, selector, zone field, and low 22 bits, with message counts.",
        "",
        "All messages.",
        "",
        *join_table(corpus),
        "",
        "Published samples only.",
        "",
        *join_table(samples),
        "",
        "## Target messages before each talkDefault",
        "",
        "For each `talkDefault` EventStart, the client-to-server messages since the",
        "previous EventStart in the same capture are searched for the nearest",
        "`0x00cc` lock and the nearest `0x00cd` set. Each carries two dwords, the",
        "actor id and a second value. The second value is classed as zero,",
        "`0xe0000000`, or other so no actor id appears. Stream order is the",
        "reconstructed client-to-server order of wrapped-actor messages. The",
        "owner is the EventStart owner actor.",
        "",
        "| Group | Messages | Lock found | Lock immediately before "
        "| Lock actor is owner | Set found | Set actor is owner | Set before lock |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, t in acc["targets"].items():
        lines.append(
            f"| `{label}` | {t['messages']} | {t['lock_since_previous_start']} "
            f"| {t['lock_immediately_before']} | {t['lock_actor_equals_owner']} "
            f"| {t['set_since_previous_start']} | {t['set_actor_equals_owner']} "
            f"| {t['set_before_lock']} |"
        )
    lines += [
        "",
        "| Group | Lock second dword | Set second dword |",
        "|---|---|---|",
    ]
    for label, t in acc["targets"].items():
        lock = ", ".join(f"{k} x{v}" for k, v in t["lock_second_dword"].items())
        sett = ", ".join(f"{k} x{v}" for k, v in t["set_second_dword"].items())
        lines.append(f"| `{label}` | {lock or 'none'} | {sett or 'none'} |")
    lines += [
        "",
        "## Not established",
        "",
        "- Whether the zone field equals a zone id. No capture records its zone",
        "  next to this field in a tracked product.",
        "- The meaning of selector 101 and of the nonzero low 22 bits.",
        "- The order of the client target messages against server messages. Only",
        "  the client-to-server stream is ordered here.",
        "- Whether the client sends the lock and set messages as part of the",
        "  talk trigger or only as a side effect of targeting.",
        "- Whether the selector follows the trigger kind or the event name.",
        "- Any trigger kind absent from the captures, including emote events.",
        "",
    ]
    return "\n".join(lines)


def render_products(acc: dict) -> dict[str, bytes]:
    return {
        "accounting.json": (json.dumps(acc, indent=2, sort_keys=True) + "\n").encode(
            "ascii"
        ),
        "verdicts.md": render_verdicts(acc).encode("ascii"),
    }


def build_outputs() -> dict[str, bytes]:
    return render_products(build_accounting())


def check_sample_joins(samples: dict) -> None:
    """Check the per-sample joins against derived/payload_samples.json."""
    published = published_sample_bytes()
    joins = samples["sample_joins"]
    if len(joins) != len(published) or samples["messages"] != len(published):
        raise ValueError("sample joins differ in count from payload_samples.json")
    for row, (capture, body) in zip(joins, published):
        if len(body) != START_LEN:
            raise ValueError("published sample has an unexpected length")
        (codes,) = struct.unpack_from("<I", body, SERVER_CODES_OFFSET)
        found = (capture, body[SELECTOR_OFFSET], *split_codes(codes))
        listed = (row["capture"], row["selector"], row["zone_field"], row["low22"])
        if found != listed:
            raise ValueError(f"sample {row['index']} differs from payload_samples.json")
    counted = Counter(
        (r["event_name"], r["selector"], r["zone_field"], r["low22"]) for r in joins
    )
    aggregated = Counter(
        {
            (r["event_name"], r["selector"], r["zone_field"], r["low22"]): r["count"]
            for r in samples["joins"]
        }
    )
    if counted != aggregated:
        raise ValueError("sample joins differ from the aggregated join table")


def validate_public_shape() -> int:
    try:
        acc_path, md_path = OUT / "accounting.json", OUT / "verdicts.md"
        acc = json.loads(acc_path.read_text(encoding="ascii"))
        if acc.get("study") != STUDY_ID:
            raise ValueError("study id changed")
        if md_path.read_bytes() != render_verdicts(acc).encode("ascii"):
            raise ValueError("verdicts.md differs from accounting.json")
        if acc_path.read_bytes() != render_products(acc)["accounting.json"]:
            raise ValueError("accounting.json is not canonically formatted")
        members = load_manifest_members()
        for name, cap in acc["captures"].items():
            if cap["sha256"] != members[name]["sha256"]:
                raise ValueError(f"{name}: source hash differs from manifest")
        for key in ("corpus", "published_samples"):
            summary = acc[key]
            if sum(r["count"] for r in summary["joins"]) != summary["messages"]:
                raise ValueError(f"{key}: join counts do not sum")
            named = sum(
                sum(c.values()) for c in summary["selector_by_event_name"].values()
            )
            if named != summary["messages"]:
                raise ValueError(f"{key}: selector counts do not sum")
        if (
            sum(c["messages"] for c in acc["captures"].values())
            != acc["corpus"]["messages"]
        ):
            raise ValueError("capture message counts do not sum")
        check_sample_joins(acc["published_samples"])
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"c2s 0x012d event start: public shape invalid: {exc}", file=sys.stderr)
        return 1
    print("verified c2s 0x012d event start public shape")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare, write nothing")
    parser.add_argument(
        "--public-shape",
        action="store_true",
        help="validate committed products without capture inputs",
    )
    args = parser.parse_args()
    if args.public_shape:
        return validate_public_shape()
    products = build_outputs()
    stale = []
    for name, expected in products.items():
        target = OUT / name
        if args.check:
            if not target.is_file() or target.read_bytes() != expected:
                stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)
    if stale:
        print("stale c2s 0x012d products: " + ", ".join(stale), file=sys.stderr)
        return 1
    action = "verified" if args.check else "wrote"
    print(f"{action} {len(products)} c2s 0x012d event start products")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
