---
type: regex
pattern: "\\b(\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\\s*(to|[-–])\\s*(\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\\s*(weeks?|days?|months?)\\b|\\bweeks?\\s*\\d+\\s*[-–]\\s*\\d+"
flags: i
match: not_contains
target: last_message
---
