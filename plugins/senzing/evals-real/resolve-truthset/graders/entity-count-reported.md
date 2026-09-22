---
type: regex
# "An entity count was reported at all" — NOT which one.
#
# This used to be a hard-coded count. A literal here is wrong twice over: it
# freezes the ENGINE's behavior into the PLUGIN's contract (an engine, config or
# tuning change legitimately moves it), and it is not an independent oracle,
# because the eval sandbox grants Bash and Grep and this file is in the
# repository the agent can read. The number the run reported is instead compared
# against what the engine actually holds, at run time, by verify_truthset.py's
# `reported_matches_engine` check.
pattern: "\\b\\d[\\d,]*\\b[^\\n]{0,40}entit|entit\\w*[^\\n]{0,40}\\b\\d[\\d,]*\\b"
flags: i
target: last_message
---
