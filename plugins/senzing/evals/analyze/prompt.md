---
description: Own-data entity resolution routes to analyze, grounds the mapping in mapping_workflow, and never fabricates a result.
tags: [analyze, routing, grounding, no-simulation]
expected_outcome: >
  analyze fires; doctor runs first; mapping_workflow is started on BOTH files and the mapper it
  returns is executed via Bash. The sandbox has no Senzing, so the run ends by saying so and
  pivoting to install / the zero-install prep tier — with no invented entities, scores or merges.
max_turns: 80
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash, Write]
---

Resolve and dedupe my customer records in crm.csv and billing.csv (both files are in this directory) — who is who across them?
