#!/usr/bin/env python3
"""Offline fixture check for the poc-planner eval graders.

Two questions, answered without spending an eval run:

1. Does any `not_contains` regex grader fire on the VERBATIM tool output the plan is REQUIRED to
   quote?  The skill body makes the plan quote the Hardware Sizing FAQ ("Phase 1/2/3"), the
   `reporting_guide(quality)` notes (">80%"), Database Tuning ("your DBA"), the PoC article's
   own rules ("Mock up specific test cases") and the license text of three tools.  A grader that
   matches any of that fails a CORRECT run — a false-fail in waiting.  v2 of the proposal
   checked the template's literal text, which is clean; the quotes are not.
2. Do the graders actually FAIL a template-following fabricated plan, and PASS a correct plan
   that quotes all of the above?  `grader-fixtures/plans/expectations.json` says which.

Python `re` is used as a stand-in for the CLI's JavaScript engine; the patterns here use only the
common subset (classes, alternation, lookahead, `flags: i`).  Exit 1 on any failure.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "plugins" / "senzing" / "evals"
FIXTURES = EVALS / "poc-planner-grounded" / "grader-fixtures"
SKILL = ROOT / "plugins" / "senzing" / "skills" / "poc-planner" / "SKILL.md"
EM_DASH = "—"


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Minimal parser for the flat `key: value` frontmatter the graders use (no PyYAML needed)."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line or line.startswith(" "):
            continue
        key, _, raw = line.partition(":")
        raw = raw.strip()
        if raw.startswith('"'):
            value = json.loads(raw)  # YAML double-quoted == JSON escaping for these patterns
        elif raw.startswith("'") and raw.endswith("'") and len(raw) >= 2:
            value = raw[1:-1].replace("''", "'")
        else:
            value = raw
        out[key.strip()] = value
    return out


def load_regex_graders() -> list[dict]:
    graders = []
    for case_dir in sorted(EVALS.glob("poc-planner-*")):
        for md in sorted((case_dir / "graders").glob("*.md")):
            fm = parse_frontmatter(md)
            if fm.get("type") != "regex":
                continue
            target = fm.get("target", "")
            file_target = None
            m = re.search(r"source:\s*file\s*,\s*path:\s*([^\s}]+)", target)
            if m:
                file_target = m.group(1)
            flags = re.I if "i" in fm.get("flags", "") else 0
            graders.append(
                {
                    "case": case_dir.name,
                    "name": md.stem,
                    "pattern": fm["pattern"],
                    "regex": re.compile(fm["pattern"], flags),
                    "match": fm.get("match", "contains"),
                    "target": target,
                    "file_target": file_target,
                }
            )
    return graders


def grader_passes(g: dict, text: str) -> tuple[bool, str]:
    hits = list(g["regex"].finditer(text))
    mode = g["match"]
    if mode == "not_contains":
        return (not hits, hits[0].group(0) if hits else "")
    if mode.startswith("count:"):
        want = int(mode.split(":", 1)[1])
        return (len(hits) == want, f"count={len(hits)}")
    return (bool(hits), hits[0].group(0) if hits else "")


def context(text: str, m: re.Match, width: int = 40) -> str:
    s = max(0, m.start() - width)
    e = min(len(text), m.end() + width)
    return text[s:e].replace("\n", "\\n")


def main() -> int:
    failures = 0
    graders = load_regex_graders()
    neg = [g for g in graders if g["match"] == "not_contains"]
    print(f"== poc-planner graders: {len(graders)} regex ({len(neg)} not_contains) across "
          f"{len({g['case'] for g in graders})} cases ==")

    # A. Every not_contains grader against every verbatim corpus fixture.
    corpus = sorted(p for p in (FIXTURES / "corpus").iterdir() if p.suffix in {".txt", ".json"})
    print(f"\n-- A. {len(neg)} not_contains graders x {len(corpus)} corpus fixtures --")
    hits_total = 0
    for fx in corpus:
        text = fx.read_text(encoding="utf-8")
        for g in neg:
            for m in g["regex"].finditer(text):
                hits_total += 1
                failures += 1
                print(f"FALSE-FAIL {g['case']}/{g['name']} fires on {fx.name}: "
                      f"'{m.group(0)}' in ...{context(text, m)}...")
    print("ok   no not_contains grader fires on any quoted corpus text" if hits_total == 0
          else f"FAIL {hits_total} corpus hit(s) — fix the grader, not the quote")

    # B. Plan fixtures against every file-targeted grader (positive and negative).
    expectations = json.loads((FIXTURES / "plans" / "expectations.json").read_text(encoding="utf-8"))
    file_graders = [g for g in graders if g["file_target"] == "senzing-poc-plan.md"]
    print(f"\n-- B. {len(file_graders)} file-targeted graders x plan fixtures --")
    for plan_name, expect in expectations.items():
        if plan_name.startswith("_"):
            continue
        text = (FIXTURES / "plans" / plan_name).read_text(encoding="utf-8")
        failed = {}
        for g in file_graders:
            ok, why = grader_passes(g, text)
            if not ok:
                failed[g["name"]] = why
        if expect.get("must_pass") == "all":
            if failed:
                failures += 1
                print(f"FAIL {plan_name}: a correct plan trips {len(failed)} grader(s): "
                      + ", ".join(f"{k} ({v!r})" for k, v in failed.items()))
            else:
                print(f"ok   {plan_name}: passes all {len(file_graders)} file graders")
        else:
            must = set(expect.get("must_fail", []))
            missing = must - set(failed)
            print(f"     {plan_name}: {len(failed)} grader(s) fail -> "
                  + ", ".join(f"{k} ({v!r})" for k, v in sorted(failed.items())))
            if missing:
                failures += 1
                print(f"FAIL {plan_name}: fabrication NOT caught by: {', '.join(sorted(missing))}")
            else:
                print(f"ok   {plan_name}: every expected grader fires ({len(must)} required, "
                      f"{len(failed)} total)")

    # C. Em-dash code point: the TBD literal must be U+2014 everywhere it is written.
    print("\n-- C. TBD literal uses U+2014 in the skill body and the grader patterns --")
    bad = 0
    skill = SKILL.read_text(encoding="utf-8")
    for m in re.finditer(r"TBD\s+[-–]\s*decided", skill):
        bad += 1
        print(f"FAIL SKILL.md uses a non-em-dash TBD literal: {m.group(0)!r}")
    for g in graders:
        if "decided by" in g["pattern"] and EM_DASH not in g["pattern"]:
            bad += 1
            print(f"FAIL {g['case']}/{g['name']} spells the TBD literal without U+2014")
    failures += bad
    print("ok   em dash consistent" if bad == 0 else f"FAIL {bad} em-dash drift(s)")

    print()
    if failures:
        print(f"poc-planner grader fixture check: {failures} failure(s)")
        return 1
    print("poc-planner grader fixture check: all clear")
    return 0


if __name__ == "__main__":
    sys.exit(main())
