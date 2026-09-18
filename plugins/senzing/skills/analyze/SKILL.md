---
name: analyze
description: >
  Answer "who is who" in the user's own data files, end to end: map to the Entity Spec, load into a
  throwaway scratch repository, resolve, then deliver a shareable report. Use when the user points
  at CSV/JSON/Parquet files and wants deduplication, record linkage, a resolved dataset, or entity
  resolution — e.g. "resolve my customer list", "dedupe these files", "find duplicates", "match
  these two lists", "load this into Senzing and show me the entities". Also the entry point for
  mapping alone, when the user wants only Senzing-ready JSON or has no Senzing installed. Runs real
  SDK code locally via Bash; records never leave the machine and results are never simulated. Runs
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
- **Never simulate entity resolution.** If Senzing isn't installed/running, say so and hand off to
  the **`install`** skill — it surfaces the license agreement and verifies with `doctor`; do not
  route around it by calling `sdk_guide(topic="install")` directly. Do not fabricate scores,
  matches, or merges.
- **PII stays local.** The customer's records are only ever touched by SDK code you run locally
  via Bash. Never paste real records into a hosted tool call.
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

1. **Pre-flight.** Invoke the `doctor` skill first and keep two things from its verdict: whether
   the SDK is importable and the license valid (needed from step 4 on), and whether this host has a
   shell that can write a workspace (needed for step 3). This flow builds its **own fresh scratch
   repository**, so a configured production database is **not** required. **No SDK is not a
   stop** — mapping (step 3) still runs; see the *mapping-only exit* after step 3.
2. **Agree a workspace — and confirm the shell can actually write to it.** Default `~/sz-workspace`
   (or `$SZ_WORKSPACE` if set). **Do not assume the shell and the file tools share one filesystem,
   or that the default path is writable** — some hosts sandbox the shell to a different filesystem
   than the file tools see. Verify by having the shell create the directory and write a probe file;
   if the default isn't writable, pick a directory the shell reports as writable. Whichever path you
   settle on, pass it as `data.workspace_dir` on `mapping_workflow`'s `start` — the returned `state`
   carries `workspace_dir` from then on, and the state-capture hook resolves the same directory from
   that field (nothing needs to be exported or passed per command). Always write the returned
   `state` to `{workspace}/.sz-state.json` yourself (step 3) — that self-written file is the
   authoritative state; the hook's copy at the same path is a best-effort backup. Mapper scripts
   write validated JSONL there. Required for sandboxed clients.
3. **Map the sources by driving ONE `mapping_workflow` through its 8-step state machine — all
   files in a single `start`.** The tool is a guided state machine, not a code generator: each
   response tells you what to do for the current step and what the next `advance` payload must
   contain. `start` takes a `file_paths` **array** for a reason: step 1 profiles every schema
   together and step 2 plans them as one entity structure — which files are masters, which are
   lookups, relationships or children, and the join keys between them. **A workflow per file
   can never see a cross-file join or relationship**, which is the point of resolving several
   files at once. It is also self-clobbering: every workflow writes fixed-name files into its
   `workspace_dir` (`profile_report.md`, `schema_hints.md`, `JOURNAL.md`, `.sz-state.json`), so
   two workflows sharing a workspace overwrite each other mid-run.
   - `start` **once**, with **all** `file_paths` and `data.workspace_dir`. Follow the per-step
     instructions the responses return — profile the sources, plan the entity structure across
     them, map fields to Entity-Spec attributes — advancing with exactly the payload shape each
     step asks for.
   - At the generate-and-validate step **you** write the mapper from the tool's instructions and
     reference material, Bash-run it so it writes `{workspace}/<data_source>_output.jsonl` per
     data source, then run the analyzer the tool provides against each output. The tool never
     sees your JSONL — **you read the analyzer's findings and self-report the verdict** in the
     advance payload. Report `approve` only when every output is genuinely clean; otherwise
     report the rework verdict it asks for and fix the mapping or the code.
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
   **Fan-out is the exception, never the default.** Only when the files are *genuinely
   independent* — no shared keys, no relationship between them, and the user wants each resolved
   on its own — MAY you run several workflows, one per file, via `field-mapper` sub-agents to
   parallelize. Then **each `field-mapper` gets its own `workspace_dir` = `{workspace}/<file-stem>/`**
   (create it first) so their fixed-name files and `.sz-state.json` cannot collide; the
   state-capture hook follows `state.workspace_dir`, so per-file directories keep its copies
   apart too. Delegate only as an optimization, never as a requirement, and only after confirming
   a spawned sub-agent actually has a shell that can run the mapper scripts against its
   workspace. Some hosts give sub-agents a reduced tool set (no shell) or a different
   filesystem; mapping is execution-bound, so a shell-less sub-agent will stall. If a sub-agent
   can't run shell commands against the workspace, **map in the current context instead**
   (which has the shell). Never let completion depend on delegation succeeding.

   **Mapping-only exit.** Stop here — and say so — when **either** `doctor` reported no importable
   SDK **or** the user asked only for Senzing-ready JSON. Deliver the validated JSONL file(s) and a
   field → attribute summary per source (the mapping decisions from step 3), then offer the
   `install` skill to go on to load and resolve. Do not describe what resolution *would* show.
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
   empty is a mid-resolution snapshot, not the answer. Get the drain loop from
   `sdk_guide(topic="redo", language=…)` and the queue-count call from
   `get_sdk_reference(topic="parameters", filter="redo", language=…)` — do not name either method
   from memory. Bash-run the drain until the count reads **0**, then report how many redo records
   were processed. Only then take the entity count and compression ratio.
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
