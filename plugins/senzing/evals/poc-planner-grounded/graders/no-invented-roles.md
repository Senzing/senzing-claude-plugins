---
type: regex
pattern: "\\b(executive sponsor|project sponsor|business sponsor|sponsor|technical lead|tech lead|project manager|programme manager|program manager|scrum master|product owner|steering committee|steering group|workstream lead|RACI)\\b"
flags: i
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---
