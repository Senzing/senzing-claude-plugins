# senzing-claude-plugins

**Bring Senzing entity resolution into Claude Code.** Map and resolve your data, build Senzing SDK
integrations, troubleshoot errors, and report on results — grounded in official Senzing knowledge so
the code is correct, and run against your own Senzing so your data stays private.

## What it does

Installing the `senzing` plugin gives you a set of `/senzing:*` commands. Each one grounds every
Senzing fact in the official Senzing knowledge base (so nothing is made up), and — where you want a
real result — writes Senzing SDK code and runs it **on your machine against your own installed
Senzing**. Your records never leave your machine.

## Requirements

- **Claude Code 2.1.143 or newer.**
- To run entity resolution (`analyze`, `demo`, `report`): **your own installed, licensed Senzing
  SDK.** `analyze` and `demo` spin up a throwaway scratch database automatically; `report` runs
  over a Senzing you've already loaded. Grounding, code generation, troubleshooting, and data
  mapping need no Senzing at all — and `/senzing:doctor` checks your setup and says what's missing.

## Install

```
/plugin marketplace add Senzing/senzing-claude-plugins
/plugin install senzing@senzing
```

Restart Claude Code, then use any of the commands below. No binary is downloaded — the Senzing
knowledge is served from the hosted Senzing MCP.

## Commands

| Command | What it does |
|---|---|
| `/senzing:analyze <files>` | Resolve and dedupe your data — who is who across your sources — in a throwaway scratch workspace, then report. Your existing Senzing is left untouched unless you ask to load into it. |
| `/senzing:build` | Generate correct, compilable Senzing SDK code (Python, Java, C#, …) for your app, with source attribution — and optionally run it. |
| `/senzing:troubleshoot` | Explain a Senzing error and how to fix it — paste an error code or a failing trace. |
| `/senzing:demo` | See entity resolution work on sample data. If Senzing isn't installed, it helps you install rather than faking a result. |
| `/senzing:report` | Explore an already-loaded Senzing: why records resolved, your biggest entities, dashboards, and match quality. |
| `/senzing:doctor` | Diagnose your Senzing setup (SDK, database, license, config) and give actionable fixes. |

You don't have to remember the commands — just say what you want ("dedupe my customer files", "why
did these two records match?", "what does error 0033E mean?", "add Senzing search to my Python
app") and the right one kicks in.

## What to expect

- **Grounded, not guessed** — every Senzing fact and every line of SDK code comes from official
  Senzing sources, never the model's memory.
- **Your data stays private** — resolution runs locally against your own Senzing; records are never
  sent off your machine.
- **No fake results** — if Senzing isn't available it says so and helps you install; it never
  invents match scores or merges.
- **Your existing Senzing is safe** — analysis runs in a throwaway scratch repository; loading into
  your real instance is an explicit choice, and it confirms first.

## Feedback

Found a problem or have a request? Open an issue in this repo, or use the plugin's built-in
`submit_feedback`.
