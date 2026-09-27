---
description: With no Senzing on the host, demo detects that via doctor (not by being told) and pivots to install instead of faking a demo.
tags: [demo, no-simulation, grounding]
expected_outcome: >
  demo fires; doctor probes the host with Bash and finds no SDK; sdk_guide(topic=install) supplies
  the install path; no match score / merge / entity count is ever presented as a result; every
  install command shown came from a tool result.
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash, Write]
---

Show me Senzing entity resolution working.
