#!/usr/bin/env bash
# Non-blocking SessionStart hook: greets once that the Senzing coworker is ready.
# First-run only — writes a marker file and stays silent on every later session.
# (The "always ground via the MCP, never training data" rule lives in the skill
#  instructions, not in this user-facing banner.)
set -euo pipefail

marker_dir="${CLAUDE_PLUGIN_DATA:-$HOME/.senzing-er}"
marker="${marker_dir}/.greeted"

# Already greeted → stay silent.
if [ -f "$marker" ]; then
  exit 0
fi

mkdir -p "$marker_dir" 2>/dev/null || true
: > "$marker" 2>/dev/null || true

cat <<'EOF'
Senzing coworker ready. Grounded by the hosted Senzing MCP (mcp.senzing.com).
Try: /senzing:analyze <files>   /senzing:demo   /senzing:build   /senzing:doctor
EOF

exit 0
