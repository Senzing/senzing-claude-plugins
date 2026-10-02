---
type: tool_used
tool: Bash
input_match: '(^|[;&|]\s*)(ls|grep)\s'
max: 0
---

# Grader: the two shell reflexes rule 8 names never happen

`poc-planner` sanctions exactly one command, `validate_plan.py`. Rule 8 calls out the
two that keep reappearing anyway, both on the model's *own* output:

- `ls -la ./senzing-poc-plan.md` — step 8 asks whether the plan file exists, and `Read`
  already answers that: if it errors, there is no file.
- `grep -n "TBD" ./senzing-poc-plan.md` — step 8 asks the model to check every TBD in a
  file it just wrote and already holds.

Both look harmless, which is exactly why they recur: the output is the model's own and
the command reads rather than writes. They are still shell calls in a planning skill
that is not supposed to touch a host.

This replaces the bound half of a `min: 1, max: 1` grader. A count could not tell a
legitimate second validation pass — the repair loop step 8 mandates — from an `ls`, so
it failed correct runs to catch incorrect ones. Matching the command separates them.
