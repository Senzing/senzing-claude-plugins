---
type: regex
pattern: "\\b(\\d+|one|two|three|four|five|six|eight|ten|twelve)\\s*(to|[-–])\\s*(\\d+|one|two|three|four|five|six|eight|ten|twelve)\\s*(weeks?|days?|months?)\\b|\\bweeks?\\s*\\d+\\s*[-–]\\s*\\d+"
flags: i
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---
