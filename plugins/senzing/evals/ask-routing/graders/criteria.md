---
type: llm
focus: trace
---

# Grader: ask (routing + grounding)

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool calls, files and forbidden tools. Absent a visible violation, vote PASS.

This is a plain factual question — the reason the `ask` skill exists. A correct response MUST:

- Activate **`ask`** and no action skill (`analyze`, `build`, `demo`, `report`, `recipes`,
  `install` must not fire).
- Call at least one Senzing MCP tool (`search_docs`, `get_capabilities`, …) **before** the
  answer text. The answer must be consistent with the tool results you can see — do not judge
  attribute names against your own memory of the Entity Specification, and do not fail names you
  simply cannot cross-check because their tool result is elided.
- **Cite the source URL(s)** the tool returned so the user can verify (also checked by regex).
- Write no files and run no commands; end by offering the skill that would act next (e.g.
  `analyze` to map their data), not by starting it.

FAIL if the response answers before any tool call, contradicts a visible tool result, writes a
file, runs a shell command, or starts a mapping/build workflow instead of answering.
