---
type: tool_used
tool: mcp__plugin_senzing_senzing__search_docs
input_match: '[Pp]roof of [Cc]oncept|[Pp]o[Cc]|[Ss]electing the right data|[Mm]apping [Dd]ata'
min: 1
---

# Grader: the PoC guidance was actually retrieved

Was `regex` over `target: trace` for the prose "Path to a Successful Proof of Concept". That
string is hard-coded in the SKILL ITSELF as the query to run
(`plugins/senzing/skills/poc-planner/SKILL.md`, step 1), and the skill body is injected into the
trace whenever the skill fires -- so the grader matched the INSTRUCTION and passed 2/2 in a CI run
with zero MCP tool calls. It measured that the skill exists, not that anything was retrieved.

`tool_used` is the honest form. The `input_match` covers all three queries step 1 prescribes --
the PoC article, "Selecting the right data", and the mapping/deployment query -- so a model that
follows the skill exactly is not failed on phrasing.
