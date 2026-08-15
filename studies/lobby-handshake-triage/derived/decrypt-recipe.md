# Lobby Decrypt Recipe Test

## Source

- Evidence class: packet capture.
- Artifact: `sources/pcap-1.23b/objects/login.pcapng`.
- Identity: SHA-256 `28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62`.
- Provenance: `sources/pcap-1.23b/manifest.yaml`, source id `pcap-1.23b`, recorded against retail 1.23b live servers.

## Verdict

`REFUTED`. The tested raw-MD5 Blowfish-ECB recipe does not decrypt the held lobby ciphertext into structurally coherent data. Plausible mode and fixed-width ticket variants also fail, so the capture does not support a lobby plaintext or opcode claim from this recipe.

## Capture-native key inputs

The first lobby connection obtains `clientNumber` 1356916754 from the final little-endian dword of packet 824's 40-byte server payload and from packet 833 frame offset `0x84`. The repeat connection obtains 1356916763 at the same locations in packets 853 and 874. The changing values rule out treating the input as a fixed executable constant.

Packets 833 and 874 carry the ASCII ticket phrase `Test Ticket Data` at frame offset `0x44`. The phrase occupies the start of a zero-padded field; the tested canonical input stops before the first zero byte.

The remaining inputs are the prescribed little-endian constants `0x12345678` and `0x000003e8`. MD5 over the concatenated bytes produces raw Blowfish keys `1ca5adbcaa7e27b2a3d57f52794ed28c` for the first connection and `a9193258afa38fe0966b2200dcdfde11` for the repeat connection.

## Ciphertext and result

For the first connection, packet 836 carries the 672-byte outer frame at reconstructed server stream offset `0x28`. Its 16-byte outer header ends at `0x38`, its 16-byte clear sub-event header ends at `0x48`, and the tested encrypted region is the following 640 bytes through `0x2c7`. Raw-MD5 Blowfish-ECB decryption begins `d3 c3 9f 1e c2 18 c1 f7 73 d3 4e 35 09 6e 48 46`; the full result remains high-entropy and contains no recognizable fixed header or capture-native client number, constants, or ticket phrase.

Packet 842 supplies a second 608-byte target at stream offset `0x2e8`. The repeat connection supplies the corresponding 640-byte and 608-byte targets in packets 877 and 883. All four raw-MD5 ECB results fail the same structural checks. Decrypting from the outer body instead of after the clear sub-event header also fails.

As robustness checks, zero-IV CBC, CFB64, and OFB were tried with the raw digest. ECB and zero-IV CBC were also tried with lowercase and uppercase 32-byte MD5 hex keys and ticket inputs terminated or padded to the visible field widths. None produced a coherent record or capture-native literal. These negative variants do not define a new recipe; they show that the canonical failure is not repaired by the common encoding ambiguities visible in this capture.

## Lobby routing cross-check

No decrypted record supports a packet-level comparison with the lobby routes in `xivl-opcodes`. In particular, the ciphertext does not newly prove lobby `0x0001`, `0x0010`, `0x01f5`, or `0x01f6`. The opcode catalog therefore requires no annotation from this study.

The clear lobby sub-event type is not itself an opcode. Applying the map-service wrapped-actor opcode offset to this direct lobby record would exceed what the capture proves.

## Evidence ceiling

This result refutes the tested recipe against the held retail capture. It does not prove that the lobby bodies are unencrypted, identify a different key derivation, or refute every Blowfish construction. No plaintext was recovered.
