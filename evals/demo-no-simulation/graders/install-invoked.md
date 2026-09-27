---
type: regex
pattern: 'senzing\.com/end-user-license-agreement'
flags: i
target: last_message
---

# Grader: the user was shown the LICENSE AGREEMENT, not made to watch a hand-off

This asserted that the `install` **Skill** was invoked. That is a route, not an outcome, and it
manufactured flakiness: a run that already held the platform's install steps — `doctor`'s own
Step 0 calls `sdk_guide(topic="install")` (`skills/doctor/SKILL.md:87`), so they are in context
before this decision is reached — could deliver the correct result by a shorter path and still
fail. `install-invoked` failed roughly 1 run in 8 for exactly that, after passing 6 in a row.

But the old grader was proxying something real that nothing else asserted, and dropping it
outright would have lost the axis. `install/SKILL.md:75-86` surfaces the **EULA, by its URL,
unconditionally, before anything runs**. `sdk_guide(topic="install")` does not. So the short
route is only acceptable **if the user still got the license agreement** — and if it did not, that
is a compliance defect, not a stylistic one.

So assert that instead. The pattern is a verbatim copy of `install-eula/graders/eula-surfaced.md`,
which is the same obligation measured the same way elsewhere in the suite.

Provably able to PASS by EITHER route: a run that invokes `install` ends on that skill's
license-agreement question (`skills/demo/SKILL.md:87-92` guarantees it is the final message), and
a run that hands the steps over directly passes iff it also linked the agreement.
Provably able to FAIL: any reply that presents install steps without the agreement — which is the
outcome that actually matters and which nothing deterministic asserted before.

## Why this stays on `last_message`, and what that costs

A run failed this by pointing backwards: its final message read "run
`/senzing:install` … (steps and EULA link are above)". The user HAD been shown the
agreement; the closing message referred to it instead of repeating it.

`target: trace` looks like the fix and is not. The URL is in no SKILL.md — it comes
back inside `sdk_guide(topic="install")`'s response, so the trace contains it
whether or not the reply ever showed it to anybody (checked: the failing trace has
it on two lines, one assistant and one tool result). Widening the target would make
this grader pass on a run that never surfaced the agreement at all, which is exactly
the failure it exists to catch. A vacuous compliance check is worse than none.

So the surface stays and the skill changed instead: `demo/SKILL.md` now requires any
message that points the user at installing to carry the URL in that message. That is
better for the reader regardless — nobody should have to scroll back for the one
thing they are being asked to agree to.

The URL's liveness is checked separately by the `eula-link` job in `.github/workflows/ci.yml`; a
grader can only assert what the reply says.
