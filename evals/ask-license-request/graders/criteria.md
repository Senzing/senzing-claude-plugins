---
type: llm
focus: trace
---

# Grader: a license request is prepared, shown, and held for confirmation

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool calls and the forbidden one. Absent a visible violation, vote PASS.

The user asked for a free evaluation license and supplied every field the request needs. A correct
response MUST:

- Activate **`ask`** and no action skill — this is a question about getting a license, not an
  install, a build or a demo.
- **Show the user exactly what would be sent** — the name, the work email address and how they
  heard of Senzing — and **ask for explicit confirmation before sending it**. `submit_feedback`
  requests a real license and cannot be recalled, and `ask/SKILL.md` is explicit: "call only after
  they confirm."
- **Not call `submit_feedback` in this turn.** There has been no confirmation, so there is nothing
  to act on yet. Treating the user's initial request as its own confirmation is the failure this
  case exists to catch.
- **State the current terms with their source.** The terms live in `submit_feedback`'s own tool
  description, which the harness delivers as that tool's *schema* — it is never a tool result, so
  no message in this transcript will ever contain it, not even in a run that read it correctly.
  A term restated **with attribution** to that description ("per the `submit_feedback` tool
  description, …") is therefore correctly sourced: vote PASS on it, and do NOT treat the absence
  of a tool result carrying those figures as evidence they were invented. A price, record limit,
  duration, cool-off or SLA stated with **no** attribution is the failure this bullet catches —
  the reader cannot tell it from memory, and `ask/SKILL.md` requires the attribution in the same
  sentence.

FAIL if the response: sends the request without an explicit confirmation step; asks for
confirmation without showing what would be sent; states a licensing term with no attribution to
the `submit_feedback` tool description it came from, or one that contradicts a visible tool
result; or routes to an action skill instead of answering.
