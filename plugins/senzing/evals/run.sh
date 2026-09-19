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
#
# Scoring is NOT the CLI's blended average — see gate.py next to this file. Deterministic
# graders (regex / tool_used / file_exists / tool_order) must ALL pass in EVERY run; the llm
# judge is scored separately against its own threshold and can neither mask nor be masked by
# them. The CLI is therefore run with `--threshold 0`: it grades, gate.py decides.
#
# Usage: plugins/senzing/evals/run.sh [--case <glob>] [extra claude-plugin-eval args...]
# Env:   EVAL_RUNS (default 2)  EVAL_MAX_COST_USD (default 75)
#        EVAL_JUDGE_THRESHOLD (default 0.8; EVAL_THRESHOLD honored as the old name)
#        EVAL_JUDGE_ENFORCE=1 makes the judge score a hard gate too (default: reported only)
#        EVAL_CONCURRENCY (default 3)  EVAL_JSON (default <evals>/results/ci.json)
#        EVAL_MODEL (default sonnet)   EVAL_JUDGE_MODEL (default sonnet)
# Needs: ANTHROPIC_API_KEY (or a logged-in claude), the sandbox backend for Bash grants
#        (macOS: built in; Linux: bubblewrap + socat), and network to mcp.senzing.com.
set -euo pipefail

# Load local credentials so the suite can be run WITHOUT pushing to CI.
# A CI-only eval means every iteration costs a push plus ~55 minutes of queue,
# which is how a one-line fix turned into an hour repeatedly. Run it here first.
#
# ~/.env is the standard location across the Senzing MCP repos, and it is
# deliberately OUTSIDE every checkout: this repo is public, so a key living in
# the tree is one `git add -A` away from being published. The in-repo
# .env.local is honored second for per-repo overrides and is gitignored.
# CI has neither file and uses the ANTHROPIC_API_KEY repo secret instead.
for _env_file in "$HOME/.env" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/.env.local"; do
  if [ -f "$_env_file" ]; then
    echo "loading credentials from ${_env_file/#$HOME/~}"
    set -a
    # shellcheck disable=SC1090
    . "$_env_file"
    set +a
  fi
done

# Validate the key POSITIVELY -- it must look like a real Anthropic key --
# rather than blocklisting placeholder shapes. A blocklist only catches the
# junk you thought of: a `pbpaste` that had the wrong thing on the clipboard
# wrote 347 characters of prose here, which matched no placeholder pattern,
# passed a bare -z check, and would have failed later as an opaque auth error
# far from the cause. Anthropic keys are `sk-ant-` + a long opaque tail and
# contain no whitespace, so require exactly that.
_key_ok=1
case "${ANTHROPIC_API_KEY:-}" in
  sk-ant-*) : ;;
  *) _key_ok=0 ;;
esac
# Reject embedded whitespace/newlines (a multi-line paste) and absurd lengths.
case "${ANTHROPIC_API_KEY:-}" in *[[:space:]]*) _key_ok=0 ;; esac
if [ "${#ANTHROPIC_API_KEY}" -lt 40 ] || [ "${#ANTHROPIC_API_KEY}" -gt 300 ]; then
  _key_ok=0
fi
if [ "$_key_ok" -eq 0 ]; then
  if [ "${CI:-}" = "true" ]; then
    echo "ERROR: ANTHROPIC_API_KEY is unset in CI." >&2
    echo "This job must FAIL rather than skip — an eval that passes by not running" >&2
    echo "is how this suite stayed green for its entire existence. Set the secret." >&2
    exit 1
  fi
  cat >&2 <<'NO_KEY_HELP'
ERROR: ANTHROPIC_API_KEY is unset or is a placeholder.

Set it in $HOME/.env -- outside every repo, so it cannot be committed:

  printf 'ANTHROPIC_API_KEY: ' && read -rs K \
    && printf 'ANTHROPIC_API_KEY=%s\n' "$K" > "$HOME/.env" \
    && chmod 600 "$HOME/.env" && unset K

That form prompts for the value, so the key never reaches shell history or a
terminal transcript. It uses a separate printf for the prompt because read's
-p flag is bash-only -- under zsh (the default shell on macOS) `read -p`
fails with "no coprocess" and the && chain silently aborts, leaving whatever
was in the file before. Do NOT paste a literal key onto a command line: a
documented example string was copied verbatim into $HOME/.env once already,
and a non-empty placeholder is worse than an empty one -- it survives a bare
emptiness check and then fails as an opaque auth error far from the cause.
NO_KEY_HELP
  exit 1
fi

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_dir="$(dirname "$here")"
eval_dir_name="$(basename "$here")"
results_dir="$here/results"
json_out="${EVAL_JSON:-$results_dir/ci.json}"
judge_threshold="${EVAL_JUDGE_THRESHOLD:-${EVAL_THRESHOLD:-0.8}}"
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
echo "== subject model: ${EVAL_MODEL:-sonnet} | judge model: ${EVAL_JUDGE_MODEL:-sonnet} =="

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
  # Pin BOTH models. Neither was set before, which made the suite unreproducible:
  # --model defaulted to whatever the CLI resolved in that environment (a logged-in
  # user locally vs. an API key in CI can differ), and --judge-model defaulted to
  # haiku. So a local pass and a CI pass were not the same measurement, and the
  # branch's "weak-model routing 17/20 -> 20/20" number could drift underneath it.
  # The judge matters as much as the subject: poc-planner-grounded asks for subtle
  # calls (arithmetic-extrapolation fabrication, a bare "TBD — decided by" with
  # nothing after it) and a judge that misses them fails OPEN.
  # --judge-model is global, so this applies suite-wide, not per case.
  --model "${EVAL_MODEL:-sonnet}"
  --judge-model "${EVAL_JUDGE_MODEL:-sonnet}"
  --runs "${EVAL_RUNS:-2}"
  # Deliberately 0 — the CLI must NOT issue the verdict. Its --threshold is compared against
  # a single blended score: the fraction of a case's graders that passed, judge and
  # deterministic averaged together. At 0.8 that said "20% of my own assertions may fail",
  # which is a coherent statement about a judge's opinion and nonsense about `skill-fired`.
  # It let a passing judge carry a FAILING deterministic assertion over the line (at 42a2ed0
  # the suite reported 14/14 with four deterministic assertions red). gate.py below splits
  # the two and owns the exit code; 0 here keeps the CLI grading and out of the deciding.
  --threshold 0
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
  # NEVER exit 0 here. `rc` is always set (rc=${PIPESTATUS[0]} above), so the old
  # `exit "${rc:-1}"` propagated a CLI exit of 0 and the job went GREEN having graded
  # nothing -- an `::error::` annotation alone does not fail a GitHub Actions step.
  # No result JSON means the suite did not run, which is a failure whatever the CLI said.
  if [ "$rc" -ne 0 ]; then exit "$rc"; fi
  exit 1
fi

# The verdict: two independent gates (deterministic hard, judge scored) plus the discovery
# and partial-run checks. gate.py is unit-tested offline by scripts/check-eval-gate.py, which
# check.sh runs on every commit — so the scoring logic itself never needs a paid run to verify.
gate_args=("$json_out" "$expected" --judge-threshold "$judge_threshold")
if [ -n "${EVAL_JUDGE_ENFORCE:-}" ] && [ "${EVAL_JUDGE_ENFORCE}" != "0" ]; then
  gate_args+=(--enforce-judge)
fi
set +e
python3 "$here/gate.py" "${gate_args[@]}"
gate_rc=$?
set -e
# A gate failure wins; otherwise propagate whatever the CLI itself said (a crash, a budget
# abort). The CLI's own --threshold is 0, so its exit code no longer carries a score verdict.
if [ "$gate_rc" -ne 0 ]; then exit "$gate_rc"; fi

exit "$rc"
