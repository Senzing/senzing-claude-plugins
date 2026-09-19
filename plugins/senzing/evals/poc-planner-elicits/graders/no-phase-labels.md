---
type: regex
pattern: "\\b(weeks?|sprints?|milestones?)\\s*(\\d+|one|two|three|four|five|six)\\b"
flags: i
match: not_contains
target: last_message
---
