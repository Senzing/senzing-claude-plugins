---
name: analyze
description: >
  Answer "who is who" in the user's own data files, end to end: map to the Entity Spec, load into a
  throwaway scratch repository, resolve, then deliver a shareable report. Use when the user points
  at CSV/JSON/Parquet files and wants deduplication, record linkage, a resolved dataset, or entity
  resolution — e.g. "resolve my customer list", "dedupe these files", "find duplicates", "match
  these two lists", "load this into Senzing and show me the entities". Also the entry point for
  mapping alone, when the user wants only Senzing-ready JSON or has no Senzing installed. Runs real
  SDK code locally via Bash; records never leave the machine and results are never simulated.
  **A small file is a reason to RUN this skill, never a reason to do the matching yourself.**
  Producing the answer by inspection, a script, or any means other than Senzing is a failure of
  this skill even when the answer is right and even when you say so: the user installed this to
  get entity resolution, not your opinion about their rows. Six records still resolve. Runs
  doctor first to confirm this host can deliver the result. Not for data already loaded in Senzing
  (use report), sample data (use demo), or a named cookbook use case (use recipes).
argument-hint: "[path/to/data ...]"
allowed-tools: Bash, Read, Write, Agent, Skill, mcp__plugin_senzing_senzing__*
---

# Analyze data with Senzing (map → load → resolve → report)

You are grounded by the **Senzing MCP server** (the bundled `senzing` MCP). Ground rules:

- **Never answer Senzing questions from training data.** All Senzing facts, attributes, SDK
  signatures, and code come from the Senzing MCP tools (`get_capabilities`, `search_docs`,
  `mapping_workflow`, `sdk_guide`, `generate_scaffold`, `reporting_guide`, …). If unsure, call
  the tool — do not guess.
- **Never simulate entity resolution.** Do not fabricate scores, matches, or merges. No Senzing on
  this host does **not** change what happens next: the run still maps (step 3) and stops at the
  *mapping-only exit*, which is the one and only place the **`install`** skill is offered (it
  surfaces the license agreement and verifies with `doctor`; never route around it via
  `sdk_guide(topic="install")`). **Installing is never a question asked before `start` has been
  called, and "install now, or mapping only?" is never a choice put to the user** — mapping is not
  optional, and installing is a follow-on they can take once the JSONL exists. Whether an install
  would succeed here is not a question this run has to answer.
- **PII stays local.** The customer's records are only ever touched by SDK code you run locally
  via Bash. Never paste real records into a hosted tool call.

**If `./senzing-poc-plan.md` exists, read it before asking the user anything.** It is the handoff
artifact `/senzing:poc-planner` writes, and its header declares a consumer contract. Parse by the
`## N.` headings and take `platform_id`, `languages` and `database` from the `## 2.` yaml block
rather than re-asking or choosing for them. **Any value you need whose text begins
`TBD — decided by` is an undecided row: stop, name the row and its owner, and send the user back
to `/senzing:poc-planner` — never fill it in yourself.** If the user wrote the plan somewhere
else, they must tell you the path.

- **Narrate progress, unprompted — as a visual, not a wall of words.** These runs are long; don't go
  silent, but don't dump prose either. At each milestone post a **compact visual** with **real
  numbers** — a one-line stat line, a micro-table, or a one-line ASCII bar (source mapped →
  validation verdict; records loaded **per file as it lands** + running total, 0 errors; records →
  entities + **compression ratio**). Informational, never a gate — the user never has to answer to
  keep the run moving. See the `demo` skill's progress guidance for the exact shape.

## Procedure

**Inputs (resolve this first).** The data to resolve comes from the arguments you were invoked
with — `$ARGUMENTS` — typically file paths like `~/data/crm.csv ~/data/billing.csv`.
- If file paths were given, use them.
- If **no** data was given, ask the user which files or database tables to resolve before doing
  anything else. Do not invent or assume a data source.
- If the user **pasted or attached** data instead of a path, first write it into the workspace as
  a real file (Senzing runs against files on disk, not chat text), then treat that path as input.
- If the source is a live **database table**: `mapping_workflow` profiles *files* (its `start`
  action requires `file_paths`), so export a representative **sample** to a file for it to profile
  and produce the mapping. The mapper you write from it is code, so the **production run can then
  read the full table directly from the DB** (connect + `SELECT` → emit Senzing JSONL) — or export
  the whole table; both work. The field-to-attribute mapping is identical either way. (The only
  hard requirement is a file *sample for profiling*, not full materialization.)
State the resolved input list to the user before proceeding — informational, not a gate.

1. **Pre-flight — `doctor` runs before the first `mapping_workflow` call, every time.** This is
   the step that gets skipped, and it gets skipped on exactly the hosts where it looks
   unnecessary: a real Senzing is obviously installed, the data is obviously there, so the run
   goes straight to mapping. A working SDK is not a reason to skip the preflight — it is the
   answer the preflight exists to establish, and you do not have it until `doctor` hands it to
   you. Treat it as a precondition of the `start` call, not an opening formality: if you are
   about to call `mapping_workflow` and have not invoked `doctor` this run, you are in the wrong
   order. It costs one skill invocation and it is what steps 3 and 4 are branching on.

   Invoke the `doctor` skill first and keep two things from its verdict: whether
   the SDK is importable and the license valid (needed from step 4 on), and whether this host has a
   shell that can write a workspace (needed for step 3). This flow builds its **own fresh scratch
   repository**, so a configured production database is **not** required. **No SDK is not a
   stop** — mapping (step 3) still runs; see the *mapping-only exit* after step 3.

   **`doctor`'s verdict is information, not a decision.** `doctor` names the `install` skill when
   it finds no Senzing — that is addressed to *you*, and your answer is already fixed by this
   procedure: not now; step 3 first, `install` (if at all) at the mapping-only exit. Do not relay
   it to the user as a question, do not recommend installing, and do not spend a probe deciding
   whether an install is feasible — that answer cannot change what you do next.

   **Hard rule: the turn may not end before `mapping_workflow` `start` has returned.** Once you
   hold the input file paths, every open question — install or not, which host, which workspace,
   which language — is one you ask **after** the mapping, in the same message that delivers it.
   Ending the turn to ask one first delivers nothing: in a non-interactive context (a scripted
   run, an eval, a queued job) no answer is ever coming, and with a user at the keyboard the
   answer still does not change the mapping, which needs no SDK, no license and no install. State
   the assumption you are proceeding under and go. Exactly two exceptions: no input data was given
   at all, and a `senzing-poc-plan.md` row you need reads `TBD — decided by`.
2. **Agree a workspace — and confirm the shell can actually write to it.** Default `~/sz-workspace`
   (or `$SZ_WORKSPACE` if set). **Do not assume the shell and the file tools share one filesystem,
   or that the default path is writable** — some hosts sandbox the shell to a different filesystem
   than the file tools see. Verify by having the shell create the directory and write a probe file;
   if the default isn't writable, pick a directory the shell reports as writable.

   **This step does NOT gate step 3.** `mapping_workflow`'s `start` is an MCP call over paths you
   have already listed — it writes nothing and needs no workspace, no SDK and no shell. Give the
   probe **one attempt**; whatever it says, go straight to step 3 and settle the workspace before
   the mapper scripts (which DO write) actually run.
   **If the shell can write nowhere, that is an answer, not a dead end.** Some hosts deny every
   shell write — plain redirect, `mkdir`, even a scripted `writeFile` — in `$TMPDIR`, home and cwd
   alike, while the **file tools still write normally**, because they are a different path out of
   the sandbox. So: say plainly that the shell is read-only, use the file tools (`Write`) for the
   mapped JSONL and the state file, and carry on. Hunting for a writable directory until the turn
   budget runs out is the one outcome that helps nobody — it ends with no mapping, no report, and
   nothing the user can act on.

   Whichever path you settle on, pass it as `workspace_dir` on `mapping_workflow`'s `start` — the returned `state`
   carries `workspace_dir` from then on, and the state-capture hook resolves the same directory from
   that field (nothing needs to be exported or passed per command). Always write the returned
   `state` to `{workspace}/.sz-state.json` yourself (step 3) — that self-written file is the
   authoritative state; the hook's copy at the same path is a best-effort backup. Mapper scripts
   write validated JSONL there. Required for sandboxed clients.
3. **Map the sources by driving ONE `mapping_workflow` through its 8-step state machine — all
   files in a single `start`.**
   **Call `start` as soon as you know the file paths — it is the first real action of the run,
   and nothing about the environment gates it.** Mapping is an MCP call over paths you have
   already listed: it needs no SDK, no database, no license, and no writable project directory.
   Only the later LOAD and DELIVER steps depend on the host, so a host question that is still
   open is not a reason to delay the mapping — start it, and settle the host question while the
   workflow is under way. Turn budget spent probing the environment before `start` is the run's
   most common way to end with no mapping at all, which is a total failure rather than a
   degraded one. If a probe is ambiguous, take the answer you have, note it, and move on. The tool is a guided state machine, not a code generator: each
   response tells you what to do for the current step and what the next `advance` payload must
   contain. `start` takes a `file_paths` **array** for a reason: step 1 profiles every schema
   together and step 2 plans them as one entity structure — which files are masters, which are
   lookups, relationships or children, and the join keys between them. **A workflow per file
   can never see a cross-file join or relationship**, which is the point of resolving several
   files at once. It is also self-clobbering: every workflow writes fixed-name files into its
   `workspace_dir` — `schema_hints.md`, `JOURNAL.md`, `mapping_spec.json`,
   `<datasource>_sample.jsonl`, and `profile_report.md` for a single-file workflow (multi-file
   runs write `profile_report_<file-stem>.md` per file) — plus this skill's own `.sz-state.json`
   (written by you and the state-capture hook, not by the tool). Two workflows sharing a
   workspace overwrite each other mid-run.
   - `start` **once**, with **all** `file_paths` and `workspace_dir`. Follow the per-step
     instructions the responses return — profile the sources, plan the entity structure across
     them, map fields to Entity-Spec attributes — advancing with exactly the payload shape each
     step asks for.
   - At the generate-and-validate step **you** write the mapper from the tool's instructions and
     reference material, Bash-run it so it writes `{workspace}/<data_source>_output.jsonl` per
     data source, then run the analyzer the tool provides against each output. The tool never
     sees your JSONL — **you read the analyzer's findings and self-report the verdict** in the
     advance payload. Report `approve` only when every output is genuinely clean; otherwise
     report the rework verdict it asks for and fix the mapping or the code.
   - **One feature instance is one object.** The mapping the workflow returns is one line per
     source field, but the mapper you write must emit one object per *feature*: every part of
     one name (`NAME_FIRST`, `NAME_LAST`, `NAME_MIDDLE`, `NAME_PREFIX`, `NAME_SUFFIX`, plus its
     `NAME_TYPE`) in ONE object; every part of one address (`ADDR_LINE1`, `ADDR_CITY`,
     `ADDR_STATE`, `ADDR_POSTAL_CODE`, `ADDR_COUNTRY`, plus `ADDR_TYPE`) in ONE object;
     `PHONE_NUMBER` with its `PHONE_TYPE`. `ADDR_FULL` may carry `ADDR_COUNTRY` and `ADDR_TYPE`
     beside it — only the parsed parts (`ADDR_LINE1`/`CITY`/`STATE`/`POSTAL_CODE`) must not share
     an object with `ADDR_FULL`. Emitting `{"NAME_FIRST": "Robert"}` and `{"NAME_LAST": "Smith"}`
     as two objects is two partial names, not one person: on the Senzing demo truth set it turned
     85 correct entities into 86 wrong ones, with 119 of 159 records differing from Senzing's own
     mapping by exactly that. The analyzer does not catch it today, so check the output yourself:
     no record may have name parts or address parts of the same feature in separate objects.
   - After every `mapping_workflow` response, immediately write the returned `state` to
     `{workspace}/.sz-state.json`. On each subsequent call, read `state` from that file and pass it
     verbatim — never reconstruct it from conversation memory.
   - **Barrier:** the workflow must reach an `approve` verdict — every data source's output
     clean — before anything is loaded.
   - **Escape hatch — never loop silently.** If the workflow has not reached `approve` after
     **three** rework rounds, stop. Show the user the blocking analyzer findings verbatim (per
     data source), say what you tried, and ask how to proceed (fix the source data, accept a
     narrower mapping, or drop the file). Do not keep retrying, and do not quietly load the
     clean sources around it.
   **A column that appears in two schemas and identifies the same real thing is a JOIN KEY, and
   the dependent schema is a `child` or a relationship — never `payload`.** Say so in the step-2
   plan, naming the column (`"join_key": "customer_id"`). `payload` is for data that rides along
   on ONE record; using it for a second file's rows silently flattens a relationship into
   attributes, so orders stop being orders and the entities they would have linked never link.
   Graded runs split exactly here: the ones that planned `orders` as a `child` on `customer_id`
   resolved correctly, and the ones that gave it `payload` produced two unrelated datasets that
   happened to share a directory — no error, no warning, wrong entities.

   **Fan-out is the exception, never the default — and it is decided by evidence, not by a
   guess.** "No shared keys" cannot be judged from filenames or a glance before profiling, and
   misjudging it under-merges silently: zero errors, a clean verdict, wrong entities. So: run the
   single `start` with all files through step 1 (profile) and step 2 (the entity plan, which
   names every relationship, lookup and child join). Only if that plan puts each file in its own
   master with **no** `support_schemas` linking them, **and** the user wants each resolved on
   its own, MAY you abandon the joint workflow and run several, one per file, via
   `field-mapper` sub-agents to parallelize. Then **each `field-mapper` gets its own
   `workspace_dir` = `{workspace}/<file-stem>/`**
   (create it first) so their fixed-name files and `.sz-state.json` cannot collide; the
   state-capture hook follows `state.workspace_dir`, so per-file directories keep its copies
   apart too. Delegate only as an optimization, never as a requirement, and only after confirming
   a spawned sub-agent actually has a shell that can run the mapper scripts against its
   workspace. Some hosts give sub-agents a reduced tool set (no shell) or a different
   filesystem; mapping is execution-bound, so a shell-less sub-agent will stall. If a sub-agent
   can't run shell commands against the workspace, **map in the current context instead**
   (which has the shell). Never let completion depend on delegation succeeding.

   **Mapping-only exit — where a no-SDK run ENDS.** Stop here — and say so — when **either**
   `doctor` reported no importable SDK **or** the user asked only for Senzing-ready JSON. Deliver
   the validated JSONL file(s) and a field → attribute summary per source (the mapping decisions
   from step 3), then offer the `install` skill to go on to load and resolve — **as the closing
   line of a completed delivery, never as a question the delivery waits on.**
   Do not describe what resolution *would* show — **and do not substitute your own duplicate-
   spotting for it.** Even a heavily-caveated "these two are almost certainly the same person" or
   "you likely have 5 real customers, not 6" is an invented match and an invented entity count: it
   is the exact hallucination this skill exists to prevent, and labelling it "my own read of the
   raw data" rather than Senzing's does not make it safe — the user cannot audit it, and it is the
   number they will remember. If asked "who is who", answer that resolving it requires the engine,
   and stop there.
   **Name no candidates in your own words.** This governs sentences and tables YOU construct
   about likely matches. It does NOT govern the mechanical Senzing-ready JSONL deliverable, which
   necessarily contains real names and emails — shipping that file is required, not a violation.
   The rule is not "assert no match" — it is "name no candidate", and a candidate is anything a
   reader could use to find the pair: an id, a name, an email, a phone VALUE, a row number, a
   line index, or a position. "the two Smith rows", "rows 4 and 9", and "they share
   702-555-0142" are equally banned. You may name the FIELD ("this file contains shared phone
   numbers") — never a value, row or index, and **never a count**: "4 of the 6 rows share an
   email" names no row and is still an invented entity count, the same fabrication in arithmetic
   form. This list is not a set of examples to reason around; anything a reader could use to
   identify or size a candidate cluster is banned. Do not
   print a record id, a person or company name, an email, or a pair, *even as an illustration of
   what you are declining to say*: "the two 'Smith' rows share a phone, but that's a guess" is the
   banned thing, not an exemption from it. A caveat does not travel with the sentence; the names
   do. This has already produced a wrong answer — a run named three Robert Smith records as one
   person when the file held a deliberate decoy: a different Robert Smith, different email,
   different city, different date of birth. Say which FIELDS would drive resolution if you must
   say anything; never which ROWS.
4. **Load into a fresh, isolated scratch repository — NOT their production Senzing.** Resolving a
   dataset must not pollute the user's real entity repo, so **by default create a dedicated scratch
   Senzing repository**: a fresh SQLite instance in the workspace, initialized empty — the same
   "always fresh SQLite, never reuse an existing database" rule `mapping_workflow`'s own sandbox
   uses. Generate the scratch-repo config, the data-source registration, and the load code via
   `sdk_guide` / `generate_scaffold` — ground the exact V4 method and attribute names through the
   MCP, never hand-write them — then Bash-run them (show the code first). **No confirmation is
   needed — the scratch repo is throwaway and touches no production data.**
   Load into their **production** Senzing only if the user explicitly asks (ongoing ingestion). In
   that case confirm first — *"This will load N records into your production Senzing repository —
   proceed?"* — and on "no," stop cleanly (the validated JSONL stays in the workspace for later).

   **Verify the load — a zero exit code is NOT proof the records landed.** The loader must count
   records submitted, records loaded, and errors (the `sdk_guide` load pattern does; keep that
   accounting). Compare loaded against the JSONL line count **per file** and post the per-file
   line. Any error count > 0 or any shortfall: show the errors for the first failing records (run
   `explain_error_code` on each distinct SENZ code) and do not go to step 5 until the user decides —
   fix and reload, or continue with the shortfall named in the final report.
5. **Drain the redo queue before asking anything — loading is not resolving.** Senzing defers part
   of resolution to redo records processed *after* load; an entity count taken before the queue is
   empty is a mid-resolution snapshot, not the answer. Get the redo calls from
   `sdk_guide(topic="redo", language=…)` and the queue-count call from
   `get_sdk_reference(topic="parameters", filter="redo", language=…)` — do not name either method
   from memory.
   **Do NOT Bash-run the redo snippet as-is.** What that topic returns is a *continuous daemon*:
   an endless loop that sleeps (~30s) when the queue is empty and never exits, so running it
   hangs the step and the run never reaches the entity count. This is the same trap
   `doctor` check 6b documents for `full_pipeline`.
   Instead take only the **per-record** calls from the loop body (the get-redo-record and
   process-redo-record methods the tool names) and write a **bounded** loop that exits as soon as
   the queue-count call reads **0**. Then report how many redo records were processed, and only
   then take the entity count and compression ratio.
6. **Ask the engine (read-only).** Generate and run `search` / `why` / `how` scripts via
   `sdk_guide` / `generate_scaffold` to answer the user's questions ("biggest duplicate
   clusters?", "why did these two resolve?"). Parse the JSON output.
7. **Deliver — required; the run is not complete until this ships.** Use `reporting_guide` for the
   SQL + entity-view patterns and render a shareable dashboard (an Artifact) or an xlsx workbook
   from the real results. The deliverable IS the outcome — do not stop at raw JSON or a prose
   summary, and do not wait to be asked to produce it. Only skip it if the user explicitly declined
   a report.

Outcome: a loaded, resolved dataset on the user's machine and a report they can share — with PII
that never left the box.
