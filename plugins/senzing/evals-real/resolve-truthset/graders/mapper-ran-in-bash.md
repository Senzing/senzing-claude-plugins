---
type: tool_used
tool: Bash
# The obligation is "run the mapper mapping_workflow returned via Bash — never
# hand-code the mapping". `tool_used: Bash` alone was satisfied by `pwd` or
# `echo hi` (exactly what the traces of the two bwrap-dead runs contain). The
# mapper is `mapper.py` from mcp.senzing.com/resources and the workflow's own
# instruction is `<name>_mapper.<ext> <input> -o <workspace>/<name>_output.jsonl`,
# so the Bash command must name a mapper AND write a .jsonl.
input_match: 'mapper[\s\S]{0,400}?\.jsonl'
min: 1
---
