---
type: regex
pattern: "\\n\\s{2,}(note|notes|guidance|hint|hints|rationale|benchmark|context|suggested|recommended|typical)[a-z_]*:"
flags: i
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---
