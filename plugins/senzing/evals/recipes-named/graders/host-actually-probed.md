---
type: tool_used
tool: Bash
input_match: 'uname|dpkg|rpm|/opt/senzing|libSz|brew|scoop|SENZING_ROOT|senzing'
---

# Grader: doctor's absence-of-SDK finding came from a real probe

Mirrors `demo-no-simulation/graders/host-actually-probed.md`: a `Skill` call naming `doctor`
proves the skill activated, not that it checked anything. This grader requires an actual `Bash`
probe of the host, so a run that merely announces "no Senzing is installed" without running a
command fails it — proven offline against a synthetic `{"command": "echo checking your system"}`
call, which does not match.
