#!/usr/bin/env bash
# Non-blocking PostToolUse hook (Write|Edit).
# Warns (never blocks) if a file that looks like Senzing SDK code was written without a
# source-URL provenance comment — a gentle nudge toward invariant "provenance intact".
# Always exits 0: this is advisory, not a gate.
set -uo pipefail

INPUT="$(cat)"

# Extract the written file path. Prefer jq; fall back to a permissive grep.
if command -v jq >/dev/null 2>&1; then
  FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)"
else
  FILE_PATH="$(printf '%s' "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"//; s/"$//' || true)"
fi

[ -z "${FILE_PATH:-}" ] && exit 0
[ -f "$FILE_PATH" ] || exit 0

# Only consider source files.
case "$FILE_PATH" in
  *.py|*.java|*.cs|*.rs|*.ts|*.js|*.go) ;;
  *) exit 0 ;;
esac

# Looks Senzing-related but has no URL comment → advisory warning on stderr.
# NOTE: `\b` is a GNU-grep extension not honored by BSD/macOS grep; use an explicit
# non-letter boundary class instead so the match behaves the same on both.
if grep -qiE 'senzing|[^A-Za-z]Sz[A-Z]' "$FILE_PATH" 2>/dev/null; then
  if ! grep -qiE 'https?://' "$FILE_PATH" 2>/dev/null; then
    echo "senzing: $FILE_PATH looks like Senzing SDK code but has no source-URL provenance comment; keep the attribution from generate_scaffold/find_examples." >&2
  fi
fi

exit 0
