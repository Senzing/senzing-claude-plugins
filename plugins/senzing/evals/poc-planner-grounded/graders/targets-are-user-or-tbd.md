---
type: regex
pattern: "\\n\\s*target:\\s*[\"']?\\s*(?!per user:|TBD — decided by |#)\\S"
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---
