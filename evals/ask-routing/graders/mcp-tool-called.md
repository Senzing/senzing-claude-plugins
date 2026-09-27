---
type: tool_used
tool: mcp__plugin_senzing_senzing__search_docs
min: 1
---

# Grader: the answer was grounded in a real MCP call

Was `regex` over `target: trace` for the string `mcp__plugin_senzing_senzing__`, which CANNOT
FAIL: every skill declares `allowed-tools: ... mcp__plugin_senzing_senzing__*` in its frontmatter,
and the Skill tool echoes that allow-list into the trace. It passed 2/2 in a CI run where the
agent had no Senzing MCP tools registered at all and its only attempt -- a `ToolSearch` for
`select:mcp__plugin_senzing_senzing__search_docs` -- returned zero matches. The grader was
matching the query string of a FAILED lookup and the skill's own frontmatter.

"What attributes does Senzing support for a person record?" is an entity-spec question, and
`ask`'s own routing table sends it to `search_docs`. Assert that call.
