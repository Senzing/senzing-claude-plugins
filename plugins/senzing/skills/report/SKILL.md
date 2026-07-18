---
name: report
description: >
  Explore and report on entities in an already-loaded Senzing instance. Use when the user has
  data in Senzing already and wants to understand it — e.g. "why did these two resolve?", "show
  me my biggest entities", "build me a dashboard of resolved entities", "run some ER quality
  checks". Generates and runs read-only search/why/how and reporting SQL, then renders the result.
argument-hint: "[question]"
allowed-tools: Bash, Read, Write, Task, Skill, mcp__plugin_senzing_senzing__*
---

# Report over an already-loaded Senzing

No mapping, no load — the data is already resolved. Grounded by the **Senzing MCP server**.

**Inputs.** `$ARGUMENTS` may carry the question (e.g. "why did A and B resolve?", "biggest
entities"). If none is given, ask what they want to see before running anything.

1. Pre-flight with `doctor` (engine reachable, entities present). If the instance has **no entities
   loaded**, say so and offer `/senzing:analyze` to load data first — do not report on an empty
   instance.
2. For entity questions, generate read-only `search` / `why` / `how` scripts via `sdk_guide` /
   `generate_scaffold` and Bash-run them; parse the JSON.
3. For analytics/quality, use `reporting_guide` (topics: reports, entity_views, data_mart,
   quality, evaluation) for the SQL and schema, and run it against the user's database.
4. **Deliver — required; the report is not complete until this ships.** Render a shareable dashboard
   (Artifact) or xlsx from the real results — a link, not a query. The rendered result is the
   deliverable; produce it without waiting to be asked.
Never simulate resolution or fabricate metrics.
