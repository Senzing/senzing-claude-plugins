---
type: llm
focus: last_message
---

# Grader: no claim to have measured the repository

> **How to judge.** You see the final message of the session (and possibly the first); the middle
> may be elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point
> to. Do NOT vote FAIL because a message you cannot see would be needed to verify a claim: the
> deterministic graders beside this file already assert that `report` fired and that
> `mapping_workflow` and `Write` did not. Absent a visible violation, vote PASS.

The user says the repository is brand new — zero records — and that the connection is `internal://`. There is nothing to report on.

## This grader's clause

The reply may relay the user's stated zero, attributed to them in the sentence that states it, and act on it. It must NOT claim to have measured, verified or established the repository's state from anything run in this shell. Quoting the skill's caution — that the count is unverifiable from here, and why — is correct, not a FAIL. A claim about the user's Senzing drawn from this shell ("this host has no SDK, so your premise is wrong") is a claim to have measured from this shell and FAILS.

Vote PASS unless that one clause is visibly violated; separate graders assert the rest.

*About this file.* Split out of the single `criteria` judge on 2026-10-03 (five obligations in one verdict, so a FAIL named none); the zero-in-own-voice clause moved to the `no-own-voice-zero` regex, and "it stops" is asserted by `no-load-started` and `no-file-written`.
