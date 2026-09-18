---
type: regex
pattern: "TBD[^\\n|]*(\\d+(\\.\\d+)?\\s*%|\\b(typical|typically|usually|commonly|industry|similar evaluations|recommend)\\b)"
flags: i
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---
