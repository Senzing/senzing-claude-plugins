#!/usr/bin/env bash
# Non-blocking PostToolUse hook (Write|Edit).
# Warns (never blocks) if a file that looks like Senzing SDK code was written without a
# source-URL provenance comment — a gentle nudge toward invariant "provenance intact".
# Always exits 0: this is advisory, not a gate.
#
# OUTPUT: hook JSON on stdout. For a PostToolUse hook that exits 0, plain stdout is
# NOT added to the model's context and stderr reaches nobody — the previous version
# wrote its nudge to stderr, so it was invisible. `additionalContext` is the only
# exit-0 channel the model actually sees.
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

# Trigger only on SDK symbols, not the bare word "senzing" (a comment like
# "# no senzing here" must not fire). Per-binding module/namespace roots plus the
# Sz* class family. Case-sensitive on purpose.
# NOTE: `\b` is a GNU-grep extension not honored by BSD/macOS grep; use an explicit
# non-letter boundary class instead so the match behaves the same on both.
SDK_SYMBOLS='senzing_core|from senzing |import senzing|senzing\.|com\.senzing|Senzing\.Sdk|sz_rust_sdk|@senzing/|[^A-Za-z]Sz(Engine|Config|Product|Diagnostic|Environment|Error|Exception|AbstractFactory|CoreEnvironment|Flag)'

grep -qE "$SDK_SYMBOLS" "$FILE_PATH" 2>/dev/null || exit 0
grep -qiE 'https?://' "$FILE_PATH" 2>/dev/null && exit 0

MSG="senzing: $FILE_PATH looks like Senzing SDK code but has no source-URL provenance comment; keep the attribution (source URL) that generate_scaffold / find_examples / sdk_guide returned with the snippet."

if command -v jq >/dev/null 2>&1; then
  jq -cn --arg m "$MSG" '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$m}}'
else
  ESC="$(printf '%s' "$MSG" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s"}}\n' "$ESC"
fi

exit 0
