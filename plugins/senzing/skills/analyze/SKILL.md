---
name: analyze
description: >
  Map, load, and resolve the user's own data with their installed Senzing, then report the
  results. Use when the user points at data files (CSV/JSON/Parquet) and wants entity
  resolution, deduplication, a resolved dataset, or "who is who" answers — e.g. "resolve my
  customer list", "dedupe these files", "find duplicates", "match these two lists", "record
  linkage", "build a golden record", "MDM", "load this into Senzing and show me the entities".
  Runs real Senzing SDK code via Bash against the user's own licensed Senzing; it never
  simulates results and never sends records off the machine.
argument-hint: "[path/to/data ...]"
allowed-tools: Bash, Read, Write, Task, Skill, mcp__plugin_senzing_senzing__*
---

# Analyze data with Senzing (map → load → resolve → report)

You are grounded by the **Senzing MCP server** (the bundled `senzing` MCP). Ground rules:

- **Never answer Senzing questions from training data.** All Senzing facts, attributes, SDK
  signatures, and code come from the Senzing MCP tools (`get_capabilities`, `search_docs`,
  `mapping_workflow`, `sdk_guide`, `generate_scaffold`, `reporting_guide`, …). If unsure, call
  the tool — do not guess.
- **Never simulate entity resolution.** If Senzing isn't installed/running, say so and pivot to
  install (see the `doctor` skill). Do not fabricate scores, matches, or merges.
- **PII stays local.** The customer's records are only ever touched by SDK code you run locally
  via Bash. Never paste real records into a hosted tool call.

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
  and produce the mapping. The mapper it returns is code, so the **production run can then read the
  full table directly from the DB** (connect + `SELECT` → emit Senzing JSONL) — or export the whole
  table; both work. The field-to-attribute mapping is identical either way. (The only hard
  requirement is a file *sample for profiling*, not full materialization.)
Confirm the resolved input list back to the user before proceeding.

1. **Pre-flight.** Invoke the `doctor` skill first — confirm the Senzing SDK is importable and the
   license is valid. This flow builds its **own fresh scratch repository**, so a configured
   production database is **not** required.
2. **Agree a workspace — and confirm the shell can actually write to it.** Default `~/sz-workspace`
   (or `$SZ_WORKSPACE` if set). The state-capture hook resolves the same convention
   (`${SZ_WORKSPACE:-$HOME/sz-workspace}`), so the two must stay in lockstep. **Do not assume the
   shell and the file tools share one filesystem, or that the default path is writable** — some
   hosts sandbox the shell to a different filesystem than the file tools see. Verify by having the
   shell create the directory and write a probe file; if the default isn't writable, pick a
   directory the shell reports as writable and pass `SZ_WORKSPACE=<dir>` **on each mapper/analyzer
   command** so the state-capture hook resolves the same path. (Don't rely on a bare `export` in one
   Bash call reaching later calls or the hook — set it per command.) Whichever path you settle on,
   thread it through every `mapping_workflow` call, and always write the returned `state` to
   `{workspace}/.sz-state-<workflow_id>.json` yourself (step 3) — that self-written file is the
   authoritative state; the hook backup is best-effort. Mapper scripts write validated JSONL there.
   Required for sandboxed clients.
3. **Map each source (fan out, then a barrier).** For every input file:
   - Call `mapping_workflow` — it returns a **mapper script + instructions** (not JSONL).
   - Run that mapper script with Bash → it writes `{workspace}/<data_source>_output.jsonl`.
   - Submit the `output_path` back to `mapping_workflow` so the tool **validates** the JSONL
     against the Entity Specification.
   - After every `mapping_workflow` response, immediately write the returned `state` to
     `{workspace}/.sz-state-<workflow_id>.json`. On each subsequent call, read `state` from that
     file and pass it — never reconstruct it from conversation memory. **Barrier:** every source
     must reach an `approve` verdict before anything is loaded.
   **Mapping many files — delegate only as an optimization, never as a requirement.** If several
   files need mapping you MAY fan out `field-mapper` sub-agents (one per file) to parallelize — but
   only after confirming a spawned sub-agent actually has a shell that can run the mapper scripts
   against the workspace. Some hosts give sub-agents a reduced tool set (no shell) or a different
   filesystem; mapping is execution-bound, so a shell-less sub-agent will stall. If a sub-agent
   can't run shell commands against the workspace, **map the files sequentially in the current
   context instead** (which has the shell). Never let completion depend on delegation succeeding.
4. **Load into a fresh, isolated scratch repository — NOT their production Senzing.** Resolving a
   dataset must not pollute the user's real entity repo, so **by default create a dedicated scratch
   Senzing repository**: a fresh SQLite instance in the workspace, initialized empty — the same
   "always fresh SQLite, never reuse an existing database" rule `mapping_workflow`'s own sandbox
   uses. Generate the scratch-repo config, the data-source registration, and the load code via
   `sdk_guide` / `generate_scaffold` — ground the exact V4 method and attribute names through the
   MCP, never hand-write them — then Bash-run them (show the code first). **No confirmation is needed — the scratch repo is throwaway and touches no production
   data.**
   Load into their **production** Senzing only if the user explicitly asks (ongoing ingestion). In
   that case confirm first — *"This will load N records into your production Senzing repository —
   proceed?"* — and on "no," stop cleanly (the validated JSONL stays in the workspace for later).
5. **Ask the engine (read-only).** Generate and run `search` / `why` / `how` scripts via
   `sdk_guide` / `generate_scaffold` to answer the user's questions ("biggest duplicate
   clusters?", "why did these two resolve?"). Parse the JSON output.
6. **Deliver — required; the run is not complete until this ships.** Use `reporting_guide` for the
   SQL + entity-view patterns and render a shareable dashboard (an Artifact) or an xlsx workbook
   from the real results. The deliverable IS the outcome — do not stop at raw JSON or a prose
   summary, and do not wait to be asked to produce it. Only skip it if the user explicitly declined
   a report.

Outcome: a loaded, resolved dataset on the user's machine and a report they can share — with PII
that never left the box.
