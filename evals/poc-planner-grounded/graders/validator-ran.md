---
type: tool_used
tool: Bash
input_match: 'validate_plan\.py'
min: 1
---

# Grader: the plan was validated before the user got it

This case writes a plan, and step 8 requires running `validate_plan.py` on it and
**fixing what it names until it prints `plan is well formed`**. So this asserts the
validator actually ran — the half that matters, and the half the old grader could
never express.

**History, because this grader has been wrong twice in one day.**

It was `max: 0` ("this skill never needs a shell"), written before the validator
existed. When the validator landed, `max: 0` contradicted the skill it graded and
the case failed deterministically.

It was then `min: 1, max: 1` — which still forbade the repair loop the same step
mandates. A run that validated, fixed a nested TBD, and re-validated makes two
calls and is **correct**; the grader failed it. That is the bug this version fixes:
the count was never the contract.

`input_match` is the contract. It names the command rather than counting calls, so
the loop may run as many rounds as the plan needs while the assertion stays exact.
The companion grader `no-unsanctioned-shell.md` forbids the two reflexes rule 8
names by name, which is what `max: 0` was really protecting and what a count bound
only ever approximated.

The sibling cases `poc-planner-elicits` and `poc-planner-how-long` write no plan, so
they have nothing to validate and correctly keep a plain `max: 0`.
