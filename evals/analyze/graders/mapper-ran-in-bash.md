---
type: tool_used
tool: Bash
# The obligation is "run the mapper mapping_workflow returned via Bash — never
# hand-code the mapping". `tool_used: Bash` alone was satisfied by `pwd` or
# `echo hi`, so this grader could not fail. The corrected form already existed
# one directory over (`evals-real/resolve-truthset/graders/mapper-ran-in-bash.md`)
# and was never back-ported; this is that port.
#
# The mapper is the script `mapping_workflow` hands back from
# mcp.senzing.com/resources, and the workflow's own instruction is
# `<name>_mapper.<ext> <input> -o <workspace>/<name>_output.jsonl`, so a Bash
# command that really ran it names a mapper AND writes a .jsonl.
#
# CHECKED against this environment before porting, because a pattern that is
# right for evals-real could be always-red here: this sandbox has NO Senzing
# SDK, so the run stops before loading. It does NOT stop before mapping — the
# mapper is what produces the zero-install prep tier's deliverable. Every
# analyze-family session in the last full run (f2) issued a matching command:
#   trace-5/41   25 Bash calls, 4 matches (node customer_mapper.ts … -o crm_output.jsonl)
#   trace-10/46  20 Bash calls, 2 matches (python3 customer_mapper.py ../crm.csv -o crm_output.jsonl)
# and the four `recipes` sessions in the same run made 1-9 Bash calls each with
# ZERO matches — so the pattern separates a run that mapped from one that did not.
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
