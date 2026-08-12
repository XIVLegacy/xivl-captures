"""Print one direction's sub-events without merging directions or collapsing runs.

Connection blocks remain separate but are concatenated deterministically.
"""

from __future__ import annotations

import argparse
import struct
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from extract_streams import maybe_inflate, parse_outer_frames, reconstruct  # type: ignore
from extract_observations import (  # type: ignore
    SUB_EVENT_CLASS_ACTOR_WRAPPED,
    SUB_EVENT_HEADER_LEN,
    INNER_HEADER_LEN,
)


class SubEvent:
    """One actor-wrapped game sub-event, with the fields order questions need."""

    __slots__ = ("index", "frame", "direction", "opcode", "sourceId")

    def __init__(self, index, frame, direction, opcode, sourceId):
        self.index     = index
        self.frame     = frame
        self.direction = direction
        self.opcode    = opcode
        self.sourceId  = sourceId


def walk_wire_order(pcap_path: Path, direction: str = "s2c") -> list[SubEvent]:
    """Return stream-ordered sub-events in deterministic connection blocks."""
    blob = reconstruct(pcap_path).get(direction, b"")
    events: list[SubEvent] = []
    for frameIndex, frame in enumerate(parse_outer_frames(blob)):
        # Wire fact: inflate from zlib magic, not outer type; compression is lane-specific.
        body = maybe_inflate(frame["body"])
        if body is None:
            body = frame["body"]

        offset = 0
        while offset + SUB_EVENT_HEADER_LEN <= len(body):
            size, eventType = struct.unpack_from("<HH", body, offset)
            if size < SUB_EVENT_HEADER_LEN or offset + size > len(body):
                break
            if eventType == SUB_EVENT_CLASS_ACTOR_WRAPPED and \
                    size >= SUB_EVENT_HEADER_LEN + INNER_HEADER_LEN:
                # Wire fact: source actor id is in the sub-event header. The opcode follows in the inner header.
                sourceId = struct.unpack_from("<I", body, offset + 4)[0]
                opcode   = struct.unpack_from("<H", body, offset + SUB_EVENT_HEADER_LEN + 2)[0]
                events.append(SubEvent(len(events), frameIndex, direction, opcode, sourceId))
            offset += size
    return events


def render(events: list[SubEvent], anchors: list[int], before: int, after: int, selfOnly: bool) -> str:
    """Render the full run, or a window around each anchor occurrence."""
    if not anchors:
        windows = [(0, len(events), None)]
    else:
        windows = [
            (max(0, i - before), min(len(events), i + after + 1), events[i])
            for i in anchors
        ]

    out: list[str] = []
    for start, end, anchor in windows:
        if anchor is not None:
            out.append(
                f"--- 0x{anchor.opcode:04x} at index {anchor.index} "
                f"frame {anchor.frame} source 0x{anchor.sourceId:08x} ---"
            )
        for event in events[start:end]:
            if selfOnly and anchor is not None and event.sourceId != anchor.sourceId:
                continue
            marker = "SELF" if anchor is not None and event.sourceId == anchor.sourceId else "    "
            out.append(
                f"  {event.index:6d} frame={event.frame:<6d} {marker} "
                f"0x{event.opcode:04x} source=0x{event.sourceId:08x}"
            )
        out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Print a capture's sub-events in the order they were sent.")
    ap.add_argument("pcap", help="Path to a .pcapng file")
    ap.add_argument("--direction", default="s2c", choices=("s2c", "c2s"))
    ap.add_argument("--around", default="",
                    help="Anchor opcode, e.g. 0x0005; prints a window per occurrence")
    ap.add_argument("--before", type=int, default=4, help="Sub-events before each anchor")
    ap.add_argument("--after", type=int, default=80, help="Sub-events after each anchor")
    ap.add_argument("--actor", default="all", choices=("all", "self"),
                    help="self keeps only the anchor's own source actor")
    args = ap.parse_args()

    pcap_path = Path(args.pcap)
    if not pcap_path.is_file():
        print(f"not a file: {pcap_path}", file=sys.stderr)
        return 1

    events = walk_wire_order(pcap_path, args.direction)
    if not events:
        print(f"no {args.direction} sub-events decoded", file=sys.stderr)
        return 1

    anchors: list[int] = []
    if args.around:
        wanted = int(args.around, 16) if args.around.lower().startswith("0x") else int(args.around)
        anchors = [i for i, event in enumerate(events) if event.opcode == wanted]
        if not anchors:
            print(f"opcode 0x{wanted:04x} not found in {args.direction}", file=sys.stderr)
            return 1

    print(f"=== {pcap_path.name} {args.direction}: {len(events)} sub-events, "
          f"{len(anchors)} anchor(s) ===")
    print(render(events, anchors, args.before, args.after, args.actor == "self"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
