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

The URL's liveness is checked separately by the `eula-link` job in `.github/workflows/ci.yml`; a
grader can only assert what the reply says.
