#!/usr/bin/env bash
# Run the eval suite (or ONE case) locally, cheaply, without CI.
#
# Why this wrapper exists — three things block `evals/run.sh` on a developer Mac,
# and none of them is obvious from its error messages:
#
#   1. The CLI floor. run.sh requires >= 2.1.269 and must NOT be 2.1.278 (which
#      starts sessions before a plugin MCP connects). On this machine `claude` is
#      a Homebrew cask symlink, so `npm i -g` cannot replace it. Install the pinned
#      CLI into a private prefix instead and put it first on PATH:
#         mkdir -p ~/.local/claude-eval
#         npm install --prefix ~/.local/claude-eval @anthropic-ai/claude-code@2.1.269
#
#   2. The Docker credential store. The Bash sandbox refuses to run when ~/.docker
#      holds symlinks anywhere inside it — Docker Desktop puts 43 of them in
#      ~/.docker/bin and ~/.docker/cli-plugins. DOCKER_CONFIG is not forwarded by
#      run.sh's env allowlist, so it cannot be redirected. Dismantling a working
#      Docker install for an eval is the wrong trade, so this runs with HOME
#      pointed at a scratch directory: the sandbox then finds no store at all.
#
#   3. The API key. run.sh reads $HOME/.env, which the scratch HOME does not have,
#      so the key is exported from the REAL home first. It is never copied to disk.
#
# Usage:
#   evals/local.sh --case report-empty-instance            # 1 run, the default
#   EVAL_RUNS=10 evals/local.sh --case poc-planner-grounded
#   EVAL_MODEL=opus EVAL_RUNS=5 evals/local.sh --case <case>   # four-model diagnosis
#
# Cost, measured: sandbox-canary $0.08/run, report-empty-instance $0.27,
# install-eula $0.44, poc-planner-grounded $0.74. A full CI cycle is ~$19.50 and
# ~70 minutes, and samples each case only TWICE — a 1-in-5 flake survives that 64%
# of the time. That is why fixes get measured here before they get pushed.
set -euo pipefail

real_home="${HOME}"
cli_prefix="${SZ_EVAL_CLI_PREFIX:-$real_home/.local/claude-eval}"
cli_bin="$cli_prefix/node_modules/.bin"

if [ ! -x "$cli_bin/claude" ]; then
  echo "ERROR: pinned CLI not found at $cli_bin/claude" >&2
  echo "  mkdir -p $cli_prefix" >&2
  echo "  npm install --prefix $cli_prefix @anthropic-ai/claude-code@2.1.269" >&2
  exit 1
fi

# Export the key from the REAL home before HOME is redirected.
if [ -f "$real_home/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$real_home/.env"
  set +a
fi
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "ERROR: ANTHROPIC_API_KEY not set and not found in $real_home/.env" >&2
  exit 1
fi

scratch="${SZ_EVAL_HOME:-${TMPDIR:-/tmp}/sz-eval-home}"
mkdir -p "$scratch"

# The sandbox hides HOME, not the filesystem. Several cases assert that Senzing
# is ABSENT — doctor-healthy-no-sdk by name, and the gates in recipes, demo and
# report that must refuse on a host which cannot deliver a result. On a machine
# with Senzing installed those cases measure the opposite of what they mean:
# doctor correctly reports an install and marks a misbehaving engine ❌, and
# recipes correctly cooks instead of refusing. Both then fail graders that are
# right about CI and wrong about here.
#
# This cost a real investigation: two "defects" were diagnosed and nearly fixed
# in skills that were behaving correctly. Warn loudly rather than pretend.
sz_local=""
for d in /opt/senzing "$(brew --prefix 2>/dev/null)/opt/senzing"; do
  [ -n "$d" ] && [ -d "$d" ] && sz_local="$d" && break
done
if [ -n "$sz_local" ]; then
  echo "== WARNING: Senzing is installed on this host ($sz_local) ==" >&2
  echo "   Cases that assert Senzing is ABSENT will not measure what they mean here:" >&2
  echo "     doctor-healthy-no-sdk, recipes-named, demo-no-simulation, report-empty-instance" >&2
  echo "   Their graders are correct for CI's empty sandbox. Run those in CI, or read a" >&2
  echo "   failure here as 'the host differs', not as a defect." >&2
  echo "   Cases that do not depend on absence (poc-planner*, ask*, build, troubleshoot," >&2
  echo "   recipes-catalog, analyze*) measure normally." >&2
fi

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "== local eval: CLI $("$cli_bin/claude" --version), HOME=$scratch, runs=${EVAL_RUNS:-1}, model=${EVAL_MODEL:-sonnet} =="

HOME="$scratch" \
PATH="$cli_bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin" \
ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  exec "$here/run.sh" "$@"
