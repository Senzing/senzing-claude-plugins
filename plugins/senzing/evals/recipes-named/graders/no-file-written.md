---
type: tool_used
tool: Write
input_match: '"file_path"\s*:\s*"(?![^"]*\.senzing-doctor-probe\.tmp")'
min: 0
max: 0
---

# Grader: the run wrote no deliverable file

This case asserts the run produces an answer, not an artifact — `expected_outcome` says it
"never starts `mapping_workflow`, writes a file, or presents any match score".

The `input_match` excludes exactly ONE path, `.senzing-doctor-probe.tmp`, and nothing else. That
is not a loosened bar; it is the only way this assertion can measure the thing it states. The same
case's `doctor-invoked` grader REQUIRES the `doctor` skill to run, and `doctor` is required to
probe workspace writability with the `Write` tool —
`plugins/senzing/skills/doctor/SKILL.md`, check 2's probe budget: "exactly one `Write` of a small
file into the current project directory and one `Read` back", named `.senzing-doctor-probe.tmp`
and deleted immediately. An unqualified `max: 0` therefore demanded `doctor` and forbade the tool
`doctor` must use, and no model could pass it: CI observed exactly that, `Write` 1x of
`.doctor-probe.tmp` removed by the very next Bash call, failing 2 of 2 runs.

An ephemeral probe deleted by the next command is not a deliverable. Anything else written is.

The exclusion and the pinned filename point at each other on purpose — change one and find the
other. Proven offline against the harness's own JS regex semantics: the probe path does not match
(in any directory), while a deliverable (`customer-360-plan.md`), the old unpinned probe name
(`.doctor-probe.tmp`) and a near-miss (`.senzing-doctor-probe.tmp.bak`) all do.
