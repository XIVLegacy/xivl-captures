# Lobby Client-Number Corroboration

## Scope

This bounded search covered every TCP payload in all 54 immutable members of
`sources/pcap-1.23b/objects`, whose membership is fixed by
`sources/pcap-1.23b/manifest.yaml`. It searched for both decimal ASCII values
and both 32-bit byte orders:

| Label | Decimal | Little-endian | Big-endian |
|---|---:|---|---|
| Launch argument | 1356916742 | `06 e8 e0 50` | `50 e0 e8 06` |
| Patched client number | 1356916754 | `12 e8 e0 50` | `50 e0 e8 12` |

The same strings and compact hex spellings were also searched across the
canonical `derived/`, `catalog/`, `studies/`, `pipelines/`, and `schemas/`
artifacts before this record was added.

## Proven wire observations

`login.pcapng` is fixed by manifest rows 132-134 at SHA-256
`28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62`.
Its first raw lobby connection contains the patched value twice:

| Packet | Direction | TCP payload offset | Frame-relative meaning |
|---:|---|---:|---|
| 824 | server-to-client | `0x24` | Final dword of the initial 40-byte server frame |
| 833 | client-to-server | `0x84` | InitialSessionData `+0x74`, because the structure begins at outer-frame `+0x10` |

Both fields contain `12 e8 e0 50`, or 1356916754. Packet 824 was captured at
Unix time 1356916754.447529. Packet 833 follows at 1356916759.275829 and also
contains the visible `Test Ticket Data` buffer at frame offset `0x44`, matching
the retail client's InitialSessionData writer.

The repeat lobby connection proves that the field was live rather than a
retail executable constant. Packet 853 server-to-client and packet 874
client-to-server both contain `1b e8 e0 50`, or 1356916763, at the same
respective offsets. Packet 853 was captured at Unix time 1356916763.696855;
the client request follows about 4.8 seconds later. This nine-second change
between connections corroborates the retail `_time64` source and cached
client-number behavior.

The first request's 1356916754 is therefore direct wire corroboration for the
launcher patch's replacement result. It is not evidence that those bytes are
present at the unpatched PE site.

## Bounded absence

The 54-member TCP-payload census found no ASCII occurrence of 1356916742 or
1356916754, no little- or big-endian occurrence of 1356916742, and no
big-endian occurrence of 1356916754. The only hits for either target were the
two little-endian 1356916754 fields above. The canonical artifact search also
found neither target before this record was added.

Account traffic in `login.pcapng` is TLS-wrapped, so this absence cannot test
whether `SERVER_UTC=1356916742` existed inside account-service plaintext. No
retained cleartext lobby, launch, or session artifact carries that launch
argument value. This is a closed-corpus bounded absence, not proof that the
launcher-to-client argument was never transported by an account service.

## Evidence ceiling

The clear initial frames establish equal server and client dwords for two
connections and the static client establishes use as MD5/Blowfish key input.
The capture does not expose server comparison code. Exact equality, tolerated
clock skew, expiry, and rejection behavior remain `INSUFFICIENT-DATA`.
