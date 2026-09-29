#!/usr/bin/env python3
"""Offline parity check: does each skill pin what its graders demand?

Answers, without spending a $20 eval run, the question three CI failures in a row
asked the expensive way:

  A. LITERAL PARITY — a positive regex grader requires a literal string in the
     model's output. If the SKILL.md that must produce it never spells that
     literal, the model free-styles and the assertion fails on some fraction of
     runs. That is exactly how `constraints-carry-user-database` failed: the
     grader wanted `database: per user: PostgreSQL`, the §2 template said only
     `database:`, and the model wrote `per user - PostgreSQL` in 1 run of 2.

  B. CLOSING-MESSAGE CONTRACT — a grader whose target is `last_message` demands
     the literal be in the FINAL message, not merely somewhere in the session.
     `report-empty-instance/redirects-to-analyze` failed that way: the skill does
     name `/senzing:analyze` (report/SKILL.md:41,47), but never says it must
     survive into the closing message, so a run that summarized without repeating
     the command failed a correctly-behaving skill.

Neither check can reason about semantics, and neither replaces the judge. They
catch the mechanical class: a grader asking for a shape nothing ever taught.

Exit 1 on any gap.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
SKILLS = ROOT / "plugins" / "senzing" / "skills"

# Cases with no skill of their own (harness self-tests).
NO_SKILL = {"canary"}

# A grader may legitimately require a literal the skill does not spell when the
# literal comes from a TOOL result rather than the skill's own prose. Each entry
# needs a reason: this list is for "the skill cannot spell it", never for "the
# skill ought to and we did not get round to it".
LITERAL_EXEMPT = {
    # case/grader: why
    "recipes-catalog/title-customer360": "titles come from the live cookbook, not the skill",
    "recipes-catalog/title-healthcare": "titles come from the live cookbook, not the skill",
    "recipes-catalog/title-ppp": "titles come from the live cookbook, not the skill",
    "recipes-catalog/title-stewardship": "titles come from the live cookbook, not the skill",
    "ask-routing/source-url-cited": "the URL is whatever the MCP tool returned",
    "ask-license-request/payload-shown": "the name and address are the prompt's test persona, echoed back",
    "install-eula/eula-surfaced": "the EULA URL comes from sdk_guide's result, not the skill's prose",
    "recipes-named/install-invoked": "same EULA URL, surfaced from the tool by the install hand-off",
}

# `last_message` graders whose literal is exempt above may still need the closing
# contract, so the two checks are exempted separately.
CLOSING_EXEMPT: set[str] = set()

# Phrases that count as telling the model its CLOSING message must carry something.
CLOSING_CUES = (
    "last message",
    "final message",
    "closing message",
    "end your reply",
    "end with",
    "close with",
    "your reply ends",
    "the reply must end",
)


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    body = text.split("---", 2)[1]
    out: dict[str, str] = {}
    for line in body.split("\n"):
        m = re.match(r"^([a-z_]+):\s*(.*)$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def case_skill(case: Path) -> str | None:
    fm = frontmatter(case / "prompt.md")
    tags = fm.get("tags", "")
    m = re.match(r"\[?\s*([A-Za-z0-9_-]+)", tags)
    return m.group(1) if m else None


def literals(pattern: str) -> list[str]:
    """Literal runs a regex requires: >=4 chars, no metacharacters, outside a negative lookahead."""
    if not pattern:
        return []
    # Drop escaped metacharacters so `\\b` etc. do not split a word.
    cleaned = re.sub(r"\\[bBdDwWsSAZ]|\\[nrt]", " ", pattern)  # \n etc. are separators, not letters
    cleaned = re.sub(r"\(\?![^)]*\)", " ", cleaned)  # negative lookahead = forbidden, not required
    cleaned = re.sub(r"\[[^\]]*\]", " ", cleaned)  # a character class is a shape, not a literal
    cleaned = re.sub(r"\\.", " ", cleaned)  # any remaining escape
    out = []
    for run in re.split(r"[^A-Za-z0-9 :_./-]+", cleaned):
        run = run.strip()
        # A run spanning an alternation is not a single required literal.
        # Require a real word: at least one alphabetic run of 4+, not a regex fragment.
        if len(run) >= 6 and re.search(r"[A-Za-z]{4}", run) and not run.isdigit():
            out.append(run)
    return out


def main() -> int:
    problems: list[str] = []
    checked = 0

    for case in sorted(p for p in EVALS.iterdir() if p.is_dir()):
        if not (case / "prompt.md").exists():
            continue  # fixture/helper directory, not an eval case
        skill_name = case_skill(case)
        if not skill_name or skill_name in NO_SKILL:
            continue
        skill_file = SKILLS / skill_name / "SKILL.md"
        if not skill_file.exists():
            problems.append(f"{case.name}: tags name skill '{skill_name}' but {skill_file} is missing")
            continue
        skill_text = skill_file.read_text(encoding="utf-8")
        skill_lower = skill_text.lower()

        for g in sorted((case / "graders").glob("*.md")):
            fm = frontmatter(g)
            if fm.get("type") != "regex":
                continue
            key = f"{case.name}/{g.stem}"
            pattern = fm.get("pattern", "").strip().strip('"')
            target = fm.get("target", "")
            # `not_contains`-style graders assert ABSENCE; the skill need not spell them.
            negated = g.stem.startswith("no-") or g.stem.startswith("not-")
            if negated:
                continue
            checked += 1

            if "last_message" in target and key not in CLOSING_EXEMPT:
                if not any(cue in skill_lower for cue in CLOSING_CUES):
                    problems.append(
                        f"{key}: grades `last_message`, but {skill_name}/SKILL.md never states a "
                        f"closing-message contract. A run that says it mid-session and summarizes "
                        f"without it fails a correctly-behaving skill."
                    )

            if key in LITERAL_EXEMPT:
                continue
            missing = [lit for lit in literals(pattern) if lit.lower() not in skill_lower]
            # Require ALL literal runs to be absent before complaining: one present
            # run means the skill does spell the shape somewhere.
            if missing and len(missing) == len(literals(pattern)) and literals(pattern):
                problems.append(
                    f"{key}: requires literal(s) {missing[:3]} that {skill_name}/SKILL.md never "
                    f"spells. The model has to invent the shape, so it will vary run to run."
                )

    print(f"checked {checked} positive regex grader(s) across the suite")
    if problems:
        print("\ngrader/skill parity gaps:\n")
        for p in problems:
            print(f"  ✗ {p}")
        print(f"\n{len(problems)} gap(s). Pin the shape in the skill, or add a reasoned "
              f"LITERAL_EXEMPT entry if the literal can only come from a tool result.")
        return 1
    print("ok   every positive regex grader's shape is pinned in the skill that must produce it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
