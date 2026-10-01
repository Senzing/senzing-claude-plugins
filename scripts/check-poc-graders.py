#!/usr/bin/env python3
"""Offline fixture check for the poc-planner eval graders that are still regexes.

Two questions, answered without spending an eval run:

1. Does any `not_contains` regex grader fire on the VERBATIM tool output the plan is REQUIRED to
   quote?  The skill body makes the plan quote the Hardware Sizing FAQ ("Phase 1/2/3"), the
   `reporting_guide(quality)` notes (">80%"), Database Tuning ("your DBA"), the PoC article's
   own rules ("Mock up specific test cases") and the license text of three tools.  A grader that
   matches any of that fails a CORRECT run — a false-fail in waiting.
2. Do the file-targeted graders PASS a correct plan that quotes all of the above, and does the
   fabricated plan still trip the ones that remain?  `grader-fixtures/plans/expectations.json`
   says which.

Scope note (2026-09-29): the content prohibitions this script was written for — metric
thresholds, duration ranges, phase labels, schedule words, invented roles, hardware
recommendations, extra `SC-n` keys, non-TBD targets — moved to the llm judge
(`poc-planner-grounded/graders/criteria.md`), because each needed a quote exemption bolted on
after failing a plan for quoting Senzing, and `constraints-carry-user-database` failed correct
plans on spelling.  What is left deterministic is the file's literal structure: the nine
`## N.` headings, the §2 keys, `SC-n` ids, a URL, the `poc_guidance_chunks_retrieved:` line, and
the `TBD — decided by` literal (present, and the only form a TBD may take).  Section A therefore
guards one grader today (`tbd-only-in-literal-form`); it stays because the corpus fixtures are
what a new regex must be tried against before it ships.

Section D (2026-10-01): the judge clauses are one `judge-*.md` grader per clause now, not one
`criteria.md`, so a judge FAIL names the clause.  The judge cannot run offline, so D asserts
what can be checked for free: every llm grader focuses on the plan file; all of them carry the
IDENTICAL shared preamble (the quoted-with-source exemption each clause depends on — a drifted
copy is how a correct plan fails one clause); and each clause `expectations.json` says the
fabricated plan violates still has its evidence in that fixture and not in the correct one, so
the fixture keeps exercising the clause it documents.

Python `re` is used as a stand-in for the CLI's JavaScript engine; the patterns here use only the
common subset (classes, alternation, lookahead, `flags: i`).  Exit 1 on any failure.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
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


GROUNDED_GRADERS = EVALS / "poc-planner-grounded" / "graders"
SHARED_START = "> **Shared preamble"
CLAUSE_START = "## This grader's clause"


def shared_region(text: str) -> str | None:
    """Everything from the shared-preamble blockquote to the clause heading — must be identical
    across every judge-*.md, because it carries the quote exemption each clause depends on."""
    start = text.find(SHARED_START)
    end = text.find(CLAUSE_START)
    if start < 0 or end < 0 or end < start:
        return None
    return text[start:end]


def check_judge_clauses(expectations: dict) -> int:
    failures = 0
    llm = []
    for md in sorted(GROUNDED_GRADERS.glob("*.md")):
        fm = parse_frontmatter(md)
        if fm.get("type") == "llm":
            llm.append((md, fm))
    print(f"\n-- D. {len(llm)} llm clause graders in poc-planner-grounded --")
    if len(llm) < 2:
        print("FAIL the judge is one monolithic rubric again — a FAIL would not name its clause")
        return 1
    regions: dict[str, str] = {}
    for md, fm in llm:
        text = md.read_text(encoding="utf-8")
        if "senzing-poc-plan.md" not in fm.get("focus", ""):
            failures += 1
            print(f"FAIL {md.name}: llm grader not focused on senzing-poc-plan.md (focus: {fm.get('focus')!r})")
        if not md.stem.startswith("judge-"):
            failures += 1
            print(f"FAIL {md.name}: llm clause graders carry the judge- prefix so they cannot collide "
                  f"with a regex grader of the same assertion")
        region = shared_region(text)
        if region is None:
            failures += 1
            print(f"FAIL {md.name}: no shared preamble block / clause heading "
                  f"({SHARED_START!r} … {CLAUSE_START!r})")
            continue
        regions[md.stem] = region
    if regions:
        canon_name, canon = next(iter(regions.items()))
        drifted = [n for n, r in regions.items() if r != canon]
        if drifted:
            failures += len(drifted)
            print(f"FAIL shared preamble drifted from {canon_name}: {', '.join(drifted)} — the quote "
                  f"exemption must read identically in every clause, or a correct plan fails one")
        else:
            print(f"ok   {len(regions)} graders carry the identical shared preamble")

    stems = {md.stem for md, _ in llm}
    plans = FIXTURES / "plans"
    for plan_name, expect in expectations.items():
        if plan_name.startswith("_") or not expect.get("judge_must_fail"):
            continue
        bad_text = (plans / plan_name).read_text(encoding="utf-8")
        good_text = (plans / "correct-plan.md").read_text(encoding="utf-8")
        named = []
        for item in expect["judge_must_fail"]:
            g = item["grader"]
            named.append(g)
            if g not in stems:
                failures += 1
                print(f"FAIL {plan_name}: judge_must_fail names {g}, which is not an llm grader here")
                continue
            ev, miss = item.get("evidence"), item.get("missing")
            if ev is not None:
                if ev not in bad_text:
                    failures += 1
                    print(f"FAIL {plan_name}: evidence for {g} is gone from the fixture: {ev!r}")
                if ev in good_text:
                    failures += 1
                    print(f"FAIL correct-plan.md carries {g}'s violating evidence {ev!r} — either the "
                          f"evidence is not discriminating or the correct plan is not correct")
            if miss is not None:
                if miss in bad_text:
                    failures += 1
                    print(f"FAIL {plan_name}: {g}'s `missing` string is present after all: {miss!r}")
                if miss not in good_text:
                    failures += 1
                    print(f"FAIL correct-plan.md lacks {g}'s `missing` string {miss!r}")
            if ev is None and miss is None:
                failures += 1
                print(f"FAIL {plan_name}: {g} entry has neither evidence nor missing")
        print(f"     {plan_name}: {len(named)} judge clause(s) documented as violated -> "
              + ", ".join(sorted(named)))
        print(f"ok   {plan_name}: every documented clause has a grader and its evidence is still in the fixture"
              if failures == 0 else f"FAIL {plan_name}: see above")
    return failures


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

    # D. The llm judge clauses: one grader per clause, same preamble, evidence still in the fixture.
    failures += check_judge_clauses(expectations)

    print()
    if failures:
        print(f"poc-planner grader fixture check: {failures} failure(s)")
        return 1
    print("poc-planner grader fixture check: all clear")
    return 0


if __name__ == "__main__":
    sys.exit(main())
