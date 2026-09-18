---
type: tool_used
tool: mcp__plugin_senzing_senzing__search_docs
input_match: '[Pp]roof of [Cc]oncept|[Pp]o[Cc]|[Ss]electing the right data|[Mm]apping [Dd]ata|[Dd]eployment [Pp]latform'
min: 3
---

## Why this regex is broader than it looks

`min` counts only calls whose input MATCHES. Step 1 of the skill prescribes exactly three
queries, and the previous pattern matched just two of them -- "Selecting the right data" contains
neither "proof of concept" nor "poc". A model following the skill VERBATIM produced 2 matching
calls against `min: 3` and failed, so this grader could not be satisfied by correct behaviour.
Every prescribed query is now covered.
