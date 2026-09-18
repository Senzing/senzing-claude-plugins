---
name: ask
description: >
  Answer a Senzing question — grounded in the Senzing MCP, never from training data — without
  writing code or running anything. Use for any factual or commercial question: supported
  attributes and the entity spec, SDK method signatures and flags, configuration, architecture,
  deployment and database options, pricing and ROI, licensing and how to get an evaluation
  license — e.g. "what attributes does Senzing support?", "how do I initialize the V4 SDK?",
  "what does Senzing cost?", "what's the ROI?", "how should I deploy this on AWS?", "which
  database should I use?". Needs no Senzing installed and no shell, so this is the one skill that
  works on any host — including information-only environments where the others cannot run. Not for
  generating code into a project (use build), running anything (analyze, demo, report), a pasted
  error code (troubleshoot), or checking this machine (doctor).
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

## Procedure

1. **Route the question.** Call `get_capabilities` if you are unsure which tool owns it. The MCP
   also publishes ready-made prompt workflows — prefer one when it fits the question
   (ROI, why-Senzing, deployment options, choosing a database, requesting an eval license,
   V3→V4 migration).
2. **Pick the tool that owns the fact.** Do not reproduce Senzing knowledge in this file — it
   goes stale silently. The MCP's copy does not.

   | Question is about | Tool |
   |---|---|
   | Anything factual — behavior, config, pricing/DSR, architecture, deployment, database tuning, best practice | `search_docs` |
   | Method arguments per binding, flags, response shapes, V3→V4 migration | `get_sdk_reference` |
   | What an error code means | `explain_error_code` |
   | Working code to look at (not write into the project) | `find_examples` |
   | Install/configure steps for a platform | `sdk_guide` |
   | Requesting a free evaluation license | `submit_feedback` with `category='license_request'` |

   ⚠ The same method has **different names and argument types in each language binding**. When the
   question names a method, pass `language` and read the divergence warnings — never translate a
   call you saw in another binding.
3. **Answer, then offer the next step.** Point at the skill that would act on it —
   `build` to write the code, `analyze` to resolve their data, `demo` to see it work,
   `install` to set Senzing up.

## Scope

Answer only. This skill writes no files and runs nothing. If the user actually wants something
done, name the skill that does it and hand off rather than half-doing it here.
