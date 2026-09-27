#!/usr/bin/env bash
# Scaffold for the `analyze` eval case: copy the synthetic CSV fixtures into the run workspace.
# Runs outside the agent sandbox, only under `claude plugin eval ... --scaffold`.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$here"/fixtures/crm.csv "$here"/fixtures/billing.csv "$PWD"/
