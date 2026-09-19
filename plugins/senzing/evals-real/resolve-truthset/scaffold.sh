#!/usr/bin/env bash
# Scaffold for the `resolve-truthset` eval case.
#
# Copies the three vendored truth-set CSVs into the run workspace, and drops a
# marker file so the job's ground-truth verification step can find this
# workspace afterwards (`claude plugin eval --keep-temp` preserves it, but the
# path is a random temp dir the job never gets told about).
#
# The ground-truth KEY is deliberately NOT copied in: the agent must not be able
# to read the answer it is being graded on. It stays in ../ground-truth/ and is
# only ever read by verify_truthset.py, outside the agent's sandbox.
#
# Runs outside the agent sandbox, only under `claude plugin eval ... --scaffold`.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$here"/fixtures/customers.csv "$here"/fixtures/reference.csv "$here"/fixtures/watchlist.csv "$PWD"/
: > "$PWD/.sz-eval-root"
