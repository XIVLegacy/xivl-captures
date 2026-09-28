# Monster Population Reported Observations

This indexed study preserves 7,049 supplied placement records and their
field-level limits. They are historical reported data, not 7,049 verified
retail sightings. Some positions are explicitly authored habitats or generated
companion offsets. No spawn home, slot, respawn rule, or confidence is inferred.

- [Evidence map](derived/evidence-map.md): verdicts, provenance boundary, and gaps.
- [Observation CSV](derived/observations.csv): original decimal spelling and stable row keys.
- [Accounting](derived/accounting.json): counts, duplicate labels, and comparison input hashes.
- [Stat model assessment](derived/stat-model-assessment.md): separate non-measurement record.
- [Source manifest](../../sources/monster-population-reported-observations/manifest.yaml): original filenames, sizes, hashes, rights, and retention.

The source objects are restricted and keep their original bytes and filenames.
Their rights are not replaced by the repository's license. Attribution to
AuroraFlare identifies the supplied compilation; individual observation
authorship and the underlying recordings remain unresolved.

## Reproduction

With the manifest-pinned objects restored, run
`python tools/import_monster_population.py`, then
`python tools/import_monster_population.py --check`.
The importer reads named tables into an isolated in-memory database; it does
not execute source programs or connect to a database service. Column positions
come from explicit INSERT columns checked against the matching CREATE TABLE.
Numeric literals remain strings, including trailing zeros. Original position
values remain in the CSV; separately recorded corrections never overwrite them.

`placement-NNNNNN` uses the one-based source tuple line within the immutable
placement member. It is stable for this pinned source, not a portable entity
identifier. Nineteen supplied `uniqueId` labels each occur twice, so consumers
must use `observation_id`. Profile IDs and condition targets remain supplied
identifiers, not client joins. Blank values mean absent/NULL, not numeric zero;
`defaulted_fields` identifies SQL defaults separately from supplied tuple fields.

Public validation checks row references, evidence classes, and anchored product
digests. Only the restricted-input check reproduces source extraction. Run the
applicable `python tools/refresh.py --check` gate, or append `--public-shape`
when restricted packet objects are unavailable.
