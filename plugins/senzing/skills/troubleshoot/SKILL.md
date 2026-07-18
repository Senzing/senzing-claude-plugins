---
name: troubleshoot
description: >
  Diagnose and resolve a Senzing error or failure. Use automatically when the user pastes a
  Senzing error code or stack trace (e.g. "SENZ0005", "0005", "5", "why is add_record failing?"),
  or asks what an error means. Looks up the authoritative cause and fix, then points at docs and
  real code examples.
argument-hint: "[error-code-or-message]"
allowed-tools: Bash, Read, Skill, mcp__plugin_senzing_senzing__*
---

# Troubleshoot a Senzing error

Grounded by the **Senzing MCP server** (456 real error codes). Do not explain Senzing errors from
training data.

1. **Inputs.** `$ARGUMENTS` may carry the error code or message. Extract the error code (e.g.
   `SENZ0005`, `0005`, or `5`) from the arguments or the recent conversation/trace. If none was
   given and none is visible, **ask the user to paste the error code or message** — do not guess a
   code. For a runtime failure without a clean code, capture the exact message.
2. Call `explain_error_code` for the authoritative cause + resolution steps.
3. Use `search_docs` for surrounding context (config, GDPR, throughput, etc.) and `find_examples`
   for a correct code pattern if the fix involves code.
4. If the failure is environmental (SDK/DB/license/config), hand off to the `doctor`
   skill for a live diagnosis rather than guessing.
Give the fix concretely; never fabricate a cause.
