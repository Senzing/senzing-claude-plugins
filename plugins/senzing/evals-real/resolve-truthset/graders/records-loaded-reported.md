---
type: regex
# "A record count was reported at all" — NOT which one. Same reasoning as
# entity-count-reported.md: the literal that used to live here was both a frozen
# engine number and a number the agent could read out of this file. The equality
# is asserted at run time against the engine by verify_truthset.py's
# `reported_matches_engine` check.
pattern: "\\b\\d[\\d,]*\\b[^\\n]{0,40}record|record\\w*[^\\n]{0,40}\\b\\d[\\d,]*\\b"
flags: i
target: last_message
---
