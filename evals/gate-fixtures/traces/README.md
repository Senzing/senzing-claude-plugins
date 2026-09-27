# Fixture traces

`gate.py`'s session check reads each run's `tracePath` and looks for the `system`/`init`
event's `mcp_servers[].status`. It now FAILS the run when it could not read a single trace
(see `session_defects`), so the fixtures have to look like real CLI output: every non-errored
run carries a `tracePath`, and errored runs carry `""` — which is exactly what the CLI writes
(measured across twelve real `aggregate-result.json` files in `../results/`).

`connected.jsonl` is the one trace they all point at. The paths in the fixtures are RELATIVE;
`gate.py` resolves a relative `tracePath` against the directory of the result JSON, so these
work from any cwd. Real CLI output is absolute.

To exercise the fail-closed path itself, `traces-unreadable.json` points at a file under this
directory that deliberately does not exist.
