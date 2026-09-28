# Lobby Handshake Decryptability Triage

## Study contents

This bounded packet-capture study inventories the canonical session and zone-transition members that could contain a lobby or pre-zone handshake. It records the TLS-versus-raw classification, raw lobby ciphertext targets, and the confirmed capture-native decrypt recipe.

## Start here

- `derived/triage.md` - inventory, verdict, and packet/frame locators.
- `derived/server-utc.md` - client-number wire fields and bounded constant census.
- `derived/decrypt-recipe.md` - capture-native key inputs, ciphertext locators,
  confirmed recipe, recovered plaintext, and historical failure record.
- `derived/record-census.md` - complete decrypted frame and subrecord census,
  cross-session correspondence, supported routes, and consumer boundaries.
- `derived/lobby-record-census.json` - schema-validated structural fixture with
  all payload values and plaintext hashes redacted.

## Source material

- `sources/pcap-1.23b/manifest.yaml:193-210` defines the session scenario (`login.pcapng`, `idling.pcapng`).
- `sources/pcap-1.23b/manifest.yaml:287-302` defines the cross-zone handoff scenario (`gridania_to_coerthas.pcapng`, `from_gridania_to_blackshroud.pcapng`).
- `sources/pcap-1.23b/manifest.yaml:303-352` defines the adjacent inn-room, map-UI, and aetheryte transition members.
- The `login.pcapng` identity is fixed by `sources/pcap-1.23b/manifest.yaml:132-134`.

## Promoted conclusions

- The stage-0 transport verdict is `GO`: `login.pcapng` contains the preserved
  raw lobby target, so the closed corpus is not limited to TLS lobby traffic.
- `login.pcapng` is mixed: TLS account traffic is present, and the same capture
  also contains raw 54994 lobby frames and raw 54992 game frames.
- Every complete port-54994 frame in both directions is reconstructed, and each
  applicable 32-byte-aligned payload extent is decoded by the confirmed
  44-byte MD5 and Blowfish ECB recipe recorded in `derived/decrypt-recipe.md`.
- The retained streams contain 16 complete outer frames and 20 complete
  subrecords. Type-`0x0003` inner routes directly support session, account,
  character, world, import, retainer, and select-character dispatch boundaries.
- Both retained server acknowledgements are 672-byte records with 32 clear
  header bytes and a 640-byte encrypted payload. Their exact comparison spans
  and repeated-value offsets are retained without payload values.
- The other inventoried members expose raw 54992 game framing and no TLS handshake; they do not add a separate lobby ciphertext target.
- The first raw lobby connection carries client number 1356916754 in both the
  initial server frame and InitialSessionData; the repeat connection carries
  1356916763 at the same offsets.
- Both client requests carry the ticket phrase `Test Ticket Data` in plaintext.
- The recipe recovers `FINAL FANTASY XIV`, version `2012.09.19.0001`, session
  tokens, character names, and a world-server handoff string from both lobby
  connections. The client implementation is cataloged by `BCS-Y-0008` and
  `BCS-Y-0013`, including the `MOVSX` key-schedule behavior.

## Topics

- login and lobby handshake
- TLS account transport
- raw 1.23b game framing
- bounded Blowfish decryptability
- lobby client number and SERVER_UTC
- map-server and zone transitions

## Evidence gaps

- The canonical game decoder includes the raw 54992 lanes from `login.pcapng`.
  Its raw 54994 lobby lanes remain outside that decoder even though their
  decrypt recipe is confirmed. TLS account traffic also remains outside.
- Server-side client-number comparison and rejection policy remain unverified.
- Clear types `0x0007` and `0x0008` have no promoted consumer case beyond the
  envelope parser and dispatcher. The acknowledgement payload's opaque repeated
  values have no supported interpretation beyond offsets and variance.
- Packet numbers are 1-based capture positions; stream offsets and frame boundaries come from the repository lane/frame reconstruction.

## Further research

- Server-side acceptance, rejection, and client-number skew policy require
  evidence beyond capture-native decryption.
