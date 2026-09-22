---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?install"'
---

Why this exists: `install-steps-from-mcp` beside it PASSED in the run where `install` was never
invoked at all. `doctor`'s own Step 0 calls `sdk_guide(topic="install")` to learn the platform's
install location, so that grader measures doctor thoroughness, not the install pivot. This one
asserts the pivot itself — demo hands off to the **`install`** skill in the same turn as the red
verdict. Necessary but not sufficient: a run can invoke `install` and still close on an
install-vs-preview menu, which is why `criteria.md` also carries a literal clause about the final
message.
