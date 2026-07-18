# Grader: build

A correct response MUST:

- Activate the **`build`** skill and generate the code with the MCP (**`generate_scaffold`** /
  `sdk_guide` / `find_examples`) — it must NOT hand-write Senzing SDK code from memory.
- Use **correct V4 SDK names** obtained from the MCP (e.g. `SzEngine` search), not deprecated or
  invented method names.
- Preserve the **source-URL provenance** comment on the generated code.
- Offer to run it against the user's own Senzing only after showing the code.

FAIL if the response: hand-writes SDK code from training data, uses wrong/confabulated method or
attribute names, or strips the source-URL provenance.
