# Map 0x0193 Clock/Value Contract

## Study contents

This study exhaustively decodes every admitted server-to-client `0x0193`
occurrence in all 54 preserved retail captures. It publishes only packet
ordering, the two application u32 values, the packet-header clock, modular
arithmetic, sentinel status, and bounded clock deltas.

## Start here

- `derived/accounting.json` - complete corpus, lane, exclusion, distribution,
  clock-correlation, and per-capture accounting.
- `derived/occurrences.csv` - one sanitized row per valid event.
- `derived/neighborhoods.csv` - three preceding and following wrapped events
  from the same reconstructed s2c lane.
- `derived/verdicts.md` - promoted arithmetic conclusion and exact boundary.

Regenerate or verify the products:

```text
python tools/extractors/extract_0193_clock_contract.py
python tools/extractors/extract_0193_clock_contract.py --check
```

## Source material

The packet source is `pcap-1.23b`, selected by the canonical sorted corpus
reducer and admitted by the shared clear TCP 54992 lane filter. TCP sequence
reconstruction removes retransmitted duplicate bytes before framing. Capture
time is assigned from the first packet that completes every byte of the
reconstructed outer frame.

The retail client route and arithmetic are recorded in
[client opcode semantics](https://github.com/XIVLegacy/xivl-opcodes/blob/0a093847d97a23dbeea5347cb072c03f0f0c030f/data/client_opcode_semantics.json)
under `s2c-0193`. The packet-header clock model is recorded in
[the native timing analysis](https://github.com/XIVLegacy/xivl-decomp/blob/37eeb2ba68c7a0ab4cd7b1c79c92d346090a6a91/docs/actor/cast-timing-clock.md).
Lua endpoint subtraction and presentation divisions are recorded in
[the timer consumer catalog](https://github.com/XIVLegacy/xivl-client-scripts/blob/c0624f13eb8a3641deeb6e2680cb8b5ce28c036f/manifests/myplayer_timer_consumers.json).

Those sources establish different layers. Native code establishes arithmetic
and storage. Lua establishes consumer presentation. This capture study tests
the wire values and their relationship to capture chronology. None of those
layers alone establishes server policy.

## Promoted conclusions

All nine events have the fixed 40-byte wrapped shape and 8-byte application
payload. The packet-header clock equals the floor of the outer-header numeric
value divided by 1000 in every event and is within 0.627 seconds of
frame-completion capture time. This places the inner clock in the
Unix-compatible whole-second domain and establishes millisecond scaling for
the outer value in these target frames without assigning the outer field
globally. The application value is an offset in that integer unit. The
non-sentinel arithmetic result is an absolute Unix-compatible sum; the
observed `0x12` path stores that sum as an endpoint.

The single `0x12` event supplies value 900. Its derived sum is 900.013696
seconds after frame completion. The eight `0x14` events contain values 2 or
15, but their branch does not establish storage or presentation of the sum.

## Claim boundary

No target occurs in `login.pcapng`, and no public artifact joins any other
capture to that capture's lobby connection or a same-session `SERVER_UTC`
value. Numeric proximity across files is not a session identity.

The study does not infer eligibility, resets, content availability, login
causality, timer nouns, or server scheduling from filenames or UI text. A
same-session packet, independent server-clock anchor, and directly linked
transition at the derived value are required to test server policy. A retained
sentinel-bearing event is separately required to observe the exceptional wire
case.

## Sanitization

Public rows contain no raw payload, endpoint address, actor identifier, player
name, token, session identifier, or capture timestamp field. Capture
identifiers are the canonical public manifest filenames. The required header
clock and exact delta permit reconstruction of capture completion time; that
is an explicit consequence of publishing the requested structural facts.

## Topics

- Complete retained-corpus `0x0193` accounting
- Packet-header and outer-header clock correlation
- Modular addition and sentinel handling
- Retransmission-safe compound framing

## Evidence gaps

The corpus contains no `0xffffffff` application value, no target in the login
capture, and no independently observed transition at a derived endpoint.

## Further research

A same-session clock anchor and endpoint transition would test server policy.
A sentinel-bearing event would test the exceptional wire path.

## Verification

Repository validation reproduces all four products, validates their schema and
checksum, and runs focused tests for modular addition, the sentinel, malformed
shape rejection, retransmission-safe frame completion, compound framing,
sanitized output, and schema mutation.
