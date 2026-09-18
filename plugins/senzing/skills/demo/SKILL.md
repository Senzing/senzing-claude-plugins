---
name: demo
description: >
  The same end-to-end run as analyze, but on Senzing's own sample data — so the user sees entity
  resolution working without having to find, prepare, or share any data of their own. Map, load,
  resolve and show the before/after in one pass against a throwaway scratch repository. Use when
  the user wants to see Senzing in action, evaluate it, or asks "show me entity resolution", "give
  me a demo", "prove this works", or a skeptical "does this actually work?" about the product.
  Real results only — if no Senzing is installed it offers install rather than faking one. Runs
  doctor first. Not for the user's own files (use analyze), a named cookbook use case (use
  recipes), or "does MY setup work?" (use doctor).
argument-hint: "[dataset]"
allowed-tools: Bash, Read, Write, Task, Skill, mcp__plugin_senzing_senzing__*
---

# Demo Senzing on sample data

Grounded by the **Senzing MCP server**. Never simulate results.

**Inputs.** `$ARGUMENTS` may name a dataset. Get the valid names from
`get_sample_data(dataset='list')` — never from memory; the list changes with the server. If none is
given, default to the truth set (the one dataset that ships with ground truth) and tell the user
which you're using; offer the list if they'd rather choose. No user data is needed.

## Narrate progress as you cook (unprompted, no response required)

A demo is a **spectator sport** — the user is watching, not driving. Do **not** run silently through
the long stretch (install → map → load → resolve → report). A wall of "ran a command / done" with
nothing to read for 15+ minutes is a failed demo *even if the result is correct* — the user is left
to "wonder." As each milestone completes, surface a short, concrete **progress checkpoint** on your
own initiative: **informational, never a question**, and never something the user must answer to
continue. (Answer-required gates stay reserved for the only two that matter: loading into the
user's **existing** repository, and any **merge/split**.)

Post a checkpoint at each milestone, each carrying **real numbers from the actual run** — never
estimated, never fabricated:
- **Environment ready** — Senzing version + database kind.
- **Mapped** — file, row count, which source fields mapped to which Entity-Spec attributes, validation verdict.
- **Loaded** — records loaded for *this* source + running total, throughput, and error count (should be 0). Report **per file as it lands**, not once at the end.
- **Resolved** — records → entities and the **compression ratio**, taken only after the redo-queue
  probe (step 2d) reads 0 — report how many redo records it processed. Never write "redo queue
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
   truth-set sample via `get_sample_data`, run the mapping workflow on it, and show the validated
   Senzing-ready records plus 2-3 raw record pairs that clearly describe the same person across
   sources. Label it plainly: *"This is the data preparation Senzing would consume — actual
   resolution requires an installed Senzing, which I can set up for you."* Never present any
   match, score, or merge as a result.
2. With a working Senzing, run the `analyze` flow on sample data — same steps, same gates:
   - **Get the data — the full file, not the preview.** `get_sample_data` returns a handful of
     inline records to show the shape plus a `download_url` for the full file. Fetch the full file
     into the workspace using the fetch instruction exactly as the tool gives it, and map/load
     **that**; never demo on the inline preview. Describe the data honestly: the CORD datasets are
     **real historical records** for evaluation (tell the user so, as the tool requires) and carry
     **no** ground truth — only the truth set does. Do not call CORD "ground-truthed".
   - **Map** it with `analyze` step 3: drive `mapping_workflow` to an `approve` verdict for each
     source, with the same escape hatch.
   - **Load into a fresh scratch repository exactly as `analyze` step 4 does — no confirmation
     needed.** The scratch repo is throwaway and touches nothing of theirs. Load into the user's
     **existing** repository only on their explicit request, and then confirm the target and the
     record count first. Verify the load as `analyze` step 4 does (loaded vs submitted, error
     count) before going on.
   - **Drain the redo queue** as `analyze` step 5 does — get the probe from the MCP, drain to 0,
     report the number processed — before taking any entity count.
3. **Deliver analytics — required; the demo is not complete until this ships.** A demo is
   **load → analytics**, not load alone. Over the **real** results, use `reporting_guide` for the
   report/entity-view + visualization patterns and produce BOTH:
   - a **report** — the before/after story: raw record count → resolved entity count, and a few
     non-obvious merges, each with a `why` explanation; and
   - a **visualization** — a shareable dashboard (an Artifact) that renders that before/after.

   The rendered report-and-visualization IS the demo, not trailing commentary — produce it without
   waiting to be asked.
