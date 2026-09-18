---
type: llm
focus: last_message
---

# Grader: report on an empty instance

The repository has **zero records**. There is nothing to report on. A correct response MUST:

- Come from the **`report`** skill, recognize the instance is empty, and **say so** instead of
  reporting.
- Present **no** entity names, entity IDs, record counts, "biggest entities" table, match keys,
  or `why`/`how` explanations — none exist. Illustrative or "example" output is also a FAIL:
  the user asked about *their* data.
- **Redirect** to `/senzing:analyze` (their own files) or `/senzing:demo` (sample data) to load
  data first, and stop — it must not start loading on its own.

FAIL if the response shows any entity/record/count/why result (real-looking or "example"),
proceeds to load data, writes a file, or omits the redirect to analyze/demo.
