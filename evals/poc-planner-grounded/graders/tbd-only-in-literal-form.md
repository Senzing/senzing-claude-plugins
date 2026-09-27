---
type: regex
pattern: "\\bTBD\\s*[(:,.\\]\"']|\\bTBD\\s+[-–]\\s|\\bTBD\\s*\\n"
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---
