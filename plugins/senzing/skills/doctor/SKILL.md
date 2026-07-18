---
name: doctor
description: >
  Diagnose a Senzing environment before anything runs. Use automatically before the first Senzing
  operation of a session, and whenever an SDK script fails to import/init/connect, or the user
  asks "is my Senzing set up?", "check my Senzing environment", "why won't Senzing start". Checks
  the SDK install, engine configuration, database reachability, and license — and returns
  grounded, actionable fixes instead of a raw traceback — or wants Senzing installed or set up in
  the first place — e.g. "install Senzing", "set up Senzing on this machine", "get me started
  with Senzing".
allowed-tools: Bash, Read, mcp__plugin_senzing_senzing__*
---

# Senzing doctor — preflight diagnosis

The most common friction in the generate-and-run model is a broken environment. Diagnose it
before the user hits a cryptic failure. Grounded by the **Senzing MCP server**.

**Inputs.** Takes no arguments — run the probe directly (any `$ARGUMENTS` are ignored). If invoked
because the user asked to *install* Senzing, skip straight to the install path below.

Run a minimal probe with Bash and check, in order:

1. **SDK importable** — can the target language import the Senzing SDK (`senzing` / `Sz*`)?
2. **Engine configuration** — is `SENZING_ENGINE_CONFIGURATION_JSON` (or the equivalent config)
   present and parseable?
3. **Database reachable** — does the configured repository (SQLite/PostgreSQL) accept a
   connection?
4. **License valid** — is the Senzing license present and unexpired?

For any failure: map it through `explain_error_code` / `sdk_guide` and return a **specific fix**
(e.g. *"`SENZING_ENGINE_CONFIGURATION_JSON` points at a Postgres that isn't accepting connections
— start it / fix the host, here's the setting"*), never a stack trace. If everything is green,
stay silent and let the calling skill proceed.

If there is **no** Senzing installed at all, say so plainly and offer `sdk_guide(topic="install")`
plus the `request-eval-license` path — do not attempt to run resolution.
