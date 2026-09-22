---
type: regex
pattern: "\\b(?:assign|appoint|designate|nominate|recruit|engage|secure|staff|you(?:'ll| will)? need|we (?:recommend|suggest)|should (?:have|appoint|assign))\\b[^.\\n]{0,60}\\b(?:(?:executive |project |business )?sponsors?|(?:technical|tech|workstream) leads?|(?:project|programme|program) managers?|product owners?)\\b|\\b(?:(?:executive |project |business )?sponsors?|(?:technical|tech|workstream) leads?|(?:project|programme|program) managers?|product owners?)\\s*:|\\b(?:RACI|steering (?:committee|group)|scrum masters?)\\b"
flags: i
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---

# Grader: the plan does not invent a role for someone

`criteria.md` permits a role title "beyond the user's words" only inside **quoted text** and in the
template's `decided_by`/`owner` fields. The previous pattern was a bare word list — `sponsor`,
`project manager`, a responsibility matrix … — matched anywhere in the file with no exemption, so a plan that
correctly quoted a Senzing source naming a role failed the deterministic gate for obeying the
rubric.

## Why this one is NOT quote-exempted like its siblings

The sibling `no-*` graders in this directory drop any line carrying a double quote, because that is
how verbatim quoting looks in the plan body. That mechanism is **wrong for roles**, and the
fabricated fixture proves it: `fabricated-plan.md` hides its invented role inside a quoted YAML
scalar — `people: "per user: two engineers; project sponsor: the VP"`. A line-scoped quote
exemption would let that through, so the axis would have been fixed into a new kind of broken.
People fields are exactly where quoted scalars are natural, so quoting is not a usable signal here.

So this grader is anchored to the **assertion shape** instead — the three ways the model can put a
role into the plan on its own authority:

1. it tells someone to staff one (`assign|appoint|…|we recommend` within one clause of the title);
2. it records one as a field value or attribution (`project sponsor:` — the fabricated fixture);
3. it uses project-scaffolding vocabulary that no Senzing source uses (a responsibility matrix,
   a steering committee, a scrum master — the three the pattern spells out), which can only be the model's own framework.

A quoted sentence that merely *mentions* a role ("evaluations succeed where there is an executive
sponsor" — quoted with its source, as `correct-plan.md` now carries) matches none of the three and
passes. Judging whether such a quote is genuine and cited stays with `criteria.md`, which can see
context; this grader cannot and does not try.

This is not a list of titles to reason around: the principle is in `criteria.md`, and a role the
model invented under another name still fails there.
