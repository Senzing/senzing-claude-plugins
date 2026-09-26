---
type: tool_used
tool: mcp__plugin_senzing_senzing__sdk_guide
input_match: '"topic"\s*:\s*"install"'
---

# Grader: the install steps came from the MCP, not from memory

`criteria.md` tells the judge, in as many words, "the `install-steps-from-mcp` grader beside this
file asserts the call happened" — and instructs it NOT to fail a run for being unable to see the
`sdk_guide` result. That grader did not exist. The name was left behind when the old
`install-invoked` assertion was rewritten into an EULA check, so for the whole life of that
instruction the judge was being told to defer to an assertion nothing was making. A judge told to
defer to a check that does not exist is worse than no check: it suppresses the one grader that
was still looking.

This is that assertion, and it is also the standing rule the grounding contract states directly:
**any skill that installs needs `sdk_guide`.** Install commands are platform-specific, they change
between releases, and a model's memory of them is exactly the training-data recall the MCP exists
to replace.

Safe on BOTH routes this case allows. `install-invoked`'s write-up argues a run may legitimately
take the short path and hand the steps over without invoking the `install` skill — but that path
runs through `doctor`, whose Step 0 makes **two deliberate `sdk_guide(topic="install")` calls**
before any decision is reached (`skills/doctor/SKILL.md:83-95`), and `doctor-invoked` already
gates that `doctor` ran. So the call is reached whichever way the run goes, and this grader adds
no new route requirement — it only asserts the grounding that both routes already perform.

Provably able to fail: a run that answers the install question from the model's own knowledge of
apt/brew commands never makes the call, which is the failure the case exists to catch.
