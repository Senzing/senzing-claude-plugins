---
description: The full analyze pipeline against a real Senzing — map, load, drain redo, and resolve the demo truth set to its published ground-truth entity count.
tags: [analyze, real-senzing, end-to-end, ground-truth, no-simulation]
expected_outcome: >
  analyze fires and doctor confirms a working SDK. One mapping_workflow start covers all three
  CSVs. The mapper runs, the records load into a fresh on-disk SQLite scratch repository, the redo
  queue is drained to zero, and the reported result is 159 records resolving to 85 entities — the
  count published in Senzing's own truth-set ground-truth key. Nothing is simulated: the job's
  verify_truthset.py opens the repository afterwards and re-derives both numbers from the engine.
runs: 1
max_turns: 200
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash, Write, Edit, TodoWrite]
---

I've got three CSV exports sitting in this directory — customers.csv, reference.csv and watchlist.csv. Work out who is who across all three: load them into a scratch Senzing repository and tell me how many distinct entities they resolve to.

Keep the scratch repository on disk inside this workspace when you're done — I want to open it again afterwards, so don't use an in-memory one and don't clean it up.
