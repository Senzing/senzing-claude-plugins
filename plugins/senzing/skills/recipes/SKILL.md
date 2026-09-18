---
name: recipes
description: >
  Run a recipe from the Senzing Cookbook — a chef-authored, step-by-step solution that Claude
  drives end to end against the user's own Senzing. Use when the user names a recipe or one of its
  use cases (fraud, customer-360, compliance / exclusion screening, PPP-loan exploration), or asks
  e.g. "show me the recipes", "run the customer 360 recipe", "senzing recipes". With no recipe
  named it lists the catalog and helps them choose. Runs doctor first — a
  recipe ends in a served result, so a host that cannot deliver one must be caught before the cook,
  not after. Not for the user's own ad-hoc data files (use analyze) or a quick demonstration on
  sample data (use demo).
argument-hint: "[recipe-id-or-name]"
allowed-tools: Bash, Read, Write, WebFetch, Agent, Skill, mcp__plugin_senzing_senzing__*
---

# Cook a Senzing Cookbook recipe

Recipes come from the **Senzing Cookbook** (`github.com/senzing/recipes`): a chef-authored,
plain-English sequence of prompts that stands up a working Senzing solution for a real mission.
You are the **sous-chef** — you interpret and *run* each prompt, backed by the **Senzing MCP**
(the kitchen staff). Drive the recipe; don't just hand the user prompts to paste.

## Recipe source

<!-- The cookbook lives on `main` in senzing/recipes. The catalog file is `cookbook.md`.
     Both were wrong here once already: this skill shipped pointing at a `cookbook-import`
     branch (since deleted) AND at `recipes.md` (which has never existed on main), so every
     run died at the catalog fetch with a misleading "cookbook unreachable" message. If the
     catalog 404s again, verify the real filename in the repo before adding a fallback ref —
     the failure mode last time was a file RENAME, which no amount of ref-juggling fixes. -->
- Raw base: `https://raw.githubusercontent.com/senzing/recipes/main/`
- Catalog: `<raw base>/cookbook.md` · a recipe: `<raw base>/recipes/<id>.md` · repo-provided
  ingredients: `<raw base>/ingredients/<...>`
- If the catalog does not pass the fetch validation below, say the cookbook is unreachable **and
  quote the URL and status you got** — do not just tell the user to allow a domain, because a
  `404` is a wrong path, not a blocked network. Never reconstruct recipes from memory.

**Fetch verbatim — to a file, and validate it before trusting it.** Use Bash
`curl -fsSL "<url>" -o "<workspace>/<name>.md"` to pull the exact markdown. `-f` rejects only HTTP
≥ 400: it happily passes an **empty body**, and a `200` that is really an HTML error page. So
before parsing anything, assert all three:
- the file is non-empty (`test -s`);
- its first non-blank line is a `# ` heading — **not** `<!DOCTYPE` or `<html`. (Both the catalog
  and the recipes open with an H1; neither has YAML frontmatter.);
- it contains at least one `## ` section heading.

A file that fails any check is a **failed fetch**, not a recipe: try the next ref, or `WebFetch`
with the same checks; never parse it as recipe steps. Then read the validated file into context —
the recipe's inline prompt blocks must be run **word-for-word** (their hard rules matter). If
`curl` is unavailable or blocked, fall back to `WebFetch` (same validation); if both fail, ask the
user to allow `raw.githubusercontent.com`, and do **not** reconstruct a recipe from memory.

**Parse it as Markdown, not by line-grep.** A recipe is an `# ` title followed by `## ` (H2)
sections — there is **no YAML frontmatter**, so do not look for any. A `#` inside a fenced code
block is **not** a heading (it's a comment in an example prompt). Skip the `## Changelog`
section — it is not part of the cook.

## Ground rules (non-negotiable)

- **Use the Senzing MCP. Do not rely on general training.** This is the recipes' own House Rule,
  baked into every prompt. All Senzing facts, attributes, SDK signatures, and code come from the
  MCP tools (`get_capabilities`, `search_docs`, `mapping_workflow`, `sdk_guide`,
  `generate_scaffold`, `reporting_guide`, …) — never from memory.
- **Never simulate entity resolution.** If Senzing isn't installed/running, say so and hand off to
  the `install` skill — never fabricate scores, matches, or merges.
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
   - **Senzing can't deploy** → hand off to the **`install`** skill (it surfaces the license
     agreement, runs the official steps, and verifies with `doctor`; do not route around it via
     `sdk_guide(topic="install")` directly — if an evaluation license is needed,
     `submit_feedback(category='license_request')`'s description states the current terms). Don't
     cook over a Senzing that won't stand up.
   - **A source is blocked** → stop and ask the user to allowlist that domain now (for recipe text
     you may fall back to `WebFetch`, but `mcp.senzing.com` is non-negotiable).
   - **No live-app surface here** (cloud sandbox, chat-only host, or a reduced sub-agent) → say so
     plainly: the recipe's *Plate* can't be a live `localhost` server here. Offer the honest
     substitution — map → load → resolve **plus a self-contained interactive HTML5 artifact** you
     deliver as a download — and recommend running the recipe in **Claude Code** for the literal
     live-server plate. Don't pretend the plate will render where it can't.

   (Browsing the catalog is fine to attempt either way; committing to cook is not.)
2. **Pick a recipe.** If no recipe was named (or the match is unclear), fetch and validate the
   catalog (`cookbook.md`) per *Fetch verbatim* and present it. Each entry is an
   `### [Title](recipes/<id>.md)` heading, an italic metadata line of ` · `-separated fields
   (currently category · difficulty · where it runs · rough duration · author), and a
   `**What you'll make:**` line. Show the title, that metadata line as-is, and the
   what-you'll-make line — render the fields the catalog actually carries rather than a fixed
   list, so a change upstream degrades to "one fewer field" instead of a wrong label. Then ask
   which to cook. If one was named, skip to step 3.
3. **Load the recipe.** Fetch and validate `recipes/<id>.md` per *Fetch verbatim*. Read the
   title and body. Show the user the
   recipe's identity up front: **title, the mission, a one-line take from the Chef's Note,
   difficulty, kitchen, estimated time**, and surface the recipe's own "before you cook" reminders
   (use your most capable model; *your result will look different each run*; the video is
   illustrative). Confirm they want to proceed.
4. **Setup — confirm before cooking.** From the *Setup: What you'll need* section (Senzing
   deployment and host capability were already cleared in pre-flight):
   - **Kitchen:** stand up the platform the recipe targets (`local`, `aws`, …) per its *Setup*/*Prep*
     prompt.
   - **Language:** **do not assume Python.** Confirm the implementation language the recipe/user
     wants before generating any code, and check it is supported on this platform via
     `sdk_guide(topic="install", platform=…, language=…)` → `compatibility_notes` — do not carry
     the support matrix from memory.
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
   the demo **video** if the recipe links one (it appears inline, near the top).

Outcome: the recipe's finished dish — a real, loaded, resolved Senzing solution on the user's
machine, served through its place setting, built by driving the chef's prompts and grounded in the
Senzing MCP.
