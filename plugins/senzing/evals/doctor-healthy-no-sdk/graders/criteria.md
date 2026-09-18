---
type: llm
focus: last_message
---

# Grader: doctor on a healthy host with no SDK

The eval sandbox is a Linux host with a working shell and network, and **no Senzing installed**.
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
