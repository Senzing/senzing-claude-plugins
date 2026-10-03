---
type: llm
focus: last_message
---

# Grader: hardware and infrastructure are ASKED

> **How to judge.** You see the final message of the session (and possibly the first); the middle
> may be elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point
> to. Do NOT vote FAIL because a message you cannot see would be needed to verify a claim: the
> deterministic graders beside this file already assert the required tool calls, the absence of a
> written file and the forbidden tools. Absent a visible violation, vote PASS.

The user gave no inventory, no constraints and no criteria. A correct reply is `poc-planner` asking its Round 1 and stopping.

## This grader's clause

Round 1 block (2) is asked as a question: the hardware available, the platform/OS, the database, cloud or on-prem, and the throughput/latency to demonstrate. FAIL if infrastructure is absent, or only stated in a declarative plan. (A `hardware…?` pattern false-failed correct replies, so this stays with the judge.)

Vote PASS unless that one clause is visibly violated. Ignore every other obligation of the reply: separate graders assert them.

*About this file.* Split out of the single `criteria` judge on 2026-10-03: it bundled seven obligations in one verdict, so a FAIL named none of them (`explanation` is just `judge votes: FAIL FAIL FAIL`). Three clauses stay with the judge because no pattern separated them from correct replies without false-failing some.
