# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
