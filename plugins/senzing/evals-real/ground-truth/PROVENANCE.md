# Ground truth — where the number comes from

`actual_truthset_key.csv` and the three fixture CSVs under
`../resolve-truthset/fixtures/` are vendored **verbatim** from the Senzing truth-set
repository, pinned to one commit:

| | |
|---|---|
| Repository | <https://github.com/Senzing/truth-sets> |
| Path | `truthsets/demo/` |
| Commit | `92f1cc705eed15a36dc271ed150eccab7f6f27fe` (2026-03-23) |
| Files | `customers.csv`, `reference.csv`, `watchlist.csv`, `actual_truthset_key.csv` |

They are vendored rather than downloaded so the expectation cannot move under a
run: a fetch at run time would let an upstream edit silently change what "correct"
means mid-PR. Refresh by re-pinning the commit and re-running the self-test.

## What the key is

That repository's README labels the two key files:

- **`actual_truthset_key.csv` — "The expected correct ER results (ground truth)."**
- `alternate_truthset_key.csv` — "Simulated results from a legacy or competing
  algorithm, used to demonstrate ER auditing."

Each row is `TEST_GROUP,CLUSTER_ID,DATA_SOURCE,RECORD_ID`. Records sharing a
`CLUSTER_ID` are the same real-world entity. The README is explicit that
`CLUSTER_ID` values are *groupings*, not identifiers to compare against Senzing's
`ENTITY_ID`: "The `CLUSTER_ID` values do not need to match Senzing's entity IDs —
the audit process compares groupings, not IDs." `verify_truthset.py` therefore
compares partitions, never id values.

## The derived expectation

Computed by `verify_truthset.py` from the files above — **never written as a
literal in an assertion**:

| Quantity | Value | How it is derived |
|---|---|---|
| Records | **159** | rows in the three fixture CSVs (CUSTOMERS 120, REFERENCE 22, WATCHLIST 17) |
| Entities | **85** | distinct `CLUSTER_ID` values in `actual_truthset_key.csv` |

Every fixture record is keyed and every keyed record is in a fixture (the
`--self-test` mode asserts exactly that), so there are no unkeyed singletons to
add. Cluster sizes: 31×1, 43×2, 6×3, 2×4, 2×5, 1×6.

## Why 85 is Senzing's own answer, not just an aspiration

A ground-truth key states what *should* happen; an eval needs to know what the
engine *does*. The same README answers that, by describing how the alternate key
was built:

> The alternate key included here was derived from **Senzing's own results** and
> then modified to simulate a legacy or competing algorithm.

It then names both modifications:

1. **More aggressive name matching** — the alternate merges close name variants
   sharing a DOB that "Senzing considers only possible matches" (it names
   "Darla Anderson" / "Darlene Anderson").
2. **No employer-based matching** — the alternate splits records "where Senzing
   merges records based on name + employer" (it names "Howard Hughes" at
   "Universal Exports" across REFERENCE and WATCHLIST).

Comparing the two keys row by row, they differ on exactly six record pairs, and
every one of them falls under those two headings:

| Direction | Records |
|---|---|
| alternate over-merges (name) | CUSTOMERS 1025 / CUSTOMERS 1026 / WATCHLIST 1027 (Darla / Darlene / Darletta Anderson) |
| alternate over-merges (name) | CUSTOMERS 1089 / CUSTOMERS 1090 (Morris I / Morris II Klein) |
| alternate splits (employer) | REFERENCE 2081 / WATCHLIST 2082 (Howard Hughes) |
| alternate splits (employer) | REFERENCE 2091 / WATCHLIST 2092 (Margaret Charney) |

Undoing exactly those documented modifications on the alternate key's 84 clusters
gives 84 + 3 (splitting the two over-merges back apart) − 2 (re-merging the two
splits) = **85**, and the resulting partition is `actual_truthset_key.csv`
record for record. So Senzing's published result on this dataset *is* the actual
key.

## Limits — state these honestly

- The equality "Senzing's result == `actual_truthset_key.csv`" is derived from
  Senzing's own documentation of how the alternate key was produced. It has not
  been confirmed here by running the engine; only a real run of this job can do
  that, and that is the point of the job.
- Engine version, config, or tuning changes could legitimately move the number.
  When this gate fails, the answer is to find out **which** clusters changed
  (the verdict JSON names them) and decide regression-or-intended. **Do not
  re-freeze the expectation to whatever the run produced** — that converts a
  bug into the specification, which is precisely the failure mode this file
  exists to prevent.
- The partition check is strictly stronger than the count. 85 entities that are
  the *wrong* 85 fails, and the verdict lists the clusters that were not
  reproduced.

## Licensing

159 records is well inside the **500 Distinct Source Record** limit Senzing
applies with no license at all (`sdk_guide(topic='install')`: "Without a license,
Senzing limits ingestion to 500 records (error SENZ9000 at record 501)... Do NOT
ask about licensing if the user has 500 or fewer records"). This job therefore
needs **no license file, no license string, and no credentials of any kind.**
