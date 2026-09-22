---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?install"'
---

Why this exists: `install-steps-from-mcp` beside it asserts `sdk_guide(topic="install")`, which
`doctor`'s own Step 0 calls unconditionally to learn the platform's install location — so it
passes in a run where the `install` skill was never invoked at all. That is the same blind spot
`demo-no-simulation` closed with its own `install-invoked.md` sibling; this case had none.

It is not a stylistic preference: `recipes/SKILL.md` ("Senzing can't deploy") says to hand off to
the **`install`** skill without asking first and explicitly "do not route around it via
`sdk_guide(topic="install")` directly". The grader beside this one therefore measures the route
the skill forbids taking alone, and this one measures the route it requires.

Provably able to PASS a correct run: both `recipes-named` sessions in the last full run (f2)
invoked it — trace-17/53 `{"skill": "senzing:install", "args": "macos_arm — no Senzing SDK
detected, …"}` and trace-21/57 `{"skill": "senzing:install"}`. Provably able to FAIL: the two
`recipes-catalog` sessions in that same run (trace-18/54, trace-36/72) invoked only
`{"skill": "senzing:recipes"}`, so this pattern finds nothing in them.
