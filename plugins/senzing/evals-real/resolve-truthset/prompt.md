---
description: The full analyze pipeline against a real Senzing — map, load, drain redo, and resolve the demo truth set to its published ground-truth entity count.
tags: [analyze, real-senzing, end-to-end, ground-truth, no-simulation]
expected_outcome: >
  analyze fires and doctor confirms a working SDK. One mapping_workflow start covers all three
  CSVs. The mapper runs, every record loads into a fresh on-disk SQLite scratch repository, the
  redo queue is drained to zero, and the reply reports the record count loaded and the entity
  count they resolved to — both taken from the engine's own output. No target entity count is
  expected here: how many entities the engine produces is the ENGINE's contract, not the
  plugin's. Nothing is simulated: the job's verify_truthset.py opens the repository afterwards,
  confirms the mapped features are present and queryable, and checks the reported counts against
  what the engine actually holds.
runs: 1
max_turns: 200
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash, Write, Edit, TodoWrite]
---

I've got three CSV exports sitting in this directory — customers.csv, reference.csv and watchlist.csv. Work out who is who across all three: load them into a scratch Senzing repository and tell me how many distinct entities they resolve to.

Keep the scratch repository on disk inside this workspace when you're done — I want to open it again afterwards, so don't use an in-memory one and don't clean it up.
