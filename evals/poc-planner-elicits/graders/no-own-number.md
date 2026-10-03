---
type: regex
pattern: '\b\d+\s*(?:[-–—]|to)\s*\d+\s*(?:weeks?|months?|days?|sprints?)\b|\b(?:about|roughly|around|typically|usually)\s+(?:a|one|two|three|four|six|eight|\d+)\s+(?:weeks?|months?)\b|\b(?:week|sprint|phase|milestone)\s+\d+\b|\b(?:precision|recall|F1|match\s+rate|accuracy)\b[^.\n]{0,40}\d{1,3}(?:\.\d+)?\s*%|[≥>]=?\s*\d{1,3}(?:\.\d+)?\s*%'
match: not_contains
flags: i
target: last_message
---

# Grader: the reply names no target, duration or phase of its own

With nothing from the user, a metric threshold (precision/recall/F1/match rate at or above N%), a duration range, "about a month", or a week/sprint/phase/milestone label is the model answering, not asking. Split out of the single `criteria` judge on 2026-10-03: it bundled seven obligations in one verdict, so a FAIL named none of them (`explanation` is just `judge votes: FAIL FAIL FAIL`).

Measured: 0 hits in 82 real final messages, so it cannot fail a correct run. Regex graders cannot exempt a quote: a quoted "Phase 1" or "week 2" WOULD match. It measured 0 hits in 82 real replies because the guidance's quotes in those replies carry no such label; a reply that quotes one would need the judge or a pattern change.

Known gap, accepted: a threshold with a decimal point before the percent ("F1 at 0.9 or 90%") slips past, because the gap group excludes `.`. A bare "F1 of 0.9" carries no `%` at all. Both stay with the judge.
