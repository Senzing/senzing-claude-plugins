---
type: tool_used
tool: Bash
input_match: 'curl[\s\S]*cookbook\.md'
---

# Grader: the catalog was actually FETCHED, not recalled

This is the positive obligation the 404 outage needed: both configured catalog refs (`recipes.md`
on `main`, and a since-deleted `cookbook-import` branch) 404'd, and every run stopped at this exact
fetch. A model that instead answers from training data makes zero matching `Bash` calls, so this
grader has `min: 1` (the default) and fails on that run — proven offline against a synthetic
`{"command": "echo hi"}` call, which does not match.

`WebFetch` is the skill's documented fallback only when `curl` is unavailable/blocked, which is
not the case in this sandbox (network to `raw.githubusercontent.com` is allowlisted by `run.sh`),
so `Bash` is the deterministic path.
