---
type: regex
pattern: "(can(no|')t|could ?n[o']t|unable to) (find|locate|read|open|access)\\b.{0,60}(crm|billing)"
flags: i
match: not_contains
target: last_message
---
