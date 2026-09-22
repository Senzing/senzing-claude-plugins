---
description: Bash can write to the eval scaffold filesystem (harness canary, not a skill test).
tags: [canary]
expected_outcome: >
  The single Bash command runs and its OUTPUT contains SANDBOXWRITE_OK, proving the sandbox
  grants Bash filesystem writes in the scaffold cwd. The token is assembled at runtime so it
  cannot appear in the echoed command text — a grader that matched the command would be blind.
max_turns: 4
timeout_seconds: 120
allowed_tools: [Bash]
---

Run exactly this Bash command and report its full output verbatim, nothing else:

`H=SANDBOX; printf 'WRITE_OK' > ./.sandbox-canary.tmp && printf '%s%s\n' "$H" "$(cat ./.sandbox-canary.tmp)" && rm ./.sandbox-canary.tmp; echo TMPDIR=$TMPDIR; pwd -P`
