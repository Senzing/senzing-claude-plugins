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
3. Render the before/after over the **real** results: raw record count → resolved entity count,
   and a few non-obvious merges with a `why` explanation. Deliver as a shareable Artifact.
