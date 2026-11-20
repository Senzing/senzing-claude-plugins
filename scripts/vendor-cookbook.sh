#!/usr/bin/env bash
# Vendor the Senzing Cookbook into the `recipes` skill.
#
# WHY THIS EXISTS. The `recipes` skill reads recipe instructions and then runs them.
# The Claude plugin directory refuses a plugin that downloads what it executes
# (findings RUNTIME_FETCH_EXEC, then "contains a download-and-run command"), and a
# commit pin did not satisfy it because the fetch itself is the objection. So the
# cookbook ships INSIDE the plugin and the skill only ever `Read`s it.
#
# The copy must not rot, so this script re-vendors from upstream and is run by
# `mcp-version-sync.yml` on every version bump: each published version carries the
# cookbook as it stood when that version was cut. Between releases, the
# `Cookbook whitelist still matches upstream` CI job surfaces drift.
#
# The file list is DERIVED from the upstream tree, never hardcoded, so a recipe added
# upstream is picked up automatically. Images and repo furniture are excluded: the
# skill never renders an image, and 1.4 MB of screenshots would be dead weight in
# every install.
#
# WHAT MAY BE VENDORED IS SET BY THE CLAUDE DIRECTORY, NOT BY TASTE. For an
# organization that is not Verified the directory accepts only Markdown, text, JSON,
# YAML and PNG/JPEG/GIF/WebP/ICO images, and cannot inspect a text file over 256 KB.
# A version carrying anything else is REFUSED outright -- worse than held. That is not
# hypothetical: v1.46.3-1 (26a8eae) bundled the recipes' ingredient `.csv`/`.jsonl`
# sample data and was refused on exactly those six files, one of which was also 302 KB.
# So this script enforces both rules below and fails rather than produce a bundle that
# would be refused. INGREDIENTS ARE deliberately NOT VENDORED: they are data, the
# directory will not take them, and a recipe fetches them at cook time as data (never
# executed), which the download-and-run policy does not reach.
#
# Usage: scripts/vendor-cookbook.sh [REF]      (REF default: main)
set -euo pipefail

REPO="senzing/recipes"
REF="${1:-main}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/plugins/senzing/skills/recipes/cookbook"
MAX_BYTES=2097152   # 2 MiB ceiling: the plugin ships to every install.

api() {
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    curl -fsSL -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" "$@"
  else
    curl -fsSL -H "Accept: application/vnd.github+json" "$@"
  fi
}

sha_of() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }

SHA="$(api "https://api.github.com/repos/$REPO/commits/$REF" | jq -r '.sha')"
[ -n "$SHA" ] && [ "$SHA" != "null" ] || { echo "could not resolve $REPO@$REF" >&2; exit 1; }
echo "Vendoring $REPO @ $SHA"

# Keep: markdown anywhere outside repo furniture, plus LICENSE (plain text).
# Drop: ingredients (data the directory refuses -- see the header), images, other
# binaries, .github/, .vscode/, contributor/housekeeping files.
PATHS="$(api "https://api.github.com/repos/$REPO/git/trees/$SHA?recursive=1" | jq -r '
  .tree[] | select(.type=="blob") | .path
  | select(startswith(".github/") or startswith(".vscode/") or startswith("ingredients/") | not)
  | select(. == "LICENSE" or endswith(".md"))
  | select(. != "CODE_OF_CONDUCT.md" and . != "CONTRIBUTING.md" and . != "CHANGELOG.md" and . != "README.md")
')"
[ -n "$PATHS" ] || { echo "upstream tree yielded no files -- refusing to empty the bundle" >&2; exit 1; }

rm -rf "$DEST"; mkdir -p "$DEST"
RAW="https://raw.githubusercontent.com/$REPO/$SHA"
count=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  mkdir -p "$DEST/$(dirname "$f")"
  curl -fsSL "$RAW/$f" -o "$DEST/$f"
  [ -s "$DEST/$f" ] || { echo "empty file from upstream: $f" >&2; exit 1; }
  count=$((count + 1))
done <<< "$PATHS"

# Enforce the directory's own rules so a refused bundle can never be produced here.
# Allowed types and the per-file inspectable limit come from the directory policy text;
# see the header for the version that was refused for breaking exactly these.
MAX_FILE_BYTES=262144   # 256 KB: the directory cannot inspect a larger text file.
violations=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  case "$f" in
    *.md|*.txt|*.json|*.yaml|*.yml|*.png|*.jpg|*.jpeg|*.gif|*.webp|*.ico|LICENSE) ;;
    *) echo "REFUSED TYPE: $f -- the directory accepts only Markdown, text, JSON, YAML and PNG/JPEG/GIF/WebP/ICO from a non-Verified org" >&2; violations=$((violations + 1)); continue ;;
  esac
  fb=$(wc -c < "$DEST/$f" | tr -d ' ')
  if [ "$fb" -gt "$MAX_FILE_BYTES" ]; then
    echo "TOO LARGE: $f is $fb bytes, over the directory's $MAX_FILE_BYTES-byte inspectable limit" >&2
    violations=$((violations + 1))
  fi
  head -c 2 "$DEST/$f" | grep -q '^#!' && { echo "SHEBANG: $f starts with #!, which the directory refuses" >&2; violations=$((violations + 1)); }
done <<< "$PATHS"
[ "$violations" -eq 0 ] || { echo "$violations file(s) would be REFUSED by the Claude directory -- refusing to vendor" >&2; exit 1; }

total=$(find "$DEST" -type f -exec cat {} + | wc -c | tr -d ' ')
[ "$total" -le "$MAX_BYTES" ] || { echo "bundle $total bytes exceeds $MAX_BYTES" >&2; exit 1; }

{
  echo "# Cookbook provenance"
  echo
  echo "Vendored verbatim from [\`$REPO\`](https://github.com/$REPO) — **do not hand-edit**."
  echo "Re-vendor with \`scripts/vendor-cookbook.sh [ref]\`; \`mcp-version-sync.yml\` runs it on"
  echo "every version bump, so each published plugin version carries the cookbook as it stood"
  echo "when that version was cut."
  echo
  echo "- Upstream commit: \`$SHA\`"
  echo "- Vendored at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- Files: $count · bytes: $total"
  echo "- Upstream license: Apache-2.0 (\`LICENSE\`, included)"
  echo
  echo "Ingredients, images and repo furniture are excluded on purpose: the directory accepts only"
  echo "Markdown/text/JSON/YAML/images from a non-Verified org, and the skill never renders an image."
  echo
  echo "| sha256 | file |"
  echo "| --- | --- |"
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    echo "| \`$(sha_of "$DEST/$f")\` | \`$f\` |"
  done <<< "$PATHS"
} > "$DEST/PROVENANCE.md"

echo "Vendored $count files ($total bytes) into ${DEST#"$ROOT"/}"
