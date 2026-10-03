---
type: regex
pattern: '\bdata\b[^\n]{0,200}\?|\?[^\n]{0,200}\bdata\b'
flags: i
target: last_message
---

# Grader: the data is ASKED about, as a question

Replaces the "asks about the data ... as questions" half of `criteria`. A `?` naming the data, in either order within the line. Measured: 34 of 34 real arms hit. A declarative plan with no  does not.
