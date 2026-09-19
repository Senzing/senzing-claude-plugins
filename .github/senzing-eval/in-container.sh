#!/usr/bin/env bash
# Run one command inside the real-Senzing eval container.
#
# Every step of the `real-senzing-e2e` job goes through here so they share one
# container contract: the repo at /work, and a HOST directory mounted at /tmp so
# the eval's temp workspaces (which `--keep-temp` preserves) survive from the
# step that runs the eval to the step that verifies the repository it left behind.
#
# --privileged is deliberate, and it is the whole reason this job runs in a
# container it builds rather than directly on the runner. `claude plugin eval`
# grants the agent Bash, which needs a sandbox, which on Linux is bubblewrap,
# which needs an unprivileged user namespace — and the GitHub ubuntu runner's
# AppArmor profile denies exactly that (fault 1 of the three documented on the
# behavioral-eval job in ci.yml). The narrower equivalent is
# `--security-opt apparmor=unconfined --security-opt seccomp=unconfined
# --cap-add SYS_ADMIN`; try that first if --privileged is ever unavailable. The
# host is an ephemeral, single-use GitHub runner VM.
#
# Usage: in-container.sh '<shell command>'
set -euo pipefail

: "${SENZING_EVAL_IMAGE:?SENZING_EVAL_IMAGE must be set}"
: "${SENZING_EVAL_TMP:?SENZING_EVAL_TMP must be set (host dir mounted at /tmp)}"

if [ "$#" -ne 1 ]; then
  echo "usage: $0 '<shell command>'" >&2
  exit 2
fi

exec docker run --rm \
  --privileged \
  --shm-size=2g \
  --volume "$PWD:/work" \
  --volume "$SENZING_EVAL_TMP:/tmp" \
  --workdir /work \
  --env TMPDIR=/tmp \
  --env HOME=/root \
  --env ANTHROPIC_API_KEY \
  --env CLAUDE_CODE_WALNUT_SPIRE \
  --env EVAL_RUNS \
  --env EVAL_THRESHOLD \
  --env EVAL_MAX_COST_USD \
  --env EVAL_MODEL \
  --env EVAL_JUDGE_MODEL \
  "$SENZING_EVAL_IMAGE" \
  bash -c "$1"
