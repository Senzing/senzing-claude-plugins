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
input_match: 'mapper[\s\S]{0,400}?\.jsonl'
min: 1
---
