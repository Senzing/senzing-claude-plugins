---
type: tool_used
tool: Bash
min: 0
max: 0
---

# Grader: the planning run touched no shell

`poc-planner` runs no shell command (rule 8). Its plan-structure check is done on the text
`Read` returns, so even the two reflexes rule 8 names by name — `ls` to see whether the plan
file exists and `grep` for TBDs in the plan just written — are defects here. `min: 0` is
required: declaring only `max: 0` makes the harness default `min` to 1, the impossible range
`1..0`.

This replaced `validator-ran.md` and `no-unsanctioned-shell.md` when `validate_plan.py` left
the plugin: the Claude directory accepts no script file from an organization that isn't
Verified. Restoring the validator restores both graders (see the CHANGELOG).
