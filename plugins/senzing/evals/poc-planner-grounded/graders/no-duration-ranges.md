---
type: regex
pattern: "(?:^|\\n)(?![^\\n]*[\"“”])[^\\n]*(?:\\b(\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\\s*(to|[-–])\\s*(\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\\s*(weeks?|days?|months?)\\b|\\bweeks?\\s*\\d+\\s*[-–]\\s*\\d+)"
flags: i
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---

# Why this pattern starts with a line scope

`criteria.md` beside this file explicitly permits **verbatim cited quotes** — it even names the
Hardware Sizing FAQ's own load phases as acceptable when quoted with their source. The previous
pattern was a flat regex over the whole target with no exemption at all, so a run that quoted
Senzing's own material — exactly what the rubric requires — tripped the deterministic gate for
doing the right thing. Same class as the grader that matched a plain READ of
`SENZING_ENGINE_CONFIGURATION_JSON`.

The prohibition belongs to the model's OWN assertions. The mechanism the grader vocabulary
actually supports is a line scope: `(?:^|\n)` anchors the match at a line start and the negative
lookahead `(?![^\n]*["“”])` drops the whole line if it carries a double quote — the only shape
verbatim quoting takes in this output. No lookbehind is used, so the pattern means the same thing
in the CLI's JavaScript engine and in `scripts/check-poc-graders.py`'s Python stand-in; both are
exercised offline against `grader-fixtures/plans/`.

What this deliberately does NOT try to do is decide whether a quote is genuine and cited. A regex
cannot see that. `criteria.md` can, and already does ("not a verbatim quote with its source is a
FAIL"). The split is intentional: deterministic here, contextual there.
