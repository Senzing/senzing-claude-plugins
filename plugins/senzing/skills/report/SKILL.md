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
allowed-tools: Read, Skill(senzing:doctor), Skill(senzing:analyze), mcp__plugin_senzing_senzing__*
---

# Report over an already-loaded Senzing

No mapping, no load — the data is already resolved. Grounded by the **Senzing MCP server**.

**Inputs.** `$ARGUMENTS` may carry the question (e.g. "why did A and B resolve?", "biggest
entities"). If none is given, ask what they want to see before running anything.

1. Pre-flight with `doctor`, then close the two gaps it leaves for this skill:

   **Supplied-preflight carve-out — it reads off the user's own words, not your impression of
   the shell.** Only when the user's own message BOTH supplies `doctor`'s result for their
   Senzing host AND states that this shell is not that host, take the result as given and do not
   re-probe this shell — a probe here reports on the wrong machine, and "one correction to your
   premise: this host has no Senzing SDK" is a report on the sandbox, not on their Senzing. One of
   those two conditions alone does not open it, and **your own inference that the shell looks
   sandboxed does not qualify.** `doctor` is deferred here, not waived: it runs on the Senzing
   host the moment a command runs there, and its verdict decides whether anything is read. With
   the pre-flight supplied, close the two gaps below from the user's words alone.

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
     `/senzing:analyze` with a SQLite scratch repository instead of grading it as empty. **On this
     branch you may not certify the repository as empty at all** — not "it is empty", not "zero is
     the correct established answer". You cannot see it, so the honest report is that the count is
     unverifiable from here, and why. You may relay a zero the user stated, but only as theirs, in
     the sentence that states it — *"you said the repository is brand new, so there is nothing to
     report on yet"*. A zero in your own voice is a finding: no `Entity count: 0`, no stat line,
     no table cell, no "the repository is empty" — the same number, unattributed, is the
     certification this branch forbids. The
     `reports` SQL counts entities too, but only against the mart tables it describes, which
     exist only if the user built them — use it when they have. On a persisted connection, show
     the number. **Zero → refuse**: say so and offer `/senzing:analyze` to load data first. To be explicit, because
     "report" is both this skill's name and the thing it emits: **you DO run this skill on an
     empty repository** — running it is how the zero becomes established fact instead of a guess.
     What you must never do is emit entity findings, counts or a dashboard from an empty one.
     **End with the hand-off as a runnable command.** Whenever you refuse or redirect, your last
     message names `/senzing:analyze` (their files) or `/senzing:demo` (sample data) literally —
     not "load some data first", and not only earlier in the conversation. A summary that drops
     the command leaves the user with a refusal and no next step.
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
