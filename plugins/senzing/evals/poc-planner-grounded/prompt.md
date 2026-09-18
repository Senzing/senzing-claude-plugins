---
description: A POC planning request with stated constraints routes to poc-planner, retrieves the PoC guidance before writing, assembles sizing/platform/load material from the MCP, and writes a nine-section handoff plan whose every number is the user's, cited, or a TBD literal — with no schedule and nothing run.
tags: [poc-planner, routing, grounding, provenance, no-fabrication, handoff]
expected_outcome: >
  poc-planner fires; no action skill and no doctor fires and the Skill tool is never used for a
  hand-off; get_capabilities and at least three PoC search_docs calls precede the Write;
  reporting_guide is called for quality AND evaluation(python), sdk_guide for the platform tree
  and for load with a record_count, search_docs for sizing; senzing-poc-plan.md exists with
  exactly nine template headings, the §2 yaml keys carrying the user's PostgreSQL/Linux/Python/
  volumes (platform_id from sdk_guide's tree is the one tool-derived §2 value), SC-n items with
  only the template's six keys whose targets are all TBD literals (the user agreed none), a
  counted provenance line, a synthetic-truth-set warning, and source URLs; the license material
  the tools return is quoted per tool and the 755k-vs-250K record-limit constraint is set against
  the vertical-slice rule rather than resolved; it contains no week/sprint labels, no duration
  ranges, no metric thresholds, no number or "typically" after a TBD, no invented role titles,
  no "you will need N cores"; mapping_workflow never starts; no shell runs; no license is requested.
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Skill, Write, Bash]
---

Help me plan a Senzing proof of concept. We have a CRM export (about 400k customer records), a billing system extract (about 350k), and a small fraud watchlist (about 5k). Two engineers for six weeks, on Linux VMs (Ubuntu) with PostgreSQL, on-prem, using Python. Our VP wants to see that duplicate customers across CRM and billing get found; we have not agreed any accuracy targets, hardware or performance numbers yet. Write the plan to senzing-poc-plan.md in this directory. Assume our answer to anything I haven't stated is "not decided yet" — the owner is our data platform lead.
