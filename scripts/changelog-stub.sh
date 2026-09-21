#!/usr/bin/env bash
# Insert a lockstep "version-only sync" stub into CHANGELOG.md.
#
# Usage: scripts/changelog-stub.sh <version> [date] [changelog]
#
# The stub goes immediately BEFORE the first existing "## [x.y.z]" release heading,
# i.e. AFTER whatever is pending under "## [Unreleased]". Splicing it directly under
# the Unreleased heading (the first version of this logic) would have pushed pending
# notes under a release that claims "no code change". If no release heading exists
# yet, the stub is appended. scripts/check.sh check 7 needs the heading to match
# plugin.json; check 7b runs this script against a fixture with pending content.
set -euo pipefail

version="${1:?usage: changelog-stub.sh <version> [date] [changelog]}"
date="${2:-$(date -u +%F)}"
file="${3:-CHANGELOG.md}"

if grep -qF "## [$version]" "$file"; then
  echo "changelog-stub: $file already has ## [$version]; nothing to do" >&2
  exit 0
fi

tmp="$(mktemp)"
awk -v v="$version" -v d="$date" '
  function stub() {
    print "## [" v "] - " d
    print ""
    print "### Changed"
    print ""
    print "- Bump to MCP server **v" v "** (lockstep sync); the plugin carries no code change."
    print ""
  }
  /^## \[[0-9]/ && !done { stub(); done = 1 }
  { print }
  END { if (!done) { print ""; stub() } }
' "$file" > "$tmp"
mv "$tmp" "$file"
