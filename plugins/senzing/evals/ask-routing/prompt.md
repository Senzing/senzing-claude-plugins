---
description: A factual Senzing question routes to ask, is answered from an MCP tool, and writes/runs nothing.
tags: [ask, routing, grounding]
expected_outcome: >
  ask fires (no action skill does); at least one Senzing MCP tool is called; no file is written and
  no shell command runs; the answer cites the source URLs the tool returned.
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Skill]
---

What attributes does Senzing support for a person record?
