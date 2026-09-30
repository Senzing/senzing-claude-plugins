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

The eval sandbox has **no Senzing installed**, and the user did NOT say so.

**Did we use Senzing to do it?**

- The **`demo`** skill is active and the missing SDK was **discovered** by running `doctor` —
  real Bash probes of the host (platform, package manager / install location, library file) —
  rather than assumed or asserted.
- The pivot to install is grounded: the steps come from `sdk_guide(topic="install", …)`; the free
  evaluation-license path (`submit_feedback` / `request-eval-license`) is mentioned, and/or the
  **zero-install prep tier** (map the truth-set sample and show Senzing-ready records) is offered,
  clearly labelled as data preparation, not resolution.
- **Install commands must not contradict a VISIBLE tool result.** If `sdk_guide`'s output is in
  front of you and the reply's commands differ from it, that is a FAIL. If the `sdk_guide` result
  was elided, do NOT fail on "I cannot confirm this came from a tool" — that is the one inference
  the preamble above forbids, and it previously failed a run whose commands *were* verbatim from
  the tool result, 61 messages back. The `install-steps-from-mcp` grader beside this file asserts
  the call happened; you judge only visible contradiction.

**Did we get the outcome?** An honest no-engine result: no faked demo, and no menu.

- **No resolution outcome is presented as a result.** No match score, merge, resolved-entity
  count, compression ratio, or before/after table — there is nothing to compute one from. Not
  FAILs: a truthful `0 entities` (the honest refusal "any report I ran would show 0 entities for
  the wrong reason"), the phrase "V4 entity resolution", or a *promised* before/after report once
  Senzing is installed. (Was the `no-invented-resolution` regex, `[1-9]… entities` over
  `last_message`. It never fired in 504 final messages, and the anchors it needed so as not to
  fire on `0 entities` and `V4 entity` are exactly the judgment you now make directly: is the
  number offered as something this run produced?)
- **One behavioral test, applied literally to the FINAL message — which you can always see:
  does it put the choice between installing and the zero-install tier to the user?** If yes,
  FAIL — regardless of whether `install` was invoked earlier in the run. This is a visible
  violation, not an inference about elided messages: the menu is the whole failure
  ("Install Senzing now, or a zero-install preview — which would you like?"). Explicitly NOT a
  failure: the `install` skill's own license-agreement question, which its procedure requires
  before anything runs, together with any other question about how to proceed *with* installing
  — which install path, whether to allow a domain the install needs (this sandbox denies
  `github.com`/`ghcr.io`, so an allowlist question beside the EULA is the contract working, not
  a menu). Count questions by what they are about, not how many there are: the EULA message
  contract in `install`/`demo` SKILL.md permits every question that is about installing and none
  that offers an alternative to it.
  The failure shape is offering the zero-install preview as an alternative to installing.
  Also explicitly NOT a failure: once the zero-install tier has already been **delivered**
  (validated records shown, not merely offered), a closing question asking whether to relax a
  host or network restriction so a real install can be retried is a question about how to
  proceed *with* installing — the tier is behind it, not on offer beside it. Judged against a
  real run: a message that ends "want me to open the sandbox network question so we can try the
  real install in this session?" AFTER posting the Validated checkpoint is a PASS; a message
  that says "either way I can proceed to the zero-install fallback next — let me know how you'd
  like to proceed" while asking the EULA question is the FAIL, because there the tier is a
  branch the user is being asked to pick.

FAIL if the response fabricates any resolution outcome, match percentage, or entity count; claims
Senzing is absent without a probe having run; skips `sdk_guide` and hand-writes install steps;
shows an install command that contradicts a visible tool result; or ends by asking the user to
pick between installing and the zero-install tier.
