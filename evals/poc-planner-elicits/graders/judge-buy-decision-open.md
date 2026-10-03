---
type: llm
focus: last_message
---

# Grader: the buy decision is asked in open terms

> **How to judge.** You see the final message of the session (and possibly the first); the middle
> may be elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point
> to. Do NOT vote FAIL because a message you cannot see would be needed to verify a claim: the
> deterministic graders beside this file already assert the required tool calls, the absence of a
> written file and the forbidden tools. Absent a visible violation, vote PASS.

The user gave no inventory, no constraints and no criteria. A correct reply is `poc-planner` asking its Round 1 and stopping.

## This grader's clause

Round 1 block (4): what would have to be TRUE for their organization to buy, asked in OPEN terms, with the three shapes (result quality, a functional integration, specific entity-graph scenarios) offered as examples. "Which of these is closest, or none?" after the open question is correct. FAIL only if a closed choice REPLACES the open question, or the shapes are presented as success criteria of the reply's own.

Vote PASS unless that one clause is visibly violated. Ignore every other obligation of the reply: separate graders assert them.

*About this file.* Split out of the single `criteria` judge on 2026-10-03: it bundled seven obligations in one verdict, so a FAIL named none of them (`explanation` is just `judge votes: FAIL FAIL FAIL`). Three clauses stay with the judge because no pattern separated them from correct replies without false-failing some.
