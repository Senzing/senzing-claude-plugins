---
type: regex
pattern: "\\b\\d+\\s*(weeks?|months?)\\b|\\b(\\d+|one|two|three|four|five|six|eight|ten|twelve)\\s*(to|[-–])\\s*(\\d+|one|two|three|four|five|six|eight|ten|twelve)\\s*(weeks?|days?|months?)\\b"
flags: i
match: not_contains
target: last_message
---
