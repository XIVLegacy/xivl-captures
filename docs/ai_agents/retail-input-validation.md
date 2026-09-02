# Retail input validation

The optional `pcap-1.23b-products-v1` workflow checks the deterministic capture
products against the exact restricted `pcap-corpus-1.23b` archive. The normal
asset-free checks remain sufficient for pull requests and public branch health;
this workflow is a separate, manually dispatched evidence check.

The public contract is in `config/retail_inputs.json` and
`config/retail_pcap_check.json`. It pins the archive SHA-256, size, private
repository commit, and path. The public source manifest retains all 54 member
names, sizes, and hashes. Local `sources/pcap-1.23b/objects/` and
`archives/` copies are caches, not alternate authorities.

The workflow is `.github/workflows/retail-checks.yml`, and its protected job is
named `PCAP Corpus Checks`. It runs only from the reviewed protected `main`
revision, uses the `retail-evidence` environment, and retains only the
schema-valid `retail-pcap-attestation` artifact containing
`retail-evidence-attestation.json`.

The workflow invokes the shared `fetch-retail-input` action from
`XIVLegacy/xivl-tools` at an immutable commit.
It receives the approved commit, PCAP path, size, SHA-256, output path, and
parent trees from this check. It allows only the authorized archive path and
requires an untruncated tree response, regular-file type and mode, the pinned
size and blob identity, and the archive SHA-256 before extraction. Other assets
in the shared private repository are outside this check's grant.

The extractor validates the complete archive before writing any member. It
rejects duplicate names, directories, links, encrypted entries, traversal or
absolute paths, non-PCAP files, compression ratios outside the fixed bound,
member drift, and uncompressed-size drift. Private bytes stay under one
temporary root. The shared `finalize-retail-attestation` action removes that
root before artifact validation and upload.

The hosted claim is exact deterministic agreement between the 54-member PCAP
archive and the already tracked products, catalogs, schemas, sidecars, and
digestion checks. It does not establish capture chronology across connection
blocks, uncaptured behavior, semantic names beyond existing evidence, TLS
plaintext, or live-server behavior outside the recorded sessions. Logs and
attestations contain only fixed stage names, counts, timings, and verdicts;
they do not contain packet fields, payloads, addresses, names, chat, or hex.

The workflow also runs the seven explicit repository unit-test modules before
retail extraction.

## Reproduced result

[Retail Checks run 32528392471](https://github.com/XIVLegacy/xivl-captures/actions/runs/32528392471)
reproduced the tracked
[`pcap-1.23b-products.json`](../../config/retail_evidence/pcap-1.23b-products.json)
attestation byte-for-byte.
The retained file is 306 bytes with SHA-256
`cca5f8f2a66220c06353dd337ed6b368420fa980aed2546751330de67884f001`.
Artifact allowlist, schema, cleanup, negative-control, and public-log leakage
reviews passed, and the ignored review root was removed completely.
