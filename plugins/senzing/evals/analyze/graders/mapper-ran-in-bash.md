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
input_match: 'mapper[\s\S]{0,400}?\.jsonl'
min: 1
---
