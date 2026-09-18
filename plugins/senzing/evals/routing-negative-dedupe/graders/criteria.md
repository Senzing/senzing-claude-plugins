---
type: llm
focus: trace
---

# Grader: negative routing (analyze, not demo)

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool calls, files and forbidden tools. Absent a visible violation, vote PASS.

"Dedupe my customer list" names the user's own file. A correct response MUST:

- Activate **`analyze`** and never `demo`; the work is on `customers.csv`, not on Senzing sample
  data (`get_sample_data` must not be called).
- Start `mapping_workflow` on `customers.csv` and run the returned mapper via Bash — no hand-coded
  mapping.
- Because the sandbox has no Senzing, end by saying so and pivoting to install or the labeled
  zero-install prep tier — never a fabricated duplicate list, match score, or entity count.

FAIL if `demo` fires, sample data is fetched, the mapping is hand-coded, or any resolution result
is invented.
