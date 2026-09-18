#!/usr/bin/env bash
# Non-blocking SessionStart hook: greets once that the Senzing coworker is ready.
# First-run only — writes a marker file and stays silent on every later session.
# (The "always ground via the MCP, never training data" rule lives in the skill
#  instructions, not in this user-facing banner.)
set -euo pipefail

# HOME may be unset in a hook's environment (hooks inherit the Claude Code process
# env, not a login shell); under `set -u` a bare $HOME then aborts the hook.
marker_dir="${CLAUDE_PLUGIN_DATA:-${HOME:-/tmp}/.senzing-er}"
marker="${marker_dir}/.greeted"

# Already greeted → stay silent.
if [ -f "$marker" ]; then
  exit 0
fi

mkdir -p "$marker_dir" 2>/dev/null || true
: > "$marker" 2>/dev/null || true

# `ask` leads: it is the only skill that works on an information-only host (no
# shell, no Senzing install) — everything else needs at least one of those.
cat <<'BANNER'
Senzing coworker ready. Grounded by the hosted Senzing MCP (mcp.senzing.com).
Try: /senzing:ask <question>   /senzing:install   /senzing:doctor
     /senzing:analyze <files>  /senzing:demo      /senzing:build
BANNER

exit 0
