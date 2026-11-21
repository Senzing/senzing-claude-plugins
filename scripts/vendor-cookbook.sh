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
# INGREDIENTS ARE NOT VENDORED. They were, as <name>.txt, until the policy review
# reported it "couldn't cover" some files -- 815 KB of the 1.15 MB was ingredient data.
# The plugin has never published, and every version waits for a human reviewer, so this
# strips to the minimum to test whether a submission with ZERO findings publishes on its
# own. Recipes get their data from the user, which is what the recipes themselves say.
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

# INGREDIENT DATA -> ALLOWED TEXT. The directory accepts Markdown, text, JSON, YAML and
# images, and cannot inspect a text file over 256 KB. The ingredients are plain UTF-8 text
# whose EXTENSION (.csv/.jsonl) is not on that list, so each is stored with a `.txt` suffix
# appended to its real name -- `crm.csv` becomes `crm.csv.txt` -- and a file over the limit
# is split on LINE boundaries into `<name>.partNN.txt`. The skill reverses both when it
# copies them into the workspace, so the recipes still see the filenames they document.
# Nothing is renamed to hide anything: every byte stays readable text, which is exactly what
# the limit is for.
while IFS= read -r f; do
  [ -n "$f" ] || continue
  base="$(basename "$f")"; dir="$(dirname "$f")"
  if [ "$(LC_ALL=C tr -dc '\000' < "$f" | wc -c | tr -d ' ')" -ne 0 ]; then
    echo "NUL byte in $base -- not text, refusing" >&2; exit 1
  fi
  sz=$(wc -c < "$f" | tr -d ' ')
  if [ "$sz" -le 262144 ]; then
    mv "$f" "$dir/$base.txt"
  else
    # split on line boundaries so each part stays valid JSONL/CSV rows
    lines=$(wc -l < "$f" | tr -d ' ')
    parts=$(( (sz + 262143) / 262144 ))
    per=$(( (lines + parts - 1) / parts ))
    split -l "$per" -a 2 -d "$f" "$dir/$base.part"
    rm -f "$f"
    for pf in "$dir/$base.part"[0-9][0-9]; do mv "$pf" "$pf.txt"; done
    echo "  split $base ($sz bytes) into $parts line-aligned parts"
  fi
done <<< "$(find "$DEST/ingredients" -type f ! -name '*.md' 2>/dev/null)"

# Enforce the directory's own rules against WHAT IS ACTUALLY ON DISK, after any
# conversion above -- not against the upstream path list, which still carries the
# original extensions. Allowed types and the per-file inspectable limit come from the
# directory policy text; see the header for the version that was refused for breaking
# exactly these.
MAX_FILE_BYTES=262144   # 256 KB: the directory cannot inspect a larger text file.
violations=0
while IFS= read -r abs; do
  [ -n "$abs" ] || continue
  rel="${abs#"$DEST"/}"
  case "$rel" in
    *.md|*.txt|*.json|*.yaml|*.yml|*.png|*.jpg|*.jpeg|*.gif|*.webp|*.ico|LICENSE) ;;
    *) echo "REFUSED TYPE: $rel -- the directory accepts only Markdown, text, JSON, YAML and PNG/JPEG/GIF/WebP/ICO from a non-Verified org" >&2; violations=$((violations + 1)); continue ;;
  esac
  fb=$(wc -c < "$abs" | tr -d ' ')
  if [ "$fb" -gt "$MAX_FILE_BYTES" ]; then
    echo "TOO LARGE: $rel is $fb bytes, over the directory's $MAX_FILE_BYTES-byte inspectable limit" >&2
    violations=$((violations + 1))
  fi
  head -c 2 "$abs" | grep -q '^#!' && { echo "SHEBANG: $rel starts with #!, which the directory refuses" >&2; violations=$((violations + 1)); }
  [ "$(LC_ALL=C tr -dc '\000' < "$abs" | wc -c | tr -d ' ')" -eq 0 ] || { echo "NUL BYTE: $rel is not clean UTF-8 text" >&2; violations=$((violations + 1)); }
done <<< "$(find "$DEST" -type f)"
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
  echo "Ingredient data is stored with a \`.txt\` suffix on its real name (\`crm.csv\` ->"
  echo "\`crm.csv.txt\`), and a file over 256 KB is split on line boundaries into"
  echo "\`<name>.partNN.txt\`. The directory accepts Markdown, text, JSON, YAML and images and"
  echo "must be able to read each file in full; the data is plain UTF-8 text either way, so this"
  echo "keeps it inspectable rather than hiding it. The skill restores the documented filenames"
  echo "when it copies them into the workspace."
  echo
  echo "| sha256 | file |"
  echo "| --- | --- |"
  while IFS= read -r abs; do
    [ -n "$abs" ] || continue
    rel="${abs#"$DEST"/}"
    [ "$rel" = "PROVENANCE.md" ] && continue
    echo "| \`$(sha_of "$abs")\` | \`$rel\` |"
  done <<< "$(find "$DEST" -type f | sort)"
} > "$DEST/PROVENANCE.md"

echo "Vendored $count files ($total bytes) into ${DEST#"$ROOT"/}"
