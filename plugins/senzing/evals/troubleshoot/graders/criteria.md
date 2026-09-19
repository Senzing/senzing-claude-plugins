---
type: llm
focus: trace
---

# Grader: troubleshoot

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool calls, files and forbidden tools. Absent a visible violation, vote PASS.

A correct response MUST:

- Activate the **`troubleshoot`** skill and call the MCP **`explain_error_code`** for `0033E`
  (accept `0033`, `33`, or `SENZ0033` as the argument form).
- Report the cause and the resolution steps **as returned by `explain_error_code`** in the trace.
  Do not judge against your own idea of what SENZ0033 means — judge whether the final answer
  matches the tool result. If the answer states a cause or a fix that is absent from that
  visible tool result, that is fabrication.
- Derive the explanation from the MCP result, **not** from the model's training data; if it also
  calls `search_docs` / `find_examples` for context, the extra material must likewise trace back
  to a tool result.

FAIL if the response: explains the error before/without calling `explain_error_code`, states a
meaning or resolution step that is not in the tool result, invents a different error code, or
writes any file.
