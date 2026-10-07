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
done < <(find . -name '*.json' -not -path './.git/*' -not -path './evals/results/*' -not -path './evals-real/results/*' | sort)

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
# The DIRECTORY PORTAL requires two manifest fields that OLDER Claude CLIs do not
# recognize, and --strict turns their "Unknown field" warning into a failure.
# This is a LOCAL-CLI problem, not a repo problem: CI installs the current CLI
# (`npm install -g @anthropic-ai/claude-code`, unpinned) and it validates both
# fields clean -- the v1.37.13-3 release log shows "✔ Validation passed" with
# both present. So this allowance exists so an older local CLI cannot fail a
# developer's check.sh over fields the portal demands and current CI accepts.
# Upgrading the local CLI is the better fix; this is the floor, not the goal.
# Each field is allowed by name, with the portal finding that demanded it:
#   privacyPolicyUrl -> portal finding PRIVACY_URL_MISSING
#   icon             -> portal finding ICON_MISSING
# Everything else --strict says is still fatal. Drop a name from this list the day
# the CLI schema learns it, and never add one without a portal finding to cite.
PORTAL_FIELDS='privacyPolicyUrl|icon'
validate_strict() {  # $1 = target, $2 = label
  local out rc findings unexpected
  out="$(claude plugin validate "$1" --strict 2>&1)"; rc=$?
  if [ $rc -eq 0 ]; then ok "$2"; return; fi
  # Distinguish "the manifest is invalid" from "the CLI could not run". Only the
  # first is this repo's problem; the second is an environment failure and is
  # reported as one, the way a missing CLI already is. ALWAYS print the output,
  # so neither case is silent -- the previous version of this check was
  # `claude plugin validate … | tail -2`, whose exit status is TAIL's, so it
  # passed unconditionally and gated nothing for the life of the script.
  if ! printf '%s\n' "$out" | grep -q "Validation"; then
    printf '%s\n' "$out" | tail -4
    note "$2: claude plugin validate could not run (exit $rc) — environment, not the manifest"
    return
  fi
  # Survivable only if EVERY reported finding is a portal field. Read the finding
  # lines themselves (they start with the CLI's bullet), never the summary line --
  # "treats warnings as errors" contains the word "errors" and matched a looser
  # pattern here, so the allowance never fired.
  findings="$(printf '%s\n' "$out" | grep -E "^[[:space:]]*❯" || true)"
  unexpected="$(printf '%s\n' "$findings" | grep -vE "Unknown field '($PORTAL_FIELDS)'" | grep -v '^$' || true)"
  if [ -n "$findings" ] && [ -z "$unexpected" ]; then
    note "$2: only portal-required unknown fields ($PORTAL_FIELDS) — allowed"
  else
    printf '%s\n' "$out" | tail -4
    bad "$2 validate"
  fi
}
if command -v claude >/dev/null 2>&1; then
  validate_strict . "marketplace"
  for plugin_dir in plugins/*/; do
    [ -f "$plugin_dir/.claude-plugin/plugin.json" ] || continue
    validate_strict "./$plugin_dir" "$plugin_dir"
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
# The regex graders left in the poc-planner-* cases assert the plan file's LITERAL structure
# (nine headings, template keys, the `TBD — decided by` literal). Each not_contains one is run
# against the VERBATIM tool output the skill makes the plan quote (Hardware Sizing FAQ
# "Phase 1/2/3", reporting_guide ">80%", ...), plus a correct and a fabricated plan fixture. A hit
# on quoted corpus text is a false-fail that would burn a paid eval run; a fabricated plan the
# graders pass is a grader that does nothing. Content prohibitions (thresholds, schedules, roles)
# are judge clauses since 2026-09-29, not regexes — one `judge-*.md` llm grader per clause since
# 2026-10-01 (formerly a single criteria.md), so a judge FAIL names the clause. Section D of the
# script checks those offline: identical shared preamble, plan-file focus, and that the fabricated
# fixture still carries the evidence for each clause expectations.json says it violates.
if python3 scripts/check-poc-graders.py; then ok "poc-planner grader fixture check"; else bad "poc-planner grader fixture check"; fi
if python3 scripts/check-grader-parity.py; then ok "grader/skill parity (surviving regexes pin a spelling; no regex bans vocabulary)"; else bad "grader/skill parity (surviving regexes pin a spelling; no regex bans vocabulary)"; fi

# The defect classes that produced this week's eval failures, each caught offline:
# an invalid template, a substitution ban the router never sees, a fetch host
# named wrong, and a prompt premise the sandbox contradicts.
if python3 scripts/check-skill-hazards.py; then ok "skill hazards (templates parse, bans in descriptions, fetch hosts, prompt premises)"; else bad "skill hazards (templates parse, bans in descriptions, fetch hosts, prompt premises)"; fi

echo; echo "== 8b. validate_plan.py accepts the correct plan and rejects the fabricated one =="
# The validator gates what poc-planner hands the user, and until now nothing exercised it.
# The two plan fixtures already exist, so this is the cheap end of the coverage a reviewer
# asked for: it would have caught a validator that accepts everything (or nothing).
VP=plugins/senzing/skills/poc-planner/validate_plan.py
VP_OK=evals/poc-planner-grounded/grader-fixtures/plans/correct-plan.md
VP_BAD=evals/poc-planner-grounded/grader-fixtures/plans/fabricated-plan.md
if python3 "$VP" "$VP_OK" >/dev/null 2>&1; then
  ok "validate_plan.py accepts correct-plan.md (exit 0)"
else
  bad "validate_plan.py REJECTS correct-plan.md — a validator that fails correct input is worse than none"
fi
if python3 "$VP" "$VP_BAD" >/dev/null 2>&1; then
  bad "validate_plan.py ACCEPTS fabricated-plan.md — the check cannot fail, so it asserts nothing"
else
  ok "validate_plan.py rejects fabricated-plan.md (exit 1)"
fi
# It must also name the nested-TBD omission by path, not just fail for some other reason:
# that omission was 5 of 10 failures in the run that motivated the validator.
# Capture first: this script runs under `set -o pipefail`, so piping a command that
# exits 1 (which this one must) into grep fails the pipeline even when grep matches.
VP_OUT="$(python3 "$VP" "$VP_BAD" 2>&1 || true)"
if printf '%s' "$VP_OUT" | grep -q "open_decisions does not list"; then
  ok "validate_plan.py names the missing §9 entry (the omission it exists to catch)"
else
  bad "validate_plan.py rejects fabricated-plan.md but not for the §9 omission — check the reason, not just the exit code"
fi

# The two mutations the old leaf-substring check could not see. Each starts from the CORRECT plan
# and removes exactly one thing, so the reason it is rejected is the only thing that changed.
vp_tmp="$(mktemp -d)"
# ONE combined EXIT trap: bash keeps a single trap per signal, so a second `trap ... EXIT` would silently replace the
# section-6 cleanup of $tmp. Both directories are removed on any exit, not just the happy path.
trap 'rm -rf "${tmp:-}" "${vp_tmp:-}"' EXIT
sed 's/SC-2 target, measured_against, decided_by/SC-2 measured_against, decided_by/' "$VP_OK" > "$vp_tmp/no-sc2-target.md"
# shellcheck disable=SC2016  # the backticks are literal characters in the plan, not a command substitution
sed 's/ (`data_subset_scope`)//' "$VP_OK" > "$vp_tmp/prose-no-key.md"
cmp -s "$VP_OK" "$vp_tmp/no-sc2-target.md" && bad "8b mutation 1 did not change the plan - the test below proves nothing"
cmp -s "$VP_OK" "$vp_tmp/prose-no-key.md" && bad "8b mutation 2 did not change the plan - the test below proves nothing"
VP_OUT1="$(python3 "$VP" "$vp_tmp/no-sc2-target.md" 2>&1 || true)"
if printf '%s' "$VP_OUT1" | grep -q "does not list 'SC-2.target'" \
   && ! printf '%s' "$VP_OUT1" | grep -q "does not list 'SC-1.target'" \
   && ! printf '%s' "$VP_OUT1" | grep -q "does not list 'SC-3.target'"; then
  ok "a plan missing ONLY SC-2.target is rejected for exactly that (not SC-1 or SC-3)"
else
  bad "validate_plan.py does not isolate SC-2.target - the leaf-substring weakness is back"
fi
VP_OUT2="$(python3 "$VP" "$vp_tmp/prose-no-key.md" 2>&1 || true)"
if printf '%s' "$VP_OUT2" | grep -q "names no §9 key"; then
  ok "a prose TBD with no §9 key is rejected, naming the line"
else
  bad "validate_plan.py accepts a prose TBD that is never listed as open"
fi
# License terms (same shape): remove only the §9 license line; and make only §6 claim the tools agree.
grep -v 'license path' "$VP_OK" > "$vp_tmp/no-license-line.md"
sed 's/The discrepancy between the paths/There is no discrepancy between the paths/' "$VP_OK" > "$vp_tmp/says-agree.md"
cmp -s "$VP_OK" "$vp_tmp/no-license-line.md" && bad "8b mutation 3 did not change the plan - the test below proves nothing"
cmp -s "$VP_OK" "$vp_tmp/says-agree.md" && bad "8b mutation 4 did not change the plan - the test below proves nothing"
VP_OUT3="$(python3 "$VP" "$vp_tmp/no-license-line.md" 2>&1 || true)"
if printf '%s' "$VP_OUT3" | grep -q "no license line"; then
  ok "a plan whose §6 discusses licensing but whose §9 has no license line is rejected"
else
  bad "validate_plan.py accepts a plan that never lists the license discrepancy as open"
fi
VP_OUT4="$(python3 "$VP" "$vp_tmp/says-agree.md" 2>&1 || true)"
if printf '%s' "$VP_OUT4" | grep -q "license terms agree"; then
  ok "a plan that calls the license terms consistent is rejected"
else
  bad "validate_plan.py accepts 'no discrepancy' about license terms the tools returned differently"
fi
# §9 license line: it names the differing SOURCES; a cap/day count/volume on it is a hint after a TBD
# (CI: every judge vote failed a §9 line restating "10-day/250K-record" and "500-record sample").
awk '/^ *- "TBD.*license path/ && !d { sub(/license path/, "license path (10-day, 250K-record offer vs 500-record sample)"); d=1 } { print }' "$VP_OK" > "$vp_tmp/license-figure.md"
cmp -s "$VP_OK" "$vp_tmp/license-figure.md" && bad "8b license-figure mutation did not change the plan - the test below proves nothing"
VP_OUT_LF="$(python3 "$VP" "$vp_tmp/license-figure.md" 2>&1 || true)"
if printf '%s' "$VP_OUT_LF" | grep -q "§9 license line carries a figure"; then
  ok "a §9 license line carrying a cap, day count or volume is rejected"
else
  bad "validate_plan.py accepts a §9 license line that restates the figures"
fi
# §3 target: the plan must not set one. Change only SC-1's target to a figure.
# awk, not sed: `0,/re/s//x/` is GNU-only and silently changes nothing on BSD sed (the cmp below catches that).
awk '!d && /target: TBD — decided by data platform lead/ { sub(/target: TBD — decided by data platform lead/, "target: F1 above 0.95"); d=1 } { print }' "$VP_OK" > "$vp_tmp/invented-target.md"
cmp -s "$VP_OK" "$vp_tmp/invented-target.md" && bad "8b mutation 5 did not change the plan - the test below proves nothing"
VP_OUT5="$(python3 "$VP" "$vp_tmp/invented-target.md" 2>&1 || true)"
if printf '%s' "$VP_OUT5" | grep -q "target is 'F1 above 0.95'"; then
  ok "a plan that sets an SC target of its own is rejected, naming the figure"
else
  bad "validate_plan.py accepts an SC target the plan invented"
fi
# Path-builder unit probes: the four shapes a real plan can take that the fixtures do not exercise.
if python3 - <<'PYEOF'
import re, sys
sys.path.insert(0, "plugins/senzing/skills/poc-planner")
import validate_plan as vp
fail = []
def paths(block): return [vp.fmt_path(x) for x in vp.block_tbd_paths(block)]
# an `id` that is not the first key still labels its item
if paths("- shape: x\n  id: SC-9\n  target: TBD — decided by a\n") != ["SC-9.target"]:
    fail.append("id-not-first item is not labelled by its id")
# a list at the SAME indent as its parent key belongs to that parent (valid YAML)
if paths("open_decisions:\n- k: TBD — decided by a\n") != ["open_decisions[0].k"]:
    fail.append("same-indent list lost its parent")
# a TBD that appears BEFORE its item's id is still reported under that id
if paths("- target: TBD — decided by a\n  id: SC-2\n") != ["SC-2.target"]:
    fail.append("a TBD before its item's id is reported under the positional label")
# a '#' inside an id is not a comment (a comment needs whitespace before it)
if paths("- id: SC-#2\n  target: TBD — decided by a\n") != ["SC-#2.target"]:
    fail.append("an id containing '#' is truncated")
# an owner may contain a digit
if not re.match(r"TBD — decided by [^:\n%]+?$", "TBD — decided by platform lead 2"):
    fail.append("an owner containing a digit is rejected")
# positional (unlabeled) items: only parent[N]/[]/[*] cover them, never a stray digit
items = vp.block_tbd_paths("data_sources:\n  - owner: TBD — decided by a\n  - owner: TBD — decided by a\n")
if [vp.covered(x, ["data_sources owner and 1 more"]) for x in items] != [False, False]:
    fail.append("a stray digit covers an unlabeled item")
if [vp.covered(x, ["data_sources[1] owner"]) for x in items] != [False, True]:
    fail.append("parent[N] does not cover exactly item N")
if [vp.covered(x, ["data_sources[] owner"]) for x in items] != [True, True]:
    fail.append("parent[] does not cover every item")
for f in fail: print("     " + f)
sys.exit(1 if fail else 0)
PYEOF
then
  ok "path-builder unit probes: id-not-first, same-indent list, digit in owner, positional coverage"
else
  bad "validate_plan.py path-builder regressed on a shape the fixtures do not exercise"
fi
awk '/^  shape: er_quality/ && !d { sub(/er_quality/, "TBD — decided by the data platform lead   # er_quality | other"); d=1 } { print }' "$VP_OK" > "$vp_tmp/tbd-comment.md"
cmp -s "$VP_OK" "$vp_tmp/tbd-comment.md" && bad "8b tbd-comment mutation did not change the plan - the test below proves nothing"
VP_OUT_TC="$(python3 "$VP" "$vp_tmp/tbd-comment.md" 2>&1 || true)"
if [[ "$VP_OUT_TC" == *"template comment rides on a TBD line"* ]]; then
  ok "a template '# candidate | list' comment after a TBD literal is rejected"
else
  bad "validate_plan.py accepts a candidate-list comment riding on a TBD line"
fi
rm -rf "$vp_tmp"

echo; echo "== 8c. no tool_used grader declares max without min (impossible range) =="
# A tool_used grader that sets `max: 0` and omits `min` gets min defaulted to 1, so the
# harness evaluates the range 1..0 — which NOTHING can satisfy. It fails every run,
# including clean ones, with "Bash called 0x (expected 1..0)". That is indistinguishable
# from a real defect until you read the range closely. `min: 0` is not optional.
# The detector, as ONE function, so the controls below exercise the same code the real
# scan uses -- not a second copy of it that could agree while the real one is broken.
#
# Frontmatter ONLY. `sed -n '/^---$/,/^---$/p'` reopens the range on any later `---` in
# the body -- these grader files use horizontal rules -- so it scanned prose for `max:`
# too, and a grader whose body opened a line with `max:` would be reported as "declares
# max without min" when its frontmatter declares neither. Stop at the first closing `---`.
declares_max_without_min() {
  fm=$(awk 'NR==1{next} /^---$/{exit} {print}' "$1" 2>/dev/null)
  printf '%s' "$fm" | grep -q "^max:" && ! printf '%s' "$fm" | grep -q "^min:"
}

# Controls FIRST. A scan that finds nothing is indistinguishable from a scan that cannot
# find anything, and this check shipped in a release about gates that claim a success they
# did not verify -- so prove it fires before trusting that it found nothing.
ctl=$(mktemp -d)
cat > "$ctl/positive.md" <<'FIXTURE'
---
type: tool_used
tool: Bash
max: 0
---

# Body

---

max: this line is prose, not frontmatter
FIXTURE
cat > "$ctl/negative.md" <<'FIXTURE'
---
type: tool_used
tool: Bash
min: 0
max: 0
---

# Body

---

max: this line is prose, not frontmatter
FIXTURE

if declares_max_without_min "$ctl/positive.md"; then
  ok "positive control: the detector flags max-without-min"
else
  bad "positive control FAILED — the detector does not catch max-without-min, so a clean scan proves nothing"
fi
# This control is the one the old sed got wrong: the body's `max:` line must not be read.
if declares_max_without_min "$ctl/negative.md"; then
  bad "negative control FAILED — a body line starting 'max:' was read as frontmatter (the sed range bug)"
else
  ok "negative control: a body line starting 'max:' is not mistaken for frontmatter"
fi
rm -rf "$ctl"

bad_range=0
for f in evals/*/graders/*.md; do
  if declares_max_without_min "$f"; then
    echo "     $f declares max: without min:"
    bad_range=1
  fi
done
if [ "$bad_range" = "0" ]; then
  ok "every grader that bounds a count declares both min and max"
else
  bad "a grader declares max without min — the harness defaults min to 1, making the range unsatisfiable"
fi

echo; echo "== 8d. no regex grader carries tool_used-only count bounds =="
# `min:`/`max:` bound a CALL COUNT and belong to `tool_used` graders. A `type: regex`
# grader rejects them, and the harness then fails the WHOLE CASE to load:
#   graders.6: Unrecognized key(s) in object: 'min', 'max'
# which surfaces as `cases run=17 expected=18` -- a structural exit 2, NOT a grader
# failure naming the file. That cost one full eval run on 2026-10-02. A regex grader
# asserts absence with `match: not_contains`.
grader_type() { awk 'NR==1{next} /^---$/{exit} {print}' "$1" 2>/dev/null | sed -n 's/^type:[[:space:]]*//p' | head -1; }
has_count_bound() { awk 'NR==1{next} /^---$/{exit} {print}' "$1" 2>/dev/null | grep -qE '^(min|max):'; }

# Controls first: a scan that finds nothing is indistinguishable from one that cannot.
ctl=$(mktemp -d)
printf -- '---\ntype: regex\npattern: "x"\nmin: 0\nmax: 0\n---\n\nbody\n' > "$ctl/positive.md"
printf -- '---\ntype: regex\npattern: "x"\nmatch: not_contains\n---\n\nbody\n'  > "$ctl/negative.md"
if [ "$(grader_type "$ctl/positive.md")" = "regex" ] && has_count_bound "$ctl/positive.md"; then
  ok "positive control: a regex grader carrying min/max is detected"
else
  bad "positive control FAILED - the 8d detector does not catch regex+min/max, so a clean scan proves nothing"
fi
if [ "$(grader_type "$ctl/negative.md")" = "regex" ] && has_count_bound "$ctl/negative.md"; then
  bad "negative control FAILED - a correct not_contains grader was flagged"
else
  ok "negative control: a regex grader using match: not_contains is not flagged"
fi
rm -rf "$ctl"

bad_keys=0
for f in evals/*/graders/*.md; do
  if [ "$(grader_type "$f")" = "regex" ] && has_count_bound "$f"; then
    echo "     $f is type: regex but declares min:/max:"
    bad_keys=1
  fi
done
if [ "$bad_keys" = "0" ]; then
  ok "no regex grader declares min:/max: (they would fail the whole case to load)"
else
  bad "a regex grader declares min:/max: - the harness will refuse to load its ENTIRE case"
fi

echo; echo "== 8e. no-cook-offered's pattern actually does what its doc claims =="
# The grader's claim -- catches the cook offer, leaves the REQUIRED description of what
# the recipe needs alone -- was prose until 2026-10-02, and prose does not run. An earlier
# revision of the pattern both MISSED the server's own wording ("continue with just 500 of
# their records", where the word before `just` is "with", not a verb in the list) and
# FLAGGED a factual sentence ("will load only 500 records"). Nothing in the repo noticed.
# Controls FIRST, as in 8d: a fixture check that cannot fail proves nothing. These run
# the SAME comparison loop against a deliberately broken pattern (the first revision this
# grader shipped, which missed the server's own wording and flagged a factual sentence)
# and against the real one, asserting the broken one is rejected.
python3 - <<'CONTROL'
import re, sys, pathlib
try:
    import yaml
except ImportError:
    # Same guard as the main block. Without it a missing dependency reports
    # "8e's fixtures do not discriminate" -- blaming the fixtures for a host
    # problem, which is the exact mistake the main block's exit 2 was added for.
    print("     ! PyYAML not available on this host")
    sys.exit(2)
fixtures = pathlib.Path("evals/recipes-named/pattern-fixtures/no-cook-offered.yaml")
fx = yaml.safe_load(fixtures.read_text(encoding="utf-8")) or {}

def failures(pat):
    rx = re.compile(pat, re.I)
    n = sum(1 for s in fx.get("must_match", []) if not rx.search(s))
    return n + sum(1 for s in fx.get("must_not_match", []) if rx.search(s))

# The first revision: keyed on a list of stemmed verbs.
broken = (r'(sampl\w*|load\w*|us\w*)\s+(just|only)\s+\d[\d,]*\s+'
          r'(of\s+(your|their|the)\s+)?records|when we (get|move) to the \w+ step'
          r'|have it ready to (attach|drop)')
bf = failures(broken)
if bf == 0:
    print("     positive control FAILED: the first revision passes these fixtures, so they "
          "do not discriminate")
    sys.exit(1)
print(f"     positive control: the superseded pattern is rejected ({bf} fixture disagreements)")
sys.exit(0)
CONTROL
# Capture the status from a BARE call. Inside the then-branch of `if ! cmd`, `$?` is the
# status of the NEGATED expression -- always 0 -- so the exit-2 arm below was dead code
# and a missing PyYAML still reported "fixtures do not discriminate". Verified:
#   probe(){ return 2; };  if ! probe; then echo $?; fi   -> 0
#   probe; echo $?                                        -> 2
ctl_rc=$?
if [ "$ctl_rc" = "2" ]; then
  bad "8e's control could not run, so the fixtures are UNVERIFIED (install PyYAML)"
elif [ "$ctl_rc" != "0" ]; then
  bad "8e's fixtures do not discriminate - they pass a pattern known to be broken"
fi

# This reads the pattern OUT OF the grader file so the two cannot drift.
if python3 - <<'PYEOF'
import re, sys, pathlib
grader = pathlib.Path("evals/recipes-named/graders/no-cook-offered.md")
fixtures = pathlib.Path("evals/recipes-named/pattern-fixtures/no-cook-offered.yaml")
if not grader.exists() or not fixtures.exists():
    print(f"     missing {grader if not grader.exists() else fixtures}")
    sys.exit(1)

fm = []
for i, line in enumerate(grader.read_text(encoding="utf-8").split("\n")):
    if i == 0:
        continue
    if line.strip() == "---":
        break
    fm.append(line)
pat = None
for line in fm:
    m = re.match(r"^pattern:\s*'(.*)'\s*$", line)
    if m:
        pat = m.group(1).replace("''", "'")  # YAML single-quote escape
if pat is None:
    print("     could not read `pattern:` out of the grader front matter")
    sys.exit(1)
rx = re.compile(pat, re.I)

try:
    import yaml
except ImportError:
    # Without this guard the ImportError propagates and the section reports
    # "pattern disagrees with its own fixtures" -- accusing the pattern of a
    # defect when the real problem is a missing dependency on this host.
    print("     ! PyYAML not available on this host")
    sys.exit(2)
fx = yaml.safe_load(fixtures.read_text(encoding="utf-8")) or {}
if not fx.get("must_match") and not fx.get("must_not_match"):
    print("     ! fixtures file is empty or not parseable - nothing was checked")
    sys.exit(2)
fails = 0
for s in fx.get("must_match", []):
    if not rx.search(s):
        print(f"     MISSED (must match): {s}")
        fails += 1
for s in fx.get("must_not_match", []):
    if rx.search(s):
        print(f"     FALSE POSITIVE (must not match): {s}")
        fails += 1
n = len(fx.get("must_match", [])) + len(fx.get("must_not_match", []))
print(f"     {n - fails} of {n} fixture strings behave as documented")
sys.exit(1 if fails else 0)
PYEOF
then
  ok "no-cook-offered matches every documented offer and no required prose"
else
  rc=$?
  # Exit 2 means the check could not RUN (no PyYAML, unreadable fixtures). Saying
  # `ok` there would affirm a claim nothing verified -- the exact defect this
  # release exists to remove -- so it is a failure, not a pass. CI has PyYAML;
  # a host without it must not be able to green this silently.
  if [ "$rc" = "2" ]; then
    bad "8e could not run, so the pattern is UNVERIFIED - this is not a pass (install PyYAML)"
  else
    bad "no-cook-offered's pattern disagrees with its own fixtures - it would miss a real offer or fail a correct run"
  fi
fi

echo; echo "== 8g. every other regex grader with fixtures does what its doc claims =="
# DIALECT: the pattern is run with Python `re`; the eval harness may use another engine. Patterns stay in
# the common subset (\\b \\w \\s \\d, (?:...), {m,n}, no lookbehind), but this proves Python behavior only:
# read a pass as "the pattern and its fixtures agree", not "the harness agrees".
# Generic form of 8e. For each evals/<case>/pattern-fixtures/<name>.yaml (except no-cook-offered,
# which has its own 8e), read `pattern:` OUT OF evals/<case>/graders/<name>.md and run it against
# the fixtures. must_match = the pattern HITS (the offending text); must_not_match = it does not.
# Exit 0 checked and clean, 1 disagreement, 2 could not run -- and 2 is a FAILURE: a check that
# cannot run must never read as a pass.
python3 - <<'PYEOF'
import re, sys, pathlib
try:
    import yaml
except ImportError:
    print("     ! PyYAML not available on this host")
    sys.exit(2)

def front_matter_pattern(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    fm = []
    for i, line in enumerate(lines):
        if i == 0:
            continue
        if line.strip() == "---":
            break
        fm.append(line)
    pat, flags = None, 0
    for line in fm:
        m = re.match(r"^pattern:\s*'(.*)'\s*$", line)
        if m:
            pat = m.group(1).replace("''", "'")  # YAML single-quote escape
        m = re.match(r"^flags:\s*(\w+)\s*$", line)
        if m and "i" in m.group(1):
            flags = re.I
    return pat, flags

def disagreements(rx, fx):
    n = sum(1 for s in fx.get("must_match", []) if not rx.search(s))
    return n + sum(1 for s in fx.get("must_not_match", []) if rx.search(s))

files = [f for f in sorted(pathlib.Path("evals").glob("*/pattern-fixtures/*.yaml"))
         if f.name != "no-cook-offered.yaml"]
if not files:
    print("     no fixture files found - nothing was checked")
    sys.exit(2)
bad = 0
for f in files:
    grader = f.parent.parent / "graders" / (f.stem + ".md")
    if not grader.exists():
        print(f"     {f}: no grader {grader.name} beside it")
        bad += 1
        continue
    pat, flags = front_matter_pattern(grader)
    if pat is None:
        print(f"     {grader}: could not read `pattern:`")
        bad += 1
        continue
    fx = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    if not fx.get("must_match") or not fx.get("must_not_match"):
        print(f"     {f}: needs BOTH must_match and must_not_match")
        bad += 1
        continue
    # Controls: a pattern that never matches must fail must_match, and one that always
    # matches must fail must_not_match -- otherwise these fixtures cannot discriminate.
    never, always = re.compile(r"(?!x)x"), re.compile(r"")
    if disagreements(never, fx) == 0 or disagreements(always, fx) == 0:
        print(f"     {f}: fixtures do not discriminate (a trivial pattern passes them)")
        bad += 1
        continue
    rx = re.compile(pat, flags)
    d = disagreements(rx, fx)
    n = len(fx["must_match"]) + len(fx["must_not_match"])
    for s in fx["must_match"]:
        if not rx.search(s):
            print(f"     {f.name} MISSED: {s[:80]}")
    for s in fx["must_not_match"]:
        if rx.search(s):
            print(f"     {f.name} FALSE POSITIVE: {s[:80]}")
    print(f"     {f.parent.parent.name}/{f.stem}: {n - d} of {n} fixtures behave as documented")
    bad += 1 if d else 0
sys.exit(1 if bad else 0)
PYEOF
g_rc=$?
if [ "$g_rc" = "0" ]; then
  ok "every fixture-backed regex grader matches its offending text and none of its required prose"
elif [ "$g_rc" = "2" ]; then
  bad "8g could not run, so those patterns are UNVERIFIED - this is not a pass (install PyYAML)"
else
  bad "a regex grader disagrees with its own fixtures - it would miss real text or fail a correct run"
fi

echo; echo "== 8f. demo routes on the blocker CLASS, not on a verdict =="
# A prompt change with no offline test is verified by prose alone. The full assertion
# (a denied package host must route into `install`) needs an eval case that reproduces
# that host, which does not exist yet. This is the cheap half: the contract that was
# WRONG -- routing only "if there is no running Senzing", a verdict -- must not come
# back, and the blocker-class wording must still be there. It cannot prove behavior;
# it proves the instruction has not silently reverted.
demo_skill=plugins/senzing/skills/demo/SKILL.md
if [ ! -f "$demo_skill" ]; then
  bad "$demo_skill is gone - this check is stale, point it at the new home"
elif ! grep -q "The trigger is the BLOCKER CLASS" "$demo_skill"; then
  bad "demo/SKILL.md lost the blocker-class routing rule - a denied host or missing permission will not route to install, and install's EULA contract is what that routing buys"
elif ! grep -q "a conditional attached to the permission request" "$demo_skill"; then
  bad "demo/SKILL.md lost the permission-conditional example - 'if you'd rather not change the sandbox rules I can fall back to a zero-install preview' is the shape that recurred after the first rule"
elif ! grep -q "a sandboxed shell" "$demo_skill"; then
  bad "demo/SKILL.md no longer names the sandboxed-shell blocker, the one that shipped install commands with no license agreement"
else
  ok "demo routes on the blocker class, and still names the blocker that caused the defect"
fi

echo; echo "== 8h. analyze lets the user's named location beat the default workspace =="
# The E2E case tells the model to keep the repository "inside this workspace", while the skill's
# default was ~/sz-workspace. A run that followed the default left the repository where the
# verifier (deliberately scoped to the scaffold directory) could not find it. Text guard only: it
# proves the precedence rule has not been removed, not that a model obeys it.
# shellcheck disable=SC2016  # the backticks are literal characters in the skill text
if grep -q "Where the user said to" plugins/senzing/skills/analyze/SKILL.md \
   && grep -qF 'never `~/sz-workspace`' plugins/senzing/skills/analyze/SKILL.md; then
  ok "analyze states that the user's named location beats the default workspace"
else
  bad "analyze/SKILL.md lost the user-location-beats-default rule - the default can again override 'inside this workspace'"
fi

echo; echo "== 8i. the CI judge is an explicit strong model and the judge gate is enforced =="
# The judge was `sonnet`, which the pinned CLI resolved to a no-thinking model whose votes did not
# track the reply. A text guard only: it proves the configuration has not reverted.
if grep -q 'EVAL_JUDGE_MODEL: claude-opus-5' .github/workflows/ci.yml \
   && grep -q 'EVAL_JUDGE_ENFORCE: "1"' .github/workflows/ci.yml; then
  ok "ci.yml pins the opus judge and enforces the judge gate"
else
  bad "ci.yml no longer pins EVAL_JUDGE_MODEL: claude-opus-5 and EVAL_JUDGE_ENFORCE: \"1\" - the noisy judge or an unenforced gate is back"
fi

echo; echo "== 8j. poc-planner's decline retrieves before it claims =="
# Removing the cited-quote exemption took away the model's reason to retrieve on the "how long" fast
# path: a run answered "Senzing's own guidance doesn't give a duration" without calling any tool.
# Text guard: the retrieve-first rule must stay in the decline paragraph.
if grep -q '\*\*Retrieve first\.\*\*' plugins/senzing/skills/poc-planner/SKILL.md; then
  ok "poc-planner's decline paragraph says to retrieve before claiming what the guidance says"
else
  bad "poc-planner/SKILL.md lost the retrieve-first rule - the decline path can again assert guidance it never opened"
fi

echo; echo "== 8k. recipes hands off to install instead of promising the cook =="
# A run stopped on a menu of Cook-step questions and promised "I'll install ... then cook the recipe".
# Text guard: the hand-off rule and its example must stay in recipes/SKILL.md.
if grep -q "do not announce the cook" plugins/senzing/skills/recipes/SKILL.md; then
  ok "recipes/SKILL.md says to hand off to install and not to announce the cook"
else
  bad "recipes/SKILL.md lost the hand-off rule - the install-then-cook promise can come back"
fi

# The judge sees only head+tail of the trace, so `install`'s own message (plan + EULA + one question)
# looks like "running the install flow inline" unless the criterion says it is the hand-off. Prior
# CI judges split 3-0 FAIL / 3-0 PASS on that shape; the clause and its FAIL boundary must stay.
if grep -q "own message is the hand-off" evals/recipes-named/graders/criteria.md \
   && grep -q "FAIL only for COOK-step content" evals/recipes-named/graders/criteria.md; then
  ok "recipes-named criteria treats install's own message as the hand-off and fails only cook-step content"
else
  bad "recipes-named criteria lost the install-message clause - the judge will fail the correct hand-off at random"
fi

# Main-branch CI (run 37196169047) failed three cases the PR run had passed -- each a real behavior the
# skill text left room for. Text guards keep the fix from being edited away.
if grep -q "fetch BEFORE you invoke" plugins/senzing/skills/recipes/SKILL.md; then
  ok "recipes/SKILL.md says to fetch the recipe before invoking install (install ends the turn)"
else
  bad "recipes/SKILL.md lost fetch-before-install - a run can hand off without ever opening the recipe"
fi
if grep -q 'is never touched." — full stop' plugins/senzing/skills/demo/SKILL.md; then
  ok "demo/SKILL.md gives the exact production sentence and forbids a conditional after it"
else
  bad "demo/SKILL.md lost the exact production sentence - the model recites 'unless you ask' again"
fi

if grep -qF "report is a checkpoint, not the answer" plugins/senzing/skills/build/SKILL.md; then
  ok "build/SKILL.md says doctor's report is a checkpoint and the run continues in the same turn"
else
  bad "build/SKILL.md lost the doctor-is-a-checkpoint rule - a run can end on the environment table"
fi

if grep -qF "You will already hold the platform's install steps" plugins/senzing/skills/recipes/SKILL.md; then
  ok "recipes/SKILL.md says holding doctor's install steps is when to hand off to install"
else
  bad "recipes/SKILL.md lost the hold-the-steps-still-hand-off rule - a run can write the install message itself"
fi

echo; echo "== 9. Eval scoring split (deterministic gate vs judge score) =="
# The suite's verdict is two independent gates, computed by evals/gate.py:
# deterministic graders must ALL pass in EVERY run (no averaging, no threshold), while the
# llm judge is scored separately. That logic decides whether a $6-17 run is a pass, so it is
# unit-tested here against synthetic result JSONs -- including the two failure modes that
# actually shipped: a passing judge masking a failed deterministic assertion, and a run that
# errored before grading being read as "nothing failed".
if python3 scripts/check-eval-gate.py; then ok "eval scoring split"; else bad "eval scoring split"; fi

echo; echo "== 10. Eval case frontmatter parses as YAML =="
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
# The case directories live at the REPO ROOT (evals/, evals-real/) -- they were moved out
# of plugins/senzing/ so the plugin-directory scanner does not read 5 MB of test
# infrastructure. The old search root was `find plugins -path '*/evals*/*'`, which after
# the move matches NOTHING: this section would print no lines, set no failure, and pass
# vacuously -- the exact shape of the bug it exists to catch. Count what it checked and
# fail on zero.
_eval_frontmatter_checked=0
while IFS= read -r pm; do
  _eval_frontmatter_checked=$((_eval_frontmatter_checked + 1))
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
done < <(find evals evals-real -name 'prompt.md' -not -path '*/results/*' | sort)
if [ "$_eval_frontmatter_checked" -eq 0 ]; then
  bad "no eval prompt.md found under evals/ or evals-real/ — this gate checked NOTHING"
  note "the search root drifted away from where the cases live; fix the find above"
else
  ok "$_eval_frontmatter_checked eval case frontmatter file(s) checked"
fi
fi

echo; echo "== 10b. bwrap-shim.py rewrites exactly the two faults, offline (fake bwrap) =="
# The shim sits over bwrap in the E2E image and rewrites its argument vector.
# It is safety-critical in both directions: rewrite too little and every Bash
# call in the eval dies; rewrite too much and the sandbox is weaker than the CLI
# intended. Exercise it here with a bwrap stand-in that just prints its argv.
shim_tmp="$(mktemp -d)"
printf '#!/bin/sh\nprintf "%%s\\n" "$@"\n' > "$shim_tmp/bwrap"; chmod +x "$shim_tmp/bwrap"
mkdir -p "$shim_tmp/empty-dir" "$shim_tmp/home"
shim_run() { BWRAP_REAL="$shim_tmp/bwrap" python3 .github/senzing-eval/bwrap-shim.py "$@" 2>/dev/null | tr '\n' ' '; }
# fault 1: a directory bind and a /dev/null (file) bind at one missing mount point
out="$(shim_run --ro-bind "$shim_tmp/empty-dir" "$shim_tmp/home/.aws" --ro-bind /dev/null "$shim_tmp/home/.aws" -- /bin/true)"
case "$out" in
  *"/dev/null"*) bad "shim left the /dev/null file mask on a mixed mount point: $out" ;;
  *"--ro-bind"*"$shim_tmp/home/.aws --ro-bind "*"$shim_tmp/home/.aws -- /bin/true"*) ok "fault 1: file mask re-pointed at a directory, bind stays read-only" ;;
  *) bad "fault 1: unexpected rewrite: $out" ;;
esac
# fault 1, writable variant: the re-pointed bind must become read-only
out="$(shim_run --ro-bind "$shim_tmp/empty-dir" "$shim_tmp/home/.aws" --bind /dev/null "$shim_tmp/home/.aws" -- /bin/true)"
case "$out" in *"--bind /dev/null"*|*"--bind $shim_tmp"*) bad "shim kept a writable --bind for a re-pointed mask: $out" ;; *) ok "fault 1: --bind forced to --ro-bind" ;; esac
# fault 2: the cap is added only when the command runs apply-seccomp, and only after the drop
out="$(shim_run --cap-drop ALL -- /bin/bash -c 'ARGV0=apply-seccomp /proc/self/fd/3 /bin/bash -c true')"
case "$out" in *"--cap-drop ALL --cap-add CAP_SYS_ADMIN --"*) ok "fault 2: CAP_SYS_ADMIN added after --cap-drop ALL for apply-seccomp" ;; *) bad "fault 2: expected cap-add after cap-drop: $out" ;; esac
out="$(shim_run --cap-drop ALL -- /bin/true)"
case "$out" in *"--cap-add"*) bad "shim added a capability to a command that does not run apply-seccomp: $out" ;; *) ok "fault 2: no apply-seccomp, no capability" ;; esac
# passthrough: an option the shim does not know must leave the vector untouched
out="$(shim_run --bogus-flag --ro-bind /dev/null "$shim_tmp/home/.aws" --ro-bind "$shim_tmp/empty-dir" "$shim_tmp/home/.aws" -- /bin/true)"
case "$out" in "--bogus-flag --ro-bind /dev/null "*) ok "unknown option: vector passed through untouched" ;; *) bad "unknown option: shim rewrote a vector it cannot parse: $out" ;; esac
rm -rf "$shim_tmp"

echo; echo "== 11. Spelling (cspell — same config CI uses) =="
# CI runs senzing-factory/build-resources cspell.yaml against .vscode/cspell.json.
# check.sh did NOT, so a run could pass every local gate and still be blocked by
# Spellcheck on the PR. That is not a cosmetic gap in this repo: every push fires
# a behavioral eval costing $6-17 and ~55 minutes, so two unknown dictionary
# words buy a full eval cycle. Local and CI must agree before the push, not after.
if command -v npx >/dev/null 2>&1; then
  # --dot: the globs alone skip files inside dot-directories (.github/**), which
  # let an unknown word in a workflow pass here and fail on the PR (PR #34).
  if npx --yes --quiet cspell@8 lint --no-progress --dot --config .vscode/cspell.json \
       --no-must-find-files "**/*" "**/.*" 2>/dev/null; then
    ok "cspell: no unknown words"
  else
    bad "cspell found unknown words (add real terms to .vscode/cspell.json words[])"
    npx --yes --quiet cspell@8 lint --no-progress --dot --config .vscode/cspell.json \
      --no-must-find-files "**/*" "**/.*" 2>&1 | grep -E 'Unknown word' | head -20
  fi
else
  note "npx not available — SKIPPED. CI still runs this; unknown words will block the PR."
fi

echo
if [ "$fail" -eq 0 ]; then printf '\033[32mAll static checks passed.\033[0m\n'; else printf '\033[31mChecks failed.\033[0m\n'; fi
exit "$fail"
