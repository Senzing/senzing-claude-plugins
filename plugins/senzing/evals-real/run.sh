#!/usr/bin/env bash
# Run the REAL-SENZING eval suite — the one that needs an installed Senzing SDK.
#
# Deliberately a second suite, separate from plugins/senzing/evals/:
#   * that suite runs on macOS with NO Senzing installed, and several of its cases
#     depend on that absence. Dropping a case that requires a working SDK into it
#     would fail there for purely environmental reasons.
#   * its run.sh asserts "cases discovered == case directories on disk", so adding
#     a directory it must not run would break that gate.
# `claude plugin eval --eval-dir` takes a directory name below the plugin, so a
# sibling directory is all it costs to keep the two apart.
#
# Usage: plugins/senzing/evals-real/run.sh [--case <glob>] [extra claude-plugin-eval args...]
# Env:   EVAL_RUNS (default 1)   EVAL_THRESHOLD (default 0.8)  EVAL_MAX_COST_USD (default 75)
#        EVAL_JSON (default <evals-real>/results/ci.json)
#        EVAL_MODEL (default sonnet)  EVAL_JUDGE_MODEL (default sonnet)
# Needs: ANTHROPIC_API_KEY (or a logged-in claude), a sandbox backend for the Bash
#        grant (Linux: bubblewrap + socat), network to mcp.senzing.com, and a
#        working Senzing SDK on the host (see .github/senzing-eval/Dockerfile).
#
# EVAL_RUNS defaults to 1 here, not 2. Each run is a full map+load+resolve, and the
# ground-truth gate that follows (verify_truthset.py) inspects the repository the
# run left behind — one run, one repository, one unambiguous verdict.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_dir="$(dirname "$here")"
eval_dir_name="$(basename "$here")"
results_dir="$here/results"
json_out="${EVAL_JSON:-$results_dir/ci.json}"
mkdir -p "$results_dir" "$(dirname "$json_out")"

expected=0
for d in "$here"/*/; do
  [ -d "$d" ] || continue
  if [ -f "$d/prompt.md" ] || [ -f "$d/case.yaml" ]; then expected=$((expected + 1)); fi
done
if [ "$expected" -eq 0 ]; then
  echo "::error::no eval cases found under $here" >&2
  exit 1
fi
echo "== $expected real-Senzing eval case(s) under $plugin_dir/$eval_dir_name =="
echo "== subject model: ${EVAL_MODEL:-sonnet} | judge model: ${EVAL_JUDGE_MODEL:-sonnet} =="

# Same early-access enablement variable the sibling suite uses.
export CLAUDE_CODE_WALNUT_SPIRE="${CLAUDE_CODE_WALNUT_SPIRE:-1}"

# Edit is granted on top of the sibling suite's list: this case actually runs the
# mapper and the loader, and a rework round means editing a script it wrote.
args=(
  "$plugin_dir"
  --eval-dir "$eval_dir_name"
  --ablation none
  --scaffold
  --mocks off
  --allow-tools "mcp__plugin_senzing_senzing__*" Bash Write Edit \
                "WebFetch(domain:mcp.senzing.com)" "WebFetch(domain:raw.githubusercontent.com)"
  --model "${EVAL_MODEL:-sonnet}"
  --judge-model "${EVAL_JUDGE_MODEL:-sonnet}"
  --runs "${EVAL_RUNS:-1}"
  --threshold "${EVAL_THRESHOLD:-0.8}"
  # A RUNAWAY GUARD, not a budget — same figure and same reasoning as the sibling
  # suite. A ceiling low enough to bind does not save money, it truncates a
  # legitimate run into a `partial` and reports a false failure.
  --max-cost-usd "${EVAL_MAX_COST_USD:-75}"
  --no-publish
  --json "$json_out"
)
help_text="$(claude plugin eval --help 2>&1 || true)"
case "$help_text" in *--trust-plugin*) args+=(--trust-plugin) ;; esac

log="$results_dir/ci.log"
set +e
claude plugin eval "${args[@]}" "$@" 2>&1 | tee "$log"
rc=${PIPESTATUS[0]}
set -e

if grep -q 'currently in early access' "$log"; then
  echo "::error::claude plugin eval is still gated (early access) on this runner — the suite did NOT run." >&2
  exit 1
fi
if [ ! -s "$json_out" ]; then
  echo "::error::no result JSON at $json_out (exit $rc) — the suite did not run to completion" >&2
  if [ "$rc" -ne 0 ]; then exit "$rc"; fi
  exit 1
fi

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
