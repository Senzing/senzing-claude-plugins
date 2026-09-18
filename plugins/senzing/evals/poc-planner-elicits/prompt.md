---
description: With no inputs, poc-planner retrieves the PoC guidance and ENDS at the questions — data, infrastructure, people, the buy decision — writing nothing, running nothing, and proposing no numbers or schedule; ask and demo do not fire.
tags: [poc-planner, ask, demo, routing, elicitation]
expected_outcome: >
  poc-planner fires and neither ask nor demo nor doctor does; get_capabilities and search_docs
  (PoC guidance) run; the reply asks about data, about hardware/platform/performance, about who
  runs it and the SDK language, and about what must be true to buy — grounded in a visible tool
  result — and stops. No file is written, no shell runs, and the reply contains no percentage,
  no "N–M weeks" and no week/sprint label: with nothing from the user, any such number is the
  model answering.
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Skill, Write, Bash]
---

We're evaluating Senzing this quarter. How should we structure the proof of concept?
