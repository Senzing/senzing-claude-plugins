---
type: tool_used
tool: Bash
min: 1
max: 1
---

# Grader: exactly one shell call, and it is the validator

This case writes a plan, so step 8 runs `validate_plan.py` on it — one `Bash`
call, by design. Every other shell use is still a defect: probing the host,
`ls`-ing the plan file, `grep`-ing the model's own output. Rule 8 of the skill
names those three by name because they are the ones that keep happening.

**This was `max: 0` and had to change, because the skill changed under it.**
The validator landed (haiku produced 4/4 structurally valid plans with it,
against sonnet's 2/10 without), and a grader asserting zero shell calls then
contradicted the skill it was grading. `min: 1` is the half that matters: it
asserts the validator actually *ran*, which `max: 0` never could. A plan written
without being validated is the failure this case exists to catch, and it would
previously have scored green.

The sibling cases `poc-planner-elicits` and `poc-planner-how-long` keep `max: 0`:
neither writes a plan, so neither has anything to validate, and a shell call in
those runs is the old defect with no new exception.
