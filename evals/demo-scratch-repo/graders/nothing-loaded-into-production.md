---
type: tool_used
tool: Bash
input_match: 'add_record|addRecord|postgres(?:ql)?://'
min: 0
max: 0
---

`SENZING_ENGINE_CONFIGURATION_JSON` was removed from this pattern. It fired on `doctor` check 7
merely READING the variable (`if [ -z "${SENZING_ENGINE_CONFIGURATION_JSON}" ]; then …`), so a
grader named "nothing loaded into production" failed a run for probing whether a config existed.
Narrowing it to the assignment instead would be worse, not better: a CORRECT scratch demo MUST
`export SENZING_ENGINE_CONFIGURATION_JSON=` pointing at its brand-new scratch SQLite file, so an
assignment ban would fail the run for doing exactly the right thing. The remaining tokens are the
production signal only — writing records (`add_record` / `addRecord`) and a `postgres://` or
`postgresql://` connection string (this case's production repository is PostgreSQL). The bare
`postgres://` scheme is included alongside `postgresql://`; a scratch repo is `sqlite3://` or
`internal://` and matches neither.
