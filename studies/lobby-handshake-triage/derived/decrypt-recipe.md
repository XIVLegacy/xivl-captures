# Lobby Decrypt Recipe

## Source

- Evidence class: packet capture.
- Artifact: `sources/pcap-1.23b/objects/login.pcapng`.
- Identity: SHA-256 `28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62`.
- Provenance: `sources/pcap-1.23b/manifest.yaml`, source id `pcap-1.23b`, recorded against retail 1.23b live servers.

## Verdict

`CONFIRMED`. The recovered recipe below decrypts both raw lobby connections in
`login.pcapng` into coherent plaintext. It is confirmed by the literal
`FINAL FANTASY XIV`, version string `2012.09.19.0001`, a 64-hex-character
session token, character names, and the world-server handoff string.

The previous `INCONCLUSIVE` result is retained below as the historical record
of the first recipe test. That verdict was correct on the evidence then
available. The old recipe is superseded because it hashed only 28 bytes of the
ticket field, while the client hashes the full 44-byte zero-padded field.

## Verified recipe

For both connections in `login.pcapng` (SHA-256
`28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62`):

    buf44 = LE32(0x12345678) | LE32(clientNumber) | LE32(1000)
            | "Test Ticket Data" (exact 16 bytes) | 16 zero bytes
            -> exactly 44 bytes
    key = MD5(buf44), 16 raw digest bytes
    cipher = Blowfish ECB, 16 rounds
    body = outer frame at +0x28 (0x18 outer header + 0x10 clear sub-event header)
    length processed = len & 0xFFE0

The key schedule sign-extends key bytes with `MOVSX` when a byte is at least
`0x80`. `clientNumber` is the little-endian dword at cleartext body `+0x5C`.

| Connection | clientNumber | key |
|---|---:|---|
| `192.168.1.101:36160` | 1356916754 (`0x50E0E812`) | `b4ee3f6c016f5bd971500db185a2ab43` |
| `192.168.1.101:36162` | 1356916763 (`0x50E0E81B`) | `17a66dfb75f3d3663d9deb1e06c42791` |

The recovered plaintext confirms:

- the literal `FINAL FANTASY XIV`;
- the version string `2012.09.19.0001`;
- a 64-hex-character session token in the client-to-server frame;
- character names in the first server-to-client frame; and
- a world-server handoff string of the form `createCallbackObject...[<ipv4>:<port>]`.

The 608-byte server frame decrypts to a short header followed by zero padding,
matching its measured 8-byte block repetition.

The client-side implementation is cataloged by `BCS-Y-0008`
(`LobbyCryptEngine::SetSessionKey` at `0x00DA1670`) and `BCS-Y-0013`
(`BF_set_key` at `0x0045ABF0`). `BCS-Y-0013` records the `MOVSX` sign-extension
quirk used by the key schedule.

## Why the old recipe failed

The old record's material order, endianness, `1000` constant, and body boundary
were correct. Its MD5 input stopped at the end of the ticket string, covering
28 bytes; the client hashes the full zero-padded 44-byte field. MD5 over 44
bytes is unrelated to MD5 over 28 bytes, so the old keys
`1ca5adbcaa7e27b2a3d57f52794ed28c` and
`a9193258afa38fe0966b2200dcdfde11` were reproducible but wrong.

The isolation matrix could not find this defect because every swept axis held
the input length at or below the ticket, and none exercised key-schedule byte
handling. The earlier `INCONCLUSIVE` verdict was therefore correct on the
evidence then available.

## Historical superseded recipe record

The following sections preserve the original refuted-recipe observations and
negative matrix. They document the evidence available before the recovered
44-byte input and sign-extension behavior were known.

### Historical verdict

`INCONCLUSIVE`. The documented raw-MD5 Blowfish recipe with constant `1000`
does not decrypt the held lobby ciphertext into structurally coherent data.
Bounded body-boundary, input-encoding, mode, and constant variations also
fail. This refutes the tested recipe as a complete construction, but does not
isolate or refute the `1000` input on its own because no alternative recovered
plaintext.

### Capture-native key inputs

The first lobby connection obtains `clientNumber` 1356916754 from the final little-endian dword of packet 824's 40-byte server payload and from packet 833 frame offset `0x84`. The repeat connection obtains 1356916763 at the same locations in packets 853 and 874. The changing values rule out treating the input as a fixed executable constant.

Packets 833 and 874 carry the ASCII ticket phrase `Test Ticket Data` at frame offset `0x44`. The phrase occupies the start of a zero-padded field; the tested canonical input stops before the first zero byte.

The remaining inputs are the prescribed little-endian constants `0x12345678` and `0x000003e8`. MD5 over the concatenated bytes produces raw Blowfish keys `1ca5adbcaa7e27b2a3d57f52794ed28c` for the first connection and `a9193258afa38fe0966b2200dcdfde11` for the repeat connection.

### Ciphertext and result

For the first connection, packet 836 carries the 672-byte outer frame at reconstructed server stream offset `0x28`. Its 16-byte outer header ends at `0x38`, its 16-byte clear sub-event header ends at `0x48`, and the tested encrypted region is the following 640 bytes through `0x2c7`. Raw-MD5 Blowfish-ECB decryption begins `d3 c3 9f 1e c2 18 c1 f7 73 d3 4e 35 09 6e 48 46`; the full result remains high-entropy and contains no recognizable fixed header or capture-native client number, constants, or ticket phrase.

Packet 842 supplies a second 608-byte target at stream offset `0x2e8`. The repeat connection supplies the corresponding 640-byte and 608-byte targets in packets 877 and 883. All four raw-MD5 ECB results fail the same structural checks. Decrypting from the outer body instead of after the clear sub-event header also fails.

As robustness checks, zero-IV CBC, CFB64, and OFB were tried with the raw digest. ECB and zero-IV CBC were also tried with lowercase and uppercase 32-byte MD5 hex keys and ticket inputs terminated or padded to the visible field widths. None produced a coherent record or capture-native literal. These negative variants do not define a new recipe; they show that the canonical failure is not repaired by the common encoding ambiguities visible in this capture.

### Bounded isolation matrix

The 2026-08-15 isolation pass first reproduced both documented keys from the
wire inputs. The MD5 material order is little-endian `0x12345678`, the
connection's little-endian client number, little-endian `1000`, then the exact
16-byte `Test Ticket Data` string. It produced keys
`1ca5adbcaa7e27b2a3d57f52794ed28c` and
`a9193258afa38fe0966b2200dcdfde11`, matching the earlier pass.

The following matrices were tested independently against all four target
bodies:

| Stage | Variations | Result |
|---|---|---|
| Body boundary | Outer-body starts `0`, `8`, `16`, `24`, and `32`; canonical start `16` with tail trims `8`, `16`, `24`, and `32` | No coherent plaintext |
| Cipher mode | ECB and zero-IV CBC in this pass; prior pass also covered CFB64 and OFB | No coherent plaintext |
| Integer encoding | Big-endian substitution for the magic, client number, or constant, one at a time | No coherent plaintext |
| Ticket extent | Exact 16 bytes, NUL-terminated, zero-padded to 32 bytes, and zero-padded to 64 bytes | No coherent plaintext |
| Constant | `0`, `1`, `10`, `100`, `1000`, `1024`, and `10000`, each little-endian | No coherent plaintext |

The constant alternatives are a bounded encoding/scale check: zero and one,
adjacent decimal scales around 1000, and the nearby binary boundary 1024. They
are not a key search.

The canonical 640-byte targets contain 58 distinct 8-byte blocks; each
608-byte target contains only nine. The latter repetition is consistent with
an encrypted fixed-record payload and argues against the candidate extent
being arbitrary trailing capture data. Across the two connections, canonical
decryption produced only 2 matching bytes out of 640 for the first response
and zero out of 608 for the second. No boundary or input variation produced
recurring structure across the repeated responses.

These results make a body-boundary-only error unlikely. The capture proves the
ticket and client-number inputs and reproduces the documented MD5 computation,
but supplies no plaintext oracle that can separate a wrong constant from
missing key material, a different derivation transform, or an unrecorded
cipher parameter. The failing stage is therefore the complete key/cipher
construction after capture-native input collection, not the `1000` constant
in isolation.

### Lobby routing cross-check

No decrypted record supports a packet-level comparison with the lobby routes in `xivl-opcodes`. In particular, the ciphertext does not newly prove lobby `0x0001`, `0x0010`, `0x01f5`, or `0x01f6`. The opcode catalog therefore requires no annotation from this study.

The clear lobby sub-event type is not itself an opcode. Applying the map-service wrapped-actor opcode offset to this direct lobby record would exceed what the capture proves.

### Evidence ceiling

No plaintext was recovered. The scoped follow-up is to establish one missing
construction detail from independent retail-client evidence: the exact bytes
fed to MD5 after the known client number and ticket, the Blowfish key encoding,
or the mode/IV initialization. A follow-up should then rerun the same four
fixed targets. The packet corpus alone cannot choose among those alternatives,
and brute-force key or constant search is not warranted.
