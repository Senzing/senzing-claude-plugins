# Senzing

**Entity resolution: point Claude at your data, it runs Senzing on your machine, and you have results today.**

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

## Where it runs

| Surface | What you get |
|---|---|
| **Claude Code** | Full capability. Every command works. |
| **Chat / Cowork** | Full capability, with one exception: a report can be a dashboard artifact or a file, but not a **live interactive service** — SDK code that serves a web UI has nowhere to serve it. |
| **Claude web** | **Informational only.** Nothing executes, in a container or on your machine. |

On Claude web what still works is the half that needs no machine at all —
`/senzing:ask`, `/senzing:troubleshoot` and `/senzing:poc-planner`, grounded in the hosted Senzing
MCP. The commands that map, load, resolve or report have nothing to run on.

Worth knowing before you install: the plugin ships no executables, so **nothing blocks the
install anywhere**. On Claude web you get a clean install, working answers, and then silence from
the commands that need a machine — there is no error message explaining why.

## Requirements

- **Claude Code 2.1.143 or newer.**
- To run entity resolution (`analyze`, `demo`, `report`, `recipes`): **your own installed, licensed
  Senzing SDK.** `analyze` and `demo` create a throwaway scratch database automatically; `report`
  runs over a Senzing you have already loaded.
- Everything else — grounded answers, code generation, troubleshooting, POC planning and data
  mapping — needs no Senzing at all.

`/senzing:doctor` checks your setup and says what is missing; `/senzing:install` sets one up.

## The Senzing connector

The knowledge this plugin runs on comes from the **Senzing MCP server**, which is listed in the
**[Claude Connectors Directory](https://claude.ai/directory/senzing)**. The
plugin bundles that connector, so installing the plugin is enough in Claude Code; you do not need
to add it separately. Its endpoint, if you ever want to add it by hand, is
`https://mcp.senzing.com/mcp` (no authentication). Setup notes for other MCP clients:
<https://mcp.senzing.com/docs>.

**On Chat and Cowork, allowlist the domain.** Those surfaces restrict outbound network access, and
the Senzing knowledge is served over HTTPS — so for the full experience, allow:

| Domain | Needed for |
|---|---|
| `mcp.senzing.com` | everything the server hosts itself — Senzing knowledge, SDK package downloads, sample-data downloads, workflow resources |
| `raw.githubusercontent.com` | indexed code examples and cookbook recipes, which are returned as raw GitHub URLs |

Without `mcp.senzing.com` the plugin cannot ground anything and will say so rather than answer
from memory. Without `raw.githubusercontent.com` you still get answers, but example code has to
come the long way round.

## Install

```
/plugin marketplace add Senzing/senzing-claude-plugins
/plugin install senzing@senzing
```

Restart Claude Code. No binary is downloaded — the Senzing knowledge is served from the hosted
Senzing MCP.

## Data

- **Your records stay on your machine.** Mapping, loading and resolution all run locally against
  your own Senzing. File paths reach the MCP as labels it never opens.
- **The plugin calls one remote service**, the hosted Senzing MCP at `https://mcp.senzing.com/mcp`,
  for Senzing knowledge. It sends the questions Claude asks and their arguments — which, when you
  are mapping, include your source field names and mapping choices. What is logged and retained is
  covered by the **[Senzing MCP privacy policy](https://mcp.senzing.com/privacy)**.
- **It also fetches public content** from `raw.githubusercontent.com`: indexed code examples and
  cookbook recipes.

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
