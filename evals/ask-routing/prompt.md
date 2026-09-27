---
description: A factual Senzing question routes to ask, is answered from an MCP tool, and writes/runs nothing.
tags: [ask, routing, grounding]
expected_outcome: >
  ask fires and no action skill does; the answer is grounded in search_docs — the tool ask's
  routing table assigns to factual questions and the one that owns the Entity Spec attribute
  list — called before any answer text; the attribute names in the answer are the ones a tool
  result returned, not recalled ones, and the answer cites the source URLs that result carried;
  no file is written and no shell command runs.
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Skill]
---

What attributes does Senzing support for a person record?
