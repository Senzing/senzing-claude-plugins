---
name: report
description: >
  Explore and report on entities ALREADY loaded in the user's Senzing — why records resolved,
  largest entities, match quality, dashboards — using read-only search/why/how calls and reporting
  SQL, rendered as a shareable result. Use when the data is already in Senzing — e.g. "why did
  these two resolve?", "show me my biggest entities", "dashboard of my resolved entities", "run
  some ER quality checks". Use it even when there may be nothing loaded — a brand-new, empty or
  unknown-size repository is this skill's job too, because establishing the entity count and
  refusing rather than inventing one IS the work. "The repository is empty" is a reason to run
  this skill, never a reason to answer the question without it. Read-only: never loads or
  mutates. Runs doctor first to confirm this host can deliver the result. Not for starting from
  data files (use analyze) or writing reporting code into a project (use build).
argument-hint: "[question]"
allowed-tools: Bash, Read, Write, Agent, Skill, mcp__plugin_senzing_senzing__*
---

# Report over an already-loaded Senzing

No mapping, no load — the data is already resolved. Grounded by the **Senzing MCP server**.

**Inputs.** `$ARGUMENTS` may carry the question (e.g. "why did A and B resolve?", "biggest
entities"). If none is given, ask what they want to see before running anything.

1. Pre-flight with `doctor`, then close the two gaps it leaves for this skill:
   - **Engine configuration.** `doctor` grades an unset `SENZING_ENGINE_CONFIGURATION_JSON` as ➖
     (not applicable) and cascades its database check to ➖ — so on a loaded repository whose
     config lives anywhere else it comes back green with **no reachable database**. If the config
     row is ➖, **ask the user for the engine configuration** (or where their application loads it
     from) before doing anything else. A skill cannot re-invoke `doctor`'s database check, so
     verify the database yourself, directly, with the matching client — `sqlite3 <path> .tables`
     for a SQLite file, `psql` for PostgreSQL, `mysql` for MySQL — before running anything.
   - **Entities present.** `doctor` never counts entities, and neither does
     `sdk_guide(topic="information")` — its snippets are version, license, repository info,
     repository performance and (Python only) stats. Get the count from `reporting_guide`: the
     `export` pattern (`reporting_guide(topic="export", language=…)`) streams every resolved
     entity — Bash-run it and count the rows. It works on any **persisted** connection (SQLite,
     PostgreSQL, …). If the config is `internal://` there is nothing a new process can report
     on — `engine_config_notes` says that store lives only in the process that loaded it, so a
     Bash-run export opens an empty store and counts 0 for the wrong reason; say so and offer
     `/senzing:analyze` with a SQLite scratch repository instead of grading it as empty. The
     `reports` SQL counts entities too, but only against the mart tables it describes, which
     exist only if the user built them — use it when they have. Show the number. **Zero →
     refuse**: say so and offer `/senzing:analyze` to load data first. To be explicit, because
     "report" is both this skill's name and the thing it emits: **you DO run this skill on an
     empty repository** — running it is how the zero becomes established fact instead of a guess.
     What you must never do is emit entity findings, counts or a dashboard from an empty one.
     Run, establish zero, say so, hand off. Never decline to run because you suspect it is empty.
2. For entity questions, generate read-only `search` / `why` / `how` scripts via `sdk_guide` /
   `generate_scaffold` and Bash-run them; parse the JSON.
3. For analytics/quality, use `reporting_guide` (topics: reports, entity_views, data_mart,
   quality, evaluation) for the SQL and schema, and run it against the user's database. If a query
   sweep runs long, **narrate progress as a compact visual, unprompted** — a one-line stat line or
   micro-table of real numbers as each result lands, not silence and not prose (see the `demo`
   skill's progress guidance). Informational, never a gate.
4. **Deliver — required; the report is not complete until this ships.** Render a shareable dashboard
   (Artifact) or xlsx from the real results — a link, not a query. The rendered result is the
   deliverable; produce it without waiting to be asked.
Never simulate resolution or fabricate metrics.
