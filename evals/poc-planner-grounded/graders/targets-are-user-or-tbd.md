---
type: regex
pattern: "\\n\\s*target:\\s*(?:[\"']\\s*(?!per user:|TBD — decided by |#)|(?![\"'])(?!per user:|TBD — decided by |#))\\S"
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---

# Grader: every `target:` is the user's own number or an owned TBD

Fires when a `target:` carries a value the skill invented — anything that is not
`per user: …`, not the literal `TBD — decided by <owner>`, and not a `#` comment.

The two legal forms are matched through an ALTERNATION, not an optional quote.
The previous pattern opened with `["']?`, which can match empty: on a quoted
value the engine tried the quote, failed the lookahead against the real value,
then BACKTRACKED to the empty branch and tested the lookahead against the quote
character itself — which is never `per user:` or `TBD`, so it matched and the
grader failed a correct plan. `target: TBD — decided by X` passed while
`target: "TBD — decided by X"` failed. The offline fixture only ever carried the
unquoted form, so nothing caught it. Each branch now commits to quoted or
unquoted before the lookahead runs, so the lookahead always tests the VALUE.
