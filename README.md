# senzing-claude-plugins

**Claude Code plugins that turn Senzing knowledge into outcomes.**

The [Senzing MCP server](https://mcp.senzing.com) is a grounding brain: it knows what's true
about Senzing (Entity Spec attributes, real V4 SDK signatures, error codes, indexed code
snippets, sample data) so an LLM never confabulates Senzing APIs. These plugins add the *hands,
front doors, and guardrails* around it — for Claude Code specifically.

> This repo is **thin config** — skills, hooks, and a marketplace manifest that point at the hosted
> Senzing MCP (`mcp.senzing.com`); it bundles no Senzing code. Because the MCP speaks the open MCP
> protocol, the same grounding is reachable from any MCP client — these plugins add the Claude Code
> experience on top.

### Relationship to `senzing-mcp-skill`

Senzing already ships [`senzing-mcp-skill`](https://github.com/Senzing/senzing-mcp-skill) — a
single Claude skill that grounds an agent against the hosted MCP (documentation only; it does not
run code). This repo is the next tier up. Three ways to consume Senzing from an agent, in
increasing capability:

1. `claude mcp add --transport http senzing https://mcp.senzing.com/mcp` — raw MCP, any client.
2. **`senzing-mcp-skill`** — grounding skill, Claude Code (exists).
3. **these plugins** — grounding **+ hands (Bash) + orchestration + rendered deliverables + gates**.

The two coexist: the skill stays the lightweight option; the plugin is the full experience. The
plugin's base grounding skill evolves from `senzing-mcp-skill` rather than reinventing it.

---

## The one idea: the agent already has hands

There is no bespoke "runtime connector." Claude Code ships the only runtime we need — the
**Bash** tool — and the customer already has the only Senzing that matters: their own installed,
licensed instance and database. So "run Senzing" is a loop the agent performs, grounded at every
step so the code that runs is version-correct rather than guessed:

```
  MCP grounds the facts  →  Claude writes REAL SDK code  →  Bash runs it on the
  customer's box, against their Senzing + DB  →  Claude reads the output
  →  Claude renders the report / dashboard / answer.
```

Everything good falls out of this for free: **PII never leaves the machine** (the code runs
where the data lives), **licensing dissolves** (the customer's own Senzing license covers running
their own SDK — we redistribute nothing that links `libSz`), and results are **always
version-correct**.

---

## Version

**Verified against Senzing MCP server v1.28.8 (2026-07).** The plugin `version` tracks the MCP
**server** version it was validated against — not the Senzing data version. The data version
(`4.3.3`) is carried separately in `plugin.json` `metadata`. Bump the plugin only when the MCP
**tool surface** changes (a new/renamed/removed tool or changed args), not on data refreshes.
Skills call `get_capabilities` first, so a plugin slightly behind the server still degrades
gracefully.

## Install

Grounding is hosted, so install is instant — no binary.

```
# GitHub-direct (relative paths resolve; simplest)
/plugin marketplace add Senzing/senzing-claude-plugins
/plugin install senzing@senzing

# — or the branded catalog URL —
/plugin marketplace add https://mcp.senzing.com/plugin
/plugin install senzing@senzing
```

> The branded URL serves only `marketplace.json`, so its plugin `source`s point back at this
> repo via a `github` source (a URL marketplace can't use relative paths).

### Compatibility

The skills and agents pre-approve the bundled MCP via the `allowed-tools` wildcard
`mcp__plugin_senzing_senzing__*`. The space/comma-separated `allowed-tools` list syntax is
documented, but the `mcp__…__*` wildcard match for bundled-plugin MCP tools should be confirmed on
a real install — plugin-name-prefixed MCP tool matching (and any hyphenated plugin prefix) needs
Claude Code ≥ 2.1.195.

---

## What's in here

This repo is the public marketplace and its one public plugin, **`senzing`** — for evaluators,
developers, data engineers, and analysts. Hosted grounding, generate-and-run, rendered deliverables.

| Front door | What it does |
|---|---|
| `/senzing:analyze <files>` | Map → (confirm) load → resolve → report over your own data. The flagship loop, with a validation barrier and a checkpoint before the first DB write. |
| `/senzing:build` | Generate real SDK code → write to files with source-URL provenance → optionally run it. |
| `/senzing:troubleshoot` | Auto-fires on a pasted error → cause + fix (error code → docs → examples). |
| `/senzing:demo` | Sample data → load → resolve → before/after render. Honest install fallback (never simulates). |
| `/senzing:report` | why / how / SQL → a shareable dashboard over already-loaded data. |
| `/senzing:doctor` | Diagnoses a broken environment (SDK / DB / license / config) before a cryptic failure. |

Sub-agents: **`senzing-grounder`** (never answer a Senzing question from training data) and
**`field-mapper`** (map many files in parallel, then a barrier).

---

## Why skills (and not 31 wrappers)

The MCP already exposes 31 reusable prompts, and they stay the explicit-invoke catalog
(`/mcp__senzing__map-data-source`, …). A skill in this repo exists **only** where it does
something a static prompt can't: auto-activate on intent, orchestrate a multi-step loop with
barriers, **run generated code via Bash**, render a deliverable, or enforce a gate. We do not
mint one skill per prompt.

---

## Portability — what reaches whom

| Layer | Open standard? | Reaches |
|---|---|---|
| The Senzing MCP (tools, 31 prompts, resources) | ✅ MCP spec | **Any** MCP client / LLM, via the hosted endpoint |
| The generate-and-run loop | ⚠️ needs a shell/exec tool | Any agentic client with code execution |
| These plugins (skills, hooks, marketplace) | ❌ Claude Code proprietary | Claude Code only |

In short: the Senzing knowledge is portable (any MCP client can reach the hosted MCP); the
`/senzing:*` commands, orchestration, and rendering are the Claude Code experience this plugin adds.

---

## Guardrails (invariants that hold everywhere)

1. **No fabrication** — every Senzing fact routes through the MCP; the `senzing-grounder` agent
   enforces it.
2. **No PII off the machine** — code runs locally; real records are never sent to a hosted tool.
3. **Provenance intact** — generated code keeps its source-URL comments.
4. **No simulated resolution** — no running Senzing means we say so and pivot to install, never
   fake scores or merges.
5. **Reproducible** — releases pin a Senzing data version, never `current`.

---

## Repo structure

```
Senzing/senzing-claude-plugins/          (this repo — PUBLIC)
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── senzing/
│       ├── .claude-plugin/plugin.json
│       ├── .mcp.json               # points at https://mcp.senzing.com/mcp
│       ├── skills/                 # analyze · build · troubleshoot · demo · report · doctor
│       ├── agents/                 # senzing-grounder · field-mapper
│       └── hooks/                  # state-capture · doctor preflight
└── README.md
```

The plugin bundles no Senzing code — it reaches Senzing's knowledge entirely through the hosted
MCP at `mcp.senzing.com`.

---

## Feedback

Found a problem or have a request? Open an issue in this repo, or use the plugin's built-in
`submit_feedback` path.
