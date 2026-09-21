#!/usr/bin/env python3
"""Offline check for the eval scoring split (`plugins/senzing/evals/gate.py`).

The suite's verdict is now two independent gates — deterministic assertions (hard, every
grader in every run) and the llm judge (scored separately). That logic decides whether a
$6-17 eval run is a pass, so it must itself be verifiable for free: this runs gate.py against
synthetic result JSONs in `plugins/senzing/evals/gate-fixtures/` and asserts the exit code and
the output text named in `expectations.json`.

The fixtures encode the failure modes that actually happened, not hypotheticals:
  * masked-deterministic  — the defect the split exists to fix (42a2ed0 reported 14/14 with
                            four deterministic assertions red)
  * flaky-deterministic   — a boolean obligation honoured in one run and not the other
  * judge-only            — the opposite error: a judge dissent read as a case failure
  * run-error / partial   — a run that graded nothing must never pass vacuously
  * structural-and-deterministic
                          — both at once: the exit code must be the highest of the two, so a
                            run that never completed does not report as an assertion defect

Exit 1 on any mismatch.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "plugins" / "senzing" / "evals" / "gate-fixtures"
GATE = ROOT / "plugins" / "senzing" / "evals" / "gate.py"


def main() -> int:
    spec = json.loads((FIXTURES / "expectations.json").read_text(encoding="utf-8"))
    checks = spec["checks"]
    print(f"== eval scoring split: {len(checks)} case(s) against {GATE.name} ==")

    failures = 0
    for check in checks:
        cmd = [sys.executable, str(GATE), str(FIXTURES / check["fixture"]),
               str(check["expected_cases"])]
        if check.get("enforce_judge"):
            cmd.append("--enforce-judge")
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        out = proc.stdout + proc.stderr
        problems = []
        if proc.returncode != check["rc"]:
            problems.append(f"exit {proc.returncode}, expected {check['rc']}")
        for needle in check.get("must_contain", []):
            if needle not in out:
                problems.append(f"missing from output: {needle!r}")
        for needle in check.get("must_not_contain", []):
            if needle in out:
                problems.append(f"unexpectedly present: {needle!r}")
        if problems:
            failures += 1
            print(f"FAIL {check['name']}")
            for p in problems:
                print(f"       {p}")
            print("     --- gate.py output ---")
            for line in out.splitlines():
                print(f"     | {line}")
        else:
            print(f"ok   {check['name']} (exit {proc.returncode})")

    print()
    if failures:
        print(f"eval scoring split check: {failures} failure(s)")
        return 1
    print("eval scoring split check: all clear")
    return 0


if __name__ == "__main__":
    sys.exit(main())
