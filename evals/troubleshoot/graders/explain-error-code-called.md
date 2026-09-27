---
type: tool_used
tool: mcp__plugin_senzing_senzing__explain_error_code
input_match: '"\s*:\s*"?(SENZ)?0*33E?(?![0-9])'
---

# Grader: the code looked up is the code the user asked about

Was `input_match: '(SENZ)?0*33E?'` — unanchored, so it matched the bare digits `33` ANYWHERE in
the serialized tool input. `{"error_code": "1033"}` contains `33` and passed; so did `0330`,
`3300` and a version string. The case is `0033E`, and looking up a different error while the
rubric grades "does the answer match the tool result" is precisely the failure this grader is the
deterministic half of.

The pattern is now anchored to the JSON **value** boundary: a closing key quote, the colon, an
optional opening value quote, then the code, then a not-a-digit lookahead. `(SENZ)?0*` and `E?`
keep every argument form `criteria.md` accepts (`0033E`, `0033`, `33`, `SENZ0033`), and the
optional value quote keeps a bare integer argument (`{"error_code": 33}`) passing. `1033`, `0330`
and `3300` no longer can: `0*` cannot consume a leading `1`, and the lookahead rejects a trailing
digit. Only fixed-width lookahead is used, so it means the same thing in every engine.
