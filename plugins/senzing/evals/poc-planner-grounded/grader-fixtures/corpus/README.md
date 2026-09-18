# Grader fixtures — verbatim tool output the plan is REQUIRED to quote

Captured 2026-09-18 from the plugin's own server (`mcp__plugin_senzing_senzing__*`, index built
2026-09-18 17:43 UTC). `scripts/check-poc-graders.py` runs every `not_contains` regex grader in the
`poc-planner-*` cases against each file here. **Any hit is a false-fail in waiting**: the body
makes the plan quote this text, so a grader that fires on it fails a correct run. The template
alone is the wrong fixture — the template is clean; the quotes are not (the Hardware Sizing FAQ
says "Phase 1/2/3" nine times).

Refresh by re-running the same calls against the plugin's server only — a differently-configured
`senzing` server has leaked an internal-only chunk in the past.

| File | Call |
|---|---|
| `hardware-sizing-faq.txt` | `search_docs(query="hardware sizing POC evaluation minimum requirements", max_results=5)` → result 1 excerpt (`local://hardware-sizing-faq.md`) |
| `poc-article-chunks.txt` | every chunk of "The Path to a Successful Proof of Concept (PoC)" returned by the step-1 query set plus heading re-queries |
| `reporting-guide-quality.json` | `reporting_guide(topic="quality")` |
| `reporting-guide-evaluation-python.json` | `reporting_guide(topic="evaluation", language="python")` (design concepts; the code sample omitted) |
| `sdk-guide-install-tree.json` | `sdk_guide(topic="install")` |
| `sdk-guide-install-linux-apt-python.json` | `sdk_guide(topic="install", platform="linux_apt", language="python")` (`direct_download` package list omitted) |
| `sdk-guide-load-python-755000.json` | `sdk_guide(topic="load", language="python", record_count=755000)` (code sample omitted; notes, anti-patterns and `compatibility_notes` kept) |
| `database-tuning-chunks.txt` | `search_docs(query="PostgreSQL database tuning", category="database", max_results=5)` excerpts |
| `get-sample-data-list.json` | `get_sample_data(dataset="list")` |
| `submit-feedback-description.txt` | the `submit_feedback` tool description (the license terms the body quotes) |
