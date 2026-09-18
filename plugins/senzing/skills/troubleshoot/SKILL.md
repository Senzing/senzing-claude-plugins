---
name: troubleshoot
description: >
  Explain a specific Senzing error and how to fix it. Use automatically when the user pastes a
  Senzing error code or stack trace (e.g. "SENZ0005", "0005", "5", a traceback naming add_record),
  or asks what an error means. Looks up the authoritative cause and fix, then points at docs and
  real code examples. If the cause turns out to be environmental (SDK, database, license, config),
  hands off to doctor. Not for "is my setup OK?" with no error in hand (use doctor).
argument-hint: "[error-code-or-message]"
allowed-tools: Read, Skill, mcp__plugin_senzing_senzing__*
---

# Troubleshoot a Senzing error

Grounded by the **Senzing MCP server**. Do not explain Senzing errors from training data.

> **The gate: `explain_error_code` runs BEFORE you write a single sentence about the error.**
> You will often recognise a Senzing code and be able to produce a fluent, confident,
> plausible-sounding explanation with no tool call at all. That is the failure this skill exists
> to prevent, and it is indistinguishable from a correct answer to the user — which is what makes
> it dangerous. Codes are version-specific and the catalog is authoritative; your recollection is
> not. Never answer first and verify after: call the tool, read what it returns, then write.
> The ONLY case where you may respond without having called it is when no code is available at
> all and you are asking the user for one.

1. **Call `explain_error_code` first.** Take the code from `$ARGUMENTS` or the recent
   conversation/trace and pass it as-is — the tool normalizes the forms people actually paste
   (`SENZ0005`, `0005`, `0033E`, `5`), so do not reformat it, and do not let uncertainty about the
   format become a reason to skip the call. Only if no code is available anywhere: **ask the user
   to paste the error code or message** and stop — do not guess a code. For a runtime failure with
   no clean code, capture the exact message and go to `search_docs`.
2. Use what it returned for the cause + resolution steps. **If it has no entry for the code, say
   exactly that** — "the catalog has no entry for X" — and fall back to `search_docs` with the
   code and the message text. Never supply a plausible-sounding cause from memory; an invented
   explanation for an unknown code is worse than no answer.
3. Use `search_docs` for surrounding context (config, GDPR, throughput, etc.) and `find_examples`
   for a correct code pattern if the fix involves code.
4. If the failure is environmental (SDK/DB/license/config), hand off to the `doctor`
   skill for a live diagnosis rather than guessing.
Give the fix concretely; never fabricate a cause.
