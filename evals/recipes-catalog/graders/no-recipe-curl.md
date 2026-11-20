---
type: tool_used
tool: Bash
input_match: '(curl|wget)[^\n]*([Ss]enzing/recipes|cookbook|recipes/)'
min: 0
max: 0
---

# Grader: no recipe content was downloaded with curl/wget

The sibling of `no-recipe-webfetch` for the shell path. The pattern requires the download tool AND
a recipe/cookbook target on the same command, so it does not match `doctor`'s reachability probe
(a HEAD request to a bare host root) or the `cp` of bundled ingredient files into the workspace.
