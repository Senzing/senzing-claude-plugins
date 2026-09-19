# Hook fixtures

Real PostToolUse payloads, fed to the hooks by `scripts/check.sh` (section 6) so a hook
that silently matches nothing is caught before it ships.

- `mapping_workflow_start.payload.json` — a live `mapping_workflow action=start`
  response captured 2026-09-18, in the shape Claude Code actually delivers: `tool_response`
  is a CallToolResult **content array** whose single text block is compact JSON **plus** the
  server's `[REMINDER: ...]` footer. `__WORKSPACE__` is substituted at test time.
- `write_tool.payload.json` — a `Write` payload. `__FILE__` / `__DIR__` are substituted at
  test time; the test writes the file the hook is expected to inspect.
