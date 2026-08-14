# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.32.9-3] - 2026-08-14

Plugin-only patch on MCP server v1.32.9 (no server change).

### Changed

- **Centralized the environment preflight in `doctor`, run up front by every skill.** The
  reachability + capability checks that only `recipes` had (hand-rolled inline) now live in
  `doctor`, so all skills share one gate: **network/allowlist** (`mcp.senzing.com` +
  `raw.githubusercontent.com` reachable), **host shell + writable workspace**, Senzing
  **SDK/engine/DB/license**, and **interactive-outcome capability** (can this host serve a live
  `localhost` app, or only a self-contained HTML5/PDF artifact?). `doctor` reports a compact
  status table and a specific fix per failing row. `recipes` drops its duplicated block and defers
  to `doctor`; `demo` and `build` run it up front too.

- **Fail fast on the deliverable, not after a 45-minute run.** Because the interactive-outcome
  check runs in preflight, skills that can end in a *live interactive app* now decide up front:
  `recipes` offers a self-contained interactive **HTML5 artifact** (map → load → resolve) in a
  cloud sandbox and recommends **Claude Code** for the literal live-server plate; `build`
  generates code anywhere but flags that **writing into the user's local project and running it**
  need Claude Code, handing back a downloadable artifact otherwise; `demo`'s dashboard was already
  a self-contained Artifact, so it lands everywhere. The environment is decided *before* the work,
  never revealed as impossible at the end.

## [1.32.9-2] - 2026-08-14

Plugin-only patch on MCP server v1.32.9 (no server change).

### Added

- **Uploadable plugin release for Claude Desktop.** A new
  `Release plugin (.zip)` workflow (`.github/workflows/release-plugin.yml`) fires
  on the `senzing--v<version>` tag, packages the plugin with
  `scripts/build-plugin-zip.sh` into `senzing-claude-plugin-<version>.zip`
  (canonical nested `senzing/` layout, validated with
  `claude plugin validate --strict`), and attaches it to the GitHub Release.
  Install in Claude Desktop via *Settings → Plugins → Add → Upload a file*, or in
  Claude Code via `claude --plugin-url` — re-uploading a newer same-named `.zip`
  updates in place. This is the plugin itself (skills/hooks/agents), not an MCP
  bundle.

### Fixed

- **`recipes` resolves its cookbook ref at runtime so it survives the
  branch→`main` migration.** Instead of a single pinned `RECIPE_REF`, the skill
  now tries `RECIPE_REFS = [main, cookbook-import]` in order and uses the **first**
  whose `recipes.md` fetches (a non-empty `200`) for every URL that run. While the
  cookbook lives on `cookbook-import` it is used; the moment it lands on `main` the
  skill picks `main` automatically — no plugin re-release needed at the cut-over,
  and no empty catalog if `cookbook-import` is later retired. Drop `cookbook-import`
  from the list once `main` is canonical.

## [1.32.9-1] - 2026-08-14

Plugin-only feature on MCP server v1.32.9 (no server change).

### Added

- **`recipes` skill → `/senzing:recipes [recipe]`.** Cook a curated, step-by-step
  recipe from the **Senzing Cookbook** (`github.com/senzing/recipes`). With no
  recipe named it fetches the catalog (`recipes.md`) and helps the user choose;
  with one named it loads `recipes/<id>.md`, confirms the kitchen/language/
  ingredients, and **drives each cook → plate → plus step in order** against the
  user's own Senzing — rather than handing the user prompts to paste. Recipe
  content is fetched **verbatim** via `curl` (falling back to `WebFetch`) so each
  step's inline prompt runs word-for-word; the cooking metaphor's own House Rule
  (*"Use the Senzing MCP. Do not rely on general training."*) keeps every step
  grounded, and stewardship (merge/split) is gated — confirmed before each write,
  never automatic. Recipes are parsed as Markdown (a `#` inside a fenced prompt is
  not a heading); internal frontmatter (`version`, `senzing_version`) and the
  `## Changelog` section are skipped.

### Changed

- **Unprompted, visual progress on the long-running skills (`demo`, `analyze`,
  `report`, and the new `recipes`).** These runs can take 15+ minutes, and the
  demo flow in particular is a spectator sport — the user is watching, not
  driving. The skills now require a **progress checkpoint at each milestone**
  (environment ready · mapped · loaded **per file as it lands**, with counts and
  errors · records → entities + compression ratio), surfaced **on the skill's own
  initiative** and **never as a gate** — the user never has to answer to keep the
  run moving (answer-required prompts stay reserved for loading into a production
  repo and for merges/splits). Each checkpoint is a **compact visual** — a
  one-line stat line, a micro-table, or a one-line ASCII bar — explicitly **not a
  wall of prose and not silence**. Fixes feedback that a ~18-minute demo showed
  little but terse "ran a command / done" lines with nothing to glance at until
  the final dashboard.

### Note

- **Recipe ref is pinned to the `cookbook-import` branch** until it merges to
  `main` in `senzing/recipes`. Flip the single `RECIPE_REF` marker in
  `plugins/senzing/skills/recipes/SKILL.md` from `cookbook-import` to `main` when
  it lands, so the command never lists an empty catalog.
- **Tool surface (MCP) is unchanged** — this adds a plugin skill only; no MCP tool
  was added, removed, or renamed. The `-1` suffix marks a plugin-only patch on the
  same server pin; `mcp-version-sync.yml` strips it, so daily version sync won't
  revert it.

## [1.32.4] - 2026-08-01

Version pin to Senzing MCP server **v1.32.4**.

**No plugin content changes.** v1.32.4 is the second #mcp-logging feedback batch:
three flag documents the extractor had been silently skipping (closing two
separately-reported gaps in one fix), corrected error-code guidance for
SENZ-7426, a data-mapping warning that fired on every correct mapping, per-input
profiler output paths, CSV sources without a header row, and pruning of indexed
pages that no longer exist upstream.

**Tool surface is unchanged** — the release altered behavior, response fields
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
