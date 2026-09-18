---
type: regex
pattern: "(precision|recall|f1|accuracy|match rate|compression|throughput|latency)\\s*(≥|>=|>|of at least|at least|of|target(ed)?( of)?|:)\\s*\\d+(\\.\\d+)?\\s*%|\\d+(\\.\\d+)?\\s*%\\s*(precision|recall|f1|accuracy|match rate)|\\b(precision|recall|f1|accuracy|match rate|compression)\\s*(≥|>=|>|above|below|under|over|of at least|at least)\\s*\\d+(\\.\\d+)?\\b"
flags: i
match: not_contains
target: { source: file, path: senzing-poc-plan.md }
---
