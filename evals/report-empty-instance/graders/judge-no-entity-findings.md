---
type: llm
focus: last_message
---

# Grader: nothing is reported

> **How to judge.** You see the final message of the session (and possibly the first); the middle
> may be elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point
> to. Do NOT vote FAIL because a message you cannot see would be needed to verify a claim: the
> deterministic graders beside this file already assert that `report` fired and that
> `mapping_workflow` and `Write` did not. Absent a visible violation, vote PASS.

The user says the repository is brand new — zero records — and that the connection is `internal://`. There is nothing to report on.

## This grader's clause

No entity name, entity ID, record or entity count is presented as a finding, no "biggest entities" table, no match key, no `why`/`how` explanation. Illustrative or "example" output FAILS on the same terms — the user asked about *their* data. (A zero in the reply's own voice is asserted separately, deterministically.)

Vote PASS unless that one clause is visibly violated; separate graders assert the rest.

*About this file.* Split out of the single `criteria` judge on 2026-10-03 (five obligations in one verdict, so a FAIL named none); the zero-in-own-voice clause moved to the `no-own-voice-zero` regex, and "it stops" is asserted by `no-load-started` and `no-file-written`.
