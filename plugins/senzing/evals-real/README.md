# Real-Senzing evals

The sibling suite (`../evals/`) proves the plugin **routes and grounds** correctly. It cannot
prove the plugin **resolves** anything: it runs on a macOS runner with no Senzing installed, and
its `analyze` case says so in its own `expected_outcome` — "The sandbox has no Senzing, so the run
ends by saying so." That case covers steps 1–3 of `analyze`'s seven. Across the whole suite, no
grader has ever asserted an entity count, a match score, a why/how result or a rendered report.

This suite closes that hole. One case goes the full distance — map, load, drain the redo queue,
resolve — against a **real Senzing SDK**, and then the repository it built is opened with that SDK
and spot-checked: the records went in, ER ran, the mapped features are really in the engine and are
queryable, and the counts the run reported are the counts the engine holds.

It is a **smoke test, not a validation suite**. It does not grade Senzing's answer.

## Why it is a separate directory

`claude plugin eval --eval-dir` takes a directory name below the plugin, which is all it costs to
keep the two suites apart. They must be apart because:

- The macOS behavioral-eval job is built around a host with **no Senzing**, deliberately (see the
  `runs-on` comment on `behavioral-eval` in `.github/workflows/ci.yml` — three stacked bubblewrap
  faults on ubuntu-24.04). Several of its cases assert that absence. A case needing a working SDK
  would fail there environmentally.
- `../evals/run.sh` asserts *cases discovered == case directories on disk*. Adding a directory it
  must not run would break that gate.

Nothing here modifies that suite or that job.

## The case

| Case | Utterance | What must actually happen |
|---|---|---|
| `resolve-truthset` | "Work out who is who across customers.csv, reference.csv and watchlist.csv — load them into a scratch Senzing repository and tell me how many distinct entities they resolve to. Keep the repository on disk." | `analyze` fires, `doctor` first; **one** `mapping_workflow(action=start)` over all three files; the mapper runs via Bash; a fresh on-disk SQLite scratch repository is created and loaded with no confirmation gate; `sdk_guide(topic=redo)` is retrieved and the queue is drained to zero; the reply reports the record and entity counts **the engine gave it** |

The user's "keep it on disk, I want to open it again" is not decoration: it is what makes the run
verifiable. An `internal://` in-memory repository would leave nothing behind to check.

## What this job gates on — and what it only reports

**It is a smoke test, not a validation suite.** It answers one question: *does the thing basically
work, end to end?* Few checks, coarse, durable. Every gating check has to survive an engine
upgrade, a config change and a differently-worded mapper, or it will flake and get ignored — which
is worse than not having it.

`verify_truthset.py` runs as a job step, opens the repository the agent built with the real V4
SDK, and **gates on five things, each of which is the plugin's own contract**:

| # | Check | What it asserts | Why it is durable |
|---|---|---|---|
| 1 | `data_went_in` | every submitted record is in the repository, nothing else is, and `count_redo_records()` is 0 | record counts are ours; a rejected record is a missing one, so this subsumes "0 load errors" |
| 2 | `er_ran` | entities **<** records | no target number and no tolerance — it only says the engine merged *something* instead of returning N singletons |
| 3 | `features_present` | two or three known rows, read back with `SZ_ENTITY_INCLUDE_ALL_FEATURES`, carry the feature types **their own columns supplied** | the expectation is derived per row from the source CSVs, never a frozen list. This is the one that matters most: a file-level check proves only that we *wrote* an attribute — if the mapper emits a name the engine does not recognize, the file looks perfect, the load reports success, and the feature is simply not there |
| 4 | `searchable` | `search_by_attributes` on one of those rows' own values returns that record | proves the features are queryable, not merely stored — and it is the only coverage `search`/`report` have over a *loaded* repository |
| 5 | `reported_matches_engine` | the counts the run told the user are among the counts the engine holds | pure anti-fabrication, and needs no ground-truth key at all |

Two or three known records is a spot check. Every record is a validation suite. It is kept at spot.

**The published truth-set key is REPORTED, never gating.** The exact entity count and the full
cluster partition are still computed and still printed in full, under a heading that says so,
because a cluster diff is a valuable early warning of a mapping regression. It must never block a
merge:

- Whether Senzing merges A with B is the **ENGINE's** contract, not the plugin's.
  `ground-truth/PROVENANCE.md` already concedes that an engine version, config or tuning change
  can legitimately move the number.
- Gating on it flaked exactly that way: green on `825ea4f` and `b431c10`, **red on `6cb6177`**
  (86 ≠ 85, 18 clusters not reproduced) with no mapping-related change in between.
- The mapping defect it was indirectly detecting — one feature split across objects — is caught
  directly and cheaply by check 3.

This is the same standing the llm judge already has in `../evals/gate.py`: *reported, not gating*.
Also out of scope for the same reason: per-feature-type row-count tolerances, and anything that
pins mapper style.

### No literals, on either side

No grader and no case file may contain a count the engine produces. A literal is wrong twice over:
it freezes the engine's behavior into the plugin's contract, and the eval sandbox grants `Bash`
and `Grep`, so a number sitting in a grader in this repository is readable by the agent being
graded — not an independent oracle. `records-loaded-reported` and `entity-count-reported` therefore
assert only that *a* count was reported; the equality is check 5, computed at run time on both
sides. `--self-test` fails if a literal comes back.

### Finding the right repository

The verifier locates the `.sz-eval-root` marker `scaffold.sh` drops in the run workspace and then
looks for the SQLite repository **beside it**. It used to take "the Senzing repo with the most
`DSRC_RECORD` rows anywhere under `/tmp`", which on a run that loaded nothing selected the Senzing
*preflight's* own three-record database and printed "159 of 159 records are not in the repository".
That was read as a plugin defect twice, the second time with the full log open. A missing marker,
or no repository beside it, now exits **78 — ENVIRONMENTAL, explicitly not a plugin verdict**,
matching every other environmental distinction in the workflow.

## The gate is not a grader

`claude plugin eval` has `llm`, `regex`, `tool_used`, `tool_order`, `file_exists` and `baseline`
graders — and **no shell/command grader**. So every grader verdict is ultimately a statement about
text the agent produced, and text is exactly what a fabricating run is good at. The authoritative
checks therefore run *outside* the eval, as a job step, against the engine.

No repository found is not a pass: the job goes red either way, and the message says whether it is
a plugin verdict or an environmental one.

`verify_truthset.py --self-test` runs first, free and offline, on every trigger including fork
PRs. It re-derives the expectation from the vendored key and fixtures, asserts no literal has crept
back into a grader, and then **runs all five gating checks against a stubbed repository and proves
each one can FAIL**. A check that cannot fail is worse than no check, and nothing else in this job
would notice one.

## Graders that were deliberately NOT written

Three obvious-looking graders are absent because the Senzing MCP's own tool output contains the
strings they would match, so they would be scored against the corpus rather than the run:

| Not written | Why |
|---|---|
| `not_contains: internal://` on the trace | `sdk_guide`'s `engine_config_notes` recommend `internal://` verbatim. It would fail every correct run. |
| `contains: sqlite3://` on the trace | Same notes contain it. It would pass without the agent doing anything. |
| `contains: count_redo_records` on the trace | `sdk_guide(topic='redo')` returns a snippet containing it. Passes on retrieval alone. |

The redo obligation is graded as the *tool call* (`sdk_guide(topic=redo)`), and the actual drain is
asserted by the engine in `verify_truthset.py` (check 1). This is the same rule the sibling suite's README
states: a grader that fires on quoted corpus text is a false-fail in waiting, and one that passes
without the work is worse than none.

## Run it

```bash
# free and offline — fixture drift, literal creep, and proof that every gating
# check can fail. No Senzing, no API key.
python3 plugins/senzing/evals-real/verify_truthset.py --self-test

# needs a Linux host with senzingsdk-runtime installed (see
# .github/senzing-eval/Dockerfile), ANTHROPIC_API_KEY, and a sandbox backend
# (bubblewrap + socat)
plugins/senzing/evals-real/run.sh --keep-temp
python3 plugins/senzing/evals-real/verify_truthset.py \
  --search-root "${TMPDIR:-/tmp}" \
  --reported-from plugins/senzing/evals-real/results/traces
```

`--reported-from` is what makes check 5 possible: it reads the run's own final message out of the
collected CLI traces, so the "reported" side of the comparison is the run's, and the "engine" side
is the engine's, and neither is a number written down in this repository.

`EVAL_RUNS` defaults to 1 here (each run is a full map+load+resolve, and the gate inspects the one
repository it produces). `EVAL_MAX_COST_USD` is left at 75 — a **runaway guard, not a budget**. A
ceiling low enough to bind does not save money, it truncates a legitimate run into a `partial` and
reports a false failure.

## Licensing

159 records sits inside Senzing's **500 Distinct Source Record** no-license ceiling
(`sdk_guide(topic='install')`). This suite needs no license file, no license string and no
credentials of any kind. The SDK install accepts the Senzing EULA explicitly, in the open, in the
workflow that builds the image.
