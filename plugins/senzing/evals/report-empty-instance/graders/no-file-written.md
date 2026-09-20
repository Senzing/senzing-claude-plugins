---
type: tool_used
tool: Write
input_match: '"file_path"\s*:\s*"(?![^"]*\.senzing-doctor-probe\.tmp")'
min: 0
max: 0
---

<!--
The `input_match` excludes exactly ONE path and nothing else: `.senzing-doctor-probe.tmp`, the
workspace-writability probe `doctor` is REQUIRED to make with the `Write` tool
(`plugins/senzing/skills/doctor/SKILL.md`, check 2's probe budget). This skill runs `doctor`
first, so an unqualified `max: 0` demands `doctor` and forbids the tool `doctor` must use — the
contradiction that no model could pass in `recipes-named`, as CI observed. An ephemeral probe deleted by the next
command is not a deliverable; anything else written is, and still fails this grader. The pinned
filename and this exclusion point at each other on purpose. See
`plugins/senzing/evals/recipes-named/graders/no-file-written.md` for the full derivation.
-->
