---
name: build
description: >
  Generate correct, compilable Senzing SDK code for the user's own application and write it into
  their project. Use when the user wants to add Senzing to an app or service — e.g. "add Senzing
  search to my Python service", "scaffold a Senzing loader", "write the add-record code", "wire up
  the V4 SDK in Java". Emits code from real indexed snippets with source-URL provenance, and can
  optionally run it against the user's own Senzing to prove it works; if they do, it calls doctor
  first. Not for
  answering a question about the SDK when no code is wanted (use ask), dashboards over
  already-loaded data (use report), or resolving data files (use analyze).
argument-hint: "[language] [workflow]"
allowed-tools: Bash, Read, Write, Skill, mcp__plugin_senzing_senzing__*
---

# Build a Senzing SDK integration

Grounded by the **Senzing MCP server**. Do not write Senzing SDK code from training data — it is
commonly wrong (attribute names, method signatures, initialization patterns). The anti-patterns
themselves live in the MCP: before committing to a design, run
`search_docs(query=<what you are about to write>, category='anti_patterns')`.

**Pre-flight the deliverable — run `doctor` up front whenever the user wants the code written
into a project or run, not only when it is time to run.** Generating the code and returning it —
inline, or as a downloadable / self-contained HTML5 artifact with its provenance comment intact —
works in any environment. The two later steps have **different** gates, and `doctor`'s verdict
answers both:
- **Step 3 (write)** is gated on the **file tools**: do they write the user's project? In Claude
  Code they do. In Cowork the file tools also write the user's folder — only the **shell** is
  sandboxed there. In Claude Desktop / Chat there is no project on disk to write to: hand the
  code back as a download and say where it goes.
- **Step 4 (run)** is gated on the **shell**: is it the user's machine with a working Senzing
  (`doctor` checks 4–9 green)? A sandboxed or cloud shell proves nothing about their Senzing —
  say so and offer `/senzing:build` in **Claude Code** on that host.
Never claim to have edited files you could not write, and never claim a run you did not perform.

Always:

1. **Inputs.** `$ARGUMENTS` may name the language and/or workflow (e.g. `python search`). Determine
   the target language (Python/Java/C#/Rust/TypeScript) and the workflow. Use the workflow names
   `generate_scaffold` itself enumerates in its description (it accepts aliases) — do not carry
   over `sdk_guide` topic names, which are a different vocabulary for setup and guidance, and do
   not keep a copy of either list here. If either input is missing or ambiguous, **ask — do not
   default to Python**. If it's being wired into an existing project, ask for or read the
   relevant file(s) so the code matches. If the user wants the code written into their project
   or run, invoke `doctor` now (see the pre-flight above) and keep its verdict for steps 3–4.
2. Call `generate_scaffold` for the code, then `find_examples` and `get_sdk_reference` to confirm
   signatures and fill gaps. Use `sdk_guide` for setup/config steps.
   **Confirm argument types for the target language before writing any method call:**
   `get_sdk_reference(topic='parameters', filter=<method>, language=<target>)`. The same method
   has a different name AND different argument types in each binding; the response carries the
   cross-binding divergence warnings, so read them there rather than from memory. **Never carry a
   call from one binding to another.**
3. **Write the code into the user's project with its source-URL provenance comment preserved** —
   do not strip attribution. Match the surrounding code's style. Only when the file tools target
   the user's project (pre-flight); otherwise hand it back as a download.
4. If `doctor` showed a working Senzing behind a shell on the user's machine, offer to **Bash-run**
   the generated code against it so "it compiles" becomes "it works." Show the code first. Never
   simulate results. Read-only scripts (search/why/how/export) may run after showing the code.
   Any script that writes — add/replace/delete records, config changes, purge — requires an
   explicit 'proceed?' confirmation that names the target database first.

## What DONE means

Say which of the two you delivered:
- **Written** (no run requested, or no runnable host): the code is in the user's project (or
  handed back) with its provenance comment intact **and** it compiles / type-checks with the
  project's own toolchain (e.g. `python -m py_compile`, `cargo check`, `dotnet build`) — name
  the command you ran. Code you did not compile is a draft, not a deliverable.
- **Proven** (run requested and `doctor` allowed it): additionally it executed against the
  user's Senzing and you reported the real output. Never report Proven when you delivered
  Written.
