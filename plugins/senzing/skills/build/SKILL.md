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

> **Two gates, and neither is optional.**
> 1. **`generate_scaffold` produces the code — you do not.** You can write plausible Senzing
>    Python from memory, and it will be wrong in ways that compile: V3 `G2Engine` names, methods
>    that no longer exist, argument types that differ per binding. Emitting hand-written SDK code
>    is a failure even if the user never notices. Call `generate_scaffold`, then
>    `get_sdk_reference(topic='parameters', …)` to confirm argument types, before writing a line.
> 2. **If the user named a file, the deliverable is that file.** Do not downgrade a write to an
>    inline snippet or a download on the *assumption* that the environment is sandboxed. The
>    probe below decides that, and it costs one Write plus one Read. Assuming is how a user who
>    said "put it in senzing_search.py" gets a chat message instead of a file.

**Pre-flight the deliverable — run `doctor` up front whenever the user wants the code written
into a project or run, not only when it is time to run.** Generating the code and returning it —
inline, or as a downloadable / self-contained HTML5 artifact with its provenance comment intact —
works in any environment. The two later steps have **different** gates. `doctor`'s verdict
answers the run gate; the write gate needs one probe of its own:
- **Step 3 (write)** is gated on the **file tools**: do they write the user's project? In Claude
  Code they do. In Cowork the file tools also write the user's folder — only the **shell** is
  sandboxed there. In Claude Desktop / Chat there is no project on disk to write to: hand the
  code back as a download and say where it goes. `doctor` check 3 reports Cowork and Claude
  Desktop / Chat under one "cloud sandbox" verdict, so it cannot tell these apart — when it says
  cloud sandbox, **probe**: `Write` a small file into the project and `Read` it back. Landed →
  the file tools write the project; not landed → download. **Run the probe — do not infer the
  answer from doctor's verdict.** "Cloud sandbox" is precisely the verdict that does NOT
  distinguish the two, so treating it as "cannot write" is reading a result the check did not
  produce. A missing Senzing install says nothing about whether the file tools work: the write
  gate and the run gate are independent, and code can be written into a project that has no
  Senzing on it at all.
- **Step 4 (run)** is gated on the **shell**: is it the user's machine with a working Senzing —
  `doctor` 4, 5, 6 and 6b ✅ (7–9 may legitimately be ➖/⚠️ on a healthy host: 7 is ➖ with no
  `SENZING_ENGINE_CONFIGURATION_JSON`, 8 cascades to ➖, 9 is ⚠️ on the built-in eval license)?
  A run against the user's **own repository** additionally needs 7–8 ✅; a scratch or in-process
  run does not. A sandboxed or cloud shell proves nothing about their Senzing — say so and offer
  `/senzing:build` in **Claude Code** on that host.
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
   do not strip attribution. Match the surrounding code's style. **If the user named a path or
   filename, that exact file is the deliverable** — write it there, then `Read` it back to
   confirm it landed and say so. Hand the code back as a download ONLY when the probe above
   actually failed, and then say plainly that the file tools could not reach their project.
   A response that ends with code in the chat when the user asked for a file is not done.
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
  the command you ran. With no shell (Claude Desktop / Chat), say "Written — not compiled here"
  and give the compile command for the user to run; never call that Proven.
- **Proven** (run requested and `doctor` allowed it): additionally it executed against the
  user's Senzing and you reported the real output. Never report Proven when you delivered
  Written.
