#!/usr/bin/env bash
# Run the plugin's behavioral eval suite — the SAME entry point locally and in CI.
#
# Why this exists: the suite sat at the repo root for months while CI ran
# `claude plugin eval ./plugins/senzing`, which only discovers `<plugin>/evals/`. Zero cases
# were ever found, and the job was `continue-on-error` behind `workflow_dispatch`, so nothing
# could fail. This script (1) asserts the discovered case count equals the case directories on
# disk, (2) refuses to treat the early-access gate message as a pass, and (3) propagates the
# CLI's threshold exit code.
#
# Usage: plugins/senzing/evals/run.sh [--case <glob>] [extra claude-plugin-eval args...]
# Env:   EVAL_RUNS (default 2)  EVAL_THRESHOLD (default 0.8)  EVAL_MAX_COST_USD (default 75)
#        EVAL_CONCURRENCY (default 3)  EVAL_JSON (default <evals>/results/ci.json)
# Needs: ANTHROPIC_API_KEY (or a logged-in claude), the sandbox backend for Bash grants
#        (macOS: built in; Linux: bubblewrap + socat), and network to mcp.senzing.com.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_dir="$(dirname "$here")"
eval_dir_name="$(basename "$here")"
results_dir="$here/results"
json_out="${EVAL_JSON:-$results_dir/ci.json}"
mkdir -p "$results_dir" "$(dirname "$json_out")"

# Every immediate child directory holding a prompt.md or case.yaml is a case.
expected=0
for d in "$here"/*/; do
  [ -d "$d" ] || continue
  if [ -f "$d/prompt.md" ] || [ -f "$d/case.yaml" ]; then expected=$((expected + 1)); fi
done
if [ "$expected" -eq 0 ]; then
  echo "::error::no eval cases found under $here" >&2
  exit 1
fi
echo "== $expected eval case(s) on disk under $plugin_dir/$eval_dir_name =="

# The early-access rollout is a per-organization server-side flag that a headless CI runner
# cannot receive; this is the CLI's own documented enablement variable for that situation
# (see the text `claude plugin eval` prints when enabled). Harmless where already enabled.
export CLAUDE_CODE_WALNUT_SPIRE="${CLAUDE_CODE_WALNUT_SPIRE:-1}"

# The plugin's MCP server is a public hosted endpoint, so the cases run against the REAL server
# (--mocks off) — the graders check that real tool calls happened. Bash/Write are granted so
# doctor can probe the host and build can write a file; the two WebFetch domain grants open the
# sandbox network to the hosts the skills need (doctor's reachability probe + resource fetches).
args=(
  "$plugin_dir"
  --eval-dir "$eval_dir_name"
  --ablation none
  --scaffold
  --mocks off
  --allow-tools "mcp__plugin_senzing_senzing__*" Bash Write \
                "WebFetch(domain:mcp.senzing.com)" "WebFetch(domain:raw.githubusercontent.com)"
  --runs "${EVAL_RUNS:-2}"
  --threshold "${EVAL_THRESHOLD:-0.8}"
  --max-cost-usd "${EVAL_MAX_COST_USD:-75}"
  --no-publish
  --json "$json_out"
)
# Flags that newer CLIs add; probe --help so an older local install still runs the suite.
# --trust-plugin is REQUIRED on a headless runner (a non-TTY run is refused without it).
help_text="$(claude plugin eval --help 2>&1 || true)"
case "$help_text" in *--trust-plugin*) args+=(--trust-plugin) ;; esac
case "$help_text" in *--concurrency*)  args+=(--concurrency "${EVAL_CONCURRENCY:-3}") ;; esac
log="$results_dir/ci.log"
set +e
claude plugin eval "${args[@]}" "$@" 2>&1 | tee "$log"
rc=${PIPESTATUS[0]}
set -e

if grep -q 'currently in early access' "$log"; then
  echo "::error::claude plugin eval is still gated (early access) on this runner — the suite did NOT run. Enablement variable CLAUDE_CODE_WALNUT_SPIRE=1 was set; check the CLI version / rollout." >&2
  exit 1
fi
if [ ! -s "$json_out" ]; then
  echo "::error::no result JSON at $json_out (exit $rc) — the suite did not run to completion" >&2
  exit "${rc:-1}"
fi

# Discovery gate + human-readable summary. Exit 1 if fewer cases ran than exist on disk.
python3 - "$json_out" "$expected" "${EVAL_THRESHOLD:-0.8}" <<'PY'
import json, sys
path, expected, threshold = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
r = json.load(open(path))
cases = r.get("cases", [])
agg = r.get("aggregates", {})
print(f"\n{'CASE':<28}{'SCORE':>7}  STATUS")
for c in cases:
    score = (c.get("aggregates") or {}).get("score")
    s = "n/a" if score is None else f"{score:.2f}"
    ok = score is not None and score >= threshold
    print(f"{c.get('name',''):<28}{s:>7}  {'pass' if ok else 'FAIL'}")
print(f"\ncases run={len(cases)} expected={expected} passed={agg.get('casesPassed')}/{agg.get('casesTotal')} "
      f"overall={agg.get('overallScore')} cost=${r.get('costUsd')} partial={r.get('partial')} ({r.get('partialReason')})")
if len(cases) < expected:
    print(f"::error::only {len(cases)} of {expected} cases were discovered — eval layout regression", file=sys.stderr)
    sys.exit(1)
if r.get("partial"):
    print(f"::error::partial run: {r.get('partialReason')}", file=sys.stderr)
    sys.exit(2)
PY

exit "$rc"
