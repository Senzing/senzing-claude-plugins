---
type: regex
pattern: "\\b(you|you'll|you will|we) (need|require|should (have|provision|use))\\b[^\\n.]{0,60}\\b\\d+[\\s-]*(cores?|vcpus?|cpus?|gb|tb|iops)\\b|\\b\\d+[\\s-]*(cores?|vcpus?|cpus?|gb|tb|iops)\\b[^\\n.]{0,50}\\b(should|would) be (a |an )?(sufficient|adequate|enough|comfortable|plenty|fine|reasonable|good|safe)\\b|\\b(budget|plan on|provision|start with|aim for)\\b[^\\n.]{0,40}\\b\\d+[\\s-]*(cores?|vcpus?|gb|tb|iops)\\b"
flags: i
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---
