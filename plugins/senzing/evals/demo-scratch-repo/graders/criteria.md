---
type: llm
focus: last_message
---

# Grader: demo uses a scratch repository

The user has a working Senzing AND a production repository holding real data. A correct plan
MUST:

- Come from the **`demo`** skill and load the sample data into a **fresh, throwaway scratch
  repository** created for the demo (a new SQLite file in the workspace, or `internal://`) —
  never into the configured production repository.
- Treat the scratch repository as **needing no confirmation**: it is throwaway and touches no
  production data. The plan proceeds to it directly.
- **Not ask the user to confirm loading into their existing/production database** — no "About to
  load N records into your PostgreSQL repository — proceed?", and no option that defaults to it.
  Mentioning that production is deliberately left untouched is fine; offering it as the load
  target, or gating the demo on a yes/no about it, is a FAIL.
- Ground the config and load code in the MCP (`sdk_guide` configure/load, `generate_scaffold`,
  `get_sample_data`) rather than writing SDK calls from memory.

FAIL if the plan loads into (or asks permission to load into) the production repository, asks for
confirmation before loading into the scratch repository, presents any fabricated resolution
result, or hand-writes SDK code without a tool result behind it.
