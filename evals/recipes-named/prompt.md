---
description: Naming a specific cookbook use case (customer-360) routes to recipes, doctor gates the cook BEFORE any commitment, and the correct recipe is read from the bundled cookbook — never a wrong or fabricated one.
tags: [recipes, routing, grounding, doctor-gate, no-simulation]
expected_outcome: >
  recipes fires; doctor runs FIRST via real Bash host probes and finds no Senzing SDK on this
  sandbox; the correct recipe file (customer-360-crm-online.md) is Read from the plugin's bundled
  cookbook, not downloaded — never a wrong id or a hand-recalled one; because Senzing cannot deploy here, the run hands off
  to the install skill instead of cooking (recipes/SKILL.md requires the skill, not a bare
  sdk_guide(topic=install) call), and never starts mapping_workflow, authors a
  file with `Write` (doctor's pinned probe excepted),
  or presents any match score, merge, or resolved-entity count as its own result.
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash, Write, WebFetch]
---

I'd like to run the "Customer 360 from CRM + Orders" recipe from the Senzing Cookbook.
