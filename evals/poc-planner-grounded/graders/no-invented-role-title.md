---
type: regex
pattern: '(?:^|\n)(?![^\n]*["“”])[^\n]*\b(?:(?:project|programme|program|delivery)\s+(?:sponsor|manager|lead|owner)|(?:executive|business|project|program(?:me)?)\s+sponsor|sponsor|steering\s+(?:committee|group)|product\s+owner|scrum\s+master|work-?stream\s+lead|tech(?:nical)?\s+lead|RACI|responsibility\s+matrix|stakeholder\s+matrix)\b'
match: not_contains
flags: i
target: { source: file, path: senzing-poc-plan.md }
---

# Grader: the plan assigns no role the user did not state

Replaces the `judge-no-invented-role` clause, whose list is enumerable: a sponsor, project/programme
manager, tech or work-stream lead, product owner, steering committee, scrum master, or a responsibility
matrix. The user said "our VP"; the plan says `the VP`, not `the sponsor`.

**Why it moved out of the judge.** Under an opus judge, a plan that restated the guidance's own question —
"whether procurement, an architecture review, or a business owner already holds a number" — failed this
clause unanimously in CI, while the judge's own replay said both pass and fail for that plan depending on the
run (the CI-passing plan failed 1 of 6, the failing one 3 of 6). The ambiguity was never an invented role: a
role named inside an open QUESTION is not a role assigned. The list of roles that ARE assignments is a
pattern, and a pattern does not flip.

Measured: **0 hits in 36 real plan files**, 0 in the verbatim corpus quotes a plan is required to carry
(`check-poc-graders.py` section A re-checks that on every run), and it fires on the fabricated fixture
("project sponsor: the VP"). Deliberately NOT matched: `owner`, `business owner`, `procurement`, `lead` alone —
those appear in the user's own words, the template's `decided_by`/`owner` fields, and restated guidance questions.

## Quote exemption, by line

A role named inside a cited quote is not a FAIL ("A cited quote that merely mentions a role is not"), and the
correct fixture carries one on purpose: *"Evaluations succeed where there is an executive sponsor who wants the
answer"*, with its source. A whole-file pattern false-fails that, which is exactly why content prohibitions like this
moved to the judge on 2026-09-29. So the pattern matches only **lines with no quotation mark**: an assigned role is
stated in the plan's own voice, and a quoted one sits on a line that carries its quote. This trades recall for
precision on purpose: a role smuggled inside a double-quoted YAML scalar escapes this grader, and
`judge-constraints-are-the-users` still reads that case. Measured: 0 of 36 real plans, 0 on the correct fixture, and a
hit on the fabricated one ("a kick-off meeting with the VP and the project sponsor").

**Known trade-offs.** A bare `sponsor` on an unquoted line would also fail "no sponsor was named"; none of 36 real plans
says that, and the validator loop surfaces it. A role placed inside a double-quoted YAML scalar escapes this grader by
design and is covered by `judge-constraints-are-the-users`, whose fabricated-plan evidence is exactly that shape
(`people: "per user: two engineers; project sponsor: the VP"`, `expectations.json`).
