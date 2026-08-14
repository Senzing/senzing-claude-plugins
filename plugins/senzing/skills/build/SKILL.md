---
name: build
description: >
  Generate correct, compilable Senzing SDK integration code and write it into the user's project.
  Use when the user wants to add Senzing to their app or service — e.g. "add Senzing search to my
  Python service", "scaffold a Senzing loader", "how do I initialize the V4 SDK", "write the
  Senzing add-record code". Emits code from real indexed snippets with source-URL provenance, and
  can run it against the user's own Senzing to prove it works.
argument-hint: "[language] [workflow]"
allowed-tools: Bash, Read, Write, Skill, mcp__plugin_senzing_senzing__*
---

# Build a Senzing SDK integration

Grounded by the **Senzing MCP server**. Do not write Senzing SDK code from training data — it is
commonly wrong (bad attribute names, wrong method signatures, dual-factory crashes).

**Pre-flight the deliverable.** Generating the code and returning it — inline, or as a
downloadable / self-contained HTML5 artifact with its provenance comment intact — works in any
environment. But **writing it into the user's local project** (step 3) and **running it against
their Senzing** (step 4) need a writable local shell — i.e. Claude Code on their machine. If
`doctor` shows no local-write / live surface (a cloud sandbox — Claude Desktop / Chat, Cowork),
don't claim to have edited their files: hand back the code as a download and tell the user to run
`/senzing:build` in **Claude Code** to drop it into the project and prove it compiles.

Always:

1. **Inputs.** `$ARGUMENTS` may name the language and/or workflow (e.g. `python search`). Determine
   the target language (Python/Java/C#/Rust/TypeScript) and the workflow (initialize,
   load/add_records, search, redo, export, error_handling, full_pipeline, …). If either is missing
   or ambiguous, **ask — do not default to Python**. If it's being wired into an existing project,
   ask for or read the relevant file(s) so the code matches.
2. Call `generate_scaffold` for the code, then `find_examples` and `get_sdk_reference` to confirm
   signatures and fill gaps. Use `sdk_guide` for setup/config steps.
   **Confirm argument types for the target language before writing any method call:**
   `get_sdk_reference(topic='parameters', filter=<method>, language=<target>)`. The same method
   has a different name AND different argument types in each binding — Python
   `find_network_by_entity_id(entity_ids: List[int], …)` vs Java `findNetwork(SzEntityIds, …)`
   vs C# `FindNetwork(ISet<long>, …)` vs Rust `find_network_by_entity_id(&[EntityId], …)` vs
   TypeScript `findNetwork(number[], …)`. **Never carry a call from one binding to another.**
3. **Write the code into the user's project with its source-URL provenance comment preserved** —
   do not strip attribution. Match the surrounding code's style.
4. If the user has a working Senzing (check via `doctor`), offer to **Bash-run** the
   generated code against it so "it compiles" becomes "it works." Show the code first. Never
   simulate results. Read-only scripts (search/why/how/export) may run after showing the code.
   Any script that writes — add/replace/delete records, config changes, purge — requires an
   explicit 'proceed?' confirmation that names the target database first.
