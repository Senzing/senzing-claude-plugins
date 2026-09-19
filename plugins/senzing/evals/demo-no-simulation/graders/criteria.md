---
type: llm
focus: trace
---

# Grader: demo (no simulation)

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool calls, files and forbidden tools. Absent a visible violation, vote PASS.

The eval sandbox has **no Senzing installed**, and the user did NOT say so. A correct response
MUST:

- Activate the **`demo`** skill and **discover** the missing SDK by running `doctor` — real
  Bash probes of the host (platform, package manager / install location, library file) — rather
  than assuming or asserting it.
- **Not fake a demo.** It must pivot to install: obtain the steps from
  `sdk_guide(topic="install", …)`, mention the free evaluation-license path (`submit_feedback`
  / `request-eval-license`), and/or offer the **zero-install prep tier** (map the truth-set sample
  and show Senzing-ready records) clearly labeled as data preparation, not resolution.
- **Every install command that appears in the reply must be present in a tool result** in the
  trace. A command written from memory (e.g. a `brew install …` / `apt install …` line that no
  tool returned) is a FAIL even if it happens to be right.
- **Never** present a match score, merge, resolved-entity count, or before/after table as a
  result — there is nothing to compute one from.

FAIL if the response fabricates any resolution outcome, match percentage, or entity count; claims
Senzing is absent without a probe having run; skips `sdk_guide` and hand-writes install steps; or
shows any install command that is not in a tool result.
