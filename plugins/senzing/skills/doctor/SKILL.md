---
name: doctor
description: >
  Diagnose a Senzing environment before anything runs. Use automatically before the first Senzing
  operation of a session, and whenever an SDK script fails to import/init/connect, or the user
  asks "is my Senzing set up?", "check my Senzing environment", "why won't Senzing start". The
  shared up-front preflight for every skill: checks network/allowlist reachability
  (mcp.senzing.com + raw.githubusercontent.com), the host shell, the SDK install, engine
  configuration, database reachability, license, AND whether this host can serve a live interactive
  app or only a self-contained artifact — returning grounded, actionable fixes instead of a raw
  traceback — or wants Senzing installed or set up in the first place — e.g. "install Senzing",
  "set up Senzing on this machine", "get me started with Senzing".
allowed-tools: Bash, Read, mcp__plugin_senzing_senzing__*
---

# Senzing doctor — environment preflight

The most common friction in the generate-and-run model is a broken environment — a blocked
network, a missing SDK, or an **outcome the host can't actually deliver**. Diagnose it **once, up
front**, before the user hits a cryptic failure or invests in a long run. Grounded by the
**Senzing MCP server**. This is the shared preflight — other skills (`analyze`, `demo`, `report`,
`recipes`, `build`) run `doctor` first and act on its verdict, so the checks live here, not
duplicated in each skill.

**Inputs.** Takes no arguments — run the probe directly (any `$ARGUMENTS` are ignored). If invoked
because the user asked to *install* Senzing, skip straight to the install path below.

Run a minimal Bash probe and check, in order. The first two decide whether anything can work at
all and whether the intended result is even deliverable here, so they run **even when no local SDK
is present**:

1. **Grounding reachable (network / allowlist).** Probe `https://mcp.senzing.com/` **and**
   `https://raw.githubusercontent.com/` (e.g. `curl -fsSI`). `mcp.senzing.com` is the source of
   truth for *everything* (grounding, SDK downloads, sample data) — nothing works without it;
   `raw.githubusercontent.com` serves recipes and indexed code examples. Sandboxed hosts (Claude
   Desktop / Chat, Cowork) often block these — if either is unreachable, stop and ask the user to
   **allowlist that domain now**.
2. **Interactive-outcome capability.** Can this host serve a **live app the user drives** — a
   writable shell *plus* the ability to build/run a local server the user can reach at
   `localhost`? Claude Code on the user's machine can. A cloud sandbox (Claude Desktop / Chat,
   Cowork) can run the code and hand back a **self-contained interactive HTML5 (or PDF) artifact**,
   but **can't expose `localhost`** — so any outcome that must be a *live server* needs Claude
   Code. Determine which you are and report it, so skills that can end in an interactive app
   (`recipes`, `build`, `demo`) offer the artifact substitution or recommend Claude Code **before**
   a long run — never after.
3. **Host shell + writable workspace.** Can Bash create a workspace and write a file? A shell-less
   or reduced-tool surface (e.g. a spawned sub-agent with a trimmed tool set) can't run the SDK
   path — say so plainly.
4. **SDK importable** — can the target language import the Senzing SDK (`senzing` / `Sz*`)?
5. **Engine configuration** — is `SENZING_ENGINE_CONFIGURATION_JSON` (or the equivalent config)
   present and parseable?
6. **Database reachable** — does the configured repository (SQLite/PostgreSQL) accept a
   connection?
7. **License valid** — is the Senzing license present and unexpired?

Report the result as a **compact status table** — one row per check, `✅ / ⚠️ / ❌` with a
one-line status — so caller and user see viability at a glance. For any failure: map it through
`explain_error_code` / `sdk_guide` and return a **specific fix** (e.g. *"allowlist
`mcp.senzing.com`"*, or *"`SENZING_ENGINE_CONFIGURATION_JSON` points at a Postgres that isn't
accepting connections — start it / fix the host, here's the setting"*), never a raw stack trace.
Checks 1–3 are host-level and pass/fail independently of whether Senzing is installed; a green
host with no SDK is a valid state (the caller may only need grounding or code generation).

If there is **no** Senzing installed at all, say so plainly and offer `sdk_guide(topic="install")`
plus the `request-eval-license` path — do not attempt to run resolution.
