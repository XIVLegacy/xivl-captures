# Retail input validation

The optional `pcap-1.23b-products-v1` lane checks the deterministic capture
products against the exact restricted `pcap-corpus-1.23b` archive. The normal
asset-free gate remains sufficient for pull requests and public branch health;
this lane is a separate, manually dispatched evidence check.

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

The extractor validates the complete archive before writing any member. It
rejects duplicate names, directories, links, encrypted entries, traversal or
absolute paths, non-PCAP files, compression ratios outside the fixed bound,
member drift, and uncompressed-size drift. Private bytes stay under one
temporary root and are removed before artifact validation and upload.

The hosted claim is exact deterministic agreement between the 54-member PCAP
archive and the already tracked products, catalogs, schemas, sidecars, and
digestion checks. It does not establish capture chronology across connection
blocks, uncaptured behavior, semantic names beyond existing evidence, TLS
plaintext, or live-server behavior outside the recorded sessions. Logs and
attestations contain only fixed stage names, counts, timings, and verdicts;
they do not contain packet fields, payloads, addresses, names, chat, or hex.
