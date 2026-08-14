#!/usr/bin/env bash
# Package the Senzing plugin as an uploadable .zip release artifact.
#
# The archive follows the canonical layout — a single top-level plugin folder
# with `.claude-plugin/plugin.json` nested inside it:
#
#   senzing-claude-plugin-<version>.zip
#   └── senzing/
#       ├── .claude-plugin/plugin.json
#       ├── skills/ agents/ hooks/ .mcp.json ...
#
# That .zip installs three ways: Claude Desktop (Settings -> Plugins -> Add ->
# Upload a file), `claude --plugin-url <url>` (CI build artifact), and
# `claude --plugin-dir <zip>` (local test). Re-uploading a newer same-named .zip
# updates the plugin in place.
#
# Usage: scripts/build-plugin-zip.sh [VERSION]
# VERSION defaults to the plugin.json version (CI derives it from the git tag).
set -euo pipefail
cd "$(dirname "$0")/.."

PLUGIN_DIR="plugins/senzing"          # source plugin root
PLUGIN_NAME="senzing"                 # top-level folder inside the archive
ARTIFACT="senzing-claude-plugin"      # release .zip basename (download filename)
OUT_DIR="dist"
PLUGIN_JSON="$PLUGIN_DIR/.claude-plugin/plugin.json"

command -v jq  >/dev/null 2>&1 || { echo "jq is required" >&2; exit 1; }
command -v zip >/dev/null 2>&1 || { echo "zip is required" >&2; exit 1; }

VERSION="${1:-$(jq -r '.version' "$PLUGIN_JSON")}"

# Validate the plugin manifest when the Claude CLI is available (CI installs it;
# check.sh does the same). Never a hard failure locally if the CLI is absent.
if command -v claude >/dev/null 2>&1; then
  echo "== claude plugin validate =="
  claude plugin validate "$PLUGIN_DIR" --strict
fi

# Stage a clean copy so the archive has a single `senzing/` root and no cruft.
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -R "$PLUGIN_DIR" "$STAGE/$PLUGIN_NAME"
find "$STAGE" -name '.DS_Store' -delete

mkdir -p "$OUT_DIR"
OUT="$(pwd)/$OUT_DIR/$ARTIFACT-$VERSION.zip"
rm -f "$OUT"
( cd "$STAGE" && zip -qr "$OUT" "$PLUGIN_NAME" )

echo "Built $OUT_DIR/$ARTIFACT-$VERSION.zip"
unzip -l "$OUT" | tail -n +2 | head -8
