# Lobby Handshake Decryptability Triage

## Study contents

This bounded packet-capture study inventories the canonical session and zone-transition members that could contain a lobby or pre-zone handshake. It records the TLS-versus-raw classification, raw lobby ciphertext targets, and a refuted capture-native decrypt recipe.

## Start here

- `derived/triage.md` - inventory, verdict, and packet/frame locators.
- `derived/server-utc.md` - client-number wire fields and bounded constant census.
- `derived/decrypt-recipe.md` - capture-native key inputs, ciphertext locators, and recipe verdict.

## Source material

- `sources/pcap-1.23b/manifest.yaml:193-210` defines the session scenario (`login.pcapng`, `idling.pcapng`).
- `sources/pcap-1.23b/manifest.yaml:287-302` defines the cross-zone handoff scenario (`gridania_to_coerthas.pcapng`, `from_gridania_to_blackshroud.pcapng`).
- `sources/pcap-1.23b/manifest.yaml:303-352` defines the adjacent inn-room, map-UI, and aetheryte transition members.
- The `login.pcapng` identity is fixed by `sources/pcap-1.23b/manifest.yaml:132-134`.

## Promoted conclusions

- The stage-0 transport verdict is `GO`: `login.pcapng` contains the preserved
  raw lobby target, so the closed corpus is not limited to TLS lobby traffic.
- `login.pcapng` is mixed: TLS account traffic is present, and the same capture also contains raw 54994 lobby frames.
- The 54994 server-to-client frames provide a raw Blowfish target candidate; no decryption or key claim is made.
- The other inventoried members expose raw 54992 game framing and no TLS handshake; they do not add a separate lobby ciphertext target.
- The first raw lobby connection carries client number 1356916754 in both the
  initial server frame and InitialSessionData; the repeat connection carries
  1356916763 at the same offsets.
- Both client requests carry the ticket phrase `Test Ticket Data` in plaintext.
- Raw-MD5 Blowfish-ECB with the capture-native inputs does not produce coherent
  lobby plaintext; common mode, digest-encoding, and ticket-width variants also
  fail.

## Topics

- login and lobby handshake
- TLS account transport
- raw 1.23b game framing
- bounded Blowfish decryptability
- lobby client number and SERVER_UTC
- map-server and zone transitions

## Evidence gaps

- The cipher, key, mode, and plaintext for the raw 54994 body remain unverified;
  the tested recipe is refuted.
- Server-side client-number comparison and rejection policy remain unverified.
- Packet numbers are 1-based capture positions; stream offsets and frame boundaries come from the repository lane/frame reconstruction.
- The canonical decoder excludes `login.pcapng`; this triage preserves its mixed transport evidence without changing generated products.

## Further research

- A consumer may test a materially different, independently sourced decrypt using the raw locators in `derived/triage.md`; retain the failed parameters in `derived/decrypt-recipe.md`.
