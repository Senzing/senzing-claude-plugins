---
type: tool_used
tool: Bash
# See `plugins/senzing/evals/analyze/graders/mapper-ran-in-bash.md` — same
# back-port, same reason. A bare `tool_used: Bash` is satisfied by `pwd`.
#
# The mapper is the script `mapping_workflow` hands back, invoked as
# `<name>_mapper.<ext> <input…> -o <workspace>/<name>_output.jsonl`, so a Bash
# command that really ran it names a mapper AND writes a .jsonl.
#
# CHECKED against this environment (no Senzing SDK in the sandbox) before
# porting. Every multi-file-join session in the last full run (f2) issued a
# matching command — trace-25/61 and trace-29/65 both ran
# `python3 customers_mapper.py ../customers.csv ../orders.csv -o customers_output.jsonl`
# (1 match each, out of 14 and 25 Bash calls) — while the four `recipes`
# sessions in the same run matched zero times across 1-9 Bash calls each.
input_match: '_output\.jsonl'
min: 1
---

## Why the pattern names the OUTPUT, not the script (2026-09-25)

This matched the token `mapper` in the Bash command — a filename the plugin does not own.
`analyze/SKILL.md:146` says "**you** write the mapper", and `grep -rn "_mapper"` finds nothing
outside these graders: no skill, agent or hook names it. The convention belongs to the MCP
server's workflow instructions, so a server-side rename would red two cases with zero plugin
defect, and a run that named its script `map_crm.py` failed while doing everything right.

`{workspace}/<data_source>_output.jsonl` IS the plugin's: `analyze/SKILL.md:147` specifies it, the
analyzer step consumes it, and the downstream load reads it. Asserting the output keeps the real
obligation — the mapping was produced by running code, not hand-written — while dropping a
dependency on someone else's naming.

Discrimination is unchanged where it matters: a hand-coded mapping writes no `_output.jsonl`, and
the sessions this grader is meant to exclude write no `.jsonl` at all.
