#!/usr/bin/env bash
# Local + CI lockstep checks for the Senzing Claude Code plugins.
# Run before every commit; CI runs the exact same script.
# Tiers implemented here are the "static" tier — no API/auth, fast, deterministic.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

fail=0
note() { printf '  %s\n' "$*"; }
ok()   { printf '\033[32mok\033[0m   %s\n' "$*"; }
bad()  { printf '\033[31mFAIL\033[0m %s\n' "$*"; fail=1; }

echo "== 1. JSON parses =="
while IFS= read -r f; do
  if python3 -m json.tool "$f" >/dev/null 2>&1; then ok "$f"; else bad "$f (invalid JSON)"; python3 -m json.tool "$f" 2>&1 | head -3; fi
done < <(find . -name '*.json' -not -path './.git/*' -not -path './evals/results/*' | sort)

echo; echo "== 2. Hook scripts (bash -n + shellcheck) =="
while IFS= read -r s; do
  if ! bash -n "$s"; then bad "$s (bash syntax)"; continue; fi
  if command -v shellcheck >/dev/null 2>&1; then
    if shellcheck -S warning "$s"; then ok "$s"; else bad "$s (shellcheck)"; fi
  else ok "$s (bash -n only; shellcheck not installed)"; fi
  [ -x "$s" ] || bad "$s (not executable — chmod +x)"
done < <(find . -name '*.sh' -not -path './.git/*' | sort)

echo; echo "== 3. Skill & agent frontmatter (name + description required) =="
while IFS= read -r md; do
  # Frontmatter must be the first block delimited by --- ... ---
  fm="$(awk 'NR==1&&$0!="---"{exit} NR==1{next} $0=="---"{exit} {print}' "$md")"
  if [ -z "$fm" ]; then bad "$md (no YAML frontmatter)"; continue; fi
  miss=""
  grep -qE '^\s*description\s*:' <<<"$fm" || miss="$miss description"
  grep -qE '^\s*name\s*:'        <<<"$fm" || miss="$miss name"
  if [ -n "$miss" ]; then bad "$md (missing:$miss)"; else ok "$md"; fi
done < <(find plugins -name 'SKILL.md' -o -path '*/agents/*.md' | sort)

echo; echo "== 4. claude plugin validate --strict =="
if command -v claude >/dev/null 2>&1; then
  if claude plugin validate . --strict 2>&1 | tail -2; then ok "marketplace"; else bad "marketplace validate"; fi
  for pdir in plugins/*/; do
    [ -f "$pdir/.claude-plugin/plugin.json" ] || continue
    if claude plugin validate "./$pdir" --strict 2>&1 | tail -2; then ok "$pdir"; else bad "$pdir validate"; fi
  done
else
  note "claude CLI not on PATH — skipping (CI installs it). Install: npm i -g @anthropic-ai/claude-code"
fi

echo
if [ "$fail" -eq 0 ]; then printf '\033[32mAll static checks passed.\033[0m\n'; else printf '\033[31mChecks failed.\033[0m\n'; fi
exit "$fail"
