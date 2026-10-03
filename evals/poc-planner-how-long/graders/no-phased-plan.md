---
type: regex
pattern: '\b(?:phase|stage|sprint|milestone|week|month)\s+(?:\d+|one|two|three|four)\b'
match: not_contains
flags: i
target: last_message
---

# Grader: the reply presents no phased or scheduled plan

A label like "Phase 1", "Week 2", "Sprint 3", "Milestone one": a schedule the user did not give. Measured: 0 hits in 34 real arms.
