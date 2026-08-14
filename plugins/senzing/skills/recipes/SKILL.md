---
name: recipes
description: >
  Cook a Senzing solution from the Senzing Cookbook — a curated, step-by-step recipe you pick and
  Claude walks through, end to end. Use when the user wants a guided, opinionated build for a use
  case (fraud, customer-360, compliance/exclusion screening, PPP-loan exploration) rather than an
  open-ended task — e.g. "show me the recipes", "run the customer 360 recipe", "cook the healthcare
  exclusion recipe", "walk me through a Senzing cookbook recipe", "senzing recipes". With no recipe
  named it lists the catalog and helps you choose; with one named it stands up the kitchen, loads
  the ingredients, and drives each cook/plate/plus step in order against your own Senzing.
argument-hint: "[recipe-id-or-name]"
allowed-tools: Bash, Read, Write, WebFetch, Task, Skill, mcp__plugin_senzing_senzing__*
---

# Cook a Senzing Cookbook recipe

Recipes come from the **Senzing Cookbook** (`github.com/senzing/recipes`): a chef-authored,
plain-English sequence of prompts that stands up a working Senzing solution for a real mission.
You are the **sous-chef** — you interpret and *run* each prompt, backed by the **Senzing MCP**
(the kitchen staff). Drive the recipe; don't just hand the user prompts to paste.

## Recipe source

<!-- REF: recipes are migrating from the `cookbook-import` branch to `main` in senzing/recipes.
     RECIPE_REFS is tried in order so the skill self-heals across the merge — no plugin
     re-release needed at the moment it lands. Once `main` is canonical and the branch is
     retired, drop `cookbook-import` from the list. -->
- `RECIPE_REFS = [main, cookbook-import]` — candidate refs, highest priority first.
- **Resolve the ref once, at the start of the run:** try each ref in order and pick the **first**
  whose catalog fetches successfully (a non-empty `200`) —
  `curl -fsSL "https://raw.githubusercontent.com/senzing/recipes/<ref>/recipes.md"` (`-f` fails on
  `404`, so "first that succeeds" is well-defined). Call the winner `REF` and use it for **every**
  URL for the rest of the run, so catalog, recipe, and ingredients all come from one source.
- Raw base: `https://raw.githubusercontent.com/senzing/recipes/${REF}/`
- Catalog: `<raw base>/recipes.md` · a recipe: `<raw base>/recipes/<id>.md` · repo-provided
  ingredients: `<raw base>/ingredients/<...>`
- If **no** ref yields a catalog, tell the user the cookbook is unreachable (and to allow
  `raw.githubusercontent.com`); do **not** reconstruct recipes from memory.

**Fetch verbatim.** Use Bash `curl -fsSL "<url>"` to pull the exact markdown into context — the
recipe's inline prompt blocks must be run **word-for-word** (their hard rules matter). If `curl`
is unavailable or blocked, fall back to `WebFetch`; if both fail, ask the user to allow
`raw.githubusercontent.com`, and do **not** reconstruct a recipe from memory.

**Parse it as Markdown, not by line-grep.** A recipe is YAML frontmatter + a body of `## ` (H2)
sections. A `#` inside a fenced code block is **not** a heading (it's a comment in an example
prompt). Skip the internal frontmatter keys (`version`, `senzing_version`) and the `## Changelog`
section — neither is part of the cook.

## Ground rules (non-negotiable)

- **Use the Senzing MCP. Do not rely on general training.** This is the recipes' own House Rule,
  baked into every prompt. All Senzing facts, attributes, SDK signatures, and code come from the
  MCP tools (`get_capabilities`, `search_docs`, `mapping_workflow`, `sdk_guide`,
  `generate_scaffold`, `reporting_guide`, …) — never from memory.
- **Never simulate entity resolution.** If Senzing isn't installed/running, say so and pivot to
  install via the `doctor` skill — never fabricate scores, matches, or merges.
- **PII stays local.** Repo ingredients are synthetic and safe. If the user swaps in their own
  data, its records are only ever touched by SDK code you run locally via Bash — never pasted into
  a hosted tool call. Bake that into the load prompt.
- **Run the recipe's prompts as written.** The chef put the exact hard rules, data-source names,
  and serve preferences in each fenced prompt. Execute them; don't paraphrase them away. Hard rules
  are **cumulative** — later steps say "keep all previous hard rules in force," so carry them.

## Procedure

**Inputs.** `$ARGUMENTS` may name a recipe by `id` (e.g. `customer-360-crm-online`) or by title
words. Match it against the catalog `id`s; on a fuzzy/multiple match, confirm which before cooking.

1. **Pre-flight FIRST — run `doctor`.** A recipe ends in a *served* result (a loaded Senzing **and**
   an interactive app/visual), so clear the whole path **before** investing in a cook — don't march
   into a recipe that can't reach its plate. `doctor` checks it all in one pass: sources reachable
   (`mcp.senzing.com` + `raw.githubusercontent.com` allowlisted), host shell writable, Senzing
   deployable (SDK / license / DB), and **interactive-outcome capability**. Act on its verdict
   before cooking:
   - **Senzing can't deploy** → help install (`doctor` → `sdk_guide(topic="install")`; free 10-day
     eval via `submit_feedback`); don't cook over a Senzing that won't stand up.
   - **A source is blocked** → stop and ask the user to allowlist that domain now (for recipe text
     you may fall back to `WebFetch`, but `mcp.senzing.com` is non-negotiable).
   - **No live-app surface here** (cloud sandbox, chat-only host, or a reduced sub-agent) → say so
     plainly: the recipe's *Plate* can't be a live `localhost` server here. Offer the honest
     substitution — map → load → resolve **plus a self-contained interactive HTML5 artifact** you
     deliver as a download — and recommend running the recipe in **Claude Code** for the literal
     live-server plate. Don't pretend the plate will render where it can't.

   (Browsing the catalog is fine to attempt either way; committing to cook is not.)
2. **Pick a recipe.** If no recipe was named (or the match is unclear), `curl` the catalog
   (`recipes.md`) and present it: for each entry show **title · use_case · difficulty · kitchen ·
   estimated time · author** and its "what you'll make" line, then ask which to cook. If one was
   named, skip to step 3.
3. **Load the recipe.** `curl` `recipes/<id>.md`. Read the frontmatter and body. Show the user the
   recipe's identity up front: **title, the mission, a one-line take from the Chef's Note,
   difficulty, kitchen, estimated time**, and surface the recipe's own "before you cook" reminders
   (use your most capable model; *your result will look different each run*; the video is
   illustrative). Confirm they want to proceed.
4. **Setup — confirm before cooking.** From the *Setup: What you'll need* section (Senzing
   deployment and host capability were already cleared in pre-flight):
   - **Kitchen:** stand up the platform the recipe targets (`local`, `aws`, …) per its *Setup*/*Prep*
     prompt.
   - **Language:** **do not assume Python** — its binding is Linux-only. Confirm the implementation
     language the recipe/user wants before generating any code.
   - **Ingredients:** if the recipe uses repo-provided ingredients, `curl` them from
     `<raw base>/ingredients/<...>` into the workspace before the Cook step. If the user brings
     their own data, take the paths, keep PII local, and note where the mapping will differ.
   - **Workspace:** agree one (default `~/sz-workspace` or `$SZ_WORKSPACE`) and thread it through
     every step (the writability probe already ran in pre-flight).
5. **Cook the steps in order.** Walk the action sections as the recipe lays them out —
   *Prep → Cook → Plate → Plus* (names and count vary; cook whatever H2s are present). For each:
   - Show the step's inline prompt block, then **execute it yourself** — this is a driven
     walk-through, not a paste-list.
   - Ground the work through the MCP the way the sibling skills do: `mapping_workflow` for every
     mapping (never hand-code Senzing JSON), `sdk_guide`/`generate_scaffold` for loaders and SDK
     code, `reporting_guide` for the plate (mart/SDK only — no direct DB queries; render the graph
     only for a selected entity). Reusing the `analyze` / `build` / `report` flows for the heavy
     lifting is encouraged; keep the recipe's prompt as the source of truth for *what* to build.
   - **Gate the writes.** Before loading records, confirm target + counts. Load into a fresh
     scratch repository by default; touch the user's production Senzing only on explicit request,
     and confirm first.
   - **Narrate progress as a visual, unprompted.** Cooking is long-running and the user is watching;
     don't go silent, but don't dump prose. At each milestone post a **compact visual** with real
     numbers — a one-line stat line, micro-table, or one-line ASCII bar (loaded **per file as it
     lands** + total, 0 errors; records → entities + compression). Informational, never a gate. See
     the `demo` skill's progress guidance for the exact shape.
   - After each step, state the recipe's **Expected outcome** and answer its "Questions that may
     come up" if they arise. Don't hold match/merge numbers to any exact target — the recipe warns
     results vary run to run.
6. **Optional refinements — only if the user wants them.** *Garnish* (why/how/graph) is
   presentation-only and safe. **Season to taste** is stewardship (merge/split): it changes the
   resolved truth across every view — **gate each merge/split, confirm before it writes, never
   automatic.**
7. **Wrap up.** Summarize what was built and why it matters, per the recipe's *Wrap Up*, and link
   the demo **video** if the frontmatter carries one.

Outcome: the recipe's finished dish — a real, loaded, resolved Senzing solution on the user's
machine, served through its place setting, built by driving the chef's prompts and grounded in the
Senzing MCP.
