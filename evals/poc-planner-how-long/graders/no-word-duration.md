---
type: regex
pattern: '\b(?:a\s+few|several|a\s+couple\s+of|couple\s+of|handful\s+of)\s+(?:weeks?|months?|days?|hours?|quarters?|sprints?)\b|\b(?:typically|usually|generally|normally|roughly|about|around)\s+(?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|twelve)\s+(?:weeks?|months?|days?|hours?|quarters?|sprints?)\b|\b(?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|twelve)[-\s](?:to|or)[-\s](?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|twelve)\s+(?:weeks?|months?|days?|hours?|quarters?|sprints?)\b|\b(?:one|two|three|four|five|six|eight|ten|twelve)-(?:week|month|day|sprint)\b'
match: not_contains
flags: i
target: last_message
---

# Grader: a reply to "how long" names no duration in WORDS

The digit forms are `no-duration`. This covers "a few weeks", "typically a month", "two to three weeks", "a six-week effort". Conservative: it needs a quantifier (few/several/couple, or typically/usually/about/around + a count word, or a spelled-out range or compound) before the unit, so a bare "weeks" or "the length depends" stays clean. Measured: 0 hits in 34 real arms.
