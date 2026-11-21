---
type: tool_order
before: { tool: Skill, input_match: '"skill"\s*:\s*"(?:[\w-]+:)?doctor"' }
after: { tool: Bash, input_match: 'customer-360-crm-online\.md' }
---

# Grader: doctor runs BEFORE the cook is committed to

A recipe ends in a served result, so a host that cannot deliver one must be caught before the
cook, not after (SKILL.md step 1). This asserts `doctor` precedes fetching the specific recipe
file, catching a run that fetches/reads the recipe first and only checks the host afterward — a
regression this grader would visibly fail (`after` would occur before `before` in the trace).
