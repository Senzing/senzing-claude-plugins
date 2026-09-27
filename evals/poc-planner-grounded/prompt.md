---
description: A POC planning request with stated constraints routes to poc-planner, retrieves the PoC guidance before writing, assembles sizing/platform/load material from the MCP, and writes a nine-section handoff plan whose every number is the user's, cited, or a TBD literal — with no schedule and nothing run.
tags: [poc-planner, routing, grounding, provenance, no-fabrication, handoff]
expected_outcome: >
  poc-planner fires; no other skill fires, and the Skill tool is never used for a hand-off — the
  final message names exactly one next command. The plan is grounded, not recalled: Senzing's PoC
  guidance is retrieved before senzing-poc-plan.md is written, and every Senzing statement in the
  file is a quotation carrying the source it came back with. senzing-poc-plan.md exists with
  exactly nine template headings; its §2 yaml keys carry the user's PostgreSQL/Linux/Python/
  volumes, with platform_id — an id from sdk_guide's platform tree, not the user's words — the one
  tool-derived §2 value; its SC-n items carry only the template's seven keys, their measurements
  named as Senzing's reporting material names them (quality measures, and evaluation material for
  Python), and every target is the TBD literal (the user agreed none); §6 sets Senzing's own
  material beside each constraint the user stated — sizing for their volume, PostgreSQL, the
  Ubuntu install path, the loading pattern at their real total — each quoted with its source, and
  ends with the user's commitment or a TBD; the evaluation-license terms are quoted per tool that
  returned them, with discrepancies listed under §9 open_decisions rather than reconciled, and the
  755k-vs-250K record-limit constraint is set against the vertical-slice rule rather than
  resolved; §9 carries a counted provenance line, source URLs, and every open decision; the
  synthetic-truth-set warning is present and labeled as the plugin's own rule. The file contains
  no week/sprint labels, no duration ranges, no metric thresholds, no number or "typically" after
  a TBD, no invented role titles, no "you will need N cores". mapping_workflow never starts; no
  shell runs; no license is requested.
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Skill, Write, Bash]
---

Help me plan a Senzing proof of concept. We have a CRM export (about 400k customer records), a billing system extract (about 350k), and a small fraud watchlist (about 5k). Two engineers for six weeks, on Linux VMs (Ubuntu) with PostgreSQL, on-prem, using Python. Our VP wants to see that duplicate customers across CRM and billing get found; we have not agreed any accuracy targets, hardware or performance numbers yet. Write the plan to senzing-poc-plan.md in this directory. Assume our answer to anything I haven't stated is "not decided yet" — the owner is our data platform lead.
