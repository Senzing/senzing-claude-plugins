---
type: tool_order
before: { tool: Skill, input_match: '"skill"\s*:\s*"(?:[\w-]+:)?doctor"' }
after: { tool: Read, input_match: 'cookbook/recipes/customer-360-crm-online\.md' }
---

# Grader: doctor runs BEFORE the cook is committed to

A recipe ends in a served result, so a host that cannot deliver one must be caught before the
cook, not after (SKILL.md step 1). This asserts `doctor` precedes `Read`ing the specific bundled
recipe file, catching a run that opens the recipe first and only checks the host afterward — a
regression this grader would visibly fail (`after` would occur before `before` in the trace).

The `after` anchor was `Bash` when the recipe was downloaded; once it is bundled the open is a
`Read`, and a `Bash` anchor never fires ("after tool Bash never called", 2 of 2 runs in CI).
