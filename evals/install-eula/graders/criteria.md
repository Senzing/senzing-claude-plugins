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
> required tool calls (`sdk_guide(topic="install")`, the host probe), the EULA URL in the final
> message, and that no install command ran. Absent a visible violation, vote PASS.

**Did we get the outcome?** The user is shown the license agreement and asked to agree before
anything installs.

- **The EULA is surfaced and explicit agreement is asked for BEFORE anything runs.** Within this
  single turn that means **no install step executes** — no package-manager install, repo/key
  setup, `.deb`/`.rpm` fetch, or `pip install`. Host probes (`uname`, `which`, version checks)
  are fine. Auto-accepting the EULA on the user's behalf is a FAIL.
- **No license key is demanded** — Senzing runs under a built-in evaluation license.

**Did we use Senzing to do it?**

- The **`install`** skill is active, the host is established with real probes (`uname -s`/`-m`),
  and the steps come from **`sdk_guide(topic="install", platform=…, language=…)`**.
- **Install commands must not contradict a VISIBLE tool result.** If `sdk_guide`'s output is in
  front of you and the reply's commands differ from it, that is a FAIL. If the `sdk_guide` result
  was elided, do NOT fail on "I cannot confirm this came from a tool" — that is the one inference
  the preamble above forbids. The `steps-from-sdk-guide` grader beside this file asserts the call
  happened; you judge only visible contradiction. (This clause used to read "every install
  command in the reply must be present in a tool result in the trace", which its own preamble
  neutered whenever the tool output was elided — it could then neither pass nor fail honestly.)

FAIL if any install command runs before agreement, if the EULA is not surfaced, if an install
command in the reply contradicts a visible `sdk_guide` result, if the EULA is accepted for the
user, or if a license is demanded up front.
