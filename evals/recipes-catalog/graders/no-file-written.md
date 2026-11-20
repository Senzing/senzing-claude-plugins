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
`evals/recipes-named/graders/no-file-written.md` for the full derivation.
-->

Why `tool: Write` and not Bash: the skill copies the recipe's bundled ingredient files into the
workspace with a plain `cp`, and `doctor` probes writability, so a Bash-level file-write check
would forbid steps the skill requires. (Before the cookbook was bundled the skill instead
REQUIRED `curl -o` for the catalog and recipe; the reasoning is the same.) What this grader
forbids is an AUTHORED file — a plan, a mapping, a report — which the model can only produce with `Write`.
The case's `expected_outcome` says the same (review on 7785bfb).
