---
description: install surfaces the license agreement before anything runs and never hand-writes install commands.
tags: [install, eula, grounding]
expected_outcome: >
  install fires; the host is established with uname; the steps come from sdk_guide(topic=install);
  the EULA / license agreement is surfaced and explicit agreement requested BEFORE any install
  command runs — so in this single turn zero install commands execute; every install command shown
  is verbatim from a tool result.
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Install Senzing on this machine so I can try it. I'll be using Python.
