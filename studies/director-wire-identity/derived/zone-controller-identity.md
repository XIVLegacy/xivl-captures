# Zone Controller Wire Identity

The retained retail 1.23b packet captures show seven paired observations of
the numeric `0x0005` SetMap field and a later `0x00CC` object update. In every
pair, the `0x00CC` wrapper source actor ID matches

    (4 << 28) | (SetMap +0x04 << 19) | 1

where `SetMap +0x04` is kept as the observed numeric field. The frame and
subevent locators below are zero based within s2c connection 0. The source
actor is the `0x0003` wrapper header field at subevent offset `+0x04`.

| Capture | SetMap locator | SetMap +0x04 | `0x00CC` locator | Wrapper source | Application class |
|---|---|---:|---|---|---|
| `login.pcapng` | frame 2, offset 0 | 244 | frame 19, offset 384 | `0x47A00001` | `ZoneMasterPrvI0` |
| `return_to_inn.pcapng` | frame 37, offset 0 | 244 | frame 49, offset 624 | `0x47A00001` | `ZoneMasterPrvI0` |
| `teleport_to_gridania.pcapng` | frame 58, offset 0 | 206 | frame 69, offset 2608 | `0x46700001` | `ZoneMasterFstF0` |
| `teleport_to_camp_nine_ivies.pcapng` | frame 72, offset 0 | 151 | frame 83, offset 1584 | `0x44B80001` | `ZoneMasterFstF0` |
| `gridania_to_coerthas.pcapng` | frame 175, offset 0 | 150 | frame 186, offset 1584 | `0x44B00001` | `ZoneMasterFstF0` |
| `gridania_to_coerthas.pcapng` | frame 844, offset 0 | 152 | frame 856, offset 1584 | `0x44C00001` | `ZoneMasterFstF0` |
| `gridania_to_coerthas.pcapng` | frame 1319, offset 0 | 145 | frame 1330, offset 1584 | `0x44880001` | `ZoneMasterRocR0` |

The SetMap event is an actor-wrapped `0x0003` subevent whose game inner header
declares `0x14`, with a 48-byte subpacket and a 16-byte application payload.
The `0x00CC` event has the same wrapper and inner header values, a 296-byte
subpacket, and a 264-byte application payload. Its NUL-terminated ASCII class
string is at application payload offset `+0x24`. These are framing and byte
observations; they do not assign a native lookup rule or a server-side class
contract.

The five source members are pinned by
`sources/pcap-1.23b/manifest.yaml` with these SHA-256 values:

- `login.pcapng`: `28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62`
- `return_to_inn.pcapng`: `9a81e483d3dd2673081afef06ed521c190c4d42be16e95e24097f25ff81f58c1`
- `teleport_to_gridania.pcapng`: `779141dc79a4bcf4bfc2e265f8b9510607d5a6b6e78d32f8940e5a847e598fa0`
- `teleport_to_camp_nine_ivies.pcapng`: `fac2b485608247d299a406a7065e19918789118e7e544ca85cec4d772da0e3ab`
- `gridania_to_coerthas.pcapng`: `63152a1ed6e446df5cc4750fe50a0839f9e45ad270c79abfc72b5c09cc47e547`

This finding concerns observed ZoneMaster object identities. It does not
identify a director, establish camera causation, define native actor-lookup
rules, cover unobserved numeric values, or classify every high-nibble-4 actor
as a director. No retained row has SetMap numeric value 128; `0x44000001`
for 128 is a derivation from the relation above, not captured evidence.
