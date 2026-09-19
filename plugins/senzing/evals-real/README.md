# Real-Senzing evals

The sibling suite (`../evals/`) proves the plugin **routes and grounds** correctly. It cannot
prove the plugin **resolves** anything: it runs on a macOS runner with no Senzing installed, and
its `analyze` case says so in its own `expected_outcome` — "The sandbox has no Senzing, so the run
ends by saying so." That case covers steps 1–3 of `analyze`'s seven. Across the whole suite, no
grader has ever asserted an entity count, a match score, a why/how result or a rendered report.

This suite closes that hole. One case goes the full distance — map, load, drain the redo queue,
resolve — against a **real Senzing SDK**, and the answer is checked against **published ground
truth**.

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
| `resolve-truthset` | "Work out who is who across customers.csv, reference.csv and watchlist.csv — load them into a scratch Senzing repository and tell me how many distinct entities they resolve to. Keep the repository on disk." | `analyze` fires, `doctor` first; **one** `mapping_workflow(action=start)` over all three files; the mapper runs via Bash; a fresh on-disk SQLite scratch repository is created and loaded with no confirmation gate; `sdk_guide(topic=redo)` is retrieved and the queue is drained to zero; the reply reports 159 records resolving to 85 entities |

The user's "keep it on disk, I want to open it again" is not decoration: it is what makes the run
verifiable. An `internal://` in-memory repository would leave nothing behind to check.

## The ground truth, and where the number comes from

`ground-truth/actual_truthset_key.csv`, vendored at a pinned commit from
[Senzing/truth-sets](https://github.com/Senzing/truth-sets), whose README calls it "the expected
correct ER results (ground truth)". 159 records → **85 entities**, and the full partition of which
records belong together.

Both numbers are **derived at run time** from that key, never written as a literal in an
assertion. `ground-truth/PROVENANCE.md` carries the pin, the derivation, the evidence that 85 is
Senzing's own answer and not merely an aspiration, and the limits of that claim. Read it before
touching the expectation.

## The gate is not a grader

`claude plugin eval` has `llm`, `regex`, `tool_used`, `tool_order`, `file_exists` and `baseline`
graders — and **no shell/command grader**. So every grader verdict is ultimately a statement about
text the agent produced, and text is exactly what a fabricating run is good at.

The authoritative check therefore runs *outside* the eval, as a job step:
`verify_truthset.py --search-root` finds the SQLite repository the run left behind, opens it with
the real V4 SDK, and asks the engine:

1. every ground-truth record is present and resolvable (`get_entity_by_record_id`);
2. no entity in the repository lacks a ground-truth record (`export_json_entity_report`) — nothing
   else was loaded;
3. the entity count equals the count derived from the key;
4. the **partition** matches cluster for cluster — 85 entities that are the wrong 85 fails, and
   the verdict names the clusters that were not reproduced;
5. `count_redo_records()` is zero — an entity count taken with redo outstanding is a
   mid-resolution snapshot.

No repository found is a FAIL, not a skip: a run that reports entity counts and leaves no
repository behind did not resolve anything.

`verify_truthset.py --self-test` runs first, free and offline, on every trigger including fork
PRs. It re-derives the expectation, asserts the key and the fixtures still describe the same
records, and asserts the two literals in the graders still match the derived numbers — so fixture
drift fails for $0 rather than halfway through a paid run.

## Graders that were deliberately NOT written

Three obvious-looking graders are absent because the Senzing MCP's own tool output contains the
strings they would match, so they would be scored against the corpus rather than the run:

| Not written | Why |
|---|---|
| `not_contains: internal://` on the trace | `sdk_guide`'s `engine_config_notes` recommend `internal://` verbatim. It would fail every correct run. |
| `contains: sqlite3://` on the trace | Same notes contain it. It would pass without the agent doing anything. |
| `contains: count_redo_records` on the trace | `sdk_guide(topic='redo')` returns a snippet containing it. Passes on retrieval alone. |

The redo obligation is graded as the *tool call* (`sdk_guide(topic=redo)`), and the actual drain is
asserted by the engine in `verify_truthset.py`. This is the same rule the sibling suite's README
states: a grader that fires on quoted corpus text is a false-fail in waiting, and one that passes
without the work is worse than none.

## Run it

```bash
# needs a Linux host with senzingsdk-runtime installed (see
# .github/senzing-eval/Dockerfile), ANTHROPIC_API_KEY, and a sandbox backend
# (bubblewrap + socat)
plugins/senzing/evals-real/run.sh --keep-temp
python3 plugins/senzing/evals-real/verify_truthset.py --search-root "${TMPDIR:-/tmp}"
```

`EVAL_RUNS` defaults to 1 here (each run is a full map+load+resolve, and the gate inspects the one
repository it produces). `EVAL_MAX_COST_USD` is left at 75 — a **runaway guard, not a budget**. A
ceiling low enough to bind does not save money, it truncates a legitimate run into a `partial` and
reports a false failure.

## Licensing

159 records sits inside Senzing's **500 Distinct Source Record** no-license ceiling
(`sdk_guide(topic='install')`). This suite needs no license file, no license string and no
credentials of any kind. The SDK install accepts the Senzing EULA explicitly, in the open, in the
workflow that builds the image.
