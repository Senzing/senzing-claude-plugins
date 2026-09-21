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
done < <(find . -name '*.json' -not -path './.git/*' -not -path './plugins/*/evals/results/*' | sort)

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
  for plugin_dir in plugins/*/; do
    [ -f "$plugin_dir/.claude-plugin/plugin.json" ] || continue
    if claude plugin validate "./$plugin_dir" --strict 2>&1 | tail -2; then ok "$plugin_dir"; else bad "$plugin_dir validate"; fi
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
for plugin_dir in plugins/*/; do
  [ -f "$plugin_dir/.claude-plugin/plugin.json" ] || continue
  ver="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$plugin_dir/.claude-plugin/plugin.json")"
  if grep -qF "## [$ver]" CHANGELOG.md; then ok "CHANGELOG.md has ## [$ver]"; else bad "CHANGELOG.md has no '## [$ver]' heading (plugin.json says $ver)"; fi
done

echo; echo "== 7b. changelog-stub.sh keeps pending [Unreleased] notes out of the sync stub =="
# The auto-sync PR writes its own ## [x.y.z] stub. If it were spliced directly under
# [Unreleased], any pending notes there would be misfiled under a release that says
# "no code change" — so the fixture has pending content and asserts the ordering.
stub_fixture="$(mktemp)"
printf '# Changelog\n\n## [Unreleased]\n\n### Added\n\n- pending feature\n\n## [1.0.0] - 2026-01-01\n\n- old\n' > "$stub_fixture"
if bash scripts/changelog-stub.sh 1.0.1 2026-01-02 "$stub_fixture" \
   && [ "$(grep -n '^## \[\|^- pending' "$stub_fixture" | cut -d: -f2 | tr '\n' '|')" = "## [Unreleased]|- pending feature|## [1.0.1] - 2026-01-02|## [1.0.0] - 2026-01-01|" ] \
   && bash scripts/changelog-stub.sh 1.0.1 2026-01-02 "$stub_fixture" 2>/dev/null \
   && [ "$(grep -c '^## \[1.0.1\]' "$stub_fixture")" = 1 ]; then
  ok "stub lands after pending notes, before the previous release; idempotent"
else
  bad "changelog-stub.sh ordering/idempotence (see scripts/changelog-stub.sh)"; grep -n '^## \[\|^- ' "$stub_fixture"
fi
rm -f "$stub_fixture"

echo; echo "== 8. poc-planner graders vs the corpus they must quote (offline fixture check) =="
# Every not_contains grader in the poc-planner-* cases is run against the VERBATIM tool output the
# skill makes the plan quote (Hardware Sizing FAQ "Phase 1/2/3", reporting_guide ">80%", ...),
# plus a correct and a fabricated plan fixture. A hit on quoted corpus text is a false-fail that
# would burn a paid eval run; a fabricated plan the graders pass is a grader that does nothing.
if python3 scripts/check-poc-graders.py; then ok "poc-planner grader fixture check"; else bad "poc-planner grader fixture check"; fi

echo; echo "== 9. Eval case frontmatter parses as YAML =="
# Why: `claude plugin eval` silently DROPS a case whose frontmatter will not parse -- it
# prints one "✗ ... invalid YAML frontmatter" line and carries on. run.sh's discovery gate
# catches the resulting count mismatch, but only DURING a paid run. poc-planner-how-long
# shipped with `description: "How long will a Senzing POC take?" routes to ...` -- a double-
# quoted scalar with text after the closing quote -- so the case never loaded and was never
# graded, and nothing on the free static tier said so. Section 3 only covers SKILL.md/agents.
# PyYAML is the only third-party dependency this script uses. Guard it the same way
# jq/shellcheck/claude are guarded above -- unguarded, a runner without PyYAML turns
# every eval prompt.md into an unexplained ModuleNotFoundError wall instead of the
# "X not installed" line this file uses everywhere else. CI installs it explicitly
# (see the `static` job) so the gate never silently skips where it must run.
if ! python3 -c 'import yaml' 2>/dev/null; then
  bad "PyYAML not installed — cannot validate eval frontmatter (pip install pyyaml)"
  note "this gate is the only thing that catches an eval case that silently never loads"
else
while IFS= read -r pm; do
  if python3 - "$pm" <<'PYEOF'
import sys, yaml
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
if not text.startswith("---"):
    sys.exit("no YAML frontmatter (must open with --- on line 1)")
parts = text.split("---", 2)
if len(parts) < 3:
    sys.exit("frontmatter is not closed by a second ---")
try:
    data = yaml.safe_load(parts[1])
except Exception as e:
    sys.exit(f"invalid YAML frontmatter: {e}")
if not isinstance(data, dict):
    sys.exit("frontmatter is not a YAML mapping")
if "description" not in data:
    sys.exit("missing: description")
PYEOF
  then ok "$pm"; else bad "$pm"; fi
done < <(find plugins -path '*/evals/*' -name 'prompt.md' -not -path '*/results/*' | sort)
fi

echo
if [ "$fail" -eq 0 ]; then printf '\033[32mAll static checks passed.\033[0m\n'; else printf '\033[31mChecks failed.\033[0m\n'; fi
exit "$fail"
