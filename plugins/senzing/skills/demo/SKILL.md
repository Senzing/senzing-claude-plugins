---
name: demo
description: >
  The same end-to-end run as analyze, but on Senzing's own sample data — so the user sees entity
  resolution working without having to find, prepare, or share any data of their own. Validate,
  load, resolve and show the before/after in one pass against a throwaway scratch repository. Use when
  the user wants to see Senzing in action, evaluate it, or asks "show me entity resolution", "give
  me a demo", "prove this works", or a skeptical "does this actually work?" about the product.
  Real results only — if no Senzing is installed it offers install rather than faking one. Runs
  doctor first. Not for the user's own files (use analyze), a named cookbook use case (use
  recipes), or "does MY setup work?" (use doctor).
argument-hint: "[dataset]"
allowed-tools: Bash, Read, Write, Agent, Skill, mcp__plugin_senzing_senzing__*
---

# Demo Senzing on sample data

Grounded by the **Senzing MCP server**. Never simulate results.

**Inputs.** `$ARGUMENTS` may name a dataset. Get the valid names from
`get_sample_data(dataset='list')` — never from memory; the list changes with the server. If none is
given, default to `truthset` (the smallest) and describe it to the user from its `list`
description — attribute nothing to a dataset that the tool response does not say; offer the
list if they'd rather choose. No user data is needed.

## Narrate progress as you cook (unprompted, no response required)

A demo is a **spectator sport** — the user is watching, not driving. Do **not** run silently through
the long stretch (install → validate → load → resolve → report). A wall of "ran a command / done" with
nothing to read for 15+ minutes is a failed demo *even if the result is correct* — the user is left
to "wonder." As each milestone completes, surface a short, concrete **progress checkpoint** on your
own initiative: **informational, never a question**, and never something the user must answer to
continue. (Answer-required gates stay reserved for the only two that matter: loading into the
user's **existing** repository, and any **merge/split**.)

Post a checkpoint at each milestone, each carrying **real numbers from the actual run** — never
estimated, never fabricated:
- **Environment ready** — Senzing version + database kind.
- **Validated** — file, record count, data sources, feature coverage from the analyzer, verdict.
- **Loaded** — records loaded for *this* source + running total, throughput, and error count (should be 0). Report **per file as it lands**, not once at the end.
- **Resolved** — records → entities and the **compression ratio**, taken only after the redo-queue
  probe (the redo bullet in step 2) reads 0 — report how many redo records it processed. Never write "redo queue
  drained" without having run that probe.

**Make it a visual, not a paragraph.** The failure mode on both sides is silence *and* a wall of
words — a demo watcher wants something to *glance at*, not read. Each checkpoint is a compact
visual: a **one-line stat line**, a **micro-table**, or a **one-line ASCII bar** — never prose. A
few lines, then move on. Examples (shape, not literal):

```
✓ Loaded CRM        1,000 records · 0 errors · 1.2k/s   (total 1,000)
✓ Loaded ONLINE       579 records · 0 errors · 1.1k/s   (total 1,579)
Resolved  1,579 records → 1,192 entities   (1.33× compression)
  records   ████████████████████  1,579
  entities  ███████████████       1,192
```

Prefer **many small, quick-to-scan updates** over one silent march *or* a dense report. The full
dashboard Artifact (step 3) is the finale — these checkpoints are the pulse on the way there, not a
second report.

1. Pre-flight with `doctor` (it clears network/allowlist, host shell, Senzing, **and**
   interactive-outcome capability up front). This demo's finale is a **dashboard Artifact** (step
   3) — a self-contained HTML5 visual — so it lands even on a cloud sandbox that can't serve a live
   `localhost` app; no live-server substitution is needed here. **If there is no running Senzing**,
   do not fake a demo — hand off to the **`install`** skill: it surfaces the license agreement,
   runs the official steps, and verifies with `doctor`. Do not route around it by calling
   `sdk_guide(topic="install")` directly. (If an evaluation license turns out to be needed,
   `submit_feedback(category='license_request')` requests one; its description states the current
   terms — do not quote a duration from memory.) Offer to resume the demo the moment install
   completes. If the user can't or won't install now, offer the zero-install tier: pull the
   sample via `get_sample_data` (see step 2 for the download), validate it with `analyze_record`,
   and show the validated Senzing-ready records. **Do not select or preview which records look
   alike — that is the engine's job, not yours, with or without an SDK present.** Picking the
   pairs yourself is the same invented-match the rule in step 2 bans; having no SDK makes it
   worse, not permitted, because nothing can check you. If asked to show duplicates exist, point
   at the dataset's own description from `get_sample_data`. Label it plainly: *"This is the data Senzing would consume — actual
   resolution requires an installed Senzing, which I can set up for you."* Never present any
   match, score, or merge as a result.
**Never name a match before Senzing has found one — in EVERY branch, including the
zero-install tier.** Until the engine has returned results you have no results: printing a record
id, name, email, DOB or pair as a "these look alike" preview invents them, and a caveat does not
make it safe. Pick nothing by resemblance; say which FIELDS Senzing would resolve on. This governs
step 1 as much as step 2 — having no SDK makes a guess worse, not permitted, because nothing can
check it.

2. With a working Senzing, run the `analyze` flow on sample data — same steps, same gates:
   - **Get the data — the full file, not the preview — and this is the one flow where *you*
     download it.** `get_sample_data` returns a handful of inline records to show the shape plus
     a `download_url` in its citation. Its own instruction says to present that URL and not
     download it yourself — that rule is for chat answers, where the user takes the file. Here
     the load code needs the file on disk, so fetch it into the workspace:
     `curl -fsSL <download_url> -o {workspace}/<dataset>.jsonl`, using the URL exactly as
     returned (if the response flags the download as capped or truncated, say so). Never demo
     on the inline preview. Describe the data honestly: it is **real data** for evaluation (tell
     the user so, as the tool requires), and say only what its `list` description says about it.
   - **Validate — do not map.** Sample records are already Senzing JSON (`DATA_SOURCE`,
     `RECORD_ID`, `FEATURES[…]`); running `mapping_workflow` on them would map Senzing JSON to
     Senzing JSON. Instead call `analyze_record(file_paths=[…], workspace_dir=…)`, run the
     analyzer it returns, and post the **Validated** checkpoint from its findings. Note the
     distinct `DATA_SOURCE` codes — the load step registers them. `mapping_workflow` is for the
     user's own data (`analyze`).
   - **Load into a fresh scratch repository exactly as `analyze` step 4 does — no confirmation
     needed.** The scratch repo is throwaway and touches nothing of theirs. Load into the user's
     **existing** repository only on their explicit request, and then confirm the target and the
     record count first. Verify the load as `analyze` step 4 does (loaded vs submitted, error
     count) before going on.
   - **Drain the redo queue** as `analyze` step 5 does — get the probe from the MCP, drain to 0,
     report the number processed — before taking any entity count.
   - **Name the storage target in the write-up** — the repository, never a record. These two
     rules sit next to each other and must not be confused: you MUST name where the data went,
     and you must NOT name what is in it. The closing message must say, in words, that the data
     went into a **throwaway scratch repository** and which storage backed it (the SQLite file, or
     `internal://`). A viewer of the result must never be left wondering whether a demo touched a
     real repository of theirs — and "I used a scratch repo" is the sentence that answers it.
   - **Never name a RECORD** (the rule above is about naming the STORAGE; this one is about its
     contents). **Never preempt the engine with your own duplicate-spotting.** Before the load has run you
     have no results, so naming likely matches invents them. Do not print a record id, name,
     email, or pair as a "these look like a match" preview, *even heavily caveated* — a run did
     exactly this, naming two name-variant pairs by DOB and license number before resolving
     anything. The demo's whole claim is that Senzing found it; a guess in the same message
     dilutes the one thing being demonstrated.
3. **Deliver analytics — required; the demo is not complete until this ships.** A demo is
   **load → analytics**, not load alone. Over the **real** results, use `reporting_guide` for the
   report/entity-view + visualization patterns and produce BOTH:
   - a **report** — the before/after story: raw record count → resolved entity count, and a few
     non-obvious merges, each with a `why` explanation; and
   - a **visualization** — a shareable dashboard (an Artifact) that renders that before/after.

   The rendered report-and-visualization IS the demo, not trailing commentary — produce it without
   waiting to be asked.
