---
description: Negative routing — "dedupe my customer list" is analyze on the user's file, NOT demo on sample data.
tags: [analyze, demo, routing]
expected_outcome: >
  analyze fires and demo does not; mapping_workflow is started on customers.csv; get_sample_data
  is never called (that would be a demo).
max_turns: 80
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash, Write]
---

Dedupe my customer list in customers.csv — it's in this directory.
