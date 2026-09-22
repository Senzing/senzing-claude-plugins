---
type: llm
focus: last_message
---

# Grader: doctor on a healthy host with no SDK

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool calls and forbidden shapes. Absent a visible violation, vote PASS.

The eval sandbox has a working shell and network and **no Senzing installed**. Its OS is
**whatever `uname` reports** — today a macOS (Darwin/arm64) GitHub runner, not Linux. Judge every
install-location claim against the OS the run actually observed. This rubric previously asserted
"a Linux host"; the report correctly said macOS/Homebrew and the judge scored that as the rubric's
own named failure ("inferred from a directory for a different OS"), failing 100% of runs on a
premise the rubric itself got wrong.
Nothing on it is broken. A correct report MUST:

- Be the `doctor` skill's per-check report (one row per check with exactly one status glyph),
  and it MUST have run real probes — the platform (`uname`) and the platform's own install
  location — before pronouncing on the SDK. The verdict must name what it checked and where.
- Mark the SDK/install row **➖ "not installed"** (not applicable), and cascade every downstream
  row that depends on it (loader path, import, engine self-test, license) to **➖** as well.
- Contain **no ❌ anywhere**: ❌ is reserved for something that is present AND misbehaving AND
  user-fixable. "Not installed" is not a failure; a report that renders it as ❌, or that says the
  machine "has no Senzing runtime" / "is broken" as a failure verdict, FAILS.
- Frame the result as a **healthy host** that can still do grounding and code generation, and
  **offer install** — the `install` skill or `sdk_guide(topic="install", platform=…)` — as the
  next step. Sandbox-only limits (e.g. "artifact only, cannot expose localhost") are ⚠️ at most.

FAIL if any row shows ❌; if the SDK absence is stated without a probe of the platform-correct
location (e.g. inferred from a directory for a different OS, or from memory); if downstream checks
repeat the absence as additional failures; if it asks for a license; or if install is not offered.

<!--
DELETED GRADER: `install-offered.md` (`type: regex`, `pattern: "install"`, `target: last_message`).

It could not fail. `not-installed-glyph-present.md` beside it REQUIRES the same message to carry
the ➖ "not installed" row, and this rubric requires the SDK row to read "not installed" — so the
substring `install` is structurally guaranteed to be present before the offer is ever considered.
It passed on the word inside the thing it was supposed to be checking the response TO. It also
passed on "Senzing is not installed and I cannot install it", the exact opposite of the
obligation.

Not replaced, because the obligation is not a word. "Offer install as the next step" is a
judgement about what the report proposes, and the last bullet plus the final FAIL clause of this
rubric already make it — the llm grader can see the offer; a regex can only see the letters.
Deleting a grader that cannot fail costs no coverage. See `plugins/senzing/evals/REVIEW-LOOP.md`.
-->
