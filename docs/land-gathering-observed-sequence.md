# Selected land-gathering wire sequence

The retained Logging packets show a command request, a judge-mode kick and
request, then selected HarvestJudge delegates and client EventUpdate records.
They establish the typed observations below, without a complete node-click to
first-swing transaction for Mining, Logging, Quarrying and Harvesting.

## Questions and evidence bounds

| Question | Observation or answer | Evidence locator | Confidence | Unknowns |
| --- | --- | --- | --- | --- |
| Judge-mode sequence and replies | Logging has the selected request/kick/delegate sequence below, with six adjacent client EventUpdate observations. Harvesting ended an event before the second command request. | [Request and kick](#request-and-kick), [selected delegates](#selected-delegates-and-adjacent-replies), [request repetition](#request-repetition). | High for typed records and completion order. | Causal reply pairing, complete Mining/Quarrying chains, rendered first swing, duplicate requests while judge mode is open, and a slow-reply automatic retry producer. |
| HarvestJudge message 20 and failures | The canonical script/text finding identifies message 20 as "You failed to obtain anything." and records related failure/end messages. | `xivl-client-scripts:docs/gathering-marker-fishing-ui.md`, [Selected HarvestJudge text](https://github.com/XIVLegacy/xivl-client-scripts/blob/main/docs/gathering-marker-fishing-ui.md#selected-harvestjudge-text). | High for the recorded literal cells and bank. | Server conditions selecting each message and a complete failure-to-text mapping. |
| Tool draw, state and companion packets | Logging packet 58 contains state 50, CommandResult X00 and loadTextData in that subevent order. | [State and result neighborhood](#state-and-result-neighborhood). | High for same-frame co-occurrence. | Necessity or sufficiency for drawing a tool, complete meanings of states 0/2/30+/50, companion X00/X01 requirements, and nearby-player broadcast. |
| Node markers and class eligibility | The recovered MiningPoint consumer maps 1200053/1200055/1200057 to 10/11/12 and returns visible only for 1200057. A separate local depiction path selects an actor-attached marker. | [Marker boundary](#marker-boundary). | High for the authenticated mapping; static scope only. | Universal cross-class visibility, current-main-class gating, native talk/push enable producers, and a retail server RunEventFunction noticeEvent _setMapMarker route. |

## Source identity and packet geometry

Evidence class: `packet-capture`, source `pcap-1.23b`, recorded against retail
1.23b live servers. The [source manifest](../sources/pcap-1.23b/manifest.yaml)
owns provenance and restricted-member distribution. These two exact members
were identity-checked before decoding:

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `gather_wood.pcapng` | 157688 | `c308aa4c984eb3e1912383c06e5115c6924713978df43cdb8075335e1bac7d32` |
| `harvest.pcapng` | 60680 | `8522a844b6904207c3465ae1d1038599eddb8b9dc47800d5230c8a1c3ad0e440` |

All selected records are on main connection 0. Frame, subevent and byte
offsets are zero-based. Capture packet numbers are one-based and identify
the earliest captured packet completing all bytes of the outer frame.
Completion order across directions is an observation, not a causal join.
Stream order remains local to one connection and direction.

Application offsets start after the 16-byte subevent header, 8-byte inner
header and 8-byte game-message preamble. Every selected delegate has a
176-byte subevent and 144-byte application. Its outer selector is
`delegateCommand` in the 32-byte name field at application `+0x29`.
Typed parameters occupy `[0x49,0x89)`, exactly 64 bytes. The following seven
application bytes are outside the typed parameter span and are not arguments.
Each selected EventUpdate has a 120-byte subevent and 88-byte application,
with parameters in `[0x11,0x51)` and seven following bytes outside decoding.

Notation: `i(n)` is tag `0x00` with four big-endian integer bytes (32 bits), `r(bits)`
is tag `0x06` with four bytes of reference bits (32 bits), quoted text is NUL-terminated tag
`0x02`, true/false are tags `0x03`/`0x04`, and nil is the explicit tag
`0x05`. Reference bits alone do not prove a resolved native object or Lua
table. END is a separate `0x0F` tag. It is not an integer argument equal to 15.

## Request and kick

In `gather_wood.pcapng`, main connection 0, the selected completion order is:

| Direction | Completing packet | Frame/subevent; decoded-body offset | Opcode and observation |
| --- | ---: | --- | --- |
| c2s | 33 | 8/1; 64 | `0x012D`, `commandRequest`, owner bits `0xA0F05EED`. |
| s2c | 52 | 10/0; 0 | `0x012F`, KickEvent, containing NUL-terminated `commandJudgeMode` at application `+0x10`. |
| c2s | 54 | 10/1; 64 | `0x012D`, `commandJudgeMode`, owner bits `0xA0F055F3` / qualified command 22003. |
| s2c | 58 | 12/2; 112 | `0x0130`, `delegateCommand`, inner method `loadTextData`. |

The commandRequest application is 184 bytes, with its name at `+0x11` and
128-byte parameters `[0x31,0xB1)`. Its complete emitted vector is
`[i(20002),i(0),nil,nil,r(0x44B00031),nil,nil,nil,nil]`.
END is parameter offset 21, followed by 106 zero padding bytes. Seven
application bytes after the parameter span are separate. These emitted
positions do not recover the original Lua supplied argument count.

The [selected commandJudgeMode request vectors](../studies/director-wire-identity/README.md#selected-commandjudgemode-request-vectors)
own the complete Logging and Harvesting judge-request vectors, their typed
layout and CRC boundary. The selected kick has a 144-byte subevent and
112-byte application. Its other fields have not been assigned a complete
argument layout here. These records do not independently identify a node
click producer or prove that each step caused the next.

## Selected delegates and adjacent replies

Every selected server delegate has trigger field `0x029B2941` at application
`+0`, owner field `0xA0F055F3` at `+4`, event-type byte zero at `+8`, and
event name `commandJudgeMode` at `+9`. Its outer function selector remains
`delegateCommand` at `+0x29`, separate from the inner method key.
The complete typed prefix is
`[r(0xA0F4E204),"method",r(0xA0F055F3)]`. The first reference encodes the
HarvestJudge registry key, the string is the inner method key,
and the final reference is the command-owner reference. The remaining typed
values below follow that prefix. They are not complete Lua argument lists.

The static identity comes from
`xivl-client-data:manifests/staticactor_class_paths.json`, record `id=320004`,
which maps to `/Judge/Harvest/HarvestJudge`. That manifest has SHA-256
`d612438827e5997422ab6f64a807e567ddf1b953c532e8a319d67b93c53c9db0`.
The key rule `0xA0F00000 | low_id` in
`xivl-decomp:docs/resource/static-actor-registry.md`,
[File contract and retail coverage](https://github.com/XIVLegacy/xivl-decomp/blob/main/docs/resource/static-actor-registry.md#file-contract-and-retail-coverage),
gives `0xA0F4E204` for 320004. This static registry identity does not establish
historical object resolution or callback execution.

| Completing s2c packet; frame/subevent; body offset | Inner method | Remaining typed tail | Adjacent c2s 0x012E completing packet; frame/subevent; body offset | Complete typed reply values |
| --- | --- | --- | --- | --- |
| 58; 12/2; 112 | `loadTextData` | `[]` | 59; 12/3; 184 | `[nil]` |
| 76; 20/0; 0 | `openInputWidget` | `[i(22003),i(1)]` | 78; 18/0; 0 | `[true]` |
| 82; 23/1; 72 | `orderInputWidget` | `[i(0),false,i(22003)]` | 83; 20/1; 64 | `[true]` |
| 94; 27/0; 0 | `askInputWidget` | `[i(22003),i(1),i(0),false,false,nil,false]` | 121; 33/2; 120 | `[i(22704),i(20),true]` |
| 126; 36/1; 40 | `orderInputWidget` | `[i(80),false,i(22003)]` | 127; 35/1; 64 | `[true]` |
| 135; 40/0; 0 | `askInputWidget` | `[i(22003),i(2),i(0),false,false,nil,false]` | 200; 60/1; 64 | `[i(22705),i(0xFFFFFFFC),true]` |

Delegate END offsets within the 64-byte parameter span are respectively
24, 37, 39, 45, 39 and 45, followed by 39, 26, 24, 18, 24 and 18 zero padding
bytes. Reply END offsets are respectively 1, 1, 1, 11, 1 and 11, followed by
62, 62, 62, 52, 62 and 52 zero padding bytes. All six replies have application
byte `+0x10` equal to zero. That byte is separate from the typed values.

These are adjacent observations on the selected connection. Event/control
correlation keys were not verified, so the table does not prove causal
callback pairing. `0xFFFFFFFC` has the conditional signed-int32 interpretation
-4; neither the raw token nor that interpretation establishes a named result.

### Lua formals and conditional adaptation

The canonical [HarvestJudge widget calls](https://github.com/XIVLegacy/xivl-client-scripts/blob/main/docs/gathering-marker-fishing-ui.md#harvestjudge-widget-calls)
in `xivl-client-scripts:docs/gathering-marker-fishing-ui.md` own the fixed
formals and return contracts. They distinguish `loadTextData(self,A1,A2)`,
`openInputWidget(self,A1,A2,A3,A4)`,
`orderInputWidget(self,A1,A2,A3,A4,A5)` and
`askInputWidget(self,A1,A2,A3,A4,A5,A6,A7,A8,A9)`.

The conditional native adapter in
`xivl-decomp:docs/script/delegate-command-producer.md`,
[Delegate and callback positions](https://github.com/XIVLegacy/xivl-decomp/blob/main/docs/script/delegate-command-producer.md#delegate-and-callback-positions),
inserts the selected binding's Lua value O as A1, uses the first decoded
reference as self, consumes the method key, and forwards the second decoded
reference as A2. Only then do the remaining typed tails begin at A3. Thus
22003 is conditionally A3 for open/ask and A5 for order. The raw owner or
trigger key alone does not establish O. Successful historical binding,
callable lookup and execution are not proved by parsing these packets.

The static contract says open/order return one result, while ask returns
the two widget values followed by its selection flag, zeroing the first two
only for an exactly-false selection flag. Those recovered routes remain
distinct from the uncorrelated wire observations.

## Request repetition

In `harvest.pcapng`, main connection 0, s2c EndEvent `0x0131` completes in
packet 123, frame 39/subevent 2, decoded-body offset 128. Its subevent is
80 bytes and application is 48 bytes. The second c2s commandRequest completes
in packet 175, frame 45/subevent 1, decoded-body offset 64. It uses owner
`0xA0F05EED` and vector
`[i(20006),i(0),nil,nil,r(0x44B00039),nil,nil,nil,nil]`, END offset 21 and
106 zero padding bytes in the same 128-byte request parameter geometry.

The earlier event-ending record prevents treating this later request as
evidence of an automatic retry while judge mode remained open. Duplicate
request handling and an automatic producer triggered by slow replies remain
unresolved. The retained observations also do not establish a complete
Mining/Quarrying chain or the instant a first swing rendered.

## State and result neighborhood

In Logging packet 58, s2c frame 12, subevents 0/1/2 contain `0x0134`,
`0x013C` and the loadTextData delegate, at decoded-body offsets 0/40/112.
The first has an 8-byte application with main-state byte `+0` equal to 50.
The second is the adopted CommandResult X00 shape: a 72-byte subevent,
40-byte application and row count zero at application `+0x20`.
The [adopted opcode snapshot](../derived/opcode_names.json) supplies the
packet names; `tools/extractors/extract_battle_results.py:decode_packet`
owns the result geometry. The state-byte interpretation is documented by
`xivl-opcodes:opcodes.json`, clientbound `0x0134`, `wire_application`.

This same-frame ordering establishes co-occurrence. It does not prove a tool
draw, that state 50 or X00 is necessary or sufficient for animation, a required
X01 companion, full meanings for state values 0/2/30+/50, or broadcast to
nearby players. Native scene-record broadcasts are not evidence of network
delivery to other clients.

## Marker boundary

The static local consumers are canonical in these findings:

- `xivl-client-scripts:docs/gathering-marker-fishing-ui.md`,
  [Mining-point markers](https://github.com/XIVLegacy/xivl-client-scripts/blob/main/docs/gathering-marker-fishing-ui.md#mining-point-markers).
- `xivl-decomp:docs/actor/map-marker-lanes.md`,
  [Actor-attached path](https://github.com/XIVLegacy/xivl-decomp/blob/main/docs/actor/map-marker-lanes.md#actor-attached-path).

MiningPoint's class mapping and visibility test, and DepictionJudge's local
talkable-marker path, do not establish a universal current-class rule.
Native talk/push enable producers and a historical server `noticeEvent
_setMapMarker` invocation remain unestablished. A local depiction call is
not proof of a server RunEventFunction route.

## Reproduction and decode limits

Use only the two manifest members identified above. Run
`python tools/validate_framing.py sources/pcap-1.23b/objects/gather_wood.pcapng sources/pcap-1.23b/objects/harvest.pcapng`
before extracting selected records. Canonical framing reported zero
compression-flag mismatches. After reconstruction, both members had zero
admitted unparsed stream bytes, truncated subevents, short wrapped inner
headers and compressed-frame inflation failures.

Canonical reconstruction discarded six trailing s2c bytes per member,
outside complete frames. The framing CLI sees already-trimmed streams and
therefore reports zero trailing bytes. The admitted main/chat connection
totals were 224 c2s and 241 s2c frames for gather_wood, and 72 c2s and 90 s2c
frames for harvest. Selected application records were all complete.

Use `reconstruct_lanes`, `parse_outer_frames`, `maybe_inflate` and
`parse_sub_events` through
`tools/extractors/extract_00da_00e1_comparison.py:_decode_capture` for the
locators and earliest completing-packet calculation. Select only main
connection 0 and the frame/subevent pairs above. Decode the stated parameter
spans through END, checking each leaf boundary and zero padding. Preserve
the seven-byte application remainder separately from arguments.

The decoder was inspected at repository revision
`9b40150d7f3fa4dc0ed1f014bbf6988df897e4d0`. The reconstruction resolves
overlaps canonically; no alternate overlap reconstruction was performed.
Neither aggregate sequence motifs nor concatenated connection blocks supply
capture-wide chronology. No new live-client observation or full-corpus
negative search is claimed.
