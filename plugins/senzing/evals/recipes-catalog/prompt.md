---
description: Browsing the cookbook routes to recipes and the catalog is actually FETCHED live, not answered from memory — the case that would have caught the catalog-404 outage.
tags: [recipes, grounding, no-simulation]
expected_outcome: >
  recipes fires; the live cookbook.md catalog is fetched via Bash curl — not recalled from
  training data; the reply lists the real catalog entries (the PPP-loan ingestion recipe, both
  Customer 360 recipes, and the Healthcare Exclusion Screening recipe) and writes no files.
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Skill, Bash, WebFetch, Write]
---

What recipes are in the Senzing Cookbook?
