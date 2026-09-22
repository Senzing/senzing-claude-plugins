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
# Scoring is NOT the CLI's blended average — the verdict comes from the SAME gate.py the
# behavioral suite uses (../evals/gate.py). Deterministic graders (regex / tool_used /
# tool_order / file_exists) must ALL pass in EVERY run; the llm judge is scored separately
# against its own threshold and can neither mask nor be masked by them. The CLI is therefore
# run with `--threshold 0`: it grades, gate.py decides.
#
# Usage: plugins/senzing/evals-real/run.sh [--case <glob>] [extra claude-plugin-eval args...]
# Env:   EVAL_RUNS (default 1)   EVAL_MAX_COST_USD (default 75)
#        EVAL_JUDGE_THRESHOLD (default 0.8; EVAL_THRESHOLD honored as the old name)
#        EVAL_JUDGE_ENFORCE=1 makes the judge score a hard gate too (default: reported only)
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
judge_threshold="${EVAL_JUDGE_THRESHOLD:-${EVAL_THRESHOLD:-0.8}}"
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
  # Deliberately 0 — the CLI must NOT issue the verdict. Its --threshold is compared against
  # a single blended score: the fraction of a case's graders that passed, judge and
  # deterministic averaged together. This case has eight deterministic graders and one llm
  # grader, so at the old 0.8 a red boolean cost 1/9 = 0.111 and landed at 0.889, above the
  # line. That is not a hypothetical: CI run 35724685327 reported
  #   cases run=1 expected=1 passed=1/1 overall=0.888888888
  # with `records-loaded-reported` FAILING, and the case was scored a pass. The job only went
  # red because verify_truthset.py is a separate step. gate.py below splits the two and owns
  # the exit code; 0 here keeps the CLI grading and out of the deciding.
  --threshold 0
  # A RUNAWAY GUARD, not a budget — same figure and same reasoning as the sibling
  # suite. A ceiling low enough to bind does not save money, it truncates a
  # legitimate run into a `partial` and reports a false failure.
  --max-cost-usd "${EVAL_MAX_COST_USD:-75}"
  --no-publish
  --json "$json_out"
)
help_text="$(claude plugin eval --help 2>&1 || true)"
case "$help_text" in *--trust-plugin*) args+=(--trust-plugin) ;; esac

# --keep-temp is LOAD-BEARING, not a debugging nicety. gate.py reads each run's trace.jsonl to
# prove the Senzing MCP was actually connected in that session, and the CLI writes that trace
# INSIDE the scaffold dir it deletes on exit unless this flag is set (`--keep-temp  Preserve
# scaffold dirs for debugging`). gate.py now FAILS a run whose traces it could not read rather
# than passing on no evidence, so keeping them is part of running the suite -- not something
# every caller must remember. CI passes it too; this appends it only when neither the caller
# nor an older CLI already covered it, so the flag is never duplicated and never invented.
case " $* " in
  *" --keep-temp "*) : ;;
  *) case "$help_text" in *--keep-temp*) args+=(--keep-temp) ;; esac ;;
esac

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

# The verdict: two independent gates (deterministic hard, judge scored) plus the discovery,
# partial-run and session-trace checks. This is the behavioral suite's gate.py, used verbatim —
# a second scorer for the one suite that measures a real outcome is how this job passed a case
# with a red deterministic grader (see the --threshold 0 comment above). gate.py is unit-tested
# offline by scripts/check-eval-gate.py, which check.sh runs on every commit.
gate="$plugin_dir/evals/gate.py"
if [ ! -f "$gate" ]; then
  echo "::error::scorer not found at $gate — this suite cannot issue a verdict without it" >&2
  exit 1
fi
gate_args=("$json_out" "$expected" --judge-threshold "$judge_threshold"
           --summary-title "Real-Senzing eval")
# The judge stays REPORTED, not gating, exactly as in the behavioral suite: the CLI records the
# judge's votes but not its reasoning, so a judge FAIL is not diagnosable from the artifact.
# This case does have one llm grader (`criteria`); its eight others are deterministic and hard.
if [ -n "${EVAL_JUDGE_ENFORCE:-}" ] && [ "${EVAL_JUDGE_ENFORCE}" != "0" ]; then
  gate_args+=(--enforce-judge)
fi
set +e
python3 "$gate" "${gate_args[@]}"
gate_rc=$?
set -e
# A gate failure wins; otherwise propagate whatever the CLI itself said (a crash, a budget
# abort). The CLI's own --threshold is 0, so its exit code no longer carries a score verdict.
if [ "$gate_rc" -ne 0 ]; then exit "$gate_rc"; fi

exit "$rc"
