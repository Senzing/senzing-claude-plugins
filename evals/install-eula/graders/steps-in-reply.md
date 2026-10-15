---
type: regex
pattern: '```'
target: last_message
---

# Grader: the reply hands the user the official install commands, in a code block

`install/SKILL.md` ("If it cannot be installed here") fixes the blocker reply's shape: host, blocker,
**the recommended path's official commands verbatim in a fenced code block**, the EULA, one question.
Every reply in this case owes the commands — the user is being asked to agree to an install, and on a
Python-on-macOS host the Docker path's commands are what they would run.

PR #73 (v1.39.0) eval, run 0: the reply probed for Docker, found none, and ended on "install Docker
yourself, or use a different language?" with no commands. `criteria` failed it 3 of 3, citing the
skill's own "a blocker does not shorten the turn" rule. Three earlier CI runs of the same no-commands
shape (10-11 run 1, 10-14 run 1, 10-15 11:38 run 1) had passed the judge — the defect was there, the
judge just did not always see it. This makes the obligation deterministic.

A fence is the discriminator because the skill now requires one; inline backticks around a single
command name (`brew`, `docker`) are not the commands.

Fixtures: `pattern-fixtures/steps-in-reply.yaml`.
