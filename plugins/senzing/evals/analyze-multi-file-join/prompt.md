---
description: Two related files (customers + orders joined on customer_id) are mapped by ONE mapping_workflow whose start carries BOTH file_paths — never one workflow per file — and the cross-file join is recognized.
tags: [analyze, multi-file, relationships, grounding, no-simulation]
expected_outcome: >
  analyze fires; doctor runs first; exactly ONE mapping_workflow `start` is issued and its
  `file_paths` array holds BOTH customers.csv and orders.csv (a single-file `file_paths` anywhere
  is the per-file regression this case exists to catch). The step-2 entity plan sent back to the
  tool names customer_id as the join key between the two schemas (orders as a child/relationship
  of customers), so the run treats the files as related rather than mapping each in isolation.
  If field-mapper sub-agents are fanned out at all, no two share a workspace_dir. The sandbox has
  no Senzing, so the run ends at the mapping-only exit — saying so and pivoting to install / the
  validated JSONL — with no invented entities, scores or merges. (Not plan-level: the mapping
  steps run for real against the hosted MCP; only the load/resolve steps are unavailable here.)
max_turns: 80
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash, Write]
---

customers.csv is my customer master and orders.csv is their order history (both files are in this directory). Resolve and dedupe my customers across both files — who is who?
