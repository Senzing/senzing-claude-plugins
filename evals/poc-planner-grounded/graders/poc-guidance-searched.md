---
type: tool_used
tool: mcp__plugin_senzing_senzing__search_docs
input_match: '[Pp]roof of [Cc]oncept|[Pp]o[Cc]|[Ss]electing the right data|[Mm]apping [Dd]ata|[Dd]eployment [Pp]latform'
min: 1
---

## Why this regex is broader than it looks

`min` counts only calls whose input MATCHES. Step 1 of the skill prescribes exactly three
queries, and the previous pattern matched just two of them -- "Selecting the right data" contains
neither "proof of concept" nor "poc". A model following the skill VERBATIM produced 2 matching
calls against `min: 3` and failed, so this grader could not be satisfied by correct behavior.
Every prescribed query is now covered.

## `min: 3` -> `min: 1` (2026-09-25)

The COUNT of search calls is not an outcome. This grader's own prose above records that it already
false-failed a verbatim-compliant run which made 2 matching calls — an assertion that fails correct
behavior is measuring the route, not the result.

What actually matters is carried by siblings that assert the result directly: `retrieved-before-written`
(the plan was retrieved BEFORE it was written — order), `sizing-material-retrieved` (the specific
material is present — coverage), and `provenance-kept` (it is cited). Those hold however many calls
it took to get there.

`min: 1` keeps the real floor — a plan written with NO retrieval is recalled, not grounded, and
still fails here.
