---
type: regex
pattern: "\\b(gantt|timeline|kick-?off (date|meeting)|go-live date|sprint planning)\\b"
flags: i
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---
