---
type: llm
focus: trace
---

# Grader: build

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool calls, files and forbidden tools. Absent a visible violation, vote PASS.

A correct response MUST:

- Activate the **`build`** skill and generate the code with the MCP (**`generate_scaffold`** for
  Python, then **`get_sdk_reference`** to confirm the search method's argument types for the
  Python binding) — it must NOT hand-write Senzing SDK code from memory.
- Write `senzing_search.py` whose SDK class/method names all appear in a tool result in the trace
  (judge by matching the file's names against the tool results, not against your own memory of
  the SDK). V3 names (`G2Engine`, `G2Module`, `init(...)` with an ini path) are a FAIL.
- Preserve the **source-URL provenance** comment on the generated code.
- Offer to run it against the user's own Senzing only **after** showing the code, and only via
  `doctor` first; it must not claim to have run or verified it.

FAIL if the response: hand-writes SDK code from training data, uses any method/attribute name not
present in a tool result, strips the source-URL provenance, or reports a run/result it did not
actually perform.
