# Standard practice: fix → re-run → four-model review → fix

**Any eval failure goes through this loop. Not optional, not "when it looks tricky".**

A skill fix is a PROMPT change, and a prompt change is a *hypothesis about model
behavior* until a model is graded against it. Writing one and reporting it as
fixed is the single easiest way to ship a regression that reads as green.

## The loop

1. **Diagnose from evidence, not from the score.** Download the run artifact and
   read the failing grader's `explanation` and the run's `evidence` (the final
   message the judge saw). Classify each failure as: real skill defect · bad
   rubric · judge noise. Never assume the skill is wrong — three of the seven
   judge failures in the run that produced this document were defective rubrics.
2. **Write the fix.**
3. **Send it to four models before spending a run.** See below.
4. **Integrate, then re-run.**
5. **Repeat until the deterministic gate is clean.** Judge failures are reported
   separately and do not block.

## Step 3: the four-model review

Spawn four independent read-only reviewers, one per model, on the SAME material.
These are instructions consumed by an LLM, so the reviewers ARE the consumers.

| Model | Role | Ask it for |
|---|---|---|
| **Sonnet** | **The bar.** Both suites pin `EVAL_MODEL=sonnet`, so this is literally the model that will grade the change. | "Would this change your behavior? Quote the sentence you would still write." Its ranking is the one to sequence from. |
| **Opus** | The ceiling. | "Where would a smaller model diverge from you? Name the inference you are making that the text never states." An unstated premise is the defect. |
| **Haiku** | Input, **not** a gate. A rule needing a capable model is acceptable. | Ambiguity and self-contradiction that would bite ANY model: overloaded words, colliding imperatives, unclear scope. |
| **Fable** | Independent perspective. | Loopholes, and whether the fix contradicts the eval's own fixtures/expected outcome. |

Give every reviewer these four questions:
- **(a)** Would this actually change your behavior, or is it satisfiable in
  letter while violated in spirit? Quote the sentence you would still write.
- **(b)** Name the next loophole. Every original failure was a model routing
  AROUND a rule it had technically obeyed.
- **(c)** Does it contradict another rule in the same file — or the eval's own
  `prompt.md` / fixtures / graders?
- **(d)** Propose tighter wording: exact replacement text.

## Why — the four findings that justify the cost

Run this against the session that created this file. Four reviews, one round,
caught three fixes that would have shipped:

1. **A fix that made its own case impossible to pass.** A `poc-planner` ban on stating a
   total the user never stated collided with `prompt.md`'s expected outcome, the
   GOOD fixture `correct-plan.md`, and a deterministic grader requiring an
   integer `record_count`. Whatever the model did, one side failed. *Found by
   checking the fix against the eval's own artifacts — always do (c).*
2. **A fix in a branch that never executes.** `demo`'s anti-naming rule sat under
   step 2 ("With a working Senzing"), but the failing case runs step 1, the
   zero-install tier — which ORDERED the banned act verbatim. The failing run was
   obeying the file. *Found independently by two models.*
3. **A rule contradicting itself.** `report`'s "Never report on an empty
   instance" against a description saying an empty repo IS this skill's job;
   "report" is both the skill's name and its output.
4. **Closed lists read as exhaustive.** An enumerated ban (id/name/email/pair)
   let row numbers, shared values and COUNTS through. "4 of 6 rows share an
   email" names no row and is still an invented entity count.

## Rules that fall out of this

- **A closed list is a loophole.** State the principle, then say "this is not a
  list of examples to reason around".
- **Check the fix against the eval's own fixtures and `expected_outcome`.** A
  rule that contradicts them cannot pass no matter how good the model is.
- **Check which BRANCH the failing case executes.** A rule in the other branch is
  inert.
- **Prefer one imperative early over precision late.** A rule 120 lines after the
  temptation loses to the temptation.
- **Never report a prompt fix as verified without a graded run**, and prefer ≥2
  runs per case — these graders are flaky per-run, not always-red, so a single
  green run is close to no evidence.

## Round 2 — the judge records votes, not reasons. Re-judge to find the clause.

`ci.json` stores `judgeVotes: [false, false, false]` and nothing else, so which
rubric clause fired is **not** in the artifact. Do not guess it. Extract the
exact material the judge saw — for a `focus: trace` grader the `evidence` string
IS the transcript; for a `focus: { source: file }` grader it is the file — and
re-run the rubric against it **on the judge's own model** (both suites pin
`EVAL_MODEL=sonnet`), asking it to name the clause and the sentence. Two cases,
two answers no amount of reading would have produced:

5. **A clause no transcript can ever satisfy.** `ask-license-request` failed 2/2
   on its first outing for stating the eval-license terms. The terms are real —
   the run read them from `submit_feedback`'s tool description. But a tool
   *description* is injected as that tool's **schema**; it is never a tool
   result, so it appears in no transcript message. The judge saw a visible
   `ToolSearch` whose visible result carried no terms, and correctly called an
   invented result. The rubric simultaneously *required* the terms and left the
   judge no way to see where they came from. Fix on both sides: `ask` now
   attributes any term to the tool description in the same sentence, and the
   rubric grades the attribution — the thing that IS visible.
6. **The skill ordered the act the rubric bans — again.** `poc-planner`'s §6 step
   said "say plainly if they mismatch" about the *Rightsizing* check. One run
   obeyed and wrote "not obviously mismatched against 755,000 records" — the
   plan's own adequacy verdict on the user's volume, which the rubric bans as
   extrapolation and which the GOOD fixture `correct-plan.md` never does (it
   quotes, lists their answers, and stops). Same shape as finding 2. The skill
   was fixed, not the rubric.

Two further rules:

- **Give a file-focused rubric the same "How to judge" preamble as a
  trace-focused one.** `poc-planner-grounded` was the only `criteria.md` in the
  suite without one, and it re-litigated in prose the surface prohibitions its
  34 deterministic siblings already enforce *with the quote exemptions built in*
  — on a 20k-character, quote-dense document. Name the siblings, say the judge's
  job is the two things a regex cannot see (is the quote genuine and cited; did
  the plan add a judgement of its own), and say the template's own empty
  collections are the template.
- **The catch-all sentence must not be broader than the bullet above it.**
  "if it offers to build a truth set" (unqualified) contradicted the §5 bullet
  that bans only a **synthetic/labelled** one — and would have failed the repo's
  own `correct-plan.md`, which quotes the guidance's real-data truth-set route.
  Fourth instance of finding 3.
