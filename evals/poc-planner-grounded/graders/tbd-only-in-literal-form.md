---
type: regex
pattern: "(?:^|\\n)[ \\t]*(?:-[ \\t]+|[A-Za-z_][A-Za-z0-9_]*:[ \\t]*)[\"']?TBD(?![ \\t]+—[ \\t]+decided by )"
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---

# Grader: an undecided VALUE carries its owner; the word in prose is not a defect

The rule this enforces is `poc-planner`'s: an undecided row reads
`TBD — decided by <owner>` and nothing else. The defect it exists to catch is a
TBD that smuggles in the model's own guess — `TBD (typically 90-95%)` — or one
with no owner at all, because both hand the user a number they never gave.

**It was unanchored, and that made it fire on correct runs.** The old pattern was
`\bTBD\s*[(:,.\]"']|\bTBD\s+[-–]\s|\bTBD\s*\n` — any `TBD` followed by
punctuation, anywhere in the file. A run failed CI on this line, which is the
plan being *right*:

```
- "Discrepancy (not a TBD, a flag): sdk_guide(load) says email sales@senzing…"
```

The model used the word in a sentence, to say that item is **not** a TBD, and the
comma after it tripped the grader. Failing a run for correctly describing the
rule is worse than not checking at all: it teaches nothing and costs a rerun.

So the pattern now matches only a TBD in **value position** — after a `key:` or a
`- ` list marker, optionally quoted — which is the only place a TBD can actually
withhold a decision. Prose is left alone.

Checked against eight cases, four that must fire and four that must not:
`target: TBD (typically 90-95%)`, `- TBD, to be sorted`, `target: "TBD"`, and a
bare `target: TBD` all fire; `TBD — decided by <owner>` quoted and unquoted, the
"not a TBD, a flag" line above, and `the following are TBD, each owned` all stay
silent.

The former sibling `targets-are-user-or-tbd.md` anchored on `target:` keys the same
way and never produced this failure; it moved to the judge on 2026-09-29 because
what it really asked — is this target the user's number or an invented one — is a
judgment about content, and its `per user:` prefix was a spelling the skill imposed
only so a regex could see provenance. This grader stays because the TBD literal has
exactly one correct spelling and a bare `TBD` with no owner is a defect in every
context.
