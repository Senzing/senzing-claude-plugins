---
type: tool_used
tool: mcp__plugin_senzing_senzing__get_sample_data
min: 1
---

# Grader: the demo's data came from Senzing, not from the model

`demo` demonstrates entity resolution **on Senzing's own sample data**. The data
is therefore not incidental to the demo — it is half of the claim being made.
`demo/SKILL.md:23` says the dataset is chosen from `get_sample_data(dataset='list')`
"never from memory; the list changes with the server", and `:99,105,118` have the
run pull the records through it.

Before this, neither demo case asserted a single MCP tool. A run that invented
plausible-looking customer rows, resolved them by inspection and presented the
before/after would have passed every deterministic grader here — which is
precisely the failure the MUST tier caught on `routing-negative-dedupe`, where
opus produced a careful, clearly-labeled result without ever starting an engine.

A demo you performed yourself is not a demo of Senzing, and a demo of data you
invented is not a demo of Senzing's data.

`min: 1`, no `input_match`: which dataset a run picks is its own business and
pinning one would be a route assertion. That the rows came from the server
rather than from recall is the outcome.
