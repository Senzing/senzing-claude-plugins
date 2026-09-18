---
type: tool_used
tool: mcp__plugin_senzing_senzing__get_capabilities
min: 1
---

# Grader: doctor grounded itself in the MCP

Was `regex` over `target: trace` for the literal tool name. That target is the raw trace, which
carries skill bodies, allow-lists and the model's own prose, so the check flipped between
identical runs -- it was reading text, not tool use. `poc-planner-grounded/graders/grounding-checked.md`
already asserts exactly this with `tool_used`; use the same primitive here rather than two
different answers to one question.
