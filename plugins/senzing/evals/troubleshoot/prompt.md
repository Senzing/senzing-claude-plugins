---
description: An error code routes to troubleshoot and the explanation comes from explain_error_code, not memory.
tags: [troubleshoot, routing, grounding]
expected_outcome: >
  troubleshoot fires; explain_error_code is called for 0033; the answer restates ONLY what the tool
  returned (cause + resolution steps) and writes no files.
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Skill, Bash]
---

What does Senzing error 0033E mean and how do I fix it?
