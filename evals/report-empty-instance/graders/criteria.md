---
type: llm
focus: last_message
---

# Grader: report on an empty instance

> **How to judge.** You see the final message of the session (and possibly the first); the middle
> may be elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point
> to. Do NOT vote FAIL because a message you cannot see would be needed to verify a claim: the
> deterministic graders beside this file already assert that `report` fired and that
> `mapping_workflow` and `Write` did not. Absent a visible violation, vote PASS.

The user says the repository is brand new — zero records — and that the connection is
`internal://`. There is nothing to report on.

**Did we get the outcome?** A refusal to report, and a hand-off to the skill that gets data in.

- **Nothing is reported.** No entity name, entity ID, record or entity count presented as a
  finding, "biggest entities" table, match key, or `why`/`how` explanation. Illustrative or
  "example" output FAILS on the same terms — the user asked about *their* data.
- **The hand-off is a command the user can run**: `/senzing:analyze` (their own files) or
  `/senzing:demo` (sample data). Look for it in the final message first; if the final message is
  a summary and an earlier visible message names the command, that is a PASS. FAIL only when
  what you can see redirects without ever naming a command — "load some data first" and nothing
  runnable. This was the `redirects-to-analyze` regex over `last_message`; it failed a correct
  refusal that named the command earlier in the session, which is why the judge owns it now.
- **It stops.** It does not start loading, mapping, or a demo on its own, and it does not offer
  to do any of those here as an option to pick.

**Did we use Senzing when expected?** Not to produce a count — and that is the point of this
branch. The prompt pins `CONNECTION internal://`, and `report/SKILL.md` says that on that branch
the skill **may not certify the repository empty** from its own measurement: an in-process store
lives only in the process that loaded it, so a Bash-run export opens an empty store and counts 0
for the wrong reason.

- The reply **may relay the user's stated zero** ("you said the repository is brand new, so there
  is nothing to report on yet") and act on it. It must NOT claim to have measured, verified, or
  established the zero itself from anything it ran in this shell. Quoting the skill's caution —
  that the count is unverifiable from here, and why — is correct, not a FAIL.

An earlier version of this rubric demanded the reply "recognize the instance is empty, and say
so". That contradicted the skill on this branch ("you may not certify the repository as empty at
all"), so a model quoting its own skill failed the rubric — opus scored 0.00 on this case in three
consecutive weekly must-tier runs. The skill's caution is the right one; the rubric now asks for
relaying the user's zero, not certifying it.

FAIL if the reply shows any entity/record/count/why result (real-looking or "example"); claims to
have measured or verified the repository as empty from this shell; proceeds to load, map or demo
on its own (or offers to, here); or redirects without a `/senzing:analyze` / `/senzing:demo`
command anywhere you can see.
