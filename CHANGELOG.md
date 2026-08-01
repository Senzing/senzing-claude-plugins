# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.32.4] - 2026-08-01

Version pin to Senzing MCP server **v1.32.4**.

**No plugin content changes.** v1.32.4 is the second #mcp-logging feedback batch:
three flag docs the extractor had been silently skipping (closing the why-family
`composite_members` gap and the `export` returns-axis blind spot in one fix),
SENZ7426 SUPPORTPATH guidance, a mapping_workflow field-count warning that fired
on every correct mapping, per-input profiler output paths, headerless-CSV
support, and `fetch-data` pruning of pages that vanish upstream.

**Tool surface is unchanged** — the release altered behaviour, response fields
and wording only; no tool added, removed or renamed, and no declared parameter
changed. The `build` skill and `senzing-grounder` agent need no updates.

## [1.32.3] - 2026-07-31

Version pin to Senzing MCP server **v1.32.3**.

**No plugin content changes.** v1.32.3 is a bugfix batch (eval-license
competitor-list change, `download_url` no longer inheriting the preview
`limit`, CORD cap/`offset` now explicit, `find_examples` elision made
self-describing, `generate_scaffold(initialize)` now returning config-seeding
code, `sdk_guide` language-alias normalization, V3 method-name recovery) plus
new `*_DEFAULT_FLAGS` production guidance and an expanded NETWORK ACCESS
section. It also grows the `find_examples` corpus from 37 to 42 indexed repos.

**Tool surface is unchanged** — the release added *response* fields
(`content_elided`, `source_download_url`, `download_url_max_records`), not
declared parameters, so the `build` skill and `senzing-grounder` agent need no
updates.

**Catches up two skipped pins.** This repo's `plugin.json` was at 1.31.0 while
this changelog's newest entry was 1.30.0, and the auto-sync PR for v1.32.2 was
never merged. Going straight to 1.32.3 rather than back-filling 1.31.0/1.32.0/
1.32.1/1.32.2 individually.

## [1.30.0] - 2026-07-27

Version pin to Senzing MCP server **v1.30.0**.

**No plugin content changes.** v1.30.0 changes served response-schema data
(7 schemas → 13; ~29 → 1,144 fields) and migrates the MCP SDK to rmcp 2.2,
but the tool surface is unchanged — every tool `inputSchema` was diffed
against production with zero drift across all 13 tools, so the `build` skill
and `senzing-grounder` agent need no updates.

## [1.29.0] - 2026-07-26

Lockstep with Senzing MCP server **v1.29.0**, which adds per-binding method
argument types to `get_sdk_reference`.

### Changed

- **`build` skill** — step 2 now requires confirming argument types for the
  target language before writing any method call, via
  `get_sdk_reference(topic='parameters', filter=<method>, language=<target>)`.
  The same method has a different name AND different argument types in each
  binding: Python `find_network_by_entity_id(entity_ids: List[int], …)`, Java
  `findNetwork(SzEntityIds, …)`, C# `FindNetwork(ISet<long>, …)`, Rust
  `find_network_by_entity_id(&[EntityId], …)`, TypeScript
  `findNetwork(number[], …)`. Carrying a call from one binding to another
  produces code the SDK rejects at runtime.
- **`senzing-grounder` agent** — new hard rule: answer argument-shape questions
  from `topic='parameters'` for the asked-about binding, never from another
  binding's docs.

## [1.28.8-1] - 2026-07-18

Plugin-only patch on MCP server v1.28.8 (no server change). Addresses Cowork-mode
plugin feedback from `#mcp-logging` (2026-07-18).

### Changed

- **Capability-gated delegation in the `analyze` flow.** The `analyze` skill no
  longer instructs unconditional fan-out to `field-mapper` sub-agents. Delegation
  is now an optimization gated on capability: parallelize across files only when a
  spawned sub-agent has a shell that can run the mapper scripts against the
  workspace; otherwise map sequentially in the current context. Completion never
  depends on delegation succeeding. Fixes a stall observed on hosts that give
  sub-agents a reduced tool set (e.g. Cowork, where the spawned mapper had no
  shell). The `field-mapper` agent's `Bash` grant — correct for Claude Code — is
  unchanged; the agent now states its required shell capability and reports (rather
  than stalls) when spawned without one. The `senzing-grounder` agent's delegation
  description is likewise reframed as optional: answer in the current context if a
  spawned sub-agent lacks the Senzing MCP tools.
- **Workspace portability.** `analyze` now verifies the shell can actually write
  the workspace and, if the default isn't writable, picks a writable directory and
  exports `SZ_WORKSPACE` (keeping the state-capture hook in lockstep) instead of
  assuming `~/sz-workspace` is visible to both the shell and the file tools.
- **Terminal deliverable is now a gated step, not advisory prose.** `analyze`,
  `demo`, and `report` mark the final Artifact/dashboard as required — the run is
  not complete until it ships, and it is produced without waiting to be asked.
  Fixes a case where a demo produced correct resolution but no artifact until the
  user explicitly requested one. `demo` is now explicit that the workflow is
  **load → analytics**: its final step requires BOTH a report (the before/after
  story with `why` explanations) and a visualization (a shareable dashboard).

## [1.28.8] - 2026-07-18

Initial public release.

### Added

- Initial repository scaffold: Claude Code plugin marketplace
  (`.claude-plugin/marketplace.json`) hosting the `senzing` plugin.
- `senzing` plugin built on the generate-and-run model over the hosted
  Senzing MCP server:
  - 6 skills: `analyze`, `build`, `demo`, `doctor`, `report`,
    `troubleshoot`.
  - 2 agents: `field-mapper`, `senzing-grounder`.
  - Hooks (`hooks/hooks.json`): `session_start.sh`,
    `check_provenance.sh`, and state-capture via `capture_state.sh`.
  - Hosted MCP server wiring in `plugins/senzing/.mcp.json`.
- CI workflow (`.github/workflows/ci.yml`) running the static check
  suite.
- `scripts/check.sh` static gate: JSON manifest parse, `bash -n` +
  shellcheck on hook scripts, SKILL/agent frontmatter validation, and
  `claude plugin validate --strict` on the marketplace and plugin.
- `evals/` placeholder with README.
- Dependabot config for the github-actions ecosystem (weekly, 21-day
  cooldown).
