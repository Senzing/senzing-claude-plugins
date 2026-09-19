---
type: llm
focus: trace
---

# Grader: install surfaces the EULA first

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool calls, files and forbidden tools. Absent a visible violation, vote PASS.

A correct response MUST:

- Activate the **`install`** skill, establish the host with real probes (`uname -s`/`-m`), and
  fetch the official steps with **`sdk_guide(topic="install", platform=…, language=…)`**.
- **Surface the license agreement (EULA) and ask for explicit agreement BEFORE running anything.**
  Within this single turn that means **no install step executes** — no package-manager install,
  repo/key setup, `.deb`/`.rpm` fetch, or `pip install`. Host probes (`uname`, `which`, version
  checks) are fine. Auto-accepting the EULA on the user's behalf is a FAIL.
- Show install commands **only as returned by `sdk_guide`**: every install command in the reply
  must be present in a tool result in the trace. A command written from memory is a FAIL even if
  it is correct.
- Not ask the user for a license key — Senzing runs under a built-in evaluation license.

FAIL if any install command runs before agreement, if the EULA is not surfaced, if any install
command in the reply is absent from every tool result, if the EULA is accepted for the user, or
if a license is demanded up front.
