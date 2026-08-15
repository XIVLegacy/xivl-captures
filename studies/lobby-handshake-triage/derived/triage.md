# Lobby Handshake Triage Record

## Verdict

`login.pcapng` contains a raw lobby target candidate. Its account service is TLS-wrapped, but two later TCP connections to `202.67.50.8:54994` carry the 1.23b outer frame and sub-event headers in the clear, followed by body bytes that are not decoded here. The candidate ciphertext regions are recorded below; no Blowfish decryption, key recovery, or plaintext assertion was attempted.

## Canonical inventory

The manifest exposes these relevant capture groups:

- Session/login: `login.pcapng`, `idling.pcapng` (`sources/pcap-1.23b/manifest.yaml:193-210`).
- Cross-zone handoff: `gridania_to_coerthas.pcapng`, `from_gridania_to_blackshroud.pcapng` (`sources/pcap-1.23b/manifest.yaml:287-302`).
- Adjacent inn-room, map-UI, and aetheryte transitions (`sources/pcap-1.23b/manifest.yaml:303-352`).

No separate `pre-zone` member is named in the canonical manifest. The transition members above use raw 54992 game framing; their first server/client payloads are frame markers such as `01 01 00 00` or `01 00 00 00` (for example `idling.pcapng` packet 1, `gridania_to_coerthas.pcapng` packet 1, and `from_gridania_to_blackshroud.pcapng` packet 1), not TLS records.

## Transport classification and raw target

| Capture/flow | Classification | Locator |
|---|---|---|
| `login.pcapng`, `192.168.1.101:36154 -> 124.150.158.110:443` | TLS-wrapped account transport | packet 33 c2s payload begins `16 03 01`; packet 35 s2c begins `16 03 01`. A second TLS connection repeats at packets 574/645. |
| `login.pcapng`, `192.168.1.101:36160 -> 202.67.50.8:54994` | Raw lobby request framing | packet 833 c2s; reconstructed c2s stream frame offset `0x0000`, size 648, marker `01 00 03 00`; body includes the visible `Test Ticket Data` field. |
| `login.pcapng`, `202.67.50.8:54994 -> 192.168.1.101:36160` | Raw lobby response; Blowfish target candidate | packet 836 carries reconstructed s2c frame offset `0x0028`, size 672, marker `00 00 00 00`; after the 16-byte sub-event header, target body length is 640 bytes. Packet 842 carries frame offset `0x02c8`, size 640; target body length is 608 bytes. |
| `login.pcapng`, `192.168.1.101:36162 -> 202.67.50.8:54994` | Raw lobby request framing (repeat connection) | packet 874 c2s; reconstructed c2s stream frame offset `0x0000`, size 648, marker `01 00 03 00`. |
| `login.pcapng`, `202.67.50.8:54994 -> 192.168.1.101:36162` | Raw lobby response; Blowfish target candidate (repeat connection) | packet 877 carries frame offset `0x0028`, size 672; packet 883 carries frame offset `0x02c8`, size 640; target body lengths are 640 and 608 bytes after their 16-byte sub-event headers. |
| `login.pcapng`, `202.67.51.120:54992` | Raw map/pre-zone game framing, not a lobby target | secondary lane begins packet 913 c2s / 915 s2c; main lane begins packet 923 c2s / 925 s2c. These are parseable 1.23b frames, not TLS records. |

The remaining transition members are also raw 54992 game framing between `192.168.1.101` and `202.67.51.120`, with no TLS record or separate lobby lane: `idling.pcapng` packet 1; `gridania_to_coerthas.pcapng` packet 1; `from_gridania_to_blackshroud.pcapng` packet 1; `move_out_of_room.pcapng` packet 1; `checkbed.pcapng` packet 2; `check_room_map.pcapng` packet 2; `gridania_map.pcapng` packet 1; `coerthas_map.pcapng` packet 1; `teleport_to_camp_nine_ivies.pcapng` packet 1; `teleport_to_camp_tranquil.pcapng` packet 2; `teleport_to_gridania.pcapng` packet 1; and `return_to_inn.pcapng` packet 3. Their first game payloads begin with the repository's raw frame markers (`01 00 00 00` or `01 01 00 00`), so none is a TLS-wrapped or additional raw lobby target.

The stream/frame offsets above are from `tools/extractors/extract_streams.py` lane reconstruction. Packet locators are 1-based positions in the immutable pcap object. The `login.pcapng` object identity is `sources/pcap-1.23b/manifest.yaml:132-134` (sha256 `28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62`, 856236 bytes).

## Boundary

This record establishes only that a raw 54994 lobby body is available for a future decrypt attempt. It does not identify Blowfish parameters or derive a key. The observed raw lane contradicts the existing pure-TLS caveat in `sources/pcap-1.23b/manifest.yaml:204-208`; generated catalog and scenario files remain outside this triage scope.
