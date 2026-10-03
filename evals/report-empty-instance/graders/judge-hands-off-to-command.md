---
type: llm
focus: last_message
---

# Grader: the hand-off is a command the user can run

> **How to judge.** You see the final message of the session (and possibly the first); the middle
> may be elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point
> to. Do NOT vote FAIL because a message you cannot see would be needed to verify a claim: the
> deterministic graders beside this file already assert that `report` fired and that
> `mapping_workflow` and `Write` did not. Absent a visible violation, vote PASS.

The user says the repository is brand new — zero records — and that the connection is `internal://`. There is nothing to report on.

## This grader's clause

`/senzing:analyze` (their own files) or `/senzing:demo` (sample data) is named literally. Look in the final message first; if the final message is only a summary and an earlier VISIBLE message names the command, that is a PASS. FAIL only when what you can see redirects without ever naming a command — "load some data first" and nothing runnable. Naming both is one hand-off with two entry points, not a menu.

Vote PASS unless that one clause is visibly violated; separate graders assert the rest.

*About this file.* Split out of the single `criteria` judge on 2026-10-03 (five obligations in one verdict, so a FAIL named none); the zero-in-own-voice clause moved to the `no-own-voice-zero` regex, and "it stops" is asserted by `no-load-started` and `no-file-written`.
