---
type: regex
pattern: '\b(?:who|people|team|engineers?|staff|skill\w*|runs?|running)\b[^\n]{0,200}\?|\?[^\n]{0,200}\b(?:who|people|team|engineers?|staff|skill\w*)\b'
flags: i
target: last_message
---

# Grader: the people are ASKED about, as a question

The other half: who runs it, their skills, their time. A `?` naming people/team/skills/who. Measured: 34 of 34 real arms hit.
