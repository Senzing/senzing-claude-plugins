---
type: tool_used
tool: WebFetch
input_match: 'raw\.githubusercontent\.com|github\.com/[Ss]enzing/recipes|senzing\.com/cookbook'
min: 0
max: 0
---

# Grader: no recipe content was fetched over the network with WebFetch

The `recipes` skill reads a cookbook bundled inside the plugin. The Claude directory held the
listing on "contains a download-and-run command" because the skill used to fetch recipe text and
then run it, so the invariant worth guarding is **nothing is downloaded** — not merely that a
`Read` happened. `WebFetch` stays in this case's `allowed_tools` precisely so that a run that
reaches for it is caught here instead of being made impossible.
