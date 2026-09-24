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
  2  the run is structurally unusable (cases missing, partial run, a run that errored,
     a session without the Senzing MCP, or not one session trace the gate could read)
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


def evaluate_case(case: dict, blind_runs: set[int] | None = None) -> dict:
    """Split one case's graders into the deterministic gate and the judge score.

    ``blind_runs`` are run indices this suite already proved had NO Senzing MCP
    tools in session. They are excluded rather than graded: a session with no
    tools cannot exercise the skill, so every assertion about the skill measures
    the outage, not the plugin. Grading them anyway is how a 2.5-minute
    CONNECT_TIMEOUT window was reported as 40 plugin assertion failures while
    the skill under test was behaving exactly as written -- `poc-planner`
    refused to produce a plan it could not ground, which is its rule 3.

    This does NOT soften the gate. A case whose every run was blind reports
    `not measured` and still exits non-zero; the suite stays red and the PR
    stays unmergeable. It only stops issuing a SKILL verdict on a session that
    had no skill tools.
    """
    blind_runs = blind_runs or set()
    types = {g.get("name"): g.get("type") for g in case.get("graders") or []}
    runs = (case.get("arms") or {}).get(SUBJECT_ARM) or []

    det_failures: dict[str, dict] = {}   # grader name -> {runs: [i, ...], why: str}
    det_names: set[str] = set()
    judge_per_run: list[float] = []
    errors: list[str] = []

    blind_skipped: list[int] = []
    for i, run in enumerate(runs):
        if i in blind_runs:
            blind_skipped.append(i)
            continue
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
        "blind_runs": blind_skipped,
        "measured_runs": len(runs) - len(blind_skipped),
    }


# The CLI's own words when a session never got the MCP's tools. Matching the
# terminal message rather than the init snapshot is what separates "the server
# was slow to connect" from "this session could not exercise the plugin at all".
TOOLS_UNAVAILABLE = "failed to connect, so their tools are unavailable"
CONNECT_TIMEOUT = "CONNECT_TIMEOUT"


def session_defects(report: dict, base_dir: str | None = None) -> tuple[list[dict], dict]:
    """Runs whose session never had the Senzing MCP connected, plus what was actually read.

    A `tool_used: mcp__…` grader cannot tell "the skill declined to call the tool" from
    "the tool was not in the session", and neither can a judge reading the transcript. The
    CLI records the answer at the top of every trace: the `system`/`init` event carries
    `mcp_servers`, each with a `status`. Anything other than `connected` means the agent was
    graded without the tools under test, which is an invalid measurement, not a plugin
    verdict — so it fails the run STRUCTURALLY rather than showing up as skill defects.

    Real: CLI 2.1.278 starts a session without waiting for the plugin MCP server, and the
    first session on a runner can stay `pending` forever — one run burned five ToolSearch
    calls and twenty seconds of sleeps before giving up with zero `mcp__` calls, and every
    Senzing assertion in it would have failed as though the skill were at fault. Measured
    the other way too: all 66 traces of the last 2.1.259 run were `connected`.

    THE CHECK MUST NOT FAIL OPEN. Its first version `continue`d on a missing `tracePath` and
    on a path that no longer existed, so "not one trace could be opened" was indistinguishable
    from "every session was connected" — a clean structural pass issued on zero evidence. The
    sibling real-Senzing workflow already hit exactly that: it "collected 0 traces on two
    consecutive runs — which silently disabled the bwrap check", the one line in that job that
    would have said the sandbox was broken. So the counts come back with the defects and the
    caller fails the run when nothing was inspected.

    `counts` is over the runs this gate is entitled to expect a trace from:
      graded   — runs that did NOT error. An errored run never started a session, and the CLI
                 writes `"tracePath": ""` for it (measured: every empty tracePath across twelve
                 real result JSONs belongs to a run with a non-null `error`). Those already
                 fail structurally as "a run errored before grading"; counting them here would
                 report the same fault twice under a misleading name.
      declared — graded runs that carry a non-empty tracePath.
      read     — declared traces whose file was found and opened. Not "parsed": a trace whose
                 init event is absent or malformed still proves the gate had the artifact in
                 hand, which is the claim being defended.
    """
    defects: list[dict] = []
    counts = {"graded": 0, "declared": 0, "read": 0, "blind": 0}
    for case in report.get("cases") or []:
        for arm_runs in (case.get("arms") or {}).values():
            for idx, run in enumerate(arm_runs or []):
                if run.get("error"):
                    continue
                counts["graded"] += 1
                path = run.get("tracePath")
                if not path:
                    continue
                counts["declared"] += 1
                # tracePath is absolute in CLI output; resolve a relative one against the
                # result JSON so a results artifact carrying its own traces stays readable.
                if base_dir and not os.path.isabs(path):
                    path = os.path.join(base_dir, path)
                if not os.path.exists(path):
                    continue
                status = None
                blind = False
                try:
                    with open(path, encoding="utf-8", errors="replace") as fh:
                        for line in fh:
                            # Terminal evidence beats the init snapshot. `pending`
                            # at init is a benign race — a run can report pending
                            # and then make a dozen MCP calls once the handshake
                            # lands. What proves a session never got tools is the
                            # CLI saying so later, in a tool result.
                            if TOOLS_UNAVAILABLE in line or CONNECT_TIMEOUT in line:
                                blind = True
                            if '"subtype":"init"' not in line:
                                continue
                            try:
                                event = json.loads(line)
                            except ValueError:
                                continue
                            if event.get("type") != "system":
                                continue
                            for server in event.get("mcp_servers") or []:
                                if "senzing" in str(server.get("name", "")):
                                    status = server.get("status")
                except OSError:
                    continue
                counts["read"] += 1
                if blind:
                    counts["blind"] += 1
                    defects.append({"case": case.get("name", "?"), "run": idx,
                                    "status": status or "unknown", "blind": True})
                elif status is not None and status != "connected":
                    # Init said not-connected but the session never complained —
                    # report it as a soft signal, do NOT exclude its grading.
                    defects.append({"case": case.get("name", "?"), "run": idx,
                                    "status": status, "blind": False})
    return defects, counts


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
    ap.add_argument("--summary-title", default="Behavioral eval",
                    help="heading this verdict is filed under in GITHUB_STEP_SUMMARY. Two "
                         "suites share this scorer; the heading must say which one ran.")
    args = ap.parse_args()

    with open(args.result_json, encoding="utf-8") as fh:
        report = json.load(fh)

    # Detect MCP-blind runs BEFORE grading, so a session that never got the
    # plugin's tools is excluded from the plugin's verdict instead of being
    # scored by it. Ordering is the whole fix: this used to run after grading,
    # so the suite could certify a run invalid and still publish its assertions.
    blind, traces = session_defects(
        report, os.path.dirname(os.path.abspath(args.result_json)))
    blind_by_case: dict[str, set[int]] = {}
    for d in blind:
        if d.get("blind"):
            blind_by_case.setdefault(d["case"], set()).add(d["run"])

    cases = [
        evaluate_case(c, blind_by_case.get(c.get("name", "?")))
        for c in report.get("cases") or []
    ]
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

    emit(f"SESSION traces      {traces['read']}/{traces['graded']} graded run(s) inspected for "
         f"MCP connectivity ({traces['declared']} declared a tracePath) — "
         f"{len(blind)} run(s) not connected, {traces['blind']} of them with NO tools in "
         f"session (excluded from grading, not scored)")
    for c in cases:
        if c.get("blind_runs"):
            emit(f"    NOT MEASURED {c['name']}  run(s) {c['blind_runs']} had no Senzing MCP "
                 f"tools — {c['measured_runs']} of {c['runs']} run(s) actually graded")

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
            fh.write(f"### {args.summary_title}\n\n```\n" + "\n".join(lines) + "\n```\n")

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
    # Nothing inspected is not a clean bill of health. See session_defects' docstring: the
    # first version of this check `continue`d past every unreadable trace and then reported
    # structural success, which is a verdict about a measurement that never happened.
    if traces["graded"] and not traces["read"]:
        print(f"::error::the session gate inspected NOTHING: {traces['graded']} graded run(s), "
              f"{traces['declared']} with a tracePath, 0 traces readable — so this run carries "
              "NO evidence that the Senzing MCP was connected in any session. Likely cause: the "
              "run's temp workspaces were cleaned up before the gate ran (pass --keep-temp to "
              "`run.sh`), or the CLI stopped recording tracePath. Do not read the verdict above "
              "as a connectivity pass.", file=sys.stderr)
        tripped.append((2, "structural: no session traces readable"))
    if blind:
        print(f"::error::{len(blind)} run(s) started without the Senzing MCP connected, so the "
              "agent was graded without the tools under test — an invalid measurement, not a "
              "plugin verdict: "
              + ", ".join(f"{d['case']}#{d['run']} ({d['status']})" for d in blind[:8]),
              file=sys.stderr)
        tripped.append((2, "structural: session had no Senzing MCP"))

    # A case with NO measured run is not a pass. Excluding blind runs from the
    # plugin's verdict must never turn "we could not measure this" into silence
    # — that would be the one change that actually weakens the gate.
    unmeasured = [c for c in cases if c.get("measured_runs") == 0 and c.get("runs")]
    if unmeasured:
        print("::error::" + f"{len(unmeasured)} case(s) had NO measured run — every run lost the "
              "Senzing MCP, so nothing about the plugin was tested: "
              + ", ".join(c["name"] for c in unmeasured), file=sys.stderr)
        tripped.append((2, "structural: case not measured at all"))

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
