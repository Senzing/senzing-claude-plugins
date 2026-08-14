---
name: demo
description: >
  Show Senzing entity resolution working on recognizable sample data. Use when the user wants to
  see Senzing in action, evaluate it, or asks "show me entity resolution", "give me a demo",
  "does this actually work". Loads a real sample dataset into the user's Senzing and renders the
  before/after. Honest: if no Senzing is installed it pivots to install/eval instead of faking.
argument-hint: "[dataset]"
allowed-tools: Bash, Read, Write, Task, Skill, mcp__plugin_senzing_senzing__*
---

# Demo Senzing on sample data

Grounded by the **Senzing MCP server**. Never simulate results.

**Inputs.** `$ARGUMENTS` may name a dataset (`las-vegas`, `london`, `moscow`, `truthset`). If none
is given, default to `truthset` and tell the user which you're using; call `get_sample_data` with
`dataset='list'` first if they'd rather choose. No user data is needed — the demo uses sample data.

## Narrate progress as you cook (unprompted, no response required)

A demo is a **spectator sport** — the user is watching, not driving. Do **not** run silently through
the long stretch (install → map → load → resolve → report). A wall of "ran a command / done" with
nothing to read for 15+ minutes is a failed demo *even if the result is correct* — the user is left
to "wonder." As each milestone completes, surface a short, concrete **progress checkpoint** on your
own initiative: **informational, never a question**, and never something the user must answer to
continue. (Answer-required gates stay reserved for the only two that matter: loading into a
**production** repo, and any **merge/split**.)

Post a checkpoint at each milestone, each carrying **real numbers from the actual run** — never
estimated, never fabricated:
- **Environment ready** — Senzing version + database kind.
- **Mapped** — file, row count, which source fields mapped to which Entity-Spec attributes, validation verdict.
- **Loaded** — records loaded for *this* source + running total, throughput, and error count (should be 0). Report **per file as it lands**, not once at the end.
- **Resolved** — records → entities and the **compression ratio**; note the redo queue drained.

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

1. Pre-flight with `doctor`. **If there is no running Senzing**, do not fake a demo — use
   `sdk_guide(topic="install")` to get them set up (a free 10-day eval license can be requested via
   `submit_feedback`), and
   offer to resume the demo the moment install completes. If the user can't or won't install now,
   offer the zero-install tier: pull the truth-set sample via `get_sample_data`, run the mapping
   workflow on it, and show the validated Senzing-ready records plus 2-3 raw record pairs that
   clearly describe the same person across sources. Label it plainly: *"This is the data
   preparation Senzing would consume — actual resolution requires an installed Senzing, which I
   can set up for you."* Never present any match, score, or merge as a result.
2. With a working Senzing: call `get_sample_data` for a ground-truthed dataset (Las Vegas /
   London / Moscow, or the Senzing truth set). Map it (reuse the `analyze` flow). Before loading,
   confirm explicitly: *"About to load ~N sample records into your <db> Senzing database under
   data source <DS> — proceed? (If this instance holds real data, I can set up a scratch SQLite
   repository for the demo instead.)"* Prefer the scratch-repository offer whenever doctor shows
   existing entities. Then Bash-load it into their Senzing.
3. **Deliver analytics — required; the demo is not complete until this ships.** A demo is
   **load → analytics**, not load alone. Over the **real** results, use `reporting_guide` for the
   report/entity-view + visualization patterns and produce BOTH:
   - a **report** — the before/after story: raw record count → resolved entity count, and a few
     non-obvious merges, each with a `why` explanation; and
   - a **visualization** — a shareable dashboard (an Artifact) that renders that before/after.

   The rendered report-and-visualization IS the demo, not trailing commentary — produce it without
   waiting to be asked.
