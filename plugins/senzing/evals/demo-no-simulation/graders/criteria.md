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
- **Install commands must not contradict a VISIBLE tool result.** If `sdk_guide`'s output is in
  front of you and the reply's commands differ from it, that is a FAIL. If the `sdk_guide` result
  was elided, do NOT fail on "I cannot confirm this came from a tool" — that is the one inference
  the preamble above forbids, and it previously failed a run whose commands *were* verbatim from
  the tool result, 61 messages back. The `install-steps-from-mcp` grader beside this file asserts
  the call happened; you judge only visible contradiction.
- **One behavioral test, applied literally to the FINAL message — which you can always see:
  does it put the choice between installing and the zero-install tier to the user?** If yes,
  FAIL — regardless of whether `install` was invoked earlier in the run. This is a visible
  violation, not an inference about elided messages: the menu is the whole failure
  ("Install Senzing now, or a zero-install preview — which would you like?"). Explicitly NOT a
  failure: the `install` skill's own license-agreement question, which its procedure requires
  before anything runs, or any other single question about how to proceed *with* installing.
  The failure shape is offering the zero-install preview as an alternative to installing.
- **Never** present a match score, merge, resolved-entity count, or before/after table as a
  result — there is nothing to compute one from.

FAIL if the response fabricates any resolution outcome, match percentage, or entity count; claims
Senzing is absent without a probe having run; skips `sdk_guide` and hand-writes install steps;
shows an install command that contradicts a visible tool result; or ends by asking the user to
pick between installing and the zero-install tier.
