#!/usr/bin/env bash
# Non-blocking PostToolUse hook for mapping_workflow.
# Advisory state capture: mirrors the returned workflow `state` to a file so a later
# call can re-read it instead of reconstructing it from conversation memory (the
# design's #1 opaque-state mitigation). Best-effort — never blocks, always exits 0.
#
# OUTPUT CONTRACT (skills depend on this exact path — keep in lockstep):
#   <state.workspace_dir>/.sz-state.json
# The `analyze` skill and the `field-mapper` agent read that file. There is NO
# workflow id in a mapping_workflow state (the state is {step, step_name,
# file_paths, workspace_dir}), so the file name carries none. The workspace is
# taken from the state object itself because the server echoes back the exact
# workspace_dir the skill passed at `start`; a hook process inherits the Claude
# Code process env, NOT the Bash tool's env, so SZ_WORKSPACE/HOME are only a
# last-resort fallback here.
#
# PAYLOAD SHAPE (verified against a live call, 2026-09-18): for an MCP tool the
# PostToolUse `tool_response` is a CallToolResult content array —
#   [{"type":"text","text":"<compact json>\n\n[REMINDER: ...]"}]
# (some hosts wrap it as {"content":[...]}). It is NOT an object with a `.state`
# key, and the text block is NOT pure JSON: the server appends an
# anti-confabulation footer that must be stripped before `fromjson`. The previous
# version of this hook assumed `.tool_response.state` and never wrote a file.
set -uo pipefail

INPUT="$(cat)"

# jq is required to parse the payload; without it, quietly no-op.
command -v jq >/dev/null 2>&1 || exit 0

STATE="$(printf '%s' "$INPUT" | jq -c '
  def blocks:
    if type == "array" then .
    elif type == "object" and has("content") then .content
    else [] end;
  def parsed_texts:
    map(select(type == "object" and .type == "text") | .text
        | sub("\\s*\\[REMINDER:[^\\]]*\\]\\s*$"; "")
        | try fromjson catch empty);
  (.tool_response // empty) as $r
  | ([$r | select(type == "object" and has("state"))] + ($r | blocks | parsed_texts))
  | map(select(type == "object") | .state // empty | select(type == "object"))
  | first // empty' 2>/dev/null || true)"

[ -z "${STATE:-}" ] && exit 0

WORKSPACE="$(printf '%s' "$STATE" | jq -r '.workspace_dir // empty' 2>/dev/null || true)"
[ -n "${WORKSPACE:-}" ] || WORKSPACE="${SZ_WORKSPACE:-${HOME:-/tmp}/sz-workspace}"

mkdir -p "$WORKSPACE" 2>/dev/null || exit 0

# Write-then-rename so a reader never sees a half-written file.
TMP="$WORKSPACE/.sz-state.json.tmp.$$"
if printf '%s\n' "$STATE" > "$TMP" 2>/dev/null; then
  mv -f "$TMP" "$WORKSPACE/.sz-state.json" 2>/dev/null || rm -f "$TMP"
else
  rm -f "$TMP" 2>/dev/null
fi

exit 0
