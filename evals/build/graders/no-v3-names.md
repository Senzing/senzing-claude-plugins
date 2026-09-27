---
type: regex
pattern: "\\bG2[A-Za-z_]*|g2engine|from senzing import G2"
match: not_contains
target: { source: file, path: senzing_search.py }
---
