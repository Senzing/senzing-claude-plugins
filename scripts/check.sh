#!/usr/bin/env bash
# Local + CI lockstep checks for the Senzing Claude Code plugins.
# Run before every commit; CI runs the exact same script.
# Tiers implemented here are the "static" tier — no API/auth, fast, deterministic.
# Section 6 also RUNS every hook against a real captured payload: a hook whose jq path
# matches nothing exits 0 and looks healthy, which is how capture_state.sh shipped
# without ever writing a state file.
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
    if shellcheck -S style "$s"; then ok "$s"; else bad "$s (shellcheck)"; fi
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

echo; echo "== 5. Skill name matches its directory =="
for d in plugins/*/skills/*/; do
  dir="$(basename "$d")"
  fm_name="$(awk 'NR==1&&$0!="---"{exit} NR==1{next} $0=="---"{exit} /^[[:space:]]*name[[:space:]]*:/{sub(/^[[:space:]]*name[[:space:]]*:[[:space:]]*/,""); print; exit}' "$d/SKILL.md" | tr -d '"'"'"' ')"
  if [ "$fm_name" = "$dir" ]; then ok "$d (name: $fm_name)"; else bad "$d (frontmatter name '$fm_name' != directory '$dir')"; fi
done

echo; echo "== 6. Hooks run against real payloads (fixtures) =="
HOOKS=plugins/senzing/hooks
FIX="$HOOKS/fixtures"
if ! command -v jq >/dev/null 2>&1; then
  bad "jq not installed — hook fixture tests cannot run (brew install jq / apt-get install jq)"
else
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT

  # 6a. capture_state: REAL mapping_workflow start response (content-array shape, REMINDER footer)
  #     must land at <state.workspace_dir>/.sz-state.json — the path the analyze skill reads.
  ws="$tmp/ws-from-state"
  sed "s|__WORKSPACE__|$ws|g" "$FIX/mapping_workflow_start.payload.json" \
    | env -u SZ_WORKSPACE HOME="$tmp/home-a" bash "$HOOKS/capture_state.sh"
  if [ -s "$ws/.sz-state.json" ] && jq -e --arg ws "$ws" '.step == 1 and .workspace_dir == $ws and (.file_paths | length) == 1' "$ws/.sz-state.json" >/dev/null 2>&1; then
    ok "capture_state.sh wrote <state.workspace_dir>/.sz-state.json from the real payload"
  else
    bad "capture_state.sh did not write $ws/.sz-state.json from the real mapping_workflow payload"
  fi
  [ -e "$tmp/home-a/sz-workspace/.sz-state.json" ] && bad "capture_state.sh wrote to \$HOME instead of state.workspace_dir"

  # 6b. capture_state: state without workspace_dir falls back to $HOME/sz-workspace (SZ_WORKSPACE unset).
  jq -cn '{tool_response:{content:[{type:"text",text:("{\"state\":{\"step\":2,\"step_name\":\"plan_entity_structure\"}}\n\n[REMINDER: fixture]")}]}}' \
    | env -u SZ_WORKSPACE HOME="$tmp/home-b" bash "$HOOKS/capture_state.sh"
  if jq -e '.step == 2' "$tmp/home-b/sz-workspace/.sz-state.json" >/dev/null 2>&1; then
    ok "capture_state.sh falls back to \$HOME/sz-workspace when state has no workspace_dir"
  else
    bad "capture_state.sh fallback to \$HOME/sz-workspace failed"
  fi

  # 6c. capture_state: a non-workflow payload must write nothing.
  printf 'x = 1\n' > "$tmp/plain.py"
  sed "s|__FILE__|$tmp/plain.py|g; s|__DIR__|$tmp|g" "$FIX/write_tool.payload.json" \
    | env -u SZ_WORKSPACE HOME="$tmp/home-c" bash "$HOOKS/capture_state.sh"
  if [ -e "$tmp/home-c/sz-workspace/.sz-state.json" ]; then bad "capture_state.sh wrote a state file for a Write payload"; else ok "capture_state.sh ignores non-workflow payloads"; fi

  # 6d. check_provenance: SDK code without a URL -> hook JSON (additionalContext) on STDOUT, nothing on stderr.
  printf 'from senzing_core import SzAbstractFactoryCore\n' > "$tmp/sdk.py"
  out="$(sed "s|__FILE__|$tmp/sdk.py|g; s|__DIR__|$tmp|g" "$FIX/write_tool.payload.json" | bash "$HOOKS/check_provenance.sh" 2>"$tmp/prov.err")"
  if printf '%s' "$out" | jq -e '.hookSpecificOutput.hookEventName == "PostToolUse" and (.hookSpecificOutput.additionalContext | length) > 0' >/dev/null 2>&1 && [ ! -s "$tmp/prov.err" ]; then
    ok "check_provenance.sh emits hook JSON on stdout for un-attributed SDK code"
  else
    bad "check_provenance.sh did not emit hook JSON on stdout (stdout: '$out'; stderr: '$(cat "$tmp/prov.err")')"
  fi

  # 6e. check_provenance: a bare comment mentioning senzing, or SDK code that HAS a URL, must stay silent.
  printf '# no senzing here\n' > "$tmp/comment.py"
  printf '# source: https://github.com/senzing-garage/code-snippets-v4\nfrom senzing_core import SzAbstractFactoryCore\n' > "$tmp/attributed.py"
  quiet=1
  for f in comment.py attributed.py; do
    out="$(sed "s|__FILE__|$tmp/$f|g; s|__DIR__|$tmp|g" "$FIX/write_tool.payload.json" | bash "$HOOKS/check_provenance.sh" 2>&1)"
    [ -z "$out" ] || { quiet=0; bad "check_provenance.sh fired on $f: $out"; }
  done
  [ "$quiet" -eq 1 ] && ok "check_provenance.sh stays silent on a bare comment and on attributed code"

  # 6f. session_start: must survive an environment with HOME unset (set -u).
  if env -i PATH="$PATH" CLAUDE_PLUGIN_DATA="$tmp/plugin-data" bash "$HOOKS/session_start.sh" >"$tmp/ss.out" 2>"$tmp/ss.err" \
     && grep -q '/senzing:ask' "$tmp/ss.out" && grep -q '/senzing:install' "$tmp/ss.out"; then
    ok "session_start.sh runs with HOME unset and advertises ask + install"
  else
    bad "session_start.sh failed with HOME unset (stderr: $(cat "$tmp/ss.err"))"
  fi
fi

echo; echo "== 7. CHANGELOG has an entry for the current plugin version =="
for pdir in plugins/*/; do
  [ -f "$pdir/.claude-plugin/plugin.json" ] || continue
  ver="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$pdir/.claude-plugin/plugin.json")"
  if grep -qF "## [$ver]" CHANGELOG.md; then ok "CHANGELOG.md has ## [$ver]"; else bad "CHANGELOG.md has no '## [$ver]' heading (plugin.json says $ver)"; fi
done

echo
if [ "$fail" -eq 0 ]; then printf '\033[32mAll static checks passed.\033[0m\n'; else printf '\033[31mChecks failed.\033[0m\n'; fi
exit "$fail"
