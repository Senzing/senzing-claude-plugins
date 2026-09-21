#!/usr/bin/env python3
"""Score an eval run as TWO independent verdicts instead of one blended average.

WHY THIS EXISTS
---------------
`claude plugin eval` scores a case as *the fraction of its graders that passed* and compares
that one number to `--threshold`.  With the suite's historical threshold of 0.8 that reads:
"20% of my own assertions may fail and the case still passes."

That is a coherent statement about a judge's opinion.  It is nonsense for the other graders.
`skill-fired` either fired or it did not.  A regex either matched or it did not.  There is no
such thing as 80% of a boolean, and the blend let both errors through in both directions:

  * a passing judge carried a FAILING deterministic assertion over the line
    (at 42a2ed0 the suite reported 14/14 while `install-eula/eula-surfaced`,
    `poc-planner-grounded/no-shell-ran`, `.../tbd-only-in-literal-form` and
    `report-empty-instance/skill-fired` were all failing);
  * a failing judge sank cases whose deterministic assertions were all green,
    and the report gave no way to tell the two apart.

So this script splits them:

  DETERMINISTIC gate  — `regex`, `tool_used`, `tool_order`, `file_exists`, ...
                        Hard. Every such grader must pass in EVERY run of the case.
                        Not averaged, not weighted, no threshold.  A boolean obligation the
                        skill honours only half the time is a defect, not a rounding error.

  JUDGE score         — `llm` graders only.  Legitimately fractional, so it keeps a threshold
                        of its own (`--judge-threshold`), reported as its own number and
                        failing with its own message.  It can never mask, or be masked by,
                        the deterministic gate.

Exit codes.  More than one can apply to a single run; the HIGHEST one is returned, and the
closing `gate verdict:` line names every gate that tripped.  The code is a LABEL for what to
read first, not a severity ranking -- every caller treats any non-zero as a failed suite.

  0  both gates clean
  1  a deterministic assertion failed
  2  the run is structurally unusable (cases missing, partial run, a run that errored)
  3  judge below its threshold, with --enforce-judge

Highest-wins is what the docstring always claimed, but not what the code did: the checks were
written in order and the deterministic one ran LAST, so its rc=1 silently overwrote the
structural rc=2.  A run that errored before grading and also had a red assertion therefore
reported "a deterministic assertion failed" -- a verdict about a measurement that never
completed, which is exactly the class of confident-but-meaningless number this script exists
to stop.  Computing the code with max() also makes it independent of the order the checks
happen to be written in.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# The one fractional grader kind.  Everything else is a boolean obligation.
JUDGE_TYPES = {"llm"}
# Only the "with" arm is the plugin under test; an ablation arm is SUPPOSED to do worse.
SUBJECT_ARM = "with"


def _fmt(score: float | None) -> str:
    return "  n/a" if score is None else f"{score:5.2f}"


def evaluate_case(case: dict) -> dict:
    """Split one case's graders into the deterministic gate and the judge score."""
    types = {g.get("name"): g.get("type") for g in case.get("graders") or []}
    runs = (case.get("arms") or {}).get(SUBJECT_ARM) or []

    det_failures: dict[str, dict] = {}   # grader name -> {runs: [i, ...], why: str}
    det_names: set[str] = set()
    judge_per_run: list[float] = []
    errors: list[str] = []

    for i, run in enumerate(runs):
        if run.get("error"):
            errors.append(f"run {i}: {run['error']}")
            continue
        graders = run.get("graders") or []
        if not graders:
            errors.append(f"run {i}: no graders were evaluated")
            continue
        judged = []
        for g in graders:
            name = g.get("name", "?")
            # An unknown name means the definition list and the run disagree -- grade it
            # deterministically rather than letting it slip into the fractional bucket.
            if types.get(name) in JUDGE_TYPES:
                judged.append(bool(g.get("passed")))
                continue
            det_names.add(name)
            if not g.get("passed"):
                entry = det_failures.setdefault(name, {"runs": [], "why": ""})
                entry["runs"].append(i)
                entry["why"] = g.get("explanation") or entry["why"]
        if judged:
            judge_per_run.append(sum(judged) / len(judged))

    judge = sum(judge_per_run) / len(judge_per_run) if judge_per_run else None
    return {
        "name": case.get("name", "?"),
        "runs": len(runs),
        "det_total": len(det_names),
        "det_failures": det_failures,
        "judge": judge,
        "judge_runs": len(judge_per_run),
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("result_json")
    ap.add_argument("expected_cases", type=int)
    ap.add_argument("--judge-threshold", type=float, default=0.8)
    ap.add_argument("--enforce-judge", action="store_true",
                    help="make the judge score a hard gate too (exit 3). Off by default: the "
                         "CLI records the judge's VOTES but not its reasoning, so a judge FAIL "
                         "is not diagnosable from the artifact and cannot be a merge gate yet. "
                         "It is still reported, loudly, and nothing averages it away.")
    ap.add_argument("--quiet", action="store_true", help="omit the per-case table")
    args = ap.parse_args()

    with open(args.result_json, encoding="utf-8") as fh:
        report = json.load(fh)

    cases = [evaluate_case(c) for c in report.get("cases") or []]
    lines: list[str] = []

    def emit(text: str = "") -> None:
        lines.append(text)
        print(text)

    if not args.quiet:
        emit(f"\n{'CASE':<28}{'DETERMINISTIC':>15}{'JUDGE':>8}  VERDICT")
        for c in cases:
            det_bad = len(c["det_failures"])
            det_ok = c["det_total"] - det_bad
            det_col = f"{det_ok}/{c['det_total']} {'ok' if not det_bad else 'FAIL'}"
            judge_low = c["judge"] is not None and c["judge"] < args.judge_threshold
            why = []
            if c["errors"]:
                why.append("run error")
            if det_bad:
                why.append("deterministic")
            if judge_low and args.enforce_judge:
                why.append("judge")
            if why:
                verdict = "FAIL (" + " + ".join(why) + ")"
            elif judge_low:
                verdict = "pass · judge below threshold"
            else:
                verdict = "pass"
            emit(f"{c['name']:<28}{det_col:>15}{_fmt(c['judge']):>8}  {verdict}")

    det_bad_cases = [c for c in cases if c["det_failures"]]
    judge_bad_cases = [c for c in cases
                       if c["judge"] is not None and c["judge"] < args.judge_threshold]
    error_cases = [c for c in cases if c["errors"]]
    judged = [c["judge"] for c in cases if c["judge"] is not None]

    emit()
    emit(f"DETERMINISTIC gate  {len(cases) - len(det_bad_cases)}/{len(cases)} cases clean "
         f"(every regex / tool_used / file_exists assertion, in every run — no threshold)")
    for c in det_bad_cases:
        for name, info in sorted(c["det_failures"].items()):
            runs = ",".join(f"#{r}" for r in info["runs"])
            emit(f"    {c['name']}/{name}  failed {len(info['runs'])} of {c['runs']} run(s) "
                 f"({runs}): {info['why']}")
    if judged:
        emit(f"JUDGE score         mean {sum(judged) / len(judged):.2f} over {len(judged)} "
             f"case(s), threshold {args.judge_threshold:.2f} — "
             f"{len(judge_bad_cases)} below "
             f"({'enforced' if args.enforce_judge else 'reported, not gating'})")
    else:
        emit("JUDGE score         no llm graders in this run")
    for c in judge_bad_cases:
        emit(f"    {c['name']}  judge {c['judge']:.2f} across {c['judge_runs']} run(s)")
    for c in error_cases:
        for err in c["errors"]:
            emit(f"    RUN ERROR {c['name']}  {err}")

    agg = report.get("aggregates") or {}
    emit()
    emit(f"cases run={len(cases)} expected={args.expected_cases} "
         f"cli-blended-score={agg.get('overallScore')} cost=${report.get('costUsd')} "
         f"partial={report.get('partial')} ({report.get('partialReason')})")
    emit("(cli-blended-score is the CLI's own average of BOTH grader kinds — reported for "
         "reference only; it decides nothing here.)")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write("### Behavioral eval\n\n```\n" + "\n".join(lines) + "\n```\n")

    # (code, label) for every gate that tripped. Collected rather than assigned so the exit
    # code can be max()'d at the end -- see the module docstring.
    tripped: list[tuple[int, str]] = []
    if len(cases) < args.expected_cases:
        print(f"::error::only {len(cases)} of {args.expected_cases} cases were discovered — "
              "eval layout regression", file=sys.stderr)
        tripped.append((2, "structural: cases missing"))
    if report.get("partial"):
        print(f"::error::partial run: {report.get('partialReason')}", file=sys.stderr)
        tripped.append((2, "structural: partial run"))
    if error_cases:
        print(f"::error::{len(error_cases)} case(s) had a run that errored before grading — "
              "the suite did not measure the plugin", file=sys.stderr)
        tripped.append((2, "structural: a run errored before grading"))
    if judge_bad_cases:
        level = "error" if args.enforce_judge else "warning"
        print(f"::{level}::JUDGE score: {len(judge_bad_cases)} case(s) below "
              f"{args.judge_threshold:.2f} — "
              + ", ".join(f"{c['name']} ({c['judge']:.2f})" for c in judge_bad_cases),
              file=sys.stderr)
        if args.enforce_judge:
            tripped.append((3, "judge below threshold"))
    if det_bad_cases:
        failed = sum(len(c["det_failures"]) for c in det_bad_cases)
        print(f"::error::DETERMINISTIC gate: {failed} assertion(s) failed across "
              f"{len(det_bad_cases)} case(s) — "
              + ", ".join(f"{c['name']}/{n}" for c in det_bad_cases
                          for n in sorted(c["det_failures"])),
              file=sys.stderr)
        tripped.append((1, "deterministic assertion failed"))

    if not tripped:
        return 0
    rc = max(code for code, _ in tripped)
    # One line that says what the exit code means AND everything else that was wrong with the
    # run, so a reader never has to infer the rest from a single number.
    print(f"::error::gate verdict: exit {rc} — "
          + "; ".join(f"[{code}] {label}" for code, label in sorted(tripped)),
          file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
