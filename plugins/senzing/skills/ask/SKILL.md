---
name: ask
description: >
  Answer a Senzing question — grounded in the Senzing MCP, never from training data — without
  writing code or running anything. Use for any factual or commercial question: supported
  attributes and the entity spec, SDK method signatures and flags, configuration, architecture,
  deployment and database options, pricing and ROI, licensing and how to get an evaluation
  license — e.g. "what attributes does Senzing support?", "how do I initialize the V4 SDK?",
  "what does Senzing cost?", "what's the ROI?", "how should I deploy this on AWS?", "which
  database should I use?". Needs no Senzing installed and no shell, so it works on any host —
  including information-only environments — and is the fallback when no other skill fits. Not for
  generating code into a project (use build), running anything (analyze, demo, report), a pasted
  error code (troubleshoot), checking this machine (doctor), or planning, scoping or sizing a proof
  of concept / pilot / evaluation (use poc-planner).
argument-hint: "[question]"
allowed-tools: Read, mcp__plugin_senzing_senzing__*
---

# Ask Senzing a question

The single entry point for questions that want an **answer**, not an action.

This skill exists because model knowledge of Senzing is outdated and confidently wrong — wrong
attribute names, wrong method signatures, V3 patterns presented as V4, invented config options.
Every other skill in this plugin *does* something; without this one, a plain question either
matched nothing or matched a skill that would start writing files.

## The one rule

**Never answer from training data. Always ground the answer in an MCP tool call first** — even
when you are confident. Then answer in your own words and **cite the source URLs the tools
return**, so the user can verify.

If the tools genuinely do not cover it, say so plainly rather than filling the gap from memory.
"I could not find that in the Senzing documentation" is a correct answer; an invented one is not.

**Ground the arithmetic, not just the retrieval.** Never extrapolate a retrieved figure into a new
one — "the sizing FAQ says N cores for 100k, so for 1M you'd need roughly 10×" is fabrication with
a citation. Quote the figure with its source and stop; a number that is in no tool result and did
not come from the user is not yours to produce. For a plan-, scope- or POC-shaped question that
lands here anyway: answer from the retrieved PoC guidance only; any target, duration, size or
threshold not in a tool result or from the user is `TBD — decided by <owner>`; then point at
`/senzing:poc-planner`.

## Procedure

1. **Route the question.** Call `get_capabilities` if you are unsure which tool owns it. The MCP
   also publishes prompt workflows (ROI, why-Senzing, deployment options, choosing a database,
   requesting an eval license, V3→V4 migration) — but a skill **cannot** invoke them; they are
   user slash commands. When a question matches one, run the tool calls that prompt would have
   run yourself: `search_docs` with the question's own terms (for V3→V4,
   `get_sdk_reference(topic="migration")`), then answer from the results. You may mention the
   prompt as something the user can run directly.
2. **Pick the tool that owns the fact.** Do not reproduce Senzing knowledge in this file — it
   goes stale silently. The MCP's copy does not.

   | Question is about | Tool |
   |---|---|
   | Anything factual — behavior, config, pricing/DSR, architecture, deployment, database tuning, best practice | `search_docs` |
   | Method arguments per binding, flags, response shapes, V3→V4 migration | `get_sdk_reference` |
   | What an error code means | `explain_error_code` |
   | Working code to look at (not write into the project) | `find_examples` |
   | Install/configure steps for a platform | `sdk_guide` |
   | Requesting a free evaluation license | `submit_feedback` with `category='license_request'` — see below |

   ⚠ **The license request is the one call in this skill with a side effect** — it emails a license.
   Its description names the fields it needs (currently the requester's first name, a work email
   address, and how they heard of Senzing; last name optional) and the current terms — read both
   from the tool, not from here. Collect the fields, show the user exactly what will be sent,
   and call only after they confirm.

   ⚠ The same method has **different names and argument types in each language binding**. When the
   question names a method, pass `language` and read the divergence warnings — never translate a
   call you saw in another binding.
3. **Answer, then offer the next step.** Point at the skill that would act on it —
   `build` to write the code, `analyze` to resolve their data, `demo` to see it work,
   `install` to set Senzing up, `poc-planner` to plan an evaluation.

## Scope

Answer only. This skill writes no files and runs no code; its one side-effecting tool call is the
confirmed license request above. If the user actually wants something done, name the skill that
does it and hand off rather than half-doing it here.
