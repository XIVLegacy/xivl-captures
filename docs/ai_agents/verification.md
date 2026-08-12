# Verification

`.github/workflows/checks.yml` is the authoritative list of CI-covered checks,
and CI runs them on every pull request and push to `main`.

## Restricted-corpus check

CI declares `XIVL_CORPUS_ABSENT=1` and validates the public repository shape.
When the restricted capture objects are restored locally, leave that variable
unset and run:

```powershell
python tools/refresh.py --check
```

Exit 0 proves the object hashes, schemas, catalogs, generated scenario and axis
views, derived products, sidecars, and public/private boundary agree with the
restored corpus. A public checkout reports the restricted-object skip and does
not make that stronger claim.

## Local documentation and comment feedback

For optional local review of a documentation or comment change:

- confirm `docs/README.md` lists every tracked docs page and every listed link
  resolves in both directions
- confirm no tracked public document contains a live sibling checkout path
- for a Python comment-only change, compare the parsed structure or use an
  equivalent behavior-preserving check

These reviews cover contracts and techniques that the repository gate does not
validate.

## Claim limits

A green gate does not prove live server behavior, a live client session, the
truth of an uncited video observation or wiki-tier transcription, or semantic
correctness beyond the captured packet and source inputs.

Report any unverified edge, the missing artifact, and the maintainer run needed
next. Do not claim client, network, or live validation that did not run.
