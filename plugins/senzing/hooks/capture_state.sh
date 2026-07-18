#!/usr/bin/env bash
# Non-blocking PostToolUse hook for mapping_workflow.
# Advisory state capture: mirrors the returned workflow `state` to a file so a later
# call can re-read it instead of reconstructing it from conversation memory (the
# design's #1 opaque-state mitigation). Best-effort — never blocks, always exits 0.
set -uo pipefail

INPUT="$(cat)"

# jq is required to parse the payload; without it, quietly no-op.
command -v jq >/dev/null 2>&1 || exit 0

# Extract the workflow `state` object. Try the common payload shapes.
STATE="$(printf '%s' "$INPUT" | jq -c '(.tool_response.state // .state // empty)' 2>/dev/null || true)"

[ -z "${STATE:-}" ] && exit 0
[ "$STATE" = "null" ] && exit 0

# Extract a workflow id (best-effort across shapes). Fall back to "current".
WORKFLOW_ID="$(printf '%s' "$INPUT" | jq -r '(.tool_response.workflow_id // .tool_response.state.workflow_id // .state.workflow_id // .workflow_id // empty)' 2>/dev/null || true)"
[ -z "${WORKFLOW_ID:-}" ] && WORKFLOW_ID="current"

# Sanitize the id so it is safe as a filename component.
WORKFLOW_ID="$(printf '%s' "$WORKFLOW_ID" | tr -c 'A-Za-z0-9._-' '_')"

# Must resolve to the SAME workspace the analyze/field-mapper skills use, or the state
# backup lands where the skill never looks. Skills default to ~/sz-workspace (override via
# SZ_WORKSPACE). Keep this in lockstep with the skills' workspace convention.
WORKSPACE="${SZ_WORKSPACE:-$HOME/sz-workspace}"
mkdir -p "$WORKSPACE" 2>/dev/null || exit 0

printf '%s\n' "$STATE" > "$WORKSPACE/.sz-state-${WORKFLOW_ID}.json" 2>/dev/null || true

exit 0
