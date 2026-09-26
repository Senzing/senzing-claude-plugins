# Senzing

**Resolve, dedupe and link your records with Senzing — on your machine, on your data.**

Senzing entity resolution finds, deduplicates, links, and resolves person and organization records
within and across data sources — building an identity-resolved graph with no training or
tuning. Senzing is used for master data management (MDM), customer 360, fraud detection,
compliance/KYC, sanctions and exclusion screening, supply chain/KYB, and identity intelligence.

## How it works — three actors, and only one of them sees your data

This plugin does not perform entity resolution itself, and neither does Senzing's MCP server.

| | What it does | What it sees |
|---|---|---|
| **Senzing MCP** (`mcp.senzing.com`) | supplies the knowledge — entity specification, SDK signatures, official install and mapping procedures, error catalog | the questions Claude asks it. **Never your records.** |
| **Claude** | does the work — writes Senzing SDK code from that grounding and runs it | your data, on your machine |
| **Your Senzing** | resolves the records | your data, on your machine |

So every Senzing fact comes from Senzing's own published knowledge rather than model training
data, and where you want a real result the code runs **on your machine against your own installed
Senzing**. Your records are never sent to Senzing.

## Commands

| Command | What it does |
|---|---|
| `/senzing:analyze <files>` | Resolve and dedupe your data — who is who across your sources — in a throwaway scratch workspace, then report. Your existing Senzing is left untouched unless you ask to load into it. |
| `/senzing:ask <question>` | Answer a Senzing question — attributes, SDK signatures, config, architecture, deployment, pricing and ROI — grounded with source links, never from training data. Answers only; it writes nothing and runs nothing. |
| `/senzing:demo` | See entity resolution work on sample data. If Senzing isn't installed, it helps you install rather than faking a result. |
| `/senzing:build` | Generate correct, compilable Senzing SDK code (Python, Java, C#, …) for your app, with source attribution — and optionally run it. |
| `/senzing:report` | Explore an already-loaded Senzing: why records resolved, your biggest entities, dashboards, and match quality. |
| `/senzing:recipes [recipe]` | Cook a guided use-case recipe from the [Senzing Cookbook](https://github.com/senzing/recipes) — fraud, customer 360, exclusion screening — standing up a working solution against your own Senzing. |
| `/senzing:poc-planner [use case]` | Plan a Senzing proof of concept with you: which data, what hardware, who runs it, what "success" means. Proposes no targets or timelines of its own. |
| `/senzing:troubleshoot` | Explain a Senzing error and how to fix it — paste an error code or a failing trace. |
| `/senzing:install` | Install and set up Senzing on this machine — SDK, database and license — using the official platform-specific steps, then verifies with `doctor`. |
| `/senzing:doctor` | Diagnose your Senzing setup (SDK, database, license, config) and give actionable fixes. |

You don't have to remember the commands — just say what you want ("dedupe my customer files", "why
did these two records match?", "what does error 0033E mean?", "add Senzing search to my Python
app") and the right one kicks in.

### Three things to try first

1. `/senzing:demo` — see entity resolution run end to end on real sample data, no setup decisions.
2. `dedupe my customer files` (or `/senzing:analyze data/*.csv`) — resolve your own data in a
   throwaway scratch repository, then get a report of who is who.
3. `what Senzing attributes should I map a phone number to?` (or `/senzing:ask …`) — a grounded
   answer with source links.

## Requirements

- **Claude Code 2.1.143 or newer.**
- To run entity resolution (`analyze`, `demo`, `report`, `recipes`): **your own installed, licensed
  Senzing SDK.** `analyze` and `demo` create a throwaway scratch database automatically; `report`
  runs over a Senzing you have already loaded.
- Everything else — grounded answers, code generation, troubleshooting, POC planning and data
  mapping — needs no Senzing at all.

`/senzing:doctor` checks your setup and says what is missing; `/senzing:install` sets one up.

## Install

```
/plugin marketplace add Senzing/senzing-claude-plugins
/plugin install senzing@senzing
```

Restart Claude Code. No binary is downloaded — the Senzing knowledge is served from the hosted
Senzing MCP.

## Data

What the plugin sends, and where:

- **To `https://mcp.senzing.com/mcp`** (the hosted Senzing MCP, over HTTPS): the questions Claude
  asks it, and the arguments of each call — a topic, an error code, a programming language, the
  **source field names** of a file you are mapping, and your mapping choices. When you map a *code*
  field (a document-type or status column, say), the distinct code values in it are enumerated and
  sent, because the server validates that every one of them is accounted for. **Tool calls and
  their parameters may be logged**, as its privacy notice states. The server's own instructions
  direct the model not to send personal data, credentials or sensitive values; the same goes for
  you — don't paste them into a prompt.
- **Never sent:** the contents of your records — the names, addresses, identifiers and rows
  themselves. Mapping, loading and resolution run locally, and file paths reach the server as
  labels it never opens.
- **To `raw.githubusercontent.com`**: fetching indexed public code examples and cookbook recipes.
- **On your machine only:** the generated SDK code, the scratch database, and every resolved
  result.

Senzing's privacy notice: <https://senzing.com/privacy-notice/>

## Troubleshooting

Something failing? Run `/senzing:doctor` first — it checks the SDK, database, license and config
and gives actionable fixes. For a specific error, `/senzing:troubleshoot <error code or trace>`.

## Support

- **Email:** <support@senzing.com>
- **Issues and feature requests:** <https://github.com/Senzing/senzing-claude-plugins/issues>
- **Security concerns:** email <support@senzing.com> with "security" in the subject line.
- In-session: the plugin's built-in `submit_feedback` sends a note to the maintainers.

## What to expect

- **Grounded, not guessed** — every Senzing fact and every line of SDK code comes from official
  Senzing sources, never the model's memory.
- **Your data stays private** — resolution runs locally against your own Senzing; records are never
  sent off your machine.
- **No fake results** — if Senzing isn't available it says so and helps you install; it never
  invents match scores or merges.
- **Your existing Senzing is safe** — analysis runs in a throwaway scratch repository; loading into
  your real instance is an explicit choice, and it confirms first.

## License

Proprietary — see [LICENSE](./LICENSE). Copyright © Senzing, Inc. All rights reserved.
