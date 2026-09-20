# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **Real-Senzing end-to-end eval (`plugins/senzing/evals-real/`, `.github/workflows/real-senzing-e2e.yml`).**
  The behavioral suite has never tested `analyze` past step 3 of 7 and structurally could not — it
  runs on a macOS host with no Senzing, and its own `analyze` case says so ("The sandbox has no
  Senzing, so the run ends by saying so"). No grader anywhere asserted an entity count, a match
  score, a why/how result or a report. The new `resolve-truthset` case goes the full distance on a
  Linux container that really has `senzingsdk-runtime`: one `mapping_workflow` over all three
  truth-set CSVs, mapper run, load into a fresh on-disk SQLite scratch repository, redo queue
  drained, entities counted.
  The verdict is **not** a grader — `claude plugin eval` has no shell grader, so every grader is a
  statement about text the agent produced, and text is what a fabricating run is good at. A job
  step opens the repository the run left behind with the real V4 SDK and checks it against
  Senzing's own published ground-truth key (`Senzing/truth-sets`, pinned): 159 records, **85**
  entities, the exact cluster partition, and an empty redo queue. Both numbers are derived from
  the key at run time, never frozen literals; `ground-truth/PROVENANCE.md` records the pin, the
  derivation and its limits. No repository found is a FAIL, never a skip. A free offline
  self-test re-derives the expectation (and cross-checks the two literals the graders carry)
  before any budget is spent, and a free Senzing preflight proves the engine resolves on the host
  before that. 159 records sits inside the 500-record no-license ceiling, so no license or
  credential is involved.
  Separate workflow and separate eval directory on purpose: the macOS `behavioral-eval` job and
  its suite are untouched, and it does not gate every PR (`workflow_dispatch`, weekly, or the
  `real-senzing-e2e` label).

- **Sandbox preflight (`.github/senzing-eval/sandbox-preflight.sh`).** Proves the agent's Bash
  tool can actually run a command in the eval container before any eval budget is spent. It
  drives the real pinned CLI with the sandbox on through its own public settings keys
  (`sandbox.enabled`, `sandbox.failIfUnavailable`) and asserts the observable — a shell command
  ran and its output came back — by having it read a nonce the model cannot know, so a model that
  never touched Bash cannot echo the marker back and turn it green. Haiku, ~$0.016, against the
  $0.53 and 2.5 minutes it protects. Verified in both directions before shipping: exits 0 with
  the nonce, exits 1 with the nonce file removed.

### Fixed

- **The real-Senzing E2E scored the plugin 0.44 twice for a broken container, not a broken
  plugin.** Every Bash call the agent made died before running, with
  `bwrap: Can't mount tmpfs on /newroot/run/shm: No such file or directory`, so it correctly
  refused to invent an entity count and the graders scored the refusal. Three defects, all fixed:
  (a) the image gave itself `/run/shm` as a *symlink* to `/dev/shm`; bwrap populates its new root
  after `pivot_root`, when `/dev` does not exist there, and the symlink also slips past
  `ensure_dir()` (stat fails on the dangling link, mkdir returns EEXIST and reads as success) so
  setup dies at the mount instead. It is a real directory now. (b) Nothing asserted the sandbox —
  the Senzing preflight proves the *engine* runs, which is a different question. There is a
  sandbox preflight now (above). (c) The job's own diagnostics could not read their own input:
  the `--keep-temp` workspace is left root-owned with its modes closed, so the host-side `find`
  for the scaffold marker and the trace files silently came back empty on both runs — which
  disabled the `grep 'bwrap:'` check that would have named the real fault. Both now run inside
  the container.

## [1.37.4] - 2026-09-19

Plugin release on MCP server v1.37.4. Branch `fix-doctor-platform-gate`.

### Added

- **`poc-planner` skill** — plan a proof of concept *with* the user; explicitly not a project
  plan. A facilitator, not a generator: it retrieves Senzing's own PoC guidance, asks the
  rightsizing questions (data, systems, people — plus hardware available, performance to
  demonstrate, and platform), assembles the corpus's sizing / database / platform / load material
  against the user's stated constraints with every item attributed, and works through what must
  be true for a buy decision. Writes `./senzing-poc-plan.md` as a handoff artifact: fixed
  headings, a YAML constraint block (`volume_records`, `database`, `platform_id`, `languages`,
  `data_sources[]`…), individually-addressable `SC-n` success criteria, and the machine-detectable
  `TBD — decided by <owner>` literal so a downstream skill can tell decided from undecided and
  refuse to fill the difference. Never calls `doctor` (planning needs the MCP reachable, not a
  working install); never invokes a sibling skill (hand-off means naming the next command); never
  offers to generate a truth set; where tools disagree on license terms it quotes each and lists
  the discrepancy rather than reconciling. Deterministic file-level graders catch the common
  fabrication shapes (week-numbered schedule, metric thresholds, hardware verdicts, hedged TBDs,
  a `guidance:` hint under a target); a file-focused judge covers the rest (phase structure, role
  titles, extrapolation).
- **Offline grader fixture check (`scripts/check-poc-graders.py`, `check.sh` section 8).** Runs
  every `not_contains` grader against the verbatim tool output the plan is required to quote
  (Hardware Sizing FAQ, `reporting_guide(quality)`, the PoC article, Database Tuning, both
  `sdk_guide` results, the `submit_feedback` terms) and against a correct and a fabricated plan
  fixture. Caught two false-fails before the first paid run: a bare-percentage grader fired on
  seventeen quotable corpus figures, and the proposed hardware-recommendation pattern missed its
  own example.
- **`ask`** — the entry point for questions. Routes to the MCP and writes nothing. Added because every other skill is a *doer*: a plain question either matched nothing or matched a skill that would start writing files, and two independent weak-model reviews said they would answer Senzing questions from stale training data instead.
- **`install`** — install and set up Senzing. Reproduces no install commands; detects the host, takes the official steps from `sdk_guide`, surfaces the EULA, then verifies with `doctor`. Previously buried at the end of `doctor`'s description where the command picker truncated it.
- Explicit "Not for X — use Y" boundaries on every skill description. Weak-model routing measured 17/20 → 20/20.


- **`ask` skill** — answer any Senzing question grounded solely in the hosted MCP. The only
  skill that works on an information-only host (no shell, no Senzing install), so it now leads
  the session banner.
- **`install` skill** — install / set up Senzing on the current machine, split out of `doctor`.
- **Hook fixture tests in `scripts/check.sh` (section 6).** A REAL `mapping_workflow`
  PostToolUse payload (content-array shape, `[REMINDER: …]` footer intact) is fed to
  `capture_state.sh` and the state file must appear; a `Write` payload is fed to
  `check_provenance.sh` and hook JSON must appear on stdout; `session_start.sh` must run with
  `HOME` unset. Fixtures live in `plugins/senzing/hooks/fixtures/`. Also: every `SKILL.md`
  `name:` must equal its directory (section 5), and `CHANGELOG.md` must have a `## [<version>]`
  heading for the version in `plugin.json` (section 7).
- **CI: live server version check.** The "MCP endpoint reachable" job accepted any status
  below 500, so a 404 from a moved path passed. It now also fetches
  `/.well-known/agent-card.json` on the MCP host and requires its `version` to equal
  `plugin.json`'s (a `-N` plugin-patch suffix is stripped first).

### Changed

- Synced to MCP server **v1.37.4**, which carries the v1.37.3 security fix (CVE-2026-14456, HIGH, `libssl3t64` on both deployed images) plus a batch of field-reported corrections: `get_sample_data` no longer blocking a guided download, `brianmacy/sz-cpp-sdk` indexed as a community C++ SDK, a search-index chunker that was blind to level-1 `#` headings (10,968 → 11,217 chunks corpus-wide), `plan-a-poc` no longer inventing PoC success criteria, and `sdk_guide(full_pipeline)` honouring `record_count`. Tool surface unchanged. Note the CI gate compares `plugin.json` against the **live** agent-card, so a plugin version bump must follow the server deploy rather than lead it — this branch was blocked by that gate until the bump, which is the gate working as designed.


- **`ask`** names `poc-planner` in its Not-for clause, no longer claims to be the only skill
  that works on an information-only host, and now grounds arithmetic as well as retrieval: it
  may not extrapolate a retrieved sizing figure into a new one, and a plan-shaped question that
  lands there is answered from the PoC guidance only with `TBD — decided by <owner>` for anything
  no tool or user supplied.

### Fixed

- **The `demo-scratch-repo` eval case contradicted itself twice**, and the plugin was being
  marked down for obeying it. (a) The prompt says "before you execute anything that loads data,
  show me the plan and the exact commands", while the grader FAILed any plan that "asks for
  confirmation before loading into the scratch repository" — so a run that produced a correct
  scratch-SQLite plan with production untouched still lost the judge 3-0 for ending with "shall I
  run it?". The grader now scores the real property (never offering production as a target, never
  treating the throwaway repo as a decision the user must approve) and states that the handshake
  this prompt asks for is not a gate. (b) The prompt asserts a green doctor and a configured
  production Postgres, but the macOS eval sandbox has neither, so roughly one run in two correctly
  refused to plan on a premise it could see was false and lost four graders as collateral. The
  context block now says to take it as given and not re-probe the shell. No threshold was lowered.

- **The behavioral eval job had never once executed.** It was green because
  `ANTHROPIC_API_KEY` was unset, so it SKIPPED. With the secret set it ran for the first
  time and reported 4/14 — which turned out to measure the runner, not the plugin (below).
- **CI graded an agent with no MCP tools and no working shell.** Two independent runner
  faults: `ubuntu-24.04` denies bubblewrap its user namespace
  (`kernel.apparmor_restrict_unprivileged_userns=1`), so every Bash call died with
  `bwrap: loopback: Failed RTM_NEWADDR` — 52 of them, `pwd` included; and the runner has no
  `/run/shm`, so once that was cleared the sandbox still failed with
  `Can't mount tmpfs on /newroot/run/shm`. Fault 1 was cleared by moving the job into a
  `--privileged` container. **Correction (see Unreleased): the claim that both were "fixed and
  asserted before any spend" was wrong on both counts.** The fix for fault 2 gave the image a
  `/run/shm` *symlink*, which does not satisfy the mount, and nothing asserted the sandbox at
  all — there was no sandbox preflight until the entry under Unreleased added one.
- **Four eval graders could not fail.** Every `regex`/`target: trace` MCP-grounding grader
  matched the tool NAMES in each skill's own `allowed-tools:` frontmatter (and, for
  `article-actually-retrieved`, a literal hard-coded in `poc-planner/SKILL.md` as the query to
  run) — so they passed 2/2 in runs with zero MCP calls. All four are now `tool_used`.
- **One eval grader could not pass.** `poc-guidance-searched` required `min: 3` matching
  `search_docs` calls, but its regex missed `"Selecting the right data"` — one of the three
  queries the skill itself prescribes. A model following the skill verbatim scored 2.
- **`poc-planner` could never write a plan.** `poc-planner-elicits` requires no file and
  `poc-planner-grounded` requires `senzing-poc-plan.md` to exist; the skill had no branch
  between them and step 2 blocked unconditionally on an answer, so the grounded contract was
  unsatisfiable. Now an explicit ELICIT/DRAFT mode.
- **`analyze` step 5 hung the run.** It told the model to Bash-run the `sdk_guide(topic="redo")`
  snippet, which is a `while True` daemon that sleeps forever — so a successful load never
  reached the entity count. Now a bounded loop, mirroring `doctor` check 6b.
- **`install` could ping-pong with `doctor` forever.** Step 5 had no branch for a failed
  verification, and `brew install --cask senzingsdk` exits 0 while installing nothing when the
  EULA variable is unset.
- **`build` skipped the MCP and refused to deliver.** It generated SDK code without
  `generate_scaffold`/`get_sdk_reference`, and downgraded an explicit "put it in
  senzing_search.py" to an inline snippet by assuming a sandbox instead of running the probe.
- **`troubleshoot` answered from training data.** One run explained an error code in two turns
  without calling `explain_error_code`; the mandatory call is now a gate above the procedure.
- **`poc-planner` said "these six keys only" while listing seven** (`id`, `shape`, `statement`,
  `measurement`, `measured_against`, `decided_by`, `target`) in the skill, the grader and its
  prompt — a weak model drops one, most likely `decided_by`.
- **`poc-planner` promised a consumer contract nobody honored.** Nothing read
  `senzing-poc-plan.md`; `analyze`, `doctor` and `install` now do, and stop on any
  `TBD — decided by` row they need.
- **An eval case silently never ran.** `poc-planner-how-long/prompt.md` had invalid YAML
  frontmatter (a double-quoted scalar with text after the closing quote), so `claude plugin
  eval` dropped it — 13 of 14 discovered.
- **Two gates that could not fail.** `check.sh` never parsed eval `prompt.md` frontmatter, and
  `run.sh` exited 0 when the CLI produced no result JSON.
- **checkov false positive blocked the PR.** Its secrets scan walks the whole repo and flagged
  documented placeholder connection strings (`sqlite3://na:na@…`) in captured MCP fixtures.
- **This CHANGELOG section was a bad merge** — duplicate `Added`/`Changed`/`Fixed` blocks and an
  orphaned 1.37.2 prose line nested inside it.

- **`/senzing:recipes` was dead in production.** Both configured catalog refs 404'd (`recipes.md` on `main`, and a `cookbook-import` branch deleted after merge); the real catalog is `cookbook.md` on `main`. Every run stopped at the catalog fetch and told the user to allowlist a domain that was never blocked. The ref-fallback list was built to survive a branch *move* and cannot survive a file *rename*. Also removed instructions to parse YAML frontmatter that recipes do not have.
- **The state-capture hook had never written a file.** Four independent defects, including that the MCP returns a content array rather than a parsed object, that the `workflow_id` it keyed filenames on does not exist in the response, and that a `[REMINDER: …]` footer shares the text block with the JSON. It exited 0 regardless, so nothing ever surfaced it. Now covered by six fixture tests.
- **The eval suite was never discovered and could never fail.** Cases lived at repo root while `claude plugin eval` looks under the plugin; the job was additionally `workflow_dispatch` + `continue-on-error`. Moved, gated, and grown from 4 cases to 11.
- **`analyze` drove one `mapping_workflow` per file.** The tool takes a `file_paths` array and does explicit multi-schema analysis, so per-file workflows could never see a cross-file join — multi-file runs silently produced worse mappings with no error. Parallel sub-agents also clobbered each other's fixed-name files in a shared workspace.
- **`demo` loaded the user's production repository by default**, inverting its own description, the README and `analyze`.
- **The EULA gate could be bypassed** — three skills routed around `install` straight to `sdk_guide(topic="install")`.
- **`build` required `doctor` checks 4–9 green**, which is unreachable on a healthy machine (7 is ➖ when the config env var is unset, 8 cascades, 9 is ⚠️ on the built-in eval license).
- **`report` claimed the entity count works on `internal://`**, which the MCP contradicts — that store lives only in the process that loaded it, so a Bash-run export counts zero.
- Numerous restated Senzing facts replaced with tool calls, per the rule that the MCP owns facts and the plugin owns workflow.


- **`capture_state.sh` had never written a state file — three independent defects.**
  (1) It read `.tool_response.state`, but an MCP tool's `tool_response` is a CallToolResult
  content array `[{"type":"text","text":"<json>\n\n[REMINDER: …]"}]`; the path matched
  nothing, so the hook exited 0 silently on every call. (2) It named the file
  `.sz-state-<workflow_id>.json`, but a `mapping_workflow` state is
  `{step, step_name, file_paths, workspace_dir}` — there is no `workflow_id` — so even a
  working writer and the skills' reader disagreed on the name. (3) It resolved the workspace
  from `SZ_WORKSPACE`/`HOME`, which a hook inherits from the Claude Code process, not from the
  Bash tool's environment. Proof: `~/sz-workspace` has hosted mapping runs since 2026-08-21
  and contained zero `.sz-state-*` files; the old hook fed the captured payload writes
  nothing, the new one writes the state. Now: parse the content array, strip the footer,
  take `workspace_dir` **from the state itself**, and write `<workspace_dir>/.sz-state.json`
  (write-then-rename). The `analyze` skill and `field-mapper` agent read that exact path.
- **`check_provenance.sh` nudged nobody.** It wrote to stderr and exited 0; for a
  PostToolUse hook that reaches neither the model nor the user. It now emits
  `{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":…}}` on stdout.
  Its trigger also fired on the bare word `senzing` (a comment `# no senzing here` tripped
  it); it now matches SDK symbols only (`senzing_core`, `from senzing`, `com.senzing`,
  `Senzing.Sdk`, `sz_rust_sdk`, `@senzing/`, the `Sz*` class family).
- **`session_start.sh` crashed under `set -u` when `HOME` was unset**
  (`HOME: unbound variable`, exit 1). Uses `${HOME:-/tmp}`. Banner now lists `ask` and
  `install`.
- **`doctor` reported a healthy machine as broken** and its interactive-outcome capability
  gate was restored; `demo` is now explicitly `analyze` on sample data; running generated
  code from `build` is optional, not assumed.
- **CI `install-smoke` hard-coded `Skills (9)`.** The count is derived from the skills
  directory, and every skill name must appear in `claude plugin details` output.
- `.gitignore` now ignores `**/evals/results/` (behavioral-eval output, wherever the evals tree lives).

## [1.37.2] - 2026-09-18

Version sync to MCP server v1.37.2 (`plugin.json` only). Server headline: boot-time
self-smoke turns Fly's rolling deploy into a per-machine canary; rollbacks no longer replace
every machine at once. Also: `troubleshoot` stops hard-coding the error-code count
(`450+`) — the literal had drifted to three different values across three repos in one day.

## [1.37.1] - 2026-09-17

Version sync to MCP server v1.37.1 (`plugin.json` only). Server headline: TypeScript SDK doc
examples restored in `find_examples` (they vanished on every clean build).

## [1.37.0] - 2026-09-17

Version sync to MCP server v1.37.0 (`plugin.json` only). Server headline: rmcp 3.4.0; three
more `senzing` repos indexed (incl. the Cookbook, which `recipes` consumes); crawler prefers
origin-served markdown.

## [1.36.1] - 2026-09-03

Version sync to MCP server v1.36.1 (`plugin.json` only). Server headline: `sdk_guide`'s dead
EULA link (`senzing.com/senzing-eula` → `senzing.com/end-user-license-agreement/`) fixed.

## [1.35.5] - 2026-09-01

Version sync to MCP server v1.35.5 (`plugin.json` only). Server headline: reindex of the
refreshed upstream Windows Quickstart; refreshed committed SDK snippets from
`code-snippets-v4`.

## [1.35.4] - 2026-09-01

Version sync to MCP server v1.35.4 (`plugin.json` only). Server headline: full
`senzing.com/releases` history captured (multi-`<article>` fix).

## [1.35.3] - 2026-09-01

Version sync to MCP server v1.35.3 (`plugin.json` only). Server headline: Senzing 4.4.0
Feature Store & Advisory Locking configuration guide indexed for `search_docs`.

## [1.35.1] - 2026-08-29

Version sync to MCP server v1.35.1 (`plugin.json` only). Server headline: `senzing.com/releases`
served from a committed fallback (Cloudflare blocks datacenter IPs); CORD 250k eval samples.
(v1.35.0 was superseded before a plugin sync landed.)

## [1.33.0] - 2026-08-20

Version sync to MCP server v1.33.0 (`plugin.json` only). Server headline: `needs_input`
clarification responses no longer read as empty; eval-license duration corrected (10-day).
(v1.34.x had no plugin sync.)

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
