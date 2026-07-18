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
commonly wrong (bad attribute names, wrong method signatures, dual-factory crashes). Always:

1. **Inputs.** `$ARGUMENTS` may name the language and/or workflow (e.g. `python search`). Determine
   the target language (Python/Java/C#/Rust/TypeScript) and the workflow (initialize,
   load/add_records, search, redo, export, error_handling, full_pipeline, …). If either is missing
   or ambiguous, **ask — do not default to Python**. If it's being wired into an existing project,
   ask for or read the relevant file(s) so the code matches.
2. Call `generate_scaffold` for the code, then `find_examples` and `get_sdk_reference` to confirm
   signatures and fill gaps. Use `sdk_guide` for setup/config steps.
3. **Write the code into the user's project with its source-URL provenance comment preserved** —
   do not strip attribution. Match the surrounding code's style.
4. If the user has a working Senzing (check via `doctor`), offer to **Bash-run** the
   generated code against it so "it compiles" becomes "it works." Show the code first. Never
   simulate results. Read-only scripts (search/why/how/export) may run after showing the code.
   Any script that writes — add/replace/delete records, config changes, purge — requires an
   explicit 'proceed?' confirmation that names the target database first.
