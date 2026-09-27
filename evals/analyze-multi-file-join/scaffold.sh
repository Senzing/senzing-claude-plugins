#!/usr/bin/env bash
# Scaffold for the `analyze-multi-file-join` eval case: copy the two RELATED synthetic CSVs
# (customers.csv, orders.csv — joined on customer_id) into the run workspace.
# Runs outside the agent sandbox, only under `claude plugin eval ... --scaffold`.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$here"/fixtures/customers.csv "$here"/fixtures/orders.csv "$PWD"/
