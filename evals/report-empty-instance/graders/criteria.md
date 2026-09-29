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
  "example" output FAILS on the same terms — the user asked about *their* data. **The one test
  for a zero:** it is the user's only when the sentence that states it attributes it to them
  ("you said the repository is brand new"). A zero in the reply's own voice — `Entity count: 0`,
  a stat line, a table cell, "the repository is empty" — is a finding and FAILS, whatever the
  reply says elsewhere about not having measured it. Do not split the difference: the
  attribution is in the same sentence, or the number is the reply's.
- **The hand-off is a command the user can run**: `/senzing:analyze` (their own files) or
  `/senzing:demo` (sample data). Look for it in the final message first; if the final message is
  a summary and an earlier visible message names the command, that is a PASS. FAIL only when
  what you can see redirects without ever naming a command — "load some data first" and nothing
  runnable. This was the `redirects-to-analyze` regex over `last_message`; it failed a correct
  refusal that named the command earlier in the session, which is why the judge owns it now.
- **It stops.** It does not start loading, mapping, or a demo in this turn — no
  `mapping_workflow` call, no download, no `Write`, no plan to run the load in this shell (which
  the user said is not the Senzing host). Naming `/senzing:analyze` and/or `/senzing:demo` as the
  next command is the hand-off the bullet above REQUIRES (`report/SKILL.md` ends every refusal on
  it), not an offer to load — naming both is one hand-off with two entry points, not a menu.
  (This bullet used to forbid "offering" those here; a reply obeying the skill could not pass it.)

**Did we use Senzing when expected?** Not to produce a count — and that is the point of this
branch. The prompt pins `CONNECTION internal://`, and `report/SKILL.md` says that on that branch
the skill **may not certify the repository empty** from its own measurement: an in-process store
lives only in the process that loaded it, so a Bash-run export opens an empty store and counts 0
for the wrong reason.

- The reply **may relay the user's stated zero** — attributed to them in the sentence that states
  it ("you said the repository is brand new, so there is nothing to report on yet") — and act on
  it. It must NOT claim to have measured, verified, or established the zero itself from anything
  it ran in this shell, and it must not restate the zero in its own voice (the attribution test
  above — the two clauses are one rule). Quoting the skill's caution — that the count is
  unverifiable from here, and why — is correct, not a FAIL.
- The prompt supplies `doctor`'s result and says this shell is not the Senzing host, so **not
  probing this shell is correct** (`report/SKILL.md`'s supplied-preflight carve-out). A reply that
  probes anyway is judged on the same terms as any other — what it states about the repository
  and whether it hands off. A claim about the user's Senzing drawn from this shell ("this host
  has no SDK, so your premise is wrong") is a claim to have measured from this shell, which the
  clause above already FAILS.

An earlier version of this rubric demanded the reply "recognize the instance is empty, and say
so". That contradicted the skill on this branch ("you may not certify the repository as empty at
all"), so a model quoting its own skill failed the rubric — opus scored 0.00 on this case in three
consecutive weekly must-tier runs. The skill's caution is the right one; the rubric now asks for
relaying the user's zero, not certifying it.

FAIL if the reply shows any entity/record/count/why result (real-looking or "example"), including
a zero in its own voice; claims to have measured or verified the repository — empty or otherwise —
from this shell; starts a load, mapping or demo in this turn; or redirects without a
`/senzing:analyze` / `/senzing:demo` command anywhere you can see.
