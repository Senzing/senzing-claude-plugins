---
name: recipes
description: >
  Run a recipe from the Senzing Cookbook — a chef-authored, step-by-step solution that Claude
  drives end to end against the user's own Senzing. Use when the user names a recipe, asks for one
  by use case (e.g. "a customer 360 recipe", "is there a fraud recipe?" — the bundled catalog decides
  what exists), or asks e.g. "show me the recipes", "run the customer 360 recipe", "senzing recipes". With no recipe
  named it lists the catalog and helps them choose. **Cook the recipe against Senzing — never
  produce its result by other means.** A recipe whose output you assembled yourself is not that
  recipe, however close the answer looks. Runs doctor first — a recipe ends in a served result,
  so a host that cannot deliver one must be caught before the cook, not after. Not for the user's own ad-hoc data files (use analyze) or a quick demonstration on
  sample data (use demo).
argument-hint: "[recipe-id-or-name]"
allowed-tools: Read
---

# Cook a Senzing Cookbook recipe

> **NO SENZING ON THIS HOST? READ THE RECIPE, CALL `Skill(senzing:install)`, AND LET ITS MESSAGE BE YOUR
> ENTIRE REPLY.** After `doctor` reports no SDK and you have read the named recipe, the next tool call
> is `Skill(senzing:install)` with `args` = **doctor's platform id and nothing else** (e.g. `"macos_arm"`) —
> no language: the recipe's language is its Setup decision (step 4), made when you cook, not install's
> question now. You already hold install steps (doctor fetched them), which is not a reason
> to write the install message yourself. **After `install` loads, do not open the recipe file again** —
> CI caught two runs that re-read it right after `install` loaded, then mined it for a language menu ("the
> smoother fit for building the Customer 360 web app this recipe asks for") and for its Setup section
> ("attach your Senzing license file and the two ingredient CSVs"). When `install` returns, **add nothing before or after its message** —
> no doctor recap, no recipe summary ahead of it: no recap of
> the recipe's Setup section, no "you'll also need your license file", no remark about the 500-record limit
> or an evaluation license, no offer to copy the ingredient CSVs. CI caught both: a reply that wrote the
> install message itself, and one that invoked `install` and then appended "recipe handles up to 500 records
> without a license" (false — this recipe loads ~1,600) plus an offer to copy the ingredient files — Cook-step
> content that is not yours to put to the user here. Do not tell the user the recipe will resume or is ready to cook once Senzing is installed, and do not
> name its Prep → Cook → Plate steps anywhere in this reply — CI caught "…and only then resume the recipe's
> Prep → Cook → Plate steps" appended to install's message, and "the recipe's full Prep→Plate flow is reachable
> here once Senzing is installed" prepended to it; both announce the cook the user has not agreed to.

## Recipe source

<!-- BUNDLED, deliberately. This skill reads instructions and then runs them, so what
     executes must not be able to arrive — or change — after review. Earlier versions
     fetched the catalog and each recipe from raw.githubusercontent.com at a pinned
     commit; the pin answered Anthropic's RUNTIME_FETCH_EXEC finding, but the directory
     then held the listing again on "contains a download-and-run command", which a pin
     cannot satisfy because the fetch itself is the objection. The cookbook now ships
     INSIDE the plugin under `cookbook/`, vendored verbatim from senzing/recipes. Nothing is
     fetched at cook time, so the skill needs no network and no egress allowance for its source.
     NO COMMIT SHA IS WRITTEN HERE ON PURPOSE: `mcp-version-sync.yml` re-vendors on every
     version bump, so a SHA in this file would be stale by the next release. The commit that
     was vendored, the file list and their hashes live in `cookbook/PROVENANCE.md`, which the
     vendor script rewrites each time. Refresh by hand with `scripts/vendor-cookbook.sh [ref]`;
     between releases the `Cookbook whitelist still matches upstream` job in ci.yml reports
     bundle-vs-upstream drift as a NOTICE (never a red check, since the next version bump
     re-vendors it) and fails only when a recipe the eval graders whitelist is missing from the
     bundle. -->
- Bundled root: `cookbook/`, inside this skill's own directory and shipped with the plugin.
- Catalog: `cookbook/cookbook.md` · a recipe: `cookbook/recipes/<id>.md` · repo-provided
  ingredients: **not bundled** — see *Ingredients* below
- **Read them with `Read`. This skill downloads nothing, ever** — no shell download, no `WebFetch`, no network
  of any kind for recipe content. There is no reachability question to answer and no domain
  to ask the user to allow.
- Upstream of record is `senzing/recipes`; the exact commit this build carries is recorded in
  `cookbook/PROVENANCE.md`. That is **provenance, not a runtime source**: never fetch it while
  cooking, and never treat a newer upstream recipe as authoritative over the bundled copy. The
  bundle is what was reviewed, so the bundle is what you cook. `PROVENANCE.md` is generated —
  it is not a recipe, so never offer it or cook from it.
- **senzing.com publishes the same cookbook for people to read** — the AI Cookbook, under
  Resources: [Get Started](https://senzing.com/cookbook-get-started/) (the cookbook's own setup
  walkthrough, not general Senzing onboarding) and [Recipes](https://senzing.com/cookbook-recipes/).
  Those pages are copies and can lag the bundle, so **never take recipe content from them**.
  Link them for the user to browse or share.
- **A bundled file that will not open is a packaging bug, not an unreachable cookbook.** Say
  which path failed and stop; do not reconstruct a recipe from memory, and do not go looking
  for the content anywhere else.

**Read verbatim.** `Read` `cookbook/cookbook.md` for the catalog and `cookbook/recipes/<id>.md`
for a recipe. The recipe's inline prompt blocks must be run **word-for-word** — their hard rules
matter. Never paraphrase a prompt block, and never reconstruct one from memory.

**Parse it as Markdown, not by line-grep.** A recipe is an `# ` title followed by `## ` (H2)
sections — there is **no YAML frontmatter**, so do not look for any. A `#` inside a fenced code
block is **not** a heading (it's a comment in an example prompt). Skip the `## Changelog`
section — it is not part of the cook.

## Ground rules (non-negotiable)

- **Use the Senzing MCP. Do not rely on general training.** This is the recipes' own House Rule,
  baked into every prompt. All Senzing facts, attributes, SDK signatures and code come from the
  MCP tools (`get_capabilities`, `search_docs`, `mapping_workflow`, `sdk_guide`,
  `generate_scaffold`, `reporting_guide`, …) — never from memory.
- **Never simulate entity resolution.** If the Senzing SDK isn't installed/running, say so and hand off to
  the `install` skill — never fabricate scores, matches or merges.
- **PII stays local.** Repo ingredients are synthetic and safe. If the user swaps in their own
  data, its records are only ever touched by SDK code you run locally via Bash — never pasted into
  a hosted tool call. Bake that into the load prompt.
- **Run the recipe's prompts as written.** The chef put the exact hard rules, data-source names,
  and serve preferences in each fenced prompt. Execute them; don't paraphrase them away. Hard rules
  are **cumulative** — later steps say "keep all previous hard rules in force," so carry them.

## Procedure

**Inputs.** `$ARGUMENTS` may name a recipe by `id` (e.g. `customer-360-crm-online`) or by title
words. Match it against the catalog `id`s; on a fuzzy/multiple match, confirm which before cooking.

1. **Pre-flight FIRST — run `doctor`.** A recipe ends in a *served* result (a loaded Senzing SDK **and**
   an interactive app/visual), so clear the whole path **before** investing in a cook — don't march
   into a recipe that can't reach its plate. `doctor` checks it all in one pass: sources reachable
   (`mcp.senzing.com` allowlisted; the recipes are bundled and need no domain), host shell writable, Senzing software
   deployable (SDK / license / DB), and **interactive-outcome capability**. Act on its verdict
   before cooking:

   **A red verdict is a cue to take the degraded path, not permission to stop and ask.** This is
   the way this step fails, it does not look like a failure, and CI has caught it: `doctor` probed
   the host beautifully, reported no SDK, and the run's final message was the status table plus
   "which would you like?" — so the recipe was never opened and `install` was never reached. The
   user asked to cook and got an environment report and a menu. `doctor` says the same thing about
   itself: "A no-SDK verdict is the caller's cue to take its degraded path — **never** a reason to
   stop short of it." Say what you found in one line, then **take the path below in the same
   turn**. None of these bullets is a question, and a host that is merely sandboxed or reduced is
   not a reason to abandon the request.

   **These bullets are the whole list — not examples to reason around.** A host that is reduced,
   sandboxed, or restricted in some way none of them names is still one of these cases: take the
   closest one, never a fourth stop of your own. And mapping the ingredients, scaffolding the
   loader, or writing plan files **is** the Cook step — do not do it here, and do not offer it as
   an option either. Ending on "which would you like?" over a choice that includes the forbidden
   act is the same violation as performing it. **How to cook is part of the cook.** On a host that
   cannot cook yet, do not put the license decision or a smaller sample ("cook with just 500
   records") to the user as a choice: those are Cook-step decisions, and a reply that ends "attach
   a license, request the evaluation one, or go with the 500-record sample?" has offered the cook.
   Do NOT state the record count, the unlicensed limit, a license or the ingredient files here —
   CI caught "this recipe loads ~1,600 records, over the 500-record limit — do you have a license?"
   appended to a correct hand-off, which is the license decision put to the user as a choice. `install`
   owns the license conversation. Hand off to `install` and say nothing about what happens after it.
   - **the Senzing SDK can't deploy** → still identify and read the named recipe (step 2/3) so you can
     name it (mission, kitchen, time — not its Setup needs), **then** hand off to the **`install`** skill without asking first.
     **Order matters: read the recipe BEFORE you invoke `install`** — `install` asks its question
     and ends the turn, so a read you leave for afterwards is never made (CI caught a run that went
     doctor → `install` and never opened the recipe it was asked to cook). `Read`
     `cookbook/cookbook.md`, match the id, `Read` `cookbook/recipes/<id>.md`, and only then invoke
     `install` (it
     surfaces the license agreement, runs the official steps and verifies with `doctor`; do not
     route around it via `sdk_guide(topic="install")` directly — if an evaluation license is
     needed, `submit_feedback(category='license_request')`'s description states the current
     terms). Don't cook over a Senzing SDK that won't stand up, and don't stop at the diagnosis
     either. **You will already hold the platform's install steps** — `doctor` fetched them with
     `sdk_guide(topic="install")` — **and that is exactly when to hand off, not a reason to skip it.**
     CI caught a run that, holding those steps, wrote the install message itself and ended it
     with "attach a license file, or I can request a free evaluation license" plus an offer to
     copy the recipe's ingredient files: a Cook-step license choice and an offer to cook. Your next
     action after reading the recipe is `Skill(senzing:install)` with `args` set to doctor's
     platform id only (no language — see the banner); its first message is the one the user reads. **Hand off; do not
     run the install flow yourself in the message, and do not announce the cook.** A reply that stops on a menu
     ("Before I can cook, three things need your input: the license agreement, your language, whether you have a
     license file or want the evaluation one") and ends "Once I have those, I'll install Senzing + Java, stand up a
     local instance, then cook the recipe's Prep → Cook → Plate → Plus steps" has asked Cook-step questions and
     proposed the cook. Invoke `install` (it asks what installing needs, in one message) and stop; do not say the
     recipe will resume or name its steps.
     **The license agreement URL must appear in the reply the user reads**, not only inside a
     sub-skill's own output: state `https://senzing.com/end-user-license-agreement/` in your
     message before anything installs. Delegating the hand-off does not discharge this — a run
     that routes correctly but leaves the user never seeing the agreement has skipped a
     compliance step, which is why it is asserted rather than assumed.
   - **`mcp.senzing.com` is blocked** → this one IS a stop: ask the user to allowlist that domain
     now. Nothing downstream works without it, which is what makes it different from the bullets
     around it. Recipe text is never a reason to ask for a domain: it is bundled, so there is
     nothing to fall back to and nothing to allowlist for it.
   - **No live-app surface here** (cloud sandbox, chat-only host or a reduced sub-agent) → say so
     plainly: the recipe's *Plate* can't be a live `localhost` server here. Then **make** the
     honest substitution — map → load → resolve **plus a self-contained interactive HTML5
     artifact** you deliver as a download — and mention that **Claude Code** gives the literal
     live-server plate. Substitute the plate; do not put the substitution to the user as a choice
     and wait. Don't pretend the plate will render where it can't.

   (Browsing the catalog, and reading the recipe the user named, are fine to attempt either way;
   committing to cook is not.)
2. **Pick a recipe.** If no recipe was named (or the match is unclear), `Read` the bundled
   catalog (`cookbook/cookbook.md`) per *Read verbatim* and present it. Each entry is an
   `### [Title](recipes/<id>.md)` heading, an italic metadata line of ` · `-separated fields
   (currently category · difficulty · where it runs · rough duration · author), and a
   `**What you'll make:**` line. Show the title, that metadata line as-is and the
   what-you'll-make line — render the fields the catalog actually carries rather than a fixed
   list, so a change upstream degrades to "one fewer field" instead of a wrong label. Then ask
   which to cook, naming only titles and categories that appear in the bundled catalog. Do not
   suggest a use case the catalog does not list: the catalog alone decides what exists, whatever
   the user or this skill's own description happens to mention — so when asked "is there a …
   recipe?", answer from the catalog you just read, never from memory of an earlier version of
   it. You may add one line pointing to
   [the Recipes page on senzing.com](https://senzing.com/cookbook-recipes/) for browsing the same
   catalog on the web. If one was named, skip to step 3.
3. **Load the recipe.** `Read` the bundled `cookbook/recipes/<id>.md` per *Read verbatim*. Read the
   title and body. Show the user the
   recipe's identity up front: **title, the mission, a one-line take from the Chef's Note,
   difficulty, kitchen, estimated time**, and surface the recipe's own "before you cook" reminders
   (use your most capable model; *your result will look different each run*; the video is
   illustrative). State the recipe's identity and continue — **no confirmation gate here**; the
   only gates are loading into the user's existing repository (step 5) and any merge/split
   (step 6).
4. **Setup — settle the particulars, then cook.** From the *Setup: What you'll need* section
   (Senzing deployment and host capability were already cleared in pre-flight). Confirming a fact
   **against a tool** is required below; stopping to put a question to the user and waiting for
   the answer before you continue is not — settle these in the same turn:
   - **Kitchen:** stand up the platform the recipe targets (`local`, `aws`, …) per its *Setup*/*Prep*
     prompt.
   - **Language:** **do not assume Python.** Take the language the recipe or the user names, and
     confirm it is supported on this platform via
     `sdk_guide(topic="install", platform=…, language=…)` → `compatibility_notes` — that is the
     confirmation that matters here, and it is a check against a tool, not a question to the user.
     Do not carry the support matrix from memory. Only if neither the recipe nor the user names a
     language, ask — and say which one you will use if no answer comes, rather than stopping.
   - **Ingredients:** the recipes' sample files are **not** in the bundle and **you do not fetch
     them**. The Claude directory accepts only Markdown, text, JSON, YAML and images from a
     non-Verified organization, so the `.csv`/`.jsonl` ingredients cannot ship inside the plugin
     (a version that carried them was refused outright), and this skill downloads nothing. That
     matches how the recipes are written: they tell the reader to get the files and **attach them
     to the chat or drop them in the working folder**. So relay that instruction — name the files
     the recipe names and point the user at
     [the cookbook's ingredients folder](https://github.com/senzing/recipes/tree/main/ingredients)
     to download them. A bundled recipe's own ingredient link is relative (`../ingredients/…`) and
     will not resolve from inside the plugin, so give the user that GitHub link instead of the
     relative one. Then wait for the files: ask for the path rather than guessing one, exactly as
     the recipes say. They are synthetic sample data — say so. If the user brings their own data
     instead, take the paths, keep PII local, and note where the mapping will differ.
   - **Workspace:** use the location the user named ("this directory", a path) if they gave one,
     otherwise a default (`~/sz-workspace` or `$SZ_WORKSPACE`), and thread it through
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
   - **Gate the writes — the one gate, and only it.** Load into a fresh scratch repository by
     default: that target is throwaway and touches nothing of theirs, so **state** it and the
     record counts and keep going — it is a narration, not a question. Touch the user's existing
     or production Senzing only on their explicit request, and there confirm the target and the
     counts first and wait. Do not manufacture a gate for the scratch case; step 3 named the only
     two, and this is one of them.
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
   the demo **video** if the recipe links one (it appears inline, near the top). If the recipe
   loaded records, close with the engine work as counters taken from the code that ran:
   `add_record` calls made, `process_redo_record` calls made and the engine's version and build
   number (`SzProduct.get_version()` returns `VERSION` and `BUILD_NUMBER`). Read them off the
   counters, never off what you expect them to be — a dish nobody cooked cannot produce a build
   number it never asked the engine for.
   Say it as one line, in exactly this shape:
   `Engine work: <N> add_record calls, <M> process_redo_record calls, engine <VERSION> build <BUILD>.`

Outcome: the recipe's finished dish — a real, loaded, resolved Senzing solution on the user's
machine, served through its place setting, built by driving the chef's prompts and grounded in the
Senzing MCP.
