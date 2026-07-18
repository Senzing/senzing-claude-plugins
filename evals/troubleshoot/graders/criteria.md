# Grader: troubleshoot

A correct response MUST:

- Activate the **`troubleshoot`** skill and call the MCP **`explain_error_code`** for `0033E`.
- Report the **real** cause — SENZ0033 is an unknown (DATA_SOURCE, RECORD_ID) reference
  ("Unknown record") — and the MCP's resolution steps.
- Derive the explanation from the MCP result, **not** from the model's training data.

FAIL if the response: explains the error from memory, invents a different meaning, or fabricates
resolution steps not grounded in the MCP.
