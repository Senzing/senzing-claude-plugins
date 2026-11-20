---
description: Browsing the cookbook routes to recipes and the catalog is actually READ from the plugin's bundled cookbook — not answered from memory, and never downloaded.
tags: [recipes, grounding, no-simulation]
expected_outcome: >
  recipes fires; the bundled cookbook/cookbook.md catalog is Read — not recalled from training
  data and not downloaded (no curl, no WebFetch: the Claude directory refuses a plugin that
  downloads what it executes); the reply lists the real catalog entries (the PPP-loan ingestion
  recipe, both Customer 360 recipes, Patient Fraud Detection, and the Healthcare Exclusion
  Screening recipe) and authors
  no file — the `Write` tool is never used except for doctor's pinned probe. `WebFetch` and
  `Bash` stay allowed so the no-download graders measure restraint rather than impossibility.
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Skill, Bash, WebFetch, Write]
---

What recipes are in the Senzing Cookbook?
