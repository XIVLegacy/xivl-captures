# Monster population evidence map

## Confirmed

The pinned placement member `server_battlenpc_spawn_locations.sql` has SHA-256
`149aa117f031e213152ad14b382d30a62ac7857f7f1ea390286636f383245bf3`.
This is one file's identity, not an archive digest or proof of Git ancestry.
The [source manifest](../../../sources/monster-population-reported-observations/manifest.yaml)
records every retained member. Restricted provenance retains the supplied
origin, reported revision, license, and comparison identity without making
them retail evidence. No newer source checkout substitutes for these bytes.

[Accounting](accounting.json) reconciles 7,049 records in 27 numeric zones,
599 referenced profiles, 84 NM aliases, 63 candidate-group memberships,
27 link-group memberships, 12 conditions, and 16 matched condition targets.
All requested count comparisons agree. The 84 entries in [NM aliases](nm-aliases.csv)
resolve to existing records, not additional spawns. Alias literal differences
are listed rather than hidden by numeric rounding. Nineteen repeated labels
are preserved as 38 separate rows with distinct source-line keys.

These are confirmed facts about the supplied artifacts, not retail population
counts. The stale-cleanup predicates are applied only to account for the
selected source rowset. Commented tuples and example conditions are not active
records. There is no supported predicate for a previously reported 6,905-row
subset; its 144-row difference does not establish inactivity.

Three [unidentified comment records](unidentified-records.json) preserve the
source's skipped capture lines 2, 77, and 78 with original XYZ and numeric zone.
They are not counted as active placements. Named NM capture-line references
and associated behavior notes remain in the observation CSV; the referenced
underlying capture CSV is unavailable in the pinned set.

## Field verdicts

| Fields | Verdict | Limit |
|---|---|---|
| Source filename, line, digest, observation key | Confirmed artifact identity | A locator is not a retail actor ID. |
| Numeric zone | Supplied, unresolved client binding | No canonical zone name is inferred. |
| Subject label, profile ID, reported actor ID | Supplied profile join | No verified client identity or display-name join. |
| Minimum/maximum level | Supplied profile values | Not per-sighting measured levels; no patch is established. |
| XYZ and rotation | Source literal precision retained | `position_verdict` distinguishes reports, authored habitats, density expansion, and generated offsets. |
| Roaming, delay, private area, candidate/link groups | Reported configuration only | No retail behavior, home, or exclusive-spawn rule follows. |
| Conditions and targets | Reported condition plus exact supplied-key match | Weather/time rules and companion eligibility are not independently corroborated. |
| HP, MP, other profile stats | Separate supplied/model values | Not placement observations or retail measurements. |

The positional partition is 4,727 reported-unverified rows, 1,990 rows in
explicitly authored-habitat sections, 322 density-expansion rows, and 10
generated companion offsets. These categories describe source statements;
they are not confidence grades. Source section dates are compilation labels,
not footage dates or patch identities.

[Source corrections](source-corrections.json) retain the two authored position
changes separately with before/after literals and locators. The observation
CSV keeps the original values. The profile file preserves supplied values and
defaults separately; [profile changes](profile-changes.json) records applied
field updates. The external class join at profile member line 869 is not
reproduced: its NM-flag effect remains unresolved and cannot supply confidence
or retail identity.

## Contradicted

**Material:** treating the complete rowset as directly observed retail
placements conflicts with explicit authored-habitat and generated-offset
statements in the source. In particular, placement member lines 6659-6661
describe recorded ground with authored habitats, not recovered retail spawn
XYZ. Ten companion offsets are explicitly generated near a reported boss.
This rejects a blanket measurement claim; it does not prove that every
reported position is wrong.

**Material:** a tested empirical stat formula is not a recovered retail formula.
The [separate assessment](stat-model-assessment.md) records that boundary.

## Comparison with retained observations

[Comparisons](comparisons.json) checks the Navmut CSV using equal numeric zone
and XYZ rounded to 0.001, and the packet spawn CSV using exact displayed XYZ
decimals without a zone or subject join. Neither scan finds a matching row.
The exact compared file digests are in accounting. This is a bounded numeric
comparison, not a proximity search, identity proof, or disproof of a sighting.
Different time samples, rounding, movement, and coverage can differ.

The [Navmut evidence map](../../navmut-world-population-observations/derived/evidence-map.md)
already leaves home/slot/respawn semantics unresolved. The retained packet
rows in `derived/spawn_observations.csv` are actor sightings; even a numeric
match would not establish a spawn home. Zero rows here receive corroborated
retail status. No underlying video was available to inspect.

## Unverifiable and gaps

- Video URL, title, time range, observation date, and patch identity are missing.
- Original per-sighting notes and the referenced NM capture CSV are not in the pinned input set.
- Individual authorship, recording independence, and source-to-video chains remain unresolved.
- Client zone/subject identity joins and individual measured level evidence are missing.
- Respawn timing, homes, slots, behavior conditions, and confidence are not established.
- Source-provided web references are leads, not independently inspected corroboration here.
- The 67 pre-range scripted rows and nine Together We Stand rows are consumer exceptions, not new retail evidence; no exception policy or allocation is imported.
- The reported source revision is metadata only: the supplied directory has no Git metadata. File checksums, not that claim, establish the inspected bytes.

## Unique value and consumer citation

The recoverable value is a precision-preserving, individually addressable
record of what the supplied compilation reports, with its non-observational
parts exposed. Cite only the needed CSV `observation_id`, its SHA-256 from
[checksums](checksums.sha256), and this field verdict map, under the exact
`xivl-captures` commit. A local commit is not a publicly resolvable permalink.
This study does not close consumer gameplay or implementation acceptance.
