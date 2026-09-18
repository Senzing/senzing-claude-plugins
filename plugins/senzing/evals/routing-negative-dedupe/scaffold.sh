#!/usr/bin/env bash
# Scaffold for the `routing-negative-dedupe` eval case: copy the synthetic CSV into the workspace.
# Runs outside the agent sandbox, only under `claude plugin eval ... --scaffold`.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$here"/fixtures/customers.csv "$PWD"/
