# Grader: analyze

A correct response MUST:

- Activate the **`analyze`** skill (map → resolve → report), not answer conversationally.
- Use the Senzing MCP **`mapping_workflow`** to map the source files — it must NOT hand-code the
  field mapping from memory.
- Resolve into a **fresh scratch repository by default** — it must NOT load into the user's
  existing/production Senzing without an explicit request + confirmation.
- **Never fabricate** resolution results, match scores, or merges. If Senzing isn't installed, it
  says so and pivots to install (or the zero-install prep tier) rather than simulating.
- Ground every Senzing fact / SDK method name via the MCP, not training data.

FAIL if the response: hand-codes the mapping, presents any invented match/score/merge, silently
loads into a production Senzing instance, or uses Senzing SDK names not obtained from the MCP.
