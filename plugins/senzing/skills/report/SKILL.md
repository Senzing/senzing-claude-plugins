---
name: report
description: >
  Explore and report on entities ALREADY loaded in the user's Senzing — why records resolved,
  largest entities, match quality, dashboards — using read-only search/why/how calls and reporting
  SQL, rendered as a shareable result. Use when the data is already in Senzing — e.g. "why did
  these two resolve?", "show me my biggest entities", "dashboard of my resolved entities", "run
  some ER quality checks". Read-only: never loads or mutates. Runs doctor first to confirm this
  host can deliver the result. Not for starting from data files (use analyze) or writing reporting
  code into a project (use build).
argument-hint: "[question]"
allowed-tools: Bash, Read, Write, Task, Skill, mcp__plugin_senzing_senzing__*
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
     from) before doing anything else, and re-run the database check with it.
   - **Entities present.** `doctor` never counts entities. Before any report, run a read-only
     count against the repository — get the call from `sdk_guide(topic="information", language=…)`
     or the query from `reporting_guide` — and show the number. **Zero → refuse**: say so and offer
     `/senzing:analyze` to load data first. Never report on an empty instance.
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
